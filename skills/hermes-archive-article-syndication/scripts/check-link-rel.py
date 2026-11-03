#!/usr/bin/env python3
"""Print the rel attribute on every in-body outbound link of a live article.

Use before claiming whether a platform's links are followed. Reputation is not
evidence; the rendered markup is.

Usage:
    python3 check-link-rel.py https://dev.to/some-author/some-slug-abc123
"""

import re
import sys

from scrapling.fetchers import Fetcher

# Templated sitewide links (chrome, sidebar, footer, cross-promo). Their rel does
# not tell you anything about what an author's body link is worth.
IGNORE_HOSTS = (
    "algolia.com",
    "forem.com",
    "mlh.io",
    "x.com",
    "twitter.com",
    "facebook.com",
    "instagram.com",
    "twitch.com",
    "fosstodon.org",
    "bsky.app",
)


def link_rels(url: str) -> list[tuple[str, str]]:
    page = Fetcher.get(url, stealthy_headers=True)
    html = page.html_content
    if not html:
        raise SystemExit(f"empty response for {url}")

    out = []
    for href, attrs in re.findall(r'<a[^>]+href="(https?://[^"]+)"([^>]*)>', html):
        if any(host in href for host in IGNORE_HOSTS):
            continue
        match = re.search(r'rel="([^"]*)"', attrs)
        out.append((href, match.group(1) if match else "NO-REL"))
    return out


def verdict(rels: list[str]) -> str:
    joined = " ".join(rels).lower()
    if "nofollow" in joined or "ugc" in joined or "sponsored" in joined:
        return "NOFOLLOW (no link equity)"
    return "FOLLOWED (link equity passes)"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)

    rels = []
    for href, rel in link_rels(sys.argv[1]):
        rels.append(rel)
        print(f"{rel:<28} {href[:110]}")

    if not rels:
        raise SystemExit("\nNo in-body outbound links found. Pick an article that "
                         "actually links out before drawing a conclusion.")

    print(f"\n{len(rels)} in-body outbound links  ->  {verdict(rels)}")
