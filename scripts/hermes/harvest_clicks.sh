#!/usr/bin/env bash
# harvest_clicks.sh - pull [PB-CLICK] notices into leads/clicks.log and rebuild
# the clicker groups. Cheap, idempotent, sends nothing.
#
# Runs daily (including Friday and Saturday) so a weekend click does not sit in
# the inbox until the Sun-Thu DAILY OUTREACH REFILL trap fires. Silent when
# there is nothing new, so a Telegram delivery is not noise.
set -uo pipefail
cd ~/money_ideas || { echo "harvest_clicks: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

OUT="$(python3 build_clicker_groups.py --harvest 2>&1)"
NEW="$(printf '%s\n' "$OUT" | awk '/^harvest: /{print $2}' | head -1)"
if [ "${NEW:-0}" != "0" ]; then
  printf '%s\n' "$OUT" | tail -6
fi
