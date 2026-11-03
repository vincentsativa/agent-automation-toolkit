#!/usr/bin/env bash
# Daily backup of Vinny's TODAYS DATA FILES folder to the private backup repo.
# Mirrors Bill's daily-data-backup.sh, adapted to Frank (WSL) paths.
set -euo pipefail

SRC="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES"
REPO_DIR="/tmp/daily-data-backup"
REMOTE_URL="https://github.com/vincentsativa/linux-hermes-backup.git"
BRANCH="main"

if [ ! -d "$SRC" ]; then
    echo "Source folder not found: $SRC"
    exit 1
fi

# Clone or pull the repo (fresh clone each run keeps it clean and simple)
if [ -d "$REPO_DIR/.git" ]; then
    cd "$REPO_DIR"
    git pull -q --rebase origin "$BRANCH" 2>/dev/null || true
else
    rm -rf "$REPO_DIR"
    git clone -q "$REMOTE_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

git config user.name "hermes-backup"
git config user.email "[REDACTED_EMAIL]"

# Sync today's data files into a dated subfolder
DEST="$REPO_DIR/daily-data-files/$(date +%Y-%m-%d)"
mkdir -p "$DEST"
rsync -a --delete "$SRC/" "$DEST/"

if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "No changes since last backup."
    exit 0
fi

git add -A
git commit -q -m "Daily data files backup $(date +%Y-%m-%d)"
git push origin "$BRANCH" 2>&1
echo "✓ Daily data files backed up to $REMOTE_URL"
