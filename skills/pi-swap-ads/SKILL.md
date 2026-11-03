---
name: swap-ads
description: Swaps ad/CTA creatives across all article pages, index.html, and the process-article template on articles.phantom-byte.com. Use when changing ad copy, replacing affiliate offers with owned CTAs, or updating the site-wide promotional slot. Triggers on phrases like "change the ad copy", "swap the ads", "update the CTA", "replace ads", "new ad creative", "change the affiliate offer", or "update the site-wide promo".
---

# Swap Ads Skill

## Overview

Swaps the CTA/ad creative across:
- All article HTML pages (top + bottom slots in each)
- `index.html` (horizontal ad slot)
- `process-article` skill template (so future articles get the new creative)

Uses the `scripts/swap-ads-v2.py` script and regex-based replacement.

## WORKFLOW

### Step 1: Gather New Ad Creative

Get from the user:
- **Label** (small eyebrow text, e.g., "⚠️ Exit the Cloud")
- **Headline** (primary H4, e.g., "Own Your Weights. Own Your Data.")
- **Body** (description paragraph)
- **Button text** (CTA button copy)
- **Link URL** (where the ad points to)
- **Label color** (hex color for the eyebrow text, default: `#FF6B35`)
- **Is it an owned/free resource?** → If yes, REMOVE all ad disclaimers. If it's an affiliate offer, keep `rel="nofollow sponsored"` and "Partner Offer" label.

### Step 2: Update the Swap Script

Edit `~/workspace/articles/scripts/swap-ads-v2.py`:

Update the three `NEW_AD_*` constants at the top of the script:
- `NEW_AD_TOP` — for article top slot (`ad-slot-article-top`)
- `NEW_AD_BOTTOM` — for article bottom slot (`ad-slot-article-bottom`)
- `NEW_AD_INDEX` — for homepage horizontal slot (`ad-slot-horizontal`)

Each uses this template (update the `{PLACEHOLDERS}`):

```html
<div class="ad-slot {AD_CLASS}">
    <a href="{LINK_URL}" target="_blank">
        <div class="ad-creative" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.25); border: none; {EXTRA_STYLES}">
            <p style="font-size: 0.7rem; color: {LABEL_COLOR}; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">{LABEL}</p>
            <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{HEADLINE}</h4>
            <p style="margin: 0 0 16px 0; font-size: 0.95rem; line-height: 1.5; color: #e0e0e0; font-weight: 400;">{BODY}</p>
            <div style="text-align: center;">
                <span style="display: inline-block; padding: 11px 22px; background: linear-gradient(90deg, #00FF88 0%, #00cc6a 100%); color: #0a0a1a; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 10px rgba(0, 255, 136, 0.35);">{BUTTON_TEXT}</span>
            </div>
        </div>
    </a>
</div>
```

**For owned/free resources (no disclaimers):**
- Remove the wrapper `<div>` with `ad-performcb`, `data-campaign-id`, `data-subid`
- Remove `rel="nofollow sponsored"` from the `<a>` tag
- Label should be something direct (not "Partner Offer" or "Sponsored")

**For affiliate offers (keep tracking):**
- Keep `rel="nofollow sponsored"` on the `<a>` tag
- Label should include disclosure like "Partner Offer" or "Sponsored"

### Step 3: Test Locally on One File (MANDATORY)

```bash
cd ~/workspace/articles

# Test on the reference template first
python scripts/swap-ads-v2.py --file why-your-ai-agent-went-paralyzed.html
```

Verify the output:
- Ad copy matches what user specified
- No old ad remnants (PerformCB, old labels, old links)
- HTML is well-formed

**Show the user the test result and wait for explicit approval before proceeding.**

### Step 4: Run on All Files (After Approval)

```bash
cd ~/workspace/articles

python scripts/swap-ads-v2.py
```

Expected: 70+ article files updated + index.html.

### Step 5: Update Process-Article Skill Template

Edit `~/.pi/agent/skills/process-article/SKILL.md`:

Replace the two ad slot sections:
1. Find `<!-- Ad Slot (Top) -->` block → replace with the new `<!-- CTA Slot (Top) -->` block
2. Find `<!-- Ad Slot (Bottom) -->...` → replace with the new `<!-- CTA Slot (Bottom) -->` block

Also verify `scripts/ad-manager.js` is NOT referenced at the bottom. If it is, remove it.

### Step 6: Run SEO Maintenance

```bash
cd ~/workspace/articles

python seo-maintenance.py --all
```

This regenerates:
- `sitemap.xml` (72+ URLs)
- `rss.xml` (50 articles)
- `llms.txt` (for AI crawlers)

### Step 7: Git Commit

```bash
cd ~/workspace

git add articles/*.html articles/index.html articles/sitemap.xml articles/rss.xml articles/llms.txt articles/scripts/swap-ads-v2.py
git commit -m "feat: swap ads to <new-ad-description> + SEO maintenance"
```

### Step 8: Build & Deploy to Cloud Run

```bash
cd ~/workspace/articles

gcloud builds submit --config cloudbuild.yaml --timeout=300s
```

Wait for build + deploy to complete (typically 1-3 minutes).

### Step 9: Verify Live

```bash
sleep 15

# Check homepage loads
curl -sI "https://articles.phantom-byte.com/" | head -1

# Check article loads
curl -sI "https://articles.phantom-byte.com/why-your-ai-agent-went-paralyzed.html" | head -1

# Check HSTS headers
curl -sI "https://articles.phantom-byte.com/" | grep -i "strict-transport"

# Check new ad present (adjust grep terms for your ad copy)
curl -s "https://articles.phantom-byte.com/" | grep -c "YOUR_HEADLINE_KEYWORD"

# Verify old ads gone
curl -s "https://articles.phantom-byte.com/why-your-ai-agent-went-paralyzed.html" | grep -c "Partner Offer"  # should be 0

# Verify sitemap/RSS
curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c '<loc>'  # 72+
curl -s https://articles.phantom-byte.com/rss.xml | grep -c '<item>'     # 50
```

Expected:
- `200 OK` for homepage and articles
- `strict-transport-security` header present
- New ad text present, old ad text absent
- 72+ sitemap URLs, 50 RSS articles

### Step 10: Submit to Google

```bash
cd ~/workspace/articles

python seo-maintenance.py --submit-url="https://articles.phantom-byte.com/sitemap.xml"
```

### Step 11: Report Success

```
✅ ADS SWAPPED & DEPLOYED

**New creative:** <label> → <headline>
**Link:** <url>
**Updated:** 78 articles + index.html + process-article template
**SEO:** sitemap (72 URLs), RSS (50), llms.txt regenerated
**Google:** Submitted via Indexing API

**Backup:** articles/backup-sovereign-ad-swap-YYYY-MM-DD/
```

## FILE PATHS

| Path | Purpose |
|------|---------|
| `~/workspace/articles/scripts/swap-ads-v2.py` | The ad swap script (edit NEW_AD_* constants) |
| `~/workspace/articles/` | All article HTML files |
| `~/workspace/articles/index.html` | Homepage with horizontal ad slot |
| `~/.pi/agent/skills/process-article/SKILL.md` | Template for new article generation |
| `~/workspace/articles/why-your-ai-agent-went-paralyzed.html` | Reference article to test on |
| `~/workspace/articles/seo-maintenance.py` | SEO auto-generator (run on every deploy) |
| `~/workspace/articles/cloudbuild.yaml` | Cloud Build config for deployment |

## AD SLOT LOCATIONS IN HTML

All article pages have two ad slots:
1. **Top** — after `</figure>` (featured image), before `<!-- Article Body -->`
2. **Bottom** — after `</div>` (article-footer), before `</article>`

Homepage has one ad slot:
1. **Horizontal** — inside `<section class="ad-slot ad-slot-horizontal">`, before footer

## SAFETY CHECKS

Before deploying:
- ✅ Tested on one file locally first
- ✅ User explicitly approved the test result
- ✅ `seo-maintenance.py --all` ran successfully
- ✅ sitemap.xml has 72+ URLs
- ✅ rss.xml has 50 articles
- ✅ Old ad terms (Partner Offer, noklnk, PerformCB) absent from test file
- ✅ New ad terms present in test file
- ✅ Git committed before deploy
