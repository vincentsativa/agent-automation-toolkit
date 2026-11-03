---
name: money-ideas-outreach
description: >-
  THE MAP for Vinny's money_ideas cold-outreach project, the "Email
  Deliverability Rescue" offer. Read this FIRST for anything about email,
  outreach, cold email, the campaign, prospects, the sending pipeline, the
  staging cron, the planning docs, the VPS/SES migration, or money_ideas. When
  Vinny says just "email", "the emails", or "the outreach", he means THIS
  project. This skill says where every file, plan, script, credential and
  reference lives and which side of the Windows/WSL boundary it is on, so nobody
  has to search the filesystem again.
---

# money_ideas outreach, where everything is

Two worlds, one project. Most mistakes here are boundary mistakes: searching the
Windows side for a WSL file, or the WSL side for a Windows file.

| | Windows (pi runs here) | WSL Ubuntu (user `<linux-user>`) |
|---|---|---|
| Pipeline code |, | `~/money_ideas/` |
| Plans + memory | `~\workspace\memory\` |, |
| Skills | `~\.pi\agent\skills\` | `~/.hermes/skills/` |
| Cron |, | `~/.hermes/cron/jobs.json` |
| Credentials |, | `~/.config/phantombyte/mailer.env` |

Crossing: `\\wsl.localhost\Ubuntu\home/<linux-user>\...` is `~/...`;
`/mnt~/` is `~\`.

## Read these before touching anything

1. **The planning file**, `~\workspace\memory\deliverability-rescue-vps-plan.md`.
   The VPS plan, the SES migration, the AWS/EC2 credit, the dashboard, the data
   business, the port-25 conflict, and the funding-gated roadmap. **This is what
   Vinny means by "our planning file".** Update it there; do not scatter plan
   text into other docs.
2. **The pipeline authority**, `~/.hermes/skills/email-deliverability-rescue-workflow/SKILL.md`
   (103KB) plus its `references/` (28 files: cadence, copy rules, verification,
   state protection, OSM sourcing, venues, partner/referral channel, the pi
   handoff rules). The skill is the authority; a plan summary is not.
3. **This session's harness only lists `~\.pi\agent\skills\`.** The
   project's real skills live under `~/.hermes/skills/` and are NOT
   in the startup list. Go read them; do not conclude they do not exist.
4. `~\.pi\agent\instructions.md`, hard rules (never leak
   credentials into a repo; never run `gcloud run domain-mappings`).
5. **The partner channel** (added 2026-10-08), the white-label fix + referral
   second go-to-market, aimed at web/IT agencies, MSPs, and consultants. The
   plan is the dated "2026-10-08, The partner channel" section in the planning
   file; the operational doc with the two-arm email drafts and the `/partner`
   page outline is `references/partner-referral-channel.md`.

   **Boundary that matters:** partner domains are a SEPARATE list and store from
   the buyer pool. `TARGET_INDUSTRIES.txt` still excludes `it_msp` / `b2b_agency`
   as BUYERS; they are partners only. Never merge the two lists, and never add
   channel fields to the buyer `state.json`.

## The pipeline (all in `~/money_ideas/`)

| Script | What it is |
|---|---|
| `outreach.py` | The sender. Gate chain, rendering, `build_message`, `tagged_offer_url`, `plain_body_to_html` / `mask_tracked_urls_html` (link masking), `send_one`, `verify_mailboxes`. **2026-10-05: `preflight_sending()` refuses a real `--send` from a domain that fails its own records; `CHANGE_NOTE` + `NO_PITCH` replaced the hard price line; per-provider volume in `state.json`** |
| `schedule_drafts.py` | **Current staging path.** Queues into the IONOS `Scheduled` folder over the Open-Xchange API with a real send time. `body_to_html`, `verify_scheduled` |
| `check_scheduled.py` | Independent read-back of the folder. `--expect N` must print `RESULT: OK` |
| `clean_prospects.py` | Pool cleaning: role boxes, buyer fit, dedupe vs `state.json` |
| `email_scan.py` | The DNS grader (SPF / DKIM / DMARC / MX). Also the offer's own hook. Writes `severity` + `enforcement` + `alignment` columns (2026-10-05 enforcement reclassification) |
| `auth_enforcement.py` | **New 2026-10-05.** One copy of the Gmail/Microsoft enforcement model: consumer-provider buckets, the 5,000/day threshold, gateway-rejection classification (`classify_rejection`), and `preflight_sending_domain()` (alignment: exists but does not pass). Imported by `email_scan`, `harvest_bounces`, `outreach` |
| `domain_preflight.py` | **New 2026-10-05.** CLI that proves a SENDING domain would pass enforcement before it sends or is warmed. `python3 domain_preflight.py <domain> [--ses] [--print-records]`. Run it for the SES `mail.vincentsativa.com` identity before any send |
| `find_contacts.py`, `osm_*.py`, `harvest.sh` | Sourcing and contact harvesting |
| `mail_verify.py` | RCPT mailbox probe. Local vantage is **IPv6-only** (ISP blocks outbound 25 on IPv4), so IPv4-only MX hosts come back UNKNOWN and fall back to the hosted verifier. Verdicts cache to `verify_cache.json`. `harvest_bounces.harvest_full()` now buckets refusals; gateway auth rejections go to `auth_rejections.txt` (NEVER suppressed) |
| `preverify_pool.py` | Pre-verify up to `--limit` uncached pool addresses. Run by the weekend cron; sends nothing |
| `check_verifier.py` | Is the verifier key alive and how many credits are left? **Free** (sandbox endpoint). Separates a dead key (401) from the vendor's site being down |
| `build_lead_groups.py`, `build_clicker_groups.py`, `click_tokens.py` | `leads/` groups, click attribution (`o` = offer, `c` = per-recipient token) |
| `test_outreach.py` | Known-answer suite. Run after ANY `outreach.py` edit. Sends nothing. Needs `mailer.env` sourced or one check false-fails on the missing postal address |
| `stage_drafts.py` | Legacy IMAP-drafts path (kept for when Vinny asks for drafts) |
| `partner_outreach.py` | **Partner channel sender (added 2026-10-08).** White-label/referral pitch to agencies, MSPs, web/IT shops. Own template, own state (`partner_state.json`), own log. Reuses `schedule_drafts` staging and the `outreach` gates. Read-back is scoped to partner addresses, so it coexists with the buyer batch in `Scheduled`. Role boxes allowed BY DEFAULT (`--drop-role` for strict); the buyer channel still never mails role. Signature = IONOS default (name + websites) + postal. `--reconcile` repairs queued mail left untracked by a failed verify. **`partner_fit()` has two admission routes as of 2026-10-11: an OSM tag in `KEEP_SOURCES` / an agency-shaped name, OR `industry_source` starting `dir:` (a directory row is agency-shaped by construction; DENY_NAME and `partner_exclude.txt` still veto).** Meter: **50/day as of 2026-10-11** (was 30). Sourcing: the agency directories below, plus `partner_metros4.txt` (OSM, 55 metros) as the backstop. **Sourcing-limited, not rate-limited**, measured ~7.6 usable addresses per OSM metro. |
| `directory_prospects.py` | **Directory scraper (added 2026-10-11).** Builds partner prospects from agency directories instead of OSM, because OSM is exhausted for agencies. Reads `topdevelopers.co` (10,836 agency profiles) and `superbcompanies.com` (77,931), honours robots.txt at runtime with RFC 9309 matching (query strings included), single-threaded with a per-host delay, resumable via `directory_seen_<source>.txt`, appends new domains to `partner_prospects_master.csv`. Emits the OSM pool schema with `industry_source="dir:<source>"`. **Measured 40/40 correct domain extraction** on the first twenty profiles of each source. It does NOT find email addresses; that stays `find_contacts.py`. Tests: `test_directory_prospects.py` (85 offline cases, real markup embedded as fixtures). |
| `directory_pool_todo.py` | **New 2026-10-11.** Works out which pool domains still need a DNS scan and which still need a harvested contact, so a directory run pays only for what is genuinely new (`--only-domains`). |
| `infer_addresses.py` | **New 2026-10-30. The pool's own data as a source.** `contacts_master.csv` held **1,015 rows where the harvest found a real person's name on the site and no address printed**, those were being discarded. This turns `first last @ domain` into five ordered candidates (first, first.last, firstlast, last, flast), drops business-looking captures (`All Pierogi`, `Vehicles Schedule`, `Us From`, 363 rejected in the first 400 rows), verifies through the RCPT gate and, with `--apply`, patches the winning address into the row that already exists for that domain (same row count, temp + `os.replace`). Only a proven address is kept; nothing is sent. |
| `csv_append.py` | **New 2026-10-11.** The only supported way to append rows into a master pool CSV. Refuses a missing/empty/headerless source, dedupes on `--key` (default `domain`) so a re-run is idempotent, pads short rows, refuses to shrink the file, and writes via a temp file + `os.replace`. It exists because the shell idiom it replaced (`[ -s "$M" ] || head -1 "$SRC" > "$M"`) **emptied `partner_contacts_master.csv`** during the 2026-10-11 refill run - and because that script was being edited while it ran. Tests: `test_csv_append.py` (31 offline cases). |

State: `state.json` + `outreach_log.csv` are the campaign's **contact history**.
Never delete them. The test suite redirects to a temp dir; keep it that way.
`auth_rejections.txt` (new 2026-10-05) is runtime data too, the gateway
rejections `harvest_bounces.py` records, gitignored, regenerable from the inbox.

Cron (WSL Hermes, `~/.hermes/cron/jobs.json`, `hermes cron list`). Seven jobs;
read `hermes-outreach-cron` for the full picture, this is the index:
`06dc0591b995` INSTABOX POOL HARVEST `0 20 * * 0-4` (**buyer supply, 1,200 domains at 32 workers on freemachine**),
`be4516e1f17a` PARTNER DIRECTORY REFILL `0 19 * * 0-4`,
`e17cf424467a` PROSPECT POOL REFILL `0 21 * * 0-4`,
`7fbe48d22b87` DAILY OUTREACH REFILL `0 0 * * 1-5` (**buyer, `LIMIT=30`**),
`69327c970056` PARTNER OUTREACH REFILL `30 9 * * 1-5` (**agency, `LIMIT=50`**),
`f46166120182` WEEKDAY VERIFIER PREFILL `0 10 * * 1-5`,
`104b31c84850` WEEKEND VERIFIER PREFILL `0 10 * * 0,6`.
The directory refill grows the agency pool in the evening, the pool refill measures
the buyer pool after it, the buyer stages at 00:00, the agency stages at 09:30, and
the verifier prefill mops up at 10:00. Each staging job stages for a **same-day**
send (buyer 09:00, agency 13:00). The daily job harvests bounces before it cleans.
(**2026-10-13:** the buyer staging moved 01:30 -> 00:00 so the day's queue is in
place when Vinny checks the folder at night; it is same-day staging, so the folder
is empty from ~12:00 until the run. See `hermes-outreach-cron` for why midnight and
why not the evening.)

**2026-10-11 channel rebalance:** buyer 100 -> 30/day, agency 30 -> 50/day, after
the first real agency reply landed. The **sourcing** constraint, not the meter, is
what limits the agency channel (~7.6 usable addresses per OSM metro). See
`hermes-outreach-cron` and `references/partner-referral-channel.md`.

Git: `github.com/vincentsativa/money_ideas`, private, branch `main`, pushed from
WSL. Commit code only, never `state.json` or the `prospects_*.csv` runtime data.

## Gotchas that have already cost time

- **Verification has three layers:** the local RCPT probe (free, IPv6-only reach),
  the hosted verifier for UNKNOWN only (free 100/day, key in `mailer.env`), and
  `verify_cache.json` (30-day TTL, `MAIL_VERIFY_RECHECK=1` to force a re-probe).
  A remote DEAD is never written to the suppression file, the `REMOTE_` code
  prefix carries that through the cache.
- **Gateway rejection ≠ dead mailbox (2026-10-05).** A Microsoft `5.7.515` /
  `5.7.509` or a Gmail unauthenticated refusal means the SENDING domain failed
  SPF/DKIM/DMARC; the recipient is fine. `harvest_bounces.py` records these in
  `auth_rejections.txt` and never suppresses. `outreach.py` refuses a live
  `--send` when the sending domain fails the auth pre-flight
  (`auth_enforcement.preflight_sending_domain()`), unless `--skip-auth-preflight`.
  Live example 2026-10-05: `user@example.com` refused with 550 5.7.509 after the
  recipient's own gateway re-injected our message from an IP outside
  `_spf-us.ionos.com` (a forwarding/ARC artifact, still the new failure mode).
- **An `except Exception: pass` in a path that must work is a bug.** One swallowed
  a `NameError` in `save_verify_cache` and the cache looked like it worked while
  writing nothing. Never fatal, never silent: warn and return True/False.
- **A test must never write a production file.** The suite redirects state, log,
  stop list AND the verdict cache into a per-run temp dir at module level; two
  `@example.com` fixtures had reached the real cache before that was added.
- **Never put a shell variable in a `wsl.exe ... bash -lc '...'` one-liner.**
  `D=$(mktemp -d)` arrives empty and silently drops the flag. Write the script to
  `/mnt~/<file>` and run
  `wsl.exe -d Ubuntu -u vincent -- python3 /mnt~/<file>`.
- Files WSL executes must have **LF** endings. CRLF fails with a fake syntax error.
- **imaplib:** `search()` returns *sequence* numbers. `UID STORE`/`UID FETCH` on
  those is a silent no-op, so `EXPUNGE` removes nothing. Use `UID SEARCH` first.
- **A domain is not a person.** Two pool domains can share one contact address;
  a run keeps one email per address. `verify_scheduled` counts stored MESSAGES,
  not unique addresses, or a duplicate cancels out on both sides.
- **Link invariant:** clean address to the reader, UTM tags + click token in the
  href. `link_tracked` + `link_masked` on the read-back enforce it.
- **`VERIFY_BACKFILL_MARGIN`:** with `--hold-unknown` only the VERIFIED head may
  send, and a 175-candidate window yields ~85 verified. Default raised 75 -> 200
  (a 300-candidate window) on 2026-10-08, which actually fills 100 once the pool
  is healthy; measured that night: 233 sendable -> 100 staged, read-back OK.
- **Queued mail never re-renders.** A batch already in `Scheduled` keeps the old
  format; changing it means the documented re-stage (back up the folder, empty
  it, roll back `state.json` from `state.json.bak-sched-*`, re-run with `START`).
- **When told to make a skill, make it here** (`~\.pi\agent\skills\`)
  or in `~/.hermes/skills/` and say which. Then record the path in
  this file.

## Long jobs / narration

The pipeline skill's rule: a multi-call sequence with no visible progress reads
as disappearing. Send ONE line naming what is running and that nothing has been
sent or posted, then keep working. Do not answer "what are you doing" with a plan
for what will happen next.
