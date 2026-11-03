---
name: hermes-state-migration
description: Migrate Hermes state between machines, clone a backup repo, restore skills/cron/memories/kanban, handle config gaps, and manage multi-machine cron handoff.
version: 1.1.0
author: Hermes Agent
tags: [hermes, migration, backup, restore, setup, multi-machine]
---

# Hermes State Migration

Migrate Hermes from one machine to another by cloning a private backup repo and restoring state. Read-only from the repo, never push back.

## When to Use

- Setting up a fresh Hermes install on a new machine (Linux, macOS, WSL)
- Restoring from a backup after a reinstall
- Provisioning a second Hermes instance while the first is still active
- Moving from WSL to native Linux (or vice versa)
- **Partial migration**: copying only cron jobs (or only skills, only memories) from the backup, leaving existing state intact
- **Multi-repo migration**: user has separate backup repos (e.g. `wsl-hermes-backup` AND `windows-hermes-backup`), confirm which one to use from
- **Non-Hermes agent backups**: user also keeps backup repos for other tools (e.g. `pi-agent-backup` for the Pi coding agent). Same clone-and-restore principle, but the target layout differs, see [references/pi-agent-backup.md](references/pi-agent-backup.md) for the Pi-specific sync-not-clone pattern.

## Prerequisites

- Hermes installed on the target machine
- A GitHub personal access token (classic or fine-grained) with repo read access to the backup repo
- The backup repo contains: `skills/`, `cron/`, `memories/`, `kanban/` directories
- Config (`.env`, `config.yaml`) is typically **gitignored**, must be set up separately
- **CRITICAL, Confirm the exact backup repo name with the user.** Do NOT infer it from a prior session or a different machine's backup name. Users may maintain separate repos per machine (WSL vs Windows), using the wrong one is a hard failure the user will call out immediately.

## Migration Steps

### 1. Clone the Backup Repo

```bash
cd /tmp
GIT_TERMINAL_PROMPT=0 git clone https://<TOKEN>@github.com/<user>/<repo>.git backup-hermes
```

Use `GIT_TERMINAL_PROMPT=0` to prevent git from hanging on auth prompts if the token is wrong.

### 2. Inspect the Backup

Check what's in the repo before copying:

```bash
ls /tmp/backup-hermes/
cat /tmp/backup-hermes/.gitignore   # Shows what's intentionally excluded
```

Common gitignored items: `config/.env`, `config/config.yaml`, `*.lock` files, `.curator_backups/`, `.hub/`.

### 3. Stop Cron (Prevents File Conflicts)

```bash
hermes cron status   # Check if gateway/cron is running
# If running, stop it. On a fresh install it likely isn't.
```

### 4. Restore State Directories

Use `rsync -a --delete` to mirror the backup into `~/.hermes/`:

```bash
rsync -a --delete /tmp/backup-hermes/skills/    ~/.hermes/skills/
rsync -a --delete /tmp/backup-hermes/cron/      ~/.hermes/cron/
rsync -a --delete /tmp/backup-hermes/memories/  ~/.hermes/memories/
rsync -a --delete /tmp/backup-hermes/kanban/    ~/.hermes/kanban/
```

**`--delete` is intentional**, it ensures stale skills/jobs from the old install are removed, not accumulated. The backup is the source of truth.

### 4b. Partial Migration (Cron-Only or Selective Restore)

When the user wants to migrate specific crons (or skills, memories) from a backup WITHOUT overwriting existing state:

**Step 1, Read the backup's jobs.json** to see what's available:
```bash
cat /tmp/backup-hermes/cron/jobs.json | python3 -m json.tool
```

**Step 2, Create each cron via `cronjob action=create`** with the exact schedule, model, skills, and prompt from the backup. Adapt paths:
- Windows paths like `C:\Users\...` → `/home/<user>/...`
- Windows-specific skills may not exist on the target, copy them from the backup's `skills/` directory or substitute

**Step 3, Pause all imported crons immediately** since the old machine is still running them:
```bash
cronjob action=update job_id=<ID> schedule=<schedule> # if you used create
```

Or use `cronjob action=pause job_id=<ID>` after creation.

**Step 4, Verify** by listing and checking each job's state shows `paused`.

This approach avoids the destructive `rsync --delete` pattern and lets the user keep local jobs that don't exist in the backup.

For **individual skill migration**, copy the skill directory from the backup into the target's skills:
```bash
cp -r /tmp/backup-hermes/skills/<category>/<skill-name> ~/.hermes/skills/<category>/
```

### 5. Verify Restoration

```bash
echo "Skills:" && ls ~/.hermes/skills/ | wc -l
echo "Cron jobs:" && cat ~/.hermes/cron/jobs.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('jobs',[])))"
echo "Memories:" && ls ~/.hermes/memories/
echo "Kanban:" && ls -R ~/.hermes/kanban/
```

### 6. Handle Config (Gitignored)

Config is almost always gitignored. On the new machine:

- **Ollama/local models**: Usually already set up, no action needed
- **API keys**: Set up fresh via `hermes setup` or edit `~/.hermes/.env`
- **Gateway platforms** (Telegram, Discord, etc.): Set up fresh via `hermes gateway setup`
- **Custom providers**: Re-add in `~/.hermes/config.yaml` if needed

### 7. Cron: Multi-Machine Handoff

When migrating between machines where the old machine is still running cron:

```bash
# On the new machine, cron is restored but should be paused
hermes cron status   # Will show "Gateway is not running, cron jobs will NOT fire"

# When ready to migrate:
# 1. Pause/disable cron on the old machine
# 2. Enable gateway on the new machine: hermes gateway install
# 3. Verify jobs fire: hermes cron list
```

**Do NOT enable cron on the new machine until the old one is disabled**, otherwise both machines fire the same jobs, causing duplicate deliveries.

## Pitfalls

- **Token in command history**: The PAT is visible in shell history and Hermes terminal output. Store it securely, save to memory so you can reuse it across tool calls without pasting it each time.
- **`rsync --delete` is destructive**: Double-check source/destination paths. A swapped pair wipes `~/.hermes/`.
- **Config is never in the repo**: Don't expect `.env` or `config.yaml` to be restored. Plan for manual setup.
- **Cron output dirs are large**: The `cron/output/` directory can have hundreds of historical run logs. This is expected, they're small files.
- **Lock files cause rsync warnings**: `*.lock` files in memories/ and other dirs are transient. The backup's `.gitignore` typically excludes them, so they won't exist in the clone. If they do, just remove them.
- **Don't assume the user needs API keys**: If they use Ollama/local models exclusively, no API keys are needed. Ask before suggesting key setup.
- **Cron is paused by design on a fresh install**: The old machine is still running jobs. Don't restart cron on the new machine without confirming the handoff plan.
- **LISTENING: the user named the exact repo, use it.** If the user says "Windows, not WSL" and names the repo, do NOT search for the wrong one first. Trust their words over your session history. When they say "windows-hermes-backup", clone that, not "wsl-hermes-backup". Getting this wrong produces anger and wasted tool calls.
- **Windows paths in cron prompts must be adapted.** Replace `C:\Users\<user>\...` with `/home/<user>/...`. Check every cron prompt from a Windows backup for hardcoded Windows paths before creating the job. The Pinterest cron and other data-file-referencing jobs are common culprits.
- **Missing skills from the Windows backup need to be copied.** If a cron references `writing-style` or another skill that doesn't exist on the Linux target, copy it from the backup's `skills/` directory before creating the cron, or the job will fail on load.

## Verification Checklist

### Full Migration (rsync --delete)
- [ ] Repo cloned successfully
- [ ] Skills count matches backup (53 in the example above)
- [ ] Cron jobs.json is valid JSON with expected job count
- [ ] Memories (MEMORY.md, USER.md) restored
- [ ] Kanban workspaces restored
- [ ] Config set up (if needed)
- [ ] Cron handoff confirmed with user (old machine disabled before new one enabled)
- [ ] Backup repo clone removed from /tmp

### Partial Migration (cron-only)
- [ ] Backup repo cloned and inspected
- [ ] For each imported cron: Windows paths adapted to Linux
- [ ] For each imported cron: referenced skills exist locally or copied from backup
- [ ] All imported crons are paused (state shows `paused`)
- [ ] User notified the list is ready for them to review
