#!/usr/bin/env bash
# x-algorithm update watcher
# Checks xai-org/x-algorithm for new commits and releases since last run.
# Silent on no change. Outputs a Telegram-ready alert when something moved.

REPO="xai-org/x-algorithm"
STATE_FILE="$HOME/.hermes/scripts/x-algorithm-state.txt"
API="https://api.github.com/repos/$REPO"

# Ensure state file exists
mkdir -p "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"

OLD_SHA=$(cat "$STATE_FILE" 2>/dev/null | head -1)

# Fetch latest commit on main
LATEST=$(curl -sf "$API/commits?sha=main&per_page=1" 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$LATEST" ]; then
  echo "x-algorithm check: could not reach GitHub API. Will retry next Sunday."
  exit 0
fi

NEW_SHA=$(echo "$LATEST" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['sha'])" 2>/dev/null)
NEW_DATE=$(echo "$LATEST" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['commit']['committer']['date'])" 2>/dev/null)
NEW_MSG=$(echo "$LATEST" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['commit']['message'])" 2>/dev/null)

if [ -z "$NEW_SHA" ]; then
  echo "x-algorithm check: could not parse latest commit. Will retry next Sunday."
  exit 0
fi

# Check for new releases
RELEASE=$(curl -sf "$API/releases/latest" 2>/dev/null)
RELEASE_TAG=""
RELEASE_NAME=""
if [ $? -eq 0 ] && [ -n "$RELEASE" ]; then
  RELEASE_TAG=$(echo "$RELEASE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name',''))" 2>/dev/null)
  RELEASE_NAME=$(echo "$RELEASE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name',''))" 2>/dev/null)
fi

# First run: just store the SHA, don't alert
if [ -z "$OLD_SHA" ]; then
  echo "$NEW_SHA" > "$STATE_FILE"
  exit 0
fi

# No change
if [ "$OLD_SHA" = "$NEW_SHA" ]; then
  exit 0
fi

# There is a change. Gather the commits between old and new.
COMMITS_SINCE=$(curl -sf "$API/compare/$OLD_SHA...$NEW_SHA" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$COMMITS_SINCE" ]; then
  AHEAD=$(echo "$COMMITS_SINCE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('ahead_by',0))" 2>/dev/null)
  COMMITS_LIST=$(echo "$COMMITS_SINCE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d.get('commits', []):
    msg = c['commit']['message'].split('\n')[0][:120]
    print('  - ' + msg)
" 2>/dev/null)
else
  AHEAD="?"
  COMMITS_LIST="  - (could not fetch commit list)"
fi

# Save new state
echo "$NEW_SHA" > "$STATE_FILE"

# Build the alert
echo "📡 x-algorithm repo updated"
echo ""
echo "New commits on xai-org/x-algorithm: $AHEAD ahead of last check."
echo ""
echo "Commits:"
echo "$COMMITS_LIST"
echo ""
echo "Latest commit: $NEW_SHA"
echo "Date: $NEW_DATE"
echo "Message: $NEW_MSG"
echo ""
if [ -n "$RELEASE_TAG" ]; then
  echo "Latest release: $RELEASE_TAG - $RELEASE_NAME"
  echo "Releases: https://github.com/$REPO/releases"
fi
echo ""
echo "Repo: https://github.com/$REPO"
echo ""
echo "If the params module or weight values landed, patch x-algorithm-post-optimization with the real constants."