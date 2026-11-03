"""Deep-pull the Himalayas feed by offset, in parallel, writing incrementally.

The default adapter reads 40 pages of a feed that carries over 128,000 live
postings, so it sees roughly one day of inventory and reports the rest as a
supply shortage. This script pages as deep as you ask and dedupes by guid.

Usage:
    python pull_himalayas_deep.py --max-offset 20000 --out himalayas-deep.jsonl
    python pull_himalayas_deep.py --max-offset 60000 --start 20000 --out himalayas-deep.jsonl

Offset is deprecated in favour of cursor pagination, but cursor is sequential
and slow; offset still returns distinct pages and parallelises cleanly. Rows
land in the output file as they arrive, so a timeout never loses the pull.
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# This directory contains select.py, which shadows the standard library module
# `select`. socket imports select, so any module that pulls in socket with this
# directory on sys.path dies with "partially initialized module 'socket'" and a
# circular-import traceback. Drop our own directory from sys.path for this
# script: it needs no sibling module, and the deep pull has to be able to fetch.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path
               if os.path.abspath(p or os.getcwd()) != _here]

import requests  # noqa: E402

BASE = "https://himalayas.app/jobs/api?limit=20&offset=%d"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; jobsearch/1.0)"}


def fetch(offset, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(BASE % offset, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                return r.json().get("jobs", [])
            time.sleep(1.0 * (attempt + 1))
        except Exception:
            time.sleep(1.0 * (attempt + 1))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-offset", type=int, default=20000)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--out", default="himalayas-deep.jsonl")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    seen = set()
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as fh:
            for line in fh:
                try:
                    seen.add(json.loads(line).get("guid"))
                except Exception:
                    pass

    offsets = list(range(args.start, args.max_offset, 20))
    fh = open(args.out, "a", encoding="utf-8")
    t0 = time.time()
    added = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for done, jobs in enumerate(pool.map(fetch, offsets), 1):
            for item in jobs:
                key = item.get("guid") or item.get("title")
                if key and key not in seen:
                    seen.add(key)
                    fh.write(json.dumps(item, ensure_ascii=False) + "\n")
                    added += 1
            if done % 100 == 0:
                fh.flush()
                print("offsets %d/%d rows %d added %d %.0fs" % (done, len(offsets), len(seen), added, time.time() - t0), flush=True)
    fh.close()
    print("DONE rows %d added %d in %.0fs" % (len(seen), added, time.time() - t0))


if __name__ == "__main__":
    main()
