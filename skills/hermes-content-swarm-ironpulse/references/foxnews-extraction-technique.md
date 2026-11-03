# Fox News AI — Story Extraction Technique

## Why This Exists

Fox News renders its AI category page with a mix of visible `<article>` elements and image-linked cards. Some article links point to `foxbusiness.com`, which reliably returns 404/error pages. This reference documents what works and what doesn't.

## Working Extraction

### Step 1: Navigate and Browse

```javascript
browser_navigate('https://www.foxnews.com/category/tech/artificial-intelligence')
```

The page shows:
- A hero/top story with a large image (featured article)
- A grid of secondary stories with images
- Smaller card-style stories further down

### Step 2: Extract with Article Selector

Unlike The Verge, Fox News actually uses `<article>` tags:

```javascript
document.querySelectorAll('article');
```

Each `<article>` contains:
- An `<h2>` or `<h4>` heading with the headline as a child `<a>` link
- An image (may or may not be directly related to the story)
- Tags/labels like "BINARY BATTLEGROUND", "FUTURE DELIVERED", etc.

### Step 3: Get Links

```javascript
const articles = document.querySelectorAll('article');
Array.from(articles).map(a => {
  const h = a.querySelector('h2, h3, h4');
  const links = a.querySelectorAll('a[href]');
  const url = links.length > 0 ? links[0].getAttribute('href') : '';
  return { headline: h?.textContent?.trim(), url: url?.substring(0,80) };
});
```

## Known Pitfalls

- **Fox Business links return 404** — Any story link pointing to `foxbusiness.com` will result in a 404 when navigated to. Only `foxnews.com`-hosted articles are reliably accessible.
- **Article URL navigation returns 404 (May 2026):** Even `foxnews.com`-hosted article URLs can return 404 when navigated to directly from the category listing. Extract full story content from the category page snapshot rather than opening individual article URLs. If you must get article detail, try the snapshot approach first.
- **Article text is not accessible** — Even when you can navigate to a Fox News article, the page text may be blocked behind a paywall or bot detection.
- **No timestamps visible** — Fox News AI category page does not display relative timestamps for most stories. Verify recency via Google News cross-reference instead.
- **No datetime attributes** — The `<time>` elements on Fox News may be absent or lack `datetime` attributes.
- **Stories may be older** — Fox News AI section aggregates stories from days/weeks prior. Verify timestamps before including.
