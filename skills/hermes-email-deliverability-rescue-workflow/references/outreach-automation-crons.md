# The outreach automation: crons, the master pool, and the daily run

Vinny built the daily data side as scripts wrapped in two Hermes cron jobs. Read this before touching, quoting, or reporting on the automated run. The scripts are the authority; anything prose says about a count or a default is a claim to re-check.

## The jobs (state as of 2026-10-13)

| Job | Script | Schedule | Stages |
|---|---|---|---|
| `PARTNER DIRECTORY REFILL` | `partner_directory_refill.sh` | `0 19 * * 0-4` | nothing; grows the agency pool |
| `DAILY OUTREACH REFILL` | `daily_outreach_refill.sh` | `0 0 * * 1-5` (00:00, same-day) | buyer, `LIMIT=30`, `GAP=6` |
| `PARTNER OUTREACH REFILL` | `partner_refill.sh` | `30 9 * * 1-5` | agency, `LIMIT=50`, `GAP=4` |
| `WEEKDAY VERIFIER PREFILL` | `weekday_verifier_prefill.sh` | `0 10 * * 1-5` | nothing; `LIMIT=40` |
| `WEEKEND VERIFIER PREFILL` | `weekend_verifier_prefill.sh` | `0 10 * * 0,6` | nothing; `LIMIT=60` Sat / `40` Sun |
| `PROSPECT POOL REFILL` | `refill_check.sh` | `0 21 * * 0-4` | nothing; gates on `REFILL_AT=100` |

- **`DAILY OUTREACH REFILL`** - workdir `~/money_ideas`, runs 00:00 Mon-Fri and stages the SAME day's 09:00 send (see the 2026-10-13 note below). One pass: clean the sendable list from the master pool, optionally refill when the pool cannot cover the run, stage the day's sends into the IONOS Scheduled folder through `schedule_drafts.py`, verify with the independent read-back (`check_scheduled.py --expect N`), then print a short summary that the cron's report repeats in a few lines.
- **`PROSPECT POOL REFILL`** - cheap and deterministic on purpose: rebuild the clean list, print `POOL HEALTHY` or `REFILL NEEDED` against `REFILL_AT`, and only on `NEEDED` does the `prospect-refill` skill run the heavy source, scan, harvest, clean sequence. The heavy half needs the Windows side, which is not always on, so the check and the work are deliberately separate jobs.
- **`WEEKDAY` / `WEEKEND VERIFIER PREFILL`** - spend the hosted verifier's free 100/day tier on the pool ahead of a staging run. They send nothing. They are not optional: the staging run holds out every address it cannot prove, and the local RCPT probe cannot reach IPv4-only MX hosts. **The 100/day tier is shared with the partner run**, which is why the weekday prefill was cut to 40 - the partner job at 09:30 must be able to spend calls first.
- **`PARTNER OUTREACH REFILL`** - the agency/MSP channel, a separate list and a separate state file (`partner_state.json`). Stages a same-day 13:00 send, so partner and buyer mail never sit in the Scheduled folder at the same time.

### The 2026-10-11 re-prioritisation (Vinny)

The channel mix was deliberately rebalanced: **buyer 100 -> 30/day, agency 30 -> 50/day.**
The evidence was a reply from `dominique@temerarii.com` to the agency pitch - the
first real human reply in the mailbox - against roughly 700 buyer sends and zero
replies. It is a throttle, not a pause: the buyer side still runs every weekday,
which keeps `hello@phantom-byte.com` sending daily and keeps the scanned-domain
dataset growing. See `hermes-outreach-cron` (Windows side) and
`partner-referral-channel.md` for the sourcing consequence, which is the part
that actually binds: OSM yields only about 7.6 usable agency addresses per metro.

- **`PARTNER DIRECTORY REFILL`** (`be4516e1f17a`, `0 19 * * 0-4`, `--no-agent`) - the one that GROWS the partner pool, added 2026-10-11 when OSM turned out to be exhausted for the agency segment (~7.6 usable addresses per metro, so the whole 55-metro OSM queue is ~8 send-days at 50/day). Reads agency directories instead - they exist to list agencies and publish each agency's own website - via `directory_prospects.py`: `topdevelopers.co` (10,836 agency profiles) and `superbcompanies.com` (77,931), both measured at 40/40 correct domain extraction on their first twenty profiles. Chain inside `partner_directory_refill.sh`: scrape -> `directory_pool_todo.py` (what is genuinely new) -> `email_scan.py` -> `harvest.sh` (4 workers) -> append to the two master files -> print the eligible count. **Never sends and never stages.** It runs at 19:00, two hours before the pool refill, so the two heavy jobs cannot overlap.

## Rules that keep the automated run honest

- **Read the knobs out of the script, never out of prose.** `LIMIT`, `START`, `GAP`, `BATCH`, `REFILL`, `DRY`, `POOL`, and `REFILL_AT` are env vars assigned at the top with `:-` defaults, and Vinny raises them as the ramp moves. The header comment above the code rots first: it still described 20 where the assignment said 100. Quote the assignment, and when the comment and the code disagree, the code wins and the comment is the thing to fix.
- **The master pool is `contacts_master.csv` + `scan_master.csv`, and it is the spine.** Every fresh batch is appended into those two files and the sendable list is re-derived from the union by `clean_prospects.py`. That is why no batch has to be tracked separately and why two batches are never summed by hand: the dedupe on domain AND address is the union.
- **The cleaner's output file is a count, not always the input.** A wrapper may build the clean file only to size the pool, then stage from the raw pool and let the full gate chain re-run inside `schedule_drafts.py`. That is safe because the gates run again on the send path, but never read a fresh clean file as proof of what was staged: verify against the staging read-back.
- **A cron that stages is not a cron that sends.** These jobs queue real send times into the Scheduled folder. The standing rule against fully automating the send, and the reply cadence, stay Vinny's to lift, and a cron report is a status rather than permission.
- **Still owed: reply handling.** The scheduling half is built; the piece remaining is what happens when a reply lands. Never bake an assumption about it into a script.
- **A zero-token script job is how the cheap half should stay.** The pool-health check does arithmetic and prints one line, so it needs no model; keep new deterministic steps in shell and leave the model for the report.

## Who maintains it

Vinny's split, stated plainly: **Pi maintains the code, this side runs and proves it.** Pi is on the Windows side and reaches the same files. A targeted change to copy, a rule, or a constant is made here in one pass; a structural defect in how a script walks a list, reads a page, or parses a record goes back to Pi. Because both agents edit these files, read the live script before editing or quoting it, every time: a remembered dict, default, or CSV column order describes a file that has probably moved since, and the live file beats both this reference and any brief handed over.

## Verifying an automated run

- Prove a run by reading it back, never by trusting the wrapper's own success line: the scheduler's read-back plus the folder read are what make "staged" a fact.
- After a copy or rule change that the cron consumes, exercise the real code path once (a dry run through the same script) rather than reading the diff, because the wrapper's own gates, not the unit test, decide what actually goes out.
- A failure inside one of these crons is a finding to report, not a reason to edit the job on your own initiative: name the script, the exit line, and what it blocks, then stop.

## 2026-10-13 - the buyer staging moved 01:30 -> 00:00 (same-day, unchanged)

Vinny reported that for two nights running the IONOS `Scheduled` folder was empty
when he looked at it ("nothing staged for tomorrow"), 2026-10-12 and 2026-10-13.

There was no sending failure. `Sent Items` shows the campaign sending every
weekday: 100 buyer on 2026-10-09, 30 buyer + 47 partner = 77 on 2026-10-12, and
the 2026-10-12 01:36 run staged 30 for 09:00 with the read-back `RESULT: OK`. The
pool is healthy (286 sendable) and the verifier key is alive (78 credits).

The cause was the **same-day staging window**. Since 2026-10-09 the daily job runs
at 01:30 and stages for *that same day's* 09:00 send, so the folder is empty from
about 12:00 (when the morning send finishes) until 01:30. Vinny checks the folder
at night, sees it empty, and reads that as "nothing staged". Before 2026-10-09 the
job staged for the *next* day, so tomorrow's batch was visible the evening before
- that is the behaviour he was used to.

Fix: the cron is now `0 0 * * 1-5` (00:00 Mon-Fri). Same-day staging is kept, but
00:00 is the earliest a same-day batch can be staged and still send that same
morning, so the queue is in place before he checks. 00:00 also still sits just
after the hosted verifier's daily reset, so the staging keeps first call on the
fresh 100/day tier (at 23:30 the day's partner run and prefill would have spent
it). The read-back is untouched: the folder is still empty at staging time, so the
whole-folder count stays honest. 2026-10-13's batch was staged by hand during the
transition so no send day was lost.

