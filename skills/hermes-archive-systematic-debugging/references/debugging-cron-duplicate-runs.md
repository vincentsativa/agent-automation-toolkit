# Debugging Duplicate Cron Job Runs

## Symptom

A cron job scheduled for `0 8 * * *` (8am daily) fires twice on the same day, once at 8am, once in the afternoon (~3:30pm). The second run is NOT scheduled in the job's `schedule` field, it's a ghost fire.

## Evidence Pattern (June 2026, Job 0c6b83ba6986)

Output files from `~/.hermes/cron/output/{job_id}/`:

```
2026-06-06_08-03-52.md   ← scheduled 8am run
2026-06-06_14-10-39.md   ← duplicate, unscheduled
2026-06-11_08-05-27.md   ← scheduled 8am run
2026-06-11_15-24-39.md   ← duplicate, unscheduled
```

Same gap pattern on two different days. The `last_run_at` and `next_run_at` in jobs.json confirm the job ran and was marked ok both times.

## Root Cause

### The Lock Architecture (the problem)

`tick()` in `cron/scheduler.py` uses `fcntl.flock()` on a file as its cross-process lock. But **inside a single process**, two threads can hold the same flock independently, each has its own file descriptor, and the OS grants them independently.

The race:

1. **Ticker thread (gateway):** calls `tick()` → gets the file lock → calls `get_due_jobs()` → finds job due → calls `advance_next_run()` (bumps `next_run_at` forward) → submits job to `_process_job` via thread pool → releases file lock
2. **Pool thread:** runs `_process_job` → calls `run_job()` → calls `mark_job_run()` at completion → opens the same lock file with a NEW fd → can acquire the lock independently
3. **Meanwhile:** If the ticker thread fires again (60s later, next tick cycle) while the pool thread is still processing the job but `mark_job_run` hasn't written `next_run_at` yet... the job record still shows the old `next_run_at` or a stale value because the in-flight guard (`_running_job_ids` set) is the ONLY defense, and it depends on the pool thread still running

BUT the actual bug pattern here doesn't match a simple race on the same tick cycle. The duplicate fires 6-7 hours after the scheduled run. This means:

### The Real Sequence

1. 8am: job fires, `advance_next_run()` pushes `next_run_at` from "2026-06-11T08:00" to "2026-06-12T08:00"
2. Job runs in pool thread (takes a while, tens of minutes because it's an LLM agent task)
3. `mark_job_run()` completes, writes `next_run_at = "2026-06-12T08:00"` 
4. **Later:** Gateway restarted or process experienced some state reset
5. The running-set (`_running_job_ids`) was a set in memory, it dies with the process
6. After restart, `_get_due_jobs()` runs. It checks `next_run_at <= now`. But something caused it to see the job as due again

**Most likely path:** The job's `next_run_at` was advanced to the next day's 8am correctly. But on process restart, some state recovery or tick timing glitch caused `get_due_jobs()` to recompute the schedule differently, landing on an earlier time.

### Why 3:30pm specifically?

The duplicate runs happened at 14:10 and 15:24 on two different days, different times, not a fixed offset from 8am. This rules out a constant timezone shift or a second crontab expression. More likely: the previous day's long-running job completed around that time, and `mark_job_run`'s `compute_next_run()` call recomputed `next_run_at` relative to `last_run_at` (the completion time) instead of the desired base.

In `compute_next_run()` in `jobs.py`:

```python
if last_run_at:
    base_time = _ensure_aware(datetime.fromisoformat(last_run_at))
cron = croniter(schedule["expr"], base_time)
next_run = cron.get_next(datetime)
```

If the job completed at ~14:10 (say, 6+ hour run), `compute_next_run(schedule, "2026-06-06T14:10:00")` would compute the *next* occurrence of `0 8 * * *` after 14:10, which is **tomorrow at 8am**, correct. So the next_run_at AFTER mark_job_run should be fine.

**The true culprit:** The `advance_next_run()` call in `tick()` line 2017 runs BEFORE `mark_job_run()`. It bumps next_run_at forward using `compute_next_run(schedule, now)` where `now` is the current time during tick. Then `mark_job_run()` runs later with `compute_next_run(schedule, last_run_at)` where `last_run_at` is the completion time. If these two calls disagree on which is the "real" next run, and the job record's `next_run_at` is read by a subsequent tick before `mark_job_run` writes its value... the job could be considered due again.

**Short version:** Two write paths to `next_run_at` (advance_next_run → before run, mark_job_run → after run) without proper mutual exclusion in the same process because `fcntl.flock` doesn't guard intra-process threads.

## Proper Fix

### Option A: Threading RLock Sandwich

Wrap the tick + job processing in an `threading.RLock()` so in-process concurrency is gated by the RLock, and cross-process concurrency by fcntl:

```python
# At module level
_tick_rlock = threading.RLock()

def tick(...):
    with _tick_rlock:
        # existing fcntl lock + body
```

### Option B: `running_at` Timestamp on Job Record

Add a `running_at` field that `tick()` stamps when it picks up a job. Before firing, check: does the job have a `running_at` that's less than 30 minutes old? If yes, skip. `mark_job_run` clears it on completion.

### Option C: Combine Both

RLock for the tick body + `running_at` field as defense-in-depth. The RLock prevents the race; `running_at` covers process restart edge cases where the in-memory `_running_job_ids` set is lost.

## Investigation Commands

```bash
# Check output files for duplicate timestamps
ls -la ~/.hermes/cron/output/{job_id}/

# Read job record
cat ~/.hermes/cron/jobs.json | python3 -c "import sys,json; j=json.load(sys.stdin); [print(f\"{j['id']}: last={j.get('last_run_at')} next={j.get('next_run_at')} status={j.get('last_status')}\") for j in j.get('jobs',[]) if j['id']=='0c6b83ba6986']"

# Check if gateway process restarted around the duplicate time
grep -i "restart\|start\|cron ticker started\|shutdown" ~/.hermes/logs/gateway.log | tail -20

# Check tick timing
grep -i "tick\|job.*due\|job.*run" ~/.hermes/logs/gateway.log | tail -20
```