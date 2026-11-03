#!/usr/bin/env python3
"""RSS-first AI-news headline discovery for cron sessions.

Usage:  python3 rss_discover.py [feed_key]
        python3 rss_discover.py all          # iterate every feed below

Feed keys: techcrunch, venturebeat, ars, wired, mittr, googlenews
Runs via `terminal()` (execute_code is BLOCKED in cron mode).
Prints "pubDate | title | link" per item so you can filter freshness by date.
"""
import sys
import xml.etree.ElementTree as ET
from scrapling.fetchers import Fetcher

FEEDS = {
    "techcrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "venturebeat": "https://venturebeat.com/category/ai/feed/",
    "ars": "https://arstechnica.com/ai/feed/",
    "wired": "https://www.wired.com/feed/tag/ai/latest/rss",
    "mittr": "https://www.technologyreview.com/feed/",
    "googlenews": "https://news.google.com/rss/search?q=artificial+intelligence+OR+AI&hl=en-US&gl=US&ceid=US:en",
}


def parse(url, limit=25):
    f = Fetcher()
    r = f.get(url, follow_redirects=True)
    root = ET.fromstring(r.body if hasattr(r, "body") else r.content)
    out = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub = item.findtext("pubDate", "").strip()
        if title:
            out.append((pub, title, link))
        if len(out) >= limit:
            break
    return out


def main():
    keys = sys.argv[1:]
    if not keys:
        keys = ["techcrunch"]
    if keys == ["all"]:
        keys = list(FEEDS)
    for key in keys:
        url = FEEDS.get(key)
        if not url:
            print(f"unknown feed: {key}")
            continue
        print(f"=== {key} ===")
        for pub, title, link in parse(url):
            print(f"{pub} | {title} | {link}")
        print()


if __name__ == "__main__":
    main()
