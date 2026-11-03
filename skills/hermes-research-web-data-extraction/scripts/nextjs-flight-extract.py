#!/usr/bin/env python3
"""Parse a Next.js / React Server Components flight payload out of a page's HTML.

Use when a catalog page renders client-side from an embedded JSON payload:
get_all_text() returns only nav and filter labels, and page.text is empty.

Usage:
    python nextjs-flight-extract.py <url> [array-key]

    array-key defaults to "resources". It is the JSON key whose array holds the
    rows you want, e.g. "resources", "items", "results", "data".

Prints: status, detected render mode, declared totals, row count, and the rows.
Requires scrapling (from scrapling.fetchers import Fetcher).

Set ARRAY_KEY to whatever the site uses; find it by grepping the decoded blob
for '"<key>":['. Rows are printed as JSON so nothing is silently reshaped.
"""

import json
import re
import sys

from scrapling.fetchers import Fetcher


def decode_page(page):
    """page.text is often empty on these sites; fall back to raw bytes."""
    body = page.body
    if isinstance(body, bytes):
        for enc in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return body.decode(enc)
            except Exception:
                continue
    return str(body)


def flight_blob(html):
    """Join every self.__next_f.push chunk, then unescape into one JSON blob."""
    if "__NEXT_DATA__" in html:
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if m:
            return "NEXT_DATA_JSON:" + m.group(1), "__NEXT_DATA__"
    chunks = re.findall(r'<script>self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    if not chunks:
        return None, "none"
    # Chunks split mid-JSON-string: concatenate FIRST, decode SECOND.
    return "".join(chunks).encode().decode("unicode_escape"), "flight"


def bracket_match(blob, key):
    """Find "key":[ and return the parsed array by bracket matching to depth 0.

    Never regex for {...}: nested objects terminate the match early and drop rows.
    """
    marker = '"%s":[' % key
    i = blob.find(marker)
    if i < 0:
        return None
    seg = blob[i + len(marker):]
    depth = 0
    for j, ch in enumerate(seg):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(seg[: j + 1])
                except Exception as exc:
                    print("PARSE FAIL: %s" % exc, file=sys.stderr)
                    return None
    return None


def declared_totals(blob):
    out = {}
    for key in ("resultTotal", "resultPageTotal", "totalCount", "total"):
        m = re.search(r'"%s":(\d+)' % key, blob)
        if m:
            out[key] = int(m.group(1))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    url = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else "resources"

    page = Fetcher().get(url, follow_redirects=True)
    html = page.html_content or decode_page(page)
    print("status: %s  html_bytes: %d" % (page.status, len(html)))

    blob, mode = flight_blob(html)
    print("render mode: %s" % mode)
    if not blob:
        print("No embedded JSON payload. This page is not a flight/Next.js catalog; "
              "use CSS selectors or get_all_text() on it instead.")
        return 1

    if blob.startswith("NEXT_DATA_JSON:"):
        data = json.loads(blob.split(":", 1)[1])
        print(json.dumps(data, indent=1)[:4000])
        return 0

    print("declared totals: %s" % declared_totals(blob))
    rows = bracket_match(blob, key)
    if rows is None:
        print("No '%s' array in the payload. Keys present:" % key)
        for m in re.finditer(r'"([A-Za-z_][A-Za-z0-9_]*)":\[', blob):
            print("   -", m.group(1))
        return 1

    print("rows parsed: %d" % len(rows))
    print(json.dumps(rows, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
