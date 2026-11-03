#!/usr/bin/env bash
# refill_check.sh - measure the sendable prospect pool and say whether a refill
# is due. Cheap and deterministic: this is the SCRIPT half. The heavy refill
# (source -> scan -> harvest -> clean) is done by the agent following the
# prospect-refill skill, because it takes a long time and the Windows side is
# not always on. Run by the Hermes cron "PROSPECT POOL REFILL".
#
# Threshold 200 -> 100 on 2026-10-11: the BUYER channel was throttled 100 -> 30
# staged/day so the agency/partner channel could take the volume, and a 200
# threshold would fire the heavy refill every single night while draining a 30/day
# budget. 100 sendable is ~3 days of buffer at the new rate.
#
# 2026-10-30, two defects in this script made it report a healthy pool for eight
# nights while the pool drained from 285 to 20:
#   1. bare `python3` resolved to a Python without `requests` (the same failure
#      the daily script pinned /usr/bin/python3 for on 2026-10-22).
#      clean_prospects.py died at import every night.
#   2. the count was read with `wc -l` on prospects_master_clean.csv, and the
#      only guard was that the file EXISTS - so a crashed run re-counted the
#      Oct 20 file (285 rows) and printed POOL HEALTHY on top of it.
# Now: the interpreter is pinned, the old file is deleted before the run, and a
# missing file is a FAILURE, never a count.
set -uo pipefail
cd ~/money_ideas || { echo "REFILL CHECK: money_ideas not found"; exit 0; }

REFILL_AT="${REFILL_AT:-100}"
PY="${PY:-/usr/bin/python3}"
if ! "$PY" -c "import requests" >/dev/null 2>&1; then
  printf 'REFILL CHECK ABORTED: interpreter %s cannot import requests, so nothing was measured.\n' "$PY"
  exit 0
fi

rm -f prospects_master_clean.csv
"$PY" clean_prospects.py --contacts contacts_master.csv --scan scan_master.csv \
        --state state.json --out prospects_master >/tmp/refill_clean.out 2>&1
if [ ! -f prospects_master_clean.csv ]; then
  echo "REFILL CHECK FAILED: clean_prospects.py produced no list this run."
  tail -3 /tmp/refill_clean.out
  exit 0
fi
SENDABLE=$(( $(wc -l < prospects_master_clean.csv) - 1 ))
BREAKDOWN="$(grep -m1 '^sendable breakdown:' /tmp/refill_clean.out || true)"

if [ "$SENDABLE" -lt "$REFILL_AT" ]; then
  echo "REFILL NEEDED: ${SENDABLE} sendable person addresses, below the ${REFILL_AT} threshold."
  [ -n "$BREAKDOWN" ] && echo "$BREAKDOWN"
  echo "Follow the prospect-refill skill to source, scan, harvest and clean a new batch, then report the new count."
else
  echo "POOL HEALTHY: ${SENDABLE} sendable (threshold ${REFILL_AT}). No refill needed."
  [ -n "$BREAKDOWN" ] && echo "$BREAKDOWN"
fi
