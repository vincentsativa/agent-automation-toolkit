---
name: openleads-prospecting-pipeline
description: "Use when Vinny describes what he wants to sell and needs a target list with contact emails (agent-driven prospecting: offer -> ICP -> how many targets -> verified emails) via OpenLeads."
---

# Agent-Driven Prospecting Pipeline (OpenLeads)

Vinny states what he sells in one sentence. This skill turns that into a sized
ICP, then finds the businesses and the people behind them, then resolves and
verifies their email addresses, then writes a prospect sheet he can send from.

The whole loop is: **offer -> ICP -> target count -> contacts -> verified emails -> sheet.**
One agent does all of it. Do not delegate any step.

## Rule 0, Single agent, one pass
No `delegate_task`, no subagents, no parallel agents. Run the steps in order in
this session and keep every artifact in a workspace folder.

## Rule 1, This pipeline finds and verifies. It does not send.
Use `find`, `enrich`, `verify`, `sources`, `doctor`. Do **not** run
`openleads run`, `openleads send`, `openleads drip --live`, or `openleads
schedule` unless Vinny asks for sending in that specific turn. Vinny's outreach
goes out through his own mail setup (`email-sender` skill, IONOS SMTP from
hello@phantom-byte.com), not from OpenLeads. Sending is a separate decision with
its own deliverability risk, so never fire it as a side effect of a search.

## Rule 2, Never invent a number
Every count in the ICP, every tier, and every email in the sheet must come from
an actual command run whose CSV you keep. Never estimate a lead count, never
write a company name you did not receive back. If a source returns nothing, the
sheet says it returned nothing and the run names the fallback source used.

**Parameters are per-job, never fixed.** There is no standing ICP. Industry, size
band, problem, target role, and geography are all re-derived from what Vinny says
that day, and any of them can change between two runs. Never carry the last run's
numbers into this one, and never treat an earlier size band, vertical, or city as
a default. If a parameter is missing, ask (Constitution Article 4) instead of
substituting the previous value. A run that reuses a stale parameter without
being told to is a failure even when the output looks clean.

**Never source geography from files lying around.** Domain lists, scan CSVs, and
contact sheets already in the project folder are the OUTPUT of earlier runs, not
a statement of current targeting. Tampa and Orlando files sat in the folder for
weeks and got treated as live targeting twice, once to the point of quoting
Florida statutes back at Vinny as if they applied to him. He lives in New York
and had never asked for Florida. Read the folder for tooling, never for target
geography. When nothing in the current instruction names a place, ask.

**Default geography is the New York metro**, because that is where Vinny lives.
It is also the better pool: one of the largest concentrations of businesses with
real mail infrastructure in the country, and near enough that a job can be more
than an email. Do not reach for a distant market unless he names it. Retail
service trades in thin markets, salons, plumbers, single-truck contractors, are
low-value prospects whose defect costs them nothing visible, so a $500 fix is a
hard sell there regardless of how real the finding is. Weight toward commercial
and professional categories, and toward firms with staff, a marketing budget, and
a mail system somebody actually manages.

## Rule 3, Tiers are the send policy
OpenLeads grades each email `safe`, `risky`, or `bad` with a confidence percent.
- `safe` (usually 98%) = verified from the company's own published address or
  ground-truth pattern. Send first.
- `risky` (roughly 50 to 70%) = pattern guess. Second wave only, and only after
  the safe tier is exhausted.
- `bad` / `none` = no email. Discard for sending; keep only as company intel.
Report the tier counts in the sheet header so Vinny can size the send batch.

## Rule 4, No phone calls
Vinny has hearing loss and does not take calls. Never put a phone number in a
prospect sheet, an ICP, or a follow-up plan. Where a normal sales process wants
a call, substitute email plus a written one-pager or a recorded walkthrough.
Every sheet should be labeled email-only contact.

## Rule 5, Diagnose before contacting when a public check exists
If the offer depends on a defect Vinny can verify remotely (mail records, dead
contact forms, mobile layout, HTTPS, missing DMARC), run the check across the
prospect list first and record the finding per row. A cold email that carries a
true, specific finding about their own domain beats any generic pitch. See the
`local-small-business-clients` skill, `references/prospect-diagnosis-scripts.md`.

## Rule 6, License: personal use, Vinny's call

Vinny's stated use is **personal: finding clients for his own services.** That sits
inside the PolyForm Noncommercial 1.0.0 grant (personal, research, educational,
nonprofit), so proceed on that basis. Do not re-litigate it or raise it every run.

Two things stay true and stay in place: the repo's license files are never
removed or edited, and the line is reselling the data itself. His own outreach to
his own prospects is his use. Packaging these lead lists as a deliverable and
selling them is a different use, so raise it once if that ever comes up, then drop
it.

---

## Step 1, Turn the offer into an ICP

Vinny gives one sentence, in some form of this shape:

> AI architecture and agent infrastructure services for 20 to 500 employee SaaS
> companies with [X employees] with [X problem].

That sentence is an **example of the shape, not a fixed template.** The vertical,
the size band, the problem, the role, and the geography all change per job. Every
field below is re-read from what Vinny says for this run, and none of them carries
over from a previous run. A local-services job looks nothing like a SaaS job, and
both go through this same step.

Extract and write down five fields. Everything else in the pipeline keys off
these. Ask for only what is genuinely missing (Constitution Article 4). Never
default a field to the last run's value.

| Field | From the sentence | Notes |
|---|---|---|
| `offer` | what he sells | the service, one line |
| `industry` | the buyer's industry | whatever this job targets, not the last one |
| `size_band` | employee range | the 20 to 500 band is one example, not the rule; many jobs have no size band at all (local businesses, agencies, clinics) |
| `problem` | the pain signal | must be something checkable or searchable |
| `role` | who to contact | founder, CEO, CTO, head of engineering, owner, editor |
| `geo` | where | city, state, country, or "remote/any" |

**Problem signal is the hard part.** A size band is not what you usually need, and
when a size band IS in play no free source filters on it, so the problem has to
become a discovery signal. Three shapes:

- **Stated publicly** (they ship agent features, they post AI job listings, their
  docs mention agents) -> use the `local` source by category and city, `domains`
  on a company list you build, or `yc` for startups.
- **Verifiable remotely** (their mail records, their forms, their site) -> find
  the company first, then run a checker per domain to prove the problem.
- **Not exposed anywhere free** -> say so plainly and propose the closest
  proxy signal that IS exposed. Do not pretend the free sources filter on it.

## Step 2, Decide how many targets

Never pick a round number out of the air. Compute it and show the arithmetic
with the assumption that each number rests on. Cold-email math:

```
deals_needed   = monthly_revenue_goal / price_per_deal
replies_needed = deals_needed / close_rate
sends_needed   = replies_needed / reply_rate
contacts       = sends_needed * 1.2          # 20% headroom for bad/missing emails
```

`reply_rate` and `close_rate` must come from Vinny, or from his own measured
sent/reply history, or be written down as an explicit labeled assumption in the
sheet. Never present a guessed rate as a fact. When there is no history, state
the assumption in the output and offer to recalibrate after the first send batch.

Cap the first pass. A first run collects **25 to 60 contacts**, not 500, because
the offer copy, the problem signal, and the tier mix all need one real batch
behind them before volume means anything. Scale only after a batch produces
replies.

## Step 3, Route to the right source

OpenLeads federates automatically, but for this ICP pin the source with
`-s <name>` so the run is repeatable and you can name what returned what. What
actually works, verified on this machine:

| Source | Returns | Use for |
|---|---|---|
| `local` | businesses by category + city (OpenStreetMap) with websites and real published emails | any "category in city" ICP; no size filter needed; the most reliable source for `safe` business emails |
| `yc` | startup founders with team size (the source applies its own 2 to 200 cap) and industry | startup and SaaS ICPs where a size band matters |
| `domains` | real published emails for any domain you name (homepage, contact, team, security.txt) | large companies with a real contact page; near-useless on small SaaS sites that publish no role address |
| `enrich` | a CSV of name + domain resolved to a verified email; `--deep` harvests the company's own published addresses and can promote risky to safe | any list Vinny supplies, any list you assemble, and any yc row you want upgraded |
| `hn`, `companies`, `edgar`, `producthunt`, `npi`, `openalex` | see `references/recipes.md` | narrow verticals only; several return zero |

Match the source to the ICP instead of forcing one source on every job. A local
services ICP with no size band is a `local` job. A startup ICP with a size band is
a `yc` job. A job that starts from named companies is an `enrich` or `domains`
job. A job that needs a real published contact at a large company is `domains`.

**Size bands are mostly not free-source-filterable.** Only `yc` carries employee
count, and it applies its own 2 to 200 cap. So a "20 to 500 employees" band is
covered below 200 by `yc` and not covered above it, and a band on a non-startup
vertical has no filter at all. When the job has a size band, state plainly which
part of it the sources can actually honor and how the rest gets covered (usually a
list Vinny supplies, resolved with `enrich`). Many jobs have no size band, which
makes this a non-issue.

## Step 3b, Freespoke as a second local sweep

`~/money_ideas/freespoke_finder.py` (mirror and notes at
`scripts/freespoke_finder.README.txt`). Freespoke's web search renders a
`PlacesSection` of business cards above the normal results. Each card carries
name, the business's OWN website, street address, masked phone, and review count.
It is a second, independent sweep of the same shape as `local`, useful when
Overpass is thin or rate-limited.

```bash
cd ~/money_ideas
python3 freespoke_finder.py --pairs "nail salons:new york" "plumbers:tampa" \
    -o fs.csv --domains fs_domains.txt
python3 email_scan.py --file fs_domains.txt --csv fs_scan.csv
```

Rules that make it work:

- **Output feeds the same downstream.** The CSV carries Business Name, Website,
  Domain, Address, City, State, Zip, Phone, Reviews, Industry. `--domains` writes
  the one-per-line file `email_scan.py` and `find_contacts.py` already take,
  which puts the result in the same shape as the `local` route.
- **It is a directory slice, not a census.** One pair returned 2 cards, not 2
  thousand. Volume comes from many narrow industry x city pairs, so the pair
  list is the input that matters. Do not promise big numbers per query.
- **Query shape.** `<industry> <city>` works. Keep the industry as a plain
  business category. A two word industry that collided with a news phrase
  returned zero cards, so if a pair returns nothing, try the simpler category
  noun before concluding the site is empty.
- **The place data is Foursquare.** The rating block is `FoursquareReviewStars`
  and the card links `foursquare.com`, so a Foursquare business listing is what
  makes a business appear. Check Foursquare's terms for commercial outreach use
  before the output becomes a send list, the same gate as Google Places.
- **Scrapling timeout units differ by fetcher.** `StealthyFetcher.fetch`
  `timeout` is MILLISECONDS; `Fetcher.get` `timeout` is SECONDS. Passing 90 to
  StealthyFetcher is 90ms and every load dies instantly. Multiply by 1000.
- **`css_first` does not exist on nested Selectors.** A card from
  `page.css(...)` is a `Selector`; `card.css_first(...)` raises AttributeError.
  Use `card.css(sel)[0]` and read `.get_all_text()`, not `.text`, which returns
  an empty string on container elements.
- **Masked phone numbers.** The card HTML masks digits (`+121****0137`) and only
  the `tel:` href carries the real number. Capture it from the href. Regardless,
  phones never go on a prospect sheet (Rule 4).
- **The same business can appear twice.** It can show as both a website card and
  a card whose website field points at `foursquare.com`. Dedupe on domain, then
  name.

## Step 3c, Pasting a list from ChatGPT or anywhere else

`~/money_ideas/parse_domain_list.py`. Vinny has a ChatGPT
subscription and can get a name plus website list in one prompt for any industry
and city. The paste comes back in a fixed shape: a header row, a number on its
own line, a business name, then a link whose TEXT is the bare domain with a
`?utm_source=chatgpt.com` tail. The script turns that into a domains file.

```bash
python3 parse_domain_list.py --file pasted.txt --out domains.txt --csv named.csv
python3 find_contacts.py --file domains.txt --out contacts.csv
python3 email_scan.py --file domains.txt --csv scan.csv
```

Rules:

- **The link text is usually the bare domain, so do not read it as the name.**
  When the text before the URL is itself the domain, the real name is on the
  line above. Reading it wrong fills the name column with domains.
- **`?utm_source=chatgpt.com` is stripped automatically** by reducing every URL
  to its host, which also drops `/location/new-york/` style path tails.
- **The list is a model answer, so verify before sending.** ChatGPT produces
  plausible business names that may not exist, may be out of business, or may
  have the wrong domain. `find_contacts.py` skipping a domain or finding nothing
  on it is a signal to check that business by hand rather than a failure.
- **It behaves like the Freespoke route downstream.** Name to domain and nothing
  else, so `find_contacts.py` resolves the address and `email_scan.py` proves
  the defect. Measured on a 25 domain contractor list: 10 reachable, 14 with no
  address printed on their pages, 1 skipped as a national brand.
- **The parser is not ChatGPT specific.** Any pasted list carrying URLs works,
  including markdown tables and bulleted lists.

## Step 4, Run and collect

Work in a workspace folder and append every run to files, so counts survive a
long run and you can verify the total against what was asked.

```bash
OUT=~/prospecting/$(date +%F)-<slug>
mkdir -p "$OUT"
OL=~/tools/openleads/ol.sh          # WSL launcher; Windows launcher is ol.cmd

# 1. discover businesses + people with real emails
$OL find "<category> in <city>" -s local -n 40 --format csv -o "$OUT/local.csv"

# 2. email a named-company list (one line with domains, or use enrich)
printf 'company,domain\nAcme,acme.com\n' > "$OUT/list.csv"
$OL enrich "$OUT/list.csv" -o "$OUT/enriched.csv"

# 3. verify anything you need to re-check
$OL verify a@acme.com b@acme.com
```

Then read the CSV back, filter and count in code (never by hand), and merge the
per-source files into one deduped sheet on the domain + email key. Report safe,
risky, and bad counts separately.

## Step 5, The prospect sheet

One CSV plus one short header block. Columns, in the order OpenLeads emits them
plus your additions:

`First Name, Last Name, Email, Title, Organization Name, Website, City, Country,
Email Tier, Confidence %, Source, Role Match, Problem Finding, Date Added,
Sent?, Reply?, Follow-up Date`

- `Problem Finding` is filled from Step 5's checker when one applies, and left
  empty when it does not. Never fabricate a finding.
- `Role Match` flags whether the found person is actually the role in the ICP,
  because business-level sources return `info@` style addresses with no person.
- Header block states: ICP sentence, offer, size band, target count asked for,
  target count actually collected, tier split, sources used, sources that
  returned nothing, and every rate assumption.

Write it to the workspace folder and hand Vinny the path. Offer the next step
(outreach drafting through the `email-sender` skill) but do not send anything.

## Setup on this machine

Already installed and verified. Do not reinstall unless something broke.

**WSL agent**
- Engine: `~/.venvs/openleads` (venv, Python 3.11.15), installed from
  `~/tools/openleads` (repo v4.0.1), extras `[all]`.
- Launcher: `~/tools/openleads/ol.sh` (sets `PYTHONIOENCODING=utf-8`).
- Also on PATH: `~/.local/bin/openleads` -> the venv console script.
- Test suite: `302 passed`. State and DB live in `~/.openleads`.
- **SMTP port 25 is blocked on this network from WSL.** The engine compensates
  with DNS + Gravatar + ground-truth pattern harvesting, so `safe` tier still
  resolves. Port 25 probing works from the Windows side, so prefer Windows for
  hard-to-verify addresses.

**Windows agent**
- Repo copy: `C:\Users\<user>\workspace\openleads`, venv at
  `C:\Users\<user>\.venvs\openleads` (Python 3.12.10), `openleads.exe` in its
  `Scripts\` folder, which is on the User PATH.
- Launcher: `C:\Users\<user>\workspace\openleads\ol.cmd`.
- **UTF-8 is mandatory on Windows.** The CLI prints box-drawing characters and
  crashes with `UnicodeEncodeError` on a cp1252 console. `PYTHONIOENCODING=utf-8`
  is set in the User environment and inside `ol.cmd`. From WSL, call the Windows
  side as `cmd.exe /c "ol.cmd <args>"` after `cd` into that folder.
- Test suite: `301 passed, 1 failed`. The one failure is
  `tests/test_settings_cli.py::test_secret_stored_separately_and_masked`, which
  asserts POSIX `0600` on `secrets.json`. Windows ACLs cannot express `0600`, so
  the assertion is not portable. It is cosmetic, not functional: the file is
  still written and still kept separate from `settings.json`. Do not "fix" it by
  loosening permissions, and do not treat it as a broken install.
- Port 25 is open here, so SMTP verification is available.

Windows and WSL keep separate state (`~/.openleads` vs
`C:\Users\<user>\.openleads`). A run on one side does not see the other's leads or
CRM. Pick one side per campaign and stay on it.

## Pitfalls (learned here)

- `--verified-only` combined with federated search can hang past a minute with no
  output. Do not use it for collection. Collect all tiers, then filter in code.
- **Overpass rate-limits.** The `local` source calls the free
  `overpass-api.de` endpoint. Hammering it with repeated finds in a short window
  returns `HTTP 429 Too Many Requests` (or `504`), and OpenLeads does not retry
  and **does not cache failures**, so the CLI reports `0 leads` when the real
  cause is rate limiting, not an empty result. If `local` returns nothing,
  check `openleads doctor` and the `note:` line the engine prints, then wait and
  retry once. Do not loop probes against it; you make the limit worse and the
  results less reliable. `ol_retry.py` (see `references/recipes.md`) exists for
  this, but treat a retry as a last resort, not a default.
- Filtering in a federated query (for example `"<category> in <city>" -n 6
  --verified-only`) is the slowest path. Pinning `-s local` is faster and yields
  the same or better rows.
- The `local` source needs a category AND a place. A bare city returns noise, and
  a category with no place returns nothing.
- `enrich` needs a **name** to resolve a person's address. A row with only a
  company and a domain comes back `bad` with no email. Supply a CSV of person +
  domain (the `yc` output is a good source of exactly that shape).
- `companies` (Wikidata) has been returning `HTTP 502` and empty result sets.
  Do not build a pipeline step that depends on it.
- `edgar` and `hn` returned zero leads in testing. Treat them as best-effort.
- `producthunt` returns products, not domains, so no emails.
- `npi` and `openalex` are healthcare and academic verticals and rarely carry
  B2B sales emails.
- Output CSVs are CRLF with a UTF-8 BOM, so read them with `utf-8-sig`.
- Do not put the repo's `.git` folder on the Windows copy; it is a working copy,
  not a checkout.

See `references/recipes.md` for the exact commands, the ICP worked example from
Vinny's 10-money-ideas plan, and the source test log. See `references/setup.md`
for the safety review, the install and repair runbook for both machines, and the
update procedure.
