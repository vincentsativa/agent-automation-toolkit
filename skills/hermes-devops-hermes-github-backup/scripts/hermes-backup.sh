#!/usr/bin/env bash
# Weekly Hermes backup script — pushes config, skills, cron, memories, kanban to GitHub
# Clone-based: always clones the existing remote to preserve history (never git init).
set -euo pipefail

BACKUP_DIR=/tmp/hermes-backup
HERMES_HOME="$HOME/.hermes"
REMOTE_URL="https://github.com/vincentsativa/wsl-hermes-backup.git"

# Clone or pull the existing repo so we have full history
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

# Write .gitignore to block sensitive files from being committed
cat > "$BACKUP_DIR/.gitignore" << 'GITIGNORE'
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
GITIGNORE

# Sync essentials (exclude cache/logs/media and sensitive files)
# NOTE: config.yaml and .env are intentionally NOT synced — they contain live API keys
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
echo "✓ Backup pushed to github.com/vincentsativa/wsl-hermes-backup"