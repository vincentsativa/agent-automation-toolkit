---
name: prospect-scraping
description: >-
  Source, scan, harvest, and clean cold-outreach prospect data for the Email
  Deliverability Rescue offer (Vinny, WSL). Use when Vinny says "scrape
  prospects", "build a list", "get me more leads", "harvest contacts", "run the
  scanner", "clean the list", "new batch of domains", "load more prospects", or
  when running the pipeline as the backup when he is on the road.
trigger: Prospect sourcing / contact harvest / list cleanup for the outreach pipeline.
---

# Prospect scraping pipeline (WSL, `~/money_ideas/`)

The data side of the Email Deliverability Rescue campaign. Order is fixed:
**source -> scan -> qualify -> harvest contacts -> clean -> send.** Never reorder.

All work happens in WSL under `~/money_ideas/`, LF line endings.
Run every script with an interpreter that has `requests` (probe it: `harvest.sh`
does this for you; a plain `python3` may be the Hermes runtime with no requests).

## The five commands (the whole pipeline)

```bash
cd ~/money_ideas
source ~/.config/phantombyte/mailer.env      # SMTP pass + postal address

# 1. SOURCE business domains from OpenStreetMap (free, terms permit it)
python3 osm_industry_prospects.py --max-domains 2000      # writes prospects_<batch>_industry.csv

# 2. SCAN the records; only a CONFIRMED defect is a prospect
python3 test_email_scan.py                                # run this first, read pass/fail
python3 email_scan.py --file <domains>.txt --csv scan_<batch>_results.csv --resume

# 3. HARVEST contacts (parallel; auto-loads the OSM email sidecar)
./harvest.sh --file qualified_<batch>.txt --out contacts_<batch> --workers 4
#    -> contacts_<batch>_final.csv (domain,email,person,kind,source_url,note)

# 4. CLEAN the harvested list into the sendable list (this is the new step)
python3 clean_prospects.py --contacts contacts_<batch>_final.csv \
        --scan scan_<batch>_results.csv --state state.json --out prospects_<batch>
#    -> prospects_<batch>_clean.csv   (sendable, person-shaped)
#    -> prospects_<batch>_dropped.csv (every drop with its reason)

# 5. SEND (Vinny's call on N and the time; never auto-send)
python3 outreach.py --csv scan_<batch>_results.csv --emails contacts_<batch>_final.csv \
        --offer-url https://phantom-byte.com/email-deliverability-rescue --limit N   # dry
```

## The role rule (2026-09-29): a shared role mailbox is NEVER mailed

`outreach.py` drops every role-shaped address on every run (default, not a flag).
`clean_prospects.py` applies the same rule when it builds the stored list, so the
stored list and the send list never disagree again. Role shapes include
`info@, sales@, service@, office@, hello@, contact@, support@, admin@, billing@,
noreply@, webmaster@, marketing@, careers@, hr@`.

`--allow-role` on `outreach.py` is the only override and exists for tests. Never
pass it on a real run.

## What "clean the list" means (`clean_prospects.py`)

One pass, in order, reusing the same modules the send path uses:
1. drop no-address rows;
2. drop rows the scan did not qualify (`qualified == yes`);
3. **role rule** - drop every role-shaped address;
4. drop suppressed / proven-dead addresses and dead domains;
5. drop already-contacted (domain OR address) when `--state state.json` is given;
6. buyer-fit (`prospect_fit.is_target`) - chains, institutions, function desks,
   never-monitored locals, misspelled provider domains;
7. dedupe on domain AND address.

Output is auditable: `_clean.csv` is the send list, `_dropped.csv` is every row
with its reason. Re-run it any time the harvest grows; it is idempotent.

## Measured rates (use these to size a run, never project)

- Reachable addresses per harvested domain: **39 percent** (646 of 1,652).
- Of those: about **47 percent are OSM tag addresses**, ~37 percent role, ~16
  percent person. Named persons are the scarce signal: **6.3 percent, one per 16 domains**.
- The role rule removes every role address, so plan on **person addresses only**:
  roughly **1 reachable person per 10-16 domains harvested**. That is the number
  that caps the daily send now.
- Defect rate (a domain is a prospect) runs **~82 percent** of scanned small
  businesses.

## Where the efficiency is (ranked, safest first)

1. **OSM `email` tag first.** One Overpass call beats up to nine page fetches per
   domain and yields ~47 percent of reachable addresses. `find_contacts.py`
   auto-loads `osm_emails*.csv`; always pass `--osm-emails` for a new batch.
2. **Don't chase role boxes.** They are now never mailed, so the harvest should
   not spend page fetches to collect them. When the only address a page yields is
   role-shaped, the domain is not sendable without a person address - treat it as
   a person-hunt target, not a finished contact.
3. **Short connect timeout for dead hosts.** Runtime is dominated by 15s timeouts
   on dead/slow small-business sites. A `(connect=5, read=12)` timeout tuple cuts
   that roughly 3x on the dead-host share, with no loss on live sites.
4. **Connection reuse + retries.** A `requests` `HTTPAdapter` with a real pool
   size and `Retry` on transient errors removes repeated handshakes and dropped
   sockets.
5. **Parallelize.** `harvest.sh --workers 4` is the proven shape (1,652 domains in
   ~50 min). `email_scan.py` is single-threaded - split the domain list into 4 and
   run 4 scans (2,000 domains in ~8 min).
6. **Resume, never restart.** `find_contacts.py --out` skips domains already in
   the output file; seed every part with the existing CSV.
7. **Keep the path list short.** An 8-path sweep over 61 no-address domains
   recovered 0. `/contact-us`, `/contact`, `/about` are the only additions that
   ever paid. Do not widen it.

## Hard rules

- Never send a role box. Never pass `--allow-role` on a real run.
- Never skip the bounce harvest or mailbox verification on a real send.
- Never add two batches together to report a total; compute the union on domain
  AND address, then subtract the contact history.
- A `none` harvest result is final for that domain, not a retry.
- `state.json` is not the contact history; `outreach_log.csv` is (append-only).
  Never make `state.json` the only record.
- Every write auto-backs-up first. Keep it that way.
