#!/usr/bin/env bash
# dir_harvest_instabox.sh - run the partner DIRECTORY contact harvest on InstaBox,
# woken from this machine.
#
# WHY (approved by Vinny 2026-11-02): step 4 of partner_directory_refill.sh was the
# only heavy part of that job - four local find_contacts.py workers against ~420
# domains, which ran 18:00 -> ~18:46 and once hit the 90-minute cron timeout
# (2026-10-25). The workers now run on the box and this machine only drives them.
# Measured 2026-10-30, same batch: 4 local workers = 32 domains/min, 16 threads on
# the box = 67 domains/min at load average 0.04 - it is bound by other people's web
# servers, not by CPU.
#
# THE BOX CANNOT HOLD THE SCHEDULE. Free tier: self-pauses after 30 idle minutes,
# a run is capped at 480 minutes. The Hermes cron in WSL stays the clock and this
# script WAKES the box every single run. Never assume it is already running.
#
# Usage:
#   dir_harvest_instabox.sh --file dir_todo_contacts.txt --out dircontacts \
#                           [--threads 32] [--max-min 40] [--machine m_xxx]
#
# Writes <out>_part1.csv and <out>_final.csv locally, same columns as harvest.sh,
# so the caller merges with csv_append.py exactly as before.
#
# Exit codes (the caller falls back to the local harvest.sh on 2):
#   0  harvested, <out>_final.csv written
#   2  box not usable this run (unreachable / cooldown / cannot start / no CSV back)
#   3  bad invocation
#   6  <out>_final.csv written but the wait was capped, so the run was cut short
set -uo pipefail

PY=/usr/bin/python3
KEYFILE="${KEYFILE:-~/.config/phantombyte/instabox.env}"
BASE="https://api.instabox.sh"
REMOTE=/data/workspace/harvest

FILE=""
OUT="dircontacts"
THREADS="${THREADS:-32}"
MAX_MIN="${HARVEST_MAX_MIN:-40}"
WAKE_MAX="${HARVEST_WAKE_MAX:-180}"
MACHINE="${INSTABOX_MACHINE:-}"

while [ $# -gt 0 ]; do
  case "$1" in
    --file)    FILE="$2"; shift 2 ;;
    --out)     OUT="$2"; shift 2 ;;
    --threads) THREADS="$2"; shift 2 ;;
    --max-min) MAX_MIN="$2"; shift 2 ;;
    --machine) MACHINE="$2"; shift 2 ;;
    -h|--help) sed -n '3,28p' "$0"; exit 0 ;;
    *) printf 'unknown argument: %s\n' "$1" >&2; exit 3 ;;
  esac
done

line() { printf '%s\n' "$1"; }

if [ -z "$FILE" ] || [ ! -s "$FILE" ]; then
  line "INSTABOX DIR HARVEST: no domain list (${FILE}). Nothing done."
  exit 3
fi
if [ ! -s "$KEYFILE" ]; then
  line "INSTABOX DIR HARVEST: no API key at ${KEYFILE}."
  exit 2
fi
KEY="$(sed -n 's/^INSTABOX_API_KEY=//p' "$KEYFILE" | head -1)"
[ -n "$KEY" ] || { line "INSTABOX DIR HARVEST: ${KEYFILE} has no INSTABOX_API_KEY."; exit 2; }

api_get() { curl -sS -m 60 -H "X-API-Key: $KEY" "$BASE$1"; }
api_exec_on() {   # api_exec_on MACHINE CMD TIMEOUT
  local body; body="$(mktemp)"
  "$PY" -c 'import json,sys;print(json.dumps({"cmd":sys.argv[1],"timeoutSeconds":int(sys.argv[2])}))' \
        "$2" "$3" > "$body"
  curl -sS -m 120 -X POST -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
       --data-binary @"$body" "$BASE/v1/machines/$1/exec"
  rm -f "$body"
}
api_post_empty() {  # api_post_empty PATH IDEMPOTENCY_KEY
  local body; body="$(mktemp)"; printf '{}' > "$body"
  curl -sS -m 120 -X POST -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
       -H "Idempotency-Key: $2" --data-binary @"$body" "$BASE$1"
  rm -f "$body"
}
jget() {  # jget dotted.path  (reads JSON on stdin, prints "" when absent)
  "$PY" -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); raise SystemExit(0)
v = d
for k in sys.argv[1].split("."):
    if not isinstance(v, dict):
        v = None; break
    v = v.get(k)
if isinstance(v, (dict, list)):
    v = json.dumps(v)
print("" if v is None else v)' "$1"
}

# ------------------------------------------------------- 0. which machine
if [ -z "$MACHINE" ]; then
  LIST="$(api_get /v1/machines)"
  MACHINE="$(printf '%s' "$LIST" | "$PY" -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
ms = d.get("machines") or d.get("data") or ([] if isinstance(d, dict) else d)
for m in ms or []:
    if m.get("state") not in ("deleting", "error"):
        print(m.get("id", "")); break')"
fi
[ -n "$MACHINE" ] || { line "INSTABOX DIR HARVEST: no machine reachable with this key. Nothing done."; exit 2; }

state_of() { api_get "/v1/machines/$MACHINE" | jget state; }

# --------------------------------------------------------------- 1. wake
# Never assume it is up. Idle pause takes it after 30 minutes; a stopped or
# suspended machine answers machine_not_running, so it has to be resumed. A
# machine that hit its 480-minute cap answers machine_cooldown with a 5-20 minute
# retry; that is longer than this job is worth waiting, so the caller falls back.
wake() {
  local st waited=0 last_resume=-15 code resp
  while [ "$waited" -lt "$WAKE_MAX" ]; do
    st="$(state_of)"
    case "$st" in
      running) line "  box: ${MACHINE} running${WOKE:+ (woken in ${waited}s)}"; return 0 ;;
      error|deleting) line "  box: ${MACHINE} is ${st}, cannot use it this run"; return 2 ;;
      suspended|stopped)
        if [ $(( waited - last_resume )) -ge 15 ]; then
          resp="$(api_post_empty "/v1/machines/$MACHINE/resume" "resume-${MACHINE}-$(date +%s%N)")"
          code="$(printf '%s' "$resp" | jget error.code)"
          last_resume="$waited"; WOKE=1
          case "$code" in
            ""|operation_conflict) : ;;
            machine_cooldown)
              line "  box: cooling down after a long run ($(printf '%s' "$resp" | jget error.retryAfterSeconds) s) - not waiting that out"
              return 2 ;;
            *) line "  box: resume refused (${code})"; return 2 ;;
          esac
        fi ;;
    esac
    sleep 5; waited=$(( waited + 5 ))
  done
  line "  box: still ${st:-unknown} after ${WAKE_MAX}s"
  return 2
}

line "INSTABOX DIR HARVEST  $(date '+%Y-%m-%d %H:%M')"
line "domains: $(grep -cve '^\s*$' "$FILE")   threads: ${THREADS}   max wait: ${MAX_MIN} min"
wake || exit 2

SMOKE="$(api_exec_on "$MACHINE" "python3 -c 'import requests' && echo PYOK" 90 | jget stdout)"
case "$SMOKE" in
  *PYOK*) : ;;
  *) line "  box: python3 there cannot import requests - not starting a worker that would die"; exit 2 ;;
esac

# ------------------------------------------------------- 2. upload + start
TAG="$(date +%F_%H%M)"
curl -sS -m 120 -X PUT -H "X-API-Key: $KEY" --data-binary @"$HOME/money_ideas/find_contacts.py" \
     "$BASE/v1/machines/$MACHINE/files?path=${REMOTE}/find_contacts.py&parents=true" >/dev/null
curl -sS -m 120 -X PUT -H "X-API-Key: $KEY" --data-binary @"$FILE" \
     "$BASE/v1/machines/$MACHINE/files?path=${REMOTE}/dir_domains_${TAG}.txt&parents=true" >/dev/null

CMD="cd ${REMOTE} && rm -f out_dir_${TAG}.csv h_dir_${TAG}.log && nohup python3 find_contacts.py --file dir_domains_${TAG}.txt --out out_dir_${TAG}.csv --workers ${THREADS} --no-osm-autoload > h_dir_${TAG}.log 2>&1 & echo STARTED"
STARTED="$(api_exec_on "$MACHINE" "$CMD" 60 | jget stdout)"
case "$STARTED" in
  *STARTED*) line "  box: harvesting $(grep -cve '^\s*$' "$FILE") domains on ${THREADS} threads" ;;
  *) line "  box: would not start ($(printf '%s' "$STARTED" | cut -c1-160))"; exit 2 ;;
esac

# --------------------------------------------------------------- 3. wait
# The pattern is bracketed so the exec shell running it cannot match itself,
# which is what makes a plain "pgrep -f find_contacts.py" never reach zero.
DEADLINE=$(( $(date +%s) + MAX_MIN * 60 ))
CAPPED=0
while :; do
  sleep 30
  ALIVE="$(api_exec_on "$MACHINE" 'ps -eo args= | grep -c "[f]ind_contacts.py"' 60 | jget stdout | tr -dc '0-9')"
  [ -n "$ALIVE" ] || ALIVE=0
  printf '%s alive=%s\n' "$(date +%H:%M:%S)" "$ALIVE" >> /tmp/dir_harvest_instabox.log
  [ "$ALIVE" -eq 0 ] && break
  if [ "$(date +%s)" -gt "$DEADLINE" ]; then CAPPED=1; break; fi
done

# ----------------------------------------------------------- 4. pull + merge
RAW=/tmp/dir_box_out_${TAG}.raw
curl -sS -m 180 -H "X-API-Key: $KEY" \
     "$BASE/v1/machines/$MACHINE/files/content?path=${REMOTE}/out_dir_${TAG}.csv" -o "$RAW"

# Only the part files written by THIS run may reach the merge, so a stale part
# from an earlier local run can never inflate _final.csv.
rm -f "${OUT}"_part*.csv

if "$PY" - "$OUT" "$RAW" <<'PY'
import json, sys
prefix, raw_path = sys.argv[1], sys.argv[2]
raw = open(raw_path, encoding='utf-8', errors='replace').read()
text = raw
try:
    d = json.loads(raw)
except json.JSONDecodeError:
    d = None
if isinstance(d, dict):
    if d.get('error'):
        sys.exit(1)
    for k in ('content', 'data', 'text'):
        if isinstance(d.get(k), str):
            text = d[k]; break
if 'domain' not in text.split('\n', 1)[0]:
    sys.exit(1)
open(f'{prefix}_part1.csv', 'w').write(text if text.endswith('\n') else text + '\n')
PY
then
  :
else
  line "  box: no readable CSV came back. Last lines of the box log:"
  api_exec_on "$MACHINE" "tail -6 h_dir_${TAG}.log" 60 | jget stdout | sed 's/^/    /'
  [ "$CAPPED" = "1" ] || exit 2
fi

if [ "$CAPPED" = "1" ]; then
  api_exec_on "$MACHINE" "pkill -f 'find_contacts.py --file dir_domains_${TAG}.txt' || true" 60 >/dev/null
fi

if [ -s "${OUT}_part1.csv" ]; then
  # Same merge contract as harvest.sh: dedupe on domain, rank a person above a
  # role box, sort deterministically. Nothing is invented for a domain that
  # produced no row.
  "$PY" - "$OUT" <<'PYEOF'
import csv, sys
prefix = sys.argv[1]
FIELDS = ["domain", "email", "person", "kind", "source_url", "note"]
order = {"person": 0, "role": 1, "osm": 2, "none": 3, "skip": 4}
seen = {}
with open(f"{prefix}_part1.csv", newline="") as fh:
    for r in csv.DictReader(fh):
        d = (r.get("domain") or "").strip().lower()
        if d and d not in seen:
            seen[d] = {k: r.get(k, "") for k in FIELDS}
rows = sorted(seen.values(), key=lambda r: (order.get(r["kind"], 9), r["domain"]))
out = f"{prefix}_final.csv"
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
got = sum(1 for r in rows if r["email"].strip())
by = {}
for r in rows:
    if r["email"].strip():
        by[r["kind"]] = by.get(r["kind"], 0) + 1
print(f"merged -> {out}")
print(f"  domains: {len(rows)}")
print(f"  with an address: {got}")
for k in ("person", "role", "osm"):
    if k in by:
        print(f"    {k}: {by[k]}")
PYEOF
fi

if [ ! -s "${OUT}_final.csv" ]; then
  line "INSTABOX DIR HARVEST: nothing merged. Pool unchanged."
  [ "$CAPPED" = "1" ] && exit 6
  exit 2
fi

if [ "$CAPPED" = "1" ]; then
  line "INSTABOX DIR HARVEST: wait capped at ${MAX_MIN} min - domains not reached were not harvested."
  exit 6
fi
exit 0
