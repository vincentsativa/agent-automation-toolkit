---
name: article-qa-review
title: Article QA Review Checklist for Article Blaster
version: 1.0
description: Systematic QA review workflow for PhantomByte articles - em dash sweep, fact-checking, style compliance, and SEO audit
author: Vinny Barreca
tags: [qa, article-blaster, phantom-byte, seo, fact-checking]
---

# Article QA Review Checklist

**When to use:** After drafting a PhantomByte article, before publishing. Run this QA review to catch style violations, factual errors, and SEO gaps.

**Prerequisites:**
- Article draft file (`.md`)
- Synthesis documents (synthesis-1, synthesis-2)
- Keywords document (if available)
- `phantom-byte-writing-style` skill loaded
- For draft selection/evaluation methodology, see `references/panel-voting.md`

---

## Phase 1: Em Dash Sweep (CRITICAL)

**PhantomByte style explicitly prohibits em dashes.** This is a hard requirement.

### Search Patterns
```bash
# Search for em dash (U+2014)
search_files(pattern='-', path=<draft_path>, target='content')

# Search for en dash (U+2013)
search_files(pattern='–', path=<draft_path>, target='content')
```

### Action
- **If found:** Replace every instance with:
  - Period + new sentence: "word. Word"
  - Parentheses: "word (word)"
  - Colon for explanations: "word: explanation"
  - Comma for simple breaks

### Pass Criteria
- Zero em dashes (`-`) in draft body
- Zero en dashes (`–`) in draft body
- Synthesis documents may contain em dashes (they're source materials, not published content)

---

## Phase 2: Fact-Checking Against Source Research

**Every statistic, claim, date, name, and number must be verified against available sources. When synthesis documents exist, use them. When they don't, perform independent web verification before publishing.**

### Source Priority
1. **Synthesis documents** (if available), primary source per normal workflow
2. **Independent web verification**, required when draft arrives without synthesis docs, OR when draft contains claims not found in synthesis docs
3. **Cross-reference multiple sources**, any claim that appears in only one source should be flagged as ⚠️ SINGLE-SOURCE

### Fabrication Detection (CRITICAL)
When a draft contains specific statistics, model names, pricing, or product names that cannot be verified through web search:
- **Flag immediately** as ❌ UNVERIFIED / LIKELY FABRICATED
- **Do not publish** with unverified specific numbers (exact percentages, dollar amounts, model names)
- **Replace with verified alternatives** or generalize the claim (e.g., "studies show significant failure rates" instead of "59.4% false rejection rate")
- Common fabrication patterns to watch for:
  - Model names that don't exist on HuggingFace or official pages
  - Benchmark scores that don't appear on official leaderboards
  - "Postmortems" or reports that can't be located at the cited source
  - Products or tools that don't have real GitHub repos or websites
  - Pricing that contradicts official pricing pages

### Process

1. **Extract claims from draft** - Read through and identify factual assertions:
   - Statistics (percentages, counts, dates)
   - Named entities (people, companies, laws)
   - Specific events (investigations, breaches, settlements)
   - Technical specifications (hardware, performance numbers)

2. **Cross-reference with synthesis documents** - For each claim:
   - Open synthesis-1 and synthesis-2
   - Search for the claim or supporting data
   - Verify exact numbers, names, and characterizations

3. **Mark verification status**:
   - ✅ VERIFIED - Matches source exactly
   - ⚠️ PARTIAL - Accurate but missing context
   - ❌ UNVERIFIED - No source support found
   - ⚠️ MISSING IN DRAFT - Important data from sources not included

### Common Claims to Verify
- Criminal investigation details (who, what, when, outcomes)
- Breach/incident specifics (company, cause, impact numbers)
- Investment/deal amounts ($ figures, companies involved)
- Polling data (percentages, demographic breakdowns)
- Technical specs (hardware requirements, performance metrics)
- Regulatory actions (FTC settlements, law firm apologies)
- **Model names**, verify exists on HuggingFace or official vendor page
- **Benchmark scores**, verify on official leaderboard (LiveCodeBench, SWE-Bench, LMSYS, etc.)
- **Pricing claims**, verify against official pricing pages
- **Named reports/postmortems**, confirm the document actually exists at the cited source

### Output Format
```markdown
### Claim: [Brief description]
**Article Text (Line N):** "[quote from draft]"
**Source Verification (synthesis-X, line N):** "[quote from source]"
**Status:** ✅ VERIFIED / ⚠️ PARTIAL / ❌ UNVERIFIED
```

---

## Phase 3: Grammar and Style Review

### Contraction Enforcement
**PhantomByte style requires colloquial contractions.**

**Search for expanded forms:**
- `it is` → `it's`
- `do not` → `don't`
- `does not` → `doesn't`
- `is not` → `isn't`
- `are not` → `aren't`
- `will not` → `won't`
- `would not` → `wouldn't`
- `cannot` → `can't`
- `have not` → `haven't`
- `has not` → `hasn't`
- `was not` → `wasn't`
- `were not` → `weren't`
- `they are` → `they're`
- `we are` → `we're`
- `you are` → `you're`
- `that is` → `that's`
- `here is` → `here's`
- `there is` → `there's`

**Exception:** Past-tense verbs containing "not" (e.g., "already parsed" is fine)

### Sentence Structure Check
- ✅ Short punchy fragments for emphasis ("Not a typo.")
- ✅ Medium declarations ("Hardware is not a commodity anymore.")
- ✅ Long analytical sentences with multiple clauses
- ✅ Variation in sentence length throughout

### First-Person Narrative
- ✅ Opens with personal experience or credibility statement
- ✅ Uses "I" to establish lived experience
- ✅ Speaks directly to reader as "you"

---

## Phase 4: PhantomByte Writing Style Compliance

### Opening Hook Pattern
Verify draft uses one of these patterns:

**Pattern A - Personal Visceral Reaction:**
```
I [reaction verb] at the [thing]. $[price]. For [item]. Not a typo.
```

**Pattern B - Technical Failure:**
```
If you've been [activity] lately, you've seen it. [Symptom].
```

**Pattern C - Systemic Issue:**
```
The [problem] is what happens when [cause 1] [result].
```

### Heading Structure
- **H2:** Bold, declarative statements ("The Florida Precedent: Why This Changes Everything")
- **H3:** Specific, tactical labels ("Regulatory Risk", "Security Risk")
- ✅ Use colons in headings for punchy sub-clauses

### Lists & Formatting
- ✅ Arrow prefix with bold labels: `→ **label:** description`
- ✅ Data tables for metrics comparison
- ❌ NO bullet-point lists (`- item`) inside prose paragraphs
- ❌ NO horizontal rules (`---`) between prose sections

### Closing Strategy
Final paragraph should:
- Return to opening problem with new context
- Include actionable call-to-action
- Use strategic fragments for emphasis

---

## Phase 5: SEO Keyword Audit

### Process

1. **Load keywords document** - Read priority keywords with volume, competition, and content gap scores

2. **Search draft for each priority keyword** - Use exact phrase matching:
   ```bash
   search_files(pattern='exact keyword phrase', path=<draft_path>, target='content')
   ```

3. **Evaluate placement quality:**
   - ✅ In title/H1
   - ✅ In H2 heading
   - ✅ In body (4-6 mentions for secondary, 8-12 for primary)
   - ✅ In meta description (if applicable)
   - ❌ Missing or only partial match

4. **Identify content gaps** - Keywords with high content gap score (⭐⭐⭐⭐⭐) that are completely absent

### Output Format
```markdown
| Priority | Keyword | Volume | Found? | Placement Quality |
|----------|---------|--------|--------|-------------------|
| 1 | keyword phrase | 2,400/mo | ❌ NO | MISSING |
| 2 | keyword phrase | 8,100/mo | ⚠️ PARTIAL | "variant" used, not exact |
| 4 | keyword phrase | 1,900/mo | ✅ YES | Title + Section 5 |
```

### Recommendations
For missing high-priority keywords:
- Suggest specific H2 headings to add
- Identify sections where keyword fits naturally
- Estimate revision time (words to add)

---

## Phase 6: Final Scoring & Recommendations

### Scoring Template

| Category | Score | Notes |
|----------|-------|-------|
| Em Dash Compliance | 0-100% | Zero em dashes = 100% |
| Fact-Checking | 0-100% | % of claims verified |
| Grammar & Style | 0-100% | Contraction compliance, sentence variation |
| PhantomByte Voice | 0-100% | Opening, headings, tone, closing |
| SEO Optimization | 0-100% | % of priority keywords placed |

**Overall Score:** Average of all categories

### Verdict Thresholds
- **95-100%:** Ready to publish
- **85-94%:** Ready with minor revisions
- **70-84%:** Needs significant revisions
- **<70%:** Major rewrite recommended

### Recommendation Format
```markdown
**Critical (Must Fix):**
1. [Issue] - [Estimated time to fix]

**High Priority (Should Fix):**
1. [Issue] - [Estimated time to fix]

**Medium Priority (Nice to Have):**
1. [Issue] - [Estimated time to fix]

**Estimated Total Revision Time:** X minutes
```

---

## Output Files

Save QA report to:
```
~/.hermes/workspace/article-drafts/<slug>/<slug>-qa.md
```

**Report Structure:**
1. Executive Summary (table with scores)
2. Em Dash Sweep results
3. Fact-Checking details (claim-by-claim)
4. Grammar & Style findings
5. PhantomByte compliance assessment
6. SEO keyword audit
7. Recommendations with priority levels
8. Final verdict with overall score

---

## Common Pitfalls

1. **Em dashes in synthesis documents** - These are source materials, not the draft. Only check the draft file itself.

2. **Partial keyword matches** - "local inference" ≠ "local LLM inference". Search for exact phrases.

3. **Claims without line numbers** - Always note the line number when quoting from draft for easy reference during revisions.

4. **Missing data from synthesis** - Important statistics in synthesis documents that aren't in the draft should be flagged as "MISSING FROM DRAFT" with recommendation to add.

5. **Draft path doesn't exist**, If the specified draft path doesn't exist, search sibling directories for similar slugs (e.g., `ai-liability-shield` vs `ai-liability-crisis`).

6. **Fabricated claims without synthesis docs**, When a draft arrives standalone (no synthesis docs), you MUST verify all specific numbers, model names, product names, and pricing against the web before passing fact-check. Do not assume the draft's claims are accurate. This is the #1 risk for PhantomByte articles: specific-sounding but unverifiable statistics.

---

*Skill Version: 1.0*
*Created: 2026-04-21*
*Based on QA review of "The Liability Shield: Why Sovereign AI is the Only Safe Choice for Developers"*
