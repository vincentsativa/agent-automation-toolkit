---
name: bi-automation
description: "Business Intelligence automation tool for Joe, competitive ad intelligence pipeline. Scrapling-based site registration, ad capture, DBA extraction, and advertiser identification with local dashboard."
version: 0.2.0
author: Vinny Barreca
metadata:
  hermes:
    tags: [bi, competitive-intel, scripling, automation, dashboard, joe]
    related_skills: [franks-scrapling-pipeline]
---

# BI Automation Tool, Joe's Shift 44 Pipeline

> Status: DESIGN PHASE, awaiting three-way alignment session (Vinny + Hermes + Larry)
> For: Joe (Vinny's brother, SHIFT44) AND Hermes/PhantomByte's own workflows
> Budget: Joe has money, spend what makes sense, but don't waste. Philosophy is fast/cheap on infrastructure, not a financial constraint.
> Blueprint document: `~/cache/documents/doc_826dcc863863_shift44-bi-blueprint.md`

## CRITICAL: DUAL-USE DESIGN CONSTRAINT

**This system is NOT a one-off deliverable for Joe.** Whatever gets built is also run by Vinny/Hermes for PhantomByte's own competitive intelligence. The build must be understandable from the inside by both parties.

Design implications:
- Clean separation between scraper/parser core logic and dashboard/reporting, so both parties can fork, extend, and adapt
- Trigger and cadence must make sense for PhantomByte's existing workflows, not just Shift44's
- Phase 1 is a verified parts box, verified components, not a complete pipeline. The architecture connecting them is still open
- **Next step: three-way design session (Vinny + Hermes + Larry) to define the build/trigger architecture before more code is written**

## PENDING DESIGN QUESTIONS (three-way session)

1. **Trigger**: What event or cadence fires the pipeline? (cron? manual? webhook? kanban task?)
2. **Cadence**: Is this a daily intelligence digest, on-demand research, or continuous monitoring?
3. **Output destination**: Kanban board entries? Email report? CSV dump to a shared folder? Both?
4. **Who sees what**: Does Joe get his own board/channel? Does Vinny get a separate view or a unified one?
5. **Extension points**: Where does PhantomByte's own content/SEO intelligence plug into the same pipeline?

## COST STRUCTURE

| Component | Cost | Notes |
|---|---|---|
| Scrapling (StealthyFetcher) | $0 | Handles Cloudflare/Turnstile/CAPTCHA natively |
| SQLite | $0 | Built into Python, local file |
| Streamlit | $0 | Local dashboard, no server |
| Faker | $0 | Generate realistic PII locally |
| SMS-Activate | ~$0.05/num | Only if site requires phone OTP |
| **Total** | **~$0–$5/month** | No proxies, no residential IPs, no expensive infra |

---

## THE MANUAL PROCESS (Source of Truth)

This is what the tool must automate, derived from the PDF guide and Joe's walkthrough video:

### Phase 1: Competitor Site Registration & Partner Identification

1. Navigate to competitor registration site
2. Input PII: address, date of birth (e.g., 0429), email, random phone number
3. Look for "marketing partners" or "partners" hyperlink on the registration page
4. If found, navigate to partners page and copy all DBA (Doing Business As) names
5. Submit the registration

### Phase 2: Ad Creative & Offer Link Capture

1. After registration, answer pre-qualifying questions, **select ALL possible outcomes** to maximize ad exposure
2. For EVERY ad served, document:
   - **Creative**: copy text or screenshot the ad creative into the BI sheet
   - **Position**: note position on page (higher = higher payout)
   - **Offer Link**: copy the offer/landing page URL, paste next to the creative
   - **Ad-specific DBAs**: find company names at the bottom of the ad creative (e.g., "National Health Advisor", "Aragon Advertising LLC") and record them alongside the qualifying question that triggered the ad
3. For image-heavy ads: screenshot (Command+Shift+4) and attempt to insert into the sheet

### Phase 3: Advertiser Identification & Contact Strategy

1. Go through ALL collected offer links
2. Examine supporting pages (privacy policies, terms) to identify the **actual advertiser company** (e.g., Globe Life Inc.)
3. Use LinkedIn to find a decision-maker at that company

---

## KEY REQUIREMENTS (from Vinny)

- **Fast and cheap**, lightweight approach, no expensive infrastructure
- **Local dashboard** for inputting competitor URLs, PII data, and reviewing results
- **Use Scrapling** for anti-bot circumvention (not IP hiding, just getting around blocking techniques)
- **Deployment-flexible**: must work on both VPS and local computer (Joe hasn't decided yet)
- **Not worried about IP concealment**, Joe said hiding IP is not a concern
- **Must handle**: Cloudflare, Turnstile, CAPTCHA challenges, and other anti-bot measures (Scrapling handles these natively)

---

## TECHNICAL ARCHITECTURE (Draft)

### Core Stack
- **Scraper**: Scrapling (StealthyFetcher), handles Cloudflare, Turnstile, anti-bot
- **Dashboard**: Local web UI (Streamlit or Flask + HTMX) for inputting sites, PII, and reviewing results
- **Data Store**: SQLite or local JSON/CSV files
- **Browser Automation**: Scrapling handles headless browser with stealth

### Module Breakdown

```
bi-automation/
├── dashboard/              # Local web UI
│   ├── app.py              # Streamlit/Flask entry
│   └── templates/          # HTML templates
├── scraper/
│   ├── registrar.py        # Phase 1: Registration + partner extraction
│   ├── ad_capturer.py      # Phase 2: Ad creative/link capture
│   ├── identifier.py       # Phase 3: Advertiser identification
│   └── utils.py            # Shared helpers
├── data/
│   ├── bi_store.db         # SQLite database
│   └── exports/            # CSV/Excel exports
├── config.yaml             # Site configs, PII templates
└── main.py
```

### Dashboard Features
- Input form: competitor URL, PII fields (address, DOB, email, phone)
- Live progress view of registration and ad capture
- Results table: DBAs, ad creatives, offer links, positions, advertiser IDs
- Export to CSV/Excel (BI sheet format)

---

## SCRAPLING USAGE PATTERN

```python
from scrapling.fetchers import StealthyFetcher

sf = StealthyFetcher()
# Phase 1: Load registration page
page = sf.fetch("https://competitor-site.com/register", headless=True, network_idle=True)

# Navigate forms, fill PII, submit
# Phase 2: Capture ads by selecting all qualifying options
# Phase 3: Follow offer links, parse privacy pages
```

Scrapling's adaptive parsing auto-heals broken selectors, sites that change their HTML structure usually still work.

---

## PITFALLS

- **Registration sites change frequently**: Build selectors flexibly, use Scrapling's adaptive features
- **Ads are dynamic/selective**: Must maximize question options to trigger all possible ads
- **Image creatives**: Screenshots are manual in the video; automation needs to handle both text extraction and screenshot capture
- **Multiple ads per question set**: Need to iterate through ALL ad positions, not just the first one
- **Privacy policy parsing**: These are often buried in footers or linked from offer pages, need robust link-following logic

---

## STATUS

- [x] PDF guide read and understood
- [x] Joe's walkthrough video reviewed
- [x] Architecture design finalized with Vinny
- [x] Blueprint written and emailed to hello@phantom-byte.com (May 10, 2026)
- [x] Phase 1 built and verified (`~/bi-agent/phase1/`), components are verified, not a complete pipeline
- [ ] **Three-way design session (Vinny + Hermes + Larry), PENDING. Defines build/trigger architecture before more code**
- [ ] Phase 2/3 architecture (how pieces wire together)
- [ ] Dashboard shell (Streamlit)
- [ ] Testing against real competitor sites

## CURRENT PHASE: PARTS BOX, NOT PIPELINE

Phase 1 is a verified components folder. This is intentional, the architecture connecting the scraper → parser → dashboard isn't locked yet. Do NOT build Phase 2 or 3 until the three-way session defines:
- How the system is triggered and on what cadence
- Where output goes (kanban, email, CSV, or combination)
- Who sees what (Joe's board vs. PhantomByte's view)
- Extension points for PhantomByte's own competitive intelligence workflows