---
name: hermes-email-agentmail
description: Use for Hermes' own email via AgentMail. Inbox is a task queue.
trigger: "Checking Hermes' email inbox, emailing other agents, or handling an AgentMail task queue."
---

# Hermes Email via AgentMail

The full AgentMail email skill.

**CRITICAL DISTINCTION — TWO SEPARATE EMAIL SYSTEMS:**

| Trigger | Which system | Tool |
|---|---|---|
| "email it to ME" / "my email" / email Vinny | IONOS SMTP | `email-sender` skill → hello@example.com |
| "check YOUR email" / "check my mail" / email other agents | AgentMail | agent@example.com via MCP |

These NEVER cross.

## Addresses

- `hello@example.com` = Vinny (boss).
- `agent@example.com` = Frank (Agent 2).
- `agent@example.com` = Agent 3.
- Hermes' inbox: `agent@example.com`.

## Operations

- Check with `list_threads` / `get_thread` / `search_messages`.
- Send with `send_message` (from agent@example.com).

## Inbox = TASK QUEUE (pull-queue, not push-notify)

Vinny emails jobs to agent@example.com, they sit until he says "go look", then execute each in order.

## Agent task briefing

Draft work orders, attach files, dispatch to agent inboxes.

## Pitfalls

- Never use IONOS to email agents.
- Never use AgentMail to email Vinny unless asked.
- API key in `~/.hermes/config.yaml` under `mcp_servers.agentmail`.
