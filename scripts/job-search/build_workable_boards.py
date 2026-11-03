"""Build the employer-board cache that replaces the rate-limited Workable search API.

Workable's job-board search endpoint (jobs.workable.com/api/v1/jobs) rate-limits by
IP and returns {"error":"rate_limit"} for hours at a time. On October 23, 2026 that
killed the deep pass outright: 0 records, and Workable was supplying 41 of the 65
usable leads that day. The employer's own board endpoint is a different service on
a different host and does not share that ban:

    https://apply.workable.com/api/v1/widget/accounts/<slug>?details=true

It returns the employer's postings with application_url, telecommuting, location
and employment_type, so every row is a direct-apply row with no account wall.

This script resolves company names to board slugs once, verifies each slug against
the account name the API returns, and caches the result in config/workable-boards.json.
Collection then reads the cache instead of guessing every run.

Usage:
    python build_workable_boards.py [--limit 120] [--sleep 1.5] [--date YYYY-MM-DD]
"""

import argparse
import json
import os
import re
import sys
import time

# urllib.request loads socket and select before requests touches them. The script
# directory is sys.path[0] and holds select.py, which would otherwise shadow the
# standard library select module during requests' import chain.
import urllib.request  # noqa: F401
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
CACHE = os.path.join(HERE, "..", "config", "workable-boards.json")
API = "https://apply.workable.com/api/v1/widget/accounts/%s?details=true"


def normalise(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def slug_variants(company):
    base = re.sub(r"[^a-z0-9 ]", "", (company or "").lower())
    drop = {"inc", "llc", "ltd", "corp", "corporation", "co", "the", "group", "company",
            "limited", "gmbh", "plc", "llp"}
    words = [w for w in base.split() if w not in drop]
    if not words:
        words = base.split()
    out = []
    for cand in ("".join(words), "-".join(words), "".join(words[:2]), "-".join(words[:2]),
                 words[0], "-".join(words[:3]), "".join(words[:3])):
        if cand and cand not in out:
            out.append(cand)
    return out[:6]


def probe(slug):
    """Return the account payload for a slug, or None. Waits out a 429."""
    for attempt in range(4):
        try:
            r = requests.get(API % slug, headers=UA, timeout=20)
        except Exception:
            time.sleep(2 + attempt * 2)
            continue
        if r.status_code == 200:
            try:
                return r.json()
            except Exception:
                return None
        if r.status_code in (429, 503):
            time.sleep(8 + attempt * 8)
            continue
        return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--sleep", type=float, default=1.5)
    args = ap.parse_args()

    rules = C.config("rules.json")
    include = rules.get("include_title_patterns") or []
    run = C.run_dir(args.date)

    names = {}
    for row in C.load_jsonl(os.path.join(run, "raw.jsonl")):
        if row.get("source") != "workable":
            continue
        title = row.get("title") or ""
        if not any(re.search(p, title) for p in include):
            continue
        company = (row.get("company") or "").strip()
        if company:
            names[company] = names.get(company, 0) + 1

    ordered = [n for n, _ in sorted(names.items(), key=lambda kv: -kv[1])]

    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding="utf-8"))
    boards = cache.get("boards") or {}

    done = 0
    found = 0
    for company in ordered:
        if done >= args.limit:
            break
        if company in boards:
            continue
        for slug in slug_variants(company):
            payload = probe(slug)
            done += 1
            if payload and normalise(payload.get("name")) == normalise(company):
                boards[company] = slug
                found += 1
                print("  + %-34s %-28s %d jobs" % (company[:34], slug, len(payload.get("jobs") or [])), flush=True)
                break
            time.sleep(args.sleep)
        time.sleep(args.sleep)

    cache["boards"] = boards
    cache["_comment"] = ("Company name to Workable board slug, verified against the account name the "
                         "widget API returns. Read by collect.py when the Workable search endpoint is "
                         "rate-limited. Rebuild with build_workable_boards.py.")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("probed %d slugs, resolved %d new boards, cache holds %d" % (done, found, len(boards)))


if __name__ == "__main__":
    main()
