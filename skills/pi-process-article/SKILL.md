---
name: process-article
description: Processes raw article input into complete HTML using the NEW V1 console article template (articles.phantom-byte.com redesign, June 2026). Removes "notes for you" sections, copies images, fills the template, builds SEO/schema markup, and outputs locally for review. Use when Vinny provides article text with metadata at bottom.
---

# Process Article Skill (NEW V1 Template — June 2026)

## ⛔⛔⛔ GOLDEN RULE (READ FIRST) ⛔⛔⛔

## 🛑🛑🛑 THE HEADLINE (H1) IS OFF LIMITS — NEVER TOUCH IT (VINNY, REPEATED, FINAL) 🛑🛑🛑

**NEVER change, rewrite, extend, shorten, reorder, "tighten", or "optimize" the H1/headline Vinny provides. Not one word. Not for the keyword report. Not for SEO. No exceptions. Ever.**

- The H1 is reproduced **EXACTLY as Vinny wrote it**. The ONLY permitted transformation is wrapping it in the V1 accent markup — `<span>white part</span> <span class="u">green part</span>` — with **ZERO wording changes**.
- The keyword report's `RECOMMENDED H1` / `APPROVED H1 PATTERN` / `FALLBACK H1 PATTERN` lines are **IGNORED for the H1**. The report governs the `<title>` tag, meta description, keywords, slug and links — **never Vinny's headline**.
- **Do NOT stuff keywords into the headline.** Keyword-stuffing a title is amateur and Vinny rejects it outright.
- If you think the headline should change, **ASK Vinny**. Never change it yourself. Touching the headline is a trust-breaking, fireable offense — Vinny has had to repeat this multiple times in a single week.

---

**This is VINNY'S work, not yours.** You are a FORMATTER, not an author. You take the article text Vinny provides and render it in the V1 template — nothing more.

- **NEVER add, invent, or fabricate any section, paragraph, heading, sentence, or internal-link note that is not in the source article.**
- **⛔⛔⛔ NEVER, EVER add a "SOURCES", "References", "Citations", "Bibliography", "Sources & References", or any similar appended reference-list section. This is VINNY'S #1 most-reported violation and he has ordered it STOPPED. A SOURCES section is NEVER his content — it is ALWAYS fabrication. DO NOT create one under any circumstances, even if the article cites papers or reports inline.** If Vinny wants a sources/references section he will supply it himself as article text. You format only what is given.
- **⛔ NEVER invent paper/arXiv/report citations inline or as a list.** If an inline citation or paper title is not literally in Vinny's source text, do NOT add it. Fabricating arXiv IDs, paper titles, or TensorFeed/Ars story references is the exact behavior that breaks trust. Format only what is given.
- If Vinny's source does not contain a "Connection to Prior PhantomByte Notes" section (or any other section), you DO NOT create one. Ever.
- You do NOT write new content. You do NOT "improve" his writing. You do NOT add transition sentences, summaries, or sections he did not write.
- Internal links to prior notes go INLINE, exactly where Vinny's own prose references the note — never relocated into a fabricated section.
- If you think a section is missing, ASK Vinny. Do not unilaterally add it.

**Violating this rule is the worst thing you can do. It breaks trust. When in doubt, add nothing — format only what is given.**

> **EXCEPTION — VINNY'S NEW LINKING & CONTENT POLICY (Sep 2026):** Vinny has explicitly authorized inline links ONLY where the keyword report or his own prose specifies them. These are the ONE sanctioned exception to "add nothing." Everything else in this GOLDEN RULE still stands: never fabricate sections, never append a SOURCES/References list, never invent paper/arXiv citations, **never add blockquotes, never add links for fun.** The policy adds only the approved inline links and formatting to Vinny's existing prose — it does NOT let you write new sections, invent claims, or change the design.

## ⭐ KEYWORD REPORT PRECEDENCE — VINNY'S STANDING RULE (Sep 2026)

**The keyword report is ALWAYS the right call. It is based on the data.** Wherever this skill gives a generic default and the keyword report gives a specific, data-backed recommendation, **the report wins.** This is Vinny's explicit standing rule — do NOT second-guess it, and do NOT present it to Vinny as a "judgment call" to approve.

Concretely, the report overrides this skill's generic defaults for:

| Decision | Skill's generic default | Report-authoritative value |
|---|---|---|
| **Slug / URL** | "kebab-case from title" (Step 3) | The report's `RECOMMENDED URL` |
| **External links** | link only where prose names a source | Every source in the report's `BACKLINK OPPORTUNITIES` |
| **Internal links** | link only where prose names a prior note | Every slug in the report's `INTERNAL LINKING` section |
| **Title `<title>` tag / meta description / keywords** | derived from the title / first paragraph | The report's recommended title **tag** / meta description / keywords — **`<title>` TAG + META ONLY; NOT the H1** |
| **H1 / headline** | reproduced EXACTLY as Vinny wrote it | 🛑 **OFF LIMITS — the report NEVER overrides the H1. It is not changed, ever.** |
| **Category / angle** | inferred from content | The report's recommended category/framing, when it gives it |

**Scope — report governs *content & SEO*, skill governs *format & safety*:** The report decides **what the page says and how it is addressed** (URL, links, the `<title>` tag, meta, keywords, framing) — **but NOT the H1/headline, which is OFF LIMITS and reproduced exactly as written.** Every format/safety rule in this skill still stands **unchanged** — never fabricate sections, never append a SOURCES/References list, never add blockquotes, keep the exact V1 footer, use the V1 template. The report does NOT authorize new sections, invented claims, or design changes.

**Do not ask Vinny to choose between a skill default and the report.** The report wins by default. Surface it only if the report is internally contradictory, or if a report-named source/URL does not resolve (per the hard-gate link check).

## NEW LINKING & CONTENT POLICY (Sep 2026) — VINNY'S DIRECTIVE

**VINNY'S OVERRIDING RULE (Sep 2026): Do NOT add links for fun. Do NOT add blockquotes. Do NOT touch the design. Only add an inline link where the keyword report / backlink research explicitly specifies it, or where Vinny's own prose directly names a source or a prior note.** This is a constraint, not a checklist to fill. Fewer correct links beat padding. The items below explain HOW to link when you DO link — they are not quotas.

### 1. External source links (ONLY what the keyword report says)
- **VINNY'S DIRECTIVE (Sep 2026): Do NOT add links "for fun."** Only link to sources the **keyword report / backlink research explicitly specifies**, or a primary source Vinny's prose directly names. Never pad to hit a number. If the research names a specific URL, link that exact URL. Fewer, correct links beat padding.
- Link OUTWARD to **primary sources**: official announcement pages, papers, official documentation, vendor docs, arXiv, standards bodies. NOT blogs/aggregators when a primary source exists.
- Use **descriptive anchor text** (e.g. "the official Anthropic announcement"), never bare URLs or "click here".
- Link the source INLINE at the spot in Vinny's prose where the claim is made. Do NOT append a SOURCES/References section (that rule is unchanged — see GOLDEN RULE).
- External links open in a new tab: `<a href="https://…" target="_blank" rel="noopener">descriptive anchor text</a>`.

### 2. Internal links to related PhantomByte articles (ONLY where referenced)
- **VINNY'S DIRECTIVE (Sep 2026):** Only add internal links where Vinny's prose **explicitly references a prior note** (e.g. "Note #149") or the keyword report names a specific slug to link. Do NOT sprinkle internal links onto random subject phrases to hit a count.
- If Vinny names a prior note, link it there (existing house style). If the keyword report specifies a target slug, link only that on the phrase it specifies.
- Use the real slug: `<a href="<slug>.html">real anchor text</a>`. Check `articles-data.js` / the `images/` dir for existing slugs.

### 3. NO blockquote-with-attribution-footer (VINNY'S DIRECTIVE, Sep 2026)
- **Do NOT add a `<blockquote>` with a standalone `— Source Name` footer line.** Vinny rejected this specifically ("— Allen Institute for AI, BenchMIRT announcement" looked bad and he said stop).
- Do NOT manufacture a blockquote just to satisfy a checkbox. If Vinny's prose already contains a quote, keep it as a normal inline quoted sentence/paragraph — no separate blockquote element, no fabricated footer attribution.
- Sources are linked INLINE (see #1) instead. No blockquote element is required.

### 4. At least one named statistic
- Include **at least one named statistic** — a number with a named source (e.g. "GPU utilization averages 15–30% across fleets, per a 2023 Stanford study").
- Attribute it to a real, named source. Do NOT invent numbers. If Vinny's prose has a stat, ensure it's named. If not, use a real stat from a primary source he references.

### 5. Quotable first sentences per paragraph
- Ensure each paragraph's **first sentence is quotable** — a complete, self-contained, punchy statement that stands alone (the kind you'd pull as a pull-quote).
- This is a light-touch edit: tighten the opening sentence of paragraphs that start weakly. Do NOT rewrite Vinny's content wholesale.

### 6. A table or list if the content supports it
- If the content supports it (comparisons, specs, steps, options, data), render it as a **`<table>`** or a proper **`<ol>`/`<ul>`** (house style: `<ol>` with `<li><strong>Lead-in.</strong> …</li>`).
- Do NOT force a table where prose is better. Only where it genuinely helps.

> **Reconciliation with the GOLDEN RULE:** These additions are authorized ONLY when they enhance Vinny's actual prose. **Never pad counts, never add links "for fun," never add blockquotes.** Every link must be one the keyword report specifies or that Vinny directly references. You may NOT invent new sections, new claims, a SOURCES list, or blockquotes. When adding a stat, it must be real and attributable to a source Vinny references — never fabricated. **Do NOT alter the V1 design/template — content only.**

## ⛔ MANDATORY — DO NOT GLOSS OVER THE KEYWORD REPORT'S LINKING SECTIONS

**Before you finalize ANY article, you MUST read and apply the keyword report's `BACKLINK OPPORTUNITIES` and `INTERNAL LINKING` sections.** This was a real miss (article 186): the outward/internal links were skipped on the first pass and only added after Vinny asked. Do not let that happen again.

**Hard gate — complete ALL of these before presenting the article for approval:**
1. **Read the keyword report's `BACKLINK OPPORTUNITIES` section.** It names the external sources to link OUT to. For each named source, find the REAL primary-source URL (web search if the report gives no URL — never fabricate one) and link it INLINE at the exact sentence in Vinny's prose where that claim is made, with descriptive anchor text and `target="_blank" rel="noopener"`.
2. **Read the keyword report's `INTERNAL LINKING` section.** It names prior PhantomByte articles/slugs to cross-link. Add each internal link INLINE where Vinny's prose references that theme, using the real slug from `articles-data.js` / `images/`.
3. **Verify every link resolves** to a real URL / existing slug before presenting. **Note:** the report's URLs are sometimes written without `//` (e.g. `https:arxiv.org/abs/...`) — repair them to proper `https://` and check they return 200.
4. **Do NOT add a SOURCES/References section** — links go inline only (GOLDEN RULE unchanged).

If the keyword report names a source but gives no URL, SEARCH for the real URL. If you cannot find a real URL, tell Vinny rather than silently skipping or fabricating.

## ⚠️ THIS SKILL USES THE NEW DESIGN

As of June 27, 2026, **every article on articles.phantom-byte.com uses the V1 "console" design.** The old template (`why-your-ai-agent-went-paralyzed.html` / `article-template-v2.html`) is RETIRED. Do NOT use it.

**The new template file is:**
```
~/workspace/articles/article-template-new.html
```

It contains `{{PLACEHOLDERS}}` you fill in. It already bakes in: the ghost favicon, Google Analytics (`G-PDQCZE09E4`), FCM web-push (`scripts/web-push-client.js`), `styles/main.css` + `styles/article.css`, the full inline V1 console CSS, the sticky **rail** (operator card + Contents/Archive tabs + archive list + Constellation CTA), the **ticker**, the new **header**, the new **footer**, the **Constellation** section (5 nodes), and all the rail/tab/scrollspy/push-relocate scripts.

## TRIGGER

When Vinny provides article content in this format:
```
Article text: [path or pasted content]
Main Image: [file path]
Inside article image: [file path]
```

Or says: "This article needs to be uploaded using article upload" or "do it local first"

## WORKFLOW

### Step 0: FORMAT ONLY — NEVER AUTHOR (MANDATORY)

Before doing anything, confirm: every heading, paragraph, and sentence in the output MUST come from Vinny's source text. You may only add the standard boilerplate blocks the template requires (email signup, coffee CTA, tutorials CTA, share section, SEO markup, ad slots). You may wrap note references in inline links where Vinny's prose mentions them. You may NOT invent any new section, heading, or content. If the source has no "Connection to Prior PhantomByte Notes" section, do not create one.

### Step 1: Parse Input

Extract from user message:
- **Article text** — file path OR pasted content
- **Main Image path** — local file path for featured image
- **Inside article image path** — local file path for in-article image (may be omitted)
- **Notes section** — anything labeled "notes for you", "info for you", "(info for you", etc. → DELETE COMPLETELY

### Step 2: Clean Article Content

**Remove entirely:**
- Sections starting with `## Notes for you`, `### Notes`, `(info for you`, `notes for you from you`
- Lines starting with `Main Image:`, `Inside article image:`, `Inside Image:`
- Any meta-instructions at the bottom meant for the assistant

**Preserve:** all article body content, all headings (##, ###), FAQ sections, key takeaways sections.

### Step 3: Extract Article Metadata

From the content, extract:
- **Title** — first H1 or first line
- **Description** — first paragraph or a 120–155 char summary (KEEP UNDER 160 chars)
- **Keywords** — comma-separated, from content
- **Article number (N)** — increment the previous highest (check `articles-data.js` or the highest `article-N-main.jpg` in `images/`)
- **Publish date** — today's date `YYYY-MM-DD`
- **Slug** — kebab-case from title **UNLESS the keyword report specifies a `RECOMMENDED URL`; then the report's URL wins** — see §KEYWORD REPORT PRECEDENCE
- **Category** — must match an existing category spelling exactly: `AI Infrastructure`, `AI Security`, `AI Industry`, `AI Engineering`, `AI Policy`, `AI Privacy`, `AI & Investing`, `AI & Society`, `AI Agents`, `AI Collaboration`, `AI Ethics`, `AI News`, `AI Research`, `AI Strategy`, `Cloud Infrastructure`
- **Word count** — count words in the cleaned body
- **Read time** — `ceil(wordCount / 215)` minutes
- **FAQ** — if the article has an FAQ section, capture Q&A pairs for FAQPage JSON-LD

### Step 4: Copy Images

```powershell
$articleNum = "<N>"
Copy-Item "<main_image_path>" -Destination "~/workspace/articles/images/article-$articleNum-main.jpg" -Force
# Inside image (if provided)
Copy-Item "<inside_image_path>" -Destination "~/workspace/articles/images/article-$articleNum-inside.jpg" -Force
```

**Author photo is already in place at `images/author-vinny-new.jpg` — do NOT overwrite it.** The template references it in the rail operator card.

### Step 5: Build the Article Body HTML

Build a single `<div class="article-body"> … </div>` containing, in this order:

> **Apply §NEW LINKING & CONTENT POLICY here:** as you build the body, add ONLY the inline links the keyword report or Vinny's prose specifies (descriptive anchor, `target="_blank" rel="noopener"`), and link internal slugs only where Vinny references a prior note. **No blockquotes, no padding links for fun.** Keep the V1 design untouched.

1. `<p class="lead-paragraph">…first paragraph…</p>`
2. The article sections: `<h2>`, `<h3>`, `<p>`, `<ul>`/`<ol>`, `<figure>`, `<table>`, `<pre><code>`, blockquotes, etc.
   - **Inside image** (if provided): `<figure class="article-image article-image-right"><img src="images/article-N-inside.jpg" alt="…"><figcaption>…</figcaption></figure>` (floats right, max 320px — same as all articles). Use `article-image-right` for right-float, plain `article-image` for full-width.
   - **Inside image placement + alt/figcaption — USE VISION:** look at the actual image and place it adjacent to the section its content matches (e.g. an image showing a GPU rack goes next to the GPU-utilization section). Write `alt` and `<figcaption>` from what is visibly IN the image only — describe, never invent article claims. This is formatting, not authoring. **Content match alone is NOT enough — placement must also satisfy the INSIDE-IMAGE PLACEMENT CHECK in Step 7: top of a section, fully wrapped by tall text below it, 1–2 line caption. Never the last element before the next `<h2>`.**
   - **Inject `id="sec-K"` on every `<h2>`** in order (K=1,2,3…). These ids are what the TOC links to.
   - **Code blocks — MOBILE-SAFE RULE (mandatory):** always render as `<pre><code class="language-python">…</code></pre>`. NEVER put an inline `style=` on `<pre>` or `<code>`. The stylesheet `styles/article.css` is the single source of truth for code-block wrapping — it sets `white-space: pre-wrap` + `overflow-wrap: anywhere` on `.article-body pre code` and `min-width: 0` on `.console > *`, so long identifiers / import paths / URLs wrap instead of blowing out the CSS grid and breaking mobile scrolling. Inline styles bypass these rules and reintroduce the mobile scroll bug (see the `semantic-cache-revolution-llm-api-costs.html` incident). The ONLY exception is an ASCII-art / box-drawing diagram that must NOT wrap: render it as `<pre style="overflow-x: auto; white-space: pre;">…</pre>` (no `<code>` child) so it scrolls horizontally inside the viewport-confined box — the grid guard keeps it from breaking the page.
3. **Email signup** block (see §STANDARD BLOCKS below)
4. **Buy Me a Coffee CTA** block
5. **Tutorials CTA** block (only if the article is engineering/infrastructure-flavored — otherwise omit)
6. **Share section** block

This entire `<div class="article-body">…</div>` string goes into `{{ARTICLE_BODY}}`.

> The body uses classes styled by `styles/article.css` (lead-paragraph, article-image-right, article-email-signup, coffee-cta, tutorials-cta, article-footer, share-section, related-articles, tables, code blocks, etc.). If the article needs custom styling (charts, zones, comparison tables), add a `<style>` block and put its contents into `{{ARTICLE_STYLES}}` — do NOT rely on external sheets beyond main.css/article.css.

### Step 6: Build the TOC

From the `<h2>`s in the body (in order), build the TOC `<ul>` and put it into `{{TOC}}`:
```html
<ul class="toc" id="toc">
  <li><a href="#sec-1" data-target="sec-1">$150M in One Day</a></li>
  <li><a href="#sec-2" data-target="sec-2">The Verification Horizon</a></li>
  …
</ul>
```
Truncate long labels to ~48 chars. If the article has no `<h2>`s, use:
```html
<ul class="toc" id="toc"><li class="arch-empty">No sections</li></ul>
```

### Step 7: Fill the Template Placeholders

Read `article-template-new.html`, then replace each `{{PLACEHOLDER}}`:

| Placeholder | Value |
|------|-------|
| `{{TITLE_TAG}}` | `<title>{Title} - PhantomByte</title>` (keep under 60 chars if possible) |
| `{{HEAD_META}}` | `<meta name="description" content="…">` + `<meta name="keywords" content="…">` + all `og:*` + all `article:*` (published_time, author, section) + all `twitter:*` + `<link rel="canonical" href="https://articles.phantom-byte.com/{slug}.html">` — each on its own line. **`og:image` and `twitter:image` MUST be `https://articles.phantom-byte.com/images/article-N-main.jpg?v=N` (versioned with the article number — see SEO REQUIREMENTS for the X cache-buster rule).** |
| `{{JSONLD}}` | The TechArticle `<script type="application/ld+json">…</script>` block, plus a FAQPage block if the article has FAQ. See §JSON-LD below. |
| `{{ARTICLE_STYLES}}` | Any article-specific `<style>…</style>` blocks (usually empty string) |
| `{{NOTE_NUM}}` | The article number, e.g. `112` |
| `{{CATEGORY}}` | The category, e.g. `AI Infrastructure` |
| `{{CATEGORY_UPPER}}` | `AI INFRASTRUCTURE` |
| `{{READ_TIME}}` | e.g. `8 min` |
| `{{READ_TIME_UPPER}}` | e.g. `8` |
| `{{DATE_TICKER}}` | e.g. `JUN 27 2026` (from publish date, `%b %d %Y` uppercased) |
| `{{DATE_DISPLAY}}` | e.g. `June 27, 2026` |
| `{{WORDS}}` | word count with thousands comma, e.g. `1,700` |
| `{{LEVEL_ABBR}}` | `Inter` (Intermediate), `Beg`, `Adv`, `All`, etc. |
| `{{TITLE}}` | The H1 title text **with the green accent split**: `<span>White part</span> <span class="u">Green part</span>` — the white part is the lead-in (before a colon if the title has one, else the first half of the words), the green part is the punchline (after the colon, or the second half). This matches the approved V1 design where `.article-title .u{color:var(--green)}`. Do NOT render the title as flat all-white text. |
| `{{DECK}}` | The meta description, truncated to 155 chars at a word boundary + `…` (HTML-escaped) |
| `{{TOC}}` | The TOC `<ul>` from Step 6 |
| `{{FEATURED_FIGURE}}` | `<figure class="article-featured-image"><img src="images/article-N-main.jpg" alt="…"><figcaption class="image-caption">…</figcaption></figure>` |
| `{{TOP_AD}}` | The standard top ad slot (see §STANDARD AD SLOT) |
| `{{ARTICLE_BODY}}` | The `<div class="article-body">…</div>` from Step 5 |
| `{{BOTTOM_AD}}` | The standard bottom ad slot (see §STANDARD AD SLOT) |

**After filling, VERIFY no `{{...}}` placeholders remain** (grep the output file). If any remain, you missed one.

**THEN VERIFY THE `.article-body` WRAPPER (MANDATORY — prevents the "looks like trash" bug).** This is the single most common build failure. The built file MUST contain exactly **ONE** `<div class="article-body">` that opens immediately after the top ad slot (`ad-slot-article-top`) and closes immediately before the bottom ad slot (`ad-slot-article-bottom`), wrapping the lead paragraph, ALL sections, and ALL standard blocks. If this wrapper is missing, NO body typography applies (`.article-body p` margins, `.article-body h2` `//` prefix + green border, `.article-body a` green links, `.article-body strong` white, `.article-body li` arrows) and the article renders as unstyled flat "trash." Run:
```bash
cd ~/workspace/articles
grep -c '<div class="article-body">' {slug}.html          # MUST be 1
python -c "print(open('{slug}.html',encoding='utf-8').read().count('<div')-open('{slug}.html',encoding='utf-8').read().count('</div'))"   # MUST be 0 (balanced)
```
Confirm the `<div class="article-body">` appears right after the `<!-- CTA Slot (Top) -->` block and the matching `</div>` appears right before `<!-- CTA Slot (Bottom) -->`. Compare against a known-good recent article (e.g. `llm-inference-cost-energy-per-request.html`) if unsure.

**INSIDE-IMAGE CLASS CHECK (MANDATORY — prevents the "image not wrapped on desktop" bug).** The inside article image MUST use `class="article-image article-image-right"` (floats right, max 320px on desktop, stacks full-width only at ≤680px). A bare `<figure class="article-image">` renders full-width and is WRONG — this is the regression that happened on the sovereign-compute article and got flagged by Vinny. Run:
```bash
cd ~/workspace/articles
grep -c '<figure class="article-image article-image-right">' {slug}.html   # MUST be 1 (your inside image)
grep -c '<figure class="article-image">' {slug}.html                        # MUST be 0 (no bare full-width figure)
```
Every article's inside image must match the reference render in `nvidia-pair-personal-ai-cluster.html`.

**INSIDE-IMAGE PLACEMENT CHECK (MANDATORY — prevents the "orphaned figure" bug).** The class check above keeps the float *narrow*; this check keeps it *wrapped*. A right-float figure only looks deliberate when the text that follows it in the **same section** is at least as tall as the figure. If that text is shorter, the box overhangs the section boundary into the gap before the next `<h2>` and reads as "thrown in by someone who does not give a fuck" — this happened on article 191 and Vinny flagged it.

**The house pattern (verified on #187, #188, #189, #190, #191):** the right-float inside figure sits at the **top of a section** — immediately after the `<h2>`, or after the `<h2>` plus one short intro paragraph — and is followed by a **tall block** (a long `<ol>`/`<ul>`, or several long paragraphs) that fully wraps it.

Use this order:
```html
<h2>SECTION TITLE</h2>
<p>Short intro paragraph (1–2 sentences).</p>
<figure class="article-image article-image-right">…</figure>
<ol>…long list…</ol>   <!-- or several long paragraphs — must be taller than the figure -->
```

**Placement rules:**
1. **NEVER place the figure as the last thing in a section** (directly before the next `<h2>`). That is the orphan bug. The float must finish *inside* the section, with full-width text below it.
2. **Figure height must be ≤ the text that follows it in that section.** Estimate the rendered figure height as `320 × (imageHeight / imageWidth)` (the 320px right-float width) **plus the caption height**, then confirm the wrapping text is taller than that total.
3. **Keep the `<figcaption>` to 1–2 lines — one short sentence.** House captions are a single sentence (see #188, #189, #190). A 5–7 line caption makes the box bottom-heavy and is a leading cause of the orphan. Do NOT write paragraph-length captions.
4. **Satisfy content match AND rules 1–3.** If the section whose content matches is too short to wrap the figure, place it at the top of the *next* section it also matches rather than orphaning it at the bottom of the matching one.

**Verify placement visually before presenting** (mandatory — the class/height greps cannot catch an orphan):
```bash
cd ~/workspace/articles
# loading="lazy" does NOT fire in a headless full-page screenshot, so the figure renders as an EMPTY BOX.
# Make a throwaway copy with lazy stripped, screenshot it, and eyeball the wrap:
python -c "s=open('{slug}.html',encoding='utf-8').read();open('_tmp.html','w',encoding='utf-8').write(s.replace('loading=\"lazy\">','>'))"
# open _tmp.html, screenshot + crop that band, and confirm the figure's bottom edge ends at or above the
# end of the wrapping text and does NOT overhang into the next <h2>. Then delete _tmp.html.
```

**Screenshot gotcha — do NOT misdiagnose an empty box.** A blank figure box in a headless screenshot is almost always `loading="lazy"` never firing, NOT a broken image or bad markup. Before reporting a bug, confirm the network log shows `GET images/article-N-inside.jpg → 200`, and/or render the `_tmp.html` lazy-stripped copy. Article 191 was nearly misreported as a broken image this way.

**Inside-image shape is house standard:** every article #180–#191 ships a **1254×1254 square** inside image rendered at **320px right-float**. A dense square infographic is therefore the accepted house look — do NOT "fix" it by switching to a full-width bare `<figure class="article-image">` (that is a REJECT per the class check above). Dense infographic art will be small on desktop; that is by design.

### Step 8: Punctuation Check (MANDATORY)

> ⚠️ **VINNY'S HARD RULE: EM DASHES (—) ARE NEVER ALLOWED in article body text.**
> This includes text YOU write (internal linking paragraphs, transition sentences, etc.) — not just text from the article source.
> Replace any em dashes with commas or other proper punctuation.
> The CRITICAL RULES table at the bottom of this skill enforces this. Read it before every article.

Scan ALL article body text for improper punctuation and fix:
- ` - ` (space-dash-space) used as a separator → replace with `, ` in most cases
- ` -- ` → `, ` (comma) — do NOT convert to em dashes
- Em dashes (`—`) → replace with commas or other proper punctuation
- Hyphens used where commas/semicolons/periods are grammatically correct

**Do NOT touch:** hyphens in compound words (`state-of-the-art`, `multi-agent`), hyphens in numbers (`45-minute`), dashes in URLs/paths, dashes inside `<pre>`/`<code>`, the `- ` starting list items.

### Step 9: Save for Review

Save to: `~/workspace/articles/{slug}.html`

### Step 10: Update the Archive List in the Template (housekeeping)

The rail's "Archive" tab shows a static recent-notes list. After publishing article N, prepend article N to the `<div class="arch-list" id="archList">` in `article-template-new.html` (newest first), and drop the oldest if the list grows beyond ~24 items. Also update the category counts in the `.arch-chips`. This keeps the NEXT article's sidebar current. (Existing articles keep their snapshot — that's fine.)

### Step 11: Notify User

```
✅ Article built locally (NEW V1 design)

**File:** ~/workspace/articles/{slug}.html
**Images:** article-N-main.jpg (+ article-N-inside.jpg if provided)
**SEO:** meta + OG + Twitter + TechArticle JSON-LD (+ FAQ JSON-LD if FAQ) + canonical
**Internals:** GA G-PDQCZE09E4, FCM web-push, email-signup, share-buttons, new footer, constellation, rail+TOC+archive — all intact.

Review it in a browser. Reply "YES"/"deploy"/"publish" to deploy via the publish-article skill.
```

## PRODUCT CTA SLOT (Top & Bottom) — Sovereign AI Stack Blueprint

NOTE: this is NOT an "ad." It is Vinny's own product — the **Sovereign AI Stack blueprint** (https://sovereign-ai-stack.phantom-byte.com). The HTML keeps the legacy class names `.ad-slot` / `.ad-creative` (do not rename them — `scripts/ad-manager.js` and the swap-ads skill reference them), but treat it as a product CTA, not third-party advertising. Use the CURRENT creative (managed by the swap-ads skill). As of June 2026 it is the "Exit the Cloud" sovereign-ai-stack creative. Fill `{{TOP_AD}}` and `{{BOTTOM_AD}}` each with:

```html
<div class="ad-slot ad-slot-article-top">
  <a href="https://sovereign-ai-stack.phantom-byte.com" target="_blank" rel="noopener">
    <div class="ad-creative">
      <p class="k">⚠️ Exit the Cloud</p>
      <h4>Own Your Weights. Own Your Data.</h4>
      <p>The cloud AI era is a data-harvesting trap. Stop being the product and start being the owner. Build your local sovereign stack today.</p>
      <span class="btn">Download The Blueprint</span>
    </div>
  </a>
</div>
```
(For the bottom slot use `ad-slot-article-bottom` as the second class.) If the swap-ads skill has changed the creative, use whatever the swap-ads skill says is current — check an existing recent article (e.g. `verifying-agents-is-now-harder-than-generating-them.html`) for the latest creative before filling.

**Alignment (desktop):** Only the article body is centered. `.article-body` is `max-width:760px; margin:0 auto` so the reading text has equal dead space on both sides of the ~968px main column. The `.article-title` and `.article-deck` stay left-aligned as designed (do NOT add `margin:0 auto` to them). The product CTA slot (`.ad-slot`) is full-width (`max-width:none`) with `text-align:center`, and `.ad-creative` has `text-align:center`. Do NOT change `.ad-slot` to `max-width:728px`, remove `text-align:center`, or add `margin:0 auto` to the title/deck.

## STANDARD BLOCKS (inside the article body)

**Email signup** (keep `id="articleEmailSignup"` and class `signup-form` so `scripts/email-signup.js` binds):
```html
<div class="article-email-signup">
  <h3>Get More Articles Like This</h3>
  <p>Getting your AI agent setup right is just the start. I'm documenting every mistake, fix, and lesson learned as I build PhantomByte.</p>
  <p>Subscribe to receive updates when we publish new content. No spam, just real lessons from the trenches.</p>
  <form class="signup-form" id="articleEmailSignup">
    <input type="email" placeholder="Enter your email" required>
    <button type="submit">Subscribe</button>
  </form>
</div>
```

**Buy Me a Coffee CTA:**
```html
<div class="coffee-cta">
  <p>Enjoyed this article?</p>
  <a href="https://buymeacoffee.com/drvincentsativa" target="_blank" rel="noopener" class="coffee-btn-large"><span>☕</span> Buy Me a Coffee</a>
  <p class="coffee-subtext">Support PhantomByte and keep the content coming!</p>
</div>
```

**Tutorials CTA** (optional — engineering/infra articles):
```html
<div class="tutorials-cta">
  <h3>Build Real AI Infrastructure</h3>
  <p>PhantomByte teaches you to build real AI infrastructure yourself: local AI stacks, autonomous agents, multi-agent orchestration, web scraping, and custom tools. Step-by-step PDF tutorials you download, follow, and deploy. No subscriptions. No fluff. Just skills that ship.</p>
  <div style="text-align:center"><a class="tbtn" href="https://phantom-byte.com/tutorials" target="_blank" rel="noopener">Browse Tutorials →</a></div>
</div>
```

**Share section** (keep the `share-btn-*` classes so `scripts/share-buttons.js` binds):
```html
<div class="article-footer">
  <div class="share-section">
    <h3>Share this article</h3>
    <div class="share-buttons">
      <button class="share-btn">Share</button>
      <button class="share-btn-twitter">Twitter</button>
      <button class="share-btn-facebook">Facebook</button>
      <button class="share-btn-linkedin">LinkedIn</button>
    </div>
  </div>
</div>
```

## JSON-LD

**TechArticle** (always):
```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "<title>",
  "alternativeHeadline": "<short subtitle>",
  "author": { "@type": "Person", "name": "Vinny Barreca", "url": "https://phantom-byte.com" },
  "publisher": { "@type": "Organization", "name": "PhantomByte", "logo": { "@type": "ImageObject", "url": "https://articles.phantom-byte.com/images/phantombyte-logo.png" } },
  "datePublished": "<YYYY-MM-DD>",
  "dateModified": "<YYYY-MM-DD>",
  "description": "<description>",
  "articleBody": "<first 2-3 sentences>",
  "wordCount": "<N>",
  "timeRequired": "PT<M>M",
  "proficiencyLevel": "Intermediate",
  "articleSection": "<category>",
  "keywords": "<comma-separated>",
  "image": { "@type": "ImageObject", "url": "https://articles.phantom-byte.com/images/article-N-main.jpg", "width": 1200, "height": 630 },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://articles.phantom-byte.com/<slug>.html" }
}
```

**FAQPage** (only if the article has an FAQ section): standard FAQPage schema with each Q/A. Wrap each JSON-LD in its own `<script type="application/ld+json">…</script>` and join them with a newline into `{{JSONLD}}`.

## CRITICAL RULES

| Rule | Enforcement |
|------|-------------|
| **NEVER include notes** | Delete ALL "notes for you" sections completely |
| **NEVER include metadata lines** | Remove "Main Image:", "Inside article image:" from content |
| **Use the NEW V1 template** | `article-template-new.html` — NOT the old templates |
| **No leftover placeholders** | grep the output; every `{{...}}` must be filled |
| **Author photo** | `images/author-vinny-new.jpg` (already in template — don't touch) |
| **Inside image placement** | `class="article-image article-image-right"` (float right, max 320px) — same as all articles. **Top of a section, after the H2 + a short intro, followed by a TALL block that wraps it; NEVER the last element before the next `<h2>` (orphan bug — flagged on article 191). Caption = 1–2 lines max.** Verify visually using a lazy-stripped copy (an empty box in a headless screenshot is a `loading="lazy"` artifact, not a broken image). |
| **Punctuation check** | Scan body for improper ` - ` dashes → commas. **EM DASHES (—) ARE NEVER ALLOWED in article body text.** Replace any found with commas or other proper punctuation. This is Vinny's hard rule — do not add em dashes to his writing.
| **All SEO included** | Meta, OG, Twitter, TechArticle JSON-LD (+ FAQ if present), canonical |
| **Title under 60 chars** | For the `<title>` tag (SERP truncation) |
| **Description 120–160 chars** | For meta description |
| **Footer is the NEW footer** | Already baked into the template (Network column: PhantomByte Services, Tutorials, Sovereign AI Blueprint, Vincent Sativa; Articles column; Social column; Buy Me a Coffee). Do NOT revert to the old `site-footer` with `../../index.html` Home link. |
| **Outbound links (ONLY approved)** | Link outward ONLY to sources the keyword report/backlink research specifies or Vinny's prose directly names — descriptive anchor text, inline where the claim is made, `target="_blank" rel="noopener"`. **Never pad to hit a count.** See §NEW LINKING & CONTENT POLICY. |
| **Internal links to PhantomByte articles (ONLY referenced)** | Add internal links ONLY where Vinny's prose explicitly names a prior article (e.g. "PhantomByte #124, 'Your Agent's Harness Is Your Real Model'") or the keyword report names a slug — wrap the title in `<a href="<slug>.html">`. **Never sprinkle additional links to pad a count.** Check `articles-data.js` / `images/` for real slugs. See §NEW LINKING & CONTENT POLICY. |
| **⛔ NEVER FABRICATE SECTIONS (HARD RULE)** | This is VINNY'S work, not yours. NEVER add, invent, or create any section, paragraph, heading, or sentence that is not in the article source text. If the source has no "Connection to Prior PhantomByte Notes" section, DO NOT create one. If the source has no FAQ, DO NOT add FAQ. If the source has no Related Articles, DO NOT add them. You format what Vinny wrote. You do NOT write new content for him. Any deviation must be explicitly approved by Vinny first. |
| **⛔ NEVER add a SOURCES / References section (HARDEST RULE)** | NEVER append a "SOURCES", "References", "Citations", or "Bibliography" section. It is never Vinny's content. Do not create one even when the article mentions papers/reports inline. Do not fabricate arXiv IDs, paper titles, or news story references. This has been reported repeatedly. When in doubt, add nothing. **External source links go INLINE (per the new policy) — never collected into a list at the end.** |
| **Internal links — HOUSE STYLE (inline, where referenced)** | Link the note's subject phrase INLINE, exactly at the spot where the prose references it — do NOT relocate links into a fabricated section. E.g. in a paragraph that says "Note #147 showed that GPU utilization is the new moat", link the phrase: `Note #147 showed that <a href="gpu-utilization-ai-moat.html">GPU utilization is the new moat</a>`. Keep the note number as plain text immediately before the linked phrase. Link each referenced note exactly once, at its first mention. NEVER link a whole sentence as one hyperlink. |
| **Lists — HOUSE STYLE (`<ol>` + bold lead-ins)** | Numbered lists MUST be proper `<ol>` with `<li><strong>Lead-in.</strong> rest of the text</li>`. NEVER render a list as plain-text paragraphs starting with "One." / "Two." / "Three." — Vinny rejects that as "text looks like shit." Use real list markup so the arrows/bullets and bold lead-ins render. |
| **Blockquote** | **DO NOT add blockquotes.** Vinny rejected the `— Source` attribution footer. Keep quotes as inline prose; link sources inline instead. No blockquote element. See §NEW LINKING & CONTENT POLICY. |
| **Named statistic (≥1, REQUIRED)** | Include at least one named statistic attributed to a real source. Never invent numbers. See §NEW LINKING & CONTENT POLICY. |
| **Quotable first sentences (REQUIRED)** | Each paragraph's first sentence should be a complete, quotable, self-contained statement. Light-touch tightening only. See §NEW LINKING & CONTENT POLICY. |
| **Table/list when supported (REQUIRED)** | If content supports it (comparisons, specs, steps, data), render as `<table>` or proper `<ol>`/`<ul>`. Don't force it. See §NEW LINKING & CONTENT POLICY. |
| **article-body wrapper present** | See Step 7 verification — exactly ONE `<div class="article-body">`, divs balanced, opens after top ad / closes before bottom ad. Missing wrapper = unstyled flat text. |
| **Related articles** | Do NOT add a "Related Articles" section unless explicitly asked |
| **Build locally first** | Always show user before deploying |
| **Keep main.css + article.css** | The template loads them — they style the article body content. Do not remove. |
| **Code blocks mobile-safe** | Always `<pre><code class="language-x">…</code></pre>`. NEVER inline `style=` on `<pre>`/`<code>` (except ASCII-art diagrams: `<pre style="overflow-x:auto;white-space:pre">`). Inline styles bypass `article.css` and reintroduce the mobile horizontal-scroll blowout bug. |
| **Mobile scroll guard (MANDATORY)** | The inline V1 console CSS in `article-template-new.html` now has `overflow-x:hidden` on BOTH `html` AND `.wrap`. This is the two-layer mobile scroll fix: `html{overflow-x:hidden}` prevents iOS Safari from allowing horizontal page scroll, and `.wrap{overflow-x:hidden}` catches any overflowing child content. **NEVER remove these.** If you add a new wrapper or container, give it `overflow-x:hidden` too. The `body{overflow-x:hidden}` alone is NOT sufficient on mobile browsers. |

## SEO REQUIREMENTS (EVERY ARTICLE)

- Title tag under 60 chars. Format: `Primary Keyword - PhantomByte`
- Meta description 120–160 chars with primary keyword + CTA
- `article:published_time`, `article:author` (Vinny Barreca), `article:section` (category)
- `og:image` = `https://articles.phantom-byte.com/images/article-N-main.jpg?v=N` (MANDATORY cache-buster — see note below)
- `twitter:image` = `https://articles.phantom-byte.com/images/article-N-main.jpg?v=N` (MUST match og:image, same `?v=N`)
- Canonical = `https://articles.phantom-byte.com/<slug>.html`

**X CARD CACHE-BUSTER (MANDATORY — do not skip):** X/Twitter caches link-preview cards aggressively and will NOT re-fetch the same image URL. If the image isn't live the instant the link is first shared, X caches a broken/empty card forever. To prevent this, ALWAYS append `?v=N` (the article number) to BOTH `og:image` and `twitter:image`. Because every article has a unique `N`, every article gets a unique image URL, so X is forced to re-fetch the image fresh. If an image is ever re-uploaded for an existing article, BUMP the version (e.g. `?v=N` → `?v=N+1`) so X re-fetches again. Never ship an article with a bare, unversioned og:image.

**og:site_name + twitter:card (MANDATORY):** Every article MUST also include `<meta property="og:site_name" content="PhantomByte">` and `<meta property="twitter:card" content="summary_large_image">`. Missing `og:site_name` is a common cause of degraded X cards. Verify both with the grep check in Step 7.
- TechArticle JSON-LD with `datePublished`, `wordCount`, `timeRequired`, `articleSection`, `keywords`, `image`
- FAQPage JSON-LD if FAQ present

## FILE PATHS

| Path | Purpose |
|------|---------|
| `~/workspace/articles/article-template-new.html` | **THE template** (fill placeholders) |
| `~/workspace/articles/{slug}.html` | Output article |
| `~/workspace/articles/images/article-N-main.jpg` | Featured image |
| `~/workspace/articles/images/article-N-inside.jpg` | Inside image |
| `~/workspace/articles/images/author-vinny-new.jpg` | Author photo (in template — don't touch) |
| `~/workspace/articles/styles/main.css` + `styles/article.css` | Body content styling (loaded by template) |
| `~/workspace/articles/scripts/` | web-push-client.js, email-signup.js, ad-manager.js, share-buttons.js (loaded by template) |
| `~/workspace/articles/convert-to-new-design.py` | Bulk legacy converter (already run June 27 2026 — do NOT re-run; it's idempotent but unnecessary) |
| `~/workspace/articles/seo-maintenance.py` | SEO generator (run during deploy via publish-article) |

## TOOLING NOTES

- **Use `python`, NOT `python3`** on this machine (`python3` is not installed). Any Python one-liner / script in this skill or the publish skill must be run as `python ...`.
- **Edit-tool whitespace gotcha:** in a filled template the consecutive HTML tags are separated by a single `\n` (no blank lines). When making targeted edits, match the exact single-newline spacing or the edit fails atomically. If an edit fails, re-check the whitespace rather than retrying blindly.
- **Vision is available (July 2026+):** pi now has working image input. When the selected model is vision-capable, screenshots/images are seen natively; otherwise the `vision-proxy` extension auto-bridges through `ollama/glm-5.3-flash:cloud` (see `~/.pi/agent/extensions/vision-proxy.ts`). Use it to: (1) inspect the main/inside article images for placement, alt text, and captions; (2) screenshot the built article locally (browser_screenshot + read) and visually verify layout before showing Vinny. Structural grep checks (wrapper present, divs balanced) still apply as a belt-and-suspenders step.
- **`loading="lazy"` + headless screenshots (verification gotcha):** lazy images do NOT load during a headless full-page capture, so any `<figure>` with `loading="lazy"` renders as an **empty box** in `browser_screenshot` output — including article #190's, which is known-good. Do not report a broken image based on this. Confirm via the network log (`GET images/article-N-inside.jpg → 200`) and/or screenshot a throwaway copy with `loading="lazy">` stripped to `>`. Note: `browser_evaluate` in this harness returns no value, so `scrollIntoView` cannot be used to force the lazy load — strip the attribute instead.

## BACKUP / ROLLBACK

- Pre-redesign backup of every article HTML: `~/workspace/articles/backups/pre-redesign-2026-06-27/`
- Git backup branch: `backup/pre-redesign-2026-06-27` (the live state before the redesign)
- To roll back one file: `cp backups/pre-redesign-2026-06-27/<slug>.html <slug>.html`
- To roll back everything: `git checkout backup/pre-redesign-2026-06-27 -- *.html` then redeploy

## NEXT STEP

After user approves ("YES"/"deploy"/"publish") → use `/skill:publish-article` (it runs `seo-maintenance.py --all`, rebuilds `index.html` via `node build-index.js` after you add the article to `articles-data.js`, commits, and deploys to Cloud Run).