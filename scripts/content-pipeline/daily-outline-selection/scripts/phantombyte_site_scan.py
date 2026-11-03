"""Scan articles.phantom-byte.com for outline-selection overlap checks.

Run with the Python interpreter that has scrapling installed, and run it from
this skill's own directory. Do NOT write a scratch copy into the Hermes scratch
dir: that dir holds helper modules named after stdlib modules (`select.py`,
`inspect.py`, `common.py`), and Python puts a script's own directory on
sys.path, so the copy shadows the stdlib and dies on a misleading
circular-import error deep inside urllib.

    PY=~/AppData/Local/Programs/Python/Python311/python
    "$PY" scripts/phantombyte_site_scan.py [out_dir] [slug_for_note_metadata]

Prints:
  * the pinned latest note (the featured card, which is NOT always present in
    the numbered rail) and its note number,
  * every archive card as NOTE #N, category, title, slug, so a cluster can be
    argued by note number in the answer without a second pass,
  * category counts from the cards, plus notes in the thin categories,
  * the homepage category taxonomy (the full chip set),
  * the LIVE category rail read from the pinned latest note,
  * the slug list, written to <out_dir>/phantombyte_slugs.txt for grepping.

The rail is read from the newest note page on purpose. Every note page embeds the
rail as it stood on its publish date, so an older note reports a frozen count.
The counts live in the page's archChips block, not in the visible text, so parse
html_content. Do not swap this for a visible-text regex: get_all_text() puts the
category label and its number on separate lines, which defeats `All \\d+`.
"""

import os
import re
import sys
from collections import Counter

from scrapling.fetchers import Fetcher

BASE = "https://articles.phantom-byte.com"
SKIP = {"index.html", "privacy.html", "terms.html"}

# One archive card, current layout:
#   <a href="slug.html" ...><div class="thumb"><img alt="TITLE" ...>
#   <span class="pcat">CATEGORY</span><span class="pidx">#N</span></div>
# The card carries title, category and note number together, which is what an
# overlap argument needs. The slug list alone gives topic only.
CARD_RE = re.compile(
    r'<a[^>]+href="([^"]+\.html)"[^>]*>\s*<div class="thumb"><img[^>]*alt="([^"]*)"[^>]*>'
    r'<span class="pcat">([^<]*)</span><span class="pidx">#(\d+)',
    re.S,
)


def fetch(url):
    page = Fetcher().get(url, follow_redirects=True)
    text = page.get_all_text() or ""
    html = page.html_content or ""
    return page.status, text, html


def parse_cards(html):
    """Return [(note_number, category, title, slug)] for the whole archive rail."""
    rows = [
        (int(m.group(4)), m.group(3).strip(), " ".join(m.group(2).split()), m.group(1))
        for m in CARD_RE.finditer(html)
    ]
    rows.sort()
    return rows


def parse_taxonomy(html):
    """Return the homepage data-cat chip set: the FULL category list."""
    cats = {c for c in re.findall(r'data-cat="([^"]+)"', html) if "'" not in c and "+" not in c}
    return sorted(cats)


def parse_rail(html):
    """Return [(category, count)] from the archChips block, [] when absent."""
    block = re.search(r'id="archChips"(.{0,2500}?)</div>', html, re.S)
    if not block:
        return []
    rows = re.findall(r'data-cat="([^"]+)">.*?<span class="ac-c">(\d+)</span>', block.group(1), re.S)
    return [(cat, int(n)) for cat, n in rows]


def resolve_latest(html):
    """Newest note slug: featured card first, then the rail, then highest note #."""
    for pat in (
        r'class="feat-go"[^>]*href="([^"]+\.html)"',
        r'href="([^"]+\.html)"[^>]*class="feat-go"',
        r'class="arch-item"[^>]*href="([^"]+\.html)"',
    ):
        match = re.search(pat, html)
        if match:
            return match.group(1)
    cards = parse_cards(html)
    return cards[-1][3] if cards else None


def note_meta(text):
    joined = " ".join(text.split())
    note = re.search(r"NOTE #(\d+)", joined)
    head = re.search(r"SECTION: \| ([A-Z &]+?) \|", joined)
    date = re.search(r"\u00b7 ([A-Z]{3} \d{2} \d{4}) \u00b7", joined)
    return (
        note.group(1) if note else "?",
        head.group(1).strip() if head else "?",
        date.group(1) if date else "?",
    )


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    slug_arg = sys.argv[2] if len(sys.argv) > 2 else None

    status, text, html = fetch(BASE)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print("homepage status:", status, "text chars:", len(text))

    if "// LATEST" in lines:
        i = lines.index("// LATEST")
        print("\n=== PINNED LATEST ===")
        for line in lines[i:i + 9]:
            print(line)
    else:
        print("\nPINNED LATEST block not found. Page layout changed; read the homepage text directly.")

    cards = parse_cards(html)
    print("\n=== ARCHIVE CARDS (note #, category, title) ===")
    print("cards parsed:", len(cards), "| note range:",
          "#%d-#%d" % (cards[0][0], cards[-1][0]) if cards else "-")
    for n, cat, title, slug in cards:
        print("#%d | %s | %s | %s" % (n, cat, title, slug))

    counts = Counter(cat for _, cat, _, _ in cards)
    print("\n=== CATEGORY COUNTS (from cards; add the pinned latest to its category) ===")
    for cat, n in counts.most_common():
        print("%s %d" % (cat, n))

    print("\n=== THIN CATEGORIES (<= 6 notes, list them to argue a thin-category pick) ===")
    for cat, n in counts.items():
        if n <= 6:
            print(cat, n, ["#%d" % c[0] for c in cards if c[1] == cat])

    print("\n=== HOMEPAGE CATEGORY TAXONOMY (full chip set, includes zero-note entries) ===")
    print(", ".join(parse_taxonomy(html)))
    print("A category named by an outline but absent here does not exist on the site at all,")
    print("so the note needs an existing category or the category needs adding. Report that.")

    print("\n=== ARCHIVE (slugs) ===")
    slugs = sorted({s for s in re.findall(r'href=["\']([^"\']+\.html)["\']', html) if s not in SKIP})
    slug_path = os.path.join(out_dir, "phantombyte_slugs.txt")
    with open(slug_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(slugs) + "\n")
    print("article slugs:", len(slugs))
    print("slug list written:", slug_path)

    rail_slug = resolve_latest(html)
    if rail_slug:
        _, rail_text, rail_html = fetch(BASE + "/" + rail_slug)
        rail = parse_rail(rail_html)
        note, sec, date = note_meta(rail_text)
        print("\n=== LIVE CATEGORY RAIL (from pinned latest note) ===")
        print("source note:", rail_slug, "| NOTE #" + note, "|", sec, "|", date)
        if rail:
            print(" ".join("%s %d" % (cat, n) for cat, n in rail))
        else:
            print("archChips block not found; page layout changed, read the note page html_content directly.")
    else:
        print("\nnewest slug not found in the homepage rail; pass a slug explicitly.")

    if slug_arg:
        _, a_text, _ = fetch(BASE + "/" + slug_arg.replace(".html", "") + ".html")
        note, sec, date = note_meta(a_text)
        print("\n=== NOTE METADATA: " + slug_arg + " ===")
        print("note #" + note, "|", sec, "|", date)


if __name__ == "__main__":
    main()
