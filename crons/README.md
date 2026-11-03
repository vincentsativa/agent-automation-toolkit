# Scheduled jobs

`hermes-cron-jobs.json` is the live cron table of the WSL Hermes agent, exported
with credentials, chat IDs and delivery targets removed. It covers all 34 jobs
that were active at export time, including the disabled ones.

Each entry:

```json
{
  "name": "hermes-weekly-backup",
  "schedule": "0 3 * * 0,1,2,3,4,5,6",
  "schedule_display": "0 3 * * 0,1,2,3,4,5,6",
  "enabled": true,
  "runner": "deterministic-script",
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
| `runner` | `deterministic-script` runs `script` with no model; `agent-prompt` runs `instructions` in an agent session |
| `script` | Script name for deterministic jobs — the file lives in `scripts/hermes/` |
| `model` / `provider` | Bound at job level, so a model change elsewhere does not silently change scheduled behaviour |
| `skills` | Skills the job preloads into the session |
| `deliver` | Delivery channel; all jobs here deliver to `telegram` |
| `instructions` | The full prompt, including the delivery rule and the failure behaviour |

## The jobs

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `30 AI NEWS STORIES DEDUP DAILY DATA FILE` | `0 16 * * *` | agent-prompt | EXCLUDING the stories included in the following data files, Fetch me today's top What are today's top 30… |
| `8AM TENSORFEED REPORT` | `0 8 * * *` | agent-prompt | Run me a tensorfeed report of todays ai headlines INCLUDING a 5 sentence summary of the details of each… |
| `BLOGWATCHER REPORT 30+` | `1 15 * * *` | agent-prompt | Run me an BLOGWATCHER but also include five themes worth writing about you find in the data that haven't… |
| `BRUSH FEFE'S TEETH` | `30 10 * * *` | agent-prompt | This is a daily reminder that MUST be sent every single morning. Output the following message — do not say… |
| `CLICK HARVEST` | `0 20 * * *` | deterministic-script | `harvest_clicks.sh` |
| `Check For the latest Ollama version` | `0 21 * * *` | agent-prompt | Go to GitHub and find me the latest stable Ollama version and the latest pre-release versions and give me a… |
| `Check scrapling and rotunda` | `0 21 * * 5` | agent-prompt | Check and update Scrapling and Rotunda for both you (WSL HERMES AGENT) and my Windows Hermes agent. I also… |
| `DAILY OUTREACH REFILL` | `0 0 * * 1-5` | deterministic-script | `daily_outreach_refill.sh` |
| `DAILY Pinterest Posts 5:45PM` | `45 17 * * *` | deterministic-script | `pinterest_dedup.py` |
| `Daily Data Files Backup` | `30 3 * * *` | deterministic-script | `daily-data-backup.sh` |
| `Delete Daily Data Files` | `30 3 * * *` | agent-prompt | Go to the following folder on my desktop located at C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES and… |
| `EMAIL TASK PROCESSOR (Frank/15min)` | `*/15 * * * *` | deterministic-script | `check_agentmail.py` |
| `Hermes Update Health Check` | `0 2 * * *` | deterministic-script | `update_health_check.py` |
| `INSTABOX POOL HARVEST` | `0 20 * * *` | deterministic-script | `pool_harvest_instabox.sh` |
| `IronPulse 11am` | `0 11 * * *` | agent-prompt | Run the IronPulse full report following the ironpulse skill. You MUST deliver EXACTLY 30 AI-related stories… |
| `MONEY MAKING IDEAS TO USE INSTABOX.SH` | `0 18 * * *` | agent-prompt | Find 7 Small Business Opportunities Using Instabox.sh Objective I want to identify practical, profitable ways… |
| `Ollama version check AM edition` | `0 9 * * *` | agent-prompt | Go to GitHub and find me the latest stable Ollama version and the latest pre-release versions and give me a… |
| `PARTNER DIRECTORY REFILL` | `0 4,7 * * *` | deterministic-script | `partner_directory_refill.sh` |
| `PARTNER OUTREACH REFILL` | `30 9 * * 1-5` | deterministic-script | `partner_refill.sh` |
| `PRLog.org FREE press release - MONTHLY` | `31 16 7 * *` | agent-prompt | Below are all the press releases I've done so far since February, and it's time to do a new one. I want you… |
| `PROSPECT POOL REFILL` | `0 21 * * 0-4` | deterministic-script | `refill_check.sh` |
| `PRUNE STALE PINTEREST POSTS` | `0 4 * * *` | deterministic-script | `pinterest_prune.py` |
| `Pinterest Email Backstop` | `55 17 * * *` | deterministic-script | `send_pinterest_email.py` |
| `REMINDER ONLY - UPLOAD PRESS RELEASE - MONTHLY` | `1 18 7 * *` | agent-prompt | This is a REMINDER ONLY, not a task. Write this EXACTLY: "Don't forget to upload the press release to PRLog.… |
| `SOCIAL MEDIA QUESTIONS - 5PM` | `50 16 * * *` | agent-prompt | Go look at the following data files, (Data file: C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES) THEN… |
| `Social Media Questions Email Backstop` | `0 17 * * *` | deterministic-script | `send_social_email.py` |
| `TUTORIAL IDEAS USING THE DATA` | `0 22 * * *` | agent-prompt | HARD RULE: Do not skip, reorder, or invent substitutes for any delivery step (Steps 5–8). File save, email… |
| `Three Outlines For Articles` | `45 16 * * *` | agent-prompt | Task: Research phantom-byte.com's existing content, then generate three fact-based article outlines from a… |
| `WEEKDAY VERIFIER PREFILL` | `0 10 * * 1-5` | deterministic-script | `weekday_verifier_prefill.sh` |
| `WEEKEND VERIFIER PREFILL` | `0 10 * * 0,6` | deterministic-script | `weekend_verifier_prefill.sh` |
| `WEEKLY AI NEWS STORIES` | `30 14 * * 0` | agent-prompt | Here's a clearer, more structured version of your instructions that removes ambiguity and gives your AI agent… |
| `Weekly Agent Change Briefs` **(disabled)** | `0 5 * * 0,2,4,6` | deterministic-script | `agent-change-brief-collect.sh` |
| `hermes-weekly-backup` | `0 3 * * 0,1,2,3,4,5,6` | deterministic-script | `hermes-backup.sh` |
| `x-algorithm repo update watcher` | `15 8 * * 0,3,6` | deterministic-script | `x-algorithm-update-check.sh` |
