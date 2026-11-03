---
name: hermes-github-backup
description: >-
  Back up Hermes Agent configuration and data to a private GitHub repository.
  Covers config.yaml, .env, skills/*, cron/, memories/, kanban/ — excludes
  rebuildable cache, logs, media, checkpoints.
version: 1.1.0
author: Hermes Agent
---

# Hermes → GitHub Backup

Back up the essential Hermes Agent state to a private GitHub repo so you can
recover from WSL rebuild, machine migration, or accidental data loss.

## When To Use

- You're setting up Hermes on a new machine and need to restore
- You want a remote offsite copy of your Hermes config, skills, cron jobs, and memories
- You're about to do a destructive operation (OS reinstall, disk wipe) and need a snapshot
- A cron backup job is failing and you need to diagnose and fix it

## Prerequisites

- A GitHub Personal Access Token with these permissions:
  - **Repository permissions:** `Contents: Read and write`
  - **Account permissions:** `Repositories: Create` (to create the backup repo)
- A backup target (new or existing repo under your GitHub account)

## Step-by-Step

### 1. Install `gh` CLI (if missing)

```bash
curl -sL "https://github.com/cli/cli/releases/download/v2.67.0/gh_2.67.0_linux_amd64.tar.gz" -o /tmp/gh.tar.gz
tar -xzf /tmp/gh.tar.gz -C /tmp/
mkdir -p ~/.local/bin
cp /tmp/gh_*/bin/gh ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

Add `~/.local/bin` to `~/.bashrc` if not already there:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### 2. Authenticate with GitHub

```bash
echo "<YOUR_PAT>" | gh auth login --with-token
gh auth status
```

**Pitfall:** Fine-grained PATs show `Scopes: NONE` in API response headers — this is normal. They use explicit resource-level permissions, not OAuth scopes.

### 3. Set Up Git Identity & Credential Store

```bash
git config --global user.name "vincentsativa"
git config --global user.email "your@email.com"
git config --global credential.helper store

# Read token from gh config and store in git credentials
python3 -c "
import yaml
with open('~/.config/gh/hosts.yml') as f:
    d = yaml.safe_load(f)
token = d['github.com']['oauth_token']
print(f'https://USERNAME:{token}@github.com')
" >> ~/.git-credentials
```

### 4. Create Backup Repo

If the repo doesn't exist yet, create it via the REST API (fine-grained PATs
can't use `gh repo create` which uses GraphQL):

```bash
TOKEN=$(grep oauth_token ~/.config/gh/hosts.yml | awk '{print $2}')
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"name": "wsl-hermes-backup", "private": true, "description": "Hermes Agent backup from WSL"}'
```

### 5. Security: Add .gitignore Before Staging

**CRITICAL: Do not push live credentials to GitHub.** The backup dir is a git repo — anything you copy in gets committed. Create a `.gitignore` that blocks sensitive files before staging anything:

```bash
cat > /tmp/hermes-backup/.gitignore << 'EOF'
# Sensitive credentials — never push live keys
config/.env
config/config.yaml

# Hermes internal state (rebuildable)
*.lock
skills/.curator_backups/
skills/.hub/
skills/.bundled_manifest
skills/.curator_state
skills/.usage.json
skills/.usage.json.lock
EOF
```

### 6. Stage Backup Files

Only the **essentials** — skip everything rebuildable. Do NOT copy `.env` or `config.yaml` (they contain live API keys). The `.gitignore` is a safety net, not a substitute for not staging them.

```bash
mkdir -p /tmp/hermes-backup/{config,skills,cron,memories,kanban}
# Do NOT copy .env or config.yaml — they contain live API keys
cp -r ~/.hermes/skills/* /tmp/hermes-backup/skills/
cp ~/.hermes/cron/jobs.json /tmp/hermes-backup/cron/
cp -r ~/.hermes/cron/output /tmp/hermes-backup/cron/
cp ~/.hermes/memories/MEMORY.md /tmp/hermes-backup/memories/
cp ~/.hermes/memories/USER.md /tmp/hermes-backup/memories/
cp -r ~/.hermes/kanban/workspaces /tmp/hermes-backup/kanban/
```

**Excluded by design:**
- `~/.hermes/logs/` — transient
- `~/.hermes/cache/` — rebuildable
- `~/.hermes/checkpoints/` — session snapshots
- `~/.hermes/audio_cache/` — TTS artifacts
- `~/.hermes/media_cache/` — auto-downloaded media
- `~/.hermes/config.yaml` — contains API keys
- `~/.hermes/.env` — contains API keys and tokens
### 6. Push

```bash
cd /tmp/hermes-backup
git init -b main
git add -A
git commit -m "Backup: $(date +%Y-%m-%d)"
git remote add origin https://github.com/YOUR_USER/wsl-hermes-backup.git
git push -u origin main
```

### 7. (Optional) Save Token to .env for curl Fallback

Make sure `~/.hermes/.env` has:
```
GITHUB_TOKEN=your_p...This lets API calls via `requests` or `curl` work without `gh` CLI.

## Restore

```bash
git clone https://github.com/YOUR_USER/wsl-hermes-backup.git /tmp/hermes-restore
cp /tmp/hermes-restore/config/config.yaml ~/.hermes/
cp /tmp/hermes-restore/config/.env ~/.hermes/           # only if keys still valid
cp -r /tmp/hermes-restore/skills/* ~/.hermes/skills/
cp /tmp/hermes-restore/cron/jobs.json ~/.hermes/cron/
cp -r /tmp/hermes-restore/cron/output/* ~/.hermes/cron/output/
cp /tmp/hermes-restore/memories/MEMORY.md ~/.hermes/memories/
cp /tmp/hermes-restore/memories/USER.md ~/.hermes/memories/
cp -r /tmp/hermes-restore/kanban/* ~/.hermes/kanban/
```

## Schedule Weekly Auto-Backup via Cron

Create the backup script at `~/.hermes/scripts/hermes-backup.sh`:

```bash
#!/usr/bin/env bash
# Weekly Hermes backup script — pushes config, skills, cron, memories, kanban to GitHub
set -euo pipefail

BACKUP_DIR=/tmp/hermes-backup
HERMES_HOME="$HOME/.hermes"
REMOTE_URL="https://github.com/YOUR_USER/wsl-hermes-backup.git"

# Clone or pull the existing repo so we have full history
# CRITICAL: never git init a fresh repo in /tmp — it creates a root commit with
# no common ancestor against the remote, so push gets rejected as non-fast-forward.
# Always clone to preserve commit history.
if [ ! -d "$BACKUP_DIR/.git" ]; then
    rm -rf "$BACKUP_DIR"
    git clone -q "$REMOTE_URL" "$BACKUP_DIR"
    cd "$BACKUP_DIR"
    git config user.name "hermes-backup"
    git config user.email "[REDACTED_EMAIL]"
else
    cd "$BACKUP_DIR"
    git config user.name "hermes-backup"
    git config user.email "[REDACTED_EMAIL]"
    git pull -q --rebase origin main 2>/dev/null || true
fi

# Create subdirectories (clone may not have all of them)
mkdir -p "$BACKUP_DIR/config" "$BACKUP_DIR/cron/output" "$BACKUP_DIR/memories" "$BACKUP_DIR/kanban/workspaces"

# Sync essentials (exclude cache/logs/media)
rsync -a --delete "$HERMES_HOME/config.yaml" "$BACKUP_DIR/config/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/.env" "$BACKUP_DIR/config/" 2>/dev/null || true
rsync -a --delete --exclude=.git "$HERMES_HOME/skills/" "$BACKUP_DIR/skills/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/cron/jobs.json" "$BACKUP_DIR/cron/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/cron/output/" "$BACKUP_DIR/cron/output/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/memories/" "$BACKUP_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/kanban/workspaces/" "$BACKUP_DIR/kanban/workspaces/" 2>/dev/null || true

# Copy README if not there
if [ ! -f "$BACKUP_DIR/README.md" ]; then
    cp "$HERMES_HOME/README.md" "$BACKUP_DIR/" 2>/dev/null || true
fi

# Check for changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "No changes since last backup."
    exit 0
fi

git add -A
git commit -q -m "Weekly backup $(date +%Y-%m-%d)"
git push origin main 2>&1
echo "✓ Backup pushed to github.com/YOUR_USER/wsl-hermes-backup"
```

Make executable:
```bash
chmod +x ~/.hermes/scripts/hermes-backup.sh
```

A known-good copy of this script is also at `scripts/hermes-backup.sh` in this skill directory. The template above uses `YOUR_USER` as a placeholder; the script file has the real remote URL hardcoded.

Schedule weekly (no_agent runs script directly — zero LLM cost):
```bash
cronjob action=create name="hermes-weekly-backup" schedule="0 3 * * 0" script="hermes-backup.sh" no_agent=true deliver="local"
```

The `no_agent=true` pattern runs the script directly without an LLM — cheap, silent, just git push on schedule. `deliver="local"` saves output to cron/ but sends nothing to Telegram.

## Before You Begin — Check Existing State

**CRITICAL: Before creating any backup resource (repo, script, cron job), verify it doesn't already exist.**

- **Cron jobs:** Run `cronjob action=list` and grep for "backup" before creating a new one. Duplicate cron jobs with the same name and schedule waste user trust.
- **Repo:** Check `curl -s https://api.github.com/repos/USER/wsl-hermes-backup` before attempting to create it. A 422 "name already exists" means it's already there.
- **Script:** Check `ls ~/.hermes/scripts/hermes-backup.sh` before writing a new one.
- **System state:** Never speculate about what another machine or agent has or needs. If you can't verify it with tools, say "I don't know" — don't invent plausible answers.

## Backing Up Arbitrary Data Folders (Create-or-Clone Script Pattern)

Daily backups of desktop/project folders to a dedicated private repo. Use a **create-or-clone** script:

1. **Tries `git clone` first** — if the repo already exists, clone it (preserves history, avoids the non-fast-forward root-commit trap).
2. **If the repo is missing, create it via API:** `POST /user/repos` (private). Then `git init` locally and push to `master` (`git init` defaults to `master`; the API creates an empty remote).
3. **Push to branch `master`, not `main`** (the `git init` default when using this create-or-clone pattern).
4. **Uses a CLEAN remote URL + credential store** — never embed the token in the remote URL. The credential helper (`git config credential.helper store`) supplies auth on push.
5. **Reads `GITHUB_TOKEN` from `~/.hermes/.env` for API calls only** — not for git auth.
6. **Sync with `rsync -a --delete`** to mirror deletions.
7. **Output is minimal** — just "backup complete".

## Change Briefs Pipeline

A pipeline that turns 7 days of backup diffs into dated, ordered change briefs that other agents apply:

1. **Collector script** diffs the `linux-hermes-backup` repo over the last 7 days.
2. **Agent cron** curates the diffs into WHAT / WHY / HOW-TO-REPLICATE sections.
3. **Push a dated brief** to the `agent-change-briefs` repo.
4. **Other agents clone and apply** the briefs in order.

## GitHub Access: Token, Never the Web Browser (Vinny's Standing Rule)

For ALL GitHub operations in this workflow, authenticate with the token via the `gh` CLI or `git` over HTTPS — never open a web browser / never drive the browser UI to read or modify a repo. Vinny flags browser-based GitHub access as wrong. When he asks "why are you trying to access github via web instead of token," the expectation is that you use the already-configured token credentials.

This box is set up correctly already:
- `gh` is logged in as `vincentsativa` with a stored token (`gh auth status` → active account, protocol https)
- `git config credential.helper` is `store`, so clones/pushes authenticate with the token automatically — no browser login, no curl-to-web, no manual password prompts

**When reading crons from the backup repo (the reverse direction — Vinny emails tasks to pull/sync cron definitions out of `linux-hermes-backup`):** use `gh repo clone vincentsativa/linux-hermes-backup` or `git clone` (both token-authenticated), inspect the files locally, then copy what's missing into `~/.hermes/cron/`. When adding copied crons: keep them PAUSED, pin them to the model Vinny specifies, fix file paths to match our system, and change any "Bill" references to "Frank". Leave the model settings alone. Notify Vinny on Telegram explaining the changes. Do not modify the repo — copy only.

## Instabox Backup Repo (`vincentsativa/instabox-Hermes-agent`)

The instabox sandbox has its own Hermes install that backs up to `vincentsativa/instabox-Hermes-agent` (private, branch `main`), separate from `windows-hermes-backup`. Its build script is `/data/home/.hermes/skills/productivity/instabox-backup/scripts/build_backup.py` inside the box and produces the staging tree at `/data/home/.hermes/cache/scratch/instabox-Hermes-agent`.

**The box pushes this repo itself now.** As of 2026-10-30 the box's `GITHUB_TOKEN` in `/data/home/.hermes/.env` has Contents: Read and write on `vincentsativa/instabox-Hermes-agent`, `gh` is authenticated there as `vincentsativa`, and `~/.git-credentials` holds the same token. One command does the whole job inside the box: `bash ~/.hermes/skills/productivity/instabox-backup/scripts/push_backup.sh`. It rebuilds, commits only when the tree changed, pushes to `main`, and prints the remote head read back from the API. `no changes since last backup` is a success. Trigger it over the instabox exec API, never by hand-copying files around.

**Do not push this repo from the WSL host.** Two tokens exist here and they are not the same credential: `~/.config/gh/hosts.yml` (the `gh` CLI token) is scoped to `windows-hermes-backup` and 404s on the instabox repo, while `GITHUB_TOKEN` in `~/.hermes/.env` has admin on it. Use the local token only to READ or VERIFY the repo, for example `GET /repos/vincentsativa/instabox-Hermes-agent/commits/main` and `GET /git/trees/main?recursive=1`, and to prove a push landed the same way any external write is proven.

The failure mode that used to block the box, so it is recognized if a token is ever rotated: a fine-grained PAT with `Selected repositories` can create a repo and still 404 on it afterwards, because a new repo is not added to the token's selection. Symptoms are `GET /repos/{owner}/{repo}` returning 404 while `GET /user` returns 200, and git saying `Write access to repository not granted`. The fix is adding the repo to the token's Repository access with Contents: Read and write.

If a push from the box is ever impossible and a fallback is genuinely needed: rebuild in the box with `build_backup.py`, `tar czf` the staging tree, pull it with the files API into a `mktemp -d` dir, then commit and push from WSL with the `.env` token (the local credential store already holds it, so a plain `git push -u origin main` authenticates). Never paste a token into a remote URL, and never hand a repo-writing credential to a machine without Vinny's explicit order.

## Pitfalls

- **Fine-grained PAT needs "Repositories: Create"** under Account permissions. If `gh repo create` or `POST /user/repos` returns 403, this is the missing permission.
- **A fine-grained PAT can never fork someone else's public repo, so do not route a contribution through a fork on this box.** Forking requires `administration=write` on the PARENT repo, which is un-grantable for a repo the user does not own. The response is a flat `403 Resource not accessible by personal access token`, and the diagnostic is the accepted-permissions header on the refused call:
  ```bash
  gh api -i -X POST repos/<owner>/<repo>/forks 2>&1 | grep -i "x-accepted-github-permissions"
  # administration=write,contents=read   <- the required permission, which cannot be granted
  ```
  A classic PAT with `public_repo` scope would fork; a fine-grained PAT cannot. Distinguish the two before spending any time on token workarounds, and read `403` plus that header as a hard capability limit rather than a config gap. The correct move is ONE line naming the limit and handing it to the user, because the unblocking step needs their identity. Do not burn turns enumerating permissions, retrying shapes, or testing write endpoints to confirm what the header already stated.
- **Never claim a GitHub action succeeded from a CLI success message alone.** Read the created ref back (the repo, branch, PR number) and confirm it resolves, the same as any other external write.
- **Don't back up the token itself** — the `.env` file goes to GitHub. If you push it, rotate the token. Best practice: push `.env` with a placeholder and store the real token elsewhere. See `references/credential-leak-remediation.md` for the purge procedure if you accidentally push live keys.
- **.git-credentials in the backup** — don't include it. Keep credentials out of the repo.
- **Large .hermes/ directories (~5GB)** — only the essentials are ~50MB. Speed up backups by always using the exclusion list.
- **Windows/WSL path differences** — if restoring to a different OS, paths in cron jobs and config may need adjustment.
- **skills/ is itself a git repo** — `rsync` without `--exclude=.git` copies the `.git` directory into the backup, which git then treats as a submodule (mode 160000) instead of tracking the skill files as normal files. Always use `--exclude=.git` on the skills rsync.
- **Branch name mismatch on fresh init** — `git init` creates `master` by default, but the remote uses `main`. Always use `git init -b main` to set the correct initial branch name.
- **/tmp/ gets wiped on reboot** — never `git init` a fresh repo in `/tmp`. It creates a root commit with no common ancestor against the remote, so the push gets rejected as non-fast-forward. The rebase silently fails (swallowed by `2>/dev/null || true`) and `set -euo pipefail` kills the script on the push error. The fix: `git clone` the existing remote instead of init. This preserves full commit history and pushes work cleanly. See the script template above.
- **Force-push is a band-aid, not a fix** — if you hit the non-fast-forward rejection, do not `git push --force`. That rewrites remote history and loses prior backups. Delete `/tmp/hermes-backup` entirely and let the script re-clone from the remote. The clone-based script handles this automatically.