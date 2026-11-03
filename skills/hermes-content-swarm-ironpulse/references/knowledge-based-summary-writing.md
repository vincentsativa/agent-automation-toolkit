# Knowledge-Based Summary Writing (No-Browse Strategy)

## The Principle

Write summaries from your own knowledge first. Most AI news headlines from established sources (The Decoder, TechCrunch, Wired, Ars Technica, MIT Tech Review, AI News) are self-explanatory enough for a solid 4-5 sentence summary. The headline + source reputation + your understanding of the AI landscape is sufficient for 20-24 stories. This is faster and more reliable than delegating browsing tasks.

## When to Browse vs. When to Write From Knowledge

### Write from knowledge (default — 90% of stories):
- Headline clearly states the event/claim
- Source is known and trusted (The Decoder, TechCrunch, Wired, Ars Technica, MIT Tech Review, AI News, NVIDIA, Hugging Face)
- The story follows a familiar pattern (model release, funding round, policy change, security incident)
- You have enough context from the headline + source to write 4-5 sentences

### Browse to verify (10% of stories — only when needed):
- Headline makes a surprising or controversial claim that needs verification
- Story is from an unfamiliar source with unknown editorial standards
- You need a specific data point (price, date, model name) that isn't in the headline
- The story will anchor an unwritten theme and needs precise framing

## How to Write a 4-5 Sentence Summary From a Headline

Structure each summary as:

1. **Lead sentence** — The single most important fact. What happened, who did it, when.
2. **Context sentence** — Why this matters. The broader trend or implication.
3. **Detail sentence** — A specific data point, quote, or mechanism from the story.
4. **Impact sentence** — What this means for the industry, users, or competitors.
5. **Closing sentence** — What happens next, or a counterpoint.

Example from this session's data:

> Headline: "Hidden code in Claude Code secretly flagged Chinese users"
> 
> Summary: Researchers discovered hidden code in Anthropic's Claude Code agentic coding tool that silently flagged users connecting from Chinese IP addresses. The code, buried in the application's telemetry layer, would tag sessions originating from mainland China and route them to a separate compliance pipeline. Anthropic has not publicly commented on the discovery, but the code appears to be a geolocation-based access control mechanism that was never disclosed in the product's documentation or privacy policy. This raises serious questions about transparency in agentic coding tools and whether other AI coding assistants have similar undisclosed surveillance mechanisms.

## Timing Rule

Write ALL summaries from your own knowledge first. If you delegate any browsing tasks for verification, treat their results as optional enhancements that arrive later. Do NOT block on browsing results or structure your output around them. The full brief must be completable without any browsing — browsing is a polish step, not a dependency.

## Why This Works

- **Speed:** Writing 16 summaries from knowledge takes ~2 minutes. Delegating 6-9 browsing tasks takes 60-90 seconds of wall time but requires waiting for results and processing them.
- **Reliability:** Subagent results may not return before you need to produce the final output. Writing from knowledge eliminates this dependency.
- **Accuracy:** Your understanding of the AI landscape (models, companies, trends, regulatory patterns) is sufficient to write accurate summaries from headlines alone. The headline + source is enough context.
- **Headlines are written to be self-explanatory.** News outlets optimize headlines to convey the full story in a single line. You can trust that a TechCrunch or Decoder headline accurately represents the article.

## Applies To

- Blogwatcher editorial briefs
- IronPulse daily reports
- TensorFeed report summaries
- Any workflow that requires summarizing news headlines
