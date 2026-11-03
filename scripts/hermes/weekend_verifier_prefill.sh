#!/usr/bin/env bash
# weekend_verifier_prefill.sh - spend the weekend's free verifier credits on the pool.
#
# NOTHING HERE SENDS MAIL. It verifies addresses ahead of time and writes the
# verdict cache, so the next weekday staging run reads those verdicts instead of
# probing again.
#
# Why the weekend: the hosted verifier's free tier is 100 per day and does not
# roll over, and nothing sends on Friday or Saturday. Those are two days of free
# capacity that are otherwise thrown away, and the addresses our own probe cannot
# reach (IPv4-only MX hosts, since the ISP blocks outbound port 25 on IPv4) are
# exactly the ones worth clearing in advance.
#
# Run by the Hermes cron job "WEEKEND VERIFIER PREFILL". No model is needed, so
# the job runs --no-agent and its stdout is delivered verbatim.
#
# Env knobs:
#   LIMIT=60    how many uncached pool addresses to verify (free tier is 100/day)
#
# LIMIT lowered 2026-10-11 (Sat 100 -> 60, Sun 60 -> 40) to match the buyer
# channel's new 30 staged/day. The old Sunday note ("leave headroom for the 11pm
# DAILY OUTREACH REFILL") was stale twice over: there is no 11pm job, and the
# staging run now happens at 01:30, which is a NEW day for the verifier tier, so
# Sunday's credits were never needed by it. Nothing else runs Sat/Sun.
set -uo pipefail

cd ~/money_ideas || { echo "WEEKEND PREFILL: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

# Saturday can spend a bigger slice: nothing else runs that day.
# Sunday is held a little lower so it never competes with a manual weekend run.
if [ "$(date +%u)" = "7" ]; then
  LIMIT="${LIMIT:-40}"
else
  LIMIT="${LIMIT:-60}"
fi
# Let the prefill use as many calls as it has addresses: this job is exactly the
# case the hosted verifier exists for. Bounded by the day's free tier (100).
# Without this it inherited the staging default of 40 and stopped early with
# addresses still unresolved - measured 2026-10-02: 40 of 40 spent, 28 left
# UNKNOWN that the verifier would have answered.
export MAIL_VERIFY_REMOTE_MAX="${MAIL_VERIFY_REMOTE_MAX:-$LIMIT}"

if [ ! -x /usr/bin/python3 ] && ! command -v python3 >/dev/null 2>&1; then
  echo "WEEKEND PREFILL: python3 not found; nothing done"
  exit 1
fi

echo "WEEKEND VERIFIER PREFILL  $(date '+%Y-%m-%d %H:%M %Z')"
python3 preverify_pool.py --limit "$LIMIT" 2>&1
rc=$?

if [ "$rc" -ne 0 ]; then
  echo "WEEKEND PREFILL FAILED (exit ${rc}). Nothing was sent."
  exit "$rc"
fi

echo "Nothing was sent. Verdicts are cached for the next staging run."
