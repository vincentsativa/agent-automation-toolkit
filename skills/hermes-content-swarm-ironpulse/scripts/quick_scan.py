#!/usr/bin/env python3
"""IronPulse quick scan: one pass, 24h window, no file output.

Usage:  python3 ~/.hermes/skills/content-swarm/ironpulse/scripts/quick_scan.py

Prints "<age>h | <source> | <headline>" sorted newest first, then a total.
Run this ONE script and answer from its output. Verified 0.6s, 74 stories.
"""

import urllib.request, gzip, re, html, datetime, email.utils, xml.etree.ElementTree as ET

FEEDS = {
    "TechCrunch": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "WIRED":      "https://www.wired.com/feed/tag/ai/latest/rss",
    "GoogleNews": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
}
now = datetime.datetime.now(datetime.timezone.utc)
rows = []
for name, url in FEEDS.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        raw = urllib.request.urlopen(req, timeout=20).read()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        root = ET.fromstring(raw.decode("utf-8", "replace"))
    except Exception as e:
        print("FEED FAILED:", name, e)
        continue
    for item in root.iter("item"):
        title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", item.findtext("title") or ""))).strip()
        pub = (item.findtext("pubDate") or "").strip()
        try:
            # email.utils handles both "+0000" and "GMT" zones; strptime's %z does not handle GMT.
            d = datetime.datetime(*email.utils.parsedate(pub)[:6], tzinfo=datetime.timezone.utc)
        except Exception:
            continue
        age = (now - d).total_seconds() / 3600
        if 0 <= age <= 24:
            rows.append((age, name, title))
rows.sort()
for age, name, title in rows[:15]:
    print("%5.1fh | %-10s | %s" % (age, name, title[:95]))
print("TOTAL stories within 24h:", len(rows))
