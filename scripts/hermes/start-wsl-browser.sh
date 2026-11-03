#!/usr/bin/env bash
# Start the WSL-local headless Chromium that the browser-use harness connects to.
# Hermes browser_exec connects to it via browser.cdp_url = http://127.0.0.1:9222
# (set in ~/.hermes/config.yaml). The harness daemon only auto-detects Chrome in
# standard profile dirs, so a dedicated automation Chrome on a non-default
# profile MUST be running here for browser work to work.
#
# Usage:
#   ~/.hermes/scripts/start-wsl-browser.sh          # ensure it's running, else start it
#   ~/.hermes/scripts/start-wsl-browser.sh --stop   # stop it
set -u

PORT=9222
CHROME="~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome"
PROFILE="$HOME/.hermes/chrome-debug"
LOG="$HOME/.hermes/logs/wsl-browser.log"

mkdir -p "$HOME/.hermes/logs" "$PROFILE"

if [ "${1:-}" = "--stop" ]; then
    pkill -f "remote-debugging-port=$PORT" 2>/dev/null && echo "stopped browser on :$PORT" || echo "no browser running on :$PORT"
    exit 0
fi

# Already listening? Nothing to do.
if curl -sf "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
    echo "browser already running on :$PORT"
    exit 0
fi

if [ ! -x "$CHROME" ]; then
    echo "ERROR: $CHROME not found. Run: python3 -m playwright install chromium" >&2
    exit 1
fi

nohup "$CHROME" \
    --remote-debugging-port=$PORT \
    --user-data-dir="$PROFILE" \
    --no-first-run --no-default-browser-check --no-sandbox \
    --headless=new about:blank >>"$LOG" 2>&1 &
disown

# Wait up to 10s for the CDP endpoint to come up.
for i in $(seq 1 20); do
    if curl -sf "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
        echo "browser started on :$PORT (headless chromium, profile=$PROFILE)"
        exit 0
    fi
    sleep 0.5
done
echo "ERROR: browser did not come up on :$PORT. See $LOG" >&2
exit 1
