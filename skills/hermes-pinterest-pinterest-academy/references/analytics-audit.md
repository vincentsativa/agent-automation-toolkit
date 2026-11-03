# Pinterest Analytics Audit — working recipe

Mechanics for turning a Pinterest analytics export into board and cron decisions. The rules live in SKILL.md; this file is the how.

## 1. The pinned set (what is already on the boards)

Board RSS returns the most recent ~25 pin entries per board, which is enough for a dedup or a topic audit. Run the packaged script instead of hand-rolling it:

```bash
python3 ~/.hermes/scripts/pinterest_dedup.py
```

Quirk to know before parsing it: in a board feed, the RSS `<title>` element carries the pin's TITLE TOGETHER WITH its whole description text, so a feed title is not the pin's title and is not a length-checkable field. The board name is the feed title, the rest are pins.

## 2. A pin's real destination (the export does not carry it)

The analytics export has no destination column. To find where a pin actually sends a visitor, fetch the pin page and read the embedded pin JSON. The fields that matter:

- `"link"` — the destination URL on the pin
- `"domain"` — the destination host
- `"linkDomain"` — the host plus the account that owns it if the domain is claimed, `"officialUser":null` if it is not
- `"method"` — how the pin was created, e.g. `pin_scheduling`

Working fetch (scrapling is not on the default python path on this box, so invoke the venv binary and save HTML, then parse it):

```bash
SCRATCH=$(mktemp -d /tmp/hermes-pin-XXXXXX)
~/.venv/bin/scrapling extract get "https://www.pinterest.com/pin/<PIN_ID>/" "$SCRATCH/pin.html"
```

Then regex the saved file for `"link":"(https?://[^"]+)"`, `"domain":"(...)"`, and `"linkDomain"`. Two traps: `og:description` is usually absent on a pin page, so the pin's description cannot be read from meta tags; and `og:title`/`<title>` is the pin's display title, which is a different string from what the board RSS reports for the same pin.

Batch note: pin pages run 1.2 MB each and take roughly 20 to 30 seconds apiece. A full top-pins list is a background job, not a foreground loop, and the results belong in a JSON file in the scratch dir so a timeout does not lose them.

## 3. Reading the analytics export itself

Header block gives the date range and the filters; the body gives per-day impressions; then Top Boards and Top Pins tables.

- **Sum impressions into weekly buckets before drawing a conclusion.** Day-level numbers swing wildly and one spike or dip is noise. Four weekly sums show whether reach is rising or decaying.
- **Exclude estimated days.** The export footer says which date onwards is an estimate that gets adjusted. A spike inside that window is not evidence of anything yet.
- **Compute per-board RATES, not totals.** For each board divide engagement, Pin clicks, and Saves by that board's own impressions. The board with the most impressions is frequently not the board with the best rate.
- **Outbound clicks ÷ Pin clicks** is the only ratio that says whether traffic leaves Pinterest. Saves and engagement feed distribution but do not move a visitor to the site.
- **The Canonical column is the claimed-domain flag.** A pin row reads Canonical `Yes` only when its destination domain is claimed by the account; unclaimed destinations read `No`.
- **Top Pins is capped by impressions, not by date.** The listed pins are the ones that carried the reach for the whole window, and the tail of everything else contributes little. Compare the count of listed pins against the number of pins actually published in the window before calling the publishing rate productive.

## 4. Checking the posts the cron writes

Before touching the cron, measure what it has actually produced. The daily posts file format is a `[BOARD] - Title` line, a blank line, then the description, with a blank line between posts. Split on blank lines and walk the blocks in pairs:

```python
import re, glob, os
for f in sorted(glob.glob("~/pinterest_posts_*.txt")):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", open(f, encoding="utf-8", errors="ignore").read()) if b.strip()]
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b.startswith("["):
            desc = blocks[i + 1] if i + 1 < len(blocks) and not blocks[i + 1].startswith("[") else ""
            i += 2 if desc else 1
            title = re.sub(r"^\[.*?\]\s*[-\u2014]\s*", "", b)
            if len(title) > 100 or len(desc) > 500:
                print(os.path.basename(f), len(title), len(desc), b[:60])
        else:
            i += 1
```

Report over-limit posts as a count by date, not as one example: a single file with most of a batch over the limit points at the prompt's escape hatch, while a scattered one-here-one-there pattern points at the writer.
