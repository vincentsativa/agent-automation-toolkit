---
name: keyword-research-seo
description: Do keyword research for PhantomByte articles using Google Trends, identify high, medium, and low competition targets with search volumes, trends, and strategic recommendations. Email report to Vinny.
trigger: "vinny asks for keyword research, SEO research, keyword targets, what keywords to target for an article"
---

# Keyword Research & SEO Workflow (PhantomByte)

## Trigger Conditions
- Vinny says "do keyword research" or "keyword targets" for an article
- Vinny asks "what keywords should I target" or similar
- Any request to analyze SEO/search terms for a written piece

## Email Target
- **To:** hello@phantom-byte.com
- **Subject:** "Keyword Research: [Article Title]"

## Prerequisite Skill

Before starting research, load the `phantombyte-distribution-seo` skill with `skill_view(name='phantombyte-distribution-seo')`. Its GEO and E-E-A-T framework informs the keyword strategy: high-value targets are terms that signal Experience, Expertise, Authoritativeness, and Trust, and the report should recommend content structures (quotations, statistics, citations) that boost AI search visibility.

## Research Steps

### 1. Extract concepts from available material
**If a finished article exists:** Read the full article text. Extract core concepts, unique terms, and any brand-new phrases the author coined. These coined terms are the highest-value targets (zero competition, first-mover advantage).

**If only a topic/title/outline concept exists (no full article yet):** Extract keywords from:
- The working title and subtitle
- The proposed angle or "Why" statement
- Likely subject matter, tools, frameworks, or brands the tutorial will cover
- Any coined or branded phrases in the concept description

In topic/outline mode, expect fewer concrete coined terms upfront. Run the research anyway, the Trends data will reveal which adjacent terms have traction and may reshape the final title or H2 choices.

### 2. Google Trends analysis
Navigate to `https://trends.google.com/trends/explore` and run queries in batches of up to 5 terms per URL, targeting US, Past 12 months, Web Search.

Design your own batches of up to 5 terms per URL based on the article's actual keywords. Group by theme:

Batch 1 - Core article concepts (the big umbrella terms, unique coined terms, paper names)
Batch 2 - Adjacent/benchmark terms (benchmarks cited, vendor names, frameworks)
Batch 3 - Niche/defense/ecosystem terms (the specific technical terms from the article: defense strategies, technical mechanisms, uncommon frameworks, governance terms, OIDC/SLSA jargon). Not limited to hardware, whatever is specific to this article's technical depth.

EXAMPLE for an inference-architecture article:
- Batch 1: `test-time scaling`, `best-of-N sampling`, `LaneRoPE`, `inference-time compute`, `AI inference architecture`
- Batch 2: `Mixture-of-Experts agentic coding`, `ITBench-AA`, `agentic AI benchmark`, `collaborative inference`, `k8s SRE AI`
- Batch 3: `NVIDIA Dynamo`, `AI factory`, `Laguna model`, `NVIDIA GB300`, `parallel reasoning AI`

### 3. For each Trends result, capture:
- The "Average" value shown in the table (higher = more volume)
- The trend direction (rising, flat, seasonal, spiky)
- The relative position vs other terms

### 4. Classify into three tiers:

**TIER 1: HIGH COMPETITION (Avg 25+ on Trends)**
- Umbrella terms with strong volume
- Lots of entrenched players (enterprise vendors, major pubs)
- Use sparingly, primarily as metadata/seo umbrella

**TIER 2: MEDIUM COMPETITION (Avg 10-25 on Trends)**
- Good volume, growing interest
- Fewer entrenched players
- PRIMARY TARGETS for article, optimize title, H1, URL

**TIER 3: LOW/NO COMPETITION (Avg 0-5 on Trends)**
- Brand new or coined terms
- Zero SERP competition
- CRITICAL TARGETS, first-mover advantage, limited window
- Typically: paper names, coined phrases, benchmark names

### 5. Identify the unique angle
What does THIS article have that competitors don't? (e.g., security hook vs academic hook, vendor angle vs engineering angle). This is the differentiator for SEO strategy.

### 6. Identify the critical window
New papers/benchmarks/terms typically get picked up by major pubs (VentureBeat, Ars Technica, Wired, The Register) within 4-6 weeks. State the window explicitly.

### 7. Compile the report
Write a full report to the user's home directory (`~` on Linux, `$HOME` on Windows Msys) named `keyword_research_[shortname].txt` containing:
- Methodology note
- Tier 1 breakdown (terms, volume, competition, use)
- Tier 2 breakdown
- Tier 3 breakdown
- Strategic recommendations (primary, secondary, tertiary)
- Additional notes (backlink opps, internal linking, timing)

### 8. Email it
Use the email-sender skill to send to hello@phantom-byte.com with:
- Subject: "Keyword Research: [Article Title]"
- Body: Quick summary with primary targets, critical window, unique angle
- Attachment: The full report file

## Close the Browser (MANDATORY, do not skip)
After all Trends batches are done, close the automation Chrome and VERIFY it is actually gone. Run from `terminal`:

```bash
powershell -ExecutionPolicy Bypass -File "C:/Users/<user>/kill_chromekw.ps1"
sleep 3; curl -s --max-time 3 http://127.0.0.1:9223/json/version || echo "port 9223 dead"
```

The script kills every chrome-kw PID and prints `remaining: N`. Success requires BOTH: `remaining: 0` in the script output AND `port 9223 dead` from the curl. One kill pass is NOT enough when multiple named `browser_exec` sessions were used (kw_b2/kw_b3 fresh sessions spawn extra Chrome children). Session proof (Sep 3 2026): a single kill left Chrome running and Vinny caught it. Always run the script and verify both conditions before reporting done.

## Pitfalls
- **Windows path mismatch when emailing the report (CRITICAL):** The email-sender skill's Python script uses Windows Python, which does NOT understand MSYS paths (`/c/Users/...`). When you write the report file with `write_file` (which accepts MSYS paths fine), the attachment path you pass to the email script must be a raw Windows path like `r'C:\Users\<user>\keyword_research_...txt'`. If you pass an MSYS path, `os.path.exists()` returns False inside the script and the email sends without the attachment. Always construct the attachment path as a raw Windows string or use `os.path.join(os.path.expanduser('~'), ...)` which resolves to the correct Windows path.
- Google Trends has aggressive bot detection. Five patterns of failure with solutions:
  1. **429 (Too Many Requests)**, Cloudflare block. **BEST WORKAROUND:** Use direct URL-param navigation (`https://trends.google.com/trends/explore?q=term1,term2,term3,term4,term5&geo=US`) instead of navigating to the base page and typing into the searchbox. The URL-param approach bypasses the bot detection entirely on most retries. If that also gets 429'd, retry once, a fresh session often clears it.
  2. **"Oops! Something went wrong"** after page loads, the page rendered before the error, so the data is already in the DOM. Use `browser_console` with expression `document.body.innerText` (or similar DOM selectors) to extract the table and chart data from the already-loaded page before the error overlay wipes it.
  3. **Partial data only from first batch**, Accept it. The first batch (core article terms) is the most important. Design batch 1 to contain the highest-value terms.
  4. **URL-param navigation succeeds but snapshot shows empty/partial**, the data is there in the DOM even if the accessibility snapshot doesn't show it. Always call `browser_console(expression='document.body.innerText.substring(0, 10000)')` immediately after a successful URL-param load to extract the Trends table data.
  5. **Date param in URL gets rejected**, the browser can't parse date-override params like `&date=today%2012-m`. Omit the date/time params entirely and just use `&geo=US` (or omit geo too). The defaults (Past 12 months, Web Search, Worldwide) are usually correct for Vinny's research anyway.
- Coined terms will show "Avg 0" on Trends, that's CORRECT, not an error. Zero competition is the opportunity.
- **"Insufficient data" message (new pattern):** Some coined/niche terms show "Hmm, your search doesn't have enough data to show here" instead of Avg 0. This is the SAME signal as Avg 0, zero competition, first-mover opportunity. Do not skip these terms. They appear in the Trends UI as a warning banner rather than a table row. Capture them in Tier 3 as coined/insufficient-data terms with a note about the first-mover window.
- Always load batches in priority order: batch 1 = core article concepts (highest value), batch 2 = adjacent/benchmark terms, batch 3 = hardware/ecosystem terms. If you only get one batch, you got the most important one.
- Don't skip Tier 3 terms even though they show zero volume, they're the highest value.
- Always include a note about the "critical window" for first-mover terms. Without it, the user doesn't know the urgency.
- The unique angle must be article-specific. Identify what THIS article has that competitors don't (community angle vs industry angle, security hook vs academic hook, vendor angle vs engineering angle). Do not reuse stale differentiators from past sessions.
- Internal linking suggestion: cross-link to related PhantomByte articles to build content clusters. Check the article's own citations and references for natural link targets.
- On-page GEO checklist (mandatory additions to the keyword report and outline integration, per the September 2026 strategy update, Vinny writes articles but had been omitting these, so the report must call them out explicitly):
  1. 3-8 EXTERNAL citations to primary sources (vendor announcements, papers/arXiv, official docs, government data). Descriptive anchor text, never keyword-stuffed. Cite at the point of claim, not a footer link dump. This is the KDD 2024 "Cite Sources" method (+27% AI visibility).
  2. 3-5 INTERNAL links to related PhantomByte articles with real anchor text. Fixes the orphan-page problem (Sep 2026 audit found articles had ZERO internal article links, all 189 pages only reachable via sitemap).
  3. At least one blockquote from an authoritative source and at least one named statistic (the two best GEO methods).
  4. Quotable self-contained first sentences per paragraph; a table or list where content supports it.
  5. Include a "GEO On-Page Checklist" section in every keyword report listing these 5 items so the writer sees them at write time, not after publication.
- Retrofit Mode (existing-article audit): When Vinny says "run the audit" or asks which existing articles need fixes, crawl all sitemap URLs and score each article on: external citation count (target 3-8), internal article link count (target 3-5), blockquote presence, statistic presence, table/list presence. Rank worst-first and report which articles to retrofit in priority order. Baseline finding (Sep 6, 2026 audit): sample articles averaged 1 external link (self-referential only), 0 internal article links, 0 blockquotes, 0 tables.
- See `references/example_report_data_center_war.txt` for a full worked example of a keyword research report with all sections (tier breakdown, critical window, backlink opportunities, recommended URL/meta).
- See `references/synthetic_data_paradox_trends_data.txt` for a real-world Trends data capture from Article 100 (synthetic data / model collapse / ICML 2026 paper). Useful as a comparison baseline for future AI-training-infrastructure keyword research.
- See `references/report_template_750_rack.txt` for a full report template with all sections (recommended URL, meta description, backlink opportunities, internal linking, tags). Use this as the canonical structure for all future keyword research reports.

## Integration With Outlines
When keyword research is requested alongside an article outline (not just for a finished article), the keyword research and outline are **interleaved outputs**:

1. Run keyword research first. Use the data to inform the outline.
2. Embed the keyword tier data directly into the outline document so the writer has strategic targets without cross-referencing a separate file.
3. In the outline, explicitly map:
   - **Primary targets** → title, H1, URL, first 100 words, meta description
   - **Secondary targets** → H2 headings, body content, semantic SEO
   - **Tertiary targets** → tags, image alt text, long-tail anchors
4. Include a `Keyword Research Summary` block near the top of the outline with the 3-tier breakdown.
5. Add an `SEO Integration Map` in the writer notes listing exactly where each target term should appear.

This prevents the common failure mode where keyword research gets emailed as a separate file and the outline writer never sees it.

### Standalone Report Format (when NOT paired with an outline)
If producing a standalone keyword research file, structure it like this:

```
PRIMARY TARGETS (optimize title, H1, URL, first 100 words, meta description):
  1. [term], [volume], [competition note], [why]
  2. [term], ...

SECONDARY (H2s, body content, semantic SEO):
  3. [term], ...
  4. [term], ...

TERTIARY / FUTURE (tags, image alt text, long-tail):
  5. [term], ...
```
