---
name: ionos-daily-outreach-schedule
description: Use when working Vinny's IONOS outreach mail, whether scheduling N screened emails into the Scheduled folder, reading or searching his mailbox over IMAP, or building the free domain findings sheet for a prospect or partner.
trigger: IONOS outreach mail work, which is scheduling N for a date and time, reading or searching the mailbox, or producing a free domain report for a prospect or agency partner.
---

# Daily IONOS outreach scheduling (do it right, first time)

## The one command
```
source ~/.config/phantombyte/mailer.env
export VERIFY_BACKFILL_MARGIN=60
/usr/bin/python3 -u schedule_drafts.py \
  --csv scan_master.csv \
  --emails contacts_master.csv \
  --offer-url https://phantom-byte.com/email-deliverability-rescue \
  --limit N \
  --start <YYYY-MM-DD>T<HH:MM> \
  --gap 6 --hold-unknown
```
- Interpreter is ALWAYS the explicit `/usr/bin/python3`, never bare `python3`. A bare `python3` resolves to whatever PATH the caller has, and under cron that is a different interpreter that may not import `requests`, so the whole run dies at import with nothing staged. `/usr/bin/python3` carries `requests`, `imaplib` and imports every module in the chain.
- Pool defaults to the cleaned MASTER pool (`scan_master.csv` + `contacts_master.csv`, the union of every batch, hundreds of sendable). The older single-batch pool is `scan_2000_b4_results.csv` + `contacts_2000_b4_final.csv`.
- `--limit N`: the number Vinny named. No cap and no default count.
- `--start`: local time (America/New_York), a FUTURE slot. Confirm with `date`.
- `--hold-unknown`: hold out addresses the probe could not decide, instead of mailing them.
- `--gap 6`: one every six minutes (the throttle since the buyer channel went to 30/day). `--gap 2` for a small test batch. `--jitter` (default 2) spreads each gap by up to 2 minutes; pass `--jitter 0` for exact spacing.

## THE SELECTION RULE (this is what prevents a short or dirty batch)
- ALWAYS draw from the pool: `scan_master.csv` + `contacts_master.csv` (the cleaned master, hundreds of screened prospects), or the single batch `scan_2000_b4_results.csv` + `contacts_2000_b4_final.csv`. `--limit N` takes the first N that pass the gate chain, so N clean is achievable from the pool.
- NEVER use a smaller curated list and then pass `--no-fit` to reach N. That ships chains, institutions, and function desks. If N clean cannot come from the pool, report the real achievable number and why; do NOT lower the screen to hit a count.
- NEVER pass `--no-fit` on a real schedule. The buyer-fit filter stays on.

## The cron wrapper: `~/.hermes/scripts/daily_outreach_refill.sh`
The weekday `DAILY OUTREACH REFILL` cron calls that shell script from `~/money_ideas`, not the one command directly. It harvests bounces, cleans the pool, stages `LIMIT` (default 30) at `START` (default today 09:00, weekend rolls to Monday), runs the read-back, then refreshes `leads/`.
- The script pins `PY="${PY:-/usr/bin/python3}"` and every call in it uses `"$PY"`, with a guard that aborts in one line if that interpreter cannot import `requests` and `imaplib`. Keep both if you edit it: a bare `python3` there is the difference between 30 emails staged and a 00:00 failure message with an empty folder.
- Test an edit to it with `bash -n <script>` plus `DRY=1 LIMIT=3 VERIFY_BACKFILL_MARGIN=5 bash <script>`. That exercises harvest, clean, the gate chain and the lead refresh without staging anything or spending the day's verifier tier. The dry run legitimately ends with `no drafts rendered` when today's candidates are already deduped out by `state.json`; that is not a failure.
- Prove the pin itself, not just the syntax: run the script with `PY=/usr/bin/nonexistent-python` and confirm it prints the ABORT line and exits 1.

### Recovering a missed staging day
When the cron reports a failure and the folder is empty, stage the batch by hand in the SAME session with the one command, then report. Never hand back a failure notice with nothing staged.
1. `date` for the next future slot, and select the Scheduled folder over IMAP to confirm it is empty (`M.uid('SEARCH', None, 'ALL')`).
2. Run the one command with the pinned interpreter and the real N.
3. Post-flight read-back (`check_scheduled.py --expect N`) must print `RESULT: OK`, and spot-read the first and last folder entries for recipient and subject.
IMAP note: `M.select()` and `M.uid('SEARCH', ...)` return a 2-tuple, so `M.search(None,'ALL')` with a 3-way unpack raises `ValueError: not enough values to unpack` — use `M.uid('SEARCH', None, 'ALL')`.

## What the command does
`schedule_drafts.py` runs `outreach.py` as a dry run (the full gate chain), then schedules each message into the IONOS Scheduled folder over the Open-Xchange HTTP API with a real `dateToSend`, then reads every message back and verifies the body and the send time. The gate chain:
qualified defect -> stop list -> suppression (DSN hard-bounce list, harvested from Inbox + Spam automatically) -> ROLE RULE (every shared role mailbox dropped, default; `--allow-role` only overrides for a test) -> buyer-fit (chains, institutions, function desks, never-monitored locals like noreply/webmaster, misspelled provider domains) -> dedupe (domain AND address, from `state.json`) -> tier sort -> mailbox verification -> compose.

## Port 25 and the mailbox verification (do not repeat the false alarm)
- The RCPT probe runs on the Windows side through the bridge. Port 25 IS reachable from Windows. If anything claims otherwise, prove it: `/usr/bin/python3 mail_verify.py contact@ancroofing.com` returns a real `550`.
- The probe is the slow step and prints progress in 25-address chunks. It is NOT hung; let it finish.
- The retry pass is OFF by default (fast). Enable it with `MAIL_VERIFY_RETRY=1` only for the marginal recovery.
- For a fast schedule you may add `--no-verify`; the trade is that a newly dead address bounces once and is then auto-suppressed by the next run's harvest. Name that trade when you use it.

## Pre-flight
1. `source ~/.config/phantombyte/mailer.env`
2. `date` to confirm `--start` is in the future.
3. Use the exact N Vinny named.

## Post-flight (not done until this passes)
1. The script must print `N of N scheduled ... and every message verified by read-back`.
2. Run the independent read-back:
```
/usr/bin/python3 check_scheduled.py --expect N
```
It must print `RESULT: OK`. If it prints FAIL, the run is not done.

## Recovery: the read-back count-mismatch trap
`verify_scheduled` compares the folder size to the plan. If the Scheduled folder already held messages it FAILS with `folder holds X, expected Y, extra=[...]`, and it returns BEFORE saving `state.json`. That leaves the just-scheduled messages in the folder but UNTRACKED, so a re-run would stage them again.
Recover from the FOLDER, never from `state.json`:
1. Read the folder, map recipients to domains.
2. Remove the scheduled-only entries for those domains from `state.json` (keep any with `sent_at`; those were truly mailed).
3. Empty the Scheduled folder (mark `\Deleted`, expunge).
4. Re-run the one command from a clean folder.
Back up `state.json` first; `schedule_drafts.py` already writes a `.bak-sched-*` on every run.

## Reading the mailbox over IMAP (search, find a thread, read a reply)

`set -a; source ~/.config/phantombyte/mailer.env; set +a` first; that file holds `PHANTOMBYTE_SMTP_PASS`. Connect to `imap.ionos.com:993` and log in as `hello@phantom-byte.com`. `harvest_bounces.connect()` already does exactly this, so importing it is the shortest path.

Folder names are not the obvious ones, and a wrong name fails as zero results rather than as an error. The account has exactly: `Archive`, `Archive/2026`, `Drafts`, `INBOX`, `Scheduled`, `Sent Items`, `Spam`, `Trash`. There is NO `Sent` folder; outbound webmail mail lives in `Sent Items`. Selecting a folder that does not exist returns SELECT FAILED, and a search that ignores that status reports "no messages match", which reads as "it was never sent" when it was.

**Select a folder whose name contains a space with IMAP quoting around the whole name:** `M.select('"Sent Items"', readonly=True)`. Passing the bare string raises `imaplib.IMAP4.error: EXAMINE command error: BAD [b'expected end of data instead of " Items"']` — the server reads the space as the end of the mailbox argument.

**Do not derive the folder list with a regex over `M.list()`.** `M.list()[1]` returns lines like `b'(\\HasNoChildren) "/" INBOX'`, where only names containing a space are quoted as `"/" "Sent Items"`. A pattern that grabs the last quoted token therefore matches exactly one folder and silently narrows the scan to it, which reads as "no other mail exists" rather than as a parse failure. Either iterate the eight known names above and check the SELECT status for each, or take the final whitespace token and strip surrounding quotes.

**Search a person by the root of the name, not the spelling given.** The requester's spelling is often wrong: a request for "Tracy" matches `tracey.washburn@...` only when you search the stem `trac`. And match that stem against the `From` header alone. Matching the stem against From, To, Cc and Subject together returns every mail to `*contracting.com`, `*traction*`, and similar, burying the one thread you want under hundreds of hits a day of outreach.

A message sent through SMTP by script is not copied into `Sent Items` at all, so that folder can never prove or disprove a scripted send. The delivered copy in the recipient's INBOX is the evidence.

To find the thread with an address, do not search one folder. Loop the folders above, `UID FETCH (RFC822)` each message, and match the lowercased `From` plus `To` plus `Cc` headers against the address, then print date, direction, subject and body. That pulls the original outbound pitch and the reply in one pass instead of one email at a time.

Interpreter: `python3` on PATH is not always the one holding the dependencies, and it is not the same one in an interactive shell, in cron, and in a wrapper script. `/usr/bin/python3` has `requests` and imports every module in the scheduling chain; scrapling-based page fetches run under `~/.venv/bin/python3`. Use the explicit path in every command, every script, and every cron wrapper rather than discovering the gap mid-run — a `ModuleNotFoundError` at import means nothing was staged and the day is lost.

## Free domain report (the findings sheet) for a prospect or partner

Two scripts in `~/money_ideas`, run in this order. Never hand-write record values; every line of the sheet must trace to a measurement taken the same day.

1. `/usr/bin/python3 email_scan.py <domain> --csv <scratch>/scan.csv` reads public DNS over DoH and grades MX, SPF, DKIM across common selectors, and DMARC, with severity, defect codes and the enforcement verdict.
2. `source ~/.config/phantombyte/mailer.env; /usr/bin/python3 findings_sheet.py --csv <scratch>/scan.csv --domain <domain> --offer-url https://phantom-byte.com/email-deliverability-rescue` renders the client-facing findings sheet from that CSV row, in plain language, defect by defect.

The sheet's stock close quotes the direct one-domain price of $500. When the audience is an agency partner rather than an end client, replace that section with the two partner arrangements: white label at $250 per domain implemented and billed onward under the agency's own brand at whatever price it sets, or referral at $500 billed to the client with $150 back to the agency. Say plainly that every domain gets the free sheet first, at no cost and no obligation.

Keep the sheet's honesty footer: DNS records alone cannot measure placement, and the Gmail and Microsoft enforcement threshold is 5,000 or more messages a day to their consumer addresses. Do not promise inbox placement.

A partner meeting package is the report plus a bulleted sheet of the deal, the feature list, the agency-side margin math, the objection answers, and the honesty limits. Send both as attachments in one email rather than as separate mails.

## Hard rules (from the workflow)
- This only QUEUES send times. Never automate the actual send; Vinny reviews.
- Every message carries the CAN-SPAM postal address and the opt-out; `outreach.py` refuses without them.
- A 4xx, a timeout, or a refused connection is never death. UNKNOWN is allowed to send. Only a permanent 5xx or a DNS fact (null MX, NXDOMAIN) kills an address.
- Never touch SPF/DKIM/DMARC/MX as part of scheduling. The SendGrid and MailerLite records stay.
- The circuit breaker (5% hard bounce over the last 72h, 20-send floor) refuses both a direct `--send` and a schedule when recent bounces are high. `--no-bounce-guard` overrides; use it only deliberately.
- Run every script inside WSL. Files must be LF.
- Proof is a FRESH run with the output read, never a remembered count.

## Files
- `schedule_drafts.py` - the scheduler (this command).
- `outreach.py` - the gate chain, render, compose.
- `mail_verify.py` - the RCPT mailbox probe (Windows bridge).
- `prospect_fit.py` - the buyer-fit filter.
- `harvest_bounces.py` - DSN + unsubscribe harvest (Inbox + Spam).
- `clean_prospects.py` - cleans the pool into `prospects_daily_clean.csv` (role rule + fit + dedupe).
- `check_scheduled.py` - the independent read-back.
- `build_lead_groups.py`, `build_clicker_groups.py` - refresh `leads/`.
- Cron wrapper: `~/.hermes/scripts/daily_outreach_refill.sh`.
- Pool input: `scan_master.csv` + `contacts_master.csv` (master), or `scan_2000_b4_results.csv` + `contacts_2000_b4_final.csv` (batch).
