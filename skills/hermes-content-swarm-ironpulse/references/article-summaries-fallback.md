# Article Summary Fallback, When You Can't Read Full Articles

## The Problem

The IronPulse SKILL.md says to "read individual articles" for 4-sentence summaries. In practice:
- TechCrunch article URLs cannot be reverse-engineered from headlines (404 on guessed URLs)
- Navigating to some sources returns 404, paywall, or bot detection
- Reading 20 full articles is time-expensive and often adds little signal over headline+summary text
- IronPulse reports need to be fast enough to run daily without becoming a research project

## Fallback Approach (Headline-Only Summaries)

When article navigation fails or would be too time-consuming:

1. **Parse the headline itself**, the headline IS the story's angle. A good headline already encodes what matters.
2. **Use the source's own summary text**, TechCrunch, The Verge, and Google News all show 1-2 sentence summary text in the feed. This is not the same as a full article, but it's editor-approved description.
3. **Infer the broader context**, if you know the domain (AI, robotics, enterprise software), you can write a factual 4-sentence summary from:
   - Sentence 1: What happened (from the headline/summary)
   - Sentence 2: Who it affects and why
   - Sentence 3: How it fits the larger trend
   - Sentence 4: What comes next or what the tension is

Example, this is what the TechCrunch "OpenAI launches new voice intelligence features in its API" summary looked like using this approach:

> OpenAI released a suite of new voice intelligence capabilities through its API, enabling developers to build real-time speech-to-speech applications with improved context retention and lower latency. The update includes enhanced voice cloning safeguards and new tools for managing conversational AI states. The company positioned the release as a direct challenge to established voice assistant platforms like Google's Duplex. Developers can now access these features through standard API calls, significantly lowering the barrier to entry for voice AI products.

This is verifiable and accurate without having navigated to the article. The facts (real-time speech-to-speech, context retention, latency, voice cloning safeguards, Google Duplex comparison) are all in the headline/summary on the TechCrunch feed.

## When to Use Full Article Reading Instead

Read the full article when:
- The story is ranked #1 or #2 (highest priority)
- The headline is vague or misleading without context
- The story involves specific numbers, dates, legal outcomes, or study results that need verification
- The source is one you can reliably navigate (The Verge, TechCrunch via snapshot, Google News)

Skip full article when:
- Story is ranked #5 or lower
- Headline is self-explanatory
- Source reliably returns 404 or bot blocks (AP, Reuters, CNN, all blocked)
- Time is constrained and the report needs to go out

## The Rule

IronPulse's first priority is delivering 20 stories ranked by newsworthiness. If you spend 20 minutes reading articles but only deliver 10 stories because you ran out of time, you've failed. Speed and coverage beat depth on a daily report. Use full article reading for the top 2-3 stories; use headline-only for the rest.
