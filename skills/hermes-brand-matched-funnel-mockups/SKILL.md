---
name: brand-matched-funnel-mockups
description: >
  Create multiple funnel/landing page HTML mockups that match an existing brand's
  design system. Extracts CSS variables from a live site, reads content from a
  source document (PDF/doc), and produces responsive HTML pages with Playwright
  screenshots for review.
version: 1.0.0
author: Hermes Agent
tags: [funnel, landing-page, mockup, design-system, html, css, brand]
triggers:
  - funnel page ideas
  - landing page mockups
  - create funnel pages that match
  - design mockups for
  - brand-matched landing pages
  - squeeze page
  - lead magnet page
  - application page
---

# Brand-Matched Funnel Mockups

Create multiple funnel/landing page mockups that visually match an existing website's
design system. The workflow covers: design token extraction, content ingestion,
page variant generation, and screenshot capture.

## Step 1: Extract Brand Design System

Visit the target website(s) and pull out the CSS:

```bash
curl -s https://example.com | head -300
```

Focus on extracting:
- **CSS custom properties** (`:root { --... }`), colors, spacing
- **Color palette**, primary, accent, backgrounds, text, borders
- **Typography**, font families, sizes, weights, line-heights
- **Component styles**, buttons, cards, forms, nav
- **Border radius**, rounded corners pattern (px values)
- **Shadow system**, if any

If the site uses external CSS files, curl those too. The `<style>` block in the
HTML head is usually sufficient.

**Key insight:** Match the EXACT CSS variables. Don't approximate. If the site
uses `--purple: #9D4EDD` and `--green: #00FF88`, use those exact values.

## Step 2: Ingest Content Source

Read the PDF or document that contains the content for the funnel pages:

```python
import fitz  # pymupdf
doc = fitz.open('path/to/document.pdf')
for i, page in enumerate(doc):
    text = page.get_text()
    # Process page text
```

Install pymupdf if needed: `pip3 install pymupdf`

Extract:
- Product/playbook name and tagline
- Key benefits and features
- Stats/numbers for social proof
- Pain points and failure stories
- Author info/credibility markers
- Call-to-action language

## Step 3: Generate Funnel Page Variants

Create 3-4 distinct funnel page types. Each serves a different stage of the funnel:

### Variant 1: Lead Magnet / Download Page
- **Purpose:** Top of funnel, capture email for free content
- **Layout:** Hero headline → ghost/visual → opt-in card (name + email) → social proof bar → content preview list → bottom CTA
- **CTA color:** Primary brand color (purple for PhantomByte)
- **Key elements:** Badge showing what they get (e.g., "2026 Edition • 25 Pages"), numbered feature list, privacy note

### Variant 2: Squeeze Page (Pain → Solution)
- **Purpose:** Highest-conversion page, minimal friction
- **Layout:** Two-column split, LEFT: pain points with red-accented cards + real failure stories → RIGHT: visual teaser + compact form
- **CTA color:** Contrasting accent (green for PhantomByte)
- **Key elements:** Real failure stories from the content, visual flowchart/cheat sheet preview, ultra-short form (just name + email)

### Variant 3: Email Course / Challenge Signup
- **Purpose:** Nurture funnel, daily value delivery builds trust
- **Layout:** Challenge hero (amber/warm gradient) → day-by-day card grid → urgency bar → benefits + form split
- **CTA color:** Warm accent (amber/gold) to differentiate from other pages
- **Key elements:** Numbered day cards showing deliverables, cohort urgency, bonus content on final day

### Variant 4: Application / Audit Page
- **Purpose:** Bottom of funnel, qualify and book calls
- **Layout:** Minimal hero → trust signals (3 cards) → multi-field application form → process steps
- **CTA color:** Primary brand color
- **Key elements:** Dropdown selects for qualification, textarea for pain description, numbered process timeline

## Step 4: Build HTML Files

For each variant, create a standalone HTML file with:
- All CSS inline (no external dependencies)
- CSS custom properties matching the extracted brand vars
- Fully responsive (mobile-breakpoint at 768px)
- Form inputs styled to match brand (focus states, border-radius)
- Hover/transition states on buttons and cards

**File naming:** `01-variant-name.html`, `02-variant-name.html`, etc.
**Output directory:** `~/phantombyte-funnel-mockups/` or project-appropriate path

## Step 5: Capture Screenshots

Use Playwright to screenshot each mockup for review:

```python
import asyncio
from playwright.async_api import async_playwright

async def screenshot_page(url, output_path, width=1280, height=900):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
```

Use `file:///home/<user>/path/to/mockup.html` as the URL.

## Step 6: Present to User

- Share the screenshot images inline
- Explain each variant's funnel role and CTA strategy
- Recommend the funnel flow order (traffic → squeeze → nurture → convert)
- Offer to iterate or wire up real forms

## Funnel Flow Recommendation Pattern

1. **Traffic → Squeeze page (#2)**, highest conversion, minimal form
2. **Thank you page → Upsell to challenge (#3)**, warm leads with daily value
3. **Final email → Pitch audit/application (#4)**, ready to talk
4. **Lead magnet page (#1)**, standalone SEO landing page for organic search

## Pitfalls

- **Don't mix color roles.** Each page variant should have ONE dominant CTA color.
  Squeeze = green (action), Lead magnet = purple (brand), Challenge = amber (urgency),
  Application = purple (trust).
- **Don't overdesign forms.** 2-3 fields for top-of-funnel, 5-7 for bottom-of-funnel.
  Never more than 7.
- **Ghost emoji / brand icon placement.** If the brand has a favicon or emoji
  (PhantomByte uses 👻), use it as a visual anchor in the hero, but only once.
- **PDF text extraction can be messy.** Pymupdf sometimes injects CSS class
  artifacts (e.g., `class="str"`). Clean these before using extracted quotes.
- **Vision tools may not work** with some models. If `vision_analyze` or
  `browser_vision` fails, fall back to Playwright screenshots and share the
  image paths directly with MEDIA: prefix.