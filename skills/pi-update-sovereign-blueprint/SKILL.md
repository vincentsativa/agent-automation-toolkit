---
name: update-sovereign-blueprint
description: Replaces the Sovereign AI Stack Blueprint PDF (lead magnet for email signups) on vincentsativa.com. Use when the user says "update the blueprint", "replace the PDF", "new version of the blueprint", "swap the tutorial PDF", "update the sovereign blueprint", "new pricing PDF", or similar phrasing about updating this specific tutorial/lead magnet.
---

# Update Sovereign AI Stack Blueprint, vincentsativa.com

## Overview

Replaces the `The-Sovereign-AI-Stack-Blueprint.pdf` file served at `https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf`. This is the lead magnet offered for email signups, pricing, hardware recommendations, and stack components change over time, so this PDF gets updated periodically.

**Domain:** vincentsativa.com (GitHub Pages)
**Repo:** `~\workspace\funnel-pages\` (remote: `vincentsativa/phantom-byte-funnels`)
**PDF path in repo:** `assets/The-Sovereign-AI-Stack-Blueprint.pdf`
**Live URL:** `https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf`

## Workflow

### Step 1: Get the New PDF

Ask the user for the path to the new PDF. It's typically on their Desktop or OneDrive.

### Step 2: Replace the File

```bash
cp "/path/to/new/sovereign_blueprint.pdf" \
    "~/workspace/funnel-pages/assets/The-Sovereign-AI-Stack-Blueprint.pdf"
```

### Step 3: Verify the Copy

```bash
ls -la ~/workspace/funnel-pages/assets/The-Sovereign-AI-Stack-Blueprint.pdf
```

Confirm the file size matches the source.

### Step 4: Commit & Push

```bash
cd ~/workspace/funnel-pages
git add assets/The-Sovereign-AI-Stack-Blueprint.pdf
git commit -m "feat: update Sovereign AI Stack Blueprint PDF"
git push
```

### Step 5: Wait for CDN Cache to Clear

GitHub Pages uses Fastly CDN with `Cache-Control: max-age=600` (10 minutes). The old version will be served from cache for up to 10 minutes after the push.

Wait ~10 minutes, then verify.

### Step 6: Verify Live

```bash
curl -sI "https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf" | head -20
```

**Expected:**
- `HTTP/1.1 200 OK`
- `Content-Length` matches the new file size
- `Last-Modified` shows the current date/time
- `ETag` has changed from the old value

Also verify the PDF header is valid:

```bash
curl -s "https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf" | head -c 20 | xxd
```

Expected: starts with `%PDF-1.x` or similar valid PDF header.

### Step 7: Report Success

```
✅ SOVEREIGN AI STACK BLUEPRINT UPDATED

**File:** assets/The-Sovereign-AI-Stack-Blueprint.pdf
**Size:** {new_size} bytes (was {old_size} bytes)
**Live at:** https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf
**Deploy:** GitHub Pages via vincentsativa/phantom-byte-funnels
```

## Notes

- **CDN cache:** The old PDF may be served for up to 10 minutes after push. Wait and retry if the old size/ETag is still showing.
- **No other files need updating**, this PDF is linked from the email capture flow and various guide pages. The filename stays the same, so all existing links continue to work.
- **No SEO or sitemap changes needed**, this is a static asset, not an HTML page.
- **The PDF is the lead magnet** for email signups on vincentsativa.com. Keep the filename exactly as-is so the email automation doesn't break.
