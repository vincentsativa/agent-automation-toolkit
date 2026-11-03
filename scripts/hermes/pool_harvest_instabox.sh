#!/usr/bin/env bash
# pool_harvest_instabox.sh - keep the BUYER prospect pool fed by harvesting
# contact addresses on InstaBox machines, triggered from WSL.
#
# Runs the fetch on as many machines as you point it at: it splits the domain
# batch into one slice per machine, starts a harvest on each, waits for all of
# them, pulls every slice back and merges ONCE through csv_append.py (which
# dedupes on domain, so 100 machines cannot duplicate a row).
#
# Env knobs:
#   MACHINES=m_aaa,m_bbb   machines to use. Unset = every machine the key can
#                          see (GET /v1/machines). One machine = old behaviour.
#   HARVEST_N=1200         domains PER MACHINE this run
#   HARVEST_WORKERS=32     find_contacts workers per machine
#   HARVEST_MAX_MIN=55     stop waiting after this long (box max-run is 480 min)
#   DRY=1                  pick the batch and print the split; touch nothing
#
# Measured 2026-10-30, one box, same batch: 4 workers = 32 domains/min,
# 16 workers = 67 domains/min, load average 0.04 - the boxes wait on other
# people's web servers, they are not short of CPU.
#
# What stays on this machine: the RCPT mailbox probe (mail_verify) and any
# sending. What stays out of the machines: a schedule (a free box self-pauses
# after 30 idle min; this script is the clock, woken by a Hermes cron job).
#
# Prints plain lines for the Telegram delivery. Each slice is kept as
# contacts_box_<date>_<n>.csv so a merge can be redone by hand.
set -uo pipefail
cd ~/money_ideas || { echo "INSTABOX HARVEST: money_ideas not found"; exit 0; }

PY="${PY:-/usr/bin/python3}"
KEYFILE="${KEYFILE:-~/.config/phantombyte/instabox.env}"
BASE="https://api.instabox.sh"
N="${HARVEST_N:-1200}"                 # domains per machine
WORKERS="${HARVEST_WORKERS:-32}"
MAX_MIN="${HARVEST_MAX_MIN:-55}"
DRY="${DRY:-0}"
TAG="$(date +%F)"
BODY=/tmp/instabox_body.json
WORKDIR_REMOTE=/data/workspace/harvest

line() { printf '%s\n' "$1"; }
[ -s "$KEYFILE" ] || { line "INSTABOX HARVEST: no API key at $KEYFILE. Nothing done."; exit 0; }
KEY="$(sed -n 's/^INSTABOX_API_KEY=//p' "$KEYFILE" | head -1)"
[ -n "$KEY" ] || { line "INSTABOX HARVEST: $KEYFILE has no INSTABOX_API_KEY. Nothing done."; exit 0; }

api_get() { curl -sS -H "X-API-Key: $KEY" "$BASE$1"; }
api_exec_on() {  # api_exec_on MACHINE CMD TIMEOUT
  "$PY" -c 'import json,sys;print(json.dumps({"cmd":sys.argv[1],"timeoutSeconds":int(sys.argv[2])}))' \
        "$2" "$3" > "$BODY"
  curl -sS -X POST -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
       --data-binary @"$BODY" "$BASE/v1/machines/$1/exec"
}
jget() {
  "$PY" -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: print(""); raise SystemExit(0)
v=d.get(sys.argv[1])
if isinstance(v,dict): v=v.get("code","")
print("" if v is None else v)' "$1"
}

# ----------------------------------------------------------- 0. which machines
if [ -n "${MACHINES:-}" ]; then
  IFS=',' read -r -a BOXES <<< "$MACHINES"
else
  LIST="$(api_get /v1/machines)"
  mapfile -t BOXES < <(printf '%s' "$LIST" | "$PY" -c 'import json,sys
d=json.load(sys.stdin)
ms=d.get("machines") or d.get("data") or ([] if isinstance(d,dict) else d)
for m in ms or []:
    if m.get("state") not in ("deleting","error"):
        print(m.get("id",""))' 2>/dev/null | grep -v '^$')
fi
NBOX=${#BOXES[@]}
[ "$NBOX" -ge 1 ] || { line "INSTABOX HARVEST: no machines reachable with this key. Nothing done."; exit 0; }
WANT=$(( N * NBOX ))

# ---------------------------------------------------------------- 1. the batch
BATCH=/tmp/box_harvest_batch.txt
rm -f "$BATCH"
"$PY" - "$BATCH" "$WANT" <<'PY'
import csv, json, os, sys
os.chdir('~/money_ideas')
sys.path.insert(0, '~/money_ideas')
import prospect_fit as pf
out_path, want = sys.argv[1], int(sys.argv[2])
qualified = {(r.get('domain') or '').strip().lower(): r
             for r in csv.DictReader(open('scan_master.csv'))
             if (r.get('qualified') or '').strip().lower() == 'yes'}
have = {(r.get('domain') or '').strip().lower()
        for r in csv.DictReader(open('contacts_master.csv'))}
contacted = {(d or '').strip().lower()
             for d in (json.load(open('state.json')).get('contacted') or {})}
ranks = pf.load_tranco()
batch = []
for d in qualified:
    if d in have or d in contacted:
        continue
    ok, _why = pf.is_target(d, '', ranks)
    if ok:
        batch.append(d)
    if len(batch) >= want:
        break
open(out_path, 'w').write('\n'.join(batch) + ('\n' if batch else ''))
print(len(batch))
PY
BATCHED="$(wc -l < "$BATCH" 2>/dev/null || echo 0)"
[ "${BATCHED:-0}" -ge 1 ] || { line "INSTABOX HARVEST: no unharvested buyer-fit domains left to hand the boxes."; exit 0; }
PER=$(( (BATCHED + NBOX - 1) / NBOX ))

if [ "$DRY" = "1" ]; then
  line "INSTABOX HARVEST (dry): ${BATCHED} domains over ${NBOX} machine(s), ~${PER} each."
  exit 0
fi

# -------------------------------------------------------------- 2. split + wake
SLICES=()
for _i in $(seq 1 "$NBOX"); do
  SLICES+=("/tmp/box_slice_${_i}.txt")
done
"$PY" - "$BATCH" "${#SLICES[@]}" "${SLICES[@]}" <<'PY'
import sys
src, n, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
doms = [d.strip() for d in open(src) if d.strip()]
hands = [doms[i::n] for i in range(n)]
for path, hand in zip(paths, hands):
    open(path, 'w').write('\n'.join(hand) + ('\n' if hand else ''))
PY

declare -a LIVE=()
for idx in "${!BOXES[@]}"; do
  m="${BOXES[$idx]}"
  st="$(api_get "/v1/machines/$m" | jget state)"
  case "$st" in
    running|suspended) : ;;
    stopped)
      "$PY" -c 'import json;print("{}")' > "$BODY"
      curl -sS -X POST -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
           -H "Idempotency-Key: resume-${m}-$(date +%s%N)" --data-binary @"$BODY" \
           "$BASE/v1/machines/$m/resume" >/dev/null
      sleep 8 ;;
    *) line "  ${m}: ${st:-unreachable}, skipped" ; continue ;;
  esac
  s="${SLICES[$idx]}"
  curl -sS -X PUT -H "X-API-Key: $KEY" --data-binary @"$HOME/money_ideas/find_contacts.py" \
       "$BASE/v1/machines/$m/files?path=${WORKDIR_REMOTE}/find_contacts.py&parents=true" >/dev/null
  curl -sS -X PUT -H "X-API-Key: $KEY" --data-binary @"$s" \
       "$BASE/v1/machines/$m/files?path=${WORKDIR_REMOTE}/slice_${TAG}_${idx}.txt&parents=true" >/dev/null
  CMD="cd ${WORKDIR_REMOTE} && python3 -c 'import requests' && rm -f out_${TAG}_${idx}.csv h_${TAG}_${idx}.log && nohup python3 find_contacts.py --file slice_${TAG}_${idx}.txt --out out_${TAG}_${idx}.csv --workers ${WORKERS} --no-osm-autoload > h_${TAG}_${idx}.log 2>&1 & echo STARTED"
    out="$(api_exec_on "$m" "$CMD" 60 | jget stdout)"
  case "$out" in
    *STARTED*) LIVE+=("$m"); line "  ${m}: ${WORKERS} workers on $(wc -l < "$s") domains" ;;
    *)         line "  ${m}: would not start ($(printf '%s' "$out" | cut -c1-120))" ;;
  esac
done
[ "${#LIVE[@]}" -ge 1 ] || { line "INSTABOX HARVEST: nothing started. Pool unchanged."; exit 0; }

# ------------------------------------------------------------------ 3. wait
DEADLINE=$(( $(date +%s) + MAX_MIN * 60 ))
CAPPED=0
while :; do
  sleep 45
  alive=0
  for m in "${LIVE[@]}"; do
    p="$(api_exec_on "$m" "pgrep -fc find_contacts.py || echo 0" 60 | jget stdout)"
    [ "${p:-0}" != "0" ] && alive=$((alive + 1))
  done
  printf '%s boxes_busy=%s of %s\n' "$(date +%H:%M:%S)" "$alive" "${#LIVE[@]}" >> "/tmp/instabox_harvest_${TAG}.log"
  if [ "$(date +%s)" -gt "$DEADLINE" ]; then CAPPED=1; break; fi
  [ "$alive" = "0" ] && break
done

# ------------------------------------------------------- 4. pull + merge once
TOTAL=0
for m in "${LIVE[@]}"; do
  idx=""
  for j in "${!BOXES[@]}"; do [ "${BOXES[$j]}" = "$m" ] && idx="$j"; done
  LOCAL="contacts_box_${TAG}_${idx}.csv"
  curl -sS -H "X-API-Key: $KEY" \
       "$BASE/v1/machines/$m/files/content?path=${WORKDIR_REMOTE}/out_${TAG}_${idx}.csv" -o /tmp/box_out_${idx}.raw
  if "$PY" - "$LOCAL" "/tmp/box_out_${idx}.raw" <<'PY'
import json, sys
raw = open(sys.argv[2], encoding='utf-8', errors='replace').read()
text = raw
try: d = json.loads(raw)
except json.JSONDecodeError: d = None
if isinstance(d, dict):
    if d.get('error'):
        sys.exit(1)
    for k in ('content', 'data', 'text'):
        if isinstance(d.get(k), str):
            text = d[k]; break
if 'domain' not in text.split('\n', 1)[0]:
    sys.exit(1)
open(sys.argv[1], 'w').write(text if text.endswith('\n') else text + '\n')
PY
  then
    rows=$(( $(wc -l < "$LOCAL") - 1 ))
    person=$(awk -F, 'NR>1 && $2 != "" {print $2}' "$LOCAL" | wc -l)
    TOTAL=$(( TOTAL + rows ))
    line "  ${m}: ${rows} rows, ${person} addresses"
  else
    line "  ${m}: result unreadable, slice not merged"
  fi
done

if [ "$TOTAL" -lt 1 ]; then
  line "INSTABOX HARVEST ${TAG}: nothing returned. Pool unchanged."
  exit 0
fi

cp -f contacts_master.csv "contacts_master.csv.bak-box-${TAG}"
MERGED=0
for f in contacts_box_${TAG}_*.csv; do
  [ -f "$f" ] || continue
  "$PY" csv_append.py --src "$f" --dst contacts_master.csv --key domain >/tmp/merge_${TAG}.out 2>&1
  NEWROWS="$(sed -n 's/.*new: \([0-9]*\).*/\1/p' /tmp/merge_${TAG}.out | head -1)"
  MERGED=$(( MERGED + ${NEWROWS:-0} ))
done
MASTERROWS=$(( $(wc -l < contacts_master.csv) - 1 ))

# ---------------------------------------------------------------- 5. re-clean
rm -f prospects_master_clean.csv
"$PY" clean_prospects.py --contacts contacts_master.csv --scan scan_master.csv \
      --state state.json --out prospects_master >/tmp/box_clean.out 2>&1
if [ -f prospects_master_clean.csv ]; then
  SENDABLE=$(( $(wc -l < prospects_master_clean.csv) - 1 ))
else
  SENDABLE="?"
fi
BREAKDOWN="$(grep -m1 '^sendable breakdown:' /tmp/box_clean.out || true)"

line "INSTABOX HARVEST ${TAG}: ${#LIVE[@]} machine(s), ${BATCHED} domains -> ${TOTAL} rows back, ${MERGED} new pool rows."
[ "$CAPPED" = "1" ] && line "  stopped waiting at ${MAX_MIN} min."
line "  master pool ${MASTERROWS} rows. sendable now: ${SENDABLE}"
[ -n "$BREAKDOWN" ] && line "  ${BREAKDOWN}"
