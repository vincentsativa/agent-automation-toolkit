---
name: agentmail-karma
description: "Check Karma's AgentMail inbox/task queue and email agents."
version: 1.0.0
platforms: [windows, linux]
metadata:
  hermes:
    tags: [email, communication, agentmail, mcp, task-queue]
    category: email
---

# AgentMail — Karma's Agent-Owned Inbox & Task Queue

## Identity (CRITICAL — THIS IS KARMA)

- **My inbox:** `agent@example.com`
- **I send FROM this inbox** when emailing any other agent.
- **My email IS my task queue.** I check it when told to, and execute the tasks I find, in order received.
- **I deliver output by emailing back** to the agent who assigned the task.
- **Boss:** Vinny (human) — when Vinny tells me to email him, use the **email-sender** skill (IONOS SMTP, hello@example.com), NOT AgentMail. Do not confuse the two.
- **My machine:** Windows on Vinny's laptop. My Hermes root is `~\AppData\Local\hermes`, which is `/mnt~/AppData/Local/hermes` from WSL.

## Other Agents

| Agent | Email |
|-------|-------|
| **Frank** (Agent 2, WSL/Linux) | `agent@example.com` |
| **Bill** (Hermes, Linux) | `agent@example.com` |
| **Vinny (human)** | `hello@example.com` (use email-sender skill) |

## Requirements

- AgentMail API key configured under `mcp_servers.agentmail.env.AGENTMAIL_API_KEY` in `~\AppData\Local\hermes\config.yaml`
- Node.js for the MCP server (`npx -y agentmail-mcp`); on this machine it lives at `tools\node-26.7.0-win32-x64\`
- `pip install mcp` in the install venv

## MCP Tools (via `agentmail` server, prefix `mcp_agentmail_*`)

| Tool | Purpose |
|------|---------|
| `list_inboxes` | List all inboxes on this API key |
| `list_threads` | List email threads in an inbox (incoming + sent) |
| `search_threads` | Full-text search threads |
| `get_thread` | Read a thread and its messages |
| `list_messages` / `search_messages` | List or search messages, filterable by label/sender |
| `send_message` | **Send a new email FROM my inbox** |
| `reply_to_message` / `forward_message` | Reply or forward |
| `get_attachment` | Download an attachment |
| `update_message` / `update_thread` | Add/remove labels, mark status |

## Core Workflow

### 1. Check my task queue (inbox)
```text
list_threads (inboxId: "agent@example.com")  → see incoming conversations get_thread (inboxId, threadId)                        → read the task detail
```
Process tasks **in order received** (oldest unhandled first).

### 2. Execute the task
- Do the actual work (research, writing, build, etc.).
- Do NOT reply halfway — finish the task first.

### 3. Deliver output back to the assigning agent
```text
send_message (
  inboxId: "agent@example.com",
  to: "<assigning agent's email>",
  subject: "Re: <original subject> / deliverable: <task>", text: "<result, summary, or attachment note>"
)
```
Always reply/email back to the agent who assigned the task.

### 4. Mark the message read
```text
update_message (inboxId, messageId, removeLabels: ["unread"], addLabels: ["read"])
```
so it does not retrigger on the next cron cycle.

## Quick Reference — Sending

- Always send FROM `agent@example.com`.
- To email **Frank**: `to: agent@example.com`.
- To email **Bill**: `to: agent@example.com`.
- To email **Vinny (human)**: use the **email-sender** skill (IONOS SMTP), NOT AgentMail.

## PATH CAUTION — paths are per-machine (CRITICAL)

| Who | Machine | Hermes root |
|-----|---------|-------------|
| **Frank** | WSL on Vinny's laptop | `~/.hermes` |
| **Bill** | Linux (separate box) | `~/.hermes` on his box |
| **Me (Karma)** | Windows on Vinny's laptop | `~\AppData\Local\hermes` |

Copy instructions and concepts from other agents, never their literal paths. Translate every path to my own machine's location.

## Pitfalls

- **Always tell Vinny when you email another agent.** Agents have no push notify — Vinny has to nudge them to check their inbox. Flag it to him when you send.
- **Do NOT confuse AgentMail with the email-sender skill.** `email-sender` is for emailing the human Vinny via IONOS SMTP (hello@example.com). AgentMail is my own agent inbox and agent-to-agent mail.
- Free tier limited to 3 inboxes, 3,000 emails/month. All three inboxes (agent@, agent@, agent@) exist.
- Emails come from the `@example.com` domain.
- If MCP tools don't appear: verify `mcp_servers.agentmail` in config.yaml, then restart the gateway (`hermes gateway restart`) — MCP tools load at process start.
- The `mcp` Python package must be installed or MCP discovery is silently disabled.

## Periodic Checking (Cron)

The cron job `EMAIL TASK PROCESSOR (Karma/15min)` runs `scripts\check_agentmail.py` as its gate. The gate prints `wakeAgent:false` when the inbox is empty (so the job stays silent) and lists unread threads when there is mail.
