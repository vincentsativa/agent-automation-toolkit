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
Batch 3 - Hardware/ecosystem terms (chips, orchestration frameworks, infrastructure)

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
Write a full report to `~/keyword_research_[shortname].txt` containing:
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

## Pitfalls
- Google Trends has aggressive bot detection. Three patterns of failure:
  1. **429 (Too Many Requests)**, Cloudflare block. Retry with a different browser session or accept the first batch as sufficient.
  2. "Oops! Something went wrong" after page loads, the page rendered before the error, so the data is in the DOM. Use `browser_console` with expression `document.body.innerText` (or similar DOM selectors) to extract the table and chart data from the already-loaded page before the error overlay wipes it.
  3. Partial data only from first batch, Accept it. The first batch (core article terms) is the most important. Design batch 1 to contain the highest-value terms.
- Coined terms will show "Avg 0" on Trends, that's CORRECT, not an error. Zero competition is the opportunity.
- Always load batches in priority order: batch 1 = core article concepts (highest value), batch 2 = adjacent/benchmark terms, batch 3 = hardware/ecosystem terms. If you only get one batch, you got the most important one.
- Don't skip Tier 3 terms even though they show zero volume, they're the highest value.
- Always include a note about the "critical window" for first-mover terms. Without it, the user doesn't know the urgency.
- The Aikido "hallucinated dependencies" angle is a differentiator that academic coverage won't have, call it out.
- Internal linking suggestion: cross-link to related PhantomByte articles ("The Groundhog Day Problem" etc.) to build content clusters.

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
