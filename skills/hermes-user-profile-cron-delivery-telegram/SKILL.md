---
name: cron-delivery-telegram
description: Always set deliver=telegram for Vinny's cron jobs.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Cron, Delivery, Telegram, Vinny]
references:
  - references/money-making-cron-pattern.md
---

# Cron Delivery: Telegram Only

When setting up any cron job for Vinny, the delivery target must always be `deliver="telegram"` (Home channel). Never use `"origin"` — origin deliveries are invisible to the user and he never receives them.

## When to Use

- Setting up any new cron job
- Editing an existing cron job's delivery target
- Any question about where cron output goes

## Procedure

1. When using the `cronjob` tool with `action='create'`, always include `deliver="telegram"`.
2. Never use `deliver="origin"` — the user confirmed this is the only delivery target that works for him.
3. This applies to every cron job, no exceptions.
4. **Read the persisted `deliver` field back before walking away.** The create or update call returning success is a claim about the call, not the stored job. A job created with `deliver="telegram"` has been found sitting in `jobs.json` as `deliver: local`, and every run of it was then delivered to a file on disk instead of Telegram.

```bash
python3 -c "
import json
d = json.load(open('~/cron/jobs.json'))
for j in d['jobs']:
    if j['id'] == '<job_id>': print(j['name'], '| deliver:', j['deliver'], '| origin:', j.get('origin'))
"
```

A job whose `deliver` is not `telegram` cannot notify him, no matter what its prompt tells it to do. Fix it with `hermes cron edit <job_id> --deliver telegram` and read the field back again.

## Pitfalls

- The default delivery behavior (omitting `deliver`) auto-detects the current chat, which may resolve to "origin" and be invisible to the user.
- Always be explicit: `deliver="telegram"`.

## Proving a notification was suppressed ("I never got the Telegram message")

Two fields decide whether a completion message reached him: the job's persisted `deliver`
field, and each execution's `delivery_outcome`. Check both before re-firing anything.

```bash
# 1. per-run delivery verdict for that job
python3 -c "
import sqlite3
c = sqlite3.connect('~/cron/executions.db')
for r in c.execute(\"select started_at, status, delivery_outcome, error from executions where job_id='<job_id>' order by started_at desc limit 10\"):
    print(r)
"

# 2. what the run actually wrote (delivery_outcome=suppressed means it landed here, not on Telegram)
ls -t ~/.hermes/cron/output/<job_id>/*.md | head -5
```

- `delivered` on a Telegram job vs `suppressed` on a local one is the whole diagnosis. A run can produce a perfectly good completion message and still record `suppressed`.
- **`suppressed` alone is not the bug — pair it with the response text.** A run that answered `[SILENT]` records `suppressed` on a correctly-configured Telegram job too, because there was nothing to send. Read the `## Response` block first: `suppressed` WITH real content is the mis-set `deliver`; `suppressed` with `[SILENT]` is the healthy no-op. Read the reverse way, a silent run after a delivery fix looks like the fix failed.
- The output file holds the injected prompt AND the `## Response` section. Slice the file after `## Response` before reading it: the prompt itself quotes the words `[SILENT]` and "task is completed", so a plain grep over the whole file matches every run and tells you nothing.
- Report the cause by name: the message was written to `~/.hermes/cron/output/<job_id>/` instead of being delivered, because the job's `deliver` field is `local`.

## A cron run sends ONE message on its own — the rest go through the `hermes send` CLI

A cron execution's own delivery is exactly one thing: its final response. `send_message` is
deliberately NOT registered as an agent-callable tool (see the note at the top of
`tools/send_message_tool.py`), so a run cannot ping through the tool mid-flight. It CAN
through the CLI, which reuses the gateway's platform credentials with no LLM and no agent
loop, and works with no gateway running at all for bot-token platforms:

```bash
~/.local/bin/hermes send --to telegram "EMAIL RECEIVED: <subject> from <sender>"
```

Use the absolute path — a cron process PATH does not reliably carry `~/.local/bin`. Success
prints `Sent to telegram home channel (chat_id: ...)` and exits 0; anything else is a real
failure to report, never to swallow.

The three-message shape for an email task (received, started, completed) is therefore one
run, not three ticks:

1. On the first tick that sees unread mail, BEFORE reading the body or starting work:
   `hermes send --to telegram "EMAIL RECEIVED: <subject> from <sender>"`.
2. Immediately after it: `hermes send --to telegram "TASK STARTED: <subject>"`.
3. When the work is done and the report has ACTUALLY gone out, the run's FINAL RESPONSE is
   `TASK COMPLETE: <subject> - email sent to <recipient>`, delivered by the cron itself.

Write those two CLI pings into the job's standing prompt at the TOP of its step list. A ping
sent after the work arrives late and reads as a second completion notice.

- **Do NOT spread the three messages over three ticks** (a received tick, a started tick, a
  work tick). On a 15-minute schedule that pushes the actual work two intervals down the
  road, so the user sits on "started" for half an hour. The CLI collapses all three into the
  receiving run.
- Never let the CLI pings replace the completion response. The final response is still the
  only thing the cron delivers, so the completion claim lives there and nowhere else.
- **A job's OWN standing prompt outranks an instruction inside the task it receives.** A
  task email saying "let me know on Telegram that you got this, then when done notify me"
  produces only the completion message when the job prompt says "only notify me on
  completion" — the run follows the prompt it boots with, not the mail it just read. When a
  user reports a notification that the task explicitly asked for and the job prompt never
  mentioned, that contradiction is the cause: reconcile the job prompt, do not re-fire.
- **A transient `action='run'` prompt is not a delivery test.** The job's own gate and
  standing rules still apply, so a run whose pre-run script reports nothing new returns
  `[SILENT]` and delivers nothing, no matter what the transient prompt says. Prove delivery
  with a real content run or a direct `hermes send` to the same target.

## Reminder vs Task Distinction (CRITICAL — July 10, 2026)

When Vinny says "remind me" or "remind me about X in Y time," that is a **reminder cron** — not a task cron. The distinction matters:

| Type | Purpose | Behavior |
|------|---------|----------|
| **Reminder** | Nudge the user to act | Deliver a short nudge. Do NOT execute the task, do NOT recap everything, do NOT deliver the full output. Just: "Hey, you asked me to remind you about [X]." |
| **Task** | Do the work | Execute the full workflow, deliver the result, notify on completion. |

**The failure (July 10, 2026):**
- Vinny said "remind me of this again in one hour"
- I created a cron that ran and delivered a full recap of the money-making cron (job ID, schedule, what it does, etc.)
- Vinny's response: "this was a reminder not a task... dick. lmao but whatever."
- The reminder should have just said: "Hey — one hour later. You asked me to remind you about the money-making cron. It's ready for review when you are."

**The rule:** A reminder cron's final response is a short nudge. No data, no recap, no execution. Just the nudge. The user will tell you if they want more.

## When Running AS a Cron Job (Not Setting One Up)

When you are the cron job itself (running as a scheduled task), the final response IS the delivery. For large-report cron jobs (10+ stories, long documents, etc.):

### Large Report Delivery Pattern

1. **Save the file** to the user's specified output location.
2. **Email the file** as an attachment using the email-sender skill. Keep the email body short -- just a note saying what the attachment is.
3. **Keep the final response brief.** The cron final response should be a short confirmation that the file was saved and emailed. Do not dump the full report content into the final response.
4. **The user reads the email attachment, not the Telegram message.**

### Why This Matters

The user has explicitly stated: "Do NOT spam my telegram with 20 news stories. Take the text document you've created and attach it to email. In telegram tell me when email is sent, that's it." This is the rule for any cron job that produces a large deliverable. The Telegram message is the notification; the email attachment is the content.
