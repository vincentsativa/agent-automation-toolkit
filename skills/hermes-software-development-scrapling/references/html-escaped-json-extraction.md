# Extracting HTML-Escaped JSON from Raw Page Source

## Problem
Some sites embed structured data (product listings, config objects, etc.) directly in the raw HTML response as inline JSON, but with HTML-escaped quotes (`&quot;` or `\u0026quot;`) instead of standard double quotes. The browser tool may return an empty page for these sites because they rely on JS-rendered anti-bot layers, yet a simple `curl` fetch of the raw HTML contains all the data.

## Pattern
1. Fetch raw HTML with `curl -sL --max-time 15 "URL" -o /tmp/page.html`
2. Load the file in Python and locate the JSON block (often near keywords like `products`, `window.__INITIAL_STATE__`, etc.)
3. Run `html.unescape()` on the block to replace `&quot;` with `"`
4. Parse with `json.loads()` or regex extract fields

## Example: Gumroad Product Listings
Gumroad embeds the full products array in the raw HTML with `\u0026quot;` delimiters. The browser tool returns an empty snapshot, but curl succeeds:

```python
import re, html as h

with open('/tmp/gumroad.html') as f:
    data = f.read()

idx = data.find('SellerProfileProductsSection')
snippet = data[idx:idx+25000]

# Extract names and prices from escaped JSON
names = re.findall(r'"name":"([^"]+)"', snippet)
prices = re.findall(r'"price_cents":(\d+)', snippet)
perms = re.findall(r'"permalink":"([^"]+)"', snippet)

for name, price, perm in zip(names, prices, perms):
    print(f"{name}, ${int(price)/100:.2f}")
```

## Why This Matters
Do not assume the browser tool is the only way to get data from a site. If the browser returns empty but curl returns HTML, search the raw source for embedded JSON blobs before escalating to Rotunda or other heavy fallbacks.
