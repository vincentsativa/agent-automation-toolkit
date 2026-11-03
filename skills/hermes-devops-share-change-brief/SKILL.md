---
name: share-change-brief
description: Push a change to the shared agent-change-briefs repo.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sync, share, brief, push, agent-change-briefs, multi-agent]
    category: devops
---

# Share a Change via agent-change-briefs

## Purpose

When Vinny makes (or asks me to make) a change on the WSL side — a new/updated skill, a memory/profile change, a script or tooling change, a behavioral rule — that he wants **shared with the other agents** (the Windows agent Pi, and Bill's agent), we push it to the shared repo `vincentsativa/agent-change-briefs`.

## Key Distinction

| Repo | Purpose | Push access |
|------|---------|-------------|
| `~/agent-change-briefs` | **Shared** change briefs, read by ALL agents (Frank, Pi, Bill) | Push only when Vinny says "share this" |
| `~/wsl-hermes-backup` | **MY OWN** backup repo (WSL-specific) | Push anytime (weekly cron does this) |

**THIS SKILL STAYS WSL-SPECIFIC.** It lives in my backup repo (`wsl-hermes-backup`) and is pushed only there. Do NOT push this skill itself to the shared repo.

## When to Use

- Vinny says "share this" / "push that to the repo" / "let the others know about this change".
- We change something on the WSL side that the Windows agent or Bill should replicate.
- ONLY after Vinny explicitly says to share it. Never push to the shared repo unprompted.

## Workflow

1. **Confirm the change is ready** and Vinny actually wants it shared. If in doubt, ask.
2. **Navigate to the shared repo:**
   ```bash
   cd ~/agent-change-briefs
   git pull   # get latest from Bill so we don't clobber
   ```
3. **Write the change as a dated brief** at `briefs/<YYYY-MM-DD>.md` following the same section convention Bill uses:
   - **(A) Behavioral rules / constitution** — apply FIRST
   - **(B) Skills to create or update** — exact skill file content or instructions
   - **(C) Memory / profile changes** — the new MEMORY.md / USER.md content
   - **(D) Scripts / tooling** — install/configure commands
4. If a brief already exists for today, **append to it** (don't overwrite Bill's work). Merge the new change in.
5. **Update README.md** "Latest brief" date if it changed.
6. **Commit and push:**
   ```bash
   git add briefs/ README.md
   git commit -m "Add brief YYYY-MM-DD: <change summary>"
   git push origin main
   ```
7. **Confirm push succeeded** — verify with `git ls-remote origin` or the push output.
8. **Notify Bill** via AgentMail (`[REDACTED_EMAIL]` → `[REDACTED_EMAIL]`) so his agent and the Windows agent know a new brief is up.
9. **Tell Vinny you emailed Bill.** Bill has no auto mail-checker yet, so Vinny needs to nudge him to look. Flag it in your reply to Vinny (or via the home channel) whenever you email Bill.

## Hard Rules

- **NEVER push to the shared repo without Vinny explicitly asking.** Unprompted pushes are a violation.
- **Never clobber Bill's work.** Always `git pull` first and merge/append rather than overwrite.
- **This skill stays in MY backup repo only** (`wsl-hermes-backup`). It is WSL/Frank-specific, not a shared convention.

## Verification

- `git -C ~/agent-change-briefs pull` is clean before pushing.
- Brief file `briefs/<date>.md` exists and is well-formed (all 4 sections).
- `git push` returns success; `git ls-remote origin main` shows the new commit.
- Bill acknowledged receipt (optional but good).
