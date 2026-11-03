---
name: phantombyte-distribution-seo
description: Optimize content for AI search and generative engines.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [SEO, GEO, E-E-A-T, Content, Distribution, PhantomByte]
---

# PhantomByte Distribution: SEO and GEO for AI Search

A practical guide for PhantomByte content creators to optimize articles for both traditional search engines and generative AI engines (AI Overviews, Perplexity, Bing Chat, etc.). Combines Google's official Search Quality Rater Guidelines (E-E-A-T), Google's AI Optimization Guide, and the academic GEO (Generative Engine Optimization) framework from the KDD 2024 paper.

This skill does NOT cover paid ads, social media distribution, email marketing, or link-building campaigns. It focuses purely on on-page content optimization for organic discovery through search and AI engines.

## When to Use

- Writing a PhantomByte article that is not final yet, or auditing existing content for a report to Vinny. On his finished prose this skill scores and reports only; see the HARD RULE above.
- Auditing existing content for AI search visibility.
- Planning a content strategy that targets both traditional and generative search.
- The user asks "how do we get found in AI search" or "optimize for Perplexity/AI Overviews."
- The user asks about E-E-A-T, GEO, or Google's quality rater guidelines.

## HARD RULE: WRITE-TIME ONLY. NEVER EDIT VINNY'S FINISHED ARTICLE (standing order, Oct 15 2026)

Vinny's order: no agent tells him to change an article he has already written. Any output that does is a failed run.

- Every edit step in this skill (add an anecdote, add a quotation, add statistics, add citations, tighten fluency, define terms, restructure headings) is an instruction to the WRITER before a draft exists. It applies to a piece still being written at Vinny's request.
- On a finished or published article, every step below is a SCORING CRITERION, not an edit order. Measure it, score it, and report the result to Vinny. Do not propose prose changes, do not phrase one as optional or deferential ("say the word" is still an instruction to edit), do not call his wording a defect, a miss, or an omission, and never touch the text with `patch` or `write_file`.
- Metadata is the only thing an agent may recommend for an existing article: title, H1, URL slug, meta description, tags, and link targets, and only when Vinny asks.
- When a finding conflicts with his prose, the prose wins. State the reading, state the tradeoff in one line, and leave the decision to him.
- Cite only rules that exist in the loaded skills. Never invent a policy, a ban, or a "golden rule" to justify a recommendation. A fabricated rule is a second failure on top of the first.

## Prerequisites

- A PhantomByte article in markdown or text format.
- Familiarity with the article's topic and target audience.
- No special API keys or tools required beyond standard Hermes tools.

## How to Run

Load this skill with `skill_view(name='phantombyte-distribution-seo')`, then apply the Procedure steps to any article using `read_file`, `patch`, and `write_file` tools.

## Quick Reference

| Concept | Source | Key Takeaway |
|---|---|---|
| E-E-A-T | Google Rater Guidelines | Experience, Expertise, Authoritativeness, Trustworthiness |
| YMYL | Google Rater Guidelines | Your Money or Your Life topics need highest quality standards |
| Non-commodity content | Google AI Guide | Unique POV, first-hand experience, not recycled common knowledge |
| RAG + Query Fan-out | Google AI Guide | AI search uses retrieval-augmented generation and multi-query expansion |
| GEO methods | KDD 2024 Paper | 9 optimization strategies; citations, quotations, statistics best |
| Position-adjusted visibility | KDD 2024 Paper | Earlier citations in AI responses get more weight |
| No special markup needed | Google AI Guide | No llms.txt, no chunking, no special schema required for AI search |

## Procedure

### Phase 1: Assess the Article Against E-E-A-T (write-time edits, or scoring criteria on an existing article per the HARD RULE)

1. Read the article with `read_file`.
2. Check for **Experience**: Does the article reflect first-hand or direct experience? If not, add a personal anecdote, case study, or real-world example.
3. Check for **Expertise**: Is the author's expertise clear? Add an author bio or byline that establishes credentials.
4. Check for **Authoritativeness**: Are external authoritative sources cited? Add links to reputable references.
5. Check for **Trustworthiness**: Is the information accurate, honest, and safe? Remove any exaggerated claims, and verify all facts.
6. If the topic is YMYL (health, finance, safety, legal), apply the highest quality standards: cite peer-reviewed sources, government data, or official guidelines.

### Phase 2: Apply GEO Methods (from the KDD 2024 paper) (write-time only; on an existing article these are scoring criteria)

The GEO paper found these methods boost visibility by up to 40% in generative engine responses. Apply them in priority order:

1. **Quotation Addition** (best performer, +40% visibility): Add direct quotations from authoritative sources. Use blockquote formatting.
2. **Statistics Addition** (+30%): Replace qualitative claims with quantitative data. "Many users prefer X" becomes "67% of users prefer X (Source, 2024)."
3. **Cite Sources** (+27%): Add inline citations with links to credible external sources. Every factual claim should have a citation.
4. **Fluency Optimization** (+27%): Improve sentence flow, readability, and natural language. Read the article aloud and fix awkward phrasing.
5. **Technical Terms** (+17%): Include relevant technical terminology where appropriate, but define terms on first use.
6. **Authoritative Tone** (+16%): Write with confident, authoritative language. Avoid hedging ("might", "could possibly") unless uncertainty is genuine.
7. **Easy-to-Understand** (+13%): Simplify complex sentences. Aim for Flesch reading ease appropriate to the audience.
8. **Unique Words**: Add distinctive vocabulary that sets the article apart from competitors.
9. **Keyword Stuffing** (DO NOT USE): The paper found this hurts visibility. Google's guide also warns against it.

### Phase 3: Structure for AI Search (from Google's AI Optimization Guide)

1. **Write non-commodity content**: Ensure the article provides a unique point of view that cannot be easily replicated by an LLM. First-hand reviews, original research, and expert analysis outperform generic listicles.
2. **Organize with clear headings**: Use hierarchical headings (H1, H2, H3) that create a logical content structure. AI systems use heading structure to understand page organization.
3. **Add high-quality images and video**: Include relevant media with descriptive alt text. AI Overviews can surface images alongside text.
4. **Ensure crawlability**: Verify the article is not blocked by robots.txt or noindex tags. Use Google Search Console to check indexing status.
5. **Reduce duplicate content**: If the article overlaps with other PhantomByte pieces, consolidate or differentiate them.
6. **Provide good page experience**: Fast loading, mobile-friendly, clear distinction between main content and navigation.

### Phase 4: Optimize for Citation Visibility

Generative engines cite sources inline. To maximize the chance your article gets cited prominently:

1. **Front-load key information**: Put the most important findings, statistics, and conclusions in the first third of the article. AI responses tend to cite sources that appear early in the response.
2. **Use clear, quotable sentences**: Write standalone sentences that make sense when extracted from context. Each paragraph's first sentence should be a strong, self-contained claim.
3. **Include data in structured formats**: Tables, lists, and bullet points are more likely to be extracted and cited by AI systems.
4. **Define a clear thesis**: The article should have one primary argument or finding that can be summarized in a single sentence. AI systems favor sources with a clear, unique contribution.

### Phase 5: Avoid Anti-Patterns (from Google's Mythbusting)

Google explicitly states these do NOT help and may hurt:

- **Do NOT create llms.txt files** for Google Search. Google ignores them entirely.
- **Do NOT chunk content** into tiny pieces for AI. Google's systems understand multi-topic pages.
- **Do NOT rewrite content** specifically for AI systems. Write for humans.
- **Do NOT seek inauthentic mentions** across the web. Google's spam systems detect this.
- **Do NOT overfocus on structured data** for AI search. Standard schema is fine but not required.
- **Do NOT keyword stuff**. The GEO paper confirms this reduces visibility.

## Pitfalls

- GEO methods vary in effectiveness by domain. Statistics and quotations work best for informational content; authoritative tone works better for opinion/analysis pieces.
- Google's AI Overviews and Perplexity use different underlying models. Optimizing for one may not fully transfer to the other, but the principles (E-E-A-T, citations, statistics) are broadly effective.
- The GEO paper's results are based on GPT-3.5-turbo as the generative engine. Results may differ with newer models (GPT-4, Claude, Gemini).
- E-E-A-T is not a direct ranking factor but a framework raters use. Google's algorithms approximate these signals through other metrics.
- Visibility in AI search does not guarantee click-throughs. Users may get their answer from the AI response without visiting your site. Optimize for both citation AND compelling reason to click.

## Verification

After applying the procedure, run a final check: read the article and confirm it has (1) a unique, non-commodity thesis, (2) at least one statistic or quotation from an authoritative source, (3) clear hierarchical headings, and (4) no keyword stuffing or AI-targeted gimmicks.
