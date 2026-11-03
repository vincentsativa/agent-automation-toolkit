# Scheduled jobs

`hermes-cron-jobs.json` is the live cron table exported with credentials, chat IDs and
personal paths removed. Each entry:

```json
{
  "name": "windows-weekly-backup",
  "schedule": "0 3 * * 0,1,2,3,4,5,6",
  "enabled": true,
  "runner": "deterministic-script",
  "script": "hermes-backup.py",
  "model": "deepseek-v4.1-flash:1017",
  "instructions": null
}
```

| Field | Meaning |
| --- | --- |
| `schedule` | Standard five-field cron expression |
| `runner` | `deterministic-script` runs a script with no model; `agent-prompt` runs `instructions` in an agent session |
| `script` | Script name for deterministic jobs |
| `model` | Model bound to the job, so a model change does not silently change scheduled behaviour |
| `instructions` | The full prompt, including the delivery rule and the failure behaviour |

## The jobs

| Job | Expression | Runner | Purpose |
| --- | --- | --- | --- |
| `windows-weekly-backup` | `0 3 * * *` | script | Nightly snapshot of the agent home to a private git remote |
| `EMAIL TASK PROCESSOR (Karma/15min)` | `*/15 * * * *` | prompt | Poll an agent inbox and act on task mail, gated by a script that decides whether there is anything to wake the model for |
| `PANEL RE-ARM 435PM` | `35 16 * * *` | script | Re-arms a polling window a later failure could leave disarmed |
| `PANEL STALE CLEANUP 1130PM` | `30 23 * * *` | script | Clears state left behind by an interrupted run |
| `ARTICLE OUTLINE PANEL LAUNCH 440PM` | `*/5 16-18 * * *` | prompt | Polls during the panel window and launches work only when a new outline appears |
| `SOCIAL MEDIA QUESTIONS - 5PM` | `50 16 * * *` | prompt | Produces ranked social questions from the day's data files, mails them, then sends one short Telegram line |
| `DAILY Pinterest Posts 6pm` | `1 18 * * *` | prompt | Ten pins with per-board routing and platform length limits |
| `Check For the latest Ollama version` | `0 21 * * *` | prompt | Release lookup, reports the installer link and the client version |
| `Ollama version check AM edition` | `0 9 * * *` | prompt | Same job on a morning schedule |
| `BRUSH FEFE'S TEETH` | `0 11 * * *` | prompt | A reminder that must always be delivered — the counter-example to the `[SILENT]` convention |

Jobs marked disabled in the export were paused at export time; they are kept because the
instruction text is the interesting part.

## Conventions that make this work

- **A script gate in front of the model.** The 15-minute inbox job runs a script first; the
  model only wakes when the script says there is work. Cheap polls, expensive judgement.
- **Delivery is specified in the prompt.** Every job states exactly what the final response
  may contain, because in this system the final response *is* the notification.
- **One notification per turn.** Long-running activity is patched to arrive silently
  (`scripts/telegram/silent-telegram-activity-patch.mjs`) so a scheduled job with tool use
  does not produce a burst of sounds.
- **Scripts, not shell, on Windows.** The cron runner turns relative paths into Windows
  absolute paths and hands them to Bash, which eats `\U`, `\D`, `\A` as escape sequences.
  Anything non-trivial is Python for that reason alone.
