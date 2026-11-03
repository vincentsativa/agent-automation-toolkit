# Diagnosing a Cron Job Whose Run Finished but the Ledger Says Failed

Use this when a job's report or deliverable arrived, but `last_status` is `error`, or the recorded error contradicts what the run actually did. The goal is to decide whether the work landed, and what actually failed.

## 1. Read the error string as a code path, not as a cause

The scheduler writes its error text from the code path that gave up. Several distinct failures share generic labels:

- `Interrupted by shutdown before terminal completion.` — written when a fire claim was lost (`_OWNERSHIP_LOST_INTERRUPTED`). No shutdown required.
- `Fire claim ownership lost; stale result was discarded.` — the run's result was dropped because another owner held the claim.
- `Interrupted by gateway shutdown before the run finished (tool subprocess was killed mid-flight).` — this one does involve a shutdown.

Confirm the cause from logs and process state before repeating the label to the user.

## 2. Establish whether the run completed

```bash
ls -la ~/.hermes/cron/output/<job_id>/ | tail -5
# read the latest file's "## Response" section
```

In `~/.hermes/logs/agent.log`, the cron session id is `cron_<job_id>_<timestamp>`. The turn's verdict line is authoritative:

```bash
grep "cron_<job_id>_" ~/.hermes/logs/agent.log | grep "Turn ended"
# reason=text_response(finish_reason=stop)  -> the agent finished its work
# reason=max_iterations_reached(N/N)        -> it ran out of budget (see Failure Mode #0)
```

The API-call count and latency profile also separate a healthy run (roughly 10-25 calls, a few seconds apart, diverse tools) from a looping one (calls pinned to a single tool at the iteration ceiling).

## 3. Query the two ledgers directly

```bash
python3 -c "
import sqlite3
c = sqlite3.connect('~/cron/executions.db'); c.row_factory = sqlite3.Row
print([d[0] for d in c.execute(\"select name from sqlite_master where type='table'\")])
for r in c.execute('select status,error,claimed_at,started_at,finished_at,delivery_outcome from executions where job_id=? order by rowid desc limit 5', ('<job_id>',)):
    print(dict(r))
"
```

`deliveries.db` holds `deliveries` and `delivery_tombstones`. A row present in `deliveries` proves the notice left the process; the tombstone (or its absence) says whether the run reached a terminal state.

Comparison table once you have both:

- `deliveries` says `delivered` + `executions` says `failed` — the user has the report and only the bookkeeping is wrong. Do not re-fire; find the scheduler bug.
- `deliveries` says `delivered` + `executions` says `completed` — the recorded error is stale metadata from an earlier attempt.
- no `deliveries` row + `executions` says `failed` — the work genuinely did not reach the user. Re-fire is appropriate after clearing the failure cause.
- no output file at all — the run never executed. Check `next_run_at` and the missed-run protocol.

## 4. Fire-claim contention: local fence versus file fence

The per-job fire fence is re-entrant and cross-process (`_fire_job_lock`). The error line names which layer timed out:

- `Timed out waiting for local fire fence <cron_dir>::<job_id>` — a thread lock inside one process. Self-contention: the job's own heartbeat is fighting the run's terminal phase. The heartbeat must never hold the fire fence while writing the jobs store.
- `Timed out waiting for fire fence <cron_dir>/.fire-<hash>.lock` — a competing process holds the file lock, usually a second gateway, a manual `cronjob(action='run')`, or a detached worker.

A 30-second wait is the acquisition timeout. When the wait is exhausted the code fails closed, so ownership loss is silent about which side was slow.

## 5. Deciding the repair

- Scheduler self-contention or ownership loss: fix or update the install. Never re-fire; the report already went to the user and a re-fire duplicates it.
- Genuine missed run: apply the recovery steps in SKILL.md only after confirming no output artifact and no delivery row exist for that occurrence.
- Repeated instances across unrelated jobs on different days are the signal that this is an install-level bug rather than one job's configuration.

## Pitfalls

- Do not treat a job's `last_error` as a factual description of what happened; it is a code path's summary.
- Do not re-fire to "fix" a failed ledger row on a run that delivered.
- Do not restart or update the gateway to apply a scheduler fix without first running the due-job check in SKILL.md; a restart during a queued fire vaporizes that run.
- A long gateway uptime that spans the failure timestamp rules out a shutdown as the cause in one step, before any deeper log reading.
