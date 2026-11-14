#!/usr/bin/env python
"""Fail when a job report repeats a listing from an earlier report.

Usage:
    python check_repeats.py <report file>

Exit 0  every Jobicy ID in the report was reserved for this run by
        `jobicy_pool.py --pick` and has not been reported before.
Exit 1  at least one ID was already reported on an earlier date.
Exit 2  the report has no Jobicy IDs, or no pick record exists for today.
"""

import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "reported_ids.json")
PICK_IDS = os.path.join(HERE, "pool_pick_ids.json")
JOB_ID = re.compile(r"jobicy\.com/jobs/(\d+)")


def main():
    if len(sys.argv) < 2:
        print("usage: check_repeats.py <report file>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            ids = sorted(set(JOB_ID.findall(fh.read())))
    except OSError as exc:
        print(f"FAIL: cannot read report {path}: {exc}", file=sys.stderr)
        return 2

    try:
        with open(LEDGER, encoding="utf-8") as fh:
            ledger = {str(k): v for k, v in (json.load(fh).get("ids") or {}).items()}
    except (OSError, ValueError):
        ledger = {}

    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(PICK_IDS, encoding="utf-8") as fh:
            pick = json.load(fh)
    except (OSError, ValueError):
        print("FAIL: no pool_pick_ids.json - run `jobicy_pool.py --pick` first", file=sys.stderr)
        return 2

    allowed = {str(i) for i in pick.get("ids", [])} if pick.get("date") == today else set()
    if not allowed:
        print(f"FAIL: pick record is dated {pick.get('date')}, not today ({today}) - re-run --pick", file=sys.stderr)
        return 2

    repeats = []
    unknown = []
    for jid in ids:
        if jid not in allowed:
            seen = ledger.get(jid)
            if seen:
                repeats.append((jid, seen))
            else:
                unknown.append(jid)

    if repeats:
        for jid, seen in repeats:
            print(f"REPEAT: job {jid} was already reported on {seen}")
        return 1
    if unknown:
        for jid in unknown:
            print(f"NOT FROM TODAY'S PICK: job {jid} is not in pool_pick.txt")
        return 1
    print(f"OK: {len(ids)} Jobicy IDs, all reserved for {today}, none reported before")
    return 0


if __name__ == "__main__":
    sys.exit(main())
