# Coverage Gap Analysis, articles.phantom-byte.com

Use this technique when analyzing PhantomByte's existing content to find gap topics for article recommendations.

## Extraction Strategy, Browser Console (Primary)

**The site's DOM structure supports `querySelectorAll('article h3 a, article h3')` reliably.** This was verified on July 5, 2026 returning 240 results from the full archive page. The old workaround (snapshot-first, complex fallback chain) is no longer needed.

### Primary Method: Browser Console

Navigate to `https://articles.phantom-byte.com` and run:

```javascript
[...new Set(Array.from(document.querySelectorAll('article h3 a, article h2 a'))
  .map(el => el.textContent.trim())
  .filter(t => t.length > 10))]
```

This returns every article title on the page in one shot, deduplicated. The archive page renders ~120+ articles (the full catalog), so you get the complete coverage picture without pagination.

**Duplicate title pitfall:** Using `querySelectorAll('article h3, article h3 a')` or similar overlapping selectors returns each title TWICE because `h3 a` is nested inside `h3`. Always use the `a` element selector alone and wrap in a `Set` for deduplication. Verified July 15, 2026.

### Fallback: browser_navigate Snapshot

If the console approach fails (site DOM changes), parse the `browser_navigate` response directly. The accessibility snapshot contains article headings with author names and dates:

```
- article [ref=e7]
  - heading "The Article Title" [level=3]
  - StaticText "Vinny Barreca"
  - StaticText "June 7, 2026"
```

Extract titles and dates from the navigation output text.

### Dedup Analysis

After extracting titles, cross-reference each proposed theme/article idea against:
- The full title text (for exact/topical overlap)
- The publish date (to ensure the idea isn't just a rehash of something recently covered)
- The theme category of existing articles (check against the categorization table below)

Document the namediff for each proposed theme: "Why it's NOT an already-published article."

## Categorization

Group extracted titles into categories. Observed PhantomByte categories (as of July 2026):

| Category | What counts | Coverage |
|---|---|---|
| AI Infrastructure | GPUs, power, edge, inference, compute, chips, data centers, networking, storage | Heavy (54 articles) |
| AI Engineering | Agent orchestration, context windows, pipelines, debugging, production reliability, deployment | Heavy (21 articles) |
| AI Security | Prompt injection, supply chain, MCP, guardrails, red-teaming, agent vulnerabilities | Heavy (14 articles) |
| AI Industry | IPOs, pricing, layoffs, platform wars, cultural impact, company strategy | Medium (14 articles) |
| AI Policy | Regulation, EU AI Act, government strategy, open letters, safety frameworks | Medium (6 articles) |
| AI Agents | Agent architecture, frameworks, tool use | Growing (6 articles) |
| AI Privacy | Data collection, surveillance, consent, personal data | Light (2 articles) |
| AI & Society | Impact on jobs, education, daily life, psychology | Light (2 articles) |
| AI Ethics | Fairness, bias, values, moral considerations | Light (1 article) |
| AI Research | Papers, benchmarks, model comparisons, fine-tuning | Light (3 articles) |
| AI Collaboration | Multi-agent, human-agent collaboration | Light (1 article) |
| AI & Investing | AI in finance, markets | Light (1 article) |
| AI News | General news roundups | Light (1 article) |
| AI Strategy | Strategic planning | Light (1 article) |
| Cloud Infrastructure | Cloud-specific infra | Light (1 article) |
| Industry News | Industry-specific news | Light (1 article) |
| Industry Report | Reports and analysis | Light (1 article) |

Counts verified July 15, 2026 (All Notes: 131).

## Gap Identification

For each category, count articles. Any category with 0-2 articles is a candidate. Prioritize gaps that:
- Connect to today's news (timeliness)
- Fill an obvious hole in the site's stated focus ("educational content for AI engineers")
- Are actionable for the target reader (not just explanatory)
- Have research support (recent papers, real incidents) to anchor the angle

**Strong gap signals as of July 12, 2026:**
- **Distributed / Edge AI Inference**, zero coverage. All 54 AI Infrastructure articles focus on centralized deployment. LLMlet (P2P browser inference), Sunrun (residential compute), DeepSeek (custom chip), NVIDIA Vera (edge CPU) are all uncovered.
- **AI in Education / Cognitive Dependency**, zero coverage. Brown University 96% to 48% experiment is a major data point with no PhantomByte article.
- **AI Vendor Dependency as Financial Risk**, zero coverage. S&P downgrading Oracle citing OpenAI as a credit risk is a new category of risk.
- **Data Annotation / AI Labor Supply Chain**, one article (#120, Mechanical Turk shutdown). Still thin for the scope of the topic.
- **Physical AI / Robotics**, zero coverage. China's Orca world model learning robotics from video alone is uncovered.
- **AI Data Center Siting / Community Opposition**, zero coverage. Oracle's $43B Michigan data center fight, grassroots opposition spreading.

## Writing the Gap Rationale

For each unwritten theme, include:

```
Theme N: "PROVOCATIVE ARTICLE TITLE"

Angle: 3-4 sentence pitch explaining the article concept, angle, and why it matters now.

Supporting sources:
- Headline (Source)
- Headline (Source)

Why it hasn't been covered: Cite the closest existing PhantomByte article (title + date) and explain how this angle is different.
```

## When to Use

This is Step 3 of the editorial brief workflow, after fetching headlines and identifying themes, use gap analysis to rank article recommendations.
