#!/usr/bin/env bash
# weekday_verifier_prefill.sh - spend the weekday's free verifier credits on the pool.
#
# NOTHING HERE SENDS MAIL. It verifies addresses ahead of time and writes the
# verdict cache, so the next staging run reads those verdicts instead of probing
# again.
#
# Why this exists (2026-10-08): the hosted verifier's free tier is 100 per day
# and does not roll over. The staging run holds out every address it cannot
# prove (--hold-unknown), and our own RCPT probe cannot reach IPv4-only MX hosts
# (the ISP blocks outbound port 25 on IPv4), so those fall to the hosted
# verifier, capped at MAIL_VERIFY_REMOTE_MAX per run. When the pool is drawn
# down, the staging run meets more unknowns than its remote budget can clear and
# stages fewer than --limit (measured: 85 of 100 on 2026-10-08). The weekend
# prefill already spends Sat/Sun; this does the same Mon-Fri at 10:00, well
# after the 09:00 send and well before the next day's staging, so the credits
# are spent on cache instead of thrown away.
#
# Runs --no-agent, so its stdout is delivered verbatim and no model is involved.
#
# Env knobs:
#   LIMIT=40    how many uncached pool addresses to verify (free tier is 100/day)
#
# LIMIT 100 -> 40 on 2026-10-11. The free 100/day verifier tier is SHARED with the
# PARTNER OUTREACH REFILL, which stages at 10:30 (this job runs 10:00) and can put
# up to 50 fresh agency addresses through the same remote verifier. The buyer
# channel only needs ~30 proven addresses a day now, so a 100-address prefill
# both over-served it and could starve the partner run. 40 leaves guaranteed
# headroom for it.
set -uo pipefail

cd ~/money_ideas || { echo "WEEKDAY PREFILL: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

LIMIT="${LIMIT:-40}"
# This job is exactly the case the hosted verifier exists for, so let it use as
# many calls as it has addresses (bounded by the day's free tier).
export MAIL_VERIFY_REMOTE_MAX="${MAIL_VERIFY_REMOTE_MAX:-$LIMIT}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "WEEKDAY PREFILL: python3 not found; nothing done"
  exit 1
fi

echo "WEEKDAY VERIFIER PREFILL  $(date '+%Y-%m-%d %H:%M %Z')"
# Rebuild the clean list from the master pool so the prefill sees today's pool.
python3 clean_prospects.py --contacts contacts_master.csv --scan scan_master.csv \
        --state state.json --out prospects_daily >/tmp/weekday_prefill_clean.out 2>&1 || true
python3 preverify_pool.py --limit "$LIMIT" 2>&1
rc=$?

if [ "$rc" -ne 0 ]; then
  echo "WEEKDAY PREFILL FAILED (exit ${rc}). Nothing was sent."
  exit "$rc"
fi

echo "Nothing was sent. Verdicts are cached for the next staging run."
