#!/usr/bin/env python3
"""Regular stale-cache cleanup for the /data volume.

Acts only when free space on /data is below the threshold (default 3500 MB,
override with CLEAN_MB). Only touches proven-reclaimable buckets: the pip HTTP
cache, the npm cache, and Playwright browser builds in ~/.cache/ms-playwright
that no browsers.json on the machine references and that are at least 48h old.
Never touches ~/.hermes/installs, ~/.hermes/tools, ~/.hermes/hermes-agent,
~/.pi, or any live service state.

Prints a report only when it freed at least MIN_REPORT_MB, so an empty run
sends nothing.
"""
import json
import os
import re
import shutil
import subprocess
import time

MOUNT = "/data"
HOME = os.path.expanduser("~")
SPW = os.path.join(HOME, ".cache", "ms-playwright")
THRESHOLD_MB = int(os.environ.get("CLEAN_MB", "3500"))
MIN_REPORT_MB = int(os.environ.get("MIN_REPORT_MB", "100"))
SCAN_BUDGET_S = 180

PRUNE_DIRS = {".git", "ms-playwright", "Downloads", "Desktop"}


def stat_mb(path):
    st = os.statvfs(path)
    total = (st.f_blocks - st.f_bfree) * st.f_frsize
    free = st.f_bavail * st.f_frsize
    used_pct = int(total * 100 / (total + free)) if (total + free) else 0
    return free // (1024 * 1024), used_pct


def du_mb(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total // (1024 * 1024)


def referenced_revisions():
    """Every browser revision declared by a browsers.json anywhere under HOME."""
    refs = set()
    deadline = time.time() + SCAN_BUDGET_S
    for root, dirs, files in os.walk(HOME):
        dirs[:] = [d for d in dirs if d not in PRUNE_DIRS]
        if time.time() > deadline:
            break
        if "browsers.json" not in files:
            continue
        try:
            with open(os.path.join(root, "browsers.json")) as fh:
                data = json.load(fh)
            for browser in data.get("browsers", []):
                rev = browser.get("revision")
                if rev:
                    refs.add(str(rev))
        except Exception:
            continue
    return refs


def main():
    free_before, pct_before = stat_mb(MOUNT)
    if free_before >= THRESHOLD_MB:
        return  # plenty of room, nothing to do

    report = []

    # 1. pip HTTP cache
    try:
        out = subprocess.run(["pip", "cache", "purge"], capture_output=True,
                             text=True, timeout=300).stdout.strip()
        m = re.search(r"Files removed: (\d+) \(([\d.]+) MB\)", out)
        if m and float(m.group(2)) > 0:
            report.append(f"- pip cache: {m.group(2)} MB ({m.group(1)} files)")
    except Exception:
        pass

    # 2. npm cache
    try:
        npm_dir = os.path.join(HOME, ".npm")
        before = du_mb(npm_dir)
        subprocess.run(["npm", "cache", "clean", "--force"],
                       capture_output=True, timeout=600)
        after = du_mb(npm_dir)
        if before - after > 0:
            report.append(f"- npm cache: {before - after} MB")
    except Exception:
        pass

    # 3. Playwright builds no installed package declares
    try:
        refs = referenced_revisions()
        removed, freed = [], 0
        now = time.time()
        for entry in sorted(os.listdir(SPW)):
            m = re.match(r"^(?P<base>[a-z_]+)-(?P<rev>\d+)$", entry)
            if not m:
                continue
            path = os.path.join(SPW, entry)
            if not os.path.isdir(path):
                continue
            if m.group("rev") in refs:
                continue  # some package still declares this revision
            if now - os.path.getmtime(path) < 48 * 3600:
                continue  # freshly fetched, leave it alone
            size = du_mb(path)
            shutil.rmtree(path, ignore_errors=True)
            if not os.path.exists(path):
                removed.append(entry)
                freed += size
        if removed:
            report.append(f"- stale Playwright builds: {', '.join(removed)} ({freed} MB)")
    except Exception:
        pass

    total = 0
    for line in report:
        m = re.search(r"\((\d+(?:\.\d+)?) MB\)", line)
        if m:
            total += float(m.group(1))
    if total < MIN_REPORT_MB:
        return  # nothing meaningful reclaimed, stay silent

    free_after, pct_after = stat_mb(MOUNT)
    print(f"Stale-stuff cleanup: freed {total:.0f} MB on /data "
          f"({free_before} MB free / {pct_before}% -> {free_after} MB free / {pct_after}%)")
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
