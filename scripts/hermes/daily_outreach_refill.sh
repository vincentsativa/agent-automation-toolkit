#!/usr/bin/env bash
# daily_outreach_refill.sh - the "on the road" backup for the Email
# Deliverability Rescue outreach. Runs the daily data side end to end:
#   clean the sendable list -> (optional refill: source+scan if the pool is
#   short) -> stage the day's schedule -> verify by read-back -> print a short
#   summary for Telegram.
#
# Run by the Hermes cron job "DAILY OUTREACH REFILL". No model is required to do
# the work; the cron wraps this with deepseek-v4.1-flash only to format the note.
#
# Env knobs (all optional):
#   LIMIT=30            how many to stage
#   START=tomorrow 09:00  local (America/New_York) start time
#   GAP=6               minutes between sends
#   BATCH=b4            which harvested pool to draw from
#   REFILL=0            set 1 to source+scan a fresh batch when the pool is short
#   DRY=0               set 1 to rehearse (schedule_drafts --dry, nothing staged)
#
# RATE CHANGE 2026-10-11 (Vinny): the AGENCY/PARTNER channel is the one that
# converts (43 agencies -> 1 real reply; ~700 buyer sends -> 0 replies). The
# buyer channel is throttled 100 -> 30/day and the partner channel raised
# 30 -> 50/day. This is NOT a pause: the buyer side still runs every weekday,
# which keeps hello@phantom-byte.com sending daily (reputation warmth) and keeps
# the scanned-domain dataset growing, and it costs nothing to leave alone.
# GAP 2 -> 6 so the 30 sends still spread across a ~3h window instead of a
# one-hour burst. Verified partner batch (13:00) does not overlap this window.
set -uo pipefail

cd ~/money_ideas || { echo "DAILY OUTREACH: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

# Interpreter pin (2026-10-22). The cron run's bare `python3` resolved to a
# Python WITHOUT the `requests` module, so schedule_drafts.py died at import
# and the day's emails were never staged. Never trust PATH for this script:
# /usr/bin/python3 carries requests and imports every module in the chain
# (schedule_drafts, outreach, harvest_bounces, clean_prospects, check_scheduled,
# build_lead_groups, build_clicker_groups, osm_industry_prospects, email_scan).
# Override only deliberately with PY=/path/to/python3.
PY="${PY:-/usr/bin/python3}"
if ! "$PY" -c "import requests, imaplib" >/dev/null 2>&1; then
  printf 'ABORT: interpreter %s cannot import requests; nothing staged.\n' "$PY"
  exit 1
fi

LIMIT="${LIMIT:-30}"
GAP="${GAP:-6}"
# Send time: the next WEEKDAY (Mon-Fri) at 09:00 local. If "tomorrow" lands on
# a Saturday or Sunday, roll forward to Monday so nothing is ever queued to send
# on a weekend. An explicit START passed in the environment still wins (used for
# a deliberate same-day test batch).
if [ -z "${START:-}" ]; then
  # Send the SAME day at 09:00. The cron runs Mon-Fri 01:30, so at 01:30 the
  # 09:00 send is still ahead. Same-day staging is what keeps the read-back
  # correct: the batch leaves the folder before the NEXT morning's 01:30 run, so
  # the folder never holds two batches at once. Before 2026-10-09 this staged for
  # the next day, so at 01:30 the previous day's batch (sending that same 09:00)
  # was still present and the whole-folder count check failed from the 2nd run
  # on. A weekend manual run still rolls to Monday so nothing is queued for a
  # weekend send.
  case "$(date '+%u')" in
    6) START_D="$(date -d '+2 days' '+%Y-%m-%d')" ;;  # Sat -> Mon
    7) START_D="$(date -d '+1 day'  '+%Y-%m-%d')" ;;  # Sun -> Mon
    *) START_D="$(date '+%Y-%m-%d')" ;;
  esac
  START="${START_D}T09:00"
fi
BATCH="${BATCH:-b4}"
REFILL="${REFILL:-0}"
DRY="${DRY:-0}"
# Hold out addresses the mailbox probe could not decide (timeout/refused).
# This is the fix for the 2026-09-30 bounces: 2 of the 3 hard bounces were
# addresses the probe could not verify, and the old default mailed them
# anyway. Held addresses are NOT suppressed, so they return and are
# re-probed on the next cycle. Set HOLD_UNKNOWN=0 to disable.
HOLD_UNKNOWN="${HOLD_UNKNOWN:-1}"
# Backfill window: with a hold active, verify this many candidate rows PAST
# --limit so the proven head can still fill --limit. Raised 75 -> 200 on
# 2026-10-08 for LIMIT=100: with 75 the window was 175 candidates and only ~85
# came back verified, so the Oct 8 run staged 85 of 100. Lowered 200 -> 60 on
# 2026-10-11 when LIMIT went to 30: the window is now 90 candidates, which is
# ample for 30, and a 300-candidate window on a 30-address run just burns the
# shared 100/day verifier tier (which the partner batch also draws on).
VERIFY_BACKFILL_MARGIN="${VERIFY_BACKFILL_MARGIN:-60}"
export VERIFY_BACKFILL_MARGIN
# Industry buckets a refill sources. Businesses that SEND INVOICES/QUOTES by
# email and have an owner reading the mail; agencies/SaaS/retail excluded.
TARGET_INDUSTRIES="${TARGET_INDUSTRIES:-construction,professional,realestate,financial,healthcare}"
OFFER="https://phantom-byte.com/email-deliverability-rescue"
# Default to the cleaned MASTER pool (union of every batch, ~577 sendable).
# Set POOL=b4 to use the older single-batch pool instead.
if [ "${POOL:-master}" = "master" ] && [ -f scan_master.csv ] && [ -f contacts_master.csv ]; then
  POOL_SCAN="${POOL_SCAN:-scan_master.csv}"
  POOL_CONTACTS="${POOL_CONTACTS:-contacts_master.csv}"
else
  POOL_SCAN="${POOL_SCAN:-scan_2000_${BATCH}_results.csv}"
  POOL_CONTACTS="${POOL_CONTACTS:-contacts_2000_${BATCH}_final.csv}"
fi
STAMP="$(date '+%Y-%m-%d %H:%M')"

line() { printf '%s\n' "$1"; }

# Keep the compiled lead groups current (Vinny, 2026-10-01). Reads what actually
# sent and what actually clicked, then rewrites leads/. Runs on EVERY exit path
# and is never fatal: a failure here must not affect staging or sending.
update_lead_groups() {
  "$PY" build_lead_groups.py >> lead_groups.log 2>&1 || true
  "$PY" build_clicker_groups.py --harvest >> lead_groups.log 2>&1 || true
  line "lead groups + clickers refreshed (leads/)"
}
trap update_lead_groups EXIT

line "DAILY OUTREACH REFILL  ${STAMP}"
line "pool: ${POOL_CONTACTS}  limit: ${LIMIT}  start: ${START}"

if [ ! -f "$POOL_CONTACTS" ] || [ ! -f "$POOL_SCAN" ]; then
  line "ABORT: pool files missing (${POOL_CONTACTS} / ${POOL_SCAN}). Nothing staged."
  exit 0
fi

# 0. HARVEST BOUNCES first. A hard-bounced mailbox is written to the
# suppression file by this step, so the clean below drops it and it is never
# re-sent. Non-fatal: a failure here must not stop the staging run.
BOUNCE_OUT="$("$PY" harvest_bounces.py 2>&1 || true)"
BOUNCE_LINE="$(printf '%s\n' "$BOUNCE_OUT" | grep -m1 -E '^(Suppressed|Would suppress):' || true)"
if [ -n "$BOUNCE_LINE" ]; then
  line "bounces: ${BOUNCE_LINE}"
  printf '%s\n' "$BOUNCE_OUT" | grep -E 'AUTHENTICATION GATEWAY|RECIPIENT-POLICY|CONTENT / SPAM' || true
else
  line "bounces: harvest skipped (no verdict from harvest_bounces.py)"
fi

# 1. CLEAN the sendable list from the harvested pool (role rule + fit + dedupe +
#    stored mailbox verdict). The old list is removed first: a crashed cleaner
#    used to leave an older file in place and the count was read off it, which is
#    how a run could report a number nothing in that run had measured.
rm -f prospects_daily_clean.csv
CLEAN_OUT="$("$PY" clean_prospects.py --contacts "$POOL_CONTACTS" --scan "$POOL_SCAN" \
              --state state.json --out prospects_daily 2>&1)"
if [ ! -f prospects_daily_clean.csv ]; then
  line "ABORT: clean_prospects.py produced no list this run. Nothing staged."
  printf '%s\n' "$CLEAN_OUT" | tail -3
  exit 0
fi
SENDABLE="$(($(wc -l < prospects_daily_clean.csv) - 1))"
ROLE_DROPPED="$(printf '%s\n' "$CLEAN_OUT" | awk '/role address/{print $1}' | head -1)"
BREAKDOWN="$(printf '%s\n' "$CLEAN_OUT" | grep -m1 '^sendable breakdown:' || true)"
line "sendable person addresses: ${SENDABLE}   (role boxes dropped: ${ROLE_DROPPED:-0})"
[ -n "$BREAKDOWN" ] && line "$BREAKDOWN"

# 2. Optional refill when the pool cannot cover the run (heavy: source + scan).
if [ "$SENDABLE" -lt "$LIMIT" ] && [ "$REFILL" = "1" ]; then
  line "pool short -> refilling (source + scan); this takes a while"
  REFILL_OUT="prospects_refill_$(date +%F).csv"
  "$PY" osm_industry_prospects.py --out "$REFILL_OUT" --metros osm_metros.txt \
          --only-industries "$TARGET_INDUSTRIES" --max-domains 1500 \
          >> daily_refill.log 2>&1 || true
  NEWLIST="$REFILL_OUT"
  if [ -n "$NEWLIST" ]; then
    cut -d, -f1 "$NEWLIST" | tail -n +2 | sort -u > "domains_refill_$(date +%F).txt"
    "$PY" email_scan.py --file "domains_refill_$(date +%F).txt" \
            --csv "scan_refill_$(date +%F).csv" --resume >> daily_refill.log 2>&1 || true
    line "refill scanned -> scan_refill_$(date +%F).csv (next run can draw from it)"
  fi
fi

# 3. Stage the day's schedule (the gate chain + role rule run inside outreach.py).
# A short pool stages what it has instead of staging nothing. The old floor was
# `SENDABLE < LIMIT -> NOT STAGED`, which threw proven addresses away over a
# supply problem, and the read-back was hard-wired to --expect LIMIT, so a
# 20-of-30 run printed FAIL while its 20 messages were staged correctly and
# tracked in state. Now PLAN is min(LIMIT, SENDABLE) and the read-back is
# checked against the number this run says it actually scheduled.
if [ "$SENDABLE" -lt 1 ]; then
  line "NOT STAGED: 0 sendable person addresses. Set REFILL=1, or run the prospect refill."
  exit 0
fi
PLAN="$LIMIT"
SHORT=""
if [ "$SENDABLE" -lt "$LIMIT" ]; then
  PLAN="$SENDABLE"
  SHORT="  (short of ${LIMIT} by $((LIMIT - SENDABLE)): the pool is the constraint, not the rate)"
fi

EXTRA=""
[ "$HOLD_UNKNOWN" = "1" ] && EXTRA="--hold-unknown"

if [ "$DRY" = "1" ]; then
  "$PY" schedule_drafts.py --csv "$POOL_SCAN" --emails "$POOL_CONTACTS" \
          --offer-url "$OFFER" --limit "$PLAN" --start "$START" --gap "$GAP" $EXTRA --dry \
          2>&1 | tail -5
  line "DRY RUN complete: nothing was scheduled."
  exit 0
fi

STAGE_LOG="$("$PY" schedule_drafts.py --csv "$POOL_SCAN" --emails "$POOL_CONTACTS" \
             --offer-url "$OFFER" --limit "$PLAN" --start "$START" --gap "$GAP" $EXTRA 2>&1)"
if printf '%s' "$STAGE_LOG" | grep -qE 'scheduled.*verified|every message verified'; then
  # What actually reached the folder, taken from the staging run's own line
  # "<ok> of <plan> scheduled into the IONOS Scheduled folder".
  STAGED="$(printf '%s\n' "$STAGE_LOG" | sed -n 's/^\([0-9]\{1,\}\) of [0-9]\{1,\} scheduled.*/\1/p' | tail -1)"
  EXPECT="${STAGED:-$PLAN}"
  # 4. Independent read-back.
  if "$PY" check_scheduled.py --expect "$EXPECT" >/tmp/check_sched.out 2>&1; then
    line "STAGED: ${EXPECT} emails for ${START} (verified by read-back). Review in IONOS Scheduled.${SHORT}"
  else
    line "WARNING: staged but read-back did not pass; check IONOS Scheduled folder."
    tail -3 /tmp/check_sched.out
  fi
else
  line "STAGING FAILED (nothing sent). Last lines:"
  printf '%s\n' "$STAGE_LOG" | tail -4
fi
