# Partner / referral channel (white-label fix + finders fee)

Added 2026-10-08 on Vinny's direction. The plan of record is the dated section
"2026-10-08, The partner channel" in
`C:\Users\<user>\workspace\memory\deliverability-rescue-vps-plan.md`. This file is
the operational doc: the terms, the copy drafts, the sourcing route, the page
outline, and the checks. Nothing here is built, sent, or deployed until Vinny
orders it.

## What the channel is, and what it is not

Target partners: businesses that already serve our end customers but do not
specialize in email authentication.

- Web development agencies
- Managed IT service providers (MSPs)
- Website maintenance companies
- Independent IT consultants

It is a second go-to-market channel, NOT a new target industry. The
`TARGET_INDUSTRIES.txt` exclusion of `it_msp` / `b2b_agency` from the BUYER pool
stands: as buyers they are a poor fit (they know DNS or have a vendor), as
partners they are the best fit because their client base is the unaudited
segment. Two lists, two stores, never mixed.

## Guardrails (non-negotiable)

- White-label means invisible. The findings sheet, before/after report, and
  recorded walkthrough delivered to a partner's client carry the PARTNER's
  brand. One leaked "PhantomByte" ends the relationship.
- Never touch a partner's client DNS without the partner's written
  authorization that names the domain.
- The partner cold email is a separate copy set, not a variant of the buyer set.
  It runs the same gate chain: role rule, buyer fit, dedupe, suppression,
  mailbox verify, postal address, no `Subject:` line in the body.
- No bulk-sending enablement. A partner reselling to their own existing clients
  is fine; we do not hand a partner a list to cold-blast. The offer page's "I
  will decline the work" line stays true.
- Never name an inferred CLIENT domain in the cold email. Scanning public DNS
  is fine; approaching a stranger about their client's domain is not. Name the
  partner's own domain, or the market number.

## Terms (opening position; Vinny's call)

| Line | Partner pays | Typical partner resale | Partner margin |
|---|---|---|---|
| Findings and fix spec, they apply | $99 | $250–$500 | $150–$400 |
| One-domain fix, white label (we apply and verify) | $250 | $500–$750 | $250–$500 |
| Monitoring, white label | $125 / month | $250 / month | $125 / month recurring |
| Volume, 3+ domains / month | $200 | $500–$750 | $300–$550 |
| Referral only | $150 flat finders fee | n/a | one time |

Direct-buyer price is unchanged at $500 + $250/mo. These are OPENING numbers,
not a rate card (Vinny, 2026-10-08: "any deal can be negotiated, this is a
starting point"); the levers are in "The numbers are an opening position" below.
The three-tier shape is the point: the partner picks how much of the work they
keep. "You apply it" is the most scalable (we never touch their DNS) and the
easiest yes, and it upsells to done-for-you when they get stuck.

## The measured hook (verified live 2026-10-08, `scan_master.csv`)

12,350 unique business domains; 10,389 qualified (84.1%). DMARC state:

- none published: 6,480 (52.5%)
- `p=none` monitor only: 3,125 (25.3%)
- `p=quarantine`: 1,510 (12.2%)
- `p=reject`: 1,229 (10.0%)

Headline for the pitch: **62% have no DMARC or only monitor mode; only 10%
enforce.** Re-read the CSV and recompute before quoting; the numbers move as the
pool grows.

## The two-arm partner email

**As built 2026-10-08, the live template and the finding phrases are in
`partner_outreach.py` (`TEMPLATE`, `SUBJECT`, `FINDING_SHORT`, `PORTFOLIO`), and
that file is the authority, not this section.** The drafts below are the design
that produced it; read the code before quoting the current copy. The built
email has no link (reply-driven), names the reader's own domain when the scan
found a defect, and closes with a one-time-outreach opt-out.

The buyer copy names a record on the reader's own domain because that is the
moat. A partner's own domain is often clean, so pick the arm by scan:

- **Own-domain arm** when the partner's own domain carries a qualifying defect.
- **Portfolio arm** when it does not.

Both keep the Socratic shape: observation, ally, offer, one CTA, opt-out,
postal. Short enough to read on a phone.

### Own-domain arm

Subject: `A mail records question about {domain}?`

```
Hi {person},

I checked {domain}'s mail records. Your DMARC record is set to monitor only, so
it reports on anyone spoofing your domain and blocks none of it. Your SPF and
DKIM are fine, so this is the last piece.

I am not writing to sell you a fix for your own domain. I do this work for a
living, mostly for local businesses, and I would rather run it behind the
agencies and IT shops that already look after those clients than in front of
them.

Of 12,350 business domains I have scanned, 62 percent have no DMARC record or
one that only monitors, and only 10 percent enforce. Your client base almost
certainly has the same shape, and nobody audits it.

So which client domain would you want checked first?

If it is useful, I do this white label. You keep the client and set the price, I
implement behind your brand for $250 a domain, or $125 flat if you would rather
just introduce me and stay out of it.

Want the one-page partner sheet? Reply and I will send it today. No call, email
only.

Reply "stop" and I will not write again.

{postal_address}
```

### Portfolio arm

Subject: `A white-label mail fix for {business}'s clients?`

```
Hi {person},

I scanned the mail records on 12,350 business domains this year. 62 percent have
no DMARC record or one that only monitors, so spoofing is reported and never
blocked, and only 10 percent enforce anything. The domains you look after almost
certainly have the same shape, and nobody audits them.

I am not selling you a fix for your own domain, and I never approach your client
directly. I would rather run this behind the agencies and IT shops that already
own those relationships than in front of them.

So which client domain would you want checked first?

I do this white label. You keep the client and set your price, I implement
behind your brand for $250 a domain, with monitoring at $125 a month if you want
recurring. If you would rather just introduce me, it is $125 flat per client.

Want the one-page partner sheet? Reply and I will send it today. No call, email
only.

Reply "stop" and I will not write again.

{postal_address}
```

### Copy rules that still apply

- Body paragraphs are single unwrapped lines in the source; a wrapped
  triple-quoted string ships the line breaks.
- No em dash, en dash, or spaced hyphen anywhere.
- Subject names the business, carries no protocol acronym.
- The subject lives in the header only. `build_message` strips a leading
  `Subject:` line and refuses a body that still carries one.
- One CTA, not a rotating set.
- If folded into `outreach.py`, the partner arms are a new template family
  selected by channel, not a new defect variant. Add every slot to the
  `.format()` call or a literal brace ships. Render one synthetic row per arm
  and assert no brace survives, no dash appears, and the paragraph order holds
  before any send.

## The partner landing page

A `/partner` ADDON on phantom-byte.com (never a replacement, per the
`deploy-offer-page` skill). The buyer page at `/email-deliverability-rescue` is
untouched. Build locally, verify, then Vinny approves the deploy.

Top to bottom:

1. H1: You look after their websites. Nobody looks after their mail records.
2. Lede: the measured number (62% / 10%) and the white-label offer in two lines.
3. What you get per client: findings sheet, the fix applied and verified, a
   before/after report, a recorded walkthrough, optional monitoring.
4. How white label works: delivered under your brand, we never contact your
   client, you own the relationship and set the price.
5. Two ways to work together: white-label wholesale table, and the referral fee.
6. What I will not do: no client contact, no bulk sending, no placement
   guarantee. Same honesty box the buyer page carries.
7. FAQ (do I need DNS access, how long, can you bill my client directly, what if
   a record drifts).
8. Form: name, business, website, rough client count, and a reply field. Wire it
   to the contact API and test it, exactly as the offer-page skill requires.

## Sourcing partners

**As of 2026-10-11 this section is subordinate to the directory route below, and
OSM is the backstop, not the source.** Measured end-to-end yield of the OSM route:
~22.7 raw partner prospects and ~7.6 usable email addresses per metro, so the whole
55-metro queue in `partner_metros4.txt` is worth ~400 addresses, about 8 send-days
at 50/day.

### The directory route (built 2026-10-11) - this is now the primary source

`directory_prospects.py` reads agency **directories**, which exist to list agencies
and which publish each agency's own website. Measured availability, 2026-10-11:

| Source | Agency profiles | Status |
|---|---|---|
| `topdevelopers.co` | 10,836 | works - default source |
| `superbcompanies.com` | 77,931 | works |
| `digitalagencynetwork.com` | ~1,000 per child sitemap | works intermittently; child sitemaps usually read-timeout |
| clutch.co, techbehemoths.com, themanifest.com, yellowpages.com, upcity.com | - | **403 at robots.txt** - do not wire them |
| designrush.com, goodfirms.co, sortlist.com | - | robots.txt permits, sitemaps 403 via Cloudflare - closed in practice |

Extraction accuracy measured on the first twenty profiles of each working source:
**40/40 correct** (the correct agency domain, never a sidebar, a press-release
farm, or a social link).

```bash
cd ~/money_ideas
# enumerate only, reads no profile page
python3 directory_prospects.py --source all --limit 8 --dry
# scrape 250 profiles per source, appending new domains to the partner pool
python3 directory_prospects.py --source topdevelopers,superbcompanies --limit 250
```

Or the whole chain in one command, which is what the `PARTNER DIRECTORY REFILL`
cron (`be4516e1f17a`, `0 19 * * 0-4`) runs - it is `--no-agent`, so its stdout is
delivered verbatim:

```bash
SOURCE=topdevelopers,superbcompanies PROFILES=250 DELAY=3.0 \
  bash ~/.hermes/scripts/partner_directory_refill.sh
```

That script scrapes -> works out what is genuinely new (`directory_pool_todo.py`)
-> DNS-scans it (`email_scan.py`) -> harvests contacts (`harvest.sh`, 4 workers) ->
merges into `partner_scan_master.csv` and `partner_contacts_master.csv` **through
`csv_append.py`** -> prints the eligible count. **It never sends mail and never
stages.** `PARTNER OUTREACH REFILL` stages at 09:30 from whatever the pool holds.

**Never append to a master with a shell redirect.** The original
`[ -s "$MASTER" ] || head -1 "$SRC" > "$MASTER"` emptied
`partner_contacts_master.csv` (187 rows) on 2026-10-11: `cmd > file` redirects
before it runs, so a missing `$SRC` truncated the master first. `csv_append.py`
refuses a missing/empty/headerless source, dedupes on `domain`, and writes via a
temp file plus `os.replace`. Test: `test_csv_append.py`, 31 offline cases, whose
first case is exactly that incident. **Also never edit a script that is currently
running** - bash reads a script incrementally, so a change in length mid-run shifts
the read offset and it can resume part-way through a command (that is what lost the
guard that night, and it produces a phantom "syntax error" in a file that
`bash -n` calls clean).

Verified end to end after the fix: 6 new agency domains scraped, scanned, harvested
and merged; 187 -> 193 contact rows intact; eligible partner addresses 19 -> 22;
nothing sent.

Politeness, which is not optional: robots.txt is read at runtime and honoured with
RFC 9309 matching (query strings included - a `Disallow: /*?` rule must be able to
fire); the user agent identifies the product and a contact address; one request per
URL; a `DELAY` (default 3s) between requests to a host; single-threaded, because each
source is ONE host and a worker pool against one host is abuse rather than speed.

Tests: `python3 test_directory_prospects.py` - 85 offline cases, no network, the real
profile markup embedded as fixtures. It caught a live bug the day it was written:
`urlparse().path` drops the query string, so `Disallow: /*?` could never match and a
forbidding rule silently became a permitting one.

### The OSM route (backstop)

The buckets exist in `osm_industry_prospects.py`:

- `it_msp`, `office=it|telecommunication|computer`,
  `shop=computer|electronics|mobile_phone|telecommunication`,
  `craft=electronics_repair|computer|it`.
- `b2b_agency`, `office=advertising_agency|marketing|public_relations|design|graphic_design|publisher|media`,
  `shop=advertising|marketing|printing`.

Web development / maintenance and independent IT consultants have no clean OSM
tag. Web shops tag mostly as `office=it`, `office=advertising_agency`, or
`office=marketing`; consultants as `office=consulting` or `office=it`. So a
`partner_agency` bucket is the union of `it_msp`, `b2b_agency`, and
`office=consulting`.

**Measured supply (Overpass count, 2026-10-08).** Count of
`office~^(it|advertising_agency|marketing|consulting)$` plus
`shop~^(computer|electronics|mobile_phone)$` per metro bbox: Tampa 104, Orlando
137, Miami 184, so 425 raw elements across three metros. Most elements carry no
website or email tag, so a three-metro pull yields a few hundred raw names and
on the order of 100 to 200 usable domains. OSM is thin for this segment, which
matches the existing note that it tags far more shops than agencies or MSPs. To
build a partner list past a couple hundred, run several metros, or add a
funding-gated Google Maps pull or a directory scrape. Do not expect a
thousand-partner list from OSM.

**Measured END-TO-END yield per metro (2026-10-11, from the real pool files -
this is the number to plan from).** Read `partner_prospects_master.csv`,
`partner_contacts_master.csv`, `partner_state.json`:

| Stage | Count |
|---|---|
| metros sourced (passes 1-3) | 12 |
| raw partner prospects | 272 (**22.7 / metro**) |
| contact rows harvested | 187 |
| rows carrying an email address | 91 (**7.6 / metro**) |
| actually mailed to date | 43 |
| eligible and unused on 2026-10-11 | **19** |

So the whole of OSM, at the 55 metros now queued in `partner_metros4.txt`, is
worth roughly **400 email addresses - about 8 send-days at 50/day**, and then
this segment is exhausted. **Sourcing, not send rate, is the binding constraint
on the partner channel.** Raising the meter without feeding the pool just makes
the daily job report "nothing staged".

Rejected route, with the reason: adding `professional` to
`--only-industries` looks attractive because it contains `tag:office=consulting`
(which `partner_fit()` keeps), but measured supply says a metro gives ~136
`professional` domains for ~3 useful consulting ones - ten times the Overpass and
`find_contacts.py` cost for a tenth of the yield, inside a 09:30 -> 13:00 window.
The ~60 consulting/agency addresses that are already scanned sit in the BUYER
pool (`contacts_master.csv`) and should be imported directly instead of re-sourced.

**Automation (2026-10-11).** The partner channel is now the priority one and is
scheduled like it: `PARTNER OUTREACH REFILL` (`partner_refill.sh`) runs **09:30
Mon-Fri** - moved off 10:30 so it gets first call on the shared 100/day verifier
tier before the 10:00 weekday prefill, and so a 5-metro source+scan+harvest still
finishes well before the same-day 13:00 send. Knobs: `LIMIT=50`, `GAP=4`,
`METS_PER_RUN=5`, metros from `partner_metros4.txt` (55 metros; carry-over from
pass 3 plus fresh ones, done-tracker `partner_metros_done.txt` stores the NAME).
Full cron state: `references/outreach-automation-crons.md`.

Route (confirm each script's flags against its `--help` before running):

```
cd ~/money_ideas
python3 osm_industry_prospects.py --only-industries it_msp,b2b_agency \
    --out partner_prospects_<date>.csv --metros osm_metros.txt --max-domains 300
# scan the sourced domains
python3 email_scan.py --file partner_domains_<date>.txt \
    --out partner_scan_<date>.csv --resume
# harvest contacts (run in parallel chunks, see industry-prospect-build.md)
python3 find_contacts.py --file partner_todo_<date>.txt \
    --out partner_contacts_<date>.csv
```

`agency_domains_tampa.txt` (2026-09-20) is a misnomer: it is a real-estate agent
list, already in `ALREADY_SCANNED_FILES`. Do not reuse it as a partner list.

## Tracking

- Partner offer URL: `utm_source=partner&utm_medium=email&utm_campaign=partner-program`,
  plus a per-partner token `p=<id>` once a partner is active, reusing
  `click_tokens.py`.
- A partner-sourced deal carries the partner id so reply rate and revenue split
  by channel. The partner side gets its own store; do not bolt channel fields
  onto the buyer `state.json`.

## Verification before any send

1. Scan the partner's own domain and record whether the own-domain arm or the
   portfolio arm applies. Never send an arm whose factual premise is false.
2. Render one synthetic row per arm through the build path; no literal brace, no
   dash, subject in the header only, paragraph order intact.
3. Confirm the postal address and the opt-out are present.
4. Confirm the domain is not in the buyer pool, the buyer state, or
   `suppressed_addresses.txt`, and that partner and buyer lists do not overlap.
5. Count replies before scaling, same discipline as the buyer channel: replies
   per 100 is the number that decides whether the channel is real.

## As built 2026-10-08

- **Sender:** `partner_outreach.py` in `money_ideas/`. Separate channel, separate
  state (`partner_state.json`), separate log. Reuses `schedule_drafts` staging,
  `outreach` mailbox probe / bounce guard / auth pre-flight,
  `find_contacts.address_shape`, `outreach.greeting_for`.
- **Scoped verification:** `verify_partner_scheduled` matches only the partner
  recipient addresses, so a buyer batch sitting in the same `Scheduled` folder
  does not fail the partner run. It reports the count of unrelated messages
  rather than treating them as an error.
- **Fit filter:** `partner_fit` keeps agency/MSP-shaped rows and drops retail,
  phone-repair, print, franchise and name-pattern noise. Apply it to BOTH the
  prospect list and the harvested contacts, or a filtered domain re-enters
  through the contact file (fixed 2026-10-08). **`name-pattern` is the noisy
  source.** On 2026-10-08 the loose keyword list let through a steel company, an
  ATM merchant-services firm, a gutter contractor, an arts nonprofit and a
  mosque. The keyword list was tightened (dropped systems / tech / computer /
  network / solution / studio / market / bare it), which cut the fit pool from
  145 to 109. Prefer tag-sourced rows; treat `name-pattern` as a last resort, and
  spot-check business names before staging a batch.
- **Meter:** 30/day target (Vinny, 2026-10-08), started at 14 on night one.
- **Command:**
  `python3 partner_outreach.py --contacts partner_contacts_<date>.csv --start YYYY-MM-DDTHH:MM --gap 4`
  (add `--limit 30` to cap, `--dry` to render only, `--drop-role` for the strict
  role rule, `--reconcile` to repair untracked queued mail).
- **Sourcing reality:** `osm_industry_prospects.py --only-industries it_msp,b2b_agency`
  on the FL metros returns almost nothing because those agency domains are
  already in the buyer `ALREADY_SCANNED_FILES`. New partner supply needs new
  metros. 20 metros produced 230 raw / 132 fit.
- **Role rule:** the partner channel MAY mail role boxes (Vinny, 2026-10-08);
  the buyer channel still may not. `partner_outreach.py` allows role by default;
  `--drop-role` restores the strict rule. This took the eligible pool from 15 to
  about 75.
- **Signature (linked, final):** built as HTML in
  `partner_outreach._signature_html()`, never typed into the plain template:
  `Vinny Barreca` / `https://phantom-byte.com` (anchor) / `Email Deliverability
  Rescue` (anchor to the rescue page, href tagged `utm_source=partner`) / postal.
  The plain-text converter escapes URLs, so a URL in the template ships as dead
  text (that was the 2026-10-08 miss). SMTP sends do not inherit the webmail
  signature at all.
- **Reconcile:** a failed verification after staging leaves queued mail
  untracked. `partner_outreach.py --reconcile` reads the folder and records any
  partner message missing from `partner_state.json`; the sender now saves state
  before verifying. Fired once 2026-10-08 (15 messages) and repaired cleanly.

## Reply kit (prep for the first "yes")

Not built into the send path. Prepared so the first partner reply is answered in
minutes, not assembled live. Cheap to change, because the terms may move once a
real partner pushes back.

**The one-page sheet** (mockup, not deployed):
`C:\Users\<user>\OneDrive\Desktop\MONEY MAKING OPPORTUNITIES\offer-pages\partner-sheet.html`.
Carries the measured number, the two options, what the client gets per domain,
the invisible-white-label rules, the "what I will not do" block, and a
one-domain start. Attach it, or paste it as the body. Deploying it to
`phantom-byte.com/partner` is a separate step (the `deploy-offer-page` skill).
The buyer `/email-deliverability-rescue` page is the wrong destination for a
partner reply.

**Reply template** (send in-thread; bare URLs auto-link in any client):

```
Hi {first},

Good to hear from you. Short version below, and the one page sheet is attached.

White label: you pay $250 per domain. I do the findings, the fix, and the
verification behind your brand, and you present it and bill it at whatever price
you set. Most sit between $500 and $750. You own the client and I am never in the
thread.

You apply it: I send you the findings and the exact records to publish, with the
apply steps for your client's provider, and a re-check once you make the change.
$99 per domain, and you stay in full control of the DNS.

Referral: you introduce me, your client pays $500, and I send you $150 once they
pay.

Any of the three, the client gets the full scan, the records written correctly, a
before and after report, and a recorded walkthrough. Email only, no calls.

The cleanest way to start is one client domain. Send it over and I will run the
free scan and send you the findings sheet, so you can see exactly what your
client would get before anything is billed.

Which client domain do you want to start with?

Vinny Barreca
https://phantom-byte.com
https://phantom-byte.com/email-deliverability-rescue
500 Peconic Street, Apt 231A, Ronkonkoma, NY 11779
```

**Caveats to hold.** The sheet is a mockup until a partner engages. Do not
deploy it, and do not treat the reply as a script to mass-send: it answers one
human who wrote back.

## The numbers are an opening position, not a price list (Vinny, 2026-10-08)

$250 per domain and $150 per referral are where a conversation starts, not a
published rate. Vinny: "any deal can be negotiated. this is a starting point."
So the reply kit is a floor to open from, and whoever answers a partner should
expect to move on the numbers.

Levers that can move:

- Volume: 3+ domains a month can go to $200, and a committed book lower still.
- Whole-book retainer: a flat monthly for a partner's whole client base instead
  of a price per domain.
- First client: one domain cheap or free to prove it, then standard. Now an
  approved lever, so the sheet may carry it if a partner stalls on price.
- Monitoring: the $125/$250 split is the most negotiable line, because recurring
  is where this compounds and a partner who resells it is worth more than a
  bigger one-off margin.
- Referral: $150 flat, a percentage, or a reciprocal arrangement.
- Scope: a higher price buys more done-for-you (we take the client comms); a
  lower price buys less.

What does not move:

- No placement guarantee, no bulk sending setup, no client contact without the
  partner, no DNS change without written authorization that names the domain.
- We still get paid. Anything under roughly $100 per domain, or a retainer that
  works out under that, goes to Vinny first.

Rule: do not negotiate a structural change live in a thread. Ordinary movement
on price is fine; a new deal shape (a rev-share on the whole book, a formal
reseller agreement, exclusivity) comes back to Vinny.

## Beyond per-domain: sell the system, sell the data

Vinny, 2026-10-08: "I'd also sell them the system we build for it for a good
amount of money. There are many angles." The per-domain tiers are the entry; the
system and the data are the larger plays. The ladder is in the planning file
section "2026-10-08 - Monetization angles".

What we actually own that is productizable: `email_scan.py` (the grader),
`findings_sheet.py` (scan row to plain-language finding), the browser-side
checker, the outreach/prospecting pipeline, and the scan database. **Vinny means
selling this outright for a one-time $5-10K, not licensing it as a SaaS.** The
tradeoffs (caps the partner stream, sells the moat, needs a packaging pass, worth
more after proof) are in the planning file, "2026-10-08 - Monetization angles",
item 6. Do not quote a buyer a number until Vinny sets one, and do not hand over
code in its current internal-script state.

Cannibalization: the system and the per-domain services chase the same wallet.
Sell the system as the scale tool for their whole book, the services as the hard
cases and done-for-you. Nothing here is built until the service proves demand.

**The objection, and the hammer.** A buyer will say "I'll just have my agent
build this." The answer, in Vinny's words: "NOT EVERYONE WITH A HAMMER IS A
BUILDER, YOU ARE A GUY WITH A HAMMER WHO DOESN'T KNOW HOW TO BUILD." The tool got
cheap, the ability did not. What they would buy is not the hammer, it is the
finished frame, the tuned scan logic, the 12k graded domains, and three weeks
they do not have to spend reaching parity and then maintaining it.

But the same fact cuts the other way, and it decides how to sell it. If almost
nobody with an agent can build, then almost nobody buying can RUN the machine
either. A raw code dump is therefore a liability, not a product: a non-builder
who cannot operate it calls weekly and tells people it does not work. Two exits:
sell to the rare operator who genuinely can run it (smaller pool, cleaner sale,
no strings), or sell the turnkey version and price the hand-holding into the
one-time number, with support as a bounded paid add-on and never an open door.
That is the pricing tension in build-to-sell: the less of a builder the buyer is,
the more of the value has to arrive wrapped, and the more the sale wants to slide
back toward a service. Decide which buyer up front.

**What the buyer is actually buying (Vinny, 2026-10-08):** "the testing and
innovation of the idea, and solid implementation." They are buying the risk
already taken: the R&D, the iteration, and a working, tested build, so they skip
the graveyard where most attempts die. Price anchors against what it would cost
THEM to rediscover it (months, wrong turns, likely never getting solid), not
against the labor in the code. The sellable asset is therefore the testing
dossier: the grader run across 12,350 domains, the defect rates, the before and
after reports, the bounce and click logs, the passing test suites, the fact it
has run for real and survived. The code is the artifact; the track record is the
value.

Honesty line to hold: the testing so far proves the DIAGNOSIS is accurate and the
pipeline runs. It does NOT yet prove the offer sells. That is technical
validation, not commercial validation. Sell "tested and solid" now; only sell
"proven to make money" after two or three real sales, and raise the price then,
not now.

## Open decisions for Vinny

1. **Answered 2026-10-11:** the directory route replaced the metro question. OSM
   was exhausted for agencies, so sourcing now comes from the agency directories
   (see "The directory route" above). Adding more metros is no longer the answer to
   a pool shortage.
2. The `/partner` landing page (not needed for the reply-driven email; the
   signature already links the rescue page).
3. **Owed once an agency says yes:** a reply kit and a one-page partner sheet. Dom
   (`dominique@temerarii.com`, replied 2026-10-11) has a call booked, so this is now
   the live gap rather than a hypothetical.
4. **Parked by Vinny 2026-10-11:** the partner ledger, plus adding the recurring
   monitoring tier to the partner cold copy. Both are recorded in the planning file
   (`C:\Users\<user>\workspace\memory\deliverability-rescue-vps-plan.md`, section
   "PARKED IDEA: the partner ledger") because the instruction is to get a paying
   customer first. Do not build them unprompted.
