---
name: tool-vetting
description: "Vet tools: access vs extraction, ground in real bottlenecks."
---

# Tool Vetting for Vinny's Stack

## Trigger
Use when Vinny asks "is this safe?", "would this help us?", "is this useful?", or links a tool/library for evaluation.

## Core Heuristic

**Two questions, in order:**

1. **What problem does this actually solve?**, Be precise. Not "web scraping." Is it access (getting past blocks, proxies, residential IPs, anti-bot evasion) or extraction (HTML-to-markdown, formatting, parsing, LLM-ready output)?

2. **Is that problem one Vinny has?**, Map against what's already in the stack. Don't evaluate in a vacuum.

## The Critical Distinction

| Category | Solves | Examples |
|---|---|---|
| **Access tools** | Getting past the wall, proxy rotation, residential IPs, anti-bot evasion, CAPTCHA solving | Firecrawl, BrightData, ScrapingBee, residential proxy services |
| **Extraction tools** | Formatting what's on the other side, HTML to markdown, structured data, LLM-ready output | Crawl4AI, Deepcrawl, CRW, WebReaper, GroktoCrawl |

**Firecrawl is an access tool that also does extraction.** Most open-source "Firecrawl alternatives" are extraction-only. They are not the same thing. The hard problem is access, and that costs real money, there is no open-source equivalent.

## Vinny's Existing Stack (relevant to tool evaluation)

- **TensorFeed**, API access to HN, ZDNet, The Verge, WIRED, MIT Tech Review
- **Blogwatcher**, RSS/Atom monitoring for blog lists
- **Scrapling**, stealth scraping framework (fingerprint spoofing, but still runs on your IP)
- **Rotunda browser**, agent-first Firefox fork (stealth browsing, same IP problem)
- **Browser tools**, full browser automation for JS rendering
- **IronPulse**, daily AI news pipeline

## Evaluation Template

When Vinny asks about a tool, structure the answer as:

1. **What it is** (one sentence)
2. **What problem it actually solves** (access vs. extraction vs. something else)
3. **Does Vinny have that problem?** (map to stack above)
4. **Verdict**, clear yes/no/maybe with reasoning

## Pitfalls

- **Don't be pedantic about technical similarities when the practical difference is what matters.** Crawl4AI and Firecrawl both do extraction. Only one does access. That's the difference that matters.
- **Don't evaluate in a vacuum.** Always ground against what Vinny already has. A tool that solves a problem he doesn't have is noise.
- **Don't lead with "it's similar to X" unless X solves the same actual problem.** Similar architecture does not equal similar value.
- **Don't recommend a tool that requires a paid proxy service on top** without being explicit about that cost. "Self-hosted alternative" often means "you still need to pay for the hard part separately."
- **Don't assume open source = free to operate.** Extraction engines are cheap to run. Proxy networks are not. If the tool's value depends on a paid upstream service (remote browsers, proxy APIs), say so upfront.
