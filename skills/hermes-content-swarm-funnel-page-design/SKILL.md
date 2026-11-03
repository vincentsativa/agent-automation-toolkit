---
name: funnel-page-design
description: Create production-ready funnel page mockups from source material (PDFs, playbooks, guides, product specs). Extracts brand design system from existing sites, maps content to funnel strategy, and builds responsive HTML mockups with screenshots. Also covers ESP/MailerLite integration, automated email setup, proxy architecture, and post-deployment automation wiring.
---

# Funnel Page Design from Source Material

## Overview
Takes a content asset (PDF, guide, playbook, course, etc.) and existing brand websites, then creates multiple funnel page mockups that match the brand's design system exactly. Outputs responsive HTML files + screenshots.

## Process

### 1. Ingest Source Material
- Extract text from PDFs using PyMuPDF (`fitz.open()`)
- Read full content to identify hooks, pain points, stories, and deliverables
- For web content, use browser tools to capture structure and copy

### 2. Extract Brand Design System
- Navigate to the brand's existing websites
- Pull the HTML source (`curl -s URL`) to extract CSS custom properties
- Key elements to capture:
  - CSS variables (colors, especially `--purple`, `--green`, `--dark`, etc.)
  - Font stack (usually system fonts in `font-family`)
  - Border radius patterns
  - Card styles, button gradients
  - Logo treatment (text-based logo with accent color on second word)
  - Navigation pattern
  - Footer style
- NEVER guess colors — always extract from actual CSS

### 3. Map Content to Funnel Strategy
Identify which funnel types fit the content:

| Funnel Type | Best For | Form Style |
|---|---|---|
| **Lead Magnet / Squeeze** | Free PDF, checklist, flowchart | Name + Email, minimal |
| **Split Squeeze (Pain + Solution)** | High-friction topics, real failure stories | Two-column: pain left, form right |
| **Email Challenge/Code Along** | Educational content, course material | Name + Email, day-by-day preview |
| **Application/Audit** | Services, consulting, qualified leads | Multi-field form, dropdowns, textarea |

### 4. Build Mockups
- Write self-contained HTML files (inline CSS, no dependencies)
- Use the exact brand design system extracted in step 2
- Responsive (mobile-first with `@media` breakpoints)
- Include:
  - Branded nav bar with logo treatment
  - Hero with gradient text matching brand
  - Social proof (stats from the content — page counts, months, etc.)
  - Content preview (failure signatures, chapter list, day previews)
  - Opt-in form with proper CTA button (gradient matching brand)
  - Privacy reassurance line
  - Branded footer

### 5. Generate Screenshots
- Use Playwright (`playwright.async_api`) for full-page screenshots
- 1280x900 viewport for desktop preview
- Save as PNG alongside the HTML files
- Share via `MEDIA:/path/to/file.png`

### 6. SEO Keyword Research (Parallel Deliverable)
For each funnel page mockup, produce a keyword research sheet covering:

| Element | Details |
|---|---|
| **Primary keyword** | Highest commercial intent, realistic to rank for |
| **5-8 secondary keywords** | Supporting cluster with intent + difficulty |
| **3-5 long-tail variations** | Question-based or specific, lower difficulty |
| **Search intent** | Informational / Navigational / Commercial / Transactional |
| **Difficulty estimate** | Low / Medium / High |
| **Title tag** | Under 60 chars, includes primary keyword |
| **Meta description** | Under 155 chars, includes CTA + keyword |

Also include:
- **Keyword map by funnel stage**: TOFU (awareness) → MOFU (consideration) → BOFU (decision), showing which pages target which stage
- **Content gap opportunities**: Underserved keywords competitors aren't owning yet, with suggestions for supporting blog content
- **Topic → keyword alignment table**: Map source material topics/features to specific SEO keywords

**Funnel stage mapping:**
- Lead Magnet → TOFU (informational)
- Squeeze/Diagnostic → TOFU→MOFU (commercial)
- Challenge/Course → MOFU (commercial)
- Audit/Application → BOFU (transactional)

Save as `seo-keyword-research.md` in the same output directory as the mockups.

## 7. Funnel Operational Setup (Post-Design)

After funnel HTML pages are designed, they must be wired to an email service provider (ESP) like MailerLite **before** deployment. This is a separate class of work that follows the design phase.

### 7a. ESP Audit Sequence (Diagnostic)

When checking up on an existing ESP setup, always run this full audit:

1. **Test API key** — old keys may have been rotated for security. If the key returns empty results (not 401), it may be invalid.
2. **List groups** — verify all expected funnel groups exist (playbook, flowchart, challenge, audit, newsletter).
3. **List automations** — check each automation's enabled status, trigger groups, step structure, and email content.
4. **Verify triggers** — automations need `subscriber_joins_group` triggers wired to specific group IDs. Use the detail endpoint to confirm.
5. **List subscribers** — confirm real test subscribers are landing in the correct groups.
6. **Check webhooks** — list any existing webhooks and verify their events.
7. **Test the proxy** — if a Cloud Run proxy exists, POST a test subscriber to verify the full flow.

### 7b. ESP Proxy Architecture (Security)

When forms POST subscriber data directly from client-side JavaScript, the API key is exposed. The fix is a server-side proxy:

```
Funnel HTML Form → Cloud Run Proxy → MailerLite API
                   (key server-side)
```

Key design decisions:
- Proxy maps group **slugs** (from `data-funnel` attribute) to group IDs server-side — never expose IDs to the client
- Rate limiting (5 req/min per IP) prevents abuse
- CORS set to allow all origins (funnels are public)
- Returns `{ success: true, redirect_url: "..." }` to the client
- Form actions must point to the proxy URL, not directly to MailerLite

### 7c. Automation Creation & Content

MailerLite's API (post-2022 accounts) has strict limitations for automations:

| What's Possible | What's NOT Possible |
|---|---|
| Create automation shells (name, structure) | **Enable** automations via API |
| Add triggers (subscriber_joins_group) | **Populate rich email content** via API |
| Wire triggers to group IDs | **Reorder/add steps** in a sequence |
| Update step names and metadata | **Mark automation as complete** (complete_workflow flag is read-only) |
| Upload HTML content to email steps | |

**Pitfall:** The response `"The automation is not complete and cannot be enabled."` means the API won't let you set `enabled: True` — only the dashboard can toggle the `complete_workflow` flag.

**Pitfall:** MailerLite login pages use Cloudflare Turnstile bot detection. Automated login (Playwright, Selenium, StealthyFetcher) consistently fails — the Turnstile checkbox requires real human interaction. Do NOT spend time trying to bypass it; report the wall and ask for manual dashboard work.

### 7d. Automation Email Content Design

Each email in a funnel automation follows the PhantomByte brand system:
- Dark background (`#0d0d1a`), purple accent (`#c084fc`), white/light text (`#e0e0ff`)
- Personalized greeting (`Hey {$name},`)
- Clear deliverable title as H1
- CTA button matching brand gradient (`#9D4EDD`)
- Bullet-point value summary
- From: `Vinny Barreca — PhantomByte <hello@phantom-byte.com>`
- Sign-off: `— Vinny` / `PhantomByte`

### 7e. Funnel Email Automation Types

| Funnel Type | Email Pattern | Content |
|---|---|---|
| **Lead Magnet Delivery** | 1 immediate email | Download link + value summary |
| **Flowchart Delivery** | 1 immediate email | Flowchart link + next step CTA (challenge upsell) |
| **Email Challenge** | 5 emails over 5 days (Email→1d delay→Email→...) | Day-by-day mini tool builds |
| **Audit Confirmation** | 1 immediate email | Expectations + resources while waiting |

## PhantomByte CTA Strategy (Site-Specific Decision Framework)

For articles.phantom-byte.com and phantom-byte.com, the CTA type matters strategically:

**Choose: Free tutorials gated by email (lead magnets).**
- Newsletter-only signup converts ~1-2%. Specific free resources convert 10-25%.
- The audience is developers/builders reading deep technical content. They'll trade email for a concrete guide. They won't pay for a tutorial when the articles are already that good and free.
- Paid tutorials are premature until PhantomByte exits preseason (September). Build trust and list first, monetize later.
- Repackage existing deep-dive articles as gated guides: "Sovereign AI Stack Setup Guide", "Agent Evaluation Framework", "AI Agent Debugging Playbook". The content already exists on the site — the gated version adds PDF formatting, checklists, or companion resources.

**The email list IS the compounding asset.** Every address is a future customer for phantom-byte.com services.

**What NOT to do:**
- Don't use "Subscribe to notifications" — too vague, no value prop
- Don't sell tutorials yet — preseason audience hasn't earned trust for paid
- Don't use generic newsletter CTAs — they're opt-in friction without perceived value

## Email Magnet Ideation

When generating email magnet ideas from site content, follow the framework in `references/email-magnet-ideation.md`. Core points:
- Browse full article library, cluster by theme, then ask: what concrete thing can I package?
- Each magnet needs "What you get" (specific) + "Why it works" (tied to actual site content)
- Keep magnets to one page. Instant delivery on signup, no drip delay.
- Lead with broad-appeal magnets for volume (wage tracker, model directory) or quality magnets for services funnel (architecture playbook, deployment checklist)

## Welcome Email HTML Reference
For the Sovereign AI Stack Blueprint welcome email (all-subscribers trigger), see `references/welcome-email-html.md` — contains ready-to-paste HTML, plain text, and MailerLite automation setup steps.

## Task Tracking Workflow (CRITICAL)
When Vinny assigns a task, write it immediately to `/mnt/c/Users/<user>/workspace/TODO.md`. The session todo tool (`todo` tool) is session-scoped only — it disappears when the conversation ends. The workspace TODO.md file persists across sessions. Never use the session todo tool for tracking Vinny's tasks. Update it on every new task assignment and when tasks are completed or superseded.

## Website Redesign & Services Architecture
When Vinny asks to redesign phantom-byte.com or write new services copy based on "everything we've built," see `references/website-redesign-services-audit.md` — covers the full audit workflow (sites, skills, cron, scripts, config, articles), positioning shift from commodity to specialized services, copy voice differences for websites vs articles, and the four-site ecosystem reference.

## Email Delivery (IONOS SMTP)
For sending deliverables via email, see `references/smtp-email-sending.md` — includes credentials, Python template with attachment support, and pitfalls (always write script to file, never inline with `-c`).

## Key Principles
- **Real stories over generic copy** — use actual anecdotes from the content ("$47 burned in 14 minutes" sells better than "save money")
- **Show the thing** — flowchart previews, chapter lists, deliverable tags
- **Match the brand EXACTLY** — colors, fonts, logo treatment, button gradients
- **One HTML file per page** — no build step, no dependencies, open in browser
- **Form fields match funnel intent** — squeeze = 2 fields, audit = 5+ fields to qualify

### Color Role Rules (per Variant)
Each page variant should have ONE dominant CTA color — never mix roles:
- Squeeze = green (action)
- Lead magnet = purple (brand)
- Challenge = amber (warm urgency)
- Application = purple (trust)

### Form Design Rules
- 2-3 fields for top-of-funnel (squeeze, lead magnet)
- 5-7 fields for bottom-of-funnel (audit, application)
- Never exceed 7 fields total

## File Output Structure
```
~/projectname-funnel-mockups/
├── 01-lead-magnet.html
├── 01-lead-magnet.png
├── 02-split-squeeze.html
├── 02-split-squeeze.png
├── 03-email-challenge.html
├── 03-email-challenge.png
├── 04-audit-application.html
└── 04-audit-application.png
```

## Screenshot Command
```python
import asyncio
from playwright.async_api import async_playwright

async def screenshot_page(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
```

## Funnel Variant Types

Four distinct funnel page types, each serving a different funnel stage:

| Funnel Type | Best For | Form Style | CTA Color |
|---|---|---|---|
| **Lead Magnet / Download** | Top of funnel — capture email for free content | Name + Email (2 fields) | Primary brand color |
| **Squeeze Page (Pain → Solution)** | Highest-conversion, minimal friction | Name + Email (2 fields) | Contrasting accent (green for PhantomByte) |
| **Email Challenge / Course** | Nurture — daily value delivery builds trust | Name + Email (2 fields) | Warm accent (amber/gold) |
| **Application / Audit** | Bottom of funnel — qualify and book calls | Multi-field (5-7 fields) | Primary brand color |

### Variant Layout Patterns

**Lead Magnet / Download:**
- Hero headline → ghost/visual → opt-in card (name + email) → social proof bar → content preview list → bottom CTA
- Badge showing what they get (e.g., "2026 Edition • 25 Pages"), numbered feature list, privacy note

**Split Squeeze (Pain → Solution):**
- Two-column: LEFT = pain points with red-accented cards + real failure stories → RIGHT = visual teaser + compact form
- Real failure stories from the content, visual flowchart/cheat sheet preview, ultra-short form

**Email Challenge / Course:**
- Challenge hero (amber/warm gradient) → day-by-day card grid → urgency bar → benefits + form split
- Numbered day cards showing deliverables, cohort urgency, bonus content on final day

**Application / Audit:**
- Minimal hero → trust signals (3 cards) → multi-field application form → process steps
- Dropdown selects for qualification, textarea for pain description, numbered process timeline

## PhantomByte Design System (as of April 2026)
- Background: `#0a0a0a`
- Card bg: `#111111`
- Purple: `#9D4EDD` / Dark: `#7B2CBF`
- Green: `#00FF88`
- White text: `#ffffff`
- Gray text: `#888`
- Font: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- Logo: "PHANTOM" (white) + "BYTE" (purple)
- CTA buttons: `linear-gradient(135deg, var(--purple), var(--purple-dark))`
- Green CTAs for high-contrast actions
- Border radius: 10-14px on cards, 20px on big cards
- Tag: `--dark-border: #1a1a1a`

## Playbook-Specific Hooks
The AI Agent Debugging Playbook has killer real stories for funnel copy:
- "$47 burned in 14 minutes" (reasoning loop)
- "Published a summary of a CAPTCHA page" (tool cascade)
- "847 entries in vector store, didn't know which were real" (memory poisoning)
- "5-agent pipeline deadlocked for 6 hours" (orchestration deadlock)
- "20 agents daily, not as a demo, for actual work" (authority)