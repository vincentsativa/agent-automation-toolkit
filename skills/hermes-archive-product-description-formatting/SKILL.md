---
name: product-description-formatting
description: Write and format product descriptions for digital marketplaces (Gumroad, etc.) using proper HTML. Covers structure, section layout, bullet lists, and verification. Use when creating or updating a product listing that needs a professional, readable description.
trigger: "user asks to create or update a product description on Gumroad or similar marketplace, or the description rendered as a wall of text"
---

# Product Description Formatting

## Critical Rule: HTML, Not Plain Text

The Gumroad API `description` field accepts **HTML**. If you send plain text with newlines, the API accepts it silently but the product page renders it as an unbroken wall of text. You MUST use proper HTML tags.

## Required HTML Structure

```html
<p>Opening hook paragraph. State the problem and the solution.</p>

<p>Second paragraph with personal story or credibility signal.</p>

<p>Closing paragraph of the intro section.</p>

<h2>What You Will Learn</h2>

<ul>
<li>First learning outcome.</li>
<li>Second learning outcome.</li>
</ul>

<h2>What Is Inside</h2>

<p>Brief description of what the product contains.</p>

<ul>
<li>Item one.</li>
<li>Item two.</li>
</ul>

<h2>Who This Is For</h2>

<p>Target audience description.</p>

<h2>Price</h2>

<p>$XX.XX. Value justification sentence.</p>
```

## Section Guidelines

- **Opening paragraphs (3 max):** Hook, personal story/credibility, the fix. Keep tight.
- **What You Will Learn:** 7-9 bullet points. Each is a concrete skill or deliverable.
- **What Is Inside:** 1 intro paragraph + 7-9 bullet points covering the actual contents.
- **Who This Is For:** 1-2 sentences. Be specific about skill level and use case.
- **Price:** 1-2 sentences. Justify the price with a concrete value claim.

## Em Dashes

Strip ALL em dashes before sending. Use hyphens instead.

```python
description = description.replace('\u2014', '-')
```

## Verification

After updating via PUT, navigate to the product's public URL and check the rendered page. The browser snapshot should show proper `<paragraph>`, `<heading>`, and `<list>` elements -- not a single text block.

## Python Example

```python
import urllib.request, urllib.parse, json

description = """<p>Opening paragraph here.</p>

<h2>What You Will Learn</h2>

<ul>
<li>Item one.</li>
<li>Item two.</li>
</ul>"""

data = urllib.parse.urlencode({
    'access_token': token,
    'description': description,
}).encode()

req = urllib.request.Request(f'https://api.gumroad.com/v2/products/{product_id}', data=data, method='PUT')
resp = urllib.request.urlopen(req)
```

## Pitfalls

1. **Plain text looks fine in the API response but renders as a wall of text on the product page.** Always verify by loading the public URL in a browser.
2. **Em dashes in description** -- Vinny will reject the product. Strip them programmatically before the API call.
3. **Newlines alone are not enough.** The API stores them but the product page ignores them. You need `<p>` tags.
4. **Do not use `<br>` tags for paragraph breaks.** Use `<p>...</p>` blocks. `<br>` is for inline line breaks, not paragraph separation.
