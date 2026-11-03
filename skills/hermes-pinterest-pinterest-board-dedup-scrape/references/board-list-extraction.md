# Extracting a Profile's Board List via Scrapling

Use when you need the list of boards (names + URLs/slugs) for a Pinterest account, e.g. "what boards do I have?" or auditing board coverage against keyword clusters.

## Working method

Fetch the profile's `/boards/` page and regex the raw HTML. The board names and URLs are NOT in one tidy JSON blob, they live in separate attributes, so you must pair them per-card.

```python
from scrapling.fetchers import StealthyFetcher
import re, html

# Pinterest auto-creates default topic boards on every new account. These are
# NOT user-created and must be stripped before reporting a board count or list.
# 'Created' and 'Saved' are also auto-boards (not user boards).
AUTO_BOARDS = {
    'Created', 'Saved',
    # Default seeded topic boards Pinterest ships on new accounts:
    'Entertainment: Music, Jokes, Stars, Films, Games',
    'My Dream Home', 'Fashion', 'DIY', 'Recipes', 'Travel',
}
def is_auto_board(name):
    return name in AUTO_BOARDS

sf = StealthyFetcher()
page = sf.fetch('https://www.pinterest.com/<username>/boards/',
                headless=True, network_idle=True, timeout=60000)
txt = page.body.decode('utf-8','ignore')

# Split into one chunk per board card, then extract name + href from EACH chunk.
chunks = re.split(r'(?=data-test-id="board-rep-tap-area-link")', txt)
seen = set()
for ch in chunks:
    name_m = re.search(r'data-test-id="boardCard-([^"]+)"', ch)
    href_m = re.search(r'href="(/<username>/[^"]+/)"', ch)
    if name_m and href_m:
        name = html.unescape(name_m.group(1))
        if name in seen or is_auto_board(name):
            continue
        seen.add(name)
        print(f"{name}\n    https://www.pinterest.com{href_m.group(1)}\n")
```

The `AUTO_BOARDS` set and `is_auto_board()` filter strip Pinterest's default
seeded topic boards AND the `Created`/`Saved` auto-boards before any name is
printed. Only boards the user actually built are output, so a raw scrape can
never over-report the count again.

## Pitfalls (each one bit this session)

- **Simple `"name":"..."` / `"board_name":"..."` regex is useless.** The raw HTML contains tons of JS-internal strings (e.g. `beforeWriteHeadChunked`, `buildResponder`, `getInitialProps`, `middleware`, `headPromise`) that match those patterns and swamp the real board names. Don't try to filter a keyword list out of the noise, use the `boardCard-` attribute instead, which only appears on real board cards.
- **Board name and URL are in separate elements.** Grabbing all `boardCard-<name>` matches and all `href` matches separately pairs them OFFSET (name N maps to the wrong href). You must split on `data-test-id="board-rep-tap-area-link"` and extract both name and href from within the same chunk.
- **`href` capture must be scoped to the chunk** (`href="(/<username>/[^"]+/)"`). A naive `.*?` across the whole page grabs the first href anywhere, which is the wrong board.
- **Always `html.unescape` the name**, Pinterest encodes `&` as `&amp;` in `data-test-id` (e.g. "AI News | Machine Learning &amp; Emerging Tech").
- **Filter the auto-boards**: `Created`, `Saved`, and a fresh account's default `Entertainment: Music, Jokes, Stars, Films, Games` board are NOT user boards. Pinterest ships this default "Entertainment" board on new accounts; it looks like a real user board but is auto-generated. Exclude ALL of these before reporting a board count or doing coverage analysis. Counting the Entertainment default as one of the user's boards over-reports the count by one (this exact miscount cost a session, I reported 5 boards when Vinny had 4 real ones, and he called it out).

## Why not the browser path

`browser_snapshot`/console extraction often returns empty on Pinterest (shadow DOM + lazy loading). Scrapling + regex over raw HTML is the reliable path here, same reason the main SKILL.md uses it for pin dedup.
