---
name: deploy-offer-page
description: Adds a standalone offer/landing/sales page to phantom-byte.com as an ADDON (never replacing existing pages), wires and tests its email form against the contact API, applies the full SEO/GEO head block, deploys via Cloud Run, and submits to IndexNow. Use when the user says "add this offer page", "upload this landing page to phantom-byte", "deploy this sales page", "put this on phantom-byte.com", "add an addon page", or provides an HTML offer page to go live. Companion to phantom-byte-site (which covers homepage/about/tutorials edits).
---

# Deploy Offer Page Skill

Adds a self-contained HTML offer/landing page to **phantom-byte.com** as an addon, makes the
email form actually work and prove it, wires SEO/GEO, deploys to Cloud Run, and pings search
engines. First used to ship `email-deliverability-rescue.html` (2026-09-19).

## Golden rules

1. **ADDON ONLY unless told otherwise.** Stage the HTML as a **new file**; never edit/replace
   `index.html`, `about.html`, or `tutorials/`. If internal linking is wanted (nav/footer slot on
   the homepage), **ask first** — that is a change to an existing page.
2. **Review before deploy by default.** Vinny wants to eyeball changes unless he explicitly says
   "deploy" / "ready as is". Prepare everything locally, present the diff + test results, then deploy.
   (Mirrors the articles workflow.)
3. **Never test the form with a fake email address.** This is the deliverability domain — bounces
   hurt. Use `hello@example.com` as the test submitter (it lands internally, no bounce).
4. **Check the API version first.** The live contact API must have the confirmation-link flow
   (`/api/verify` returns 400 for a bad token, not 404). If it 404s, the API needs deploying too
   (see below). The page copy promises a confirmation link; the API must deliver it.

## Repos, services, constants

| Thing | Value |
|---|---|
| Site repo | `~/workspace/phantom-byte-website` |
| Contact API repo | `~/phantom-byte-contact-api` |
| GCP project | `gen-lang-client-0237860564` |
| Region | `us-central1` |
| Cloud Run service (site) | `phantom-byte` |
| Cloud Run service (API) | `phantom-byte-contact-ionos` |
| Contact API endpoint | `https://phantom-byte-contact-ionos-1091380733401.us-central1.run.app/api/contact-form` |
| Verify endpoint | `.../api/verify?token=…` |
| GA4 ID | `G-PDQCZE09E4` (shared with the whole domain) |
| OG image | `https://phantom-byte.com/images/phantombyte-og.jpg` |
| IndexNow key | `phantombyte2026` — served at `https://phantom-byte.com/phantombyte2026.txt` |
| Recipient email | `hello@example.com` |

**How URLs work:** `nginx.conf` uses `try_files $uri $uri.html $uri/ =404;` so a file at
`my-offer.html` is served at **both** `/my-offer` and `/my-offer.html`. **Canonical must be the
extensionless form**: `https://phantom-byte.com/my-offer`.

## Workflow

### 0. Confirm the page is an addon and pick the slug
Read the source HTML. Choose a slug from the file name (lowercase, hyphenated). Verify it is not
already in the repo: `ls ~/workspace/phantom-byte-website`. If it exists, STOP and ask.

### 1. Stage it into the repo
```bash
cp "<source.html>" "~/workspace/phantom-byte-website/<slug>.html"
```

### 2. Wire SEO/GEO into the `<head>`
Insert immediately after the existing `<meta name="description">` (keep the page's own `<style>`
untouched). Replace `<title>`, `<meta description>`, and the slug in the block below. Keep the
page's own visual design — this is metadata only.

```html
<meta name="keywords" content="…5-10 keywords including a brand term…">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Vinny Barreca">
<meta name="theme-color" content="#9D4EDD">

<!-- Google Analytics (G-PDQCZE09E4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PDQCZE09E4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-PDQCZE09E4');
</script>

<link rel="canonical" href="https://phantom-byte.com/<slug>">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://phantom-byte.com/<slug>">
<meta property="og:title" content="…">
<meta property="og:description" content="…same as meta description…">
<meta property="og:image" content="https://phantom-byte.com/images/phantombyte-og.jpg">
<meta property="og:site_name" content="PhantomByte">
<meta property="og:locale" content="en_US">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="https://phantom-byte.com/<slug>">
<meta property="twitter:title" content="…">
<meta property="twitter:description" content="…">
<meta property="twitter:image" content="https://phantom-byte.com/images/phantombyte-og.jpg">
<meta property="twitter:site" content="@PhantomByteAI">

<!-- Favicon: PhantomByte ghost -->
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%239D4EDD'/%3E%3Cstop offset='100%25' stop-color='%237B2CBF'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath fill='url(%23g)' d='M50 5C25 5 10 25 10 50v35l8-8 8 8 8-8 8 8 8-8 8 8V50C66 25 60 5 50 5z'/%3E%3Ccircle fill='%230a0a0a' cx='38' cy='42' r='6'/%3E%3Ccircle fill='%230a0a0a' cx='62' cy='42' r='6'/%3E%3Cellipse fill='%230a0a0a' cx='50' cy='58' rx='8' ry='6'/%3E%3C/svg%3E">

<!-- Service / Offer + FAQ + Breadcrumb Schema (JSON-LD) -->
<script type="application/ld+json">
{ "@context": "https://schema.org", "@graph": [
  { "@type": "Organization", "@id": "https://phantom-byte.com/#organization",
    "name": "PhantomByte", "url": "https://phantom-byte.com",
    "logo": "https://phantom-byte.com/images/phantombyte-logo.png",
    "email": "hello@example.com",
    "founder": { "@type": "Person", "name": "Vinny Barreca" } },
  { "@type": "Service", "@id": "https://phantom-byte.com/<slug>#service",
    "name": "<Service name>", "serviceType": "<short type>",
    "description": "<1-2 sentences>",
    "provider": { "@id": "https://phantom-byte.com/#organization" },
    "areaServed": "Worldwide",
    "offers": [ { "@type": "Offer", "name": "<offer>", "price": "500",
      "priceCurrency": "USD", "description": "<what they get>",
      "url": "https://phantom-byte.com/<slug>" } ] },
  { "@type": "FAQPage", "@id": "https://phantom-byte.com/<slug>#faq",
    "mainEntity": [ { "@type": "Question", "name": "<q>",
      "acceptedAnswer": { "@type": "Answer", "text": "<a>" } } ] },
  { "@type": "BreadcrumbList", "@id": "https://phantom-byte.com/<slug>#breadcrumb",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "PhantomByte", "item": "https://phantom-byte.com/" },
      { "@type": "ListItem", "position": 2, "name": "<Page name>", "item": "https://phantom-byte.com/<slug>" } ] }
] }
</script>
```

Then add a footer link row to the page (inside its existing footer container) so it is not an
orphan:

```html
<p style="margin-top:14px">
  <a href="https://phantom-byte.com">Home</a> &middot;
  <a href="https://phantom-byte.com/about">About</a> &middot;
  <a href="https://phantom-byte.com/tutorials">Tutorials</a> &middot;
  <a href="https://articles.phantom-byte.com/">Articles</a> &middot;
  <a href="mailto:hello@example.com">hello@example.com</a> &middot;
  <a href="https://articles.phantom-byte.com/privacy.html">Privacy</a> &middot;
  <a href="https://articles.phantom-byte.com/terms.html">Terms</a>
</p>
```

### 3. Wire the form
The page's JS must `fetch` the contact API. Required shape:
```js
fetch('https://phantom-byte-contact-ionos-1091380733401.us-central1.run.app/api/contact-form', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, email, domain, message, source: '<page-slug>' })
})
```
- `source` is the tracking label (`'deliverability-offer-page'` for the first one). Always set it.
- Keep a hidden honeypot input (`class="hp"`, `tabindex="-1"`, `aria-hidden="true"`) and return a
  fake success without calling fetch when it is filled.
- The API requires `name` + `email` + (`message` **or** `domain`). A domain-only form is fine.
- Success message should mention the **confirmation link** (the API sends one). Error fallback must
  say "Email hello@example.com directly".

### 4. Update `sitemap.xml` and `llms.txt` (additive)
Add a `<url>` block to `sitemap.xml` (`lastmod` = today, `changefreq` monthly, `priority` 0.8).
Add the service to the `Services Offered` section and the `Key Pages` list in `llms.txt`, and bump
`Last Updated`.

### 5. Run the audit (before deploying)
```bash
python ~/.pi/agent/skills/deploy-offer-page/offer_page_check.py \
  --file ~/workspace/phantom-byte-website/<slug>.html
```
Fix every FAIL. Then do the interactive browser form test (see §7) on a local server.

### 6. Deploy
Site (builds + deploys `phantom-byte`):
```bash
cd ~/workspace/phantom-byte-website
gcloud builds submit --config cloudbuild.yaml .
```
Only if the API needs the confirmation flow (see golden rule 4), deploy it too:
```bash
cd ~/phantom-byte-contact-api
gcloud builds submit --tag gcr.io/gen-lang-client-0237860564/phantom-byte-contact-ionos .
gcloud run deploy phantom-byte-contact-ionos \
  --image gcr.io/gen-lang-client-0237860564/phantom-byte-contact-ionos \
  --platform managed --region us-central1 --allow-unauthenticated --port 8080
```
`deploy-site.sh` also exists but `gcloud builds submit` is the reliable path.

### 7. Test on the live page (mandatory)
- Load `https://phantom-byte.com/<slug>` in a browser.
- Submit with `email = hello@example.com`, real domain, whatever message.
- Confirm the success UI shows the confirmation-link copy and the POST body is correct.
- Test validation: empty required fields, bad email, and honeypot (no request should fire).
- Verify GA fired: a `google-analytics.com/g/collect` POST → **204**.
- Verify the confirmation leg by signing a token (same HMAC as the API) and GETting `/api/verify`:
  it must return 200 with `<h1>Got it. Your address is confirmed.</h1>`. Token recipe:
  `VERIFY_SECRET = sha256('phantombyte-verify-v1:' + SMTP_pass)`, payload
  `{email,name,domain,source,ts}`, token = `base64url(json) + '.' + base64url(hmac_sha256(secret, base64url(json)))`,
  TTL 48h. (SMTP pass lives in `phantom-byte-contact-api/server.js`; repo is private.)

### 8. Final live verification
```bash
curl -s -o /dev/null -w "%{http_code}\n" "https://phantom-byte.com/<slug>"
curl -s -o /dev/null -w "%{http_code}\n" "https://phantom-byte.com/<slug>.html"
curl -s https://phantom-byte.com/sitemap.xml | grep "<slug>"
curl -s https://phantom-byte.com/llms.txt | grep -i "<keyword>"
curl -sI "https://phantom-byte.com/<slug>" | grep -i strict-transport
```
All should pass. Then run the audit against the live URL:
```bash
python ~/.pi/agent/skills/deploy-offer-page/offer_page_check.py \
  --url "https://phantom-byte.com/<slug>" --domain https://phantom-byte.com
```

### 9. Indexing
IndexNow (Bing/Yandex) works immediately; the key file is already live:
```bash
python ~/.pi/agent/skills/deploy-offer-page/offer_page_check.py \
  --url "https://phantom-byte.com/<slug>" --submit-indexnow
```
Google: the Indexing API is quota-limited (**200/day, project-wide**) and often exhausted by
articles. Credentials live in `~/workspace/articles/google-indexing-credentials.json`
(service account `phantom-byte-gsc-reader@…`, no 403 → permission is fine). Google's and Bing's
`sitemap ping` endpoints are **dead** (404/410) — do not rely on them. The page is in the sitemap,
which Google polls. **Vinny usually submits Google himself** — ask before spending quota.

### 10. Report + housekeeping
Report: live URL, form test results table, SEO checklist, indexing status, and whether anything
else changed. **Flag uncommitted git changes** in both repos (site + API) and offer to back up.

## Gotchas learned the hard way

- **API version drift:** the deployed `phantom-byte-contact-ionos` was an older build with no
  `/api/verify`. The page promised a confirmation link that did not exist. Always probe
  `/api/verify?token=x.y` — 400 = good, 404 = deploy the API.
- **Don't 404 the addon:** a fresh slug legitimately 404s before deploy; that is the proof it is a
  pure addon, not a replacement.
- **Google sitemap ping is dead.** IndexNow is the only instant channel besides the Indexing API.
- **Fake test addresses bounce.** Use `hello@example.com` for the submitter.
- **Canonical uses the extensionless URL** (nginx serves both, but pick one canonical).
- **`llms.txt` is standalone** — never add an `LLMs-txt:` directive to `robots.txt` (Google rejects
  it as a syntax error).

## History
- **2026-09-19:** Skill created after shipping `/email-deliverability-rescue` and upgrading the
  contact API to the double opt-in (confirmation-link) flow.
