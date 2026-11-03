---
name: agentmail-setup
description: Use for AgentMail setup. Multi-agent email with own inboxes.
trigger: "Setting up AgentMail, configuring the AgentMail MCP server, or creating an AgentMail inbox."
---

# AgentMail Setup

Multi-agent email. Sign up at console.agentmail.to, generate API key, add MCP server to `~/.hermes/config.yaml`.

## Config

```yaml
mcp_servers:
  agentmail:
    command: npx
    args: ["-y", "agentmail-mcp"]
    env:
      AGENTMAIL_API_KEY: "am_..."
    enabled: true
```

Restart Hermes. Create inboxes via `create_inbox` (username `my-agent` → `agent@example.com`).

## Available MCP Tools

- list/get/create/delete/update inbox
- list/get/search threads + messages
- send/reply/forward
- drafts

## Pitfalls

- Free tier: 3 inboxes / 3,000 emails per month.
- Usernames unique across AgentMail.
- Node 18+.
- Configured in config.yaml, not a skill.
