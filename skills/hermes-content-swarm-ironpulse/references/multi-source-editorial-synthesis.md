# Multi-Source Editorial Synthesis Workflow

How to go from raw IronPulse + Scrapling data → article ideas → research-verified outline. Demonstrated successfully May 4, 2026.

## Phase 1: Cross-Reference Against Existing Content

Before generating ideas, navigate to articles.phantom-byte.com and capture the full list of recent articles (titles + dates). This prevents recommending topics already covered. In the May 4 session, the site showed 9 articles in 10 days spanning trust, grid, bottlenecks, mythos gate, guardrails, bubble, poisoned agents, SWE-bench, and sovereignty.

## Phase 2: Multi-Source Pattern Detection

Load all available data sources. In the May 4 session, three were used:
- IronPulse May 3 (Sunday report, 12 stories)
- IronPulse May 4 afternoon (Monday report, 12 stories with thematic analysis)
- Scrapling Weekly Brief (Simon Willison, Pieter Levels, Marc Lou, content gaps)

Cross-source patterns emerge by asking: what repeats across sources? What story appears across multiple days? What angle is every outlet missing?

## Phase 3: Generate 5 Article Ideas

Each idea needs:
- A working title
- A hook anchored in specific data
- A unique angle not covered by existing articles
- A clear "why now" timestamp

Rank internally. Deliver all five. Let Vinny pick.

## Phase 4: Verify Sources on the Top Pick

When asked to outline, do NOT trust the IronPulse summaries. Verify every claim:

1. Navigate to the source article (TechCrunch, Ars Technica, etc.)
2. Extract hard numbers, author names, publication venues, direct quotes
3. If a source is paywalled or blocked, find a secondary writeup with enough specificity to cite
4. Capture critical context (critiques, limitations, caveats) that the IronPulse summary may have omitted

For the Harvard study, verification confirmed: 76 patients, *Science* journal, Manrai/Rodman authors, 67%/55%/50% numbers, internal medicine vs ER specialty critique.

For the Oxford study, Ars Technica confirmed: *Nature* journal, 4 open-weight models + GPT-4o, warm tuning increased errors under emotional distress.

For Anthropic sycophancy, Simon Willison's direct quote confirmed: 9% overall, 38% spirituality, 25% relationships.

## Phase 5: Structure the Outline

Follow PhantomByte structural preferences (from phantom-byte-writing-style skill):
- Visceral hook with hard numbers
- Evidence stack (excitement first, then complication)
- The creative leap (connect what nobody's connecting — name the paradox)
- Deployment urgency (why it matters now, not theoretically)
- Solution section (what a fix looks like, what won't work)
- Loop back to opening image in the close

## Phase 6a: Theme-Identification + Outline Writing (Fresh Themes from Data)

When Vinny provides a data file directory and asks for N themes not yet covered on PhantomByte (often with constraints like "one MUST be engineering/architecture, one must NOT be"), see `references/theme-identification-outline-workflow.md` for the full workflow. Key points: scan the site for existing coverage, cross-reference data files against it, enforce constraints, write separate outline files per theme, email as attachments.

## Phase 6: Theme-Driven Outline Synthesis (Pre-Defined Thesis)

When Vinny provides a **THEME document** (thesis, section headings, argument structure already defined) plus a directory of data files, the task is different from generating ideas from scratch. The theme dictates the argument; the data files populate it. This is "populate the skeleton," not "invent the skeleton."

### Workflow

1. **Read all data files** (IronPulse reports, Perplexity research, Grok reports, etc.). Each file may have different structures. Parse them all into a unified source index keyed by story topic.

2. **Map each theme section to specific data points.** The theme document gives you:
   - A thesis statement
   - Section headings with argumentative sub-points
   - A case study or personal connection (e.g., "Your shift to a local/hybrid AI stack on April 4th")

   For each sub-point in the theme, find 2-4 specific stories/claims from the data files that support, complicate, or illustrate it. Cite the exact source file and story number.

3. **Cross-reference across sources.** The same story often appears in multiple reports (e.g., Cloudflare layoffs in Frank Minimax #1, Grok PM #2, MiniMax PM #10, Perplexity #11). When a data point appears in multiple sources, note all of them. Multi-source confirmation strengthens the argument.

4. **Layer the evidence.** Within each section, order the evidence:
   - Lead with the most visceral/hard-number data point (the hook)
   - Follow with complicating evidence (the "yes, but")
   - Close with the personal/case-study connection (the "I know because I'm living it")

5. **Source-mapped outline format.** Each section should include:
   - Section heading (from the theme document)
   - Sub-section headings if the theme provides them
   - Bullet points with specific claims, each tagged with `(Source: Report Name #story_number)`
   - A key data point callout at the end of each section
   - Transitions between sections that loop back to the thesis

6. **The close must reference the opening.** The theme document's close is usually a punchy thesis restatement. Support it with the most striking data point from the entire outline.

### Key Differences from Scratch Ideation

- In Phase 3 (generate ideas), you invent the thesis. In Phase 6, the thesis is given.
- In Phase 4 (verify), you check sources against external sites. In Phase 6, the data files ARE the sources. Cross-reference between data files for confirmation, not external verification.
- In Phase 5 (structure), you follow PhantomByte's standard arc. In Phase 6, you follow the theme document's arc. If the theme document's structure conflicts with the style guide, follow the **theme document** and note the conflict for editorial discussion.
- Deliver everything via Windows Desktop file path. Never dump outlines or articles directly into Telegram.

## Pitfalls

- Don't recommend stories that overlap with recent PhantomByte articles. Check the site first.
- Don't trust IronPulse summaries for exact figures. Verify against source articles.
- When a source is unreachable (Nature cookie wall, Google CAPTCHA), find a credible tech press summary with enough specificity.
- If a story sits near an anti-Elon guardrail and every outlet is covering it, it's probably not a good PhantomByte pick — too crowded, wrong framing.
- Deliver everything via Windows Desktop file path. Never dump outlines or articles directly into Telegram.