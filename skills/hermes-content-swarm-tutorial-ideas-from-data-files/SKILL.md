---
name: tutorial-ideas-from-data-files
description: 4 ranked Gumroad tutorial ideas from TODAYS DATA FILES.
trigger: "cron job 'Generate 4 Tutorial Ideas from Data Files', or Vinny asks for tutorial ideas based on today's data files"
---

# Tutorial Ideas From Data Files

Recurring daily cron workflow: read the day's AI-news data files in
`Desktop/TODAYS DATA FILES/`, apply an evidence bar to find recurring
developer/beginner pain points, generate exactly 4 ranked tutorial ideas
(2 for developers, 2 for beginners), save a dated report, email it with the
file attached, and send exactly one Telegram confirmation.

## Step 1, Review Existing Content (overlap check)
List every product already on the Gumroad store. **Use the Gumroad API v2, NOT
browser scraping and NOT the `existing_products.txt` fallback file**, the
storefront is a JS SPA (partial HTML payload) and the fallback file is often
empty (0 bytes). The API returns the full catalog in one JSON response:

```python
import urllib.request, json
token = '<access token from ~/.hermes/credentials.md>'
url = 'https://api.gumroad.com/v2/products?access_token=' + token
data = json.loads(urllib.request.urlopen(urllib.request.Request(url), timeout=30).read().decode())
for p in data.get('products', []):
    print(p.get('name'), '|', p.get('price'), '|', p.get('short_url'), '|', p.get('published'))
```

**Token source:** the Gumroad access token lives in `~/.hermes/credentials.md` under the `## Gumroad` heading, field `Access Token`. Read it from there first. If that file is ever missing, fall back to the credentials section of the `gumroad-publisher` skill rather than hunting around the disk.

- `price` is in cents; `0` = free lead magnet. `published` tells you if it's live.
- The API returns the same list on page 1 and page 2 for this account, dedupe by name.
- Capture name + price + short_url for every product. Do NOT propose ideas that
  overlap (including near-duplicates) with existing products.

## Step 2, Analyze the Data (evidence bar)
Read EVERY file in `Desktop/TODAYS DATA FILES/` (excluding existing_products.txt).
Typical files: `20-AI-News-Stories-*.md`, `ironpulse-*.txt`,
`tensorfeed_report_*.txt`, `social-media-posts-*.txt`,
`social-media-questions-*.txt`, `ai-security-board-metadata.txt`.

Identify recurring problems/pain points developers and beginners have around
agentic AI systems.

**Evidence bar (HARD):** a problem only counts if it appears in **at least 2
separate files OR at least 3 times across all files**. Record the source
file(s) and a short quote/paraphrase for each occurrence. Discard anything
below the bar. Do NOT invent or extrapolate pain points the data doesn't
support.

## Step 3, Generate Exactly 4 Ideas
- 2 for developers/engineers (technical depth, code-focused)
- 2 for beginners/newish users (simple, low-barrier entry)

Each idea must:
- Solve a real problem that passed the evidence bar (cite file + quote)
- Not overlap with existing Gumroad products
- Include a suggested price (paid: $19–$49; lead magnet: $0)
- Be labeled PAID PRODUCT or FREE LEAD MAGNET
- Mix: at least 1 paid AND at least 1 free lead magnet (aim 2/2)
- Be producible in ~1 week on Vinny's existing stack (OpenClaw, Ollama, local
  models), no new paid tools or infrastructure

## Step 4, Rank Best to Worst
Order all 4 by:
1. Strength of evidence in the data
2. Fit with existing skills/infrastructure (speed to produce)
3. Revenue or lead-gen potential

For the top 2, write a short explanation (2–3 sentences each) of why they're
the strongest choices.

## Step 5–6, Create + Save the Deliverable
Write a well-formatted text document with all 4 ranked ideas, price/lead-magnet
designation, evidence reference (source file + quote) for each, and explanation
for the top 2 picks.

Save to `Desktop/TUTORIAL IDEAS/TutorialIdeas_YYYY-MM-DD.txt` (today's date).
If that name exists, use `_v2`, `_v3`, etc. Do NOT overwrite prior files.
After saving, verify the file exists and is complete (read back the tail).

Keep body paragraphs unwrapped, one long line each, and verify with
`awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>` before delivering. Hyphens only, never em dashes.

These reports are the archive that later "pick the best N" jobs mine, so keep the
heading stable (`IDEA n - PAID PRODUCT - $N` then `Title:`) and keep the
`Evidence count:` line in a fixed shape. See `top-n-from-folder` for the parser
that reads this archive, including the format-drift pitfall.

## Step 7, Email
Send to `hello@phantom-byte.com` (verify TO + any addresses in the body via
grep before sending, see email-sender skill). Subject: `4 tutorials based on
the data`. Attach the text document (REQUIRED). Body: brief summary of the 4
ideas, 1–2 lines each with price. Sign `- Bill`. If attach fails, retry once;
if it still fails, stop and report, do NOT proceed to Step 8 as success.

## Step 8, Telegram
Send exactly ONE Telegram message saying the email has been sent. If Step 7
failed, send one message reporting the failure instead. No other Telegram
messages for this task.

## Pitfalls
- Do NOT skip the overlap check, always re-extract the current catalog via the
  Gumroad API before proposing ideas.
- Do NOT use browser scraping or the empty `existing_products.txt` fallback for
  the catalog, the API is the reliable source.
- Do NOT lower the evidence bar to fill the 4-idea quota. If fewer than 4
  problems pass, return fewer ideas rather than padding with weak ones.
- Do NOT fabricate quotes or pain points, every idea must trace to a real data
  file with a real quote.
- Do NOT claim success until the file is saved+verified, the email sent with
  attachment, and exactly one Telegram message delivered.
