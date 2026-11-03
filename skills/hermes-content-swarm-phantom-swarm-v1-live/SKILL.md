---
name: phantom-swarm-v1-live
title: Phantom-Byte Intelligence Swarm (Live-Tested Version)
version: 1.1
description: Full 6-phase multi-agent swarm workflow for SEO analysis of articles.phantom-byte.com, real-time AI intelligence gathering, synthesis, content generation, evaluation, and file export. Max 3 concurrent agents at all times. This is the live-tested version with lessons learned from the first run baked in.
author: Vinny Barreca
tags: [swarm, multi-agent, SEO, intelligence, content-creation, phantom-byte]
toolsets: [file, web, browser]
---

# Phantom-Byte Intelligence Swarm (Phantom-Swarm-V1-Live)

Full pipeline: SEO audit → Intelligence gathering → Synthesis → Writing → Evaluation → File export.

**Golden Rule: Max 3 concurrent model executions at any time.** Ollama Cloud Pro times out beyond this.

## Model Requirement (STRICT)

**This skill MUST run on one of these models only:**

1. `qwen3.5:397b` (primary)
2. `kimi-k2.5` (fallback #1)
3. `kimi-k2.6` (fallback #2)
4. `glm-5.1` (fallback #3)

**DO NOT run on any other model.** This workflow requires the reasoning capacity and context handling of these specific models. Running on smaller/unsupported models will cause failures, hallucinations, and wasted compute.

**Before executing:** Verify the current model is in the approved list above. If not, abort and notify the user.

## Concurrency & Error Protocol

- Never spawn more than 3 agents simultaneously
- If an agent hangs or returns empty payload: wait 5 seconds, retry once. If it fails again, log the failure and proceed with remaining data
- If scraping is blocked (403/Captcha) in Phase 1: pause and request manual keyword input from user
- Verification Gates are mandatory: do NOT proceed to the next phase until all agents in the current phase complete

## CRITICAL: Delegation API Key Configuration

**Problem:** `delegate_task()` fails with "no API key found" even when `OPENAI_API_KEY` is set.

**Root Cause:** The Hermes config explicitly requires `delegation.api_key` in `~/.hermes/config.yaml`. It does NOT fall back to `OPENAI_API_KEY` for delegation.

**Fix (Parallel Mode):**
```yaml
# ~/.hermes/config.yaml
delegation:
  api_key: "YOUR_API_KEY"  # Required for delegate_task()
  max_concurrent_children: 3
```

**Fallback (Sequential Mode):**
If `delegation.api_key` is empty, execute all phases manually using browser/file tools instead of `delegate_task()`. This adds ~10-15 minutes but produces identical results.

**Sequential Execution Pattern:**
```python
# Instead of: delegate_task(tasks=[scanner_a, scanner_b, scanner_c])
# Do: Execute each scanner workflow directly with browser_navigate + write_file
```

**Check before running:**
```bash
cat ~/.hermes/config.yaml | grep -A3 "delegation:"
```
If `api_key: ''` or missing, run sequential or patch config first.

## CRITICAL: Source Verification Protocol

**ALL product announcements, company claims, and specific technical specifications MUST include a primary source URL** (official blog, press release, GitHub repo, arXiv link, SEC filing). Tech blog coverage alone is NOT sufficient verification. If a scanner cannot provide a primary source, flag it as "UNVERIFIED" and exclude from top-tier ranking.

**Search Protocol:** Use Freespoke.com for all verification searches. Google/DuckDuckGo will trigger CAPTCHA blocks on residential ISP connections.

## CRITICAL: Scanner Hallucination Prevention (Lessons Learned)

**Problem:** Scanner agents have hallucinated fictional products (e.g., "Mozilla Thunderbolt" AI client — does not exist). This wastes time and risks publishing false information.

**Required Scanner Behavior:**
- **Verify product announcements against official sources** before reporting as fact (check company blogs, press releases, GitHub repos, official social media)
- **Verify exact product/model names** against primary sources before writing (e.g., "Mythos Preview" not "Mythos AI" — the fact-checker caught this discrepancy). Always use the official naming from the source.
- **Flag uncertain claims** with confidence levels: HIGH (officially confirmed), MEDIUM (multiple reputable sources), LOW (single source/unverified)
- **Do not synthesize marketing language as technical fact** — distinguish between "Mozilla announced X" vs. "Mozilla's X does Y"
- **Cross-check at least 2 independent sources** for any product launch claim before including in scanner output

**Synthesizer Duty:** When building the intelligence brief, flag any story with LOW confidence for extra fact-checking scrutiny in Phase 5.

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

Spawn 3 scanner agents concurrently via `delegate_task`.

**MANDATORY:** Each scanner must load relevant domain skills before executing:
- News Scanner: load `blogwatcher-rss-setup` for known working feeds
- Academic Scanner: load `arxiv` skill for proper paper extraction
- Developer Scanner: load `github-repo-management` for repo metadata

**SOURCE VERIFICATION REQUIREMENT:** Every story extracted MUST include:
1. Primary source URL (official blog, press release, GitHub, arXiv, SEC filing)
2. Publication date
3. Verification status: VERIFIED (primary source confirmed) or UNVERIFIED (secondary sources only)

Stories marked UNVERIFIED cannot rank in Tier 1 and must be flagged in the synthesis brief.

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

## Phase 2.5: Source Verification (NEW)

**Execute directly after Phase 2, before Phase 3 synthesis.**

For each UNVERIFIED story in scanner outputs:
1. Search Freespoke.com for the product/announcement name + official source
2. Check the claimed primary URL returns 200 OK (use browser_navigate)
3. If no primary source found after 2 search attempts: mark as "HALLUCINATION RISK" and downgrade to Tier 3

**Only proceed to Phase 3 when all top-tier stories are VERIFIED.**

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

**CRITICAL STYLE REMINDER FOR ALL WRITERS:** LLMs systematically avoid contractions, producing "it is" instead of "it's", "do not" instead of "don't", "cannot" instead of "can't", "will not" instead of "won't", etc. The PhantomByte style DEMANDS colloquial contractions throughout. Audit your draft and convert every expanded form to its contraction. This is the #1 style error writers make.

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

**PRE-SAVE STYLE CHECK (MANDATORY):** Before saving, each writer must self-audit:
1. Scan for em dashes (—) — replace with commas, periods, or colons
2. Scan for bullet/numbered lists in prose sections — convert to flowing narrative
3. Verify contractions are used throughout (it's, don't, can't, won't, you're, etc.)
4. If any violations found: fix before saving, note corrections in task summary

**Save only after passing self-check.**

**VERIFICATION GATE: AWAIT all 3 drafts. Verify at least 2 of 3 exist before proceeding.**

**Note on topic selection:** The synthesis brief's "AI Selection" picks the topic with the best SEO keyword gap coverage, but voters rank the actual article quality. A lower-SEO-fit topic written with superior style and originality can (and has) won. Don't override voter results based on the synthesis ranking alone.

## Phase 5: Evaluation, Fact-Checking & File Export

### Step 1: Voter Swarm (3 Voters concurrently)

Spawn 3 Voter Agents via `delegate_task`. Each voter receives all 3 drafts and ranks them #1-#3 with justifications based on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Source Verification** | 25% | Are claims backed by primary sources? Any hallucinations? |
| PhantomByte writing style compliance | 20% | Contractions, no em dashes, no bullet lists in prose |
| SEO keyword integration | 15% | Addresses identified keyword gaps |
| Reader engagement potential | 15% | Hook, pacing, emotional resonance |
| Technical accuracy | 15% | Specs, versions, prices, dates verified |
| Originality of angle | 10% | Fresh perspective vs. conventional framing |

**A draft with unverified claims or hallucinations CANNOT rank #1, regardless of other scores.**

Save votes to `~/.hermes/workspace/phantom-swarm/[date]-vote-[a/b/c].md`

**Wait for all 3 voters. Tally votes. Crown the winner.**

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

**DELIVERY METHOD: Origin (Telegram)**

⚠️ **CRITICAL TELEGRAM PROTOCOL** ⚠️
- Send **ONE message ONLY**
- Content: **THE FILE PATH STRING ONLY**
- Format: `\\wsl.localhost\Ubuntu\home/<linux-user>\.hermes\workspace\phantom-swarm\YYYY-MM-DD-final-article.md`
- **DO NOT paste article content**
- **DO NOT send summaries, headlines, or previews**
- **DO NOT send multiple messages**
- User reads the file themselves. You are a file path dispenser, not a content broadcaster.

Summarize the workflow into this EXACT format for your internal record:

### Part 1: The Top 10 AI News Stories
10 headlines with a minimum 4-sentence summary each.

### Part 2: Article Ideas & Angles
5 ideas ranked #1 (Best) to #5 (Worst).

### Part 3: The AI Selection
The single best fit for the site with a detailed "Why" explanation.

### Part 4: Final Draft Delivery
Provide the FULL LOCAL FILE PATH to the text document containing the winning draft.
**TELEGRAM: Send ONLY this line. Nothing else.**

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