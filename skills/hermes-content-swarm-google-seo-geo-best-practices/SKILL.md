---
name: google-seo-geo-best-practices
description: Use when Google SEO/GEO matters for content authority.
trigger: "Vinny asks to write/outline content for authority, optimize for Google SEO or GEO, follow Google best practices, or make content rank in search and AI search"
---

# Google SEO/GEO Best Practices (Google Search Central)

Distilled from Google's official Search Central documentation (developers.google.com/search). This is the authority-first framework Vinny wants applied to ALL PhantomByte content. It supersedes keyword-first thinking: content is planned and written to demonstrate authority and follow Google best practices, not reverse-engineered from keyword volume.

**Core belief:** We earn authority by being a trusted, first-hand source on AI and agentic systems. Google rewards people-first, non-commodity content with strong E-E-A-T. Keywords support the content; they never drive it.

## When to Use

- Writing or outlining any PhantomByte article (tutorial, analysis, engineering piece)
- "Follow Google best practices" / "make this authoritative" / "SEO/GEO"
- Optimizing an article for Google Search or generative AI search (AI Overviews, AI Mode)
- Choosing what to write next, prioritize authority-building over keyword-chasing
- Any skill or workflow where Google SEO/GEO matters (see Integration section)

## Primary Sources (learned from official docs)

- **Optimizing for generative AI features on Google Search**, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (updated 2026-07-10)
- **Creating helpful, reliable, people-first content**, https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- **Google's guidance on using generative AI content**, https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
- **Guide to Google Search ranking systems**, https://developers.google.com/search/docs/appearance/helpful-content-system
- **Understanding structured data**, https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
- **Article structured data**, https://developers.google.com/search/docs/appearance/structured-data/article
- **Title links**, https://developers.google.com/search/docs/appearance/title-link
- **Meta descriptions**, https://developers.google.com/search/docs/appearance/snippet

## The Authority Framework (decision order)

When planning ANY content, decide in this order, keywords never come first:

1. **Who is this for and why?** Real audience with a real goal. People-first, not search-first.
2. **What unique value do we add that no one else can?** First-hand experience, original analysis, proprietary data, real-world engineering from the PhantomByte stack. Non-commodity content.
3. **How is it made?** Transparent about process and expertise. Byline, credentials, citations.
4. **What technical structure serves it?** Semantic HTML, clean headings, structured data, fast/mobile-friendly.
5. **Only then: which keywords support it?** Use keyword-research-seo skill to surface supporting terms AFTER the angle is set.

## The 5 Non-Negotiables (from Google's own docs)

### 1. Create non-commodity, people-first content
- **Non-commodity** = a unique expert/first-hand take that goes beyond common knowledge. "7 tips for beginners" is commodity. "What our sovereign AI stack actually taught us about agent reliability in production" is not.
- Google: "Content that simply rehashes what others have said is commodity content and won't be cited by AI systems." Add original research, unique analysis, real code, benchmarks, or personal experience that can't be found elsewhere.
- A first-hand review (unique perspective based on personal experience) beats a summary (restates existing info). **Write from what you know and have built.**

### 2. Demonstrate E-E-A-T (Experience, Expertise, Authoritativeness, Trust)
- Of the four, **trust is most important**. The others contribute to trust.
- **Who**: clear authorship. Bylines that link to an author page/about page. Vinny Barreca = systems builder, built mass emailer 2004 (Shift44 seed), co-built Shift44 ($40M exit). This is the authority story, surface it. NEVER call him "founder", he is a systems builder / operator.
- **How**: transparent about how content was made, including where automation/AI was used. Explain the process.
- **Why**: content exists primarily to help people, not to manipulate rankings.
- **YMYL**: PhantomByte's AI/cloud/security topics are "Your Money or Your Life", they can impact financial stability and societal well-being. YMYL requires the HIGHEST E-E-A-T: every claim needs a citation, clear sourcing, author expertise.

### 3. Apply foundational SEO to generative AI search
- Google's AI features (AI Overviews, AI Mode) are grounded in the SAME core ranking systems. So SEO still matters, it's the same game.
- RAG/grounding: Google retrieves indexed pages, then surfaces the supporting page. Being indexed, crawlable, and high-quality IS the GEO play.
- **"AEO"/"GEO" as separate disciplines are marketing terms.** From Google's perspective, optimizing for generative AI search is just SEO. Be wary of third-party AEO/GEO tools claiming "internal" knowledge.
- **Ignore these myths (Google explicitly says you DON'T need them):**
  - llms.txt and other "special" AI markup, Google ignores them (fine for other engines, no SEO harm/benefit)
  - "Chunking" content for AI, Google understands nuance across a page
  - Rewriting just for AI / hunting long-tail keyword variants, AI understands synonyms
  - Seeking inauthentic "mentions"
  - Overfocusing on structured data, helpful but NOT required for AI search

### 4. Focus on technical clarity
- **Search technical requirements**: page must be indexed and eligible to show with a snippet.
- **Crawlability**: content must be publicly crawlable (generative AI models use crawlable content).
- **Semantic HTML** helps screen readers and all users; don't obsess over perfect code, but use headings properly.
- **Page experience**: works across devices, low latency, clear main content.
- **Reduce duplicate content**.
- **Structured data** (JSON-LD): still worth doing, it enables rich results and helps understanding, even though not required for AI search. Validate with Rich Results Test.
- **Verify site in Search Console** and monitor the **Generative AI performance report** to see AI visibility.

### 5. Never game the system
- Don't create scaled/automated content without added value (violates scaled content abuse spam policy).
- Don't create content primarily to manipulate rankings or AI responses (spam).
- Don't write to a specific word count (no preferred length), don't keyword-stuff titles, don't fake freshness by changing dates.
- AI-assisted content is fine IF it meets Search Essentials + spam policies: accurate, quality, relevant, and transparent about automation.

## The Self-Assessment Checklist (ask before shipping)

**Content & quality:**
- Does it provide original information, reporting, research, or analysis?
- Does it provide a substantial, complete, or comprehensive description of the topic?
- Does it provide insightful analysis beyond the obvious?
- Does it avoid just copying/rewriting sources, adding substantial original value?
- Is the title/heading a descriptive, helpful summary (not exaggerated/shocking)?
- Is this a page you'd bookmark, share, or recommend? Would it appear in a magazine or book?

**Expertise:**
- Does it make you want to trust it (clear sourcing, author background, About page)?
- Written/reviewed by a demonstrable expert or enthusiast?
- Any easily-verified factual errors? (Must be none, accuracy is non-negotiable.)

**People-first (yes = good):**
- Would an existing audience find it useful directly?
- Does it show first-hand expertise and depth of knowledge?
- Does the reader leave having learned enough to achieve their goal?

**Search-first warning signs (yes = bad):**
- Made primarily to attract search traffic?
- Lots of content on many topics hoping some performs?
- Extensive automation without added value?
- Mainly summarizing others without adding value?
- Writing to a word count? Changing dates to fake freshness?

## Technical Checklist (per article/page)

- **Title (`<title>`)**: descriptive, concise, unique per page. No keyword stuffing, no boilerplate. Brand concisely. This is the #1 thing users see in results.
- **Meta description**: accurate, compelling summary; relevant to the content. (Write AFTER content so it reflects the real page.)
- **Heading hierarchy**: one H1, logical H2/H3 progression. No skipped levels.
- **JSON-LD Article/NewsArticle schema**: headline, image, datePublished, dateModified, author[] (Person with name + url). Validate with Rich Results Test.
- **Author byline** linking to author/about page. **Last Updated date.**
- **Inline citations** to authoritative sources (papers, official docs, recognized experts). YMYL claims ALL need citations.
- **Structured, extractable formats**: bullets, numbered lists, tables, clear section headers.
- **Images/video** with descriptive alt text and image metadata.
- **URL**: clean, descriptive, canonical.

## GEO-Relevant Content Structure (for AI citation)

Generative engines pull individual sections, not whole articles. So:
- **Each section should be self-contained**, answer one question completely.
- **Front-load the direct answer/definition** in each section, then expand.
- **Use extractable formats** (lists, tables) that LLMs can parse and cite.
- **Cite sources by name** inline ("According to [paper/source]..."), content that explicitly references trusted sources is cited more.
- **Original data points** are high-value for AI synthesis.

## Integration (so this skill is ALWAYS applied)

This skill is the SEO/GEO layer that must be referenced wherever Google visibility matters:

1. **Three Outlines cron**, loaded so outlines are planned authority-first (non-commodity, E-E-A-T, YMYL citations, self-contained sections) before any keyword work.
2. **keyword-research-seo skill**, keyword research is performed IN SERVICE of an authority angle, not as the driver. See that skill's "Google SEO/GEO Best Practices" section.
3. **phantombyte-distribution**, this skill is the primary source for the E-E-A-T and AI-optimization steps it already covers.

## Pitfalls

- **Don't let keyword research drive the angle.** Vinny was explicit: "I don't want to decide writing material based on keywords." Authority and Google best practices come first; keywords support.
- **Don't treat GEO/AEO as separate from SEO.** Google says optimizing for generative AI search IS SEO. Avoid cargo-cult hacks (llms.txt, chunking for AI).
- **Don't write commodity content** even if it ranks for a keyword. Non-commodity, first-hand value is the long-term play.
- **Don't forget trust > expertise.** All four E-E-A-T matter, but trust is what Google weights most.
- **Don't ship unverified claims** in YMYL content, accuracy is non-negotiable for our reputation strategy.
- **Don't skip technical structure** (title, schema, headings, citations), it's the substrate of both classic and AI search.
- **Don't over-optimize for AI at the expense of human readers**, Google explicitly warns against this.

## Verification Checklist

- [ ] Content is non-commodity: original value/first-hand experience beyond common knowledge
- [ ] Clear authorship (byline → author page) and process transparency
- [ ] Every factual/YMYL claim has a citation to an authoritative source
- [ ] Title is descriptive, concise, unique, keyword-stuffed-free
- [ ] Meta description written after content, accurate
- [ ] Heading hierarchy correct (H1 → H2 → H3)
- [ ] JSON-LD Article schema present and validated (Rich Results Test)
- [ ] Sections are self-contained with front-loaded answers (AI-citable)
- [ ] No spammy practices: no keyword stuffing, no fake freshness, no scaled low-value content
- [ ] Written for people first; satisfies "would a visitor be satisfied?"
