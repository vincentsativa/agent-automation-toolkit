---
name: gumroad-publisher
description: Create and manage Gumroad digital products via the Gumroad API v2. Covers product creation, description/summary writing, pricing, slug setup, and content updates. Use when Vinny says to publish a tutorial, guide, or digital product on Gumroad.
trigger: "user asks to create a Gumroad product, publish a tutorial on Gumroad, upload to Gumroad, or set up a digital product for sale"
---

# Gumroad Publisher Skill

## Credentials

Stored in `~/.hermes/credentials.md`:
- **Account:** phantombyteai.gumroad.com
- **Access Token:** `[REDACTED_TOKEN]`
- **API Base:** `https://api.gumroad.com/v2/`

## Workflow

### 1. READ THE SOURCE MATERIAL

Read the markdown or text file containing the tutorial content. Extract:
- **Title** from frontmatter `title:` field or first heading
- **Subtitle** from frontmatter `subtitle:` field
- **Price** from frontmatter `gumroad_price:` field - convert dollar amount to cents (e.g. `$0.99` -> `99`)
- **Content** for writing description and summary

Source files live on Windows at paths like `/mnt/c/Users/<user>/OneDrive/Desktop/PI TUTORIAL/...`

### 2. CRAFT DESCRIPTION AND SUMMARY

**Custom Summary** (short, 1-2 sentences, appears under the product name):
- Hook: the problem the user is paying to solve
- What they get: the solution in plain terms
- Outcome: what changes for them after reading
- Max ~300 characters

**Description** (full product page body text - MUST be HTML):
- The Gumroad API `description` field accepts **HTML**, not plain text.
- Plain text with newlines renders as one wall of text on the product page.
- Use `<p>`, `<h2>`, `<ul>/<li>`, `<strong>` tags for proper formatting.
- Opening hook: the problem the user is paying to solve.
- "What You Will Learn" section with bullet list of specific skills.
- "What Is Inside" section with bullet list of deliverables.
- "Who This Is For" section describing target audience.
- "Price" section with value justification.
- Use hyphens (`-`) NOT em dashes (`---`) - Vinny rejects em dashes.

**Em dash rule:** BEFORE sending any text to the Gumroad API, replace ALL em dashes with hyphens:
```
text = text.replace('\\u2014', '-')
```
This applies to BOTH `custom_summary` AND `description` fields. Do not substitute en dashes; use plain hyphens.

### 3. CREATE THE PRODUCT (POST)

Use Python with urllib (not curl) for reliable HTML description handling:

```python
import urllib.request, urllib.parse, json

data = urllib.parse.urlencode({
    'access_token': token,
    'name': name,
    'price': price_cents,
    'custom_summary': summary,
    'description': html_description,
    'permalink': slug,
}).encode()

req = urllib.request.Request('https://api.gumroad.com/v2/products', data=data, method='POST')
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode())
```

Required fields: `name`, `price`, `custom_summary`, `description`, `permalink`
Optional: `customizable_price=false`, `max_purchase_count=1000`

### 4. UPDATE AN EXISTING PRODUCT (PUT)

```python
data = urllib.parse.urlencode({
    'access_token': token,
    'description': html_description,
}).encode()

req = urllib.request.Request(f'https://api.gumroad.com/v2/products/{product_id}', data=data, method='PUT')
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode())
```

### 5. VERIFY THE RENDERED OUTPUT (CRITICAL - DO NOT SKIP)

After creating or updating, you MUST verify the product page renders correctly by browsing to the `short_url` or `landing_url` from the API response:

1. Navigate to the product page URL in the browser.
2. Check that paragraphs are actual paragraphs (not one wall of text).
3. Check that bullet lists render as lists with proper bullets.
4. Check that headings render as headings.
5. Check that the custom summary appears below the product name.
6. Check that the price is correct.
7. Check that `published: false` (draft, not live).

If the description renders as a wall of text, the HTML was stripped or not sent correctly. Re-send with proper HTML tags.

### 6. MESSAGE VINNY ON TELEGRAM

After creating the draft AND verifying the page renders correctly, send Vinny a message on Telegram with:
- Product name
- Price
- Draft URL (from API response `short_url`)
- Status: "Draft - ready for you to upload the PDF, images, and final check before publishing."

## Pitfalls

1. **Description must be HTML, not plain text** - The Gumroad API `description` field accepts HTML. If you send plain text with newlines, it renders as one unbroken wall of text on the product page. Always use `<p>`, `<h2>`, `<ul>/<li>` tags.
2. **Em dashes in description/summary** - Vinny will reject the product and ask you to remove them. Always strip `\\u2014` -> `-` BEFORE the API call. Do this programmatically, not by hand.
3. **API returns product ID** - save it from the response (field `id`). You need it for PUT updates. If you don't save it, query the product list to find it.
4. **Price in cents** - Gumroad API expects cents. `$14.99` = `1499`. `$0.99` = `99`. Strip `$` and `.`, parse as integer.
5. **Product starts as unpublished draft** - Vinny uploads the PDF and images, then publishes manually. Do NOT publish via API.
6. **`max_purchase_count` field** - set to a reasonable cap like 1000 to prevent unlimited free/ultra-low price abuse when running a promotional price.
7. **`custom_permalink` vs `permalink`** - On POST, use `permalink` to set the slug. On PUT, use `custom_permalink` to change it. The API may auto-generate a random slug if `permalink` doesn't take effect on POST; fix it with a PUT using `custom_permalink`.
8. **Do not tell Vinny it's done until you have verified it yourself** - Browsing the product page and checking the rendered output is mandatory. API success response is not enough.

## Verification (MANDATORY - DO NOT SKIP)

- API returns `"success":true`
- Product has correct `name`, `price`, `short_url`, `permalink`
- `published: false` (must be draft, not live)
- No em dashes in any text field
- **BROWSE THE PRODUCT PAGE** and verify:
  - Paragraphs render as separate paragraphs, not one wall of text
  - Bullet lists render with proper bullets
  - Headings render as headings
  - Custom summary appears below the product name
  - Price is correct
- Only after all checks pass, tell Vinny it's done
