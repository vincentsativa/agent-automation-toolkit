# SHIFT44 BI, PDF Guide Summary

**Source:** `stepbystep.pdf`, AI BI Agent: Step-by-Step Business Intelligence Guide

## Phase 1: Competitor Site Registration & Partner Identification
1. Navigate to competitor registration site
2. Input PII: address, date of birth (e.g., 0429), email, random phone number
3. Look for "marketing partners" or "partners" hyperlink on registration page
4. If found → navigate to partners page → copy all DBA names → record to BI sheet
5. Submit registration

## Phase 2: Ad Creative & Offer Link Capture
1. Answer pre-qualifying questions → select ALL possible outcomes to maximize ad exposure
2. For EVERY ad served:
   - **Creative**: copy/screenshot → place in BI sheet (CSV/Google Sheets)
   - **Position**: higher position = higher payout
   - **Offer Link**: copy landing page URL → paste next to creative
3. Document ad-specific DBAs: descriptive language at bottom of ad creative (e.g., "National Health Advisor", "Aragon Advertising LLC") → record alongside the question that triggered the ad

## Phase 3: Advertiser Identification & Contact Strategy
1. Go through all collected offer links/outbound pages
2. Examine supporting pages (privacy policies, terms) to definitively identify actual advertiser company (e.g., Globe Life Inc.)
3. Use LinkedIn to find decision-maker at that company

---

## Key Ad Selectors (from Joe's walkthrough)

```javascript
const adSelectors = [
  'iframe[src*="ad"]',
  '[class*="advertisement"]',
  '[id*="creative"]',
  '[data-ad]',
  '.offer-container',
  'iframe[title*="ad"]'
];
```

## DBA Footer Patterns
Watch for company names at bottom of ad creative:
- "Operated by..."
- "© 2026 Company Name"
- "Powered by..."
- "[DBA] is a service of [PARENT]"