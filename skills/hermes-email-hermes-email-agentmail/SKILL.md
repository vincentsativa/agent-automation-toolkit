---
name: hermes-email-agentmail
description: Use for Hermes' own email via AgentMail. Inbox is a task queue.
trigger: "Checking Hermes' email inbox, emailing other agents, or handling an AgentMail task queue."
category: email
---

# Hermes Email via AgentMail

The full AgentMail email skill.

**CRITICAL DISTINCTION, TWO SEPARATE EMAIL SYSTEMS:**

| Trigger | Which system | Tool |
|---|---|---|
| "email it to ME" / "my email" / email Vinny | IONOS SMTP | `email-sender` skill → hello@phantom-byte.com |
| "check YOUR email" / "check my mail" / email other agents | AgentMail | [REDACTED_EMAIL] via MCP |

These NEVER cross.

## Addresses

- `hello@phantom-byte.com` = Vinny (boss).
- `[REDACTED_EMAIL]` = Frank (Agent 2).
- `[REDACTED_EMAIL]` = Agent 3.
- Hermes' inbox: `[REDACTED_EMAIL]`.

## Operations

- Check with `list_threads` / `get_thread` / `search_messages`.
- Send with `send_message` (from [REDACTED_EMAIL]).

## Inbox = TASK QUEUE (pull-queue, not push-notify)

Vinny emails jobs to [REDACTED_EMAIL], they sit until he says "go look", then execute each in order.

## Agent task briefing

Draft work orders, attach files, dispatch to agent inboxes.

## Pitfalls

- Never use IONOS to email agents.
- Never use AgentMail to email Vinny unless asked.
- API key in `~/.hermes/config.yaml` under `mcp_servers.agentmail`.
