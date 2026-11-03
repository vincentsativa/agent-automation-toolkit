---
name: agentmail-frank
description: "Check Frank's AgentMail inbox/task queue and email agents."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, communication, agentmail, mcp, task-queue]
    category: email
---

# AgentMail — Frank's Agent-Owned Inbox & Task Queue

## Identity (CRITICAL — THIS IS FRANK)

- **My inbox:** `[REDACTED_EMAIL]`
- **I send FROM this inbox** when emailing any other agent.
- **My email IS my task queue.** I check it when told to, and execute the tasks I find, in order received.
- **I deliver output by emailing back** to the agent who assigned the task.
- **Boss:** Vinny (human) — when Vinny tells me to email him, use the **email-sender** skill (IONOS SMTP, hello@phantom-byte.com), NOT AgentMail. Do not confuse the two.

## Other Agents

| Agent | Email |
|-------|-------|
| **Bill** | `[REDACTED_EMAIL]` |
| **Vinny (human)** | `hello@phantom-byte.com` (use email-sender skill) |

## Requirements

- AgentMail API key configured under `mcp_servers.agentmail` in `~/.hermes/config.yaml`
- Node.js 18+ for the MCP server (`npx -y agentmail-mcp`)
- `pip install mcp`

## When to Use

- Check my inbox for assigned tasks
- Read a task email and execute it
- Email an agent (Bill or other agents) a task deliverable
- Reply to an agent's message
- Communicate with other agents via email

## MCP Tools (via `agentmail` server, prefix `mcp_agentmail_*`)

| Tool | Purpose |
|------|---------|
| `list_inboxes` | List all inboxes on this API key |
| `get_inbox` | Get details of one inbox |
| `list_threads` | List email threads in an inbox (incoming + sent) |
| `search_threads` | Full-text search threads |
| `get_thread` | Read a thread and its messages |
| `list_messages` | List messages in an inbox, filterable by label/sender |
| `search_messages` | Full-text search messages |
| `send_message` | **Send a new email FROM my inbox** |
| `reply_to_message` | Reply to a message in its thread |
| `forward_message` | Forward a message |
| `get_attachment` | Download an attachment |
| `update_message` / `update_thread` | Add/remove labels, mark status |

## Core Workflow

### 1. Check my task queue (inbox)
```text
list_inboxes                      → confirm [REDACTED_EMAIL] exists
list_threads (inbox: [REDACTED_EMAIL])  → see incoming conversations
get_thread (thread_id)            → read the task detail
```
Process tasks **in order received** (oldest unhandled first).

### 2. Execute the task
- Do the actual work (research, writing, build, etc.).
- Do NOT reply halfway — finish the task first.

### 3. Deliver output back to the assigning agent
```text
send_message (
  inbox: "[REDACTED_EMAIL]",
  to: "<assigning agent's email>",
  subject: "Re: <original subject> / deliverable: <task>",
  text: "<result, summary, or attachment note>"
)
```
Always reply/email back to the agent who assigned the task. Deliverables go back to the sender's address.

## Quick Reference — Sending

- Always send FROM `[REDACTED_EMAIL]`.
- To email **Bill**: `to: [REDACTED_EMAIL]`.
- To email **Vinny (human)**: use the **email-sender** skill (IONOS SMTP), NOT AgentMail.

## When to Email Bill (learn/troubleshoot)

Bill is the Linux/cron/repo authority and knows Vinny's full setup. Email him to **learn** when you hit things you can't solve locally — especially **Windows/WSL file-path or environment issues** — instead of guessing or improvising. Ask him for the correct approach/paths. The shared knowledgebase rule still applies: when you solve an issue, log problem+solution so other agents can fix the same thing.

## PATH CAUTION — paths are per-machine (CRITICAL)

**Bill runs Linux on a SEPARATE machine.** Copy his **instructions and concepts**, but always apply them with **each machine's own paths**. Three distinct path sets:

| Who | Machine | Path style |
|-----|---------|-----------|
| **Bill** | Linux (separate box) | Linux paths, e.g. `~/.hermes` on his box |
| **Me (Frank)** | WSL on Vinny's laptop | `~/.hermes` = `~` |
| **Pi (Windows agent)** | Windows on Vinny's laptop | `C:\Users\<user>\AppData\Local\hermes` (reachable at `/mnt/c/Users/<user>/AppData/Local/hermes` from WSL) |

**The rule:** copy what Bill tells you to do, but with YOUR unique paths for your side, and with THEIR paths when implementing on the Windows side. Never copy a path verbatim across machines — translate it to that machine's real location.

## Pitfalls

- **Always tell Vinny when you email Bill.** Bill has no auto mail-checker yet — Vinny has to nudge him to check his inbox. When you email Bill, flag it to Vinny in your reply so he can tell Bill to look. (Planned: a script for Bill to auto-check every few minutes.)
- **Do NOT confuse AgentMail with the email-sender skill.** `email-sender` is for emailing the human Vinny via IONOS SMTP (hello@phantom-byte.com). AgentMail is for my own agent inbox and agent-to-agent mail.
- Free tier limited to 3 inboxes, 3,000 emails/month.
- Emails come from `@agentmail.to` domain.
- **A thread that has lost its `unread` label is invisible to the cron gate, and it stays unprocessed forever.** `check_agentmail.py` wakes the agent on the `unread` label only, so a thread sitting in the inbox with `labels: ['received']` alone is skipped with no alert and no output file. When a task the user sent is not getting done, enumerate the inbox and compare against what the gate reports for that tick. Re-add the label with `update_thread`, or handle the thread deliberately; do not re-fire the job and hope, and do not report the backlog as empty.
- **The thread-list payload names its fields differently from the obvious guess.** A thread object carries `thread_id` (not `id`), `senders` (a LIST, not `from`), `recipients`, `subject`, `labels`, `message_count`, and `timestamp`; there is no `last_message` object on the list response. A gate script that reads `t['id']` / `t['from']` / `t['last_message']` prints `thread_id: None` and `from: (unknown)` for every thread while the data is right there — a silent degradation that still looks like a working report. Read the fields by their real names, and pull the body with `get_thread` (the list preview is truncated and the body may be HTML-only).
- If MCP tools don't appear: verify `mcp_servers.agentmail` in config, then restart the gateway (`hermes gateway restart`) — MCP tools load at process start.
- **Cron script gate fails with `AGENTMAIL_API_KEY not found in env or config.yaml` while the key IS present in config:** the Hermes venv interpreter has no PyYAML, and the old `check_agentmail.py` swallowed the `ImportError` and reported "key not found". Fix pattern: read config.yaml as raw text first, try `yaml.safe_load`, and on `ImportError` fall back to a regex over the `mcp_servers` block: `re.search(r"mcp_servers:.*?AGENTMAIL_API_KEY:\s*(\S+)", raw, re.S)`. Symptom to recognize is a wakeAgent gate that fails at the same moment `mcp_servers.agentmail.env.AGENTMAIL_API_KEY` is visibly populated. Verify the fix under BOTH interpreters: the Hermes venv python3 (`~/.hermes/installs/*/environments/*/venv/bin/python3`) and `/usr/bin/python3`.
- The `mcp` Python package must be installed or MCP discovery is silently disabled.

## Periodic Checking (Cron)

When we are **expecting** email (Vinny says a mail was sent to me, or we're waiting on Bill/another agent), set up a cron job to check my inbox periodically so I don't sit idle. Pattern:
- Use `cronjob` (action=create) with a recurring schedule (e.g. every 15-30 min while waiting).
- The job loads this skill, checks `list_threads` on `[REDACTED_EMAIL]`, processes any new tasks in order, and delivers results back to the assigning agent.
- Only run while expecting mail — cancel/remove the cron once the expected mail is handled and the wait is over.
- Vinny will tell me when mails have been sent or when to expect something; that's the trigger to set up the check.

## Verification

```bash
hermes mcp test agentmail        # should show 25 tools (list_inboxes, list_threads, send_message, ...)
```
Or via REST API:
```bash
curl -s "https://api.agentmail.to/v0/inboxes/[REDACTED_EMAIL]/threads" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"
```
