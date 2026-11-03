#!/usr/bin/env python3
"""Find the latest full release and latest RC prerelease for a GitHub project.

Usage:
    python3 find-latest-rc.py ollama/ollama
    python3 find-latest-rc.py ollama/ollama --platform windows

Outputs the latest full release and the latest RC tag (including tag-only RCs).
If --platform is given, checks which of those have compiled assets matching the platform.
"""

import json
import sys
import urllib.request

OWNER_REPO = sys.argv[1] if len(sys.argv) > 1 else "ollama/ollama"
PLATFORM_FILTER = None
if len(sys.argv) > 2 and sys.argv[2] == "--platform":
    PLATFORM_FILTER = sys.argv[3] if len(sys.argv) > 3 else None


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "find-release-script/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def tag_key(tag_name):
    v = tag_name.lstrip("v")
    parts = v.split("-")
    base = parts[0].split(".")
    rc = int(parts[1][2:]) if len(parts) > 1 and parts[1].startswith("rc") else 9999
    return [int(x) for x in base] + [rc]


def fetch_all_releases():
    """Fetch all releases across all pages."""
    data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{OWNER_REPO}/releases?per_page=100&page={page}"
        batch = fetch_json(url)
        if not isinstance(batch, list) or len(batch) == 0:
            break
        data.extend(batch)
        page += 1
        if page > 5:
            break
    return data


def fetch_all_tags():
    """Fetch all git tags across all pages."""
    data = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{OWNER_REPO}/tags?per_page=100&page={page}"
        batch = fetch_json(url)
        if not isinstance(batch, list) or len(batch) == 0:
            break
        data.extend(batch)
        page += 1
        if page > 5:
            break
    return data


releases = fetch_all_releases()
tags = fetch_all_tags()

all_tag_names = {t["name"] for t in tags}

# Filter non-draft releases
valid = [r for r in releases if not r.get("draft")]
full = [r for r in valid if not r.get("prerelease")]
pres = [r for r in valid if r.get("prerelease")]

# Latest full release
full_sorted = sorted(full, key=lambda r: tag_key(r["tag_name"]), reverse=True)
if full_sorted:
    r = full_sorted[0]
    print(f"Latest full: {r['tag_name']} ({r['published_at'][:10]})")
    if PLATFORM_FILTER:
        assets = [a for a in r.get("assets", []) if PLATFORM_FILTER in a["name"].lower()]
        print(f"  Matched assets ({len(assets)}): {', '.join(a['name'] for a in assets)}")

# Latest prerelease (from releases API)
pre_sorted = sorted(pres, key=lambda r: tag_key(r["tag_name"]), reverse=True)
if pre_sorted:
    r = pre_sorted[0]
    print(f"Latest pre (release): {r['tag_name']} ({r['published_at'][:10]})")
    if PLATFORM_FILTER:
        assets = [a for a in r.get("assets", []) if PLATFORM_FILTER in a["name"].lower()]
        print(f"  Matched assets ({len(assets)}): {', '.join(a['name'] for a in assets) if assets else 'NONE'}")
else:
    print("No prerelease releases found")

# Latest RC tag (including tag-only)
rc_tags = sorted([t["name"] for t in tags if "rc" in t["name"].lower()], key=tag_key, reverse=True)
if rc_tags:
    newest_rc = rc_tags[0]
    # Check if it has a release entry
    has_release = any(r.get("tag_name") == newest_rc for r in valid)
    status = "has release page" if has_release else "TAG ONLY (no release entry, no builds)"
    print(f"Latest RC tag: {newest_rc} ({status})")

# Check all RC tags that are tag-only
tag_only_rcs = [t for t in rc_tags if not any(r.get("tag_name") == t for r in valid)]
if tag_only_rcs:
    print(f"\nTag-only RCs (no release/build assets): {', '.join(tag_only_rcs[:5])}...")
