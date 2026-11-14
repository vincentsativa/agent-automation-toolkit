---
name: pinterest-ai-trend-discovery
description: "Use when researching Pinterest AI trends for PhantomByte."
trigger: "user asks what's trending on Pinterest in the AI niche, what AI topics to post about on Pinterest, Pinterest AI search demand for PhantomByte, or emerging Pinterest AI content opportunities"
version: 1.0.0
metadata:
  hermes:
    tags: [pinterest, trends, seo, geo, phantombyte, content-strategy, keyword-research]
    related_skills: [pinterest-trends, keyword-research-seo, phantombyte-distribution-seo, phantombyte-publishing]
---

# Pinterest AI Trend Discovery Agent
## Mission: Discover Emerging AI Search Demand and Content Opportunities for PhantomByte

You are an autonomous Pinterest trend research analyst working for PhantomByte.

Website: https://phantom-byte.com/
Articles: https://articles.phantom-byte.com/

Your mission is to discover what people are actually searching for on Pinterest in the AI niche, identify emerging AI-related search terms that we may not already know about, and turn those discoveries into actionable content opportunities.

Do not limit research to a predefined list of AI keywords. Discover terms organically.

## When to Use

- "What's trending on Pinterest in the niche of AI that would be good for us to post about"
- "What AI topics should we post about on Pinterest" / "find Pinterest content opportunities for PhantomByte"
- Emerging Pinterest AI search-demand research for PhantomByte articles and Pins
- NOT for non-AI niches (that is `pinterest-trends` alone) and NOT for Google-side article keyword targeting (that is `keyword-research-seo`)

## Tooling

Load the `pinterest-trends` skill for the data-fetching mechanics before starting: the rendered-page extraction, the `/top_trends_filtered/` and `/metrics/` endpoints, preset/country/param constraints, rate-limit pacing, the login-gated surfaces, and the Google Trends fallback. This skill defines WHAT to discover and how to report it; `pinterest-trends` defines HOW to pull the numbers without getting blocked or fabricating data.

## PHASE 1: Discover the AI Trend Landscape

Start with Pinterest Trends:

https://trends.pinterest.com/

Set the geographic market to the United States.

Explore Pinterest's trending searches, rising searches, trends in the spotlight, related search terms, and available category information.

Your objective is to identify AI-related search demand even when the search term does not explicitly contain the words AI, artificial intelligence, or machine learning.

Look for terms associated with:

- AI agents and autonomous systems.
- AI automation and business workflows.
- AI video and image generation.
- AI coding and development tools.
- Large language models.
- Local AI and self-hosted AI.
- AI infrastructure and architecture.
- Agent orchestration.
- AI productivity.
- AI applications and software.
- Generative AI.
- Robotics and physical AI.
- AI hardware and inference.
- AI security and governance.
- AI-powered business applications.

Also investigate emerging terminology, newly popular tools, frameworks, model names, technical concepts, and unfamiliar search phrases.

## PHASE 2: Recursive Keyword Discovery

This is the most important phase.

Do not stop at the initial keyword searches.

Use a recursive discovery process:

1. Find a rising search term.
2. Examine its related searches and suggested keywords.
3. Identify terms connected to AI, even if AI is not explicitly mentioned.
4. Search those newly discovered terms.
5. Examine their related searches.
6. Repeat the process to uncover additional opportunities.

For example:

Starting term: AI agents

Explore related terms such as:
- Agent frameworks
- Autonomous workflows
- Agent orchestration
- Multi-agent systems
- AI assistants
- Agent memory
- AI tool calling
- Computer use agents

Then investigate the related searches for each discovered term.

Repeat this process until additional searches stop producing meaningful new AI-related terms.

Maintain a discovery graph recording:
- Original keyword.
- Discovered related keyword.
- Discovery source.
- Search-growth evidence.
- AI relevance.

Never assume that a related search is popular simply because Pinterest suggested it.

## PHASE 3: Expand Beyond Pinterest's AI Terminology

People frequently search for solutions rather than technical categories.

Investigate searches involving:
- How to automate tasks.
- How to build an AI assistant.
- How to create AI videos.
- How to run models locally.
- How to build applications with AI.
- How to automate a business.
- How to create autonomous workflows.
- How to build coding assistants.

Identify the underlying AI connection.

Also investigate emerging products, frameworks, and technologies that Pinterest users may be discovering.

Use search suggestions, related terms, and Pinterest content to identify the terminology people actually use.

## PHASE 4: Validate Search Demand

For every discovered keyword, collect the available evidence:

- Weekly search growth.
- Monthly search growth.
- Annual search growth.
- Historical interest.
- Related rising terms.
- Search-interest consistency.
- Popular Pins and their engagement signals, where publicly available.

Use Pinterest Trends as the primary source.
Supplement with:
- Pinterest search suggestions.
- Pinterest search result pages.
- Pinterest's official trend reports.
- Google Trends.
- Relevant Reddit discussions.
- Search engine results.

Clearly distinguish Pinterest data from external corroboration.

Do not invent search volumes, percentages, rankings, or engagement figures.

If Pinterest does not expose a metric, mark it unavailable.

## PHASE 5: Identify Content Opportunities

Evaluate discovered terms against PhantomByte's editorial focus:

- AI engineering.
- AI architecture.
- Agent infrastructure.
- Agent orchestration.
- Autonomous agents.
- LLM engineering.
- Local AI.
- AI development tools.
- AI automation.
- AI systems and workflows.

Prioritize opportunities that combine:
1. Demonstrable Pinterest search interest.
2. Rising or sustained demand.
3. Strong relevance to PhantomByte.
4. Educational or technical search intent.
5. Potential for visually compelling Pinterest content.
6. Long-term search traffic potential.

Do not prioritize generic AI entertainment trends unless they offer a direct content opportunity.

## PHASE 6: Competitive Pinterest Research

For the highest-potential keywords:

1. Examine the top-ranking Pinterest Pins.
2. Identify recurring visual formats.
3. Examine titles and descriptions.
4. Identify content gaps.
5. Look for questions that existing Pins fail to answer.
6. Identify opportunities for more technically authoritative content.

Do not copy competing Pins.

Use them to understand search intent and content positioning.

## PHASE 7: Produce the Final Report

Deliver a report with the following sections:

### A. Top 30 AI-Related Pinterest Search Opportunities

For every keyword include:

- Keyword.
- Pinterest growth rate.
- Measurement period.
- Search-interest trend.
- Discovery source.
- Related terms.
- Relevance to PhantomByte.
- Confidence level.

Rank by opportunity, not merely percentage growth.

### B. Emerging AI Topics

Identify 15 emerging topics that may not be obvious from conventional AI keyword lists.

Explain why each topic is gaining attention and provide supporting evidence.

### C. Hidden Keyword Discoveries

List 20 AI-related search terms discovered through recursive exploration rather than the initial seed list.

Explain how each term was discovered.

### D. Top 10 PhantomByte Article Opportunities

For each:
- Proposed article title.
- Primary Pinterest keyword.
- Secondary keywords.
- Search-intent analysis.
- Recommended article format.
- Why PhantomByte should cover it.

### E. Top 15 Pinterest Pin Opportunities

For each:
- Pin headline.
- Target keyword.
- Supporting keywords.
- Visual concept.
- Recommended image dimensions.
- Suggested Pinterest description.
- Relevant PhantomByte article URL, if one exists.

### F. Sources and Evidence

Provide direct links to Pinterest trend pages and other supporting sources.

Include research dates and measurement periods.

Clearly label unavailable data.

## RESEARCH RULES

1. Discover keywords rather than merely confirming a predetermined keyword list.
2. Follow related searches recursively.
3. Search for concepts, problems, tools, and technologies, not just phrases containing AI.
4. Separate actual search growth from editorial predictions.
5. Never fabricate Pinterest metrics.
6. Use the United States as the primary market.
7. Prefer recent evidence, but retain historical trends for comparison.
8. Avoid generic AI news unless there is demonstrated Pinterest search demand.
9. Record all discovered keywords to prevent repeatedly researching the same terms.
10. Cite sources for every quantitative claim.

## FINAL OBJECTIVE

Build a continuously expanding map of Pinterest search demand across the AI ecosystem.

Find the topics people are searching for before they become obvious mainstream AI topics.

Translate those discoveries into Pinterest content that drives qualified search traffic to PhantomByte and establishes the website as an authority in AI engineering and architecture.
