# WordPress Post-ID Bypass for Adblocker-Blocked Sites

## Problem
News sites (TechCrunch, etc.) often block automated browsers with adblocker-detection overlays, CAPTCHAs, or Turnstile challenges. Additionally, search result pages may truncate article slugs with `...`, making the actual URL unresolvable.

## Solution: WordPress Post-ID Direct Access

WordPress sites expose every post via a numeric ID at `?p=<id>`. This bypasses:
- Pretty URL routing (which may fail on truncated slugs)
- Adblocker-detection overlays (the overlay JS often only triggers on the pretty-URL page)
- Sitemap/redirect logic

### Step 1: Find the Post ID

Search the site and extract the post ID from the search results HTML:

```bash
curl -sL "https://site.com/?s=search+terms" | grep -oP 'post-[0-9]+' | head -5
```

Or look for the full post class attribute:

```bash
curl -sL "https://site.com/?s=search+terms" | grep -oP 'class="[^"]*post-[0-9]+[^"]*"' | head -5
```

The post ID is the number after `post-` in the CSS class (e.g., `post-3140971`).

### Step 2: Access via Post ID

```bash
curl -sL "https://site.com/?p=3140971"
```

This returns the raw article HTML without the adblocker overlay in most cases.

### Step 3: Extract Content

For article text, grep for paragraph tags:

```bash
curl -sL "https://site.com/?p=3140971" | grep -oP '<p[^>]*>.*?</p>'
```

For the article title, grep the `<title>` tag:

```bash
curl -sL "https://site.com/?p=3140971" | grep -oP '<title>.*?</title>'
```

### Step 4: Verify

Check the response title to confirm you got the right article:

```bash
curl -sL "https://site.com/?p=3140971" | grep -i "<title>" | head -3
```

## Why This Works

- WordPress's `?p=<id>` query parameter is a core routing primitive that bypasses the rewrite engine
- Adblocker-detection scripts are typically injected by themes/plugins that hook into the template rendering pipeline for pretty URLs
- The post-ID route renders the same content through a different code path that may skip the detection hook
- No browser/JS execution needed, plain curl suffices

## Limitations

- Only works on WordPress sites (identifiable by `/wp-content/`, `wp-json`, or `WordPress` in HTML comments/headers)
- Some sites redirect `?p=<id>` to the pretty URL, if that happens, the redirect target may still trigger the overlay
- Post IDs are sequential and guessable, but you still need to find the right one via search
- Some sites block all curl user agents, add `-H "User-Agent: Mozilla/5.0 ..."` if needed
