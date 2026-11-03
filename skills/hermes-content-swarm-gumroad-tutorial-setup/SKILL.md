---
name: gumroad-tutorial-setup
description: Create a new Gumroad tutorial product from a text file — read the source, craft name/description/summary/slug, POST to API, set permalink, and deliver the draft URL. Description MUST be HTML. Verify by loading the product page in browser.
trigger: "user says 'use the gumroad api and create a new tutorial' or 'set up a gumroad tutorial' or provides a tutorial text file path for Gumroad publishing"
---

# Gumroad Tutorial Setup

## CRITICAL RULES (read before anything else)

1. **HTML ONLY for descriptions.** Gumroad does NOT render plaintext newlines as paragraph breaks. A description with `\n\n` will appear as one wall of text on the product page. Every paragraph MUST be wrapped in `<p>`, every list in `<ul><li>`, every bold header in `<strong>`.

2. **Verify by loading the product page in browser.** The API response may show the description correctly with escaped newlines, but the rendered page can still be wrong. Always navigate to the product URL and check the page visually.

3. **The user's instructions are orders, not suggestions.** Do exactly what is asked, exactly how it is asked, on the first attempt. No iteration. No excuses.

4. **No em dashes anywhere.** Use commas, colons, periods, or hyphens.

5. **For free products, price=0.** For paid products, price in cents ($0.99 = 99, $9.99 = 999).

## Credentials

- **Account:** phantombyteai.gumroad.com
- **Access Token:** `_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE`
- **API Base:** `https://api.gumroad.com/v2/`

## Workflow

### Step 1: Read the Source Material

Read the tutorial text file from the path the user provides. Extract the title from the first heading line. Understand the full content to write a proper description and summary.

### Step 2: Craft the Product Fields

**Name:** The tutorial title from the file. Keep it clean and professional.

**Custom Summary** (short, 1-2 sentences, appears under the product name):
- Hook: the problem the user is paying to solve
- What they get: the solution in plain terms
- Outcome: what changes for them after reading
- Max ~300 characters

**Description** (full product page body text) — MUST be HTML. Do NOT use plaintext with newlines. Gumroad renders HTML natively.

**HTML STRUCTURE (non-negotiable, follow exactly):**

```
<p>Opening hook. 1-3 punchy sentences. Each sentence stands alone.</p>
<p>Context paragraph. Explains the problem or why it matters. 2-4 sentences.</p>
<p>Transition sentence. One line introducing what the product covers.</p>
<p><strong>What You'll Learn</strong></p>
<ul>
<li>Bullet one. Specific skill or concept.</li>
<li>Bullet two.</li>
<li>Bullet three.</li>
</ul>
<p>Closing paragraph. 1-4 sentences.</p>
<p>Free. Because the only thing better than an agent that answers questions is an agent that does not need to be asked.</p>
```

**HARD RULES:**
- **NO EM DASHES.** Use commas, colons, periods, or hyphens.
- **HTML ONLY.** No plaintext newlines. No markdown.
- **Each paragraph is 1-4 sentences.** Shorter is better.
- **Bold headers only for section titles** (e.g. `<strong>What You'll Learn</strong>`). Not for random emphasis.
- **Bullet lists use `<ul><li>`**, not hyphens or asterisks in plaintext.
- **After setting the description, ALWAYS verify by loading the product page in browser.** The API response is not reliable for checking rendered output.

**Link Slug:** Derive from the tutorial title. Lowercase, hyphens instead of spaces, max ~50 chars. Examples: `your-first-agent-cron-job`, `custom-tool-building`, `agent-powered-research`.

**Price:** Free = 0. Paid = cents ($0.99 = 99, $9.99 = 999).

### Step 3: Create the Product (POST)

```bash
curl -s -X POST "https://api.gumroad.com/v2/products" \
  --data-urlencode "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  --data-urlencode "native_type=digital" \
  --data-urlencode "name=<product name>" \
  --data-urlencode "price=<price in cents>" \
  --data-urlencode "price_currency_type=usd" \
  --data-urlencode "custom_summary=<short summary>" \
  --data-urlencode "description=<HTML formatted description>" \
  --data-urlencode "tags[]=<tag1>" \
  --data-urlencode "tags[]=<tag2>"
```

**CRITICAL:** Use `--data-urlencode` for ALL fields, not `-d`. The `&` character in any value will be silently truncated by plain `-d`.

**Tags:** Choose 6-10 relevant tags. Common ones: ai agents, automation, cron, scheduling, ai automation, beginner, agent pipeline, watchdog, productivity, prompt injection, ai security, llm security, agent security, cybersecurity, red teaming, defense, function calling, python, api, tool building, agent development, memory, rag, local ai, open source.

### Step 4: Set the Permalink (PUT after POST)

Gumroad's API silently ignores `permalink` on POST. Always follow up with a PUT:

```bash
curl -s -X PUT "https://api.gumroad.com/v2/products/<PRODUCT_ID>" \
  --data-urlencode "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  --data-urlencode "custom_permalink=<desired-slug>"
```

Save the product ID from the POST response (`id` field). Verify the PUT response shows `short_url` updated to your slug.

### Step 5: Verify the Draft

1. Check the API response confirms:
   - `"success": true`
   - Correct `name`, `price`, `custom_summary`
   - `short_url` shows your permalink slug
   - `"published": false` (must be a draft, not live)
   - No em dashes in any text field

2. **LOAD THE PRODUCT PAGE IN BROWSER** using `browser_navigate` to verify the description renders correctly with proper paragraph breaks, bold headers, and bullet lists. The API response is NOT sufficient to confirm formatting.

3. If the page shows a wall of text, the description needs to be re-sent as HTML via PUT.

### Step 6: Deliver to User

Tell the user:
- Product name
- Price (Free or $X.XX)
- Draft URL (from `short_url`)
- Status: "Draft, ready for you to upload the PDF, images, and final check before publishing."

## Pitfalls

1. **Em dashes in description/summary** — the user will reject the product. Strip all `\u2014` to `-` before the API call. Check every text field.

2. **`permalink` ignored on POST** — always set via PUT after creation. The POST response will have `custom_permalink: null` and an auto-generated `short_url`.

3. **`&` in any value corrupts plain `-d`** — always use `--data-urlencode`. The shell interprets `&` as a background operator.

4. **Description may be null on POST** — Gumroad API sometimes returns `"description":null` even when sent. Check the response and follow up with a PUT if needed.

5. **Price in cents** — $0.99 = 99, $9.99 = 999, Free = 0. Always use integer cents.

6. **Product starts as unpublished draft** — the user uploads PDF and images, then publishes manually. Do NOT publish via API.

7. **HTML is REQUIRED for descriptions.** Plaintext with double newlines will render as one wall of text on the product page. Always use `<p>`, `<ul><li>`, `<strong>` tags.

8. **Always verify by loading the product page in browser.** The API response showing correct `\n\n` does not mean the page renders correctly. Gumroad's product page does not convert newlines to paragraph breaks.

9. **The user's instructions are orders, not suggestions.** Follow them exactly on the first attempt. No iteration. No excuses. No explanations of what went wrong.
