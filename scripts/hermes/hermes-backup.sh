#!/usr/bin/env bash
# Weekly Hermes backup script, pushes config, skills, cron, memories, kanban to GitHub
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

# Create subdirectories
mkdir -p "$BACKUP_DIR/config" "$BACKUP_DIR/cron/output" "$BACKUP_DIR/memories" "$BACKUP_DIR/kanban/workspaces" "$BACKUP_DIR/scripts"

# Sync essentials (exclude cache/logs/media)
rsync -a --delete "$HERMES_HOME/config.yaml" "$BACKUP_DIR/config/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/.env" "$BACKUP_DIR/config/" 2>/dev/null || true
rsync -a --delete --exclude=.git "$HERMES_HOME/skills/" "$BACKUP_DIR/skills/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/cron/jobs.json" "$BACKUP_DIR/cron/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/cron/output/" "$BACKUP_DIR/cron/output/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/memories/" "$BACKUP_DIR/memories/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/kanban/workspaces/" "$BACKUP_DIR/kanban/workspaces/" 2>/dev/null || true
rsync -a --delete "$HERMES_HOME/scripts/" "$BACKUP_DIR/scripts/" 2>/dev/null || true

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