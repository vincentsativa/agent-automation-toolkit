# Scheduled jobs

`hermes-cron-jobs.json` is the live cron table of the WSL Hermes agent, exported with
credentials, chat IDs and delivery targets removed. All 34 jobs that were scheduled at
export time are here, including the one that is currently disabled.

Each entry:

```json
{
  "name": "hermes-weekly-backup",
  "schedule": "0 3 * * 0,1,2,3,4,5,6",
  "schedule_display": "0 3 * * 0,1,2,3,4,5,6",
  "enabled": true,
  "runner": "deterministic-script",
  "no_agent": true,
  "script": "hermes-backup.sh",
  "model": "deepseek-v4.1-flash:1017-cloud",
  "provider": "ollama-com",
  "skills": [],
  "deliver": "telegram",
  "instructions": null
}
```

| Field | Meaning |
| --- | --- |
| `schedule` | Standard five-field cron expression |
| `enabled` | Whether the job is live in the scheduler |
| `runner` | `deterministic-script` when `no_agent` is true; otherwise `agent-prompt` |
| `no_agent` | True means the script runs with no model call at all |
| `script` | Script name. On a `no_agent` job it is the whole job; on an `agent-prompt` job it is a gate that runs first and states the verdict in its output. Files live in `scripts/hermes/` |
| `model` / `provider` | Bound at job level, so a model change elsewhere does not silently change scheduled behaviour |
| `skills` | Skills the job preloads into the session |
| `deliver` | Delivery channel; every job here delivers to `telegram` |
| `instructions` | The full prompt, including the delivery rule and the failure behaviour |

Twelve jobs are `no_agent`, twenty-two run a model, and six of those twenty-two run a gate
script before the model sees anything.

## The jobs

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `30 AI NEWS STORIES DEDUP DAILY DATA FILE` | `0 16 * * *` | agent | EXCLUDING the stories included in the following data files, Fetch me today's top What are today's... |
| `8AM TENSORFEED REPORT` | `0 8 * * *` | agent | Run me a tensorfeed report of todays ai headlines INCLUDING a 5 sentence summary of the details of... |
| `BLOGWATCHER REPORT 30+` | `1 15 * * *` | agent | Run me an BLOGWATCHER but also include five themes worth writing about you find in the data that... |
| `BRUSH FEFE'S TEETH` | `30 10 * * *` | agent | This is a daily reminder that MUST be sent every single morning. Output the following message, do... |
| `CLICK HARVEST` | `0 20 * * *` | script | `harvest_clicks.sh` alone, no model call |
| `Check For the latest Ollama version` | `0 21 * * *` | agent | Go to GitHub and find me the latest stable Ollama version and the latest pre-release versions and... |
| `Check scrapling and rotunda` | `0 21 * * 5` | agent | Check and update Scrapling and Rotunda for both you (WSL HERMES AGENT) and my Windows Hermes agent.... |
| `DAILY OUTREACH REFILL` | `0 0 * * 1-5` | agent | `daily_outreach_refill.sh` gate, then the instruction |
| `DAILY Pinterest Posts 5:45PM` | `45 17 * * *` | agent | `pinterest_dedup.py` gate, then the instruction |
| `Daily Data Files Backup` | `30 3 * * *` | script | `daily-data-backup.sh` alone, no model call |
| `Delete Daily Data Files` | `30 3 * * *` | agent | Go to the following folder on my desktop located at C:\Users\<user>\OneDrive\Desktop\TODAYS DATA... |
| `EMAIL TASK PROCESSOR (Frank/15min)` | `*/15 * * * *` | agent | `check_agentmail.py` gate, then the instruction |
| `Hermes Update Health Check` | `0 2 * * *` | script | `update_health_check.py` alone, no model call |
| `INSTABOX POOL HARVEST` | `0 20 * * *` | script | `pool_harvest_instabox.sh` alone, no model call |
| `IronPulse 11am` | `0 11 * * *` | agent | Run the IronPulse full report following the ironpulse skill. You MUST deliver EXACTLY 30 AI-related... |
| `MONEY MAKING IDEAS TO USE INSTABOX.SH` | `0 18 * * *` | agent | Find 7 Small Business Opportunities Using Instabox.sh Objective I want to identify practical,... |
| `Ollama version check AM edition` | `0 9 * * *` | agent | Go to GitHub and find me the latest stable Ollama version and the latest pre-release versions and... |
| `PARTNER DIRECTORY REFILL` | `0 4,7 * * *` | script | `partner_directory_refill.sh` alone, no model call |
| `PARTNER OUTREACH REFILL` | `30 9 * * 1-5` | script | `partner_refill.sh` alone, no model call |
| `PRLog.org FREE press release - MONTHLY` | `31 16 7 * *` | agent | Below are all the press releases I've done so far since February, and it's time to do a new one. I... |
| `PROSPECT POOL REFILL` | `0 21 * * 0-4` | agent | `refill_check.sh` gate, then the instruction |
| `PRUNE STALE PINTEREST POSTS` | `0 4 * * *` | script | `pinterest_prune.py` alone, no model call |
| `Pinterest Email Backstop` | `55 17 * * *` | script | `send_pinterest_email.py` alone, no model call |
| `REMINDER ONLY - UPLOAD PRESS RELEASE - MONTHLY` | `1 18 7 * *` | agent | This is a REMINDER ONLY, not a task. Write this EXACTLY: "Don't forget to upload the press release... |
| `SOCIAL MEDIA QUESTIONS - 5PM` | `50 16 * * *` | agent | Go look at the following data files, (Data file: C:\Users\<user>\OneDrive\Desktop\TODAYS DATA... |
| `Social Media Questions Email Backstop` | `0 17 * * *` | script | `send_social_email.py` alone, no model call |
| `TUTORIAL IDEAS USING THE DATA` | `0 22 * * *` | agent | HARD RULE: Do not skip, reorder, or invent substitutes for any delivery step (Steps 5–8). File... |
| `Three Outlines For Articles` | `45 16 * * *` | agent | Task: Research phantom-byte.com's existing content, then generate three fact-based article outlines... |
| `WEEKDAY VERIFIER PREFILL` | `0 10 * * 1-5` | script | `weekday_verifier_prefill.sh` alone, no model call |
| `WEEKEND VERIFIER PREFILL` | `0 10 * * 0,6` | script | `weekend_verifier_prefill.sh` alone, no model call |
| `WEEKLY AI NEWS STORIES` | `30 14 * * 0` | agent | Here's a clearer, more structured version of your instructions that removes ambiguity and gives... |
| `Weekly Agent Change Briefs` **(disabled)** | `0 5 * * 0,2,4,6` | agent | `agent-change-brief-collect.sh` gate, then the instruction |
| `hermes-weekly-backup` | `0 3 * * 0,1,2,3,4,5,6` | script | `hermes-backup.sh` alone, no model call |
| `x-algorithm repo update watcher` | `15 8 * * 0,3,6` | agent | `x-algorithm-update-check.sh` gate, then the instruction |
