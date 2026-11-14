#!/usr/bin/env bash
# reply_lists.sh - read the hello@ mailbox and file every human reply on the
# right list. Sends nothing, deletes nothing, marks nothing read.
#
# Run by the Hermes cron job "REPLY LIST FILER" at 22:15 local, daily.
# The scan itself prints one line every run (including "no new replies"), so a
# missing Telegram message means the job did not fire.
set -uo pipefail
cd ~/money_ideas || { echo "reply_lists: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env
python3 reply_lists.py 2>&1
