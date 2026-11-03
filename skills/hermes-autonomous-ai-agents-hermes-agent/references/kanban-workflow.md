# Kanban Workflow & Column Semantics

This file documents the kanban board columns, use cases, and user-facing explanations
for the Hermes Agent kanban system. Written for agents to reference when explaining
kanban to users.

## Default Columns (Hermes Kanban Board)

| Column | Purpose | User Explanation |
|--------|---------|------------------|
| **Triage** | Raw idea dump, unvetted | "Dump half-baked thoughts here. The AI can spec them out and promote to Todo." |
| **Todo** | Vetted + worth doing, not yet queued | "You've decided this is real. Just not prioritized yet." |
| **Ready** | Queued for execution | "Dispatcher picks from here. Move items here when you want action taken." |
| **In Progress** | Actively being worked on | "Someone is working on this — you, or an autonomous agent." |
| **Blocked** | Stuck on external dependency | "Waiting on something outside this task before it can proceed." |
| **Done** | Completed | "Finished. Summary/result attached to the card." |
| **Archived** | Old done work, preserved for reference | "Cleaned up but not deleted. History is preserved." |

## Workflow Flow

```
Triage ──(specifier)──> Todo ──> Ready ──> In Progress ──> Done ──> Archived
                              └──> Blocked ──> Ready (when unblocked)
```

Not all columns need to be used. Many users operate with just:
- Todo → Ready → In Progress → Done

## Triage Specifier Mode (`--triage`)

When a task is created with `--triage`, the dispatcher:
1. Picks up the raw idea
2. Fleshes out a detailed spec (title, body, implementation plan, research links)
3. Promotes it to Todo
4. The spec is attached to the card as the task body

This eliminates hallucinations when kicking around ideas — the AI commits the
spec to the card for later review.

## User-Facing Examples

**Article Pipeline flow:**
1. Triage: "Article about Claude's new features" (rough idea)
2. Dispatcher specs it → Todo with outline + angle
3. Move to Ready when ready to write
4. Write PRO draft → In Progress (or move manually)
5. Flash refinement pass → In Progress
6. Done when published

## Key Differences from Trello/Generic Kanban

- **Dispatcher integration:** Cards in Ready can be autonomously claimed and
  executed by Hermes worker agents. This is the unique power — it's a queue
  for autonomous execution, not just a passive status board.
- **Workspace isolation:** Each claimed task gets an isolated workspace
  (scratch, worktree, or dir:<path>).
- **No scheduled start times:** Kanban doesn't support "run this at 5pm."
  Pair with cron if you need time-based triggering.

## Access Points

| Method | Command/URL | Notes |
|--------|-------------|-------|
| Web dashboard | `hermes dashboard` → port 9119 → KANBAN in sidebar | Sidebar scrolls; kanban is under PLUGINS |
| CLI | `hermes kanban <subcommand>` | Full feature set |
| Dashboard inline | Click column "+" buttons to create cards | Quick entry from web UI |

## Multi-Project Boards

- `hermes kanban boards list` — see all boards
- `hermes kanban boards switch <slug>` — change active board
- `hermes kanban boards create <slug>` — new board
- Each board has its own database under `~/.hermes/kanban/boards/<slug>/`
- The `--board <slug>` flag can target any board from any command
