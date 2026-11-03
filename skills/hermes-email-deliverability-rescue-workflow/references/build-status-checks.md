# Answering "is the prospect build still running?"

Vinny asks this mid-build, from Telegram, with no context carried over. Answer it from live state in one pass, then report only what the probes returned. Never answer from memory of the last build notice, and never from a report file in the folder, which may belong to a previous build.

## Probe order

1. **Processes.** `ps aux | grep -E "osm_industry|assemble_batch|scan_2000|contacts_2000" | grep -v grep`
   No match means no sourcing or scan stage is executing. Stages run as short-lived scripts, so a quiet process table means the pipeline has moved past them or finished.
2. **Cron execution record.** In `~/.hermes/cron/`, query `executions.db`:
   `select id, job_id, status, claimed_at, started_at, finished_at, delivery_outcome from executions order by rowid desc limit 10;`
   A row with `status='running'` names the job still holding the build. `suppressed` means the run produced `[SILENT]`; `delivered` means a report went out.
3. **Output mtimes.** `ls -lat ~/money_ideas/ | head -40` and `find ~/money_ideas -newermt "-30 minutes" -type f`.
   The newest mtime is when the build actually last wrote. Files written in the last few minutes mean it completed moments ago even if no notice has arrived.
4. **Counts from the artifacts, via python, not by eye.** Read the send-ready CSV with `csv.DictReader`, then report rows, unique emails, and unique domains as three separate numbers. A row count and a unique-email count differ when the harvest duplicates; report both.
5. **Distinct totals across builds** are a union over the previous `send_ready*_final.csv` files. Compute `len(set.union(*all_sets))` and also print the pairwise overlap with the newest prior batch. Report the union, and name the prior figure it corrects if one was quoted earlier.

## Duration is the probe for "this is taking longer than normal"

"Longer than normal" is a claim about a run's DURATION, and the durations are in `executions.db`, not in the process table. An idle check of a 15-minute job finishes in about a second; a run that does real work takes a couple of minutes. Rank the recent runs by duration and name the outlier by its own start time:

```python
import sqlite3, datetime
c = sqlite3.connect('~/cron/executions.db'); cur = c.cursor()
cur.execute("select claimed_at, finished_at, status, delivery_outcome from executions where job_id=? order by claimed_at desc limit 40", ('<job_id>',))
for cl, fi, st, do in cur.fetchall():
    d = (datetime.datetime.fromisoformat(fi) - datetime.datetime.fromisoformat(cl)).total_seconds() / 60
    print(f"{cl[:19]}  {d:8.1f} min  {st}  {do}")
```

A run measuring tens of minutes against a baseline of seconds IS the anomaly the question is about, and it is a single execution, not a stuck process: a finished row with a long span means the work happened and then ended.

Read `delivery_outcome` before interpreting silence on Telegram. `suppressed` means the run returned `[SILENT]` (nothing new to report); `delivered` means a report went out. An idle check is suppressed by design, so absence of a Telegram message is not evidence a task run failed to reach delivery.

## The run's own output file is the honest status

`~/.hermes/cron/output/<job_id>/<timestamp>.md` contains the run's full final `## Response`. When a long run ends without delivering, that section usually already names the steps it did not finish, in order. Read it and quote it rather than reconstructing the state of play from artifacts alone. A heavy run's artifacts can all be on disk and correct while the report email, the report file, and the completion notice were never produced, and only the `## Response` says which.

## What to report

- Whether the stage is running, finished, or waiting on the report-and-email step.
- The artifact counts, each labeled as the file it came from.
- The one thing Vinny has not been told yet: usually that the completion notice has not been sent, so nothing was missed.
- The remaining step by name, not as a promise. If the build finished but the report or email is outstanding, say exactly which.

## Pitfalls

- An execution recorded as `running` does not mean the scraping is still going. The same run writes the report and sends the mail after the artifacts land, so check the artifact mtimes before calling it in progress.
- A report file for an earlier build sitting in the same folder is not evidence about this build. Look for the current build's report file by its own name.
- Reusing an aggregate count from the last notice without re-deriving it propagates errors. Recompute from the CSVs.
- An inbound task email already marked `read` means it was picked up; use the message timestamps to establish which build an instruction belongs to rather than assuming it is still pending.

## 2026-10-05: enforcement reclassification, and the counts to expect

The Gmail/Microsoft gateway-rejection work landed as a separate commit. When a
brief or a session quotes test counts, these are the current ones (re-read them
from a fresh run, never quote from memory):

-  -> around 70 checks, 0 failures. It now also
  asserts the  mapping (SPF_MISSING/DMARC_MISSING = critical), that the
   field exists on every graded domain, and a synthetic
   case (SPF authorizes nobody + no DKIM + enforcing DMARC).
-  -> around 245 checks, 0 failures. It now asserts the
  gateway-rejection classifier, the sending-domain pre-flight, the volume
  buckets, and that the email names the change and carries no price.

New/moved files in : , ,
 (runtime, gitignored).  writes ,
, ;  buckets refusals and
never suppresses a gateway auth rejection;  /  /
 run a sending-domain pre-flight before a real send/stage.

## 2026-10-05: enforcement reclassification, and the counts to expect

The Gmail/Microsoft gateway-rejection work landed as a separate commit. When a
brief or a session quotes test counts, these are the current ones (re-read them
from a fresh run, never quote from memory):

- `python3 test_email_scan.py` -> around 70 checks, 0 failures. It now also
  asserts the severity mapping (SPF_MISSING/DMARC_MISSING = critical), that the
  alignment field exists on every graded domain, and a synthetic
  AUTH_ALIGNMENT_FAIL case (SPF authorizes nobody + no DKIM + enforcing DMARC).
- `python3 test_outreach.py` -> around 245 checks, 0 failures. It now asserts the
  gateway-rejection classifier, the sending-domain pre-flight, the volume
  buckets, and that the email names the change and carries no price.

New/moved files in ~/money_ideas/: auth_enforcement.py, domain_preflight.py,
auth_rejections.txt (runtime, gitignored). email_scan.py writes severity,
enforcement, alignment; harvest_bounces.harvest_full() buckets refusals and
never suppresses a gateway auth rejection; outreach.py / schedule_drafts.py /
stage_drafts.py run a sending-domain pre-flight before a real send/stage.
