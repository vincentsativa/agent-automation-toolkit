# Delegate Task Overload, Cron Job Hangs Without Delivery

## Symptom

A cron job fires (confirmed in agent.log) but never delivers to the user. No "delivered to telegram" entry. No output file in `~/.hermes/cron/output/<job_id>/`. The job's process is gone (no `ps aux` match) but no completion signal was recorded.

## Root Cause

The cron job's agent called `delegate_task` with more tasks than `max_concurrent_children` (default: 3). The tool returned an error:

```
Tool delegate_task returned error: Too many tasks: 6 provided, but max_concurrent_children is 3.
```

The agent then tried to recover by spawning individual subagents in a loop. Each subagent spawn took ~10+ seconds. The cron job's total runtime exceeded the scheduler's timeout (or the agent's internal timeout), and the job was killed mid-execution without ever reaching a delivery point.

## Reproduction (June 17, 2026)

- Job: "20 AI NEWS STORIES DEDUP DAILY DATA FILE" (job_id: 237b5d3ba110)
- Fired at: 16:00:43
- delegate_task error at: 16:01:50 (6 tasks, max 3)
- Recovery attempts: spawned 3 subagents starting at 16:01:55
- Last log entry: 16:13:02 (subagent init still in progress)
- No delivery recorded
- No output file for 2026-06-17
- Process was gone by 16:11 when checked

## Prevention

1. **In the cron prompt:** If the job needs to process multiple items in parallel, limit to 3 tasks per `delegate_task` call. Use sequential batches if more are needed.
2. **In the agent's prompt:** Explicitly tell the agent to avoid `delegate_task` with more than 3 tasks, or to use sequential processing instead.
3. **Scheduler-side:** Consider adding a per-job timeout that produces a delivery even on failure (e.g., "Job timed out after X minutes, partial results: ...").

## Detection

When a user asks "is job X running?" and the job appears to have missed:

1. Check agent.log FIRST: `grep <job_id> ~/.hermes/logs/agent.log | tail -20`
2. Look for `delegate_task returned error` with "Too many tasks"
3. Check if the last log entry shows subagent init without a subsequent delivery
4. If the pattern matches, the job was killed mid-flight, do NOT re-fire without fixing the prompt to limit delegate_task count
