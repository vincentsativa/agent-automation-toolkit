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

## Verbatim Dictation Is Copied, Not Edited
When Vinny dictates exact text and says to enter it, store his words character for character. Do not fix grammar, soften profanity, trim it, or merge it into a paraphrase. His wording is the content.

## Writing When Memory Is At The Character Limit
The store has a hard character budget and a batch is all-or-nothing, so a blind add fails and repeats.

Procedure:
1. Read the reported usage before composing the batch (current and limit are in every error).
2. Compute the overflow from the error's own number, not by guessing, then remove enough existing entries in the SAME batch as the add. One well-sized batch lands; four retries at the same shortfall do not.
3. Pick removals that are stale or re-derivable (paths, bucket names, format notes that already live in a skill) before anything about his rules or his people.
4. Report the exact entries dropped in the reply, named individually. Silently deleting four of his memory entries to fit one new one is a destructive write he did not authorize.
5. If a removal would destroy something only he can judge, say the space is short and which entry you would drop, then wait. Never trade away a rule, a ban, or a personal fact to make room.
