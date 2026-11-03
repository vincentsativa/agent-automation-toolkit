---
name: clone-website
description: Generates a new guide/product landing page from the saved template OR clones a live page and redesigns it with new content, then deploys to vincentsativa.com. Use when the user says "clone the template for [guide name]", "make a page for [product]", "clone this website", or "redesign this page".
---

# Clone Website Skill

## Quick Start (30 seconds)

**User provides:** guide name, content file (Markdown or labeled sections), image file, Gumroad slug (optional)

**You do:**

1. Read `template.html` (already saved locally) OR fetch live URL if user wants to clone a specific page
2. Read the content file and image
3. Run the build script
4. Git commit + push to `~\workspace\funnel-pages\`
5. Verify 200 OK at `https://vincentsativa.com/{slug}.html`

## Workflow: Local mockup first, then deploy (always)

Every redesign job follows this order, the way a human would do it:

1. **Local mockup first.** Build the redesigned page locally (write the HTML file
   to the target repo's working tree, or to a scratch path). Open it in the
   browser to verify the look, layout, responsiveness, links, and that there are
   no em dashes. Show the user what you built.
2. **Get the go-ahead.** Do NOT push or deploy until the user confirms they like
   it and tells you the target. The mockup is for review; nothing goes live yet.
3. **Then deploy.** Only after approval, deploy to the target the user names
   (see Deployment Targets below). Verify it serves correctly.

Never skip to deploy. The local mockup is the deliverable of the first step.

Redesigned pages go to ONE of two destinations. **The user will tell you which** when we start each job. Do not assume.

| Target | Host | How to deploy |
|--------|------|--------------|
| `vincentsativa.com` (and subpaths) | GitHub Pages from `main` branch of `vincentsativa/phantom-byte-funnels` repo | `git add/commit/push` in the local repo below, wait ~15s, curl-verify 200 |
| `phantom-byte.com` domain | Cloud Run (separate deployment, NOT this repo) | Ask the user for the Cloud Run project / deploy method before touching anything; do not assume a local repo exists for it |

If the user does NOT specify a target, ask before deploying. vincentsativa.com = git push to the funnel-pages repo. phantom-byte.com = Cloud Run, get instructions first.

## Files

| Path | Purpose |
|------|---------|
| `~\.pi\agent\skills\clone-website\template.html` | Single-product guide funnel template (labeled `[SECTION]` format, used by build-guide.py) |
| `~\.pi\agent\skills\clone-website\hub-template.html` | Multi-offer hub/landing template (full design system with `[PLACEHOLDER]` slots). Saved 2026-06-20 from the vincentsativa.com redesign. Use for sites that promote a set of offers + a highlighted publication. |
| `~\.pi\agent\skills\clone-website\build-guide.py` | Automation script (guide funnel pages only) |
| `~\workspace\funnel-pages\` | Local clone of the repo serving `vincentsativa.com` (GitHub Pages). NOT used for phantom-byte.com. |

## Workflow

### Method A: Build from Template (Standard)
Use when user says "clone the template" or "make a page".

The content file must use `[SECTION_LABEL]` markers (see build-guide.py for all labels).

```
[TITLE]
The Guide Name | Tagline

[META_DESC]
Description for SEO.

[BADGE]
Complete Guide

[H1_BEFORE]
The

[H1_SPAN]
Guide Name

[H1_AFTER]
Guide

[SUBTITLE]
Subtitle text here. No em dashes.

[CTA_HEADLINE]
Get Your Copy Today

[CTA_BODY]
Everything you need to get started.

[PRICE]
0.99

[ORIGINAL_PRICE]
5

[BENEFIT_1_ICON]
🤖
... (see build-guide.py for all section labels)
```

```bash
python ~\.pi\agent\skills\clone-website\build-guide.py ^
    --name "Guide Name Here" ^
    --slug guide-url-name ^
    --content "C:\full\path\to\content.txt" ^
    --image "C:\full\path\to\cover.png" ^
    --gumroad Product-Slug
```

### Method B: Clone a Live Page (New — Learned from Pi Coding Agent)
Use when user says "clone this website" pointing to a specific page URL.

**Step 1: Fetch the live page as template**
```bash
# This becomes your base — use browser_navigate to get the HTML
```

**Step 2: Read the content from Markdown**
Markdown files (`.md`) have a different structure. Extract:
- YAML frontmatter (`title`, `subtitle`, `gumroad_price`, `primary_keyword`)
- Main body text for benefits, sections, chapters
- Tables, section headers, and other structured content

**Step 3: Build HTML manually**
Since Markdown content doesn't have `[SECTION_LABEL]` markers, you need to:
1. Create the full HTML file using `write` tool
2. Swap ALL of these from the template:
   - `<title>` tag
   - `<meta name="description">`
   - `.badge` text
   - `<h1>` text (including `<span>` gradient text)
   - `.hero-subtitle` text
   - Cover image `src` → `assets/{image-name}`
   - CTA section: h2, paragraph, price
   - Buy button `href` → Gumroad link
   - 4x benefit items (icon, title, desc)
   - 8x "What's Inside" chapters (title + desc)
   - 4x "For Whom" persona cards (icon + title + desc)
   - `.subtitle` text above personas

**Step 4: Add Google Analytics**
Insert this snippet right before `<!-- Robots -->` in `<head>`:
```html
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-PDQCZE09E4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-PDQCZE09E4');
    </script>
```

**Step 5: Fix image path**
Ensure `<img src="...">` points to `assets/{filename}` not just `{filename}`.

**Step 6: Remove em dashes**
Replace `—` (U+2014) with ` - ` or just a space.

### Step 4 (Both Methods): Deploy

```bash
cd ~\workspace\funnel-pages
git add {slug}.html assets/{image-name}.png
git commit -m "feat: add {Guide Name} page"
git push
```

### Step 5: Verify

```bash
# Wait ~10-15 seconds for GitHub Pages deploy
sleep 15
curl -sI "https://vincentsativa.com/{slug}.html"
```

Expected: `200 OK`

## Rules

- **NO em dashes (`—`)** — use `-` or spaces. This applies to ALL text: titles, subtitles, badge, benefits, chapters, personas, CTA copy. Scan the finished HTML for `—` before deploying. Zero exceptions.
- **ALWAYS ask for the price if you don't know it.** Never assume a price. If the user doesn't state it, ASK: "Is this free or paid? What price?" Do NOT default to $9.99 or any other number. If it's free, set the price tag to `Free`, button to `Download Free - Instant Access`, and guarantee to `📥 Free download. No payment required. Instant digital delivery.`
- **The badge text must be derived from the tutorial content.** Read the tutorial text and write a badge that captures what it is in Title-Case format (e.g. a cron tutorial → `Beginner-Friendly Agent Automation`, a multi-agent guide → `Production-Grade Agent Architecture`). Do NOT reuse the cloned page's badge verbatim if it doesn't fit the new content.
- **ALWAYS add Google Analytics**, use ID `G-PDQCZE09E4`
- **Image names** — clean to hyphens, no spaces
- **Gumroad links** — `https://phantombyteai.gumroad.com/l/{slug}`
- **Repo for vincentsativa.com is ALWAYS** `~\workspace\funnel-pages\` — do NOT clone fresh. **phantom-byte.com is a separate Cloud Run target** (see Deployment Targets above); never assume it uses this repo.
- **Verify after deploy** — wait 15s then curl for 200

## Lessons Learned (May 2026)

1. **Use the local workspace repo**, don't clone fresh. The repo at `~\workspace\funnel-pages\` already has the right remote and CNAME config.
2. **Image path must be `assets/{file}`** — the HTML is in the root, images are in `assets/`.
3. **GA snippet goes before `<!-- Robots -->`**, not at the end of `<head>`.
4. **Markdown files** need manual content extraction — the build script only supports labeled `[SECTION_LABEL]` format.
5. **Em dashes** in Markdown files are common and must be stripped. The build script handles this automatically; manual builds must handle it.
6. **GitHub Pages takes ~10-15 seconds** to deploy after push. Always wait before verifying.
7. **When writing full HTML manually**, keep the EXACT CSS from the template — only change content, never styles.
8. **GitHub Pages deploys can fail transiently.** If `curl` returns `404` after a push but the file is confirmed on GitHub (check `raw.githubusercontent.com`), do NOT panic and do NOT go down a rabbit hole debugging the repo settings. Just push an empty commit to retrigger the build: `git commit --allow-empty -m "chore: trigger GitHub Pages rebuild" && git push`. Wait 30s and curl again. This fixes it every time.
9. **Ask for the price.** If the user does not explicitly state the price (free or paid amount), ASK before building the CTA section. Defaulting to a paid price on a free tutorial is a critical error.
10. **Badge text comes from the tutorial content**, not the cloned page. Write a fresh Title-Case badge that describes what THIS tutorial teaches (e.g. `Beginner-Friendly Agent Automation` for a cron tutorial). Reusing the source page's badge when the topic changed is wrong.
11. **Hero padding and badge spacing must match the reference page.** When cloning a page, always check the hero section spacing against `https://vincentsativa.com/your-first-agent-cron-job.html` (the canonical reference). That page uses `.hero { padding: 40px 20px 60px; }` and `.badge { margin-bottom: 10px; }`. If the user says the gap between the nav header and the badge is too large, match those values exactly. Do NOT fiddle with the badge's own margin/padding repeatedly — that's almost never what they mean.
