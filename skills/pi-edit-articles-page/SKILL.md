---
name: edit-articles-page
description: Make edits to the articles.phantom-byte.com homepage design/layout/CSS/sections and redeploy. Use when the user wants to change the articles homepage (header, hero, footer, colors, sections, ad copy, email capture, constellation links, pagination counts, mobile layout, etc.). Rebuilds index.html from the template + data, then deploys via Cloud Run. ONLY runs the live deploy after explicit user approval.
---

# Edit Articles Page Skill

Use this when the user wants to **change the articles.phantom-byte.com homepage** — anything visual or structural on `index.html` (the field-notes "operations console" redesign).

This is the counterpart to `publish-article` (which adds articles). This skill edits the **page itself**.

## ⚠️ CRITICAL GATE — DEPLOY REQUIRES APPROVAL

Editing files locally is fine. **Deploying to the live site requires explicit approval** (same gate as publish-article):
- "YES" / "deploy" / "deploy it" / "publish" / "push it"

Never run `gcloud builds submit` without explicit approval.

## ARCHITECTURE (READ FIRST)

The homepage is generated, not hand-edited. Three files own it:

| File | Role | Edit it when… |
|------|------|---------------|
| `~/workspace/articles/index-template.html` | The page design — all CSS, header, ticker, hero, featured/FEED markers, constellation, email capture, ad slot, footer, and the inline "console enhancer" JS. Has `<!--FEATURED-->` and `<!--FEED-->` markers. | You want to change the look/layout/CSS/sections/copy of the homepage. |
| `~/workspace/articles/articles-data.js` | The article card list (`window.PB_ARTICLES`, `PB_AUTHORITY`, `PB_NETWORK`). | You want to add/remove/reorder articles, or change the constellation (network) nodes. (Normally `publish-article` adds articles here.) |
| `~/workspace/articles/build-index.js` | Node script that reads `articles-data.js` + `index-template.html` and writes `index.html`. | Rarely edited. Run it after ANY change to the template or data. |
| `~/workspace/articles/index.html` | **GENERATED OUTPUT — never edit directly.** | Never. It is rebuilt by `build-index.js`. |

**Golden rule:** Edit `index-template.html` (and/or `articles-data.js`), then run `node build-index.js` to regenerate `index.html`. Then test locally. Then deploy.

## HOW THE CARDS GET INTO THE PAGE (SEO)

`build-index.js` injects, at the markers:
- `<!--FEATURED-->` → the **newest** article as a static `.featured` card (with a real `<a href>` link).
- `<!--FEED-->` → every **other** article (newest is excluded so it is not shown twice) + authority cards, as static `<article class="panel">` with a real `<a href>` link, `data-cat`, `data-href`, `data-external`.
- `<!--COUNT-->` → the true total notes (articles + authority), shown in the ticker.

**Count semantics (intentional, not a bug):** the newest article is pinned as the featured hero AND excluded from the archive grid, so it appears once. The ticker `NOTES:` shows the true total (e.g. 110). The archive grid + category filter + "All Notes" count are archive-scoped (total − 1, e.g. 109), because they describe the scrollable archive (the featured one is not in it). Don't try to make them match.

All article links are in the HTML source → SEO-friendly and no-JS visible. The inline console enhancer (bottom `<script>` of the template) only does pagination (show N, "Load more"), category filter, and the mobile rail dropdown by reading those `.panel` nodes from the DOM. It does NOT render cards.

## WORKFLOW

### Step 1: Make the edit

Edit `index-template.html` for design/CSS/section/copy changes. Common edits:

- **Colors / fonts** → the `:root` variables at the top of the `<style>` (`--purple`, `--green`, `--black`, `--panel`, `--mono`, etc.).
- **Header / nav** → the `/* HEADER */` block + `<header>` markup. Mobile shows only the green CTA; desktop shows nav + Tutorials + CTA (`@media min-width:820px`).

**⚠️ MOBILE SCROLL GUARD — NEVER REMOVE:** The inline CSS has `overflow-x:hidden` on BOTH `html` AND `.wrap`. This is the two-layer fix for mobile horizontal scroll. iOS Safari ignores `body{overflow-x:hidden}` alone — both `html` and `.wrap` must have it. If you add a new wrapper or container, give it `overflow-x:hidden` too. Run `grep -c 'overflow-x:hidden' index-template.html` after editing to confirm at least 2 occurrences.
- **Ticker** → the `.ticker` block (CONSOLE ONLINE / NOTES count / CADENCE / OPERATOR). The NOTES count is set by JS from the card count — don't hardcode it.
- **Hero** → `.sec-head` / `.sec-title` / `.sec-sub` in `<main>`.
- **Pagination count** → in the inline enhancer JS: `function pageSize(){ return window.innerWidth>=1040 ? 9 : 8; }` (desktop odd/fill, mobile even).
- **Email capture** → `.capture` / `.cap-box` / `.signup-form` (the form id stays `emailSignupForm` / `emailInput` so `scripts/email-signup.js` keeps working).
- **CTA ad slot** → `.ad-slot` / `.ad-creative` (the "Exit the Cloud" sovereign-AI CTA).
- **Constellation (network nodes)** → the static `.const-grid` cards in the template (4 sites). To change them, edit the template directly (they are NOT generated from `PB_NETWORK`).
- **Footer** → the `<footer>` markup + the `/* MOBILE FOOTER */` `@media(max-width:719px)` block. Note: on mobile the Buy Me a Coffee button is shrunk and its label is CSS-replaced via `.foot-cta a::before{content:"☕ tip the ghost"}` (desktop keeps the full "☕ Buy Me a Coffee" button). Edit that `content` to change the mobile label.

For article-list changes (add/remove/reorder articles, or change a card's title/excerpt/category), edit `articles-data.js` instead — then rebuild.

### Step 2: Rebuild

```bash
cd ~/workspace/articles
node build-index.js
```

Expected: `✅ index.html rebuilt` with article/authority counts and the featured article.

### Step 3: Test locally

Open `~/workspace/articles/index.html` in a browser. Relative paths (`images/…`, `scripts/…`) resolve to the repo, so it renders fully (cards, images, GA, Firebase, web-push, email-signup, ad-manager). Verify the edit looks right on desktop and at ~390px mobile.

For a quick mobile check you can open the page and resize, or temporarily add `#rail-open` to the URL to pre-open the mobile category dropdown.

### Step 4: Run SEO maintenance (mandatory before deploy)

```bash
cd ~/workspace/articles
python seo-maintenance.py --all
```

This regenerates `sitemap.xml`, `rss.xml`, `llms.txt` from the article `.html` files (independent of the homepage). It is not affected by homepage edits, but running it keeps everything consistent and validates SEO.

### Step 5: Confirm approval gate

Before deploying, confirm:

```
Confirming: deploy the updated articles.phantom-byte.com homepage to Cloud Run?

Reply YES to confirm.
```

Wait for YES / deploy / publish.

### Step 6: Git commit + deploy

```bash
cd ~/workspace/articles

git add index.html index-template.html articles-data.js build-index.js
git add sitemap.xml rss.xml llms.txt      # if seo-maintenance changed them
git commit -m "edit: articles homepage — <what changed>"

gcloud builds submit --config cloudbuild.yaml
```

### Step 7: Verify live

```bash
sleep 15
curl -sI https://articles.phantom-byte.com/ | head -1                      # expect 200
curl -s https://articles.phantom-byte.com/ | grep -c 'class="panel"'        # expect ~108 (articles) — cards in HTML
curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c '<loc>'   # expect 115+
curl -sI https://articles.phantom-byte.com/ | grep -i strict-transport     # HSTS present
```

## TRACKING / SCRIPTS — DO NOT REMOVE

The homepage keeps these (all must remain functional):
- Google Analytics `G-PDQCZE09E4` (inline gtag).
- Firebase FCM (`firebase-app-compat.js` + `firebase-messaging-compat.js`).
- `scripts/web-push-client.js` (FCM web push) + the push-button relocation script (the external push script nests its button inside `<header>`; the relocation script moves `#phantombyte-push-container` to `document.body` so `position:fixed` anchors to the viewport, not the header's backdrop-filter).
- `scripts/email-signup.js` (MailerLite). The form must keep `class="signup-form"`.
- `scripts/ad-manager.js` (ad slots).
- Pinterest domain verify meta, RSS `<link>`, canonical, JSON-LD `Blog` schema, OG/Twitter tags.

If you change the `<header>`, keep `id`/classes the push-button relocation script relies on (`header`, `phantombyte-push-container`) intact, or update the relocation script accordingly.

## FILE PATHS

| Path | Purpose |
|------|---------|
| `~/workspace/articles/index-template.html` | Homepage template (EDIT THIS for design changes) |
| `~/workspace/articles/articles-data.js` | Article card list (EDIT THIS for article changes) |
| `~/workspace/articles/build-index.js` | Rebuild script (run after edits) |
| `~/workspace/articles/index.html` | Generated homepage (DO NOT edit) |
| `~/workspace/articles/index-LEGACY-BACKUP.html` | Backup of the pre-redesign homepage (rollback reference) |
| `~/workspace/articles/scripts/` | `web-push-client.js`, `email-signup.js`, `ad-manager.js`, etc. |
| `~/workspace/articles/seo-maintenance.py` | SEO auto-generator (run on deploy) |
| `~/workspace/articles/cloudbuild.yaml` | Cloud Build deploy config |

## ROLLBACK

If a deploy breaks, the previous homepage is in git history and `index-LEGACY-BACKUP.html`. To roll back:
```bash
cd ~/workspace/articles
git checkout HEAD~1 -- index.html          # or restore index-LEGACY-BACKUP.html over index.html
gcloud builds submit --config cloudbuild.yaml
```

## NEVER DO

- ❌ Edit `index.html` directly (it is regenerated; your changes will be wiped on next build).
- ❌ Remove the `<!--FEATURED-->` / `<!--FEED-->` markers from the template (build will error).
- ❌ Remove tracking/push/email scripts.
- ❌ Change the email form's `class="signup-form"` (breaks MailerLite hookup).
- ❌ Deploy without running `node build-index.js` after a template/data edit.
- ❌ Deploy without explicit user approval.