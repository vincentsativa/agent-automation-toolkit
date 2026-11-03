#!/usr/bin/env bash
# partner_directory_refill.sh - grow the PARTNER (agency/MSP) pool from agency
# directories, then push the new domains through the existing scan + harvest
# chain.
#
# WHY: measured 2026-10-11, OpenStreetMap is exhausted for the agency segment.
# Twelve sourced metros gave 272 raw partner prospects and only 91 addresses
# (7.6 per metro), so the whole 55-metro queue is worth ~8 send-days at 50/day.
# The directories are actually ABOUT agencies and publish each agency's own
# website: topdevelopers.co has 10,836 agency profiles, superbcompanies.com has
# 77,931. Measured extraction accuracy on the first twenty profiles of each: 40/40.
#
# Chain:  directory_prospects.py   scrape profiles -> domains (+ master pool)
#         directory_pool_todo.py   which domains still need scan / contacts
#         email_scan.py            DNS grade (SPF/DKIM/DMARC) -> scan master
#         dir_harvest_instabox.sh the contact-page harvest, on InstaBox
#
# NOTHING HERE SENDS MAIL. This only fills the pool that partner_refill.sh stages
# from. It runs at 04:00 so it finishes well before the 09:30 agency staging and
# the 13:00 send that consume it (moved off 18:00 on 2026-11-02: the harvest was
# running while Vinny works and made the machine unusable).
#
# Env knobs:
#   SOURCE=topdevelopers,superbcompanies   comma list, or "all"
#   PROFILES=250       profile pages to read PER SOURCE this run
#   DELAY=3.0          seconds between requests to a host
#   THREADS=32         threads in the ONE harvest process on the InstaBox box
#                      (measured 2026-10-30: 16 threads = 67 domains/min, load 0.04)
#   WORKERS=16         LOCAL FALLBACK only, when the box is unusable that run:
#                      find_contacts.py worker processes on this machine
#   RETRY_BACKLOG=1    also re-attempt the older pool domains that still have no
#                      address (default 0: harvest only what this run discovered)
#   SCAN_LIMIT=0       cap the DNS scan (0 = every TODO domain)
#   DRY=1              scrape/enumerate only; no scan, no harvest, nothing staged
set -uo pipefail

cd ~/money_ideas || { echo "PARTNER DIRECTORY: money_ideas not found"; exit 1; }
# shellcheck disable=SC1091
source ~/.config/phantombyte/mailer.env

SOURCE="${SOURCE:-topdevelopers,superbcompanies}"
PROFILES="${PROFILES:-250}"
DELAY="${DELAY:-3.0}"
WORKERS="${WORKERS:-16}"
THREADS="${THREADS:-32}"
SCAN_LIMIT="${SCAN_LIMIT:-0}"
RETRY_BACKLOG="${RETRY_BACKLOG:-0}"
DRY="${DRY:-0}"

MASTER_P="partner_prospects_master.csv"
MASTER_S="partner_scan_master.csv"
MASTER_C="partner_contacts_master.csv"
STAMP="$(date '+%Y-%m-%d %H:%M')"

line() { printf '%s\n' "$1"; }

# 0. Retry guard. This job fires at 04:00 AND 07:00 (2026-11-03). A gateway
#    restart kills an in-flight run by design: on a planned stop systemd stops
#    the job's own transient scope (journal 2026-11-02 18:09:29 stopped
#    hermes-worker-cron-be4516e1f17a-exec-...scope), the scheduler records the
#    attempt as UNKNOWN, and executions.recover_interrupted_executions is
#    documented as marking such rows "without scheduling retries". So a single
#    04:00 slot lost the whole night of 2026-11-02 with nothing re-fired after
#    the gateway came back. The marker below is written ONLY when a run reaches
#    its RESULT line, so a killed run leaves none and the later fire picks the
#    chain back up: directory_seen_<source>.txt holds the scrape cursor,
#    email_scan runs with --resume, and both masters are appended by key. A fire
#    that finds today's marker prints nothing and exits, which the cron recorder
#    reports as "silent (empty output)" - no Telegram noise on days the 04:00
#    run already finished.
MARKER=".pdir_last_complete"
if [ "$DRY" != "1" ] && [ -s "$MARKER" ] && [ "$(cat "$MARKER" 2>/dev/null)" = "$(date '+%Y-%m-%d')" ]; then
  exit 0
fi

# Pick a python that can import requests. `python3` on PATH can resolve to the
# Hermes runtime, which cannot, and then every step dies quietly (harvest.sh
# learned this the hard way). Probe, do not assume.
PY=python3
if ! "$PY" -c "import requests" >/dev/null 2>&1; then
  for cand in /usr/bin/python3 /usr/local/bin/python3 python3.12 python3.11; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import requests" >/dev/null 2>&1; then
      PY="$cand"; break
    fi
  done
fi
if ! "$PY" -c "import requests" >/dev/null 2>&1; then
  line "ABORT: no python3 on this box can import requests. Nothing done."
  exit 1
fi

line "PARTNER DIRECTORY REFILL  ${STAMP}"
line "sources: ${SOURCE}   profiles/source: ${PROFILES}   delay: ${DELAY}s   python: ${PY}"

# 0. Harvest bounces first, so a dead partner mailbox cannot be re-staged.
"$PY" harvest_bounces.py >/tmp/pdir_bounces.out 2>&1 || true
BL="$(grep -m1 -E '^(Suppressed|Would suppress):' /tmp/pdir_bounces.out || true)"
[ -n "$BL" ] && line "bounces: ${BL}"

# 1. Scrape. Appends new domains to the master pool (deduped there).
#    DRY=1 enumerates the sitemaps only, reads no profile page and writes nothing.
#    dir_new_domains.txt collects exactly what this run added, so step 4 does not
#    re-attempt the whole backlog of addressless pool domains.
line ""
line "--- 1/4 scrape agency directories"
DRY_ARG=""
[ "$DRY" = "1" ] && DRY_ARG="--dry"
: > dir_new_domains.txt
SCRAPE_OUT="$("$PY" directory_prospects.py --source "$SOURCE" --limit "$PROFILES" \
              --delay "$DELAY" --new-domains-out dir_new_domains.txt $DRY_ARG 2>&1)"
printf '%s\n' "$SCRAPE_OUT" | grep -E "^(===|  [A-Z]|    |  fetching|  wrote|  appended|  profiles read|  SKIPPED|  nothing new)" | tail -40
DOMAINS_FOUND="$(printf '%s\n' "$SCRAPE_OUT" | sed -n 's/^TOTAL: profiles read .* domains found \([0-9]*\).*/\1/p' | tail -1)"
line "domains found this run: ${DOMAINS_FOUND:-0}"

if [ "$DRY" = "1" ]; then
  line "DRY=1: enumerated only. Nothing read from a profile page, nothing scanned,"
  line "       nothing harvested, nothing staged."
  exit 0
fi

if [ "${DOMAINS_FOUND:-0}" -eq 0 ]; then
  line "no new domains this run; nothing to scan or harvest."
  exit 0
fi

# 2. Which new domains still need a scan / a contact.
line ""
line "--- 2/4 work out what is actually new"
ONLY_ARG=""
if [ "$RETRY_BACKLOG" != "1" ] && [ -s dir_new_domains.txt ]; then
  ONLY_ARG="--only-domains dir_new_domains.txt"
fi
"$PY" directory_pool_todo.py $ONLY_ARG | sed 's/^/    /'

# 3. DNS scan the unscanned ones (the offer's hook is built from this).
if [ -s dir_todo_scan.txt ]; then
  N_SCAN="$(wc -l < dir_todo_scan.txt)"
  [ "$SCAN_LIMIT" -gt 0 ] && { head -n "$SCAN_LIMIT" dir_todo_scan.txt > dir_todo_scan.cap.txt; \
                              mv dir_todo_scan.cap.txt dir_todo_scan.txt; N_SCAN="$SCAN_LIMIT"; }
  line ""
  line "--- 3/4 DNS scan ${N_SCAN} domain(s) (SPF/DKIM/DMARC)"
  if "$PY" email_scan.py --file dir_todo_scan.txt --csv dir_scan.csv --resume \
        >> directory_refill.log 2>&1 && [ -s dir_scan.csv ]; then
    # csv_append refuses on a missing/empty source and never truncates the master.
    #
    # WHY THIS IS NOT A SHELL ONE-LINER (incident of 2026-10-11). The idiom used to
    # be `[ -s "$M" ] || head -1 "$SRC" > "$M"` followed by `tail -n +2 "$SRC" >> "$M"`.
    # Two things went wrong at once and together they EMPTIED
    # partner_contacts_master.csv (187 rows of contact history, restored from a
    # backup taken minutes earlier):
    #   1. `cmd > file` performs the redirection BEFORE it runs the command, so a
    #      missing $SRC truncates the master and only then fails to read it;
    #   2. worse, this script was EDITED WHILE IT WAS RUNNING. Bash reads a script
    #      file incrementally, so changing its length mid-execution shifts the read
    #      offset and bash resumes halfway through a command. That is what skipped
    #      the guard on line 1 and left only the truncating redirect.
    # So: the append now happens in Python (read, validate, then write via a temp
    # file and os.replace), AND never edit this file while a run is in flight.
    "$PY" csv_append.py --src dir_scan.csv --dst "$MASTER_S" --key domain || {
      line "    APPEND FAILED for ${MASTER_S} - see the message above. Nothing else changed."
      exit 0
    }
    line "    scanned ${N_SCAN}; appended to ${MASTER_S}"
  else
    line "    SCAN FAILED - see directory_refill.log. Nothing harvested."
    exit 0
  fi
else
  line ""
  line "--- 3/4 DNS scan: nothing new to scan"
fi

# 4. Harvest a contact address off each domain's own contact page, in parallel.
if [ -s dir_todo_contacts.txt ]; then
  N_CON="$(wc -l < dir_todo_contacts.txt)"
  line ""
  line "--- 4/4 contact harvest for ${N_CON} domain(s)"
  # The workers are the ONLY heavy part of this script, so they run on InstaBox
  # (approved 2026-11-02). The box is a free-tier VM that self-pauses after 30
  # idle minutes and caps a run at 480, so it cannot hold a schedule: this cron is
  # the clock and dir_harvest_instabox.sh wakes it every run. Exit 2 means the box
  # was not usable (asleep and would not wake, cooling down after a long run, or no
  # CSV back) and the harvest falls back to this machine so the run is not lost.
  HSTAT=0
  if bash "$HOME/.hermes/scripts/dir_harvest_instabox.sh" --file dir_todo_contacts.txt \
       --out dircontacts --threads "$THREADS" > /tmp/pdir_harvest.out 2>&1; then
    HSTAT=0
  else
    HSTAT=$?
  fi
  if [ "$HSTAT" -eq 2 ]; then
    line "    InstaBox not usable this run - harvesting on this machine instead"
    # harvest.sh merges parts 1..workers BY NAME, and a worker that finds nothing
    # writes no part file at all, so a part left behind by an earlier run is merged
    # as if it were this run's. Measured 2026-11-03 while testing this branch: a
    # stale dircontacts_part1.csv from 2026-11-01 made a 4-domain list merge 4,908
    # "domains". Clear the old parts before the fallback starts.
    rm -f dircontacts_part*.csv dircontacts_part*.log dircontacts_part*.txt
    bash harvest.sh --file dir_todo_contacts.txt --out dircontacts --workers "$WORKERS" \
          >> /tmp/pdir_harvest.out 2>&1
    HSTAT=$?
  elif [ "$HSTAT" -ne 6 ]; then
    line "    harvested on InstaBox"
  fi
  cat /tmp/pdir_harvest.out >> directory_refill.log
  # harvest.sh exits 6 when it killed a stalled worker and merged what it had.
  # That is not a clean run and this report has to say so, but the rows are real
  # and they get merged. Any other non-zero exit means it never ran (or refused
  # because another harvest holds the lock), where nothing is merged.
  if [ "$HSTAT" -eq 0 ] || [ "$HSTAT" -eq 6 ]; then
    if [ -s dircontacts_final.csv ]; then
      if "$PY" csv_append.py --src dircontacts_final.csv --dst "$MASTER_C" --key domain; then
        WITH_EMAIL="$(awk -F, 'NR>1 && $2!="" {n++} END{print n+0}' dircontacts_final.csv)"
        line "    harvest wrote ${WITH_EMAIL} address(es); merged into ${MASTER_C}"
        if [ "$HSTAT" -eq 6 ]; then
          line "    CUT SHORT: at least one worker stalled and was killed, so the domains it"
          line "    had not reached were not harvested. Everything written was merged."
        fi
      else
        line "    APPEND FAILED for ${MASTER_C} - nothing written, master intact."
      fi
    else
      line "    harvest produced no merged file - see directory_refill.log"
    fi
  else
    line "    HARVEST FAILED or already running - see directory_refill.log"
  fi
else
  line ""
  line "--- 4/4 contact harvest: nothing new to harvest"
fi

# 5. Report the eligible partner count, so the Telegram note is actionable.
line ""
ELIG="$("$PY" partner_outreach.py --prospects "$MASTER_P" --scan "$MASTER_S" \
        --contacts "$MASTER_C" --start "$(date -d 'tomorrow' '+%Y-%m-%d')T13:00" \
        --dry --no-verify 2>/dev/null | sed -n 's/^eligible after gates: //p' | head -1)"
POOL_DOMAINS="$(( $(wc -l < "$MASTER_P") - 1 ))"
line "RESULT: partner pool now ${POOL_DOMAINS} domains, ${ELIG:-0} eligible after gates."
line "partner_refill.sh stages up to 50 of those at the next 09:30 run. Nothing was sent."

# Reached only when the whole chain completed: today is stamped so the 07:00
# retry fire stays silent. A run killed before this line leaves no marker, and
# that is the signal for the retry to resume.
date '+%Y-%m-%d' > "$MARKER"
