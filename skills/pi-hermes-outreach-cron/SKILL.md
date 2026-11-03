---
name: hermes-outreach-cron
description: >-
  Find, read, and change Vinny's cold-outreach email sending schedule. The
  sender is NOT in the Windows pi workspace and NOT a system crontab, it is the
  WSL Hermes agent's own cron (`~/.hermes`, user `<linux-user>`, jobs in
  `~/.hermes/cron/jobs.json`). Use when Vinny says "change the 5am/7am cron",
  "the emails didn't send", "why are they scheduled for tomorrow", "make it send
  Monday-Friday / no weekends", "set the outreach time to 9pm/11pm", "stage N
  emails", "send N today", "outreach schedule", "daily outreach refill", or
  "prospect pool refill". When Vinny says just **"email"**, "the emails",
  "the outreach" or "the campaign", he means THIS pipeline, the WSL
  `~/money_ideas` sender, not Gmail, Outlook, n8n or any Windows mail tooling.
---

# Hermes Outreach Cron (the real sender)

> **"email" = this project.** Do not go hunting the Windows workspace, Gmail,
> n8n or Outlook. If it is about email, `cd ~/money_ideas` in WSL first.

Vinny's IONOS cold-outreach is driven by **Hermes cron jobs inside WSL**, not by
anything on the Windows side. If you are in a pi session, you are in
Msys/Windows, you MUST route through WSL.

```bash
wsl.exe -d Ubuntu -- bash -lc '<command>'
```

Do **not** hunt the Windows crontab, Task Scheduler, n8n, or `~/workspace` for
this. It lives here:

| Thing | Value |
|---|---|
| Hermes home | `~/.hermes` (user `<linux-user>`) |
| Jobs file | `~/.hermes/cron/jobs.json` |
| Cron CLI | `~/.local/bin/hermes cron {list,edit,run,runs,pause,resume}` |
| Job scripts | `~/.hermes/scripts/*.sh` |
| Workdir | `~/money_ideas` |
| Version control | `github.com/vincentsativa/money_ideas`, **private**, branch `main`. Pushed from WSL via the stored git credential (the `gh` PAT is scoped and 404s on this repo; use `git push`). |
| Credentials | `~/.config/phantombyte/mailer.env` (SMTP pass + postal address) |
| Mailbox | `hello@example.com` (imap.ionos.com:993) |
| Queued mail | IONOS `Scheduled` folder (send time in `X-OX-Date-To-Send`) |

## The seven jobs

| Job ID | Name | Script | Current schedule | Rate (2026-10-11) |
|---|---|---|---|---|
| `be4516e1f17a` | PARTNER DIRECTORY REFILL | `partner_directory_refill.sh` | `0 19 * * 0-4` (7pm Sun-Thu) | scrape, nothing sent |
| `e17cf424467a` | PROSPECT POOL REFILL | `refill_check.sh` | `0 21 * * 0-4` (9pm Sun-Thu) | nothing; fires at `REFILL_AT=100` |
| `7fbe48d22b87` | DAILY OUTREACH REFILL | `daily_outreach_refill.sh` | `0 0 * * 1-5` (00:00 Mon-Fri) | **buyer `LIMIT=30`, `GAP=6`** |
| `69327c970056` | PARTNER OUTREACH REFILL | `partner_refill.sh` | `30 9 * * 1-5` (9:30am Mon-Fri) | **agency `LIMIT=50`, `GAP=4`** |
| `f46166120182` | WEEKDAY VERIFIER PREFILL | `weekday_verifier_prefill.sh` | `0 10 * * 1-5` (10am Mon-Fri) | nothing; verify `LIMIT=40` |
| `104b31c84850` | WEEKEND VERIFIER PREFILL | `weekend_verifier_prefill.sh` | `0 10 * * 0,6` (10am Sat + Sun) | nothing; verify `LIMIT=60` Sat / `40` Sun |
| `06dc0591b995` | INSTABOX POOL HARVEST | `pool_harvest_instabox.sh` | `0 20 * * 0-4` (8pm Sun-Thu) | **buyer supply: `HARVEST_N=1200` domains, `HARVEST_WORKERS=32` on the InstaBox box** |

### The buyer pool is fed by a harvest job, and the numbers are already set (2026-10-30)

`INSTABOX POOL HARVEST` exists because the buyer pool drained 285 -> 20 in eight
nights while the nightly cron only *measured* it off a stale file. It picks
buyer-fit domains that are qualified, unharvested and uncontacted, uploads them
with `find_contacts.py` to `freemachine` (`/data/workspace/harvest`), runs the
harvest there under `nohup`, polls over `exec`, pulls the CSV back and merges it
with `csv_append.py`.

**Measured on 2026-10-30, one batch, same machine:** 4 workers = 32 domains/min,
**16 workers = 67 domains/min**, box load average 0.04. It is bound by other
people's web servers, not CPU. Defaults are now `HARVEST_WORKERS=32` in the
script and `WORKERS=16` in `harvest.sh`, do not lower them back to 4 out of
habit, and do not treat a flat sample as proof: check `pgrep -af find_contacts.py`
ON THE BOX, because killing the WSL wrapper leaves the remote process running at
the old worker count (that is exactly what happened on the first attempt).

**Rows are not domains.** `find_contacts.py` writes a row only when it finds an
address, so `wc -l` on the output can sit still for minutes while work is
happening. Measure progress with the `N/M` counter in the harvest log, not with
row counts.

Order matters and is why the times are what they are: the directory refill grows the
agency pool in the evening, the pool refill measures the buyer pool after it, the
buyer stages at 00:00, the agency stages at 09:30, and the verifier prefill mops up
at 10:00 once both have taken what they need.

## Where the agency prospects come from (added 2026-10-11)

**OSM is exhausted for agencies.** Measured: 12 sourced metros gave 272 raw
partner prospects, 187 contact rows, and 91 addresses - **7.6 per metro**. The
whole 55-metro queue is worth ~400 addresses, about 8 send-days at 50/day. Do not
answer a pool shortage by adding metros; add sources.

`directory_prospects.py` reads agency **directories** instead, and they are the
right kind of source: they exist to list agencies and they publish each agency's
own website, which is exactly what `email_scan.py` and `find_contacts.py` consume.

| Source | Profiles available | Works? |
|---|---|---|
| `topdevelopers.co` | 10,836 | yes - default |
| `superbcompanies.com` | 77,931 | yes |
| `digitalagencynetwork.com` | ~1,000 per child sitemap | flaky, child sitemaps usually time out |
| clutch.co, techbehemoths.com, themanifest.com, yellowpages.com, upcity.com | - | **no** - HTTP 403 at robots.txt |
| designrush.com, goodfirms.co, sortlist.com | - | **no** - robots.txt says yes, sitemaps 403 through Cloudflare |

Measured extraction accuracy on the first twenty profiles of each working source:
**40/40 correct**. The scraper honours robots.txt at runtime (RFC 9309 matching,
including query strings), identifies itself with a contact address, and space
requests `DELAY` seconds apart on a single thread, because each source is ONE host
and a worker pool against one host is abuse rather than speed.

```bash
# what it does, and the knobs
DRY=1 PROFILES=8 bash ~/.hermes/scripts/partner_directory_refill.sh   # enumerate only
SOURCE=topdevelopers PROFILES=250 DELAY=3.0 bash ~/.hermes/scripts/partner_directory_refill.sh
```

Chain, all inside that one script: `directory_prospects.py` (scrape -> append to
`partner_prospects_master.csv`) -> `directory_pool_todo.py` (what is actually new)
-> `email_scan.py` (DNS grade) -> `harvest.sh` (4 parallel contact harvesters) ->
append to the two master files -> print the eligible count. **It never sends mail**
and it never stages; `PARTNER OUTREACH REFILL` does that at 09:30.

`RETRY_BACKLOG=1` re-attempts older pool domains that still have no address. It is
off by default: measured 2026-10-11, the first run harvested the whole 205-domain
backlog instead of the 24 domains it had just found, which is mostly wasted work.

Tests: `python3 test_directory_prospects.py` (85 offline cases, no network; the real
profile markup is embedded as fixtures). It caught a live bug on the day it was
written: `urlparse().path` drops the query string, so a `Disallow: /*?` rule could
never match and a forbidding rule silently became a permitting one.

### Pool appends go through `csv_append.py`, and never edit a running script

**A master file was emptied on 2026-10-11.** `partner_contacts_master.csv` - 187 rows
of contact history - was truncated to zero bytes mid-run and restored from a backup
taken minutes earlier, by luck of timing. Two things went wrong, and the second is
the real cause:

1. The shell idiom `[ -s "$MASTER" ] || head -1 "$SRC" > "$MASTER"` performs the
   redirection BEFORE it runs the command, so with `$SRC` missing it truncated the
   master to zero bytes and only then failed to read its input. **Never use
   `cmd > file` to bootstrap a master; check the source first.**
2. **The wrapper script was being edited while it was running.** Bash reads a script
   file incrementally, so changing the file's length mid-execution shifts the read
   offset and bash resumes *part-way through a command*. That is what lost the guard
   and left only the truncating redirect. It also produced a phantom
   `syntax error near unexpected token 'else'` in a file `bash -n` had just called
   clean, so a phantom syntax error from a script that parses fine is a symptom of
   this, not a syntax bug. **Never edit a script while a process is executing it.**

All pool appends now run through `csv_append.py`, where reading before writing is
structural: it refuses a missing/empty/headerless source, refuses a source whose
header lacks the key column, dedupes on the key so a re-run is idempotent, pads short
rows so columns cannot shift, refuses if the row count would drop, and writes via a
temp file plus `os.replace`. `python3 test_csv_append.py` is 31 offline cases and its
first case is the incident: a missing, empty, headerless and schema-mismatched source
each have to leave the master byte-identical.

The old blind `tail -n +2 >>` had also left **25 duplicate domains** in
`partner_scan_master.csv`; `csv_append.py` deduped it in place (345 -> 320 lines, 0
duplicates).

Verified end to end after the fix by a real refill run: 6 new agency domains scraped,
scanned, harvested and merged; `partner_contacts_master.csv` 187 -> 193 rows intact;
eligible partner addresses **19 -> 22**; nothing sent.

## Channel re-prioritisation, 2026-10-11 (Vinny), read before changing any rate

**Buyer 100 -> 30/day. Agency 30 -> 50/day.** The evidence: the first real human
reply in the mailbox arrived on the **agency** pitch (`user@example.com`,
Oct 11, "Re: A white-label email security fix for your agency") against roughly
700 buyer sends and zero replies. 43 agencies had been mailed, so that is a 2.3%
reply rate on the partner channel versus 0% on the buyer channel.

**This is a throttle, not a pause.** Vinny asked whether pausing the buyer
channel outright was better. It is not, for three reasons:

1. It costs nothing to keep running at 30/day, same cron, same scripts, no
   attention. A pause saves no labour.
2. It keeps `hello@example.com` sending every weekday, which is the
   reputation the agency channel needs to stay warm. A silent domain is worse
   than a quiet one.
3. The buyer pool is the raw material the partner list is filtered out of: it
   already holds ~12,350 scanned domains, and the partner-fit slice of it
   (it_msp / b2b_agency / saas / consulting) is only partly used. Pausing stops
   the pipeline that produces that.

**The thing that actually binds is sourcing, not send rate.** Measured
2026-10-11: OSM gives ~22.7 raw partner prospects and ~7.6 usable email addresses
per metro, and 43 of them have already been mailed. The whole 55-metro queue in
`partner_metros4.txt` is worth ~400 addresses, i.e. about **8 send-days at
50/day**. After that OSM is exhausted for this segment. Expect the partner job to
start reporting "nothing staged" around then unless a directory source is added.
Details and the rejected alternatives are in
`~/.hermes/skills/email-deliverability-rescue-workflow/references/partner-referral-channel.md`.

**Timing consequence.** The partner job moved 10:30 -> **09:30** so it (a) gets
first call on the shared 100/day hosted-verifier tier before the 10:00 weekday
prefill spends it, and (b) still has time to source five metros and stage before
its same-day 13:00 send. Send windows no longer overlap: buyer runs 09:00-11:54
(30 x 6min), agency runs 13:00-16:20 (50 x 4min).

**Timing (changed 2026-10-08, corrected 2026-10-09; staging moved to midnight
2026-10-13).** The daily job stages at **00:00 Mon-Fri** and the pool refill runs
**3h before each staging run** (`21:00` Sun-Thu -> `00:00` Mon-Fri). It stages for
the **same day 09:00**, which is what keeps the read-back honest: the batch leaves
the folder before the next midnight run, so the folder never holds two batches at
once. (Before 2026-10-09 it staged for the *next* day, so at 01:30 the previous
day's batch, sending that same 09:00, was still present, and the whole-folder
count check would have failed from the second run on.) **Why 00:00 and not the
old 01:30:** staging is same-day, so the folder is empty from the moment the
morning send finishes (~12:00) until the staging run. At 01:30 Vinny looked at the
folder at night, saw it empty and read that as "nothing staged for tomorrow" (two
nights running, 2026-10-12/13). 00:00 is the earliest a same-day batch can be
staged and still send that same morning, so the queue is in place before he
checks. 00:00 also sits just after the daily hosted-verifier reset, exactly where
01:30 did, so the staging keeps first call on the fresh 100/day tier. **Do NOT
move this into the evening (e.g. 23:30) unless the verifier tier's reset time is
confirmed first:** by then the day's partner run (09:30) and prefill (10:00) have
spent it. Nothing runs the weekend, so nothing is queued for a weekend send.

- **PROSPECT POOL REFILL (9pm Sat, Sun-Wed)**, only measures the pool; if
  healthy it does nothing, if short it follows the `prospect-refill` skill. Sends
  no mail.
- **DAILY OUTREACH REFILL (00:00 Mon-Fri)**, the one that stages the day's
  emails: harvests bounces, cleans the pool, runs the gate chain, queues N
  messages into the IONOS `Scheduled` folder for **that day 09:00**, verifies by
  read-back. It runs at 00:00, after the 21:00 pool refill, before Vinny looks at
  the folder, and 00:00 is the earliest a same-day batch can be staged.
  **N is 30 as of 2026-10-11** (was 100), see the re-prioritisation above.
- **WEEKEND VERIFIER PREFILL (10am Sat/Sun, `--no-agent`)**, verifies up to 100
  uncached pool addresses into `verify_cache.json`. **Sends no mail.** It exists
  because the hosted verifier tier is 100/day and does NOT roll over, and nothing
  sends on Friday or Saturday: those are two days of free capacity that would
  otherwise be thrown away, and a weekday run that re-verified the same
  addresses would spend them twice. Its stdout is delivered verbatim, so no model
  is involved and there is nothing to hallucinate.
- **WEEKDAY VERIFIER PREFILL (10am Mon-Fri, `--no-agent`, added 2026-10-08)**, 
  the same idea for weekdays: spend the day's free verifier credits on the pool
  at 10am (after the 09:00 send, well before the next 00:00 staging) so the
  staging run meets fewer UNKNOWNs and can actually fill `--limit`. Sends no
  mail.
- **PARTNER OUTREACH REFILL (9:30am Mon-Fri, `--no-agent`, added 2026-10-09,
  moved 10:30 -> 09:30 on 2026-10-11)**, 
  stages the partner/agency batch (`partner_outreach.py`) for a **same-day 13:00**
  send. It runs mid-morning, not overnight, on purpose: the buyer job's
  read-back counts the **whole** `Scheduled` folder, so a partner batch sitting
  there when the buyer stages would fail the buyer's count. Staging and sending
  the same day means the partner messages are gone before the buyer's next 00:00
  run, the two channels never occupy the folder at the same time. It also
  harvests bounces first so a dead partner mailbox is suppressed before staging.
  Queues only; sends no mail. **Self-sourcing:** when the eligible pool is short
  it sources the next unused metros from `partner_metros4.txt` (fresh metros, not
  in the earlier partner passes or the buyer `osm_metros*.txt`), runs
  `osm_industry_prospects.py` -> `email_scan.py` -> `find_contacts.py`, appends
  to a `partner_*_master.csv` pool, marks the metro in
  `partner_metros_done.txt`, and re-counts before staging. Measured 2026-10-09:
  Seattle added ~42 prospects and lifted eligible 7 -> 19. Measured 2026-10-11:
  **only 19 eligible against a `LIMIT=50`**, this job is sourcing-limited, not
  rate-limited; do not raise `LIMIT` further without feeding the pool.

### Automations live in Hermes cron, never Windows

Anything that must happen on a schedule goes in **Hermes cron inside WSL**,
because the Hermes agent is always on and the Windows machine is not. Not Task
Scheduler, not a pi job, not n8n. Add one with:

```bash
~/.local/bin/hermes cron create '0 10 * * 0,6' --name 'NAME' \
  --script script_name.sh --no-agent --deliver telegram \
  --model deepseek-v4.1-flash \
  --workdir ~/money_ideas
```

**`--model deepseek-v4.1-flash` is NOT optional.** Omit it and the job follows
`hermes model` (the main agent model) at fire time. **Vinny switches the main
agent model often**, so an unpinned job fires on whatever model happens to be
active at that moment, that is the exact failure this prevents. Every job in
this project is pinned to `deepseek-v4.1-flash`. Vinny had to fix this by hand
after a job was created without it (2026-10-09). Set it at creation, every time, 
do not rely on the default and do not make him babysit it.

The script itself goes in `~/.hermes/scripts/` (outside every repo), must be LF
and executable, and should `cd` to `money_ideas` and `source`
`~/.config/phantombyte/mailer.env` itself.

## The Mon-Fri / no-weekends rule (two places, do not remove either)

1. **Cron expression** `0-4` on both jobs, they run **Sunday through Thursday
   nights only** (no Friday cron, no Saturday cron). Standard 5-field cron:
   `min hour dom month dow`; `0`=Sunday, `1`=Monday, ... `4`=Thursday,
   `5`=Friday, `6`=Saturday, `7`=Sunday.
2. **The script's send date** in
   `~/.hermes/scripts/daily_outreach_refill.sh`. It defaults `START`
   to **today 09:00** (same-day), because the cron runs Mon-Fri 00:00, and a
   weekend manual run rolls forward to Monday. Same-day staging is what keeps
   the folder from holding two batches at the 00:00 read-back (see Timing). An
   explicit `START=...` env var still wins (used for a deliberate same-day test
   batch).

The resulting cadence, Sunday stages Monday, Thursday stages Friday, and no
Friday/Saturday cron at all:

| Cron night | Stages/sends |
|---|---|
| Sun 9pm refill -> Mon 00:00 stage | Mon 09:00 (same day) |
| Mon 9pm refill -> Tue 00:00 stage | Tue 09:00 |
| Tue 9pm refill -> Wed 00:00 stage | Wed 09:00 |
| Wed 9pm refill -> Thu 00:00 stage | Thu 09:00 |
| Thu 9pm refill -> Fri 00:00 stage | Fri 09:00 |
| Sat / Sun | (no cron) |

## Change the schedule

```bash
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron edit e17cf424467a --schedule "0 21 * * 0-4"'
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron edit 7fbe48d22b87 --schedule "0 0 * * 1-5"'
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron edit f46166120182 --schedule "0 10 * * 1-5"'
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron edit 69327c970056 --schedule "30 9 * * 1-5"'
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron edit be4516e1f17a --schedule "0 19 * * 0-4"'
```

**A rate is not a schedule.** The `LIMIT` / `GAP` values live in the script
header (`LIMIT="${LIMIT:-50}"`), not in the cron job, so changing volume means
editing the script and the cron expression usually stays put. Current: buyer 30,
agency 50.

Verify after (never trust the edit echo alone):

```bash
wsl.exe -d Ubuntu -- bash -lc '~/.local/bin/hermes cron list'
```

## Stage / send N emails (the pipeline)

The staging pipeline lives in `~/money_ideas`:

```
clean_prospects.py  ->  schedule_drafts.py  ->  outreach.py  ->  IONOS Scheduled
                                                        \-> check_scheduled.py (independent read-back)
```

One command (this is what the cron runs):

```bash
wsl.exe -d Ubuntu -- bash -lc '
cd ~/money_ideas
source ~/.config/phantombyte/mailer.env
LIMIT=100 START="2026-09-30T11:00" GAP=2 bash ~/.hermes/scripts/daily_outreach_refill.sh'
```

- `LIMIT` = how many to stage. `START` = local (America/New_York) send start,
  `YYYY-MM-DDTHH:MM`. `GAP` = minutes between sends (buyer: 30 x 6min ≈ 3h;
  agency: 50 x 4min ≈ 3h20m).
- Omit `START` to get the next weekday 09:00.
- This only **queues** send times. IONOS sends them; the folder is the record.
- The gate chain (role rule, buyer-fit, dedupe, suppression, mailbox verify) runs
  inside `outreach.py`. On a real run **never** pass `--no-fit` or `--allow-role`.

## Send N TODAY (test a fix)

Set `START` to a slot still in the future today, e.g. 11:00. The folder must be
empty first or the count check fails, see below.

## Re-time an already-queued batch (move `Scheduled` -> today)

There is no reschedule script. Use the documented recovery:

1. Back up the folder (read raw `BODY.PEEK[]` for every message).
2. Empty it: `SELECT Scheduled`, then **UID SEARCH** for the uid set, then
   `UID STORE <uids> +FLAGS (\Deleted)`, then `EXPUNGE`. Do NOT feed the
   numbers from `search()` into a `UID` command, `search()` returns *sequence*
   numbers, and `UID FETCH`/`UID STORE` on numbers that are not UIDs returns an
   empty set, so the flag is never set, `EXPUNGE` removes nothing, and the
   folder looks untouched (this happened on 2026-10-01). Verify the flag count
   equals the message count before expunging.
3. Restore pre-stage state: `cp state.json.bak-sched-<stamp> state.json`
   (the `bak-sched-*` file is the state *before* that staging run).
4. Re-run the one command with the new `START`.
5. Verify: `python3 check_scheduled.py --expect N` must print `RESULT: OK`.

The count-mismatch trap: `verify_scheduled` compares the folder size to the plan;
leftover mail makes it FAIL **before** state is saved, leaving queued messages
untracked. Always empty the folder before re-staging, and reconcile from the
FOLDER, never from `state.json`.

## Delivered lead groups (asset, 2026-10-01)

Compiled lists of addresses mailed that **did not bounce**, grouped by campaign,
so a future offer can pull a clean list (or the group can be sold). Lives in
`~/money_ideas/leads/`; built by `build_lead_groups.py`.

| File | What |
|---|---|
| `leads/groups.json` | registry: group -> offer, counts, files |
| `leads/email_deliverability.csv` | group **email_deliverability** + metadata |
| `leads/email_deliverability.txt` | same group, plain address list |
| `leads/delivered_all.txt` | union of every group |
| `leads/README.md` | full docs + how to add a future group |

```bash
wsl.exe -d Ubuntu -- bash -lc 'cd ~/money_ideas && source ~/.config/phantombyte/mailer.env && python3 build_lead_groups.py'
```

- **delivered = sent − bounced**: reads IONOS `Sent Items` over IMAP, subtracts
  `suppressed_addresses.txt`; excludes free/consumer mailboxes and our own.
- **Self-correcting**: re-run after sends; a later bounce drops the address out,
  new sends get added, first/last-sent merged.
- Add a future offer: append a subject-rule tuple to `GROUPS` in
  `build_lead_groups.py`, re-run; an address can belong to several groups.
- As of 2026-10-01: **354** delivered in `email_deliverability` (98 with a named person).

## Verify (a run is not done until this passes)

```bash
wsl.exe -d Ubuntu -- bash -lc '
cd ~/money_ideas
source ~/.config/phantombyte/mailer.env
python3 check_scheduled.py --expect 100'
```

Must print `RESULT: OK`, with a first/last slot on the intended local day.

## The offer link: clean text, tagged href

The offer URL is tagged for attribution (`utm_source/medium/campaign/content`,
plus `o` = offer and `c` = per-recipient click token). It must never be **read**
with those parameters in it, a visible
`...?utm_source=outreach&utm_medium=email&...&c=<token>` reads like a tracking
redirect to the one person it is not for (Vinny, 2026-10-01).

The invariant in one line: **clean text to the reader, tags in the href.**

```html
<a href="https://phantom-byte.com/email-deliverability-rescue?utm_source=outreach&amp;utm_medium=email&amp;utm_campaign=deliverability-rescue&amp;utm_content=dmarc_missing&amp;o=email-deliverability-rescue&amp;c=<token>">https://phantom-byte.com/email-deliverability-rescue</a>
```

| Piece | Where |
|---|---|
| `clean_url`, `mask_tracked_urls_html`, `plain_body_to_html` | `outreach.py`, the only implementation |
| Staged path | `schedule_drafts.body_to_html` -> `outreach.plain_body_to_html` |
| Direct sends / IMAP drafts | `outreach.send_one`, `stage_drafts.py` (multipart/alternative) |
| Proof on read-back | `schedule_drafts.verify_scheduled`: `link_tracked` + `link_masked` |
| Proof in the suite | `test_outreach.check_tracked_link_masking` |

- Only a URL with a query string or fragment is rewrapped; a bare URL stays text.
- The plain-text part keeps the raw tagged URL on purpose: a text-only client
  has nowhere else to carry the parameters, and dropping them drops the click.
- IONOS stores the href with `&amp;` but normalises `&quot;` back to `"`, so the
  `optout` check (`Reply "stop"`) keeps working; the two link checks pass either way.
- **Queued mail does not pick this up.** A batch already in the IONOS
  `Scheduled` folder keeps the raw tagged URL. Applying the fix to an
  already-queued batch means the documented re-stage (empty the folder ->
  restore `state.json.bak-sched-*` -> re-run with `START`), which Vinny must approve.

## Hard rules

- This tooling only **queues** sends. Vinny reviews; never auto-send behind him.
- Never touch SPF/DKIM/DMARC/MX as part of scheduling.
- Never mail a role box (`info@`, `service@`, `admin@`, …); the cleaner enforces it.
- Run every script inside WSL. Files must be LF.
- **Every cron job is pinned to `--model deepseek-v4.1-flash`.** Creating one
  without it silently inherits the main agent model; never do it.
- Weekend sends are off by Vinny's own warm-up strategy (20 -> 50 -> 100/day).
- Proof is a fresh run's output that you read, never a remembered count.

## Gotchas learned the hard way

- **A domain is not a person.** Two pool domains can share one contact address
  (same owner runs both), and when neither is in state yet both pass every
  gate, the contacted-address gate only blocks an address it has already
  SEEN. On 2026-10-01 that staged 8 people two near-identical emails for one
  morning. Fixed 2026-10-01: the run keeps one email per address (the twin is
  skipped for that run only, never suppressed).
- **`verify_scheduled` used to be blind to that**, because it keyed the plan
  and the folder by address: a duplicate collapsed on both sides by the same
  amount and the count check passed. It now counts stored MESSAGES and names
  any address holding more than one. If a run reports "verified" but
  `check_scheduled.py` fails on duplicates, that is this class of bug.

- **Never put a shell variable in a `wsl.exe ... bash -lc '...'` one-liner.**
  `D=$(mktemp -d) && ... --drafts "$D"` reaches WSL with `$D` *empty*, silently
  dropping `--drafts`. Write the script to `/mnt/c/...` and run
  `wsl.exe -d Ubuntu -u vincent -- python3 /mnt~/<file>`.

- The sender is in **WSL Hermes cron**, not Windows. `hermes` from the pi shell
  hits the *Windows* install, always use the full `wsl.exe -d Ubuntu -- bash -lc`
  route and `~/.local/bin/hermes`.
- The 5am/7am jobs did **not** send, 7am *staged* 100 for `tomorrow 09:00`.
  Do not report "sent" from a staging run.
- Editing jobs.json by hand is unnecessary; use `hermes cron edit`.
- Quoting: running python heredocs through `wsl.exe ... bash -lc '...'` mangles
  nested quotes. Write the script to a file and run
  `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash /mnt~/<file>`.
