---
name: memory-management
description: Use before memory writes. Memory is short-term only.
trigger: "Before ANY memory write, or when deciding what belongs in memory vs profile."
---

# Memory Management

Vinny's rule: **"The memory is for short term stuff."** Memory holds TEMPORARY state cleared after it serves its purpose. It is NOT durable storage.

## What goes in memory (short-term, delete after)
- Planning notes for an upcoming session.
- Task-state ("we're using X for Y tonight").
- Items queued for a work session.

## What NEVER goes in memory
- Long-term/preference facts (profile lives in USER.md).
- Model stacks.
- Environment setup.
- Durable workflow conventions.
- Task progress.
- PR/issue numbers, SHAs, "fixed bug X".
- Anything that still matters in 7+ days.

## Rule of thumb
Before every memory write ask: "Is this SHORT-TERM temporary state cleared after the work?" If unsure, don't write.

## Delete after use
`memory(action='remove', old_text='...')` with a unique substring.

## Do NOT
Auto-save model stack/tool setup/preferences without being asked.
