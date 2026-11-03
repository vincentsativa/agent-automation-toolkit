#!/usr/bin/env bash
# Hermes Post-Update Repair (WSL side)
# Fixes the python environment + desktop build after a half-broken `hermes update`.
# Run: bash ~/.hermes/fix-after-update.sh
set -euo pipefail

HERMES="$HOME/.hermes"
UV="$HERMES/bin/uv"
DESKTOP_EXE="$HERMES/hermes-agent/apps/desktop/release/linux-unpacked/Hermes"

# --- Resolve the LIVE python environment (PM-managed; the hash changes on rebuild) ---
VENV="$(python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('$HERMES/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])" 2>/dev/null || true)"
if [ -z "$VENV" ]; then
    echo "FAILED - no installs/*/facts.json found under $HERMES"
    echo "Cannot locate the managed environment. Aborting."
    exit 1
fi
VENV_PY="$VENV/bin/python"

echo "============================================"
echo " Hermes Post-Update Repair (WSL)"
echo "============================================"
echo "Environment: $VENV"
echo

echo "[1/3] Checking Python dependencies..."
if [ ! -x "$VENV_PY" ]; then
    echo "  FAILED - interpreter missing at $VENV_PY"
    exit 1
fi
if "$VENV_PY" -c "import fastapi,uvicorn,pydantic,openai,yaml,dotenv,rich" 2>/dev/null; then
    echo "  OK - dependencies healthy"
else
    echo "  BROKEN - reinstalling dependencies..."
    if "$UV" pip install -e "$HERMES/hermes-agent" --python "$VENV_PY" \
       && "$VENV_PY" -c "import fastapi,uvicorn,pydantic,openai,yaml,dotenv,rich" 2>/dev/null; then
        echo "  OK - dependencies repaired"
    else
        echo "  FAILED - could not repair dependencies"
        FAILED=1
    fi
fi
echo

echo "[2/3] Checking desktop app build..."
if [ -x "$DESKTOP_EXE" ]; then
    echo "  OK - desktop app present"
else
    echo "  MISSING - rebuilding desktop app..."
    cd "$HERMES"
    REBUILT=""
    for attempt in 1 2 3; do
        [ -n "$REBUILT" ] && break
        echo "  attempt $attempt - running build"
        if "$VENV_PY" -m hermes_cli.main desktop --build-only && [ -x "$DESKTOP_EXE" ]; then
            REBUILT=1
        else
            echo "  attempt $attempt - build failed, repairing venv and retrying"
            "$UV" pip install -e "$HERMES/hermes-agent" --python "$VENV_PY" || true
        fi
    done
    if [ -n "$REBUILT" ]; then
        echo "  OK - desktop app rebuilt"
    else
        echo "  FAILED - could not rebuild desktop app"
        FAILED=1
    fi
fi
echo

echo "[3/3] Verifying CLI..."
if "$VENV_PY" -c "import dotenv" 2>/dev/null; then
    echo "  OK - CLI imports healthy"
else
    echo "  FAILED - CLI still broken"
    FAILED=1
fi
echo
echo "============================================"
if [ -n "${FAILED:-}" ]; then
    echo " One or more checks FAILED. Re-run this"
    echo " after closing all Hermes windows/gateways."
    echo "============================================"
    exit 1
fi
echo " Done."
echo "============================================"
