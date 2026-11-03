---
name: agent-change-briefs-sync
description: Apply the latest weekly change-brief to both Hermes agents.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sync, agent, brief, weekly, multi-agent, windows, wsl]
    category: devops
---

# Agent Change Briefs, Sync to WSL + Windows Agents

## Purpose

Every **Sunday ~5am**, Bill's agent diffs the last 7 days of changes to Vinny's Hermes setup and pushes a dated brief to the private repo `vincentsativa/agent-change-briefs` at `briefs/<YYYY-MM-DD>.md`. This skill applies that brief to BOTH agents:

| Agent | Where it runs | Hermes home |
|-------|--------------|-------------|
| **Frank** (this WSL agent) | Windows laptop, WSL | `~/.hermes` (Linux path) |
| **Windows agent** (called **Pi** in the briefs, identifies itself as **Karma**, agent3, in its own memory) | Windows | `/mnt/c/Users/<user>/AppData/Local/hermes` |

Read the Windows tree's own `memories/MEMORY.md` to learn which agent it currently is before writing to it. That tree has changed identity once already, and a stale label is how you end up reporting work against the wrong agent.

## Where briefs actually are

- `~/agent-change-briefs/briefs/<YYYY-MM-DD>.md`, the original briefs repo. It can go stale and stop receiving pushes long before the setup stops changing.
- `~/.hermes/cron/output/agent-change-brief-<YYYY-MM-DD>.md`, briefs written by the weekly cron job (`0f9182f1d46d`, schedule `0 5 * * 0,2,4,6`). Newer briefs live here when the repo is dead.
- `~/.hermes/cron/output/<job-id>/<timestamp>.md`, the same runs, filed per job.
- `/tmp/hermes-backup` (fresh clone) and `~/linux-hermes-backup` (older clone), `github.com/vincentsativa/linux-hermes-backup`, the raw source of truth the briefs diff. Compare against this when you suspect the brief pipeline has died.

## Core Workflow (run this when Vinny or Bill says "update yourself", or on the weekly cron)

1. **`git pull`** in `~/agent-change-briefs`, then list `briefs/` AND `~/.hermes/cron/output/agent-change-brief-*.md`. Take the highest date across both as the latest brief. Check Frank's AgentMail inbox as well (`[REDACTED_EMAIL]`, search `brief`) in case one arrived by mail.
2. **If the newest brief looks old, prove the pipeline is still alive before believing there is nothing to do:** read the job's `enabled` flag in `~/.hermes/cron/jobs.json`. A disabled brief job means briefs stopped while the backup repo kept moving, so the real gap is unreported.
3. **The live source of truth beats the newest brief.** With the pipeline dead, diff current `/tmp/hermes-backup` against both trees and treat anything the backup carries and a tree lacks as an unapplied brief item. Never conclude "nothing to apply" from a stale repo alone.
4. Work through each section IN ORDER:
   - **(A) Behavioral rules / constitution**, apply FIRST, governs everything
   - **(B) Skills to create or update**, replicate each skill on BOTH agents
   - **(C) Memory / profile changes**, DO NOT APPLY. Memory is never touched unless Vinny personally says add or subtract (see `memory-touch-rule`); a brief listing memory edits is not that permission. Report the skipped memory items and the reason.
   - **(D) Scripts / tooling**, install/configure tools on BOTH
5. **Apply to the Windows tree too**, writing under `/mnt/c/Users/<user>/AppData/Local/hermes/` (skills in `skills/`, memories in `memories/`).
   - A file present on both trees gets the DELTA only: patch the exact bullet or section the brief names. Never overwrite a shared skill with the WSL copy, because each tree carries content the other lacks.
   - A skill missing on the Windows tree gets copied whole (`shutil.copytree`, which brings `references/` with it), then proven with `diff -r`.
   - Match the target file's existing line ending when inserting text. A CRLF file that receives LF lines renders with join breaks; test `'\r\n' in text` first and convert the inserted block.
   - Verify with a marker table after writing, never from the memory of what you just inserted.

## Hard Rules

- **Never copy a change you don't understand.** If a brief is ambiguous, email Bill ([REDACTED_EMAIL]) BEFORE acting. Do NOT improvise.
- **Both agents must be kept in sync.** WSL is done directly; Windows is done by writing files into the `/mnt/c/.../hermes` tree.
- **The live system beats any note about it.** A brief, a skill, or a file stating the state of a tree is a claim to verify against that tree. When they disagree, the tree wins and the stale note gets corrected in the same turn.
- **Track which changes were applied** so the confirmation email is accurate.

## Deliverable / Confirmation

- After applying, email **Bill** at `[REDACTED_EMAIL]` from `[REDACTED_EMAIL]` (AgentMail, `send_message`): exactly which changes went to which tree, every item deliberately skipped with its reason, and the dead-pipeline flag when that is what you found. Read the sent thread back with `get_thread` before telling Vinny it went out.
- Final response to Vinny: concise summary of what was applied where.

## Verification

Verify per item with real output, on BOTH trees. "Synced" is only sayable after every item was walked.

- Build a marker table: one `relpath|distinct-phrase` line per brief item, then count that phrase in both trees. Present reads 1, missing reads 0. `python3 scripts/verify_two_trees.py --items <file>` does exactly this.
- Copied skills: `diff -r` the WSL source against the Windows copy. Byte-identical or it is not done.
- Edited files: grep each inserted marker on the Windows side (expect 1) and confirm the superseded line is gone (expect 0).
- Constitution: `grep -o "## Article [0-9]*"` on both trees; the article sets must match.
- Confirm the tree you wrote to is the tree you meant to write to, read from its own `memories/MEMORY.md`.
- Delta-insertion recipe and pipeline forensics commands: `references/windows-tree-sync.md`.
