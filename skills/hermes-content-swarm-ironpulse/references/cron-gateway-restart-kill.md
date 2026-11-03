# Cron Jobs Killed by Gateway Restart — Log Evidence

## Why This Reference Exists

Two consecutive days (May 5 and May 6, 2026) an IronPulse cron job was correctly scheduled at 14:00 EDT but never delivered output. Both times the cron ticker DID fire the job — the agent started working — but a gateway restart mid-execution killed the process.

## Evidence: May 6, 2026 Log Excerpts

```
2026-05-06 12:21:45 INFO gateway.run: Cron ticker started (interval=60s)
# ... ticker running ...
2026-05-06 14:00:42 INFO agent.auxiliary_client: Vision auto-detect: using main provider ollama-com (deepseek-v4-flash)
2026-05-06 14:00:43 INFO agent.auxiliary_client: Auxiliary auto-detect: using main provider custom (deepseek-v4-flash)
# JOB STARTED — agent initialized for cron worker
2026-05-06 14:10:12 INFO [cron_f1c48b92da1a_20260506_140042] agent.auxiliary_client: Auxiliary auto-detect: using main provider ollama-com (deepseek-v4-flash)
# Agent was actively working 10 minutes later
# NO completion log, NO file written
# Next log shows user message at 14:17 — by then the process was dead
```

## How to Detect This

1. `cronjob(action="list")` — `last_run_at: null`, `last_status: null` despite being scheduled
2. Check agent.log: `grep "cron_f1c48b92da1a" ~/.hermes/logs/agent.log` — process prefix exists but trails off
3. Output directory is empty for that date: `ls ~/.hermes/workspace/ironpulse-outputs/ironpulse-2026-05-06.txt` — not found
4. Desktop copy absent: `ls "/mnt/c/Users/<user>/Desktop/ironpulse-2026-05-06.txt"` — not found

## Root Cause

The Hermes cron scheduler runs inside the same gateway process. Any gateway restart — model switch, config update, WSL sleep/wake — kills all in-flight cron worker processes. Restart frequency is high during normal interactive use.

## What Actually Works

- Interactive session jobs (user is talking, process stays alive)
- External scheduling: systemd timer that runs `hermes task ...` as a separate process
- NOT the built-in cron system for time-sensitive delivery
