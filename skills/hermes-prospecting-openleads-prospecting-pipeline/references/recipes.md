# OpenLeads recipes, worked example, and source test log

Everything here was run on this machine on 2026-09-16 and the output is the real
output. Where a command returned nothing, that is recorded as nothing.

## 1. Exact launchers

WSL:

```bash
OL=~/tools/openleads/ol.sh
$OL --version          # openleads 4.0.1
$OL sources
$OL doctor
```

Windows, driven from the WSL agent (always `cd` into the folder first, because
`cmd.exe` refuses UNC working directories):

```bash
cd /mnt/c/Users/<user>/workspace/openleads
/mnt/c/Windows/System32/cmd.exe /c "ol.cmd doctor"
```

Windows, driven from the Windows agent directly:

```bat
C:\Users\<user>\workspace\openleads\ol.cmd find "marketing agencies in Miami" -s local -n 20
```

## 2. Core commands

```bash
# discover businesses + real published emails
openleads find "<category> in <city>" -s local -n <count> --format csv -o out.csv

# Hunter-style emails for a named domain
openleads find "emails at <domain>" -s domains -n <count> --format csv -o out.csv

# startup founders with team size and industry
openleads find "fintech founders" -s yc -n <count> --format csv -o out.csv

# resolve a CSV of people/companies to verified emails
openleads enrich in.csv -o out.csv            # add --deep for slower, better ground truth

# re-verify specific addresses
openleads verify a@acme.com b@acme.com

# list and inspect sources
openleads sources
openleads sources info local
```

Useful flags on `find`: `--industry`, `--location`, `--title`, `--keyword`,
`--no-people` (keep company-level rows), `--no-cache`, `--max-companies`.
Formats: `csv`, `json`, `ndjson`.

## 3. What actually returned leads (measured 2026-09-16)

| Command | Result |
|---|---|
| `find "emails at stripe.com" -s domains -n 5` | 1 lead, `safe`, 98%, `jane.diaz@stripe.com` |
| `find "marketing agencies in Miami" -s local -n 5` | 4 leads, all `safe` 98% (`hello@craftly.ai`, `hello@marketkarma.com`, `office@missionmorph.com`, `info@designhouseagency.com`) |
| `find "fintech founders" -s yc -n 5` | 5 founders, 1 `safe` 98%, 4 `risky` 52 to 62% |
| `enrich` with name + domain (`Jane Diaz / stripe.com`) | `safe` 98% |
| `enrich` with name + domain (`Eric Zhu / axisanalysis.com`) | `risky` 62% |
| `enrich` with company + domain only (Stripe, Notion, Ready, Axis) | all `bad`, no email — a person's name is required |
| `find "companies" -s companies --industry "software industry"` | 0 leads, `query.wikidata.org returned HTTP 502` |
| `find "<category> in <city>" -n 6 --verified-only` (federated) | hung past 180s, killed |
| `find "companies hiring" -s hn -n 6` | 0 leads |
| `find "cloud software" -s edgar -n 5` | 0 leads |
| `find "saas products" -s producthunt -n 5 --no-people` | 5 products, no domains, all `bad` |

Verdict: **`local`, `domains`, `enrich`, and `yc` are the four that produce
contactable, tiered leads.** Everything else is best-effort.

## 3b. Overpass rate limiting (important)

The `local` source queries `https://overpass-api.de/api/interpreter`, which is a
free, shared, rate-limited service. Its behavior here:

- A single query on its own succeeds in under a second.
- Repeated queries inside a few minutes return `HTTP 429 Too Many Requests` or
  `HTTP 504`, and `openleads` reports `0 leads` because it does not retry and
  does not cache failures.
- The 504 is misleading: it is not an empty area, it is throttling.

Practical rule: run `local` finds at a normal human pace, one every few minutes at
most, and treat a `0 leads` from `local` as "unknown, probably throttled" rather
than "no businesses exist there." The engine prints a `note:` line naming the
host and the HTTP reason when this happens, so read the run output before
concluding anything.

`ol_retry.py` is included for the retry case. It shells out to the same CLI with
the same interpreter, retries on empty output, and prints the tier split:

```bash
# WSL
~/.venvs/openleads/bin/python3 ~/tools/openleads/ol_retry.py \
  --out /tmp/leads.csv -- "marketing agencies in Miami" -s local -n 30 --format csv

# Windows (from WSL)
cd /mnt/c/Users/<user>/workspace/openleads
/mnt/c/Windows/System32/cmd.exe /c "set PYTHONIOENCODING=utf-8&& C:\Users\<user>\.venvs\openleads\Scripts\python.exe ol_retry.py --out C:\Users\<user>\leads.csv -- \"marketing agencies in Miami\" -s local -n 30 --format csv"
```

Do not use it as a substitute for pacing.

## 4. Worked ICP from Vinny's 10-money-ideas plan

Source: `10-money-ideas-start-monday-2026-09-13.txt` (Ideas 1, 4, 6, 9 are the
B2B ones, and Idea 9's buyer is the closest match to the example sentence).

**This is one worked example, not a standing configuration.** It exists to show
the arithmetic and the routing, not to be the ICP for the next job. The next run
re-derives every field from whatever Vinny says that day.

Offer sentence as given:

> AI architecture and agent infrastructure services for 20 to 500 employee SaaS
> companies with X amount of employees with X problem.

Resolved ICP:

| Field | Value |
|---|---|
| offer | AI architecture and agent infrastructure services (agent harness, context engineering, tool/API description cleanup, runtime-exploit verification gate) |
| industry | B2B SaaS, developer tools, API platforms |
| size_band | 20 to 500 employees |
| problem | agent-written code passing static analysis and failing at runtime; MCP tool descriptions missing the annotations routing depends on; tool responses overflowing the context window |
| role | founder, CTO, head of engineering, platform lead |
| geo | United States first, remote-friendly |

Target count, computed rather than guessed:

```
goal $2,500/mo, price $1,200 per engagement      -> 2.1 deals needed  -> 3
close_rate 20% (ASSUMPTION, unmeasured)          -> 15 replies needed
reply_rate 10% (ASSUMPTION, unmeasured)          -> 150 sends
contacts = 150 * 1.2                             -> 180
first-pass cap                                   -> 50 contacts
```

The sheet must print both the computed 180 and the capped 50, and label the two
rates as unmeasured assumptions until the first batch produces replies.

Discovery route for this ICP, given what the sources actually do:

1. Assemble a 60-company list of B2B SaaS and developer-tool companies with 20 to
   500 employees. Free sources do not expose the employee filter, so this list is
   partly hand-built from `local` by category and city plus any list Vinny
   supplies, and partly seeded from `yc` (which does carry team size).
2. `openleads find "emails at <domain>" -s domains` or `openleads enrich` on a
   person + domain CSV for each company on the list, so the contact is a named
   engineering lead where one exists.
3. Where only a company-level address comes back (`info@`, `hello@`), flag
   `Role Match = company-level` and treat those rows as the second wave.
4. Run one public check per domain where the offer allows it, so the first email
   carries a real finding rather than a generic pitch.

## 5. Windows specifics, verified

- `openleads.exe --version` -> `openleads 4.0.1`.
- `doctor` from Windows: `DNS-over-HTTPS reachable`, `SMTP port 25 reachable via
  alt1.aspmx.l.google.com`, `GitHub token set`.
- `doctor` and `find` both crashed with
  `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'` until
  `PYTHONIOENCODING=utf-8` was set. It is now set in the User environment and in
  `ol.cmd`. Never call the Windows CLI without it.
- `py` launcher is at
  `C:\Users\<user>\AppData\Local\Programs\Python\Launcher\py.exe`. Python 3.11 and
  3.12 are both installed under
  `C:\Users\<user>\AppData\Local\Programs\Python\`. The OpenLeads venv was built
  from 3.12.10.
- WSL and Windows do not share state. `~/.openleads` on WSL and
  `C:\Users\<user>\.openleads` on Windows are separate.
