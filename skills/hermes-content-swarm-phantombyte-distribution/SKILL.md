---
name: phantombyte-distribution
description: Optimize PhantomByte content for Google and AI search.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [SEO, GEO, Distribution, E-E-A-T, Content-Optimization]
---

# PhantomByte Distribution Optimization

Optimize PhantomByte content for maximum visibility in both traditional Google Search and generative/AI search engines (AI Overviews, Perplexity, ChatGPT Search, Gemini). Combines Google's Search Quality Rater Guidelines (E-E-A-T, YMYL, Page Quality), Google's AI Optimization Guide, and the GEO (Generative Engine Optimization) research paper (arXiv:2311.09735) into a single workflow.

This skill does NOT cover keyword research (use `keyword-research-seo` skill) or content writing (use `phantombyte-content-writing` skill). It focuses on the optimization and distribution layer after content is written.

## When to Use

- "Optimize this article for search"
- "Make this rank in AI search results"
- "Apply E-E-A-T to this page"
- "How do I get PhantomByte content into AI Overviews?"
- "Run GEO on this content"
- "Check if this page meets Google quality standards"
- "Build distribution for PhantomByte"

## Prerequisites

- A PhantomByte article or page to optimize (markdown or HTML)
- `pdftotext` (poppler-utils) installed for PDF reference extraction: `sudo apt install poppler-utils`
- `curl` for fetching reference URLs

## How to Run

1. Load this skill with `skill_view(name='phantombyte-distribution')`.
2. Read the target content with `read_file(path)`.
3. Follow the Procedure steps below, using `patch` to apply changes.

## Quick Reference

| Source | Key Concept | URL |
|--------|------------|-----|
| Google SQRG | E-E-A-T (Experience, Expertise, Authoritativeness, Trust) | https://services.google.com/fh/files/misc/hsw-sqrg.pdf |
| Google AI Guide | Foundational SEO + structured data + agentic readiness | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide |
| GEO Paper | Generative Engine Optimization (up to 40% visibility boost) | https://arxiv.org/abs/2311.09735 |

## Procedure

### Step 1: Audit for E-E-A-T Signals

Google's Search Quality Raters evaluate pages on four dimensions. Check the content for each:

- **Experience**: Does the author have first-hand or life experience with the topic? Add author bios, credentials, or "about the author" sections.
- **Expertise**: Is the content created by someone with topical knowledge? Cite sources, link to credentials.
- **Authoritativeness**: Is the website and author recognized as a go-to source? Build backlinks, get mentioned by other authoritative sites.
- **Trust**: Is the page accurate, honest, safe, and reliable? Include clear attribution, publication dates, revision history, and contact info.

For PhantomByte (AI R&D, Sovereign AI Stack, Cloud & Cyber Security), many topics are **YMYL (Your Money or Your Life)** — they can impact financial stability, health, safety, or societal well-being. YMYL content requires the highest E-E-A-T standards.

**Action**: For each article, add an author byline with credentials, a "Last Updated" date, and inline citations to authoritative sources (research papers, official docs, recognized experts).

### Step 2: Apply Google's AI Optimization Best Practices

From Google's AI Optimization Guide:

1. **Create valuable, non-commodity content**: Content that simply rehashes what others have said is "commodity content" and won't be cited by AI systems. Add original research, unique analysis, code examples, benchmarks, or personal experience that can't be found elsewhere.

2. **Build and maintain a clear technical structure**:
   - Use descriptive, unique `<title>` tags and meta descriptions
   - Implement proper heading hierarchy (H1 > H2 > H3)
   - Use structured data (Article, FAQ, HowTo, TechArticle schemas)
   - Ensure fast load times and mobile-friendly rendering
   - Use clean, semantic HTML

3. **Optimize local and business details** (if applicable): Include clear authorship, organization info, and contact details.

4. **What NOT to do** (mythbusting from Google):
   - Do NOT generate content solely for AI search — write for humans first
   - Do NOT try to "game" AI systems with hidden text or keyword stuffing
   - Do NOT create content that misrepresents expertise you don't have
   - Do NOT rely on AI-generated content without human review and fact-checking

**Action**: Add JSON-LD structured data (Article or TechArticle schema) to each page. Use the `terminal` tool to validate with Google's Rich Results Test or Schema.org validator.

### Step 3: Apply GEO (Generative Engine Optimization) Strategies

From the GEO paper (Aggarwal et al., KDD 2024), these strategies boost visibility in generative engine responses by up to 40%:

1. **Cite authoritative sources prominently**: Generative engines prefer content that explicitly references and links to trusted sources. Inline citations with named sources (e.g., "According to [source]...") increase the likelihood of being cited.

2. **Use structured, extractable formats**: Bullet points, numbered lists, tables, and clear section headers make it easier for LLMs to extract and cite your content. Dense paragraphs are less likely to be pulled into AI summaries.

3. **Include unique data and statistics**: Original numbers, benchmarks, or research findings are high-value for AI systems synthesizing answers. Content with unique data points is cited more frequently.

4. **Write self-contained, query-aligned sections**: Each section should answer a specific question or sub-topic completely. AI systems often pull a single section rather than the whole article. Structure content so individual sections are useful in isolation.

5. **Use clear, concise definitions upfront**: Lead each section with a clear definition or direct answer, then expand. Generative engines favor content that gets to the point.

6. **Domain-specific optimization**: The GEO paper found that strategy effectiveness varies by domain. For PhantomByte's focus areas (AI, cloud, cybersecurity), technical depth and authoritative citations matter more than for general topics.

**Action**: Restructure content to front-load key answers, add inline citations to authoritative sources, and break dense paragraphs into extractable list/table formats.

### Step 4: Verify and Measure

1. **Check structured data**: Use Google's Rich Results Test or Schema.org validator via `terminal`:
   ```
   curl -s "https://search.google.com/test/rich-results?url=YOUR_URL" | head -100
   ```

2. **Test AI visibility**: Ask a generative engine (Perplexity, ChatGPT, Gemini) a query your content should answer and check if it's cited. Use `web_search` or `browser_navigate` to test.

3. **Monitor Google Search Console**: Track impressions, clicks, and average position for target queries.

## Pitfalls

- **E-E-A-T is not a ranking factor directly** — it's a rater framework. But Google's algorithms are trained on rater data, so content that scores well on E-E-A-T tends to rank better.
- **GEO strategies are probabilistic** — no single change guarantees citation. Apply multiple strategies together.
- **Generative engines change fast** — what works today may change. Revisit optimization quarterly.
- **Don't over-optimize for AI at the expense of human readers** — Google's guide explicitly warns against this. Write for people first.
- **YMYL topics face higher scrutiny** — PhantomByte's AI/cloud/security content is YMYL. Every claim needs a citation.

## Verification

After applying all steps, run this check via `terminal`:

```bash
# Check structured data is valid
curl -s "https://validator.schema.org/validate?url=YOUR_URL" | python3 -m json.tool 2>/dev/null || echo "Use browser to check: https://validator.schema.org/"

# Verify page has: author, date, citations, clear headings
grep -c "author\|byline\|Last updated\|Last modified" article.md
grep -c "^##\|^###" article.md
grep -c "\[.*\](" article.md  # count of markdown links (citations)
```
