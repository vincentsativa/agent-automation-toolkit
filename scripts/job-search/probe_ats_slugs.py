"""Probe employer board slugs before adding them to config/companies.json.

Usage:
    python probe_ats_slugs.py notion stripe asg boldly seerinteractive lwolf

Every slug is tried against Greenhouse, Lever and Ashby in parallel. Prints one
line per slug with the live posting count and the vendor that answered, then the
JSON-ready arrays to paste into config/companies.json. A slug with zero postings
is either the wrong slug or a dead board; do not add it.

Ashby answers 403 to urllib's default user agent, so every request carries a
browser UA. Stdlib only, safe under Python 3.11.
"""

import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
VENDORS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}
TIMEOUT = 20


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def count_postings(vendor, payload):
    if vendor == "lever":
        return len(payload) if isinstance(payload, list) else 0
    return len((payload or {}).get("jobs") or [])


def probe(slug):
    hits = {}
    for vendor, template in VENDORS.items():
        try:
            payload = fetch_json(template.format(slug=slug))
            total = count_postings(vendor, payload)
            if total:
                hits[vendor] = total
        except Exception:
            continue
    return slug, hits


def main(argv):
    slugs = [s.strip().lower() for s in argv if s.strip()]
    if not slugs:
        print(__doc__)
        return 1
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(probe, slugs))
    buckets = {"greenhouse": [], "lever": [], "ashby": []}
    dead = []
    for slug, hits in sorted(results):
        if not hits:
            dead.append(slug)
            print("%-30s no live postings on any vendor" % slug)
            continue
        summary = ", ".join("%s=%d" % (vendor, total) for vendor, total in sorted(hits.items()))
        print("%-30s %s" % (slug, summary))
        for vendor in hits:
            buckets[vendor].append(slug)
    print("")
    print("add to config/companies.json (live slugs only):")
    print(json.dumps({k: v for k, v in buckets.items() if v}, indent=2))
    if dead:
        print("dead or misspelled, do not add: %s" % ", ".join(dead))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
