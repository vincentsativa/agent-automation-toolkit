# Auditing a Cron Config Change Without Authorization

Use when a user reports a cron's output degraded AND asks whether the job config was modified without permission. Goal: pin down WHAT changed and WHEN, forensically, without touching the job.

## Core trap: the confirmation message hides the failure

Delivery-brief jobs (email-primary + short Telegram confirmation, e.g. "Social media questions are ready") deliver a final response that reveals nothing about the actual output. The only evidence of real output is the artifact the job wrote or emailed. Verify the artifact, not the notification.

## Diagnosis order

1. **Read the actual output artifact.** For job `50dcd9876b7b`, the run writes `~/todays_x_posts.txt` and emails it. Compare the file against what the prompt REQUIRES (per-post explanations, filename format, char limits). The concrete defect lives here.
2. **Diff the job's current prompt against `jobs.json.bak.*` snapshots.**

```python
import json, glob, difflib
cur = json.load(open('~/cron/jobs.json'))
curj = {j['id']: j for j in cur['jobs']}
tgt = curj['50dcd9876b7b']
for f in sorted(glob.glob('~/cron/jobs.json.bak*')):
    d = json.load(open(f))
    bj = {j['id']: j for j in d['jobs']}
    bt = bj.get('50dcd9876b7b')
    if not bt: continue
    diff = list(difflib.unified_diff(bt['prompt'].splitlines(), tgt['prompt'].splitlines(), lineterm=''))
    print(f, '---')
    for line in diff: print(line)
```

A block present in every run after date X but absent in the oldest backup dates the change to between backups.
3. **Check `~/.hermes/cron/usage_audit.jsonl`** for the `job_id` — tokens, model, duration per run. Confirms model-pinning history.
4. **Forensic `session_search`** for `cronjob(action="update")` with that `job_id` to find WHO changed the prompt and WHEN. If no session shows the user authorizing it, state that plainly.

## Rule
Do NOT touch the job until the change is accounted for. Do not silently patch or re-run. Report the diff, the date it appeared, and ask whether to restore. Re-running or editing an unconfirmed job repeats the violation.

## Worked case (Aug 23, 2026)
Job `50dcd9876b7b` (SOCIAL MEDIA QUESTIONS - 5PM). Output `todays_x_posts.txt` had none of the per-post "why it's good" explanations the prompt requires, plus a generic filename. The prompt had gained a `BRAND IDENTITY TO SHOWCASE` block + expanded algorithm rules + hard execution order, present from Aug 20 onward but absent in `jobs.json.bak.20260818_181717`. No session showed user authorization. Conclusion: prompt was rewritten between Aug 18 and Aug 20 without user instruction.
