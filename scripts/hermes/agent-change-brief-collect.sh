#!/usr/bin/env bash
# Collector for the WEEKLY AGENT CHANGE BRIEF.
# Pulls the last 7 days of changes to the shared linux-hermes-backup repo
# and emits a diff summary for Frank's other agents (Frank/Pi) to consume.
set -euo pipefail

REPO_DIR="/tmp/hermes-backup"
REMOTE_URL="https://github.com/vincentsativa/linux-hermes-backup.git"
BRANCH="main"

if [ -d "$REPO_DIR/.git" ]; then
    cd "$REPO_DIR"
    git pull -q --rebase origin "$BRANCH" 2>/dev/null || true
else
    rm -rf "$REPO_DIR"
    git clone -q "$REMOTE_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# Emit a git diff of the last 7 days of meaningful changes.
# The consumer (agent) filters noise per its own rules.
git log --since="7 days ago" --oneline --stat -- . \
    ':!.venv' ':!.curator_backups' ':!.curator_state' ':!.bundled_manifest' \
    ':!.usage.json' ':!*.lock' 2>/dev/null | head -200
