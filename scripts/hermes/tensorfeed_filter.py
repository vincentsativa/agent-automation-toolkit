#!/usr/bin/env python3
"""
tensorfeed_filter.py, Strip unwanted recurring stories from TensorFeed before any report.

Fetches https://tensorfeed.ai/api/news, strips articles matching EXCLUDED_PATTERNS
(case-insensitive regex), saves the filtered result to /tmp/tensorfeed_filtered.json,
and prints the count filtered.

Run before ANY TensorFeed report:
    python3 ~/.hermes/scripts/tensorfeed_filter.py
Then read /tmp/tensorfeed_filtered.json (use ONLY the filtered stories).
"""

import json
import re
import sys
import urllib.request

API_URL = "https://tensorfeed.ai/api/news"
OUTPUT_PATH = "/tmp/tensorfeed_filtered.json"

# Case-insensitive regex patterns for stories to EXCLUDE entirely.
# Add exclusions here. Every story whose title or snippet matches any pattern is dropped.
EXCLUDED_PATTERNS = [
    r"openai.*rogue",
    r"rogue.*openai",
    r"hugging\s?face.*breach",
    r"breach.*hugging\s?face",
    r"ai.*kill\s?switch",
    r"kill\s?switch.*act",
    r"agent.*containment.*breach",
    r"containment.*breach",
    r"ai agent.*(escap|hack|compromis)",
    r"(escap|hack|compromis).*ai agent",
]


def fetch_news():
    """Fetch the TensorFeed news API and return the parsed JSON."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "tensorfeed-filter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def matches_exclusion(title, snippet):
    """Return True if the article matches any exclusion pattern."""
    haystack = f"{title or ''} {snippet or ''}".lower()
    for pat in EXCLUDED_PATTERNS:
        if re.search(pat, haystack):
            return True
    return False


def main():
    try:
        data = fetch_news()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: failed to fetch TensorFeed API: {e}", file=sys.stderr)
        sys.exit(1)

    # The news endpoint returns a dict with 'articles'.
    articles = data.get("articles", []) if isinstance(data, dict) else data

    filtered = []
    excluded = 0
    for art in articles:
        if matches_exclusion(art.get("title", ""), art.get("snippet", "")):
            excluded += 1
            continue
        filtered.append(art)

    # Preserve the original structure, replace articles with the filtered list.
    out = dict(data)
    out["articles"] = filtered
    out["filtered_count"] = excluded

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Filtered {excluded} of {len(articles)} stories. Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
