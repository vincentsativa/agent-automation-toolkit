# Contact harvest: measured yield and the fixes that came out of it

Source: the 2,000-domain build of 2026-09-26 (nine-industry, OSM Overpass route),
1,652 qualified domains, four parallel workers, about 54 minutes wall clock.
Every number below is from a run, not an estimate.

## The yield, which sizes every future batch

| Measure | Value |
|---|---|
| Domains harvested | 1,652 |
| Addresses reached | 646 (39.1 percent) |
| OSM tag addresses | 302 |
| Role addresses | 240 |
| Named persons | 104 |
| No address found | 1,006 |
| Named-person rate | 6.3 percent, one per 16 domains |

Use these to plan: 16 domains per named contact, 2.6 domains per reachable address,
since 20 sends a day needs about 51 scanned domains.

## Fix 1: the OSM sidecar is now auto-loaded

302 of 646 reachable addresses (47 percent) came from the OSM `email` tag alone,
ahead of any page fetch. It is the single largest contributor, and it costs one
tag lookup instead of up to nine page fetches per domain.

That run passed the sidecar by hand and nearly missed it. `find_contacts.py` now
finds it itself: `osm_emails*.csv` next to the domain list file first, then the
working directory, newest match wins. An explicit `--osm-emails` still overrides,
and `--no-osm-autoload` disables the search.

Verified live: a 40-domain run printed
`osm sidecar auto-loaded: ~/money_ideas/osm_emails_2000.csv` and
`osm emails loaded: 354 domains`.

## Fix 2: parallel workers, with a launch guard

One process wrote 21 rows in 6 minutes. Four workers over four split domain lists
finished 1,652 domains in about 54 minutes. Parallel is the default now, through
`harvest.sh`.

The failure it prevents: the single-process run was still alive when the four-way
split started, so 21 domains were processed twice and **84 duplicate rows** were
written across the old file and the part files. `harvest.sh` refuses to start
while another `find_contacts.py` is running unless `--force` is passed.

The guard pattern must name the interpreter and the script:
`pgrep -f "python[0-9.]* find_contacts\.py"`. A bare `find_contacts.py` pattern
also matches any shell whose command line merely mentions the filename, including
the Hermes wrapper around the launcher, and the guard then refuses to start
against itself. Verified: the loose pattern reported 2 workers running when zero
were.

## Fix 3: watch the workers, never a pid

A watcher keyed on a pid fires a false "done" every time the launcher re-execs
and the pid changes. That produced three false completion notices in one session.

Wait on the worker pids the launcher itself spawned, plus a stall check on the
row count, and report stall separately rather than killing anything. `harvest.sh`
does both.

## Fix 4: the interpreter must be probed, not assumed

`python3` on PATH on this machine resolves to the Hermes runtime, which has no
`requests`. Four workers died instantly on `ModuleNotFoundError`, and the merge
cheerfully reported **0 domains**, which is indistinguishable from a clean empty
result.

Two defenses, both in `harvest.sh`:

- Probe for an interpreter that can import `requests` before launching, and exit
  4 if none is found.
- After launch, check every worker log for a traceback and refuse to merge, with
exit 5, if one crashed on startup. A run that did not happen is never reported
as a run that found nothing.

## Fix 5: the path list stays short, and that is now re-confirmed

An eight-path sweep (`/about-us`, `/about`, `/team`, `/our-team`, `/staff`,
`/contact-us`, `/company`, `/locations`) was run over 61 domains that returned
HTTP 200 with no address on the home or contact page. It recovered **0 of 61**.

Run the control first: the same detector over 20 domains with a known address
refound **17 of 20**. So the zero is a real zero, not a broken probe. Do not
widen the path list.

## Fix 6: the user agent is not the problem

80 no-address domains were fetched twice, once with the production bot UA
(`PhantomByteContactCheck/1.0`) and once with a real Chrome desktop UA plus
`Accept` and `Accept-Language`. Status codes and address counts came back
**identical, 80 of 80**.

The statuses were dominated by dead hosts and walls, not by content:
`ConnectionError`, `403`, `404`, `202`, and only a minority of clean `200`s. A
`403` or `404` site publishes no address to any user agent. UA spoofing buys
nothing here, and stealth fetching is not needed for this harvest.

## Fix 7: the chain filter is a separate step, so budget it

The buyer-fit filter ran after the harvest and cut **646 to 547**, dropping 99.
Every drop was a national brand (Caliber, Sport Clips, Ace Cash Express, Seminole
Chevrolet), which is the blocklist rule working as intended.

Treat 646 as the harvest figure and 547 as the sendable figure. They are two
numbers, and reporting the first as the second overstates the send list by 99.

## The launcher

`~/money_ideas/harvest.sh`

```bash
./harvest.sh --file qualified_2000.txt --out contacts --workers 4
./harvest.sh --file domains.txt --out contacts --workers 4 --osm-emails osm.csv
./harvest.sh --file domains.txt --out contacts --dry-run
```

Writes `<out>_part1.csv` through `<out>_partN.csv`, then merges into
`<out>_final.csv`, deduped on domain, keeping every input domain. Exit codes: 3
too many harvests running, 4 no usable interpreter, 5 a worker crashed.

All three guards were verified with a real run: A, no harvest running, proceeds;
B, a live worker present, refuses with exit 3; C, a worker patched to crash on
import, refuses to merge with exit 5 and creates no final file. The merge was
verified too: 40 domains in, 40 out, 0 lost, 11 with an address.
