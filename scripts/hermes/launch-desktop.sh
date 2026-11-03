#!/usr/bin/env bash
# Launch the Hermes desktop app fast.
# Uses --skip-build to reuse the existing packaged build instead of rebuilding.
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

if ! command -v hermes >/dev/null 2>&1; then
  echo "ERROR: 'hermes' not found on PATH" >&2
  exit 1
fi

# Smoke-check the packaged binary is there before launching.
BIN="$HOME/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/Hermes"
if [ ! -x "$BIN" ]; then
  echo "ERROR: packaged desktop app not found at: $BIN" >&2
  echo "Run 'hermes desktop' once to build it, then use this launcher." >&2
  exit 1
fi

echo "Launching Hermes desktop (skip-build)..."

# Run in background so the terminal isn't tied to the app's lifetime.
nohup hermes desktop --skip-build >"$HOME/.hermes/desktop-launcher.log" 2>&1 &
echo "Started. PID $!  (log: ~/.hermes/desktop-launcher.log)"
