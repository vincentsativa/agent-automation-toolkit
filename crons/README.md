# Scheduled jobs

One job table per agent, exported with credentials and delivery targets removed. All four
tables use the same format.

| File | Agent | Jobs | `no_agent` |
| --- | --- | --- | --- |
| `hermes-cron-jobs.json` | WSL Hermes | 36 | 12 |
| `windows-hermes-cron-jobs.json` | Windows Hermes | 10 | 3 |
| `fifi-cron-jobs.json` | fifi profile (Windows) | 2 | 1 |
| `instabox-cron-jobs.json` | InstaBox Hermes (cloud VM) | 3 | 1 |

The WSL table is the live one; it documents the full field set. In the WSL table one job
is currently disabled and kept for reference (`Weekly Agent Change Briefs`). Six of the
Windows jobs are disabled the same way.

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
| `script` | Script name. On a `no_agent` job it is the whole job; on an `agent-prompt` job it is a gate that runs first and states the verdict in its output. Files live in `scripts/hermes/`, `scripts/windows-hermes/`, `scripts/instabox/` or `scripts/fifi/` |
| `model` / `provider` | Bound at job level, so a model change elsewhere does not silently change scheduled behaviour |
| `skills` | Skills the job preloads into the session |
| `deliver` | Delivery channel; every job here delivers to `telegram` |
| `instructions` | The full prompt, including the delivery rule and the failure behaviour |

Twelve of the WSL jobs are `no_agent`, twenty-four run a model, and seven of those run a
gate script before the model sees anything.

## The WSL jobs

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `30 AI NEWS STORIES DEDUP DAILY DATA FILE` | `0 16 * * *` | agent | Fetch today's AI news, dedup against prior reports, deliver as an emailed attachment |
| `8AM TENSORFEED REPORT` | `0 8 * * *` | agent | Tensorfeed AI headlines with themes and article ideas, emailed |
| `BLOGWATCHER REPORT 30+` | `1 15 * * *` | agent | Blogwatcher feed digest plus five article ideas, emailed |
| `BRUSH FEFE'S TEETH` | `30 10 * * *` | agent | The morning reminder, always speaks |
| `CLICK HARVEST` | `0 20 * * *` | script | `harvest_clicks.sh` alone, no model call |
| `Check For the latest Ollama version` | `0 21 * * *` | agent | Latest stable and pre-release Ollama versions with links |
| `Check scrapling and rotunda` | `0 21 * * 5` | agent | Weekly check and update for the scraping stack on both agents |
| `DAILY OUTREACH REFILL` | `0 0 * * 1-5` | agent | `daily_outreach_refill.sh` gate, then the instruction |
| `DAILY Pinterest Posts 5:45PM` | `45 17 * * *` | agent | `pinterest_dedup.py` gate, then the instruction |
| `Daily Data Files Backup` | `30 3 * * *` | script | `daily-data-backup.sh` alone, no model call |
| `Delete Daily Data Files` | `30 3 * * *` | agent | Clears the dated desktop data folder |
| `EMAIL TASK PROCESSOR (Frank/15min)` | `*/15 * * * *` | agent | `check_agentmail.py` gate, then the instruction |
| `Hermes Update Health Check` | `0 2 * * *` | script | `update_health_check.py` alone, no model call |
| `INSTABOX POOL HARVEST` | `0 20 * * *` | script | `pool_harvest_instabox.sh` alone, no model call |
| `IronPulse 11am` | `0 11 * * *` | agent | The 30-story IronPulse report, emailed as an attachment |
| `MONEY MAKING IDEAS TO USE INSTABOX.SH` | `0 18 * * *` | agent | Seven Instabox business opportunities |
| `Ollama version check AM edition` | `0 9 * * *` | agent | Morning Ollama version check |
| `PARTNER DIRECTORY REFILL` | `0 4,7 * * *` | script | `partner_directory_refill.sh` alone, no model call |
| `PARTNER OUTREACH REFILL` | `30 9 * * 1-5` | script | `partner_refill.sh` alone, no model call |
| `PINTEREST PERFORMANCE FEEDBACK LOOP` | `30 12 * * 0` | agent | Weekly analytics review, retunes topic weights inside fixed bands |
| `PRLog.org FREE press release - MONTHLY` | `31 16 7 * *` | agent | Monthly press release to PRLog |
| `PROSPECT POOL REFILL` | `0 21 * * 0-4` | agent | `refill_check.sh` gate, then the instruction |
| `PRUNE STALE PINTEREST POSTS` | `0 4 * * *` | script | `pinterest_prune.py` alone, no model call |
| `Pinterest Email Backstop` | `55 17 * * *` | script | `send_pinterest_email.py` alone, no model call |
| `REMINDER ONLY - UPLOAD PRESS RELEASE - MONTHLY` | `1 18 7 * *` | agent | Reminder only, no task |
| `REPLY LIST FILER` | `15 22 * * *` | agent | `reply_lists.sh` gate: file replies and opt-outs to the right lists |
| `SOCIAL MEDIA QUESTIONS - 5PM` | `50 16 * * *` | agent | Ten ranked social questions from the day's AI news |
| `Social Media Questions Email Backstop` | `0 17 * * *` | script | `send_social_email.py` alone, no model call |
| `TUTORIAL IDEAS USING THE DATA` | `0 22 * * *` | agent | Tutorial ideas from the day's data files |
| `Three Outlines For Articles` | `45 16 * * *` | agent | Three fact-based article outlines |
| `WEEKDAY VERIFIER PREFILL` | `0 10 * * 1-5` | script | `weekday_verifier_prefill.sh` alone, no model call |
| `WEEKEND VERIFIER PREFILL` | `0 10 * * 0,6` | script | `weekend_verifier_prefill.sh` alone, no model call |
| `WEEKLY AI NEWS STORIES` | `30 14 * * 0` | agent | Weekly AI news digest |
| `Weekly Agent Change Briefs` **(disabled)** | `0 5 * * 0,2,4,6` | agent | `agent-change-brief-collect.sh` gate, then the instruction |
| `hermes-weekly-backup` | `0 3 * * 0,1,2,3,4,5,6` | script | `hermes-backup.sh` alone, no model call |
| `x-algorithm repo update watcher` | `15 8 * * 0,3,6` | agent | `x-algorithm-update-check.sh` gate, then the instruction |

## The Windows Hermes jobs

Six of these ten are disabled; the live ones are the backup, the Karma inbox processor
and the three panel jobs.

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `windows-weekly-backup` | `0 3 * * 0,1,2,3,4,5,6` | script | `hermes-backup.py` alone, no model call |
| `DAILY Pinterest Posts 6pm` **(disabled)** | `1 18 * * *` | agent | Ten Pinterest posts from the day's data files |
| `BRUSH FEFE'S TEETH` **(disabled)** | `0 11 * * *` | agent | The morning reminder |
| `SOCIAL MEDIA QUESTIONS - 5PM` **(disabled)** | `50 16 * * *` | agent | Ten ranked social questions from the day's AI news |
| `Check For the latest Ollama version` **(disabled)** | `0 21 * * *` | agent | Latest stable and pre-release Ollama versions |
| `Ollama version check AM edition` **(disabled)** | `0 9 * * *` | agent | Morning Ollama version check |
| `EMAIL TASK PROCESSOR (Karma/15min)` | `*/15 * * * *` | agent | `check_agentmail.py` gate, then the instruction |
| `ARTICLE OUTLINE PANEL LAUNCH 440PM` **(disabled)** | `*/5 16-18 * * *` | agent | `check_outlines.py` gate, then the launch instruction |
| `PANEL RE-ARM 435PM` | `35 16 * * *` | script | `panel_rearm.py` alone, no model call |
| `PANEL STALE CLEANUP 1130PM` | `30 23 * * *` | script | `clear_stale_outlines.py` alone, no model call |

## The fifi profile jobs

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `Remote jobs finder` | `0 10 * * *` | agent | Ten remote jobs from the `remote-job-sources` skill, emailed |
| `fifi-profile-daily-backup` | `30 3 * * *` | script | `hermes-backup-fifi.py` alone, no model call |

## The InstaBox Hermes jobs

| Job | Expression | Runner | What runs |
| --- | --- | --- | --- |
| `BACKUP` | `10 20 * * *` | agent | Pushes a backup to GitHub using the InstaBox backup skill |
| `ARTICLE OUTLINE PANEL - 5 CHATBOTS` | `20 17 * * *` | agent | `prep_campaign.py` gate; launches, monitors or reports the panel bot run |
| `disk stale cleanup` | `0 20 * * *` | script | `disk_stale_cleanup.py` alone, no model call |
