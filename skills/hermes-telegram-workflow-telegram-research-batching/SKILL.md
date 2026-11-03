---
name: telegram-research-batching
description: Batching rules for research tasks on Telegram to prevent message spam
---

# Telegram Research Batching

## Trigger
User asks for research ("what are people saying about X?", "look up Y", "find info on Z")

## Rules
1. MAX 2 tool calls per response turn when user is on Telegram interface
2. Batch all findings into ONE consolidated response — never stream partial updates
3. If more research is needed, ASK permission: "Want me to dig deeper?"
4. Prefer direct answers with 2-3 key points over exhaustive lists
5. Each tool call = separate Telegram notification. Treat notifications like they're expensive.

## Escalation
If user says "stop spamming" or complains about message volume:
- Immediately stop all tool calls
- Summarize what was found so far in ONE message
- Do not resume research without explicit permission
- Set internal flag: this user is on a high-latency/high-notice interface

## Anti-patterns
- Chaining 5+ browser/tool calls in one turn
- Sending "Let me check..." as a standalone message before results
- Dumping raw tool output without summarizing