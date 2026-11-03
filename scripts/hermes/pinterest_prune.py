#!/usr/bin/env python3
"""
Prune stale Pinterest post files from the Linux home directory.

The DAILY Pinterest Posts cron (5:45PM) writes its working copy to
~/pinterest_posts_YYYY-MM-DD.txt. Nothing reads those files back,
so they accumulate forever. This script keeps the last KEEP_DAYS days and
deletes anything older.

Run daily by the 'PRUNE STALE PINTEREST POSTS' cron job with no_agent=True:
stdout is delivered verbatim, and empty stdout sends nothing (watchdog
pattern), so it stays silent on days when there is nothing to prune.

Scope: ONLY ~/pinterest_posts_*.txt. The Windows desktop data
folder (C:\\Users\\<user>\\OneDrive\\Desktop\\TODAYS DATA FILES) is already
cleared daily by the separate 'Delete Daily Data Files' job at 3:30AM and is
deliberately left alone here.
"""

import glob
import os
import re
from datetime import date, timedelta

HOME = "~"
KEEP_DAYS = 7
PATTERN = os.path.join(HOME, "pinterest_posts_*.txt")
NAME_RE = re.compile(r"^pinterest_posts_(\d{4}-\d{2}-\d{2})\.txt$")


def main():
    cutoff = date.today() - timedelta(days=KEEP_DAYS)
    removed = []
    kept = []
    skipped = []

    for path in sorted(glob.glob(PATTERN)):
        name = os.path.basename(path)
        m = NAME_RE.match(name)
        if not m:
            skipped.append(name)
            continue
        try:
            filedate = date.fromisoformat(m.group(1))
        except ValueError:
            skipped.append(name)
            continue
        if filedate < cutoff:
            try:
                os.remove(path)
                removed.append(name)
            except OSError as exc:
                print(f"WARN: could not delete {name}: {exc}")
        else:
            kept.append(name)

    if removed:
        print(
            f"Pruned {len(removed)} stale Pinterest post file(s) older than "
            f"{KEEP_DAYS} days: {', '.join(removed)}. "
            f"{len(kept)} kept."
        )
    if skipped:
        print(f"NOTE: {len(skipped)} unrecognized file(s) left in place: "
              f"{', '.join(skipped)}")


if __name__ == "__main__":
    main()
