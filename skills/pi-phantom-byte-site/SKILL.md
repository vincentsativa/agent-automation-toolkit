---
name: phantom-byte-site
description: Deploy, update, and manage phantom-byte.com main site (NOT articles.phantom-byte.com). Covers the AI R&D studio homepage, tutorials page, about page, SEO files, Docker/Cloud Run deployment, and the terminal-aesthetic design system. Use when the user wants to work on, change, or deploy anything related to phantom-byte.com.
---

# PhantomByte Main Site — Deployment Reference

Use this skill when the user wants to work on, change, or deploy anything related to **phantom-byte.com** (the main site, NOT articles.phantom-byte.com).

## Repo & Location

- **Local repo:** `~/workspace/phantom-byte-website`
- **Git remote:** `https://github.com/vincentsativa/phantom-byte-website.git` (branch: `main`)
- **Key files:**
  - `index.html` — the redesigned homepage (inline CSS/JS, no external deps)
  - `about.html` — about page
  - `tutorials/index.html` — tutorials page (served at /tutorials)
  - `sitemap.xml` — SEO sitemap
  - `llms.txt` — LLM reference file
  - `robots.txt` — bot permissions
  - `nginx.conf` — nginx config (HSTS, security headers, caching)
  - `Dockerfile` — nginx:alpine container
  - `cloudbuild.yaml` — Cloud Build deploy config
  - `firebase-messaging-sw.js` — FCM service worker
  - `images/` — phantombyte-og.jpg, phantombyte-logo.png

## Deploy (One Command)

```bash
cd ~/workspace/phantom-byte-website
./deploy-site.sh
```

This builds the Docker image, pushes to gcr.io, deploys to the `phantom-byte` Cloud Run service, and verifies the live site. Same workflow as the articles site (`deploy-article.sh`).

### Manual deploy (if script fails):
```bash
cd ~/workspace/phantom-byte-website
gcloud builds submit --config cloudbuild.yaml .
```

Or:
```bash
gcloud run deploy phantom-byte \
  --image gcr.io/gen-lang-client-0237860564/phantom-byte-website:latest \
  --platform managed --region us-central1 \
  --allow-unauthenticated --port 8080
```

## Domain & DNS

- **Domain:** `phantom-byte.com` → Cloud Run service `phantom-byte` (custom domain mapping)
- **Direct Cloud Run URL:** `https://phantom-byte-mvcy5omgra-uc.a.run.app`
- **DNS:** Google Frontend (GFE) anycast IPs (216.239.x.x)
- **SSL:** Auto-managed by Cloud Run

## Related Services & Repos

| Service | Domain | Repo | Cloud Run Service |
|---------|--------|------|-------------------|
| Main site | phantom-byte.com | `workspace/phantom-byte-website` | `phantom-byte` |
| Articles | articles.phantom-byte.com | `articles-phantom-byte` | `articles` |
| Contact API | — | `phantom-byte-contact-api` | `phantom-byte-contact-ionos` |
| Tutorials | phantom-byte.com/tutorials | (in main repo: `tutorials/`) | (same as main) |

## Design Style (Terminal Aesthetic)

- **Inspired by:** `https://phantom-byte.com/tutorials` (the tutorials page)
- **Color palette:** Purple (#9D4EDD) + Green (#00FF88) on dark (#050507)
- **Fonts:** Monospace (`ui-monospace, 'SF Mono', 'Cascadia Code', Menlo, Consolas, monospace`) for code elements, system sans-serif for body
- **Backdrop:** Scanline overlay + grid pattern via CSS pseudo-elements
- **Terminal block:** `.terminal` class with traffic-light dots, prompt, command output
- **Panels:** `.panel` cards with purple hover glow, `::before` gradient line
- **Kickers:** `// kicker text` in monospace purple
- **Stats:** `.stats-grid` with alternating green/purple numbers

## Key Implementation Details

### Header
- Sticky header with `backdrop-filter: blur(10px)` — this creates a CSS containing block for `position:fixed` children
- **IMPORTANT:** The external web-push script (`web-push-client.js`) appends the push button INSIDE `<header>`. Because of `backdrop-filter`, `position:fixed` on the button resolves against the header, not the viewport. The fix: a relocation script moves `#phantombyte-push-container` to `document.body` after the script inserts it. CSS `!important` overrides also enforce bottom-right positioning.
- Mobile: only "FREE AUDIT" button shows (Tutorials hidden). Desktop: both "Tutorials" (purple) and "Get a Free Audit" (green) show.

### Sections (in order)
1. **Hero** — tag, h1, lead, tagline, terminal block, CTAs
2. **Stats** — 110+ / 20+ / 64 / 6 grid
3. **The Gap** — problem statement
4. **Services** — 8 service panels with "What it is / What you get" + pricing
5. **Process** — 4-step flow (Scope → Build → Test → Ship)
6. **Proof** — authority card + metric stack
7. **Articles** — 6 most recent article cards
8. **Tutorials** — 9 tutorial links with prices
9. **Final CTA** — contact form (kept exactly as original)
10. **Footer** — About | Articles | Tutorials | Sitemap + tagline

### Contact Form (KEPT EXACTLY FROM ORIGINAL)
- **Form ID:** `contactForm`
- **Fields:** name (`contactName`), email (`contactEmail`), message (`contactMessage`)
- **API endpoint:** `https://phantom-byte-contact-ionos-1091380733401.us-central1.run.app/api/contact-form`
- **Email fallback:** `hello@example.com`
- **Script:** Inline, uses `fetch` POST with JSON body, shows success/error status

### SEO
- **Title:** `PhantomByte | AI Infrastructure That Ships`
- **Description:** "PhantomByte is an AI R&D studio. We build sovereign AI stacks, production agent systems, and autonomous content engines. Infrastructure that runs."
- **Canonical:** `https://phantom-byte.com`
- **OG/Twitter:** 13 meta tags (og:type, og:url, og:title, og:description, og:image, twitter:card, etc.)
- **JSON-LD:** Organization + WebSite + OfferCatalog (8 services with real pricing)
- **Sitemap:** `sitemap.xml` (4 URLs: /, /tutorials, /about, /articles)
- **llms.txt:** Full service descriptions for AI crawlers
- **robots.txt:** Allows GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot + wildcard (do NOT add an `LLMs-txt:` directive — Google rejects it as a syntax error; llms.txt is served standalone at the root)

### Tracking & Push
- **Google Analytics:** `G-PDQCZE09E4` (gtag)
- **Firebase FCM:** `firebase-app-compat.js` + `firebase-messaging-compat.js` (deferred)
- **Web push client:** `https://articles.phantom-byte.com/scripts/web-push-client.js` (deferred)
- **Service worker:** `/firebase-messaging-sw.js` (in repo root)

### Anchor Navigation
- All `section[id]` have `scroll-margin-top: 104px` to clear the sticky header when jumping via nav links or CTAs.

## Common Tasks

### Change homepage content
1. Edit `~/workspace/phantom-byte-website/index.html`
2. Deploy: `cd ~/workspace/phantom-byte-website && gcloud builds submit --config cloudbuild.yaml .`

### Update SEO files
- Edit `sitemap.xml`, `llms.txt`, or `robots.txt` in the repo
- Deploy same way (they're included in the Docker build)

### Update tutorials page
- Edit `~/workspace/phantom-byte-website/tutorials/index.html`
- Deploy same way

### Swap ads/CTAs site-wide
- Use the `swap-ads` skill (handles all article pages + index.html + process-article template)

### Backup to GitHub
- Use the `backup-websites` skill

## History

- **2026-06-23:** Full redesign deployed. Replaced placeholder site with AI R&D studio positioning. Terminal aesthetic from /tutorials. Cloud Build config fixed to deploy to `phantom-byte` service (was `phantom-byte-website`). Web-push button relocation fix added. Scroll-margin-top fix for anchored sections.
