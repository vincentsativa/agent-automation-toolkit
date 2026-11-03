---
name: agentmail-file-delivery
description: Use to send files or attachments via AgentMail to other agents.
trigger: "Sending a file or attachment to another agent via AgentMail, or delivering a zip to an agent inbox."
category: email
---

# AgentMail File Delivery

How to send FILES/attachments via AgentMail. Companion to `hermes-email-agentmail`.

**THE ONE HARD RULE: attachment URLs must be PUBLICLY fetchable.**

## Signed URLs do NOT work

Firebase `generate_signed_url()` does NOT work (AgentMail fetcher rejects with HTTP 403 — signed URLs carry a Google credential dropped by non-Google fetchers).

## Fix: make blob public, use `blob.public_url`

```python
blob.make_public()
print(blob.public_url)  # https://storage.googleapis.com/...
```

Verify with `curl -s -o /dev/null -w "%{http_code}" <url>` (expect 200).

## Small files (< ~300KB)

Prefer `content` (base64, `base64 -w0 <file>`) — no hosting step.

## Send

Via `mcp__agentmail__send_message`:
- inboxId: `[REDACTED_EMAIL]`
- `to`: the target agent ([REDACTED_EMAIL] = Frank / [REDACTED_EMAIL])
- `attachments: [{filename, contentType, content|url}]`
- Sign body with `— Bill`.

## Verify delivery — don't trust send result alone

`list_threads` on the target inbox, match subject, confirm attachment filename + size present.

## Zip flow

Copy to `/tmp/zip_src`, `zip -r` to Desktop, `unzip -l` to verify, `rm -rf /tmp/zip_src`. Deliver zip on Vinny's Desktop, not /tmp.

## Never route Vinny's own email through AgentMail

"email it to me" → the IONOS `email-sender` skill. AgentMail only for Hermes → other-agents.
