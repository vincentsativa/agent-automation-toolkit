---
name: cpa-lead-gen-funnel
description: Use for CPA lead-gen funnels with email capture and abandonment recovery.
trigger: "Building or rebuilding a CPA lead-gen funnel, email capture page, or abandonment recovery flow."
---

# CPA Lead-Gen Funnel

Full architecture for CPA lead-gen funnels with email capture + abandonment recovery, reverse-engineered from the Shift44/Super Samples funnel pattern (Vinny has the source code + video).

## Entry Flow

`index.php?pid=SOURCE` → Page 1 email capture → `handlepost.php` → CPA offer redirect, with abandonment popup (3 independent triggers).

## Page 1 Email Capture

- Single email field.
- Honeypot field (`emailidaddress`, display:none).
- Validation pipeline: blacklist → domain → oversight.
- Email cookie 365 days.
- Submit to `handlepost.php?page=1`.

## Hidden 14-Field Schema

`first_name, last_name, email, address, city, state, zip, gender, phone, birth_month, birth_day, birth_year, country` (13 + email = 14 total).

Standard flow: email → zip → name/address → demographics.

## 3 Abandonment Triggers (independent, first wins)

1. **Idle timer** (200s, resets on mousemove/click/keydown/scroll, 1s setInterval ping).
2. **Mouse exit** (first `mouseout` where relatedTarget is HTML, fires once).
3. **Back-button trap** (`history.pushState` on load + `popstate` + `history.forward()`).

## Offer URL (CPA payout)

```
https://tracker.net/CLICK_ID/?sub1=SOURCE&sub2=&sub3=PID&sub4=&email=&...&sub5=CAMPAIGN_ID
```
- `sub3=PID` = traffic source.
- `sub5=CAMPAIGN_ID` = creative.

## Tracking Stack

GA (UA+GA4), Google Optimize, Microsoft Clarity, Quastify, AdScore, Cloudflare Insights, custom conversion pixel.

## "Ugly Converts" Philosophy

Rough design on purpose (low overhead signal, lowers guard). Contrast with PhantomByte (authoritative/polished). Know which game you're playing.

## CPA vs Content Funnel

| Dimension | CPA funnel | Content funnel (PhantomByte) |
|-----------|-----------|------------------------------|
| Traffic source | Paid ads | SEO/GEO organic |
| Entry page | index.php?pid=SOURCE | Article |
| Validation | blacklist → domain → oversight | n/a |
| Monetization | CPA offer redirect | affiliates/products |
| Design | intentionally ugly | polished/authoritative |
| Data use | email capture → recovery | reader → subscriber |
| Asset | email list + conversion | authority + SEO |

## Pitfalls

- Ugly is intentional, don't "fix" it.
- Triggers must be independent (first wins), not dependent.
- Cookie set on submit attempt, not validation success.
- `pushState` on window load, not DOMContentReady.
- Pixel fires on popup open, not redirect.
- NO em dashes in funnel copy.
