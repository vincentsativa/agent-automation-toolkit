#!/usr/bin/env bash
# partner_refill.sh - stage the partner/agency batch into the IONOS Scheduled
# folder, sourcing fresh prospects when the pool is short.
#
# Run by the Hermes cron job "PARTNER OUTREACH REFILL" (Mon-Fri 10:30) for a
# SAME-DAY 13:00 send. Same-day (not overnight) on purpose: the buyer job's
# read-back counts the WHOLE Scheduled folder, so the partner batch must be gone
# before the next buyer staging run. Staged 10:30, sent 13:00, gone before the
# next 01:30.
#
# Env knobs:
#   LIMIT=50         how many to SEND (the partner meter is 50/day as of
#                    2026-10-11). Do NOT inflate this to compensate for probe
#                    losses: partner_outreach.py now probes limit+40% in one
#                    call and then keeps the first 50 survivors, so 50 is what
#                    lands. Before 2026-10-21 it sliced to the limit BEFORE the
#                    probe, which is why 19 and 20 Oct both sent 39 of 50.
#   START=...        local send start YYYY-MM-DDTHH:MM; default today 13:00
#   GAP=4            minutes between sends (50 x 4min = 3h20m, 13:00 -> 16:20)
#   METS_PER_RUN=5   fresh metros to source per run when the pool is short
#   DRY=1            render only; stage nothing
#
# RATE CHANGE 2026-10-11 (Vinny): the agency channel is the one that converts
# (43 agencies -> 1 real reply vs ~700 buyer sends -> 0). Meter raised 30 -> 50
# per day.
# METS_PER_RUN 3 -> 5 because 50/day drains the pool faster than 3 metros/run
# can replace it (measured 2026-10-11: only 19 eligible after gates).
#
# Deliberately NOT added to --only-industries: `professional`. It looks tempting
# (it contains tag:office=consulting, which partner_fit() keeps), but measured
# yield says no: a metro yields ~23 it_msp/b2b_agency prospects of which ~7.6
# come with an email, while `professional` adds ~136 domains per metro to scan
# and fetch and contributes about 3. Ten times the Overpass and
# find_contacts.py cost for a tenth of the yield, inside a 10:30 -> 13:00 window.
# The ~60 consulting/agency addresses that are ALREADY scanned live in the buyer
# pool and are imported directly instead (see partner_import_scanned.py).
set -uo pipefail

cd ~/money_ideas || { echo "PARTNER REFILL: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

LIMIT="${LIMIT:-50}"
GAP="${GAP:-4}"
DRY="${DRY:-0}"
METS_PER_RUN="${METS_PER_RUN:-5}"
MASTER_P="partner_prospects_master.csv"
MASTER_S="partner_scan_master.csv"
MASTER_C="partner_contacts_master.csv"
METROS="partner_metros4.txt"
DONE="partner_metros_done.txt"

line() { printf '%s\n' "$1"; }

if [ -z "${START:-}" ]; then
  BASE_DAY="$(date '+%Y-%m-%d')"
  if [ "$(date '+%H%M')" -ge "1230" ]; then
    case "$(date -d 'tomorrow' '+%u')" in
      6) BASE_DAY="$(date -d 'tomorrow +2 days' '+%Y-%m-%d')" ;;
      7) BASE_DAY="$(date -d 'tomorrow +1 day'  '+%Y-%m-%d')" ;;
      *) BASE_DAY="$(date -d 'tomorrow' '+%Y-%m-%d')" ;;
    esac
  fi
  START="${BASE_DAY}T13:00"
fi

line "PARTNER REFILL  $(date '+%Y-%m-%d %H:%M')"
line "limit: ${LIMIT}  start: ${START}  gap: ${GAP}"

# 0. Harvest bounces first so a dead partner mailbox is suppressed before staging.
BOUNCE_OUT="$(python3 harvest_bounces.py 2>&1 || true)"
BL="$(printf '%s\n' "$BOUNCE_OUT" | grep -m1 -E '^(Suppressed|Would suppress):' || true)"
[ -n "$BL" ] && line "bounces: ${BL}"

# 1. Seed the master pool from the first pack, once.
if [ ! -f "$MASTER_P" ]; then
  cp partner_prospects_2026-10-08.csv "$MASTER_P"
  [ -f partner_scan_2026-10-08.csv ] && cp partner_scan_2026-10-08.csv "$MASTER_S"
  [ -f partner_contacts_2026-10-08.csv ] && cp partner_contacts_2026-10-08.csv "$MASTER_C"
  line "seeded partner master pool from the 2026-10-08 pack"
fi
touch "$MASTER_S" "$MASTER_C" "$DONE"

count_eligible() {
  python3 partner_outreach.py --prospects "$MASTER_P" --scan "$MASTER_S" --contacts "$MASTER_C" \
      --start "$START" --dry --no-verify 2>/dev/null \
    | sed -n 's/^eligible after gates: //p' | head -1
}

ELIG="$(count_eligible)"
line "eligible before refill: ${ELIG:-0}"

# 2. Top up from fresh metros while the pool cannot fill the run.
if [ -z "$ELIG" ] || [ "$ELIG" -lt "$LIMIT" ]; then
  W="$(mktemp -d)"
  : > "$W/next.txt"
  N=0
  while IFS= read -r ln; do
    case "$ln" in \#*|"") continue ;; esac
    name="${ln%%|*}"
    grep -qxF "$name" "$DONE" && continue
    printf '%s\n' "$ln" >> "$W/next.txt"
    N=$((N + 1))
    [ "$N" -ge "$METS_PER_RUN" ] && break
  done < "$METROS"

  if [ "$N" -gt 0 ]; then
    line "pool short -> sourcing ${N} fresh metro(s): $(cut -d'|' -f1 "$W/next.txt" | paste -sd, -)"
    python3 osm_industry_prospects.py --out "$W/prospects.csv" --metros "$W/next.txt" \
        --only-industries it_msp,b2b_agency --max-domains 400 >> partner_refill.log 2>&1 || true
    if [ -s "$W/prospects.csv" ]; then
      [ -s "$MASTER_P" ] || head -1 "$W/prospects.csv" > "$MASTER_P"
      tail -n +2 "$W/prospects.csv" >> "$MASTER_P"
      cut -d, -f1 "$W/prospects.csv" | tail -n +2 | grep -v '^$' | sort -u > "$W/domains.txt"
      python3 email_scan.py --file "$W/domains.txt" --csv "$W/scan.csv" --resume >> partner_refill.log 2>&1 || true
      if [ -s "$W/scan.csv" ]; then
        [ -s "$MASTER_S" ] || head -1 "$W/scan.csv" > "$MASTER_S"
        tail -n +2 "$W/scan.csv" >> "$MASTER_S"
      fi
      python3 find_contacts.py --file "$W/domains.txt" --out "$W/contacts.csv" >> partner_refill.log 2>&1 || true
      if [ -s "$W/contacts.csv" ]; then
        [ -s "$MASTER_C" ] || head -1 "$W/contacts.csv" > "$MASTER_C"
        tail -n +2 "$W/contacts.csv" >> "$MASTER_C"
      fi
      cut -d'|' -f1 "$W/next.txt" >> "$DONE"
      ELIG="$(count_eligible)"
      line "eligible after refill: ${ELIG:-0}"
    else
      line "sourcing returned nothing (Overpass may be down); will retry next run"
    fi
  else
    line "no fresh metros left in ${METROS}"
  fi
  rm -rf "$W"
fi

# 3. Stage.
if [ "$DRY" = "1" ]; then
  python3 partner_outreach.py --prospects "$MASTER_P" --scan "$MASTER_S" --contacts "$MASTER_C" \
      --start "$START" --gap "$GAP" --limit "$LIMIT" --dry --no-verify 2>&1 | tail -8
  line "DRY RUN complete: nothing staged."
  exit 0
fi

OUT="$(python3 partner_outreach.py --prospects "$MASTER_P" --scan "$MASTER_S" --contacts "$MASTER_C" \
        --start "$START" --gap "$GAP" --limit "$LIMIT" 2>&1)"
if printf '%s' "$OUT" | grep -qE 'scheduled and verified'; then
  line "$(printf '%s\n' "$OUT" | grep -E 'scheduled and verified' | tail -1)"
  line "review in IONOS Scheduled."
else
  line "nothing staged. Last lines:"
  printf '%s\n' "$OUT" | tail -6
fi
