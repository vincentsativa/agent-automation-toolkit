---
name: q-article-swarm
title: "Q-Article Swarm - Rapid AI News Article Pipeline"
version: 1.0
description: "Full 6-phase multi-agent swarm workflow for AI news research, verification, synthesis, and article generation. Optimized for PhantomByte-style technical content. Runs with or without delegation API."
author: Vinny Barreca
tags: [content, swarm, ai-news, article-generation, phantom-byte, research]
---

# Q-Article Swarm: Rapid AI News Article Pipeline

## Overview

This skill executes a complete 6-phase swarm workflow for generating AI infrastructure news articles. Designed for PhantomByte but adaptable to any technical AI publication.

**Key Features:**
- 3 concurrent scanner agents (news, academic, developer)
- Source verification gate (Freespoke + primary sources)
- 3-draft generation (Alpha/Beta/Gamma angles)
- 3-voter + fact-checker evaluation
- UNC path delivery for Telegram

**Runtime:** ~15-25 minutes (sequential), ~5-8 minutes (parallel with delegation)

**Max Concurrent Agents:** 3 (configurable via delegation.max_concurrent_children)

---

## Phase Overview

| Phase | Name | Purpose | Tools Required |
|-------|------|---------|----------------|
| 1 | SEO & Keyword Gap Analysis | Scrape target site for gap identification | browser |
| 2 | Intelligence Gathering | Spawn 3 scanner agents | browser, web |
| 2.5 | Source Verification | Verify UNVERIFIED stories via Freespoke | browser, web |
| 3 | Data Synthesis | Create unified intelligence brief | file |
| 4 | Content Generation | Write 3 drafts (Alpha/Beta/Gamma) | file, skills |
| 5 | Evaluation | 3 voters + 1 fact-checker | file |
| 6 | Final Output | Format and deliver UNC paths | file, send_message |

---

## Prerequisites

### Required Skills
Load these before running:
- `phantom-byte-writing-style` - Voice and formatting rules
- `phantom-swarm-v1-live` - Full reference (optional, for comparison)

### Required Tools
- `browser_navigate`, `browser_snapshot`, `browser_scroll` - Web scraping
- `web_search` or `browser` - Freespoke verification
- `write_file`, `read_file`, `patch` - File operations
- `delegate_task` - Optional, for parallel execution
- `send_message` - Optional, for Telegram delivery

### Configuration Notes

**Delegation API Key Issue:**
If `delegation.api_key` is empty in `~/.hermes/config.yaml`, the swarm runs sequentially instead of in parallel. This adds ~10-15 minutes to runtime but produces identical results.

To fix for parallel execution:
```yaml
delegation:
  api_key: "your-api-key-here"
  max_concurrent_children: 3
```

---

## Phase 1: SEO & Keyword Gap Analysis

**Goal:** Scrape the target publication to identify keyword gaps.

**Steps:**

1. Navigate to the target site and scroll through all content
2. Extract topic inventory - count articles per category
3. Identify high-frequency vs. zero-coverage topics
4. Save gap analysis to workspace

**Output:** `{DATE}-seo-gap-analysis.md`

---

## Phase 2: Intelligence Gathering

**Goal:** Collect stories from 3 distinct sources.

### Scanner 2A: News/Tech
**Sources:** TechCrunch AI, The Verge AI, Ars Technica, BBC Tech, 9to5Mac
**Output:** `{DATE}-scanner-news.md`

### Scanner 2B: Academic
**Sources:** arXiv cs.AI recent, Hugging Face papers, ICLR/NeurIPS proceedings
**Output:** `{DATE}-scanner-academic.md`

### Scanner 2C: Developer
**Sources:** GitHub trending, Hacker News, Hugging Face trending
**Output:** `{DATE}-scanner-developer.md`

**Required Fields Per Story:**
- Headline, Source URL (primary), Publication date
- Summary (2-3 sentences)
- Keyword gaps addressed
- Viral potential (HIGH/MEDIUM/LOW)
- Verification status (VERIFIED/UNVERIFIED)

---

## Phase 2.5: Source Verification

**Goal:** Verify all UNVERIFIED stories using Freespoke.com.

**Process:**
1. Search each UNVERIFIED story on Freespoke
2. Check for primary source OR 3+ secondary sources
3. Update verification status in scanner files

**Verification Gate Rules:**
- VERIFIED = Primary source OR 3+ secondary sources
- UNVERIFIED = Fewer than 3 sources, no primary
- HALLUCINATION RISK = Conflicting reports, no credible sources

---

## Phase 3: Data Synthesis

**Goal:** Create unified intelligence brief from all scanner outputs.

**Process:**
1. Read all scanner files + SEO gap analysis
2. Deduplicate stories across sources
3. Tier by priority (Tier 1-4)
4. Select winner using weighted criteria
5. Generate 3 article angles (Alpha/Beta/Gamma)

**Output:** `{DATE}-synthesis-brief.md`

---

## Phase 4: Content Generation

**Goal:** Write 3 complete drafts following PhantomByte style guide.

**Required:** Load `phantom-byte-writing-style` skill before writing.

**Style Requirements:**
- First-person narrative ("I ran the benchmark...")
- Visceral opening hook
- NO EM DASHES (use periods, parentheses, or colons)
- Colloquial contractions enforced (it's, don't, can't, etc.)
- Short punchy fragments for emphasis
- Direct address to reader ("you")

**Draft Specifications:**

| Draft | Length | Structure | Tone |
|-------|--------|-----------|------|
| Alpha | 6-8K chars | Problem → Evidence → Implications | Pragmatic |
| Beta | 6-8K chars | Challenge consensus → Evidence → Callouts | Irreverent |
| Gamma | 10-15K chars | Implementation walkthrough with code | Tutorial |

**Output Files:** `{DATE}-draft-alpha.md`, `{DATE}-draft-beta.md`, `{DATE}-draft-gamma.md`

---

## Phase 5: Evaluation

**Goal:** Score all 3 drafts using 3 voters + 1 fact-checker.

### Scoring Weights
- Voter 1 (Gap Coverage): 40%
- Voter 2 (Viral Potential): 30%
- Voter 3 (Voice Alignment): 20%
- Fact-Checker (Accuracy): 10% + veto power

**Veto Rule:** Critical errors (wrong numbers, fabricated sources) disqualify draft regardless of voter scores.

**Output:** `{DATE}-evaluation-results.md`

---

## Phase 6: Final Output

**Goal:** Format and deliver final article path.

**Delivery Rules:**

1. **Telegram (CRITICAL):** Output ONLY the UNC file path. NEVER dump article content.
2. **Local Files:** Save all drafts, evaluation results, synthesis brief
3. **Format:** `\\wsl.localhost\Ubuntu\home\vincent\.hermes\workspace\q-article-swarm\{DATE}-draft-{winner}.md`

---

## Execution Modes

### Parallel Mode (Delegation Available)
Runtime: ~5-8 minutes

### Sequential Mode (No Delegation)
Runtime: ~15-25 minutes

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Em dash leakage | Search for `—` and `–`, replace with periods/parentheses |
| Token/time math errors | Use measured benchmarks, not theoretical calculations |
| Source verification skipping | Always run Phase 2.5 |
| Delegation key confusion | Config requires `delegation.api_key` specifically |
| Telegram content dump | Output ONLY UNC path, never article text |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Verification Rate | 100% |
| Fact-Check Pass | 0 critical errors |
| Gap Coverage | 2+ CRITICAL gaps |
| Voice Compliance | Zero em dashes, all contractions enforced |
| Runtime | <25 min sequential, <10 min parallel |

---

## Version History

- **v1.0** (April 23, 2026): Initial release. Tested on Tool Attention story (arXiv:2604.21816). Gamma draft won 37/40.
