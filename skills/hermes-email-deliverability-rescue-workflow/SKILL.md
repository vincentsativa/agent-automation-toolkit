---
name: email-deliverability-rescue-workflow
description: Email deliverability rescue workflow for Vinny, IDEA 2.
trigger: Email scan / deliverability rescue with script-assisted drafts.
---

# Email deliverability rescue workflow (Vinny, IDEA 2)

## Always-on rules (read before sizing anything)

- **Compliance is the DEFAULT, never a caveat.** Every part of this pipeline MUST comply: sourcing, content, opt-out, list storage, and what happens if the list is ever sold. Raise a compliance problem BEFORE something ships. The user has been in email since before CAN-SPAM, so add value on bookkeeping and fields, not the principle.
- **The send cadence is a warm-up ramp, not a host limit.** Read the send history as strategy. Never report the ramp as a constraint the user is stuck under, and never raise the host quota as a risk when the plan sits at 6 percent of it. Account age is NOT sending history.
- **Sizing and cadence math: `references/outreach-volume-and-cadence.md`. Copy-strengthening rules (subject craft, locked body order, single CTA, protected copy): `references/copy-strengthening-playbook.md`.** Read the applicable one before quoting runway, reply rates, or proposing copy changes. Build status, durations, and state-file protection: `references/build-status-checks.md`, `references/state-file-protection.md`.

## Gmail + Microsoft gateway-rejection enforcement (2026-10-05)

The failure mode changed from "filtered to the spam folder" to **rejected at the
gateway**. Gmail (enforcement ramped Nov 2025) and Microsoft (since 2025-05-05)
now REFUSE mail from a domain that fails SPF/DKIM/DMARC once it sends **5,000 or
more messages a day to that provider's consumer addresses** (not total volume).
Microsoft refuses it in the SMTP dialogue:

    550 5.7.515 Access denied, sending domain does not meet the required authentication level

A DMARC reject reads `550 5.7.509 ... does not pass DMARC verification and has a
DMARC policy of reject`. The threshold is reported sticky (cross it once and the
requirement applies even if volume drops) -- **plausible but unverified**, so
warn, never hard-block on stickiness alone.

What this changes in the pipeline:

- **Severity, not just grade.** Missing or misaligned SPF/DKIM/DMARC is
  **critical** (a gateway rejection), not a placement risk. `email_scan.py` now
  writes `severity` (critical/high/medium), `enforcement`, and `alignment`
  columns; `AUTH_ALIGNMENT_FAIL` is the one alignment failure that is certain
  from outside (SPF authorizes no sender at all + no DKIM + enforcing DMARC).
  The receive-provider-vs-SPF mismatch is reported but NOT graded: a domain can
  receive at Google and send elsewhere (`hubspot.com`, `zendesk.com` proved
  that on the first pass).
- **`auth_enforcement.py` is the single source of the model** (provider lists,
  the 5,000 threshold, `classify_rejection`, `preflight_sending_domain`). Use it;
  do not re-implement the provider lists or the phrase matcher.
- **Bounce classification.** `harvest_bounces.harvest_full()` buckets refusals
  into dead_mailbox / auth_gateway / content_block / spam_complaint / soft. A
  gateway auth rejection is **NOT a dead mailbox**: the recipient is live and the
  SENDING domain failed auth. It is logged to `auth_rejections.txt` and **never
  suppressed**.
- **Sending-domain pre-flight.** `outreach.py`, `schedule_drafts.py` and
  `stage_drafts.py` all refuse a real send/stage when the From domain fails its
  own records (`--skip-auth-preflight` overrides; tests only). The reusable CLI
  is `domain_preflight.py <domain> [--ses] [--print-records]`. Run it before
  warming any new sending domain (the SES `mail.vincentsativa.com` identity).
- **Volume awareness.** `state.json` carries a per-day, per-provider `volume`
  map; the send path warns at 80% of 5,000 for the gmail/microsoft buckets when
  the sending domain is not fully authenticated.
- **Copy.** The email and the findings sheet now say "rejected at the gateway,
  never reaches the recipient", not "landing in spam". The email adds a "why
  now" beat (`CHANGE_NOTE`) and the hard price line was removed in favour of a
  free-check soft close (`NO_PITCH`). `seed_check.py` is honest that a NONE
  result may be a gateway rejection, not placement.

**Removing the price does NOT make the email non-commercial under CAN-SPAM**
(the postal address and opt-out stay for that reason); it is a tone change and an
IONOS-AUP read, not a legal change. Say so plainly if asked.

## File inventory (all in ~/money_ideas/)
Reuse these; do not rebuild them. But do NOT describe them as verified until you have run them in this session and read the output. "Built and verified" is a claim, not a default, and a remembered pass count proves nothing.
- `email_scan.py` - deliverability scanner. SPF/DKIM/DMARC/MX, grades each, writes a CSV with a `defect_codes` and a `qualified` column. DNS-over-HTTPS, no API keys. Usage: `python3 email_scan.py --file domains.txt --csv email_scan_results.csv --resume`. **2026-10-05: also writes `severity`, `enforcement`, and `alignment` columns (missing/misaligned SPF/DKIM/DMARC = critical, a gateway rejection).**
- `auth_enforcement.py` - **NEW 2026-10-05.** The single source of the Gmail/Microsoft enforcement model: consumer-provider buckets, the 5,000/day threshold, `classify_rejection()` (auth_gateway / content_block / spam_complaint / dead_mailbox / soft), and `preflight_sending_domain()` (alignment: exists but does not pass). Imported by `email_scan.py`, `harvest_bounces.py`, `outreach.py`. Do not re-implement the provider lists or the phrase matcher.
- `domain_preflight.py` - **NEW 2026-10-05.** CLI that proves a SENDING domain would pass enforcement before it sends or is warmed. `python3 domain_preflight.py <domain> [--ses] [--print-records] [--ses-dkim-selector <sel>]`. Exit 0 = ready, 1 = not. Run it for the SES `mail.vincentsativa.com` identity before any send.
- `test_email_scan.py` - known-answer test for the scanner. Run it after ANY edit to `email_scan.py` and before any scan whose output feeds a cold email. It asserts each SPF lookup count against a second, independently written counter in the same file, checks NXDOMAIN and null MX against live domains, and asserts every qualified row carries a documented defect code with a finding behind it. A scan that has not been through this test is not a scan.
- `test_outreach.py` - known-answer test for the send path: the gates, the refusals, the dedupe, and the rendered templates. Run it after ANY edit to `outreach.py` and before any real send. It sends nothing, ever. Read the pass/fail count out of the run rather than quoting a count from a brief or a past session; the count drifts as checks are added and a wrong number is a claim with nothing behind it. One of its checks asserts that no rendered variant puts a `Subject:` line in the body and that `send_one` refuses one that does; keep that assertion in this file so the duplicate cannot return unnoticed. **It runs against a per-run temp directory for state, log, and stop list, and `outreach.py` reads those three paths from the environment so the suite can redirect the subprocess it drives.** Do not point either back at a production filename: before the fix, a single passing run overwrote and then deleted the campaign's contact history. See `references/state-file-protection.md`.
- `site_check.py` - 20-point site inspector (Idea 8), writes CSV + markdown report.
- `outreach.py` - send script. Dry-run by default, NO cap and NO default count (`--limit` is whatever Vinny names for that run, and omitting it sends the whole eligible list), one-send-ever dedupe, `stop_list.txt` checked before every send, live DNS re-check of the defect before each send, opt-out + List-Unsubscribe header. `python3 outreach.py --csv email_scan_results.csv --emails contacts.csv --offer-url URL`. It reads the SMTP password from `PHANTOMBYTE_SMTP_PASS` and the CAN-SPAM postal address from `PHANTOMBYTE_POSTAL_ADDRESS`, both from the environment, and refuses to send if either is unset. Never hardcode either value back into the file. **ROLE RULE (2026-09-29): a shared role mailbox is NEVER mailed.** Role-shaped addresses (info@, sales@, service@, office@, hello@, sales@, support@, admin@, billing@, noreply@, ...) are dropped before the dedupe on every run, which retires the HELLO_AND_INFO and C tiers so only person-shaped A/B are sendable. It is the default, not a flag; `--allow-role` overrides it for a test only, and the old `--person-only` is a deprecated no-op. Flags added 2026-09-28: `--hold-unknown` holds the addresses the probe could not decide for that run only and NEVER suppresses them; `--hold-catch-all` does the same for catch-alls; `--send-order person-first|greeting-first` sets the send order (default **person-first**, which reverses the 2026-09-23 greeting-first order, so A/B people go before the role inboxes; `greeting-first` restores the old order); and `--no-bounce-guard` / `--bounce-threshold` control the circuit breaker that pauses a real send when the hard-bounce rate on sends in the last 72h is over the threshold (5.0% over a 20-send floor). Setting `PHANTOMBYTE_UNSUBSCRIBE_URL` to the contact API's `/api/unsubscribe` adds the RFC 8058 one-click `List-Unsubscribe-Post` header per recipient, and the send path reads `[UNSUBSCRIBE]` notices out of the inbox and appends them to `stop_list.txt` automatically. The fit filter also drops never-monitored locals (webmaster, postmaster, abuse, mailer-daemon, ...) and misspelled provider domains (outook.com). **2026-10-05: `preflight_sending()` refuses a real `--send` from a domain that fails its own records; `CHANGE_NOTE` adds the "Gmail or Microsoft tightened this" beat; `NO_PITCH` replaced the hard $500/$29.99 price line with a free-check soft close. `--skip-auth-preflight` overrides the pre-flight for tests only. `state.json` carries a per-day, per-provider `volume` map.**
- `schedule_drafts.py` - the CURRENT staging path. Schedules the day's sends into the IONOS Scheduled folder over the Open-Xchange HTTP API with a real send time on each one. `python3 schedule_drafts.py --offer-url URL --limit 20 --start 2026-09-22T09:00 --gap 5`, plus `--dry` to render and print the time plan without touching the mailbox. `--jitter` (default 2) randomizes each gap by up to +/- that many minutes, so the send times are not a fixed heartbeat. It marks `state.json` with `status: "scheduled"` and never writes `outreach_log.csv`. Its full mechanism, recipient shape, and verification read-back are in the scheduling section below.
- `stage_drafts.py` - the older staging path, loads into Drafts for a hand send. Superseded by `schedule_drafts.py`; run it only if Vinny asks for drafts specifically. It selects the day's rows through the full gate chain, appends one message per prospect to the IONOS Drafts folder over IMAP, reads the folder back, and marks `state.json` in the same pass. `python3 stage_drafts.py --offer-url URL --limit 20`, plus `--dry` to render and print without touching the mailbox and `--restage` to clear the folder and re-stage it. It refuses to stage a message whose body carries a subject line, and it never writes `outreach_log.csv`.
- `osm_industry_prospects.py`, `osm_metros.txt` - industry-classified collector for Vinny's nine-industry order. Overpass route as `osm_prospects.py`, but keeps each element's tags so every domain carries the industry (`industry_source` says tag or name fallback) and screens out every already-scanned domain. Measured 2026-09-24: 1,000 domains, 805 qualified, 305 send-ready. Run its contact harvest in parallel chunks; never stop one with `pkill -f find_contacts`. Detail in `references/industry-prospect-build.md`.
- `find_contacts.py` - public contact-page harvest. Reads the business's own home page and the usual contact paths (`/contact`, `/contact-us`, `/about`, `/team`) and pulls a mailbox off the page itself. `python3 find_contacts.py --file qualified_domains.txt --out contacts.csv`. **2026-09-29: `clean_prospects.py` turns a harvest into the sendable list (role rule + suppression + fit + dedupe) and the fetch now uses a short connect timeout; see `references/list-cleaning-and-harvest-speed.md`.** It never guesses an address from a name pattern and never reads WHOIS, because registry terms forbid the outreach use. A role address is used only when no person is named. **It now auto-loads the OSM email sidecar.** Measured yield and the seven fixes proven on 2026-09-26 (parallel launch, the launch guard, pid-free watching, the interpreter probe, the path and user-agent negatives, and the separate chain-filter step) are in `references/harvest-yield-and-fixes.md`, with the launcher at `harvest.sh`.
  - **The measured yield, which sizes every batch: 1,652 qualified domains produced 646 addresses (39.1 percent)** - 302 osm, 240 role, 104 person, and 1,006 with none. The earlier 243-domain sample matched at 34.6 percent (84 addresses: 29 person, 39 role, 16 osm, 128 none, 31 skip). A named person is the scarcest signal at 6.3 percent, one per 16 domains. Budget 16 domains per named contact and about 2.6 per reachable address. The current send rate, the runway, and the refill volumes are in `references/send-cadence-and-list-economics.md`.
  - **The path list stays short, and the give-up is early. Do not widen it.** Measured on the real hits: the home page carried 54 of 70 addresses, `/contact-us` added 8, `/contact` added 6, and `/contact.html` plus `/about` added one each. Widening the net from 9 paths to 18 recovered **0 of 35** domains that the short list had missed, with the fetches verified working by hand, so those sites genuinely publish no address anywhere. Abandon a host after two failed paths rather than spending 15-second timeouts down the whole list: dead and slow small-business sites are the entire runtime of a harvest, and a wider net buys nothing but wall clock.
  - **A `none` result is a final answer for that domain, not a retry.** Fetching it again with more paths costs minutes and yields the same nothing. Re-measured 2026-09-26: an eight-path sweep over 61 domains that returned 200 with no address recovered **0 of 61**, and the same detector over 20 known-good domains refound 17, so the zero is real. The user agent is not the cause either: 80 domains fetched with the bot UA and with a real Chrome UA returned **identical** codes and counts. Most of these hosts are dead, `403`, or `404`, which publishes no address to anyone. If a contact is needed for a domain with no printed address, get it from a search or licensed source instead of re-scraping the site.
  - **Trust the `email` column first; treat `person` as a hint, not a fact.** The extractor was rebuilt to believe a name only when an owner or officer title word directly abuts it, with honorifics skipped and nav, heading, geography, and business words blocklisted. Verified live on 2026-09-20: `aacpas.com` no longer tags "Newsletters Guides", `bayshorebaptistchurch.com` now yields Scott Stearman with `sstearman@`, and the phone-glued `1-866-520-uglyinfo@coyoteuglysaloon.com` is gone, re-harvested to the real `lee@coyoteuglysaloon.com`. It is improved but not clean: `adesa.com` still tags "Canadian Auction" on `dealerreg@adesa.com`, and `247-towingservice.com` still tags "Spins European-licensed". So still read the address as the fact and the name as a hint.
  - **A printed name never reaches a greeting unless it matches the mailbox.** `name_matches_address` corroborates the name against the address, and a first-name greeting is used only on a match, so a garbage name cannot appear in a sent email. Addresses whose local part starts with a digit are rejected outright. `address_shape` classifies a mailbox as person or role by its local part, and `prospect_tier` ranks a prospect HELLO_AND_INFO, A, B, or C. The send path drops every role shape by the role rule above, so only A/B actually send; the ranking lives in `references/contact-priority-and-send-order.md`.
  - **Yield improves sharply on a batch that carries OpenStreetMap addresses, and the sidecar is now found automatically.** Measured on the 2,000-domain build: **302 of 646 reachable addresses (47 percent) came from the OSM `email` tag**, ahead of any page fetch, the largest single contributor. Passing it by hand was the weak point, so `find_contacts.py` now searches for `osm_emails*.csv` next to the domain list, then in the working directory, newest wins; `--osm-emails` still overrides and `--no-osm-autoload` disables it.
  - **Append-as-you-go is in place, not owed.** `find_contacts.py` writes each row with `flush()` and `os.fsync()` the moment it is found, so a kill keeps everything harvested, and a rerun resumes by skipping domains already in the output file. Confirmed by grep and by a live partial-file read on 2026-09-20.
  - Expect a long run of `none` results. Small business sites frequently print no address anywhere, so a large share of qualified domains yield no contact. That ratio is what sizes a batch against the daily send rate, so report it broken out by kind rather than as one total.
- `findings_sheet.py` - generates the free findings sheet that every outreach email promises in its CTA ("Want the free findings sheet for {domain}? Reply and I will send it today."). It reads the scanner's own CSV row, so every line traces to a measurement rather than to memory. Per defect code it carries plain-language wording, the four-check pass/warn/fail, the live record strings, the SPF lookup count, a Socratic question matched to the leading defect, then the fix and price. Usage: `python3 findings_sheet.py --csv email_scan_results.csv --domain foo.com`, or `--all --outdir sheets/` for every qualified row. **It is a generator only, and nothing auto-sends it.** A reply is served by hand, because automating the send is the one thing this skill forbids outright.
  - **A defect code with no entry in `DEFECT_PLAIN` ships the raw code name into the sheet.** When a new code is added to the scanner, add its plain-language wording in the same change, and assert every code present in the qualified set has one. The check is mechanical: collect the codes from the CSV, then confirm each is a key in `DEFECT_PLAIN`.
  - **Generate the sheet at the moment of sending, not at harvest time.** The sheet quotes the record strings and the four grades, so a sheet built days earlier can quote a record that has since changed, which is the same false claim the live pre-send recheck exists to prevent.
  - Verify every generated sheet the same way as the email copy: zero literal braces, zero em or en dashes, zero spaced hyphens, the postal line present, and the domain actually named. Confirm that unqualified rows produce no sheet at all.
- `prospect_fit.py` - the buyer-fit filter. Answers the question the scanner does not: is this the kind of business that buys a one-domain fix? Chains, institutions, and function mailboxes that route to a department are dropped before the dedupe. `is_target(domain, email, ranks)` returns `(ok, reasons)`; `screen_contacts(path)` reports the effect on a file and changes nothing. Wire it into the send path, not into a manual pass: `outreach.py` calls it on every dry run and every send, so a chain cannot reach a draft. Toggles: `--no-fit` to disable for a test, `--fit-download` to fetch the Tranco list if the cache is missing, `--fit-report` to print every drop with its reason.
  - **Judge only rows that have a contact address.** A row with no address is skipped later anyway, so running the fit test over it reports a number far larger than the list the filter actually changes, and that inflated number does not mean what it says. The filter must pass no-address rows straight through untouched.
  - **Err toward keeping a marginal prospect.** A wrong drop silently deletes a real local business, which costs a sale; a wrong keep costs one email out of twenty. So the rules stay specific rather than broad: no rule cuts a whole TLD, and a genuine local nonprofit survives.
  - **The cutoff is the whole Tranco top 1M here, not the top 100k used at harvest time.** Everything between 250k and 1M in the measured set was still a multi-office firm or an institution (a global aerospace supplier, a law firm with several offices, a famous steakhouse with its own marketing operation), while every real local business sat outside the list entirely.
- `run_scan.sh` - wrapper: `./run_scan.sh email my_domains.txt` or `./run_scan.sh sites my_sites.txt`
- `domains_example.txt` - PLACEHOLDER only, not real prospects.
- `email_scan_results.csv`, `site_check_results.csv` - test-run outputs only.
- `HOWTO.txt`, `HOWTO_ADDENDUM.txt` - run instructions and open items.
- Offer page: `C:\Users\<user>\OneDrive\Desktop\MONEY MAKING OPPORTUNITIES\offer-pages\email-deliverability-rescue.html` (Linux view: `/mnt/c/Users/<user>/OneDrive/...`). It lives on the Windows OneDrive side, not in `money_ideas/`, so a search of the Linux home directory will not find it. Treat the addendum's `offer-pages/email-deliverability-rescue.html` relative path as stale.
- Do not claim any of these files is missing until you have searched `/mnt/c/Users/<user>/`.

## The four open items before outreach can send
1. Real domain list: 100-150 local businesses + 60-80 agencies, one per line.
2. Run the scan, then work the `qualified` column. Each qualified row is a prospect with its defect already coded and its finding pre-written in the findings column.
3. Contacts file: `theirsite.com, owner@theirsite.com` from public contact pages.
- 4. Offer page uploaded + `--offer-url` set. The $500 payment link exists: `https://www.paypal.com/ncp/payment/VMB4RLLDSMGKG`.

## Sourcing business domains: OpenStreetMap Overpass (the free volume source)

This is the proven way to get business domains in bulk with terms that permit the use, and it costs nothing.

```
[out:json][timeout:180];
(
  nwr["website"]["name"](27.80,-82.55,28.10,-82.30);
  nwr["contact:website"]["name"](27.80,-82.55,28.10,-82.30);
);
out tags;
```

- Endpoint `https://overpass-api.de/api/interpreter`, POST `{"data": <query>}`. **Send a real User-Agent**; a bare requests call gets HTTP 406. The header that worked: `PhantomByteProspectScan/1.0 (mail deliverability screening; contact hello@phantom-byte.com)`.
- Measured, not projected: the Tampa Bay bbox above returned 2,221 businesses carrying a `website` tag, resolving to 1,249 distinct domains in a single call. Swap the bbox per metro.
- **The same query can hand you the contact address for free, without scraping anything.** OSM carries `email` and `contact:email` tags: the Tampa bbox returned 160 records with an email value covering 141 distinct domains, 29 of which were in the qualified set. Add `nwr["email"]["name"](bbox)` and `nwr["contact:email"]["name"](bbox)` to the query and use those addresses first, ahead of any page harvest. It is one API call versus nine page fetches per domain, and it is data the business published itself for contact.
- Normalize every URL: strip the scheme, keep host only, drop a leading `www.`, lowercase, and keep it only if it matches a real hostname. That is what turns tags into a domain list.
- License is ODbL 1.0 (`https://www.openstreetmap.org/copyright`). Attribution is the operative duty for a one-off screening extract. Publicly republishing an adapted database is a different question and needs the full license read first.
- Disqualified sourcing, do not revisit: **Google Places** (Maps Platform Terms 3.2.3(a) forbids exporting or bulk-downloading places content, and the AUP forbids using the services to facilitate unsolicited mass email, so it fails on both counts), **LinkedIn** (user agreement forbids it), **WHOIS/RDAP** (Verisign RDAP terms forbid mass-solicitation use, and registrant data is redacted anyway), **ChamberofCommerce.com** (terms forbid it), and chamber or association rosters without written permission from that association. Florida Sunbiz bulk data is a name source only: it carries no domains and no email addresses, so it is a supplement, never the spine.
- The full sourcing, screening, and contact-yield reference, including the Tranco blocklist recipe and the measured rates, is in `references/prospect-sourcing-and-screening.md`.

## Sizing the scan to the send budget

The sending rate is a deliberate warm-up that Vinny sets and raises: 20/day, then 50/day, then 100/day, climbing toward 500/day over weeks, weekends off. It is his strategy, never a ceiling imposed from outside, so never restate a rate as a limit. The current rate and the runway arithmetic, the refill volumes, and the rule against summing two batches without measuring the overlap are in `references/send-cadence-and-list-economics.md`.

- **Scan a working buffer over the send budget, not an inventory.** Not every scanned domain will qualify or be reachable, so scan meaningfully more than the daily rate. **The size is Vinny's call; ask, do not pick it.** Recent orders were 1,000, then 2,000. A batch in the thousands is workable: run the harvest through `harvest.sh` (parallel workers, launch guard, OSM auto-load), and read `references/bulk-build-scaling.md` for the measured rates and the run order. Scan, work it, scan again.
- **Run the contact harvest only after the scan, and only over the rows that will actually be sent.** Contacts must exist before a row is worth anything: 829 qualified domains with no reachable address is a worthless artifact.
- **Never start a bulk scan, a contact harvest, or a list build unless Vinny ordered it.** Fixing a script is not authorization to run it at volume. Test a script against a handful of known domains, then stop and report. Building the pipeline he did not ask for is the exact failure mode Article 13 and Article 16 exist to stop, and it reads to him as hours of wasted time even when the tooling works.
- Demand is not the constraint, so a huge scan is not needed to prove anything. Two independent samples put the defect rate at about 81 percent: 829 of 1,003 domains, and 243 of 300 in the 300-domain run. A third sample drawn from a curated list of large city firms came in lower, 344 of 500 (68.8 percent), because bigger firms run managed mail infrastructure and one-person shops do not. Read that as pool composition, not as a better or worse list: the same gate still produced 301 usable local prospects from one 500-domain batch. Treat a defect as the norm for small business mail records and size the list to the send budget plus a buffer, not to the supply of domains available. What that number does NOT tell you is how many reply and how many pay, so never present it as evidence the service will sell. The only answer to that is sending to 20 and counting.

## Sending credentials live in an env file

`outreach.py` and the send path read `PHANTOMBYTE_SMTP_PASS` and `PHANTOMBYTE_POSTAL_ADDRESS` from the environment. They are stored at `~/.config/phantombyte/mailer.env` (mode 600), so a session sources it rather than retyping anything:

```
source ~/.config/phantombyte/mailer.env
```

Vinny's CAN-SPAM postal address for the message footer: `500 Peconic Street, Apt 231A, Ronkonkoma, NY 11779`.

## One email, ever: the contact history that keeps this outreach and not spam

The single thing that separates this from spam is that each person is written to once. Vinny stated it plainly: keep a list of who was sent to so it only goes once, "this way it's outreach and not spam." Three layers enforce it, and all three stay.

- **Dedupe by domain AND by the person's address.** Keying on domain alone misses the same owner reachable under a second domain, which is how a first contact becomes a duplicate. `already_contacted(state, domain, email)` checks both; a row is dropped if either matches. Never narrow it back to a domain-only test.
- **`outreach_log.csv` is the durable record, append-only, one row per send** (`sent_at, domain, email, template, subject`). `state.json` is only the fast index, and `load_state()` rebuilds `contacted` from the log on every load. Deleting `state.json` must not re-open anyone, so never make it the sole history. Open the log with `newline=""` or every row is written with stray carriage returns.
- **`stop_list.txt` is read before every send**, one address per line. A reply containing "stop" goes in immediately, before anything else is done.

Verify the dedupe by test, not by reading it: record one send in the log, then assert that the same domain with a different address is blocked, that a second domain at the same address is blocked, that deleting `state.json` still blocks (rebuilt from the log), and that an unrelated fresh domain is still allowed. Four assertions, a few seconds.

## Never claim a check the pipeline cannot back

The email's first line asserts a specific record was checked: "I checked the mail records for {domain} today, and here is what I found." A template that fills in any row will happily print that claim for a domain that was never scanned, or for one whose defect was fixed since the CSV was written. Both are false statements sent to a stranger with their own DNS in front of them.

- `recheck_defect(domain, expected_code)` re-measures the domain over DNS immediately before each send and the send is REFUSED unless the expected defect is still present. Do not remove it as a speed cost; it is what makes the claim true at the moment it is sent.
- Test the refusal both ways: a fabricated row for a domain that does not exist must be refused, and our own clean domain must be refused.
- Never prove the send path with a hand-written body. Render it from a synthetic row in the scanner's exact CSV shape, so what is tested is the real pipeline's output.

## Proof of the send path, end to end

A message through `outreach.py` is not proven by a successful SMTP call. Prove it by reading it back: send to Vinny's own address and then fetch it over IMAP and print the body and the headers. Confirm in that read-back: the postal address line, the opt-out line, the offer URL, and `Authentication-Results` showing `dkim=pass`, `spf=pass`, `dmarc=pass`. Anything less is a claim, not proof.

## Screen before sending, so the email is a heads up and not a pitch

The 20-a-day cap is only affordable if every one of those 20 lands on a domain that verifiably has the defect. Screening is the step that makes the specific finding possible, and the specific finding is the only thing separating this from mass spam.

- Screen the domains before writing a word. All four checks are public and need no access: SPF, DMARC, and MX from a DNS query, and DKIM by trying the known selectors. `email_scan.py` does this and writes a `qualified` flag plus a `defect_codes` list.
- **Gate on the `qualified` column, never on the overall grade.** A `warn` is not a defect. `google.com` and `github.com` both grade WARN on `~all` alone, which is not a problem worth a stranger's inbox. Only a measured defect is, and only the scanner's `defect_codes` list records one. The outreach script filters on `qualified == yes` for exactly this reason; do not loosen it back to an `overall` FAIL/WARN test.
- The finding in the email comes from the scan row, never from memory or from a pattern assumed about that kind of business. Read the row, then write the finding.
- The scan results are a work product, not a formality. The row's finding column is what the email quotes, so a stale scan means a wrong claim sent to a stranger with his own records in front of him.

### Audit the contacts file itself before the first send

The screen runs inside the pipeline, but a contacts CSV is a file on disk that a given run did not produce, so every filter added after it was harvested did not apply to it. Read the file and check these before the first real send, not after a bounce.

- **A list the pipeline did not harvest is unverified, no matter how it is labeled.** A contacts file that arrives from another model, another agent, or a paste has no provenance and no source URL per row, and a status column beside it ("Public contact email", "Public attorney email") is the other tool's assertion, not evidence. Audit it exactly as any on-disk contacts file, and count the surviving rows before quoting any number: a 500-row list where a model filled in every row can carry as few as a couple of dozen addresses, most of them `info@` role desks on large firms. When the number matters, run the harvest yourself; the measured yield of a real harvest is the only figure that has a source.
- **Normalize case before comparing an address to a domain.** A published address is often written in caps (`FRANCES@FORGIONE.COM`), so an apex comparison that does not lowercase both sides reports a mismatch that does not exist and deletes a good row. Lowercase the address and the domain first, then compare. The false positive here is silent.
- **Check for a provenance tail on every address row.** An address that belongs to a different company than the row names is not a typo, it is the harvest having walked onto a partner, franchise, or group site. Drop the row, do not relabel it.

- **Re-check every sendable row against the current brand blocklist.** A contacts file harvested before the Tranco filter existed still carries chains, because the filter only runs at harvest time: one top-100k brand survived in exactly that way. Recompute the apex for each row and test it against `brand_blocklist.txt` on the file as it stands, rather than trusting that the pipeline already did it.
- **Reject a row whose address is on a different domain than the row names.** A contact harvested from a partner, franchise, or group site yields something like `brittanie@tottrg.com` sitting on `charleyssteakhouse.com`. The email's first line asserts a finding about the named domain, so mailing an unrelated company's inbox about it is the exact mismatch the pipeline exists to avoid. Compute it: the address must end with `@<row domain>` or `.<row domain>`.
- **A list handed in from outside is a claim, not a result, and its contact column is the least trustworthy part.** A CSV that arrives with addresses already filled in was not produced by this pipeline, so none of the harvest rules applied to it. Recompute the apex of every address against the row's own domain and drop the mismatches: a row whose address sits on another company's domain is the exact mismatch the whole pipeline exists to prevent. Compare the two domains CASE-INSENSITIVELY, or a perfectly good `NAME@THEIRDOMAIN.COM` reads as a different domain and gets dropped as a false positive.
- **Count what the column actually yields after those drops.** A prefilled column is usually a handful of addresses, not a contact list, and reporting it as one is the number that misleads. Run the real harvest and give the measured figure instead.
- **A free mailbox on a free provider is not a mismatch.** `something@gmail.com` or `@aol.com` sitting on a small shop's row is normal, and it is the address that business publishes. It passes the domain test above only by exception, so decide it by eye rather than by that test alone.
- **Count what is actually sendable, per kind, and say the number out loud before sending.** `84 sendable of 243` is a different sentence from `84 reachable`, and the two get confused when only the total is read. Report the breakdown, because that total is what the day's sends draw from.
- **Never sum two builds into a total without measuring the overlap first.** Measured failure: 305 send-ready from one build plus 547 from the next was reported as 852, when 247 addresses sat in both files and the true unique pool was 605. The overstatement was 41 percent of the real list, and it went out in a written report to Vinny before anyone checked. Dedupe the two files on the address, lowercased, report the union, and treat any "X plus Y" total as unverified until that check has run. Do it before stating the number, not after publishing it.

## Staging into IONOS with send times (the scheduling path, the current method)

Vinny's standing instruction: stop loading these into Drafts for a hand send, and schedule them instead, starting at the hour he names and one every 5 minutes. That is the staging method. `schedule_drafts.py` in `~/money_ideas/` does the whole job in one command:

```
source ~/.config/phantombyte/mailer.env
python3 schedule_drafts.py --offer-url https://phantom-byte.com/email-deliverability-rescue --limit 20 --start 2026-09-22T09:00 --gap 5
```

`--dry` renders and prints the time plan without touching the mailbox. `--start` is local time (America/New_York), `--gap` is minutes. `--csv` and `--emails` default to `email_scan_results.csv` and `contacts.csv`, so a run against another batch must pass both explicitly (the NY batch is `--csv ny500_scan_results.csv --emails ny500_contacts.csv`) and must pass the same pair to `outreach.py`, so the render and the schedule draw from the same rows.

### PRE-FLIGHT: the three checks that make tomorrow's run correct the first time

This run took over 30 minutes for a 5-minute job because the format was wrong and nobody looked. These checks are not optional, and they run BEFORE the mailbox is touched and AFTER it is written to. Skipping any one of them is what produces a second run of the same message and a second apology.

**Before scheduling anything:**

1. **Prove the dedupe index still knows the history.** `state.json` is only the fast index and it can be empty, truncated, or missing while the durable history sits elsewhere on disk. Staging someone who has already been written to is the one failure this whole system exists to prevent, and it is invisible at staging time because the folder and the response codes both look clean. So read the index first, and when it is empty or suspiciously short, reconcile against every history source before staging a single message: every `state.json*` backup, `contacted_domains.txt`, and the addresses in `Sent Items` fetched over IMAP. A candidate whose domain or address appears in any one of those is not a candidate. Report how many were reconciled and how many survived. `outreach_log.csv` is not a substitute here: it records sends, so it says nothing about mail that went out by hand outside the pipeline.
2. **Render one message and LOOK at it as HTML, not as plain text.** Run `schedule_drafts.py --dry` and read the rendered body as the reader will see it. The plain-text source having blank lines proves nothing, because the collapse happened at the API, after rendering. If the rendered body has no `<p>` tags, stop.
3. **Compare the rendered shape against the hand-sent reference.** The last manual send sits in `Sent Items`; fetch it and confirm the new render has the same paragraph count and the same beats in the same order. This is the check that would have caught the collapse before a single message was scheduled.

**After scheduling:**

4. **Read every message back off the folder and verify the body and the send time.** A 200 from the send call is NOT verification: it answered identically for the collapsed body and the correct one. `schedule_drafts.py` now does this itself in `verify_scheduled()` and exits non-zero if anything fails, so a run that did not verify cannot report success. Never report a scheduling run as done off the script's exit code alone if that step was bypassed.
5. **Run one independent read-back of the folder yourself, in the named timezone.** The script's own verifier builds its intended slot in UTC and reads the stored `X-OX-Date-To-Send` in UTC, so its time check cannot fail on a timezone mistake. After the run, fetch the folder yourself and convert each stored epoch with `zoneinfo.ZoneInfo("America/New_York")`, then print the local wall clock next to the recipient. That is the check that proves 9am means 9am here, and it is why a fresh read-back is run even when the script printed `OK` on 20 of 20. Do the copy check inside that same pass, off the STORED message: strip the tags from each body and assert the subject line is absent from the body text, comparing the whole subject string and each of its clauses. That assertion cannot be made from the template, because the collapse or the duplication happens after rendering and only the stored message shows it. Assert the same way that the paragraph count matches the reference send, that `From` carries the account address, that the postal line, the opt-out line, the offer URL and the prospect's own domain are all present, and that the folder count equals the number staged with nothing left over from a probe.
6. **If the read-back failed and the messages are already in the folder, do not re-run the command.** The state save happens after verification, so a failed verification leaves live queued mail that the tracker has never seen, and a second run stages every one of those recipients again. Recover from the folder, never from `state.json`: either reconcile the tracker from the live folder contents, or empty the folder and confirm the count is zero, and only then stage. The cross-cutting rules for this are in the `scheduled-mail-staging` skill.

**The one-command shape, no deviation:**

```
source ~/.config/phantombyte/mailer.env
python3 schedule_drafts.py --offer-url https://phantom-byte.com/email-deliverability-rescue \
  --limit 20 --start <YYYY-MM-DD>T09:00 --gap 5
```

`--start` is a parameter, never a literal to copy: set the date to the day he named, keep the `T09:00` only when he asked for 9am, and confirm today's date off the system clock before filling it in. A staged run always names a FUTURE slot, because a slot in the past is a message that has already left or is about to.

Read the `OK` lines it prints at the end. Each one names the recipient, the domain, and the paragraph count it read off the stored message. `OK` on 20 of 20 plus your own timezone read-back is the only thing that means done.

### The mechanism: the Open-Xchange HTTP API, never the web panel

IONOS webmail is App Suite on Open-Xchange, and it exposes the same API the webmail UI calls. Call it from the shell: never the panel, never a browser, and never IMAP `APPEND` into `Scheduled`, which stores the message with no `dateToSend` and schedules nothing while still returning OK. The endpoint sequence, the payload shape, the required sender field, the recipient shape, the `dateToSend` format, and the HTML content requirement all live in the `scheduled-mail-staging` skill's `references/ionos-ox-scheduled-mail.md`, and `schedule_drafts.py` implements every one of them.

The failures that read as scheduling problems and are not: a staged message with no explicit `from` is accepted, stored, and then killed at send time with `MSG-0037`, never retried; a bare address string in `to` yields "no recipient" at send time while `[None, None, addr]` is read as the literal string `null` and refused with `MSG-1008`; a `folderId` not ending in `Scheduled` means the payload was not accepted and the message landed in Drafts, and the call still returned 200; a missing session query parameter answers `SVL-0002`, which is indistinguishable from a malformed body; and a 200 from the send call says nothing about the body shape, because the collapsed body and the correct one answer identically.

### Verify a scheduling run by reading the folder's real send times

A 200 from the send call is not proof, and neither is a folder count. Read the stored `X-OX-Date-To-Send` header off every message in `Scheduled` over IMAP, convert the epoch milliseconds to local time, and print the full list. That header is the server's own record of when it will send, so it is the only thing that proves the spacing is right. Confirm the first slot is the wall clock Vinny asked for and that each following slot is exactly `--gap` minutes later.

Also confirm in that read-back that a run left no probe or test message behind: a probe scheduled for "now" fires and disappears, which is why the folder count should equal the real list.

### Scheduling marks `state.json` in the same pass

One entry per scheduled domain, `status: "scheduled"`, carrying `scheduled_at` (UTC) and `scheduled_local`, plus the returned mail id. It never writes `outreach_log.csv`, because that file records sends and a scheduled-but-not-yet-sent message is not one. Back `state.json` up before writing, same as the draft path.

### The live pre-send recheck does not run at schedule time

`recheck_defect` runs inside `outreach.py` at the moment of a real send. Scheduling through this API bypasses `outreach.py` entirely, so the finding was confirmed when the message was rendered and not again when it leaves. That is the trade the scheduling path makes, it is Vinny's call to make, and it is the one thing to name if he asks what changed.

## Staging drafts into IONOS (the manual-review path, superseded)

Kept only for the case where Vinny asks for drafts again. The scheduling path above is the current method. The command shape, the four-step procedure, the `state.json` marking rule, and the IMAP pitfalls (UID not sequence, restage keys on the folder read, copy to Trash before delete) are in `references/ionos-draft-staging.md`.

## The send cron (agreed direction, NOT built)

Vinny's plan: he hand-sends the first week himself, then a cron takes over the sending, with the drafts still loaded the night before so he can check them. The cadence is one every couple of minutes, deliberately slow. Build it only when he says go, and only after the hand week has produced reply data to design against. Note that as of 2026-09-22 the scheduling path above already puts real send times on the messages, so the scheduling half of this is built and the piece still owed is the reply handling, not the send.

- **A send cron is a rule change, not a rule violation.** The standing rule "Hermes drafts; you review and send manually" is HIS rule, written from his instructions, and he can lift it. Never present a standing rule as though it were an external obstacle: name it as his call, and reserve "this cannot move" for a mechanism whose removal would make a claim false, which is the live pre-send recheck. Presenting his own preferences as blockers, next to a real host quota, makes them read as law.
- **The host limit is not the constraint at this cadence.** IONOS's own help page, "What restrictions apply to sending bulk emails?", gives Mail Basic and Mail Business: over 30 days old, 500 emails per hour; 15 to 30 days, 400; 8 to 14 days, 100; 0 to 7 days, 50. Past it the server answers `450 Mail send limit exceeded`. Google Workspace on IONOS is 200 per day, and Exchange is per-minute plus a per-day recipient cap. One send every 2 minutes is 30 per hour, about 6 percent of the allowance, so the sending side needs no negotiation with the host. Read the live page rather than quoting a remembered number.
- **Space the sends unevenly.** A fixed interval is a regular heartbeat, and regularity is itself a pattern a receiving filter can read. Jitter each gap by a minute or two.
- **Pin the send window.** A cron that misfires outside business hours stamps 3am on a cold email, which reads automated to a filter and to anyone who notices the timestamp.
- **The live pre-send recheck stays.** `recheck_defect` is what makes the email's first line true at the moment it leaves. It runs fine inside a cron and it is the one piece that cannot be traded for speed.
- **The real constraint on automating the send is the reply, not the send.** A cron sends but nothing answers, and the reply side has no rule attached: Vinny is not at a desk and a response cadence is his call, never an assumption baked into this pipeline. Learn from the hand week when replies actually land before designing a schedule; if they cluster while he is away, a faster sender makes the operation worse rather than better. Say this when he asks what could hurt.
- **Never state a rule as his when he never set it.** He named this directly: rules he did not write appearing as his instructions is disrespectful and reads as words put in his mouth. If a line in this skill was authored here rather than given by him, say so plainly when it is raised, and never cite it as his preference.

## Standing rules
- Send from your domain. No blast tool sends unreviewed.
- NO send cap. There is no daily number, no default, and no standing throttle in either `outreach.py` or `schedule_drafts.py`: the count is whatever Vinny says for that run, and nothing is sent until he names it. The rate he does name is a deliberate warm-up he is running on purpose (20, then 50, then 100, climbing), weekends off, so read it as his strategy and never state a volume limit to him as though it were governing. Never state a rate as a limit he is working around even when the ramp is visible in the data; account age alone is not the signal, the cadence is. The contact priority for the send order is in `references/contact-priority-and-send-order.md`, and the cadence and runway math is in `references/send-cadence-and-list-economics.md`.
- **Do the arithmetic before raising a constraint, and name only constraints the numbers support.** Three separate claims were made in one session that did not survive a single calculation: that a 7-month-old account made reputation a non-issue (account age is not sending history, and the ramp was deliberate), that daily quota was something to watch (30/hour against a 500/hour allowance), and that harvesting was a throughput problem (1,852 domains/hour measured, so refill is hours of machine time). Each one was a concern raised against his plan without a number behind it. When a worry comes to mind about his approach, compute it first; if the arithmetic does not support it, do not say it. A constraint named without a figure is noise, and he is entitled to assume the plan was reasoned.
- Filter prospects: broken SPF/DKIM/DMARC only; skip clean.
- Hermes drafts; you review and send manually. Never fully automate send, unless Vinny orders the automated send. This is his rule, not an external constraint, and he has named the send cron as the direction once the hand week closes: do not cite it as a reason the plan cannot happen.
- Include one-line opt-out ("reply stop to remove").
- Separate business cash from household / SSI-linked accounts.
- No fabricated benchmarks. Every claim traces to script result or file.
- Proper punctuation; no em dashes.

## Long-running scripts: narrate the run, never go silent

Vinny stated this plainly and it is a standing rule, not a one-off: "When I know what's going on I don't get mad. It's when you disappear and I have no idea what you are doing I get angry." A slow script is fine with him; silence is not.

- Before starting a long job, say what is running, what it is doing, what it costs, and roughly how long. He knows a script does not spend his AI credits, so wall-clock time is acceptable when he can see it.
- Check in with a live progress number while it runs ("73 of 243"), taken from an actual read of the log or output, never estimated from memory.
- If a run will be silent for minutes, say so up front rather than going quiet and reporting at the end.
- **A multi-call research or fetch sequence counts as a long job even when no script is running.** Ten scrapling calls and a rules read across five sites is several minutes of him seeing nothing, and his question is "what are you doing" rather than a complaint about the result. Send ONE line naming what is being fetched and that nothing has been posted or sent, then keep working. Do not answer a "what are you doing" with a plan for what you will do next.
- **Report a finding the moment it lands, do not hold it until asked.** When the sourcing method and the contact method were both worked out but never stated, he had to pry it out of the transcript and called it exactly that. A result sitting in a scan log that he has not been told about is worth nothing to him, and it reads as withholding rather than as work in progress.
- If a check finds a problem, say the problem and what it means for the run in the same breath as the progress number. Do not save the whole picture for one summary at the end.
- The rule applies to any multi-minute job, not just this pipeline: scans, harvests, downloads, builds.

## Franchise and national brands are not prospects

A geographic sourcing query returns the national chains that happen to sit inside the bounding box. The first run of 243 qualified rows surfaced `adesa.com`, `advanceautoparts.com`, and `7-eleven.com`.

- A chain has an IT department and a vendor, not an owner reading his own inbox, so no $500 one-domain fix lands there. It also cannot plausibly receive a personal heads up.
- Filter them before the contact pass, not after: an email sent to a chain address is a wasted send out of the day's 20, which is the one budget that cannot be recovered.
- **The screen is a global-domain-rank blocklist, not a location count.** Counting how many times a domain appears in a geographic extract does NOT work: it flagged local single-location businesses as chains (`1920yborcity.com` at 3 locations, `acropolistaverna.com` at 3) while an actual chain (`advanceautoparts.com`) appeared once and slipped through. The count measures how many branches were mapped in one bbox, nothing about the business.
- **Use Tranco (`https://tranco-list.eu/top-1m.csv.zip`), a public 1M-domain popularity ranking. A registrable domain inside the global top 100,000 is a national brand, not a business with an owner reading his own email.** Download the zip once, key it by registrable domain (collapse `locations.x.com` and `x.com` to the same apex), and keep the set as a reusable `brand_blocklist.txt` so scans do not re-download it. Measured on the 243 qualified rows: the top-100k list dropped 30 chains (`7-eleven.com`, `arbys.com`, `cvs.com`, `apple.com`, `chick-fil-a.com`, `amtrak.com`, `autozone.com`, `amctheatres.com`) and left every local business standing, including the ones the location-count rule had wrongly cut.
- Also drop franchise locator subdomains by name (`locations.`, `locators.`, `find.`, `restaurants.`, `stores.`, `pizza.`, `shop.`, `order.`, `menus.`) and `.gov`/`.mil` hosts. Tranco catches the parent brand; these catch the store-finder subdomain that shares the parent's apex.
- Tune the cutoff only upward if a brand still gets through, never downward: a false positive here silently deletes a real prospect from the list, while a false negative only costs one send out of 20.
- **A curated list of "top businesses in a city" is a different pool from a geographic extract, and it carries far more chains and institutions.** A hand-assembled 500-row New York list, drawn from the largest names in each category, put 83 of the 500 (16.6 percent) inside the Tranco top 100k: Skadden, Latham, Kirkland, KPMG, Deloitte, McKinsey, Bain, Accenture, Chubb, Compass, Etsy, Northwell. Whoever wrote the list selected by prominence, and prominence in a large city means a headquarters address for a national firm. Run the blocklist as always, and expect to drop roughly a sixth of such a list before any contact work, not a twelfth.
- **A domain with no rank can still be the wrong buyer, so rank alone is not the filter.** Institutions and function desks slip through a popularity list entirely: a hospital system at rank 141,862 is caught by rank, but `careers@`, `registrar@`, `franchise@`, `mediarelations@`, and `marketing@` are caught only by reading the mailbox. `prospect_fit.py` runs both tests together for this reason.

### Filter the marginal prospects yourself, never hand them back as a decision

When a marginal prospect surfaces (a mid-size organization, a function desk, a domain that is technically not a chain but clearly not the buyer), the standing instinct to flag it as a risk and ask what to do is wrong here, and Vinny said so directly: the draft step exists so the agent drops these, and raising them for him to judge is the agent handing back its own job.

- **The filter exists to catch the bulk so the review is light.** Put the rule in the pipeline, not in a note to him. If a new class of bad prospect keeps appearing, add a signal to `prospect_fit.py` rather than reporting the pattern as a concern.
- **Never present a screening decision as a choice when the send path can make it.** A run that says "3 of these look like hospitals, want me to remove them?" is asking him to do the screening. A run that says "3 dropped, here are their reasons" is doing it.
- **Report drops as a count with reasons, and only when a run actually happened.** A list of what was filtered is useful; a warning about what might slip through before any run is the noise this rule bans.

## Diagnose from the live records first, never from memory
Pull the current DNS state before writing any finding or any fix. If `dig` is not on PATH, query Cloudflare's DoH JSON API instead of installing anything:

```bash
curl -s -H 'accept: application/dns-json' \
  "https://cloudflare-dns.com/dns-query?name=<name>&type=TXT" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('status',d.get('Status'));[print(' ',a.get('data')) for a in d.get('Answer',[])]"
```

Status 0 means the record exists; status 3 means NXDOMAIN (the record is missing, which is itself a finding). Query these names: the apex TXT (SPF plus every verification record), `_dmarc`, MX, NS, and the DKIM selectors (`s1`, `s2`, `default`, plus any provider-specific selector). A CNAME answer on a `_domainkey` name is that provider's hosted DKIM; a `TXT` answer is the raw public key.

Read the result for these, in order: does SPF exist and how many DNS lookups does it spend (10 is the hard limit, each `include` and each nested include costs one); does DKIM resolve for every sender that actually sends as this domain; is `_dmarc` a bare `p=none` with no `rua`, which is a record that does nothing; and is there a DNS record naming a sender the site no longer uses.

## Fix procedure (staged, reversible)
1. Back up the full record list before touching anything. Every change must be reversible in one minute.
2. Verify each provider's DKIM is actually enabled for this domain, and get written authorization before editing DNS.
3. Publish the DMARC record with a reporting address, still at `p=none`. Never jump straight to enforcement.
4. Leave SPF at `~all` until the DMARC reports show every legitimate sender aligning, then tighten to `-all`.
5. Only then move `p=none` to `p=quarantine`, and after another clean window to `p=reject`. Each stage is a separate authorization from Vinny.
6. Prove the result twice: raw resolver output from two independent resolvers, then the `Authentication-Results` header off a real delivered message, quoted verbatim. Resolver proof alone stops at the DNS layer, so never claim received-mail proof you have not actually read.

Received-mail proof without waiting on anyone: read your own mailbox over IMAP. The send credentials work for reading, and every delivered message carries the header verbatim.

```python
import imaplib, ssl, email
M = imaplib.IMAP4_SSL('imap.ionos.com', 993, ssl_context=ssl.create_default_context())
M.login('hello@phantom-byte.com', <mail password>)
M.select('INBOX', readonly=True)
st, ids = M.search(None, 'ALL')
for i in ids[0].split()[-5:]:
    st, data = M.fetch(i, '(BODY.PEEK[HEADER])')
    print(email.message_from_bytes(data[0][1]).get('Authentication-Results'))
```

This also closes the mailbox-existence question in one loop: send to the address, then read the bounce. Never report a delivered-mail proof you have not printed the header for.

When handing this pipeline to another agent, send it as ONE complete prompt file, written to disk and emailed to him as an attachment. He does not want it split across a chat message and an addendum, he does not write prompts himself, and a prompt long enough to be useful is long enough for the chat to truncate it, which is exactly how he ends up asking for the file by email anyway. Never hand him prompt text in chat when he asked to be emailed. Pi runs on the Windows side of the same machine, so the prompt must carry the WSL boundary rules or it fails on the first command; the full template and the cross-boundary rules are in `references/pi-handoff-prompt.md`.

Full record strings, prerequisite checks, and the verification and reporting format live in `references/dmarc-remediation.md`. `scripts/verify-deliverability.py` runs the record check and the received-mail proof in one shot.

## Offer page: Socratic method

The offer page is written in the Socratic method, and that is the required shape for every offer page in this system. He asked for it directly and confirmed it is better for this buyer.

- Open with a question the reader answers in their head, then hand them the conclusion as their own finding. Never open with an assertion about their business; it reads as a scare tactic and triggers the fight response.
- Put the questions at the open, around the problem section, on price justification, and on the monitoring close.
- Keep mechanics, the deliverables list, the guarantees section, and the process plain and declarative. Ambiguity in those parts costs the sale, and trust gets built there.
- He will supply the mockup and have Pi deploy it. Do not build or deploy the page unprompted; edit the existing HTML when asked.
- Headline shape he picked over a plain interrogative: a flat statement followed by the doubt, two beats. "You sent the invoice. But did it actually arrive?" He rejects a bland question headline, so this shape is the one to reach for. Give him one recommendation and stop; offer alternatives only if he asks, because a menu of headline options stalls him.
- In the numbered question block, number the lines and drop the question marks entirely. He asked for exactly this on the three-question section, and it is the shape to reach for again.
- When describing a technical deliverable, name both delivery paths and what each one requires. "Every change applied, or a copy-paste sheet" is too vague. State that we apply the change ourselves if they hand over DNS access, or send a copy-paste sheet if they would rather click it in, and that we verify the result either way.

## Offer page: PhantomByte branding

He approved a light branded shape for the offer page. Add exactly three pieces and no more:

- A wordmark at the top, above the h1: the word `PhantomByte`, uppercase with letter spacing, in the accent color, linked to `https://phantom-byte.com`. No logo image.
- The accent color is PhantomByte purple `#9d4edd`, taken from the live `--purple` custom property on phantom-byte.com. Never ship a blue or generic accent on a PhantomByte page; pull the palette off the homepage rather than inventing one. Apply it to the wordmark, numbered question markers, and any highlighted box border and tint. Leave the pass/warn/fail status colors alone, they carry meaning.
- One footer line: `PhantomByte. Email infrastructure, done by email.` also linked.
- The meta title prefixed with the brand, joined with a pipe: `PhantomByte | <offer name>`. **Never a spaced hyphen.** The branding rule originally prescribed `PhantomByte - <offer name>`, which directly contradicts the structural rule below that forbids a dash as a separator in the copy. A pipe satisfies both, and it is what shipped on the live page.

Do not add a banner, tagline block, or logo wall. The page's strength is that it has nothing to hide behind, and a heavy brand header fights that. The page reads as an anonymous one-person service without a name, which is fine for a local tradesperson and wrong for technical work.

Before adding a brand link, fetch the brand homepage and confirm it looks like a real business. A link to a thin or half-finished site costs more trust than the name earns. `curl -s -L` the homepage and check the title, the meta description, and the visible text length before you link it.

Verify an offer page structurally after every edit with a quick Python pass over the file: count em dashes, en dashes, and spaced hyphens (all three must be zero), check tag balance for `div/ul/li/p/table/tr/td`, and confirm the headline and the edited section render as intended. He rejects dash-as-separator anywhere in the copy, including inside an HTML page, so scan for `\s-\s` and not just the unicode dashes.

## Offer page: a real form, never a mailto button

The standing solution for every offer page CTA is an inline form that POSTs to the existing contact endpoint. Do not ship a `mailto:` button.

- `mailto:` was the first attempt and it failed on the user's own machine: the top button did nothing, which reads to him as a broken page. A `mailto` only fires when the visitor has a mail handler registered and signed in, so any desktop visitor who reads mail in a browser tab gets silence with no error. Never diagnose that as a Windows handler problem and stop there. Treat a mailto as the broken option and give the page a form.
- The endpoint already exists and is live: `https://phantom-byte-contact-ionos-1091380733401.us-central1.run.app/api/contact-form`. It accepts `{name, email, message, domain, source}` and emails the submission to hello@phantom-byte.com. Reuse it; do not stand up a new service or a third-party form host.
- Send `source: "deliverability-offer-page"` so these submissions are separable from the homepage form in the inbox.
- The top CTA anchors to the form (`href="#start"`), it does not open a mail client. Keep that pattern.
- Include a hidden honeypot field and a visible status line that reports success or failure, so a failed send does not look like a silent success.
- Backend source lives at `/mnt/c/Users/<user>/phantom-byte-contact-api/server.js`, with git remote `github.com/vincentsativa/phantom-byte-contact-api`. Edit it there. Pi deploys it; see the deployment boundary below.

The dash rule still applies to any href, not just the visible copy. A subject like `Deliverability rescue - my domain` ships a dash-as-separator inside a URL, so scan the decoded value and not only the rendered text.

Verify every button after an edit by parsing the markup and printing what each one resolves to, rather than reading it, and confirm the page contains no `mailto:` at all.

When a task names two deliverables, land the one the user can SEE first. Writing the backend before the page left him staring at an unchanged page and asking where the form was. Page first, backend second, and never leave a requested visible artifact absent while working on a hidden one.

## Contact form: proving the address is real

The submitter's email is not trusted until they prove it, because you do not want a fake address in the inbox and you do not want a typo to burn a findings-sheet reply. This is a double opt-in, and the design is deliberately stateless so it survives a container restart with no database.

1. On submit, email the owner immediately with `[UNCONFIRMED]` in the subject, carrying the domain and message, and set `replyTo` to the submitter.
2. Email the submitter a confirmation link. Sign the payload as `base64url(json) + '.' + base64url(HMAC-SHA256)` with a key derived from configuration, and expire it in 48 hours. Verify with `crypto.timingSafeEqual`.
3. `GET /api/verify?token=...` emails the owner a second notification marked `[CONFIRMED]` and renders a plain thank-you page.

This gives him a clean signal: an unconfirmed submission is not a lead, a confirmed one is. Full implementation notes in `references/contact-form-verification.md`.

## Payment

PayPal hosted checkout, `https://www.paypal.com/ncp/payment/VMB4RLLDSMGKG`, $500. Net is about $485 after the roughly 3 percent commercial fee. It is the fast path and it works today, so lead with it.

- A payment link produces a transaction, not an invoice number. The standing log rule wants client, amount, and date paid, so for anything above a one-off use PayPal invoicing instead: same fee, adds a real numbered invoice and a paper trail. Add Stripe once volume justifies it.
- Never use Gumroad for the $500 service. Ten percent flat takes $50 off every $500 job. The rule is price-dependent, not absolute: low-price digital products on this project (the $29.99 DIY guide) sell on Gumroad, where the fee is about $3 and the marketplace is worth it. Service on PayPal, tutorials on Gumroad, never mixed.
- Venmo or Zelle at this price is wrong: no invoice, no buyer protection, and personal accounts used for business breach terms.
- Payment-first still works with a link, because PayPal hands over the payer's address. The follow-up email asks for the domain.
- Business money must not land in an account wired to household benefits. Confirm the payout destination before the first payment arrives.
- He asked whether the link should go on the page. Default to email-first and send the link only after a yes, unless he says otherwise.

## The free domain checker funnel (approved expansion)

The rescue gains a free front door: a browser-side domain checker feeding the same $500 service. Full plan, keyword map, competitor gap, and the tutorial-outline prompt live in `references/free-checker-funnel-plan.md`. The rules that govern every future pass at it:

- ONE page, blended into the offer page at `/email-deliverability-rescue`, not a separate URL. Vinny overruled the separate-URL plan: the checker weaves into the existing Socratic offer page between the hero and the price block, and they are one funnel on one URL.
- Build the blended page FROM the live offer page's raw HTML, never from a homepage palette extract. Pulling the brand colors off a different page of the site produces a page that reads as a different site; he rejected exactly that. Fetch the live page HTML first and edit it, keeping its stylesheet, theme, and copy structure untouched.
- A mockup of an interactive tool ships with WORKING logic, not a placeholder results block. The checker runs client-side over DNS-over-HTTPS (Cloudflare `application/dns-json`), no backend, and is verified against known domains before delivery; a static mockup is returned as broken. Port the record logic and the SPF lookup counter from `email_scan.py`'s tested implementation rather than rewriting them.
- Verify the browser checker with Playwright: load the file, fill the input, click, wait, and read the findings table, then cross-check any surprising result against a raw `curl` DoH query before trusting it. The DOM says what the code rendered; only raw DNS says what is true.
- Reset the findings accumulator at the start of every check run, or a second check leaks the first domain's severity counts into the new verdict. Verify with a sequence test: run a broken domain, then a clean one, and assert the clean one reports clean.
- A null MX (`0 .`) parses into a truthy answer list and grades as Configured under a naive presence check. Match the literal record string and grade it as the defect it is, same rule the scanner enforces.
- Results appear with NO email, account, or signup gate, ever. That absence is what makes the tool shareable, and it is the one requirement that cannot be traded away.
- Four fixed severity states used everywhere: Confirmed problem, Warning needs attention, Informational, Unable to determine. Never a score out of 100, never a deliverability percentage. DNS proves a record missing; it cannot prove where mail lands, and the page says so in a visible honesty box.
- A DKIM miss is always worded "no key found on common selectors," never "DKIM not configured." Custom selectors cannot be enumerated from outside, and the wrong wording is a false claim to a stranger with their own DNS in front of them.
- The free checker never generates the corrected record. The $29.99 guide teaches them to write it; the $500 service writes it for them. Cross that line and the paid guide is dead.
- The tutorial sells on Gumroad at $29.99; the $500 service stays on PayPal. The never-Gumroad rule above is price-dependent, not absolute: at $500 the fee is $50, at $29.99 it is about $3 and the marketplace is worth it. Never mix the two channels.
- Capture reuses the live article wiring verbatim: `scripts/web-push-client.js` and `scripts/email-signup.js` from articles.phantom-byte.com, the `.signup-form` class, the `phantombyte-push-btn` id. Pi deploys the scripts with the page; use a separate MailerLite group so checker subscribers measure apart from the article list.
- The MVP ships without blacklist or reputation checks. DNSBL zones block or misreport from public DoH resolvers, and a wrong blacklist accusation is the worst false positive the tool could produce.

## Promotion venues for the offer

When Vinny asks where to promote the offer online, the researched 28-venue list (Reddit, Slack, vendor forums, Q&A sites, mail-industry lists, social, developer, platform communities), each with its promo angle and a three-tier sequencing plan, lives in `references/promotion-venues.md`. The universal angle: one sentence of record-level diagnosis, one Socratic question, then the service. Verify venue claims against live threads before writing new material; a venue entry written from inference instead of a live-checked thread title gets rejected on review.

**Classifieds are a separate venue class with a harder rule set than the community venues, because a listing that breaks a content rule is removed rather than downvoted.** The live-read rules for Oodle (no links to external lead generation forms, no email addresses in listing content, no phone in the title, one region, one category) plus the verified state of the other classified sites and the account-setup route are in `references/classified-ad-venues.md`. Read it before writing any classified ad; the ad it produces carries no URL, no address and no phone, with the venue's own reply button as the only route.

**Before drafting for a specific venue, read that venue's own rules page live.** For daily.dev the rules decide the whole shape of the post (self-promotion as primary purpose is a rejection, headers are ALL CAPS plain lines, corporate and personal blogs are excluded from Suggest a Source) and the fetch path plus the post shape are in `references/dailydev-and-content-venue-submission.md`. Do not draft a venue post from a remembered rule; the rules move and a rejected post costs the venue.

### Reddit rules (ban-happy, confirmed by Vinny)
- The offer link never goes in a post. r/coldemail bans self-promotion outright; a fresh account with a service link in its profile is flagged before the comment is read.
- The working sequence: two weeks of comment-only answers to fresh deliverability threads (sort by New), no link anywhere, not even the bio. Pitch only in DMs when someone asks "how do I fix this" or "who can do this for me."
- The scanner is the comment's proof layer: scan the domain named in the post, reply with the actual defect code and record string. Same specific-finding mechanic as the cold email, delivered publicly.
- r/msp is the most tolerant venue of the four and the natural white-label/referral play.

### dev.to and guest-post style content
- Format: teach-first walkthrough with real record strings from the scan CSV as the evidence. A closing offer link framed as "if you'd rather this be done for you" is accepted practice on dev.to because the article taught the fix first.
- Expectation: slow-burn SEO play, not high-intent leads. Do not promise leads from a content post.
- The proven post shape, **applicable only when Vinny orders a data piece and names the scan data as the source**: title leads with the measured number ("243 of 300 had broken mail records"), breakdown by defect code, real record strings pulled from the scan CSV (skip chain domains when quoting examples), the three-checks-in-ten-minutes section, the staged fix, then the challenge question and link. Voice per `phantom-byte-writing-style`; for dev.to the record strings belong inline and headers use the `// HEADER` plain-prose shape. **This shape is not the default for a post request.** When Vinny names one page or one article as the source, that page is the post, no scan CSV is opened, and no dataset is rebuilt: on 2026-09-22 a "write me a hackernoon post for <offer page>" request was turned into an unrequested audit of three scan CSVs, a rebuilt 1,822-domain set, and live re-verification of record strings, which burned ten minutes and produced a post citing figures he never chose. If the named source has no numbers, the post has no numbers. The measured-number shape above applies only on his explicit order to use the data.
- Vinny posts content himself when he says "tomorrow I'll put it up": the deliverable is the finished, verified draft emailed to him, never an outline plus an offer to write.
- **daily.dev is a venue with its own rules and its own post shape, and they differ from dev.to's.** Self-promotion as the primary purpose of a post is an explicit rejection there, the AI-writing clause makes padded framing prose a real risk, corporate and personal blogs are excluded from Suggest a Source (Squads and direct posting are the open routes), and section headers are ALL CAPS plain lines rather than `// HEADER`. Read the rules off its live docs before writing, and follow `references/dailydev-and-content-venue-submission.md` for the fetch path, the rule list, the post shape, and the pre-send verification.

## Notification channels for deliverables

- Email is the delivery mechanism; a Telegram message is only the doorbell. When he says "email me the report," the SMTP library gets invoked, never chat text.
- For Hermes-initiated notifications (report sent, cron finished), Telegram is the reliable channel. Do not promise an iMessage notification: the shared-tier Photon line can only reply inside a thread the user texted first, so gateway-initiated sends to his number are refused ("Target not allowed for this project") and sends to the assigned line fail validation. Photon works fine inbound and in-reply; the initiate direction is the tier restriction. If he wants iMessage notifications from Hermes-initiated flows, that needs his direction (dedicated line or config change), not an improvisation.
- Never conclude a channel is broken from one adapter error: read the gateway log for the specific handler error and state which direction failed.

## Deployment boundary (hard)

Never deploy anything, ever, for any project. No `gcloud`, no `docker push`, no `gcloud run deploy`, no push to a deploy branch. That is not in scope for any task and the user has stated it flatly and repeatedly.

- Never inspect the user's cloud accounts either. Running `gcloud auth list`, `gcloud config get-value project`, or `gcloud run services list` to see how a service is hosted is the same violation as deploying. He did not ask for it and it is his infrastructure.
- This applies even when the task is "make the endpoint do X." Write the code, verify it locally with a syntax check, and hand it over. Pi and Vinny ship it.
- A read-only-sounding command against his cloud account is not read-only in his eyes. Stay out of it.

## Outreach email: the same Socratic shape

The rule governs the cold email, not just the page, and he stated it plainly: Socratic is the best way to get the click.

The email opens with the ally beat, and Vinny specified that beat himself. It is what keeps a specific finding from reading like a mass email: you looked at their records, you hit the same class of problem on your own domain, so this is a heads up rather than a pitch. "It's a heads up, NOT mass spam."

- Beats per email, in order: the finding as a plain fact, the ally beat (heads up, not a pitch), then a question opening with "So" that makes the reader answer it about their own domain, then the fix and price as one short declarative paragraph, then the free findings-sheet CTA.
- The finding must name the actual broken record, not a general concern. "Your SPF record ends in ~all" is unarguable and provably looked at. "You may have deliverability issues" is what a mass sender writes, and it forfeits the ally position the beat is there to earn.
- The subject line stays a question that names their domain and carries the specific finding. It is what gets the message opened, and it plus the first line are what let a stranger say plainly what this is about.
- **The subject line lives in the `Subject` header and appears NOWHERE in the body.** A body that opens with the subject line makes the recipient read it twice, and it is the tell of a template merged into a message after the fact. So `TEMPLATE` does not carry a `Subject:` line, `build_message` returns the subject as a header value and strips any leading `Subject:` line from a rendered body, `send_one` refuses a body that still carries one, and `stage_drafts.py` refuses to stage one. Every one of those four guards stays: the render-time strip is what fixes a caller that filled the template itself, and the two refusals are what stop it reaching a stranger if the strip is ever bypassed. Verify it against the mailbox, not by reading the template: fetch every staged draft and assert its body carries no `Subject:` line.
- Keep the body short enough to read on a phone.
- The trust beats stay declarative, never interrogative, same as the page.
- `outreach.py` carries one variant per defect code across `SUBJECTS`, `OBSERVATION`, `QUESTIONS`, and `CTAS`: `spf_open`, `spf_over_limit`, `spf_void`, `spf_missing`, `null_mx`, `dkim_revoked`, `auth_alignment`, `dmarc_none`, `dmarc_missing`, `spf_weak`, `no_reporting`, plus `generic`. `pick_template` selects by reading the row's `defect_codes` against a priority list, so the email names the defect that was actually measured. Add a variant to all four dicts together when a new defect code is added, or the row falls through to `generic`. The ally beat is a single module constant `ALLY` inserted into `TEMPLATE`, because it is identical for every variant. The template slots are `{observation}`, `{plain}`, `{ally}`, `{change}`, `{question}`, `{value}`, `{cta}`, `{offer_url}`, `{no_pitch}`, `{postal_address}`; a slot missing from the `.format()` call ships a literal brace into the sent mail.
- Never put a claim about our own domain into the ally beat that our own records cannot back. "We had this same issue" is true while phantom-byte.com scans FAIL, and becomes a false claim the moment the fix ships. Prefer a formulation that stays accurate either way, such as "we went through our own mail records and found things we had never noticed", and check the current scan of our own domain before strengthening it.

Verify the copy by rendering it rather than reading it: import `outreach.py`, call `build_message` on one synthetic row per variant, and print each subject and body. Assert no literal `{domain}` survived and no dash-as-separator appears. Five rendered messages take a few seconds and catch the two silent failures that only show up in sent mail.

The full verification set (render, send-and-read-back, every refusal, the dedupe gate, and clearing test artifacts before a real run) is in `references/outreach-send-verification.md`. Run it before any real prospect is written to.

## Offer page files live on the Windows side

The mockups sit under `/mnt/c/Users/<user>/OneDrive/Desktop/MONEY MAKING OPPORTUNITIES/offer-pages/`, not in `~/money_ideas/`. Search there before saying a page does not exist. `write_file` will refuse to overwrite one until it has been read in full in that session, so read it first, then write.

Host offer pages on `phantom-byte.com` (the domain the outreach sends from, so sender and link match), not on `vincentsativa.com`, which is the personal brand. Deep pages like `/deliverability/` earn no search traffic on their own; the indexed articles on `articles.phantom-byte.com` are what pull traffic, and each service page should have one explaining article linking to it.

## Procedure

**For a scheduling request, the job is one command. Read `schedule_drafts.py`'s output; do not rebuild the sequence by hand.** The full pre-flight, the command shape, and the verification are in the scheduling section above. The steps below describe the gate chain it drives.

1. Check ~/money_ideas/ scripts. Reuse; do not rebuild unless broken.
2. Filter scan results to broken rows only.
3. Hermes writes drafts pulling finding from row. You review full draft.
4. Send manually, 20/day, link offer page, include opt-out.
5. Deliver fix; offer $250/mo monitoring; ask for referral.

## Explaining why the fix was staged, when he asks why it was not done in one shot

He will push back with "why wasn't it done right the first time" and he wants the mechanism, not a justification. Answer it in this order and stop:

1. Name the unknown: at the time, nothing on paper said which of the records on the domain were still in use. The domain carried SendGrid DKIM records (a channel Vinny keeps as a deliberate backup, not a stale one) and a MailerLite setup with no public selector, and there was no report history to say which of them actually sent.
2. Name the failure mode that forced the order: publishing `p=quarantine` before that was known would have sent every newsletter from a failing platform straight to spam, with no way to tell why.
3. Name why the first stage is not a hedge: `p=none` with `rua` is behavior-identical to what was already live, so it cannot break sending, and it is the only mechanism that produces the sender list. The step order is the work, not caution.
4. Close with what the report proved, in numbers, and state that the fix is safe to advance now because the unknown is resolved.

Do not answer this question with a narrative of what happened, and do not answer it with an apology. He is checking whether the sequence was reasoned or sloppy; show the reasoning in a few lines.

## Pitfalls- **Do not open the IONOS web panel or drive a browser for this pipeline. The API does the whole job.** The panel route burns a 2FA round trip to a phone, which stalls the task waiting on a code that has to be read out and typed in. Every scheduling and sending step here is a direct HTTP call from the shell, and there is no step that needs a page loaded or a button clicked. When a task says "use the API", that is what it means: find the endpoint the webmail UI itself calls and call it from the shell.
- **Do not stop at the first working-looking response.** The largest time sink on 2026-09-22 was treating a 200 from the send call as proof the message was right. It proved only that the server accepted the request. Look at the stored message before saying done.
- Auto-sending destroys deliverability; manual review is guard.
- Fixed scratch paths (e.g., /tmp/fetch.py) fail on second run; use mktemp dirs.
- Never name a helper script after a Python standard-library module you also import. A scratch file named `email.py` shadowed the stdlib `email` package, and `import requests` then died with `AttributeError: partially initialized module 'requests' has no attribute 'post' (most likely due to a circular import)`, because `urllib3` imports `email.errors` from the shadowing file. The error names `requests`, not the real cause, so check the script's own filename first when a stdlib import breaks inside a scratch dir.
- Unseparated household payments risk SSI landmines.
- Fabricated "deliverability %" breaks trust; report record state only.
- A stale sender in SPF or DKIM is the common hidden defect. A domain often carries records for a platform the owner stopped using, and a bare `p=none` DMARC hides it because nothing enforces alignment. Check what the records say against what the owner says they actually send with, and ask which platform they no longer use.
- Never publish a DMARC record whose `rua` mailbox does not exist and cannot receive. It points the reports at a black hole and the monitoring window tells you nothing.
- **An SMTP `RCPT TO` probe is EXACT on a host that discriminates, and proves nothing on a catch-all. Test both, on the same host.** The blanket claim that "hosts answer 250 for unknown recipients to avoid address harvesting, so a probe passes for addresses that do not exist" is true only of catch-all domains, and stating it as a rule sends the next person away from the check that actually works. Measured against the 2026-09-28 hard bounces: on every host that discriminates the RCPT verdict was exact, matching the provider's own DSN address for address (550 5.1.1, 552 5.2.2, 554 5.7.1); the cases RCPT could not prove were catch-alls, including Google Workspace, which answer 250 for any local part. The rule that separates the two: probe the real address, then probe a random local part at the same domain. If the random one is also accepted the domain accepts anything, so the 250 proved nothing: report CATCH_ALL and keep the address. If the random one is rejected the domain discriminates, so the 250 on the real address is proof the mailbox exists. Never report DEAD on a 4xx, a timeout, or a refused connection; a probe that did not run is not evidence a mailbox is gone, and a wrong drop deletes a real prospect. The real send plus the bounce read stays the backstop for the catch-all and accept-then-bounce cases that RCPT cannot see.
- Point `rua` at a mailbox that already exists rather than creating a dedicated one. The goal is reports landing in a working inbox, and a new mailbox is just one more thing that can be missing.
- Do not add MTA-STS, TLS-RPT, or CAA, and do not touch MX or the verification TXTs, as part of a DMARC fix. Scope creep on DNS is how a mail fix becomes a mail outage.
- `p=none` to `p=none` with a `rua` added cannot break sending. It is behavior-identical to what was already live. Say this when he asks whether a change is safe, because the risky version is `p=reject` and that is a separate authorization. With the API route the failure modes are a bad key or a wrong record id, both of which fail loudly and change nothing.
- The confirmation link is built from `BASE_URL`. It defaults to the live Cloud Run URL, which is correct in production, but a local run renders `127.0.0.1:<port>` into the emailed link. If the service ever moves, set `BASE_URL` or every confirmation link breaks silently. Read the rendered link out of a delivered email to confirm the host.
- A verification token is long enough that terminal output elides it mid-string, so a `grep` for it looks like a failure when the mail is fine. Extract the token in Python and print only `len(token)` and its segment count, then click it programmatically. Do not conclude the token is missing from a truncated print.
- Every commercial message carries Vinny's valid physical postal address, per 15 USC 7704(a)(5). `outreach.py` refuses to send without one, and that refusal is a feature: do not "fix" a blocked send by removing the check. Supply the address through `PHANTOMBYTE_POSTAL_ADDRESS`.
- A reply containing "stop" goes into `stop_list.txt` immediately, one address per line, before anything else is done. The statute allows 10 business days to process it, but a stop honored late is a stop that gets a second unwanted email in the meantime.
- Any template string carrying `{domain}` must be `.format(domain=...)`-ed at build time. A subject or body that goes out with a literal `{domain}` in it is a silent failure visible only in the sent mail, so dry-run render at least three variants before any send. This applies to every new variant too: rendering one synthetic row per defect code is what catches a missing dict entry or a missing format slot.
- **A triple-quoted Python string preserves source newlines as literal characters.** A paragraph in `TEMPLATE`, `OBSERVATION`, `QUESTIONS`, or `ALLY` that is line-wrapped in the source code ships that way into every draft and every sent mail. Keep every paragraph a single unwrapped line in the source; the reader's mail client wraps it for display. After any edit to a template literal, fetch a rendered draft over IMAP and assert the body carries no unexpected line breaks before staging or sending.
- An offer page that declares it will decline bulk mail, while an outreach script sends cold email, is not a contradiction as long as the sending stays what Vinny specified: a specific, hand-checked heads up to a small daily number. The contradiction only appears if the copy generalizes the finding or the volume grows without the screening. Keep both halves honest rather than softening either the page's stance or the email's specificity.

## Reading the DMARC aggregate report (the verification that closes the loop)

A report from `noreply-dmarc-support@google.com` arrives in Vinny's own mailbox (`hello@phantom-byte.com`), one per day, roughly 24 hours behind the window it covers, with a `.zip` attachment holding one XML file. Read it over IMAP, never AgentMail.

- Do not use the IONOS web panel, a browser, or a login screen for DNS edits under any circumstance. The panel route burns a 2FA round trip and is what caused a wrong-turn attempt at Vinny's IONOS account; the API does the same job in one PUT. A browser vault entry for IONOS exists, and it must never be used for DNS work. Reach for the API key at `/mnt/c/Users/<user>/workspace/memory/ionos-credentials.md` instead.
- Never call these records stale, never flag them as a defect, and never propose removing them.
- Stale on-disk documents will contradict the live records and the live page. `HOWTO_ADDENDUM.txt` still describes the offer page CTA as a `mailto` link and still gives `phantom-byte.com/deliverability` as the URL; the page actually uses an inline form and lives at `/email-deliverability-rescue`, and `/deliverability` returns 404. `DMARC_FIX_phantom-byte.txt` still describes the domain as `p=none`. Trust a live query over any file in `money_ideas/`, and never quote a record string or a URL out of a local note without checking it first.
- The `.zip` filename encodes the window: `<submitter>!<domain>!<begin-epoch>!<end-epoch>.zip`. Convert the epochs with `datetime.utcfromtimestamp(ts)`; a report's `date_range` is always UTC and is a fixed 24-hour window, so a report landing mid-day is normal and not a delayed failure.
- Parse it with `zipfile` + `xml.etree.ElementTree`. `report_metadata` carries the org and report ID, `policy_published` echoes the record the receiver actually saw, and each `record` carries `source_ip`, `count`, `identifiers/header_from`, and `policy_evaluated` with its `dkim`/`spf` results and any `reason` codes.
- Proof that the fix works is **every record's `policy_evaluated` showing `dkim=pass` AND `spf=pass` with an empty `reason` list**. A record whose only entries are IONOS sending IPs (`74.208.4.x`) is the correct, expected shape for this domain.
- The report's `policy_published` line is the independent confirmation that the record is live as intended. Quote it back against the live resolver answer; if they disagree, the record changed since the window closed.
- `record` counts are message counts, so a "28 messages, zero failures" claim is the sum of `count` across records. Report that sum as a total, not a guess at volume.
- A `rua`-less `record` is proof of nothing: no report can exist for a domain with no `rua`, so a mailbox full of these reports is itself the evidence the reporting fix landed.

## Domain facts: phantom-byte.com
DNS records on this domain are correct and complete. Verified 2026-09-19 after the final tightening, on both Cloudflare and Google resolvers:
- SPF: `v=spf1 include:_spf.mlsend.com include:_spf-us.ionos.com include:sendgrid.net -all` (hard fail, all three senders authorized, 4 of 10 lookups spent)
- DMARC: `v=DMARC1; p=reject; rua=mailto:hello@phantom-byte.com; fo=1; adkim=r; aspf=r; pct=100`
- MX `mx00/mx01.ionos.com`, DKIM `s1`/`s2` on SendGrid plus `s1-ionos`/`s2-ionos`, all four verification TXTs intact.
- `python3 email_scan.py phantom-byte.com` now grades OVERALL: PASS on all four records with zero findings. Do not describe the domain as having an open SPF or DMARC item; both are closed.

- DNS, MX, and mailbox hosting: IONOS (name servers `ns.ui-global-dns.de/.org/.com/.biz`, MX `mx00/mx01.ionos.com`). **All DNS edits go through the IONOS DNS API. Never the web panel, never a browser, never a login screen.** The panel route burns a 2FA round trip and is what caused a wrong-turn attempt at Vinny's IONOS account; the API does the same job in one PUT.
- IONOS DNS API, verified working 2026-09-19: base `https://api.hosting.ionos.com/dns/v1`, auth header `X-API-Key: <prefix>.<secret>`, key stored at `/mnt/c/Users/<user>/workspace/memory/ionos-credentials.md`. phantom-byte.com zone id `f9a1e796-0c8f-11f1-8880-0a5864440f43`. List zones `GET /zones`, read one `GET /zones/<id>`, change one record `PUT /zones/<id>/records/<record_id>` with `{name,type,content,ttl,disabled,prio}`, then read the zone back. Back up the full zone JSON to `/mnt/c/Users/<user>/workspace/dns-backups/` before any edit. KARMA uses this same API; she never opens the panel either.
- IONOS, every time: use the DNS API. The key is on disk at `/mnt/c/Users/<user>/workspace/memory/ionos-credentials.md`.
- SendGrid is a deliberate backup sending channel he keeps live. Never call these records stale, never flag them as a defect, never propose removing them, and never add a cleanup step for them to a prompt.
- MailerLite sends as this domain and carries a verification TXT, and no MailerLite DKIM selector resolves publicly. This is not a defect in practice: delivered mail returns `dmarc=pass`, so the platform's own hosted authentication is covering it. Do not raise a missing public selector as a problem without a failing header to back it. The MailerLite API key is currently dead (401), so the panel cannot be read over API.
- Four separate verification TXTs sit on the apex (Pinterest, Google, MailerLite). They are unrelated to mail, never delete or reorder them.
- `dmarc@phantom-byte.com` does not exist. Never point `rua` back at it. `rua` belongs on `hello@phantom-byte.com`, which already exists, so no new mailbox is ever needed. Aggregate reports arrive there as raw XML, a few per day, which is the only downside.
- Verified working state, final as of 2026-09-19: `_dmarc` resolves as `v=DMARC1; p=reject; rua=mailto:hello@phantom-byte.com; fo=1; adkim=r; aspf=r; pct=100`, and delivered mail returns `dkim=pass` on `s1-ionos`, `spf=pass`, `dmarc=pass`. Enforcement is now at `p=reject`, the end state. Earlier stages in this skill's history were `p=none` then `p=quarantine`; never quote either as the current record. Mail is authenticated on both Cloudflare and Google resolvers.
- The Google aggregate report for this domain confirms the fix end to end: a full 24-hour window with every message passing `dkim=pass` and `spf=pass`, zero failure reasons, all senders on IONOS IPs. Google's own `policy_published` echo matches the live `_dmarc` string. When asked whether the fix is real, lead with this report and its counts; it is stronger than any resolver query because the receiver measured it.
- The scanner now grades this domain OVERALL: PASS on all four records with zero findings, so it is not a qualified prospect and the `~all` worry is closed: SPF ends in `-all`, a hard fail, and `email_scan.py` reports 4 of 10 lookups spent. Never repeat the old `p=none` or `p=quarantine` note, and never describe our own sending domain as carrying an open SPF item.
- Name spelling is Barreca, never Barreto. It appears in the `FROM_NAME` constant of `outreach.py`; check it before any send.

## Screening rules the scanner must enforce

The scanner is the gate the whole offer rests on, because a cold email whose first line names a record that does not exist is worse than sending nothing. These are the rules it encodes; keep them when it is edited.

- **SPF lookup counting follows RFC 7208 section 4.6.4, and that section is the authority, not intuition.** The terms that cost a lookup are `include`, `a`, `mx`, `ptr`, `exists`, and `redirect`. The `all`, `ip4` and `ip6` mechanisms cost none and are NOT subject to the 10-lookup limit. Counting `ip4`/`ip6` makes clean domains look broken: on twenty live domains it produced six false positives (`github.com` counted 13 against a true 10, `mailchimp.com` 12 vs 7, `zendesk.com` 12 vs 6, `atlassian.com` 11 vs 6, `airbnb.com` 11 vs 7, `eventbrite.com` 11 vs 7). Counting must also recurse: an `include` pulls in the included record and its terms count too, or a domain like `hubspot.com` that delegates through `redirect=` counts 0 against a true 4.
- **Read the DoH `Status` field before grading anything.** A domain that does not exist is not a prospect. Grading an NXDOMAIN produces four findings on a dead name, and a typo then becomes a cold email naming a record that does not exist. Status 3 is NXDOMAIN and the domain is dropped; a resolver failure is reported as `unknown`, never as a missing record, because those are different facts.
- **A null MX (RFC 7505, the single record `0 .`) is a defect, not a pass.** It parses into a truthy list and slips through a naive check. A domain publishing it accepts no mail by design, which is a genuine finding worth the email.
- **No SPF, an SPF ending in `?all` or `+all`, an SPF ending in `~all`, an SPF over the lookup limit, no DMARC, DMARC at `p=none`, a revoked DKIM key (empty `p=`), a DMARC record with no `rua`, and `AUTH_ALIGNMENT_FAIL` (an SPF that authorizes no sender, with no DKIM and an enforcing DMARC) are the qualifying defects.** A DKIM selector that simply does not resolve is NOT one of them: custom selectors make that a false negative, so it stays a warning that never qualifies a domain on its own. Since 2026-10-05 each qualifier also carries a SEVERITY (missing/misaligned SPF/DKIM/DMARC = critical), because the failure mode is now a gateway rejection, not a spam-folder placement.
- **Two extra checks the scanner needs beyond the four record types:** a wildcard under `_domainkey` (probe with a random selector name, and suppress DKIM results if every name answers, because a wildcard manufactures false hits) and `rua`/`ruf` presence on the DMARC record.
- **`--resume` writes the CSV row by row with a flush, not at the end.** A scan of thousands of domains that dies at hour two with no `--resume` loses the entire run.

## Proving the scripts actually work (the part that was skipped)

The scanner was reported as "built and verified" across multiple sessions while carrying correctness defects that a single run against a known domain would have exposed. "Verified" is a claim about a fresh run in THIS session, never a description of a file's history.

- Run `python3 test_email_scan.py` and read the pass/fail count before claiming the scanner works. It exits non-zero on any failure.
- The durable technique: assert the count against a **second implementation written separately in the test file**, not against a number remembered from a previous run. Two independent implementations rarely share a bug; a remembered number proves nothing and goes stale.
- Pin at least three known-answer domains that must keep passing: one that does not exist (dropped, not graded), one with a null MX (defect, not pass), and our own domain (all four PASS, not qualified).
- Negative test the gate itself: a domain with no measured defect must come back `qualified == no`, and a qualified one must carry at least one documented code with a finding behind it.
- Test the send path's refusals too, by running `--send` with the postal address unset and confirming every message is refused. A safety check that has never been observed firing is an untested check.

## Working with Pi: what each side is actually for

Two agents run against these same files. Pi sits on the Windows side in a harness built for code, this agent runs natively in WSL where the pipeline executes. Vinny stated the division plainly: "Pi is better built for finding bugs and fine tuning code, it's MOSTLY what the harness does," and of this side, "you are the one who is going to be running and managing this. Pi can't."

The loop he wants, stated in his own terms: "we lay out the vision here, set the foundation, pass off to pi, then test and refine here, depending on what we need, edit ourselves, or back to pi, depending on issue."

- **The mechanism that makes the handoff pay off is a cold read, not greater cleverness.** The author of a file cannot see its bugs, because he reads what he meant rather than what the code does. A second reader with no memory of writing it catches things the author never will. This is the real reason to route code refinement elsewhere, and it applies even when the other agent is not smarter.
- **Route by which harness fits the fault, not by a fixed handshake.** Any step can bounce back. A wrong constant, a stale note, a one-line rule correction: do it here. A structural defect in how a script reads a page or parses a record: Pi's side. Whoever holds the right tool for that specific fault takes it.
- **This side owns: the vision, the scope, the rules a thing must obey, the live execution, and the proof.** Running the scripts, reading the mailbox, querying DNS, checking the live page, and holding the constitution all happen here. Pi cannot run this pipeline from where it sits; it can only make the code better and hand it back.
- **Never let one agent be both author and verifier of the same change.** That is the failure this division exists to prevent. The brief Pi hands back is a claim list; the verification here is a fresh run, never a read.
- **A handoff carries a named artifact, not an impression.** Vinny's design brief, Pi's diff plus its claim list, this side's run output that confirms or kills each claim. Without that, the handoff degrades into two agents trusting each other's summaries.

### A brief from another agent is a claim, not a result
This machine runs more than one agent against the same files (Pi works the Windows side, WSL Hermes works this side), and a handoff brief arriving from one of them reads like a report but is a summary of someone else's claims.

- **Re-run anything the brief asserts that DECIDES whether the work is correct**, and report the number you ran. That means every behavior claim: whether a fix actually landed, whether a gate fires, whether a refusal still refuses, whether a defect is really closed. A claim about behavior is the whole point of the handoff and it must be exercised, not repeated.
- **Do not audit the brief's cosmetics, and never keep score against the other agent.** A check count that reads 96 where the brief said 98, or a figure off by one, does not change whether the work is right or whether the tool functions. Vinny called this out directly: "you keep obsessing over an error of 2. I view that as irrelevant." He then named what it actually was: "this is a team not a competition." Surfacing a trivial discrepancy once, in passing, is fine. Raising it repeatedly, leading with it, or burying a real finding underneath it is scoring points, and it reads as searching for a flaw rather than doing the work. Lead with the finding that changes the outcome; let the rounding error go.
- **Re-read a file before quoting numbers from your own earlier run of it.** Another agent can edit a script or its output between two of your runs, and a CSV that gained columns (`kind=osm` appearing mid-session) is the tell that the file is no longer the one you last measured. Report the numbers from the read you just did, not the ones you remember.
- **When a live file contradicts the brief, the live file wins, and the brief is corrected rather than deferred to.** Where the brief and the skill disagree, the skill is the authority; where either disagrees with a live query, the live query wins.
