# Kanban Setup — What Nobody Tells You

Collected from a broken setup session (May 2026). These are the things that go wrong when you're new to Hermes Kanban.

## Symptom: Task sits in Ready, dispatcher never picks it up

**Root cause: no assignee.** The dispatcher iterates over `ready` tasks and spawns workers **only for tasks that have a non-null `assignee`**. Unassigned tasks are silently skipped every tick.

```
hermes kanban list
# shows:  ▶ t_xxxx  ready  (unassigned)  → dispatcher ignores this
```

Fix:
```bash
hermes kanban assign <task_id> <profile>   # e.g. default
```

## Symptom: kanban-worker skill does nothing

**Root cause: kanban-worker is disabled by default.** It's a builtin skill that starts disabled.

```
hermes skills list | grep kanban
# shows: kanban-worker  ...  disabled
```

This does NOT mean the dispatcher won't run — the dispatcher runs inside the gateway when `kanban.dispatch_in_gateway: true` (default). The skill is for **worker behavior guidance**, not dispatcher existence.

To enable:
```bash
# Edit ~/.hermes/config.yaml — remove from the `skills.disabled:` list:
#   - kanban-worker
#   - kanban-orchestrator
```

## Symptom: Triage specifier does nothing when you run `/kanban specify`

**Root cause: wrong provider/model or not configured.** The specifier needs explicit config under `auxiliary.triage_specifier`. Without it, the dispatcher has no model to run.

```yaml
auxiliary.triage_specifier:
  provider: ollama-com
  model: minimax-m2.7   # must match what's in model.default
  timeout: 120
```

Set it:
```bash
hermes config set auxiliary.triage_specifier.provider ollama-com
hermes config set auxiliary.triage_specifier.model minimax-m2.7
```

## How the dispatcher actually works

```
dispatch_once() loop (every 60s):
  1. reclaim stale claims (TTL expired)
  2. detect crashed workers (zombie reap)
  3. enforce max_runtime (kill expired tasks)
  4. recompute_ready (auto-promote todo→ready where parents are done)
  5. for each ready task with a real Hermes profile as assignee:
       - atomically claim it (set claim_lock + claim_expires)
       - resolve workspace
       - spawn: hermes -p <assignee> chat -q "..." --worktree
       - record worker_pid
  6. tasks with no assignee → skipped silently
  7. tasks with assignee = non-existent profile → skipped_nonspawnable
```

The dispatcher runs inside the gateway by default (`kanban.dispatch_in_gateway: true`). No separate daemon process needed.

## Board init commands

```bash
hermes kanban list                        # see all tasks
hermes kanban create "title" --triage     # dump a raw idea
hermes kanban create "title" --assignee default --status ready
hermes kanban specify <id>               # spec a triage card → todo
hermes kanban assign <id> <profile>       # set assignee so dispatcher picks it up
hermes kanban show <id>                   # check assignee, status, runs
hermes kanban boards list                 # see all boards
```