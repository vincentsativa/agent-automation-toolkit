---
name: phantom-swarm-v1
title: Phantom-Byte Intelligence Swarm
version: 1.0
description: Full 6-phase multi-agent swarm workflow for SEO analysis of articles.phantom-byte.com, real-time AI intelligence gathering, synthesis, content generation, evaluation, and file export. Max 3 concurrent agents at all times.
author: Vinny Barreca
tags: [swarm, multi-agent, SEO, intelligence, content-creation, phantom-byte]
toolsets: [file, web, browser]
---

# Phantom-Byte Intelligence Swarm (Phantom-Swarm-V1)

Full pipeline: SEO audit → Intelligence gathering → Synthesis → Writing → Evaluation → File export.

**Golden Rule: Max 3 concurrent model executions at any time.** Ollama Cloud Pro times out beyond this.

## Concurrency & Error Protocol

- Never spawn more than 3 agents simultaneously
- If an agent hangs or returns empty payload: wait 5 seconds, retry once. If it fails again, log the failure and proceed with remaining data
- If scraping is blocked (403/Captcha) in Phase 1: pause and request manual keyword input from user
- Verification Gates are mandatory: do NOT proceed to the next phase until all agents in the current phase complete

## Phase 1: SEO & Keyword Gap Analysis (The Analyst)

**Executed directly (no sub-agent).**

1. Navigate to `https://articles.phantom-byte.com` using browser
2. Scrape all visible article pages for:
   - Page titles
   - Meta descriptions
   - H1/H2 headings
   - Any existing keyword patterns
   - Article topics/angles covered
3. If blocked by bot detection (403/Captcha), pause and ask user for manual keyword input
4. Compile a keyword inventory of what PB currently covers
5. Perform a gap analysis against trending "Sovereign AI" topics to find missing high-value keywords
6. Save output to `~/.hermes/workspace/phantom-swarm/[date]-seo-gap-analysis.md`

**VERIFICATION GATE: AWAIT Analyst completion. Verify the list is compiled before proceeding.**

## Phase 2: Intelligence Gathering (The Scanner Swarm - Max 3 Agents)

Spawn 3 scanner agents concurrently via `delegate_task`:

### Agent 2A (News/Tech Scanner)
- Scan MSM and tech blogs for AI policy and product releases
- Use browser to navigate: TechCrunch AI, The Verge AI, Ars Technica AI, BBC Tech, AP News AI
- Skipped/blocked: Reuters, CNN, Bloomberg, Reddit
- Extract: headline, source, date, 4-sentence minimum summary
- Focus: Sovereign AI, local AI, self-hosting, open-source AI tools, hardware news
- Save to `~/.hermes/workspace/phantom-swarm/[date]-scanner-news.md`

### Agent 2B (Academic Scanner)
- Search ArXiv for recent papers on: sovereign AI, local LLM deployment, efficient inference, model quantization, agent frameworks
- Use browser to navigate `https://arxiv.org/list/cs.AI/recent` and `https://arxiv.org/search/?query=sovereign+AI&searchtype=all`
- Extract: paper title, authors, arxiv ID, key finding (2-3 sentences)
- Save to `~/.hermes/workspace/phantom-swarm/[date]-scanner-academic.md`

### Agent 2C (Developer Scanner)
- Scan GitHub trending repos (https://github.com/trending) for AI/ML projects
- Check Hacker News (https://news.ycombinator.com) for AI developer discussions
- Look for: new AI frameworks, self-hosted AI tools, agent orchestration libraries, local inference engines
- Extract: repo/tool name, stars/engagement, description, relevance to Sovereign AI
- Save to `~/.hermes/workspace/phantom-swarm/[date]-scanner-developer.md`

**VERIFICATION GATE: AWAIT all 3 scanners. Handle hangups per error protocol. Proceed only when at least 2 of 3 have returned data.**

## Phase 3: Data Synthesis (The Synthesizer)

**Executed directly (no sub-agent).**

1. Read all scanner outputs and SEO gap analysis
2. Deduplicate stories across all three scanner feeds
3. Map each news item to Phase 1 keyword gaps
4. Create a unified intelligence brief that:
   - Lists all unique stories with source triangulation
   - Tags each story with relevant keyword gaps it fills
   - Ranks stories by: newsworthiness × PB keyword gap relevance × viral potential
5. Save to `~/.hermes/workspace/phantom-swarm/[date]-synthesis-brief.md`

**VERIFICATION GATE: AWAIT unified intelligence brief. Verify file exists before proceeding.**

## Phase 4: Content Generation (The Writer Swarm - Max 3 Agents)

Spawn 3 Writer Agents concurrently via `delegate_task`. Each receives the synthesis brief and SEO gap analysis.

All writers must load and follow `phantom-byte-writing-style` skill.

### Writer Agent Alpha
- Write a complete article draft on the #1 ranked story
- Angle: Direct, hard-hitting analysis of the news
- Incorporate SEO keyword gaps from Phase 1
- Follow PhantomByte style guide (NO EM DASHES)
- Save to `~/.hermes/workspace/phantom-swarm/[date]-draft-alpha.md`

### Writer Agent Beta
- Write a complete article draft on the #1 ranked story
- Angle: Contrarian/underexplored take that challenges conventional framing
- Incorporate different keyword gaps than Alpha
- Follow PhantomByte style guide (NO EM DASHES)
- Save to `~/.hermes/workspace/phantom-swarm/[date]-draft-beta.md`

### Writer Agent Gamma
- Write a complete article draft on the #2 ranked story
- Angle: Technical deep-dive for the expert audience
- Incorporate remaining keyword gaps
- Follow PhantomByte style guide (NO EM DASHES)
- Save to `~/.hermes/workspace/phantom-swarm/[date]-draft-gamma.md`

**Article format:**
```
[Title]

Written by: Vinny Barreca
[Date]

[Opening paragraph - visceral, first-person, PhantomByte style]

[Body with H2/H3 headings, code blocks, tables where appropriate]
[No bullet-point lists in prose - flowing narrative]
[No horizontal rules between sections]
[Short punchy fragments for emphasis]

[Final paragraph returns to opening problem with new context]
```

**VERIFICATION GATE: AWAIT all 3 drafts. Verify at least 2 of 3 exist before proceeding.**

## Phase 5: Evaluation, Fact-Checking & File Export

### Step 1: Voter Swarm (3 Voters concurrently)

Spawn 3 Voter Agents via `delegate_task`. Each voter receives all 3 drafts and ranks them #1-#3 with justifications based on:
- PhantomByte writing style compliance
- SEO keyword integration
- Reader engagement potential
- Technical accuracy
- Originality of angle

Save votes to `~/.hermes/workspace/phantom-swarm/[date]-vote-[a/b/c].md`

**Tally votes. Crown the winner.**

### Step 2: Fact-Checker (1 agent)

Spawn 1 Fact-Checking Agent via `delegate_task`. It receives the winning draft.

Tasks:
- Verify all technical claims (specs, versions, prices, dates)
- Verify all quoted statistics
- Check for em dashes (flag every instance)
- Verify PhantomByte style compliance
- Fix any factual errors
- Finalize the text

Save to `~/.hermes/workspace/phantom-swarm/[date]-final-article.md`

**VERIFICATION GATE: Ensure the file is written correctly to disk.**

## Phase 6: Final Output Formatting (Strict Compliance)

Summarize the workflow into this EXACT format:

### Part 1: The Top 10 AI News Stories
10 headlines with a minimum 4-sentence summary each.

### Part 2: Article Ideas & Angles
5 ideas ranked #1 (Best) to #5 (Worst).

### Part 3: The AI Selection
The single best fit for the site with a detailed "Why" explanation.

### Part 4: Final Draft Delivery
Provide the FULL LOCAL FILE PATH to the text document containing the winning draft.

### Part 5: Orchestrator Sign-off
Confirmation of error handling and verification of all phases.

## Trigger Phrases
- "run phantom swarm"
- "execute phantom swarm"
- "full swarm analysis"
- "phantom-swarm-v1"

## Execution Order
1. Phase 1: Direct execution (SEO scrape + gap analysis)
2. Phase 2: delegate_task (3 scanners, max 3 concurrent)
3. Verification Gate
4. Phase 3: Direct execution (synthesis)
5. Verification Gate
6. Phase 4: delegate_task (3 writers, max 3 concurrent)
7. Verification Gate
8. Phase 5 Step 1: delegate_task (3 voters, max 3 concurrent)
9. Phase 5 Step 2: delegate_task (1 fact-checker)
10. Verification Gate
11. Phase 6: Assemble and deliver final output