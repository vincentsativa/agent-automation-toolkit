# Outline Generation from Daily Data Files

Research phantom-byte.com's existing catalog, read the day's aggregated data files, and produce fact-based article outlines matched to the site's voice and coverage gaps.

## Trigger

- "generate article outlines from today's data"
- "research our brand, read the data files, produce outlines"
- "Research phantom-byte.com's existing content, then generate [N] article outlines from a local dataset"
- Any cron-job or interactive task that combines: (a) brand research on articles.phantom-byte.com, (b) reading local data files, and (c) producing multiple article outlines as .txt files delivered by email

## Data Source Files (Standard Daily Set)

The daily dataset typically contains 4-5 files in a directory like:
`C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES`

Standard files and their purposes:

| File | Source | What It Contains |
|---|---|---|
| `ironpulse-YYYY-MM-DD.txt` | IronPulse | Top 12-20 ranked AI news stories with Pinterest/X post copy |
| `tensorfeed_report_YYYY-MM-DD.txt` | TensorFeed | 15-25 deep story summaries, 3 emerging themes, 3-5 article recommendations with coverage gap analysis. Length varies (298-523+ lines); check `total_lines` in read_file response and re-read with offset only if truncated. |
| `blogwatcher-dump-YYYY-MM-DD.txt` | Blogwatcher / Hermes Agent | Editorial brief with 24 headlines, 5 unwritten themes with namediff against existing PhantomByte articles |
| `20-AI-News-Stories-YYYY-MM-DD.md` | Aggregated | Consolidated 20-story digest with Pinterest/X copy and 3-5 synthesis themes |
| `What are today's top 30 AI-related story headlines.md` | BuildFastWithAI | Ranked top-30 with 5 exposed themes, inline footnote citations, X/Pinterest copy. Uses `[^N]` footnote refs at bottom. |
| `Weekly_AI_News_Report_YYYY-MM-DD.txt` | TensorFeed weekly | 30 ranked stories with 5 themes, includes story numbers and dates |

Read ALL files. Each contains unique angles. The tensorfeed report is especially valuable for its "Three Emerging Themes" section and article recommendations. The blogwatcher dump contains "Unwritten Themes" with explicit namediffs against existing PhantomByte articles.

### Truncation Handling

File lengths vary by day. Always check the `total_lines` field in the `read_file` response. If the response says "truncated" or `total_lines` exceeds the read limit, follow through with a second `read_file` call using the offset. The tail of a long TensorFeed report contains the ordering rationale for its article recommendations, which explains WHY each recommendation was ranked where it was. This is valuable for understanding which angles are strongest.

Do NOT blindly assume truncation. On July 15, 2026 the TensorFeed report was only 298 lines and fit in a single read. Other files (ironpulse, blogwatcher, 20-AI-News-Stories, Top 30 Headlines) are typically under 350 lines and will not truncate.

## Phase 0: The Data Leads (Core Principle)

Before any outline work begins, internalize this: the data tells its own story. You do not decide what to write about. You read the data, synthesize it, see what it exposes, and write about that. Never pre-commit to an article sequence or outline before reviewing the day's data. The data from cron dumps lands in `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES` throughout the day. When Vinny says "let's see what the data says," he means it literally — the data picks the direction, not a plan made yesterday.

## Phase 1: Brand Research (Do Not Skip)

1. Navigate to `https://articles.phantom-byte.com`
2. Note the category counts from the sidebar. Key categories and counts as of July 15, 2026:
   - All Notes: 131
   - AI Infrastructure: 54 (heavily covered, largest category)
   - AI Engineering: 21 (well covered, up from 20)
   - AI Industry: 14 (moderate)
   - AI Security: 14 (moderate)
   - AI Policy: 6 (moderate)
   - AI Agents: 6 (growing, up from 5)
   - AI Research: 3 (critical gap, high-value)
   - AI and Society: 2 (thin)
   - AI Privacy: 2 (thin)
   - AI Ethics, AI and Investing, AI Collaboration, AI Strategy, AI News, Cloud Infrastructure, Industry News, Industry Report: 1 each (very thin)
3. Click into the latest article and read the full text to internalize Vinny's voice and structure:
   - Direct, declarative, conversational. No corporate language.
   - Short paragraphs (1-4 sentences). Break often.
   - Provocative openings that name the problem in plain terms.
   - `// SECTION TITLE` headers in caps (this is the actual format on the site).
   - Every claim grounded in specific facts, numbers, paper citations, dates.
   - KEY TAKEAWAYS section after the hook with `→` bullet points (confirmed on Note #124).
   - Teaches while arguing. Accessible to newbies, depth for pros.
   - Ends with a "Bottom Line" section.
   - Footer: *PhantomByte - phantom-byte.com*
4. Scroll the archive to note recent article titles and avoid topic overlap. Also click into at least one more article (e.g., an infrastructure-focused one like Note #124 "Your Agent's Harness Is Your Real Model") to confirm the full body structure, not just the opening.
5. Note the latest article number and date. As of July 15, 2026: 131 notes, latest is "Your Token Budget Is Coming" (AI Infrastructure, July 15, by Vinny Barreca). AI Engineering now at 21 articles.

### Browser Navigation Pitfalls (IMPORTANT)

- **Direct URL navigation to article pages returns 404.** URLs like `articles.phantom-byte.com/notes/your-agent-is-drowning-in-chat-logs/` do NOT work. You MUST navigate to the homepage first and click through from there.
- **Click-through to articles may fail entirely.** As of July 15, 2026, even the "Read Today's Note" button and the nested link refs inside headings (`@e49`, `@e81`) failed to navigate away from the homepage. The snapshot kept returning homepage content. The browser tool loop warning fires after 3 identical snapshots. When this happens, do NOT keep retrying clicks. Switch immediately to `browser_console` with a `querySelectorAll` query to extract all article titles in one shot (see `references/coverage-gap-analysis.md`). For the outline generation task, the homepage snapshot plus console title extraction is sufficient to understand the catalog and voice without reading any single article in full.
- **Use the link refs inside headings, not the heading refs themselves.** When clicking an article from the archive, the heading element ref (e.g., `@e18`, `@e72`) will NOT navigate. Use the nested `link` ref inside the heading (e.g., `@e49` for the latest article, `@e81` for the second article). These are the actual `<a>` elements that trigger navigation.
- **The `// LATEST` pinned article** at the top of the homepage has its own link ref separate from the archive list. Click the heading link ref to open it.
- **browser_snapshot(full=true) may truncate** on article pages (284+ lines). The truncated portion contains the lower body sections and footer. For the outline generation task, reading the first 60% of the article (hook, structure, section headers, first few sections) is usually sufficient to internalize the voice. You do not need to read every article end to end during brand research.
- **Tool loop warning fires after 3 identical browser_snapshot calls.** If scrolling does not change the snapshot content, switch to browser_console extraction immediately. Do NOT repeat browser_snapshot more than twice on the same page state.

### Em Dash / Dash Contradiction (IMPORTANT)

There is a known contradiction between PhantomByte skills on dashes:
- `phantom-byte-writing-style` says: NO dashes of ANY kind (no em dashes, no en dashes, no hyphens used as dashes). Rewrite sentence structure to use commas, periods, colons, semicolons, or parentheses.
- `phantombyte-content-writing` says: Use em dashes in section headers (`## [SECTION NUMBER] - [SECTION TITLE]`) and in the Quick-Start section.

For OUTLINE generation specifically: the outlines are working documents for Vinny, not published articles. Use commas and periods in outline prose. If a section separator is needed, use `//` or a colon. Avoid all dash forms to be safe. When the outline is later written into a full article, the `phantom-byte-writing-style` rules apply in full (no dashes of any kind).

## Phase 2: Read Source Data

Read every file in the data directory. Extract:

- **Specific facts with sources:** model names, prices, benchmark scores, company names, dates, paper citations
- **Emerging themes:** TensorFeed's "Three Emerging Themes" section, the 20-AI-News-Stories "Three Themes" section, and the Weekly Report's "Five Themes" section are all gold
- **Coverage gaps:** TensorFeed's "Coverage Gap Analysis" section maps directly to the site's category counts
- **Recommended angles:** TensorFeed's "Article Recommendations" and blogwatcher's "Unwritten Themes" often suggest titles and specific angles with namediffs
- **Cross-file patterns:** When the same story appears in 3+ files, it is a high-confidence anchor for an outline

Do NOT skim. The blogwatcher dump contains "Unwritten Themes" that connect 2-3 stories into a synthesis no other file captures, with explicit namediffs against specific published PhantomByte articles.

## Phase 3: Generate Outlines

Distribution rule from the task spec:
- 1-2 outlines must be engineering/infrastructure-focused (authority angle: "you can't do anything in AI without solid engineering")
- Remaining outline(s) must cover a different AI angle (industry, security, tools, policy, society, etc.)

### Topic Selection Strategy

1. Check the coverage gap analysis in the data files. Prioritize thin categories (AI Agents, AI Research, AI and Society).
2. Look for cross-file themes that appear in 2+ data files. These are high-confidence angles.
3. Check the blogwatcher "Unwritten Themes" section for namediffs against existing articles.
4. Engineering/infrastructure outlines should connect to existing PhantomByte articles where possible (e.g., "extends #124" or "builds on #123") to reinforce the serial ecosystem.

### Outline File Structure

Each .txt outline file is a standalone working document. It does NOT need to use `// SECTION TITLE` header format internally. The outline is a planning document for Vinny, not a draft of the published article. Structure it for readability and traceability.

Recommended format (confirmed July 13-14, 2026):

```
ARTICLE OUTLINE #[N] — [ENGINEERING/INFRASTRUCTURE or INDUSTRY/POLICY etc.]
===================================================

TITLE: [Punchy, specific, benefit-driven, second person]
SUBTITLE: [One line clarifying the angle]

CATEGORY: [AI Engineering / AI Infrastructure / AI Policy etc.]
ESTIMATED LENGTH: [word count range]
LEVEL: [Intermediate / Beginner]
READ TIME: [~N min]

OPENING SUMMARY (for the editor's review):
[2-6 sentences. Must lead with concrete numbers, events, or data points from the source files.
Frame the problem in plain terms. This is the article's opening paragraph. More detailed than
the previous DECK format; gives Vinny the full pitch in one block.]

IN THIS ARTICLE:
→ [Section 1 name]
→ [Section 2 name]
→ [Continue for all sections]

[For each section, use the "Traceable Facts" format (confirmed July 14, superior to
the previous "Content notes" approach for traceability):]

SECTION [N]: // [SECTION TITLE]
Traceable facts from source data:
- [Fact with specific number/name/date] ([source file name, Story #])
- [Fact] ([source file name, Story #])
- [Continue listing every fact this section uses, each tagged with its source]

Angle: [1-2 sentences explaining the narrative purpose of this section. Why it exists
in the article and what the reader learns from it.]

[Repeat for each section]

SECTION [N]: // THE BOTTOM LINE
[Closing paragraph, not bullets. Must challenge the reader or land a specific point.
Connects back to the "you can't do anything in AI without solid engineering" authority
angle where relevant.]

SOURCES CITED (all traceable to provided data files):
- "[Story title]" — [Publication] ([data file name, Story #])
- [List every source this outline draws from, with the data file and story number]
```

Key improvements in the July 14 format over the July 13 format:
- "Traceable facts from source data" subsection under each section header lists the
  EXACT facts and which data file/story number each comes from. This makes
  fact-checking trivial and ensures nothing is fabricated.
- "Angle:" paragraph after the facts explains the narrative purpose of each section.
- THE BOTTOM LINE is a closing paragraph, not bullets. Matches the site's actual style.
- SOURCES CITED section at the end uses the story title and publication name, not just
  URLs. More readable for Vinny.
- No "Note #[N] Candidate" line (the note number is assigned at publication time, not
  outline time).

### Key Requirements

- Every claim must be traceable to a specific source file. No fabricated claims or unverified stats.
- The DATA SOURCES section at the end of each file is mandatory. It lists every source with the data file it came from and the date.
- Voice must match PhantomByte: direct, declarative, short paragraphs, concrete evidence, "Bottom Line" close.
- Written to teach: accessible to newbies, depth for professionals.
- No AI-isms: no "leverage," "synergy," "delve," "dive deep," "furthermore," "it's worth noting," "in today's rapidly evolving landscape."
- Each outline should connect to existing PhantomByte articles where relevant (serial ecosystem). Name the Note number explicitly (e.g., "Connects to PhantomByte Note #124").
- Titles should be second person where possible ("Your Agent's..." not "How Agents..."). This matches the site's established pattern.

## Phase 4: Save and Deliver

1. Create 3 separate `.txt` files, one per outline
2. Save to the same data directory: `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\outline[N]-[slug].txt`
3. Report the FULL Windows path for each file (e.g., `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\outline1-structured-memory.txt`)
4. Email all 3 files in a SINGLE email to `hello@phantom-byte.com`
   - Subject: "Three Article Outlines from Today's Data - [Date]"
   - Attach all 3 .txt files (not three separate emails)
   - Body: brief summary of each outline (title, angle, key data sources)
5. Use the email-sender skill (IONOS SMTP, smtp.ionos.com:587)
6. Confirm all files were attached and sent in the final response

## Outline Quality Checklist

- [ ] Every claim is traceable to a specific source file (check the DATA SOURCES section)
- [ ] No fabricated stats, prices, or benchmark scores
- [ ] Voice matches PhantomByte: direct, skeptical, concrete numbers, short paragraphs
- [ ] Each outline teaches something concrete the reader can use
- [ ] Engineering/infrastructure angle is present (1-2 outlines)
- [ ] Non-engineering angle is present (1+ outline)
- [ ] Category distribution fills a real coverage gap on the site
- [ ] DATA SOURCES section included at the end of each file
- [ ] Each outline connects to existing PhantomByte articles where relevant (name the Note number)
- [ ] Titles are second person where possible ("Your Agent's..." not "How Agents...")
- [ ] All 3 files attached to a single email
- [ ] Full Windows file paths reported in the final response

## Session Notes (July 13, 2026)

- The data directory had 4 files (20-AI-News-Stories, blogwatcher-dump, ironpulse, tensorfeed_report). All were read in a single batch (parallel read_file calls).
- The latest article (#127, "Your Agent Is Drowning in Chat Logs", AI Agents category) was read in full. Also read Note #124 ("Your Agent's Harness Is Your Real Model", AI Infrastructure) to confirm body structure including KEY TAKEAWAYS section with `→` bullet points.
- Category counts on the site as of July 13: All Notes 128, AI Infrastructure 54, AI Engineering 20, AI Industry 14, AI Security 14, AI Agents 5, AI Policy 6, AI Research 3, AI and Society 2, AI Privacy 2, AI Ethics 1, AI and Investing 1, AI Collaboration 1, AI Strategy 1, AI News 1, Cloud Infrastructure 1, Industry News 1, Industry Report 1.
- The blogwatcher dump's "5 Unwritten Themes for PhantomByte" section and the TensorFeed report's "Five Article Ideas" section were both highly valuable. The TensorFeed report's coverage gap analysis (Part 3) directly mapped to the site's category counts.
- Cross-file patterns: The White House AI power pledge appeared in 3 files (IronPulse, TensorFeed, 20-AI-News-Stories). The OpenAI safety exodus appeared in 3 files (IronPulse, TensorFeed, blogwatcher). The Apple v. OpenAI lawsuit appeared in 3 files. These high-confidence stories anchored 2 of the 3 outlines.
- The TensorFeed report's "Three Emerging Themes" (Agent Reliability Through Architecture Not Scale, AI Energy/Infrastructure Crisis, Agentic AI Regulation) directly informed the outline topic selection: Theme 1 anchored the Toolmetry engineering outline, Theme 2 anchored the energy infrastructure outline, and Theme 3 anchored the AI AGENT Act policy outline.
- Outline format used: DECK (opening hook) + IN THIS ARTICLE (bullet list) + numbered SECTION headers with "Content notes:" bullets + THE BOTTOM LINE + DATA SOURCES + ESTIMATED LENGTH/TARGET AUDIENCE/READING LEVEL. This format worked well and was confirmed as the recommended structure for future sessions.
- Outlines produced: (1) "Your Agent's Tool Descriptions Are Costing You 66% of Your Accuracy" (AI Engineering, Toolmetry via TensorFeed), (2) "The $50 Billion Question: When AI Data Centers Meet the Grid" (AI Infrastructure, White House/Meta/SK Hynix/Sunrun via IronPulse+TensorFeed), (3) "The AI AGENT Act: Washington Just Defined What an Agent Is" (AI Policy, Senator Warner's bill via TensorFeed).
- All 3 files saved to the source data directory with descriptive filenames (outline1_tool_descriptions_engineering.txt, outline2_energy_infrastructure.txt, outline3_ai_agent_act_policy.txt). Email sent successfully with all 3 attached.

## Session Notes (July 14, 2026)

- Data directory had 5 files (20-AI-News-Stories, blogwatcher-dump, ironpulse, tensorfeed_report, "What are today's top 30 AI-related story headlines.md"). The 5th file was a ranked top-30 with 5 exposed themes and inline footnote citations. All 5 read in a single parallel batch.
- Category counts updated: All Notes 130 (up from 128), AI Agents 6 (up from 5), AI Infrastructure 54, AI Engineering 20. The latest article is #128 "Your Agent's Tool Descriptions Are Costing You 66% Accuracy" (AI Engineering, July 14). Note: the site displays "NOTES: 130" in the banner but article cards show #128 as latest, suggesting 2 notes are in draft or the count includes unpublished.
- Browser navigation: direct URL navigation to article pages (e.g., `articles.phantom-byte.com/notes/your-agent-is-drowning-in-chat-logs/`) returns 404. Must navigate to the homepage first and click through via the link refs (`@e49`, `@e81`, etc.). The heading refs (`@e18`, `@e72`) do NOT work for click-through; use the nested link refs inside headings.
- The TensorFeed report had 523 lines (truncated at 500 on first read). Required a follow-up `read_file` with `offset=501` to capture the full ordering rationale for article recommendations. Always check for truncation on TensorFeed reports, which are the longest data file.
- Outline format refinement: This session used an improved structure with explicit "Traceable facts from source data:" subsections under each section header, listing the exact facts and which data file each comes from. This is MORE traceable than the previous "Content notes:" approach and is now the recommended format. Each section also includes an "Angle:" paragraph explaining the narrative purpose of that section. The structure:
  ```
  SECTION [N]: // [SECTION TITLE]
  Traceable facts from source data:
  - [Fact] ([source file, story #])
  - [Fact] ([source file, story #])
  Angle: [1-2 sentences explaining the narrative purpose]
  ```
- Outlines produced: (1) "Your Data Center Just Became a Political Problem" (AI Infrastructure, New York moratorium/xAI/Google/NVIDIA via all 5 files), (2) "Your AI Token Budget Is Coming" (AI Infrastructure/Engineering, Meta token caps/Reflection/DeepSeek/open models via 4 files), (3) "The Legal Bill for the AI Boom Is Coming Due" (AI Industry/Security, Apple vs OpenAI/Meta layoffs/Google publishers/Illinois/DOGE via 4 files).
- Distribution: 2 engineering/infrastructure + 1 industry/legal. The legal outline synthesized 5 distinct lawsuits from the data into a single "pattern" article, which is a strong approach for non-engineering outlines: find the connecting thread across multiple stories that individual news coverage misses.
- Filenames used: outline1_data_center_moratorium.txt, outline2_token_budgets.txt, outline3_legal_reckoning.txt. Short, descriptive slugs without category prefixes (previous session used category prefixes like `_engineering`). Both naming approaches are fine; the key is descriptiveness.
- Email subject: "3 Article Outlines from Today's Data - July 14, 2026". SMTP confirmed with debug output showing all 3 attachments encoded and sent successfully.

## Session Notes (July 15, 2026)

- Data directory had 5 files: "Top 30 AI Story Headlines (July 15, 2026).md", "20-AI-News-Stories-2026-07-15.md", "blogwatcher-dump-2026-07-15.txt", "ironpulse-2026-07-15.txt", "tensorfeed_report_2026-07-15.txt". All read in a single parallel batch.
- Category counts updated: All Notes 131 (up from 130), AI Engineering 21 (up from 20). Latest article is "Your Token Budget Is Coming" (AI Infrastructure, July 15, by Vinny Barreca). AI Infrastructure remains at 54.
- **TensorFeed report was only 298 lines this session (NO truncation).** The reference above says "The TensorFeed report is often 500+ lines" but length varies by day. Always check the `total_lines` field in the read_file response. Only re-read with offset if the response says "truncated" or `total_lines` exceeds the read limit. Do NOT blindly assume truncation.
- **Browser click-through to articles still does not work.** Even the "Read Today's Note" button (`@e19`) and the link inside the latest heading (`@e49`) failed to navigate away from the homepage. The snapshot kept returning the homepage content. The reliable fallback is `browser_console` with a `querySelectorAll` query to extract all article titles in one shot (see `references/coverage-gap-analysis.md`). Do NOT waste turns repeating `browser_snapshot` or `browser_click` on article links that fail to navigate.
- **Console title extraction returns duplicates.** The selector `document.querySelectorAll('article h3, article h2, .article h3, h3 a')` returns each title twice because `h3` and `h3 a` overlap (the `a` is nested inside the `h3`). Either deduplicate in JavaScript with a Set, or use `h3 a` alone to get unique titles. The dedup pattern:
  ```javascript
  JSON.stringify([...new Set(Array.from(document.querySelectorAll('article h3 a, article h2 a')).map(el => el.textContent.trim()).filter(t => t.length > 5))])
  ```
- **Outline format deviation (PITFALL).** This session's outlines used the older "Content notes" bullet format instead of the "Traceable facts from source data" format confirmed as superior on July 14. The older format lists facts as prose bullets without source tags, making fact-checking harder. Future sessions MUST use the "Traceable facts from source data" format with per-fact source attribution. If the outline format reverts to untraceable prose bullets, that is a regression.
- Outlines produced: (1) "Your AI Factory's Real Ceiling Is a Power Plant, Not a GPU" (AI Infrastructure, NY moratorium/Blackstone/xAI/NVIDIA/SKorea via all 5 files), (2) "Your Agent Has Too Much Freedom: The Case for Least Autonomy" (AI Security/Engineering, arXiv Least Autonomy paper/Grok codebase uploads/OpenAI file deletion/Codex encrypted comms via 4 files), (3) "The Model Is Not the Product: Why AI Implementation Just Became a Trillion-Dollar Business" (AI Industry, Anthropic/Blackstone Ode JV/Chinese model cost arbitrage/Bonsai 27B/Meta agent platform via 5 files).
- Distribution: 2 engineering/infrastructure + 1 AI industry. The industry outline used the "business model shift" angle (implementation as the new product layer) rather than a lawsuit-synthesis angle. Both approaches work for the non-engineering outline.
- Filenames used long descriptive slugs: `outline1-your-ai-factorys-real-ceiling-is-a-power-plant.txt`, etc. This is fine but creates very long paths. Short slugs (e.g., `outline1_power_plant.txt`) are equally valid and easier to reference.
- Email subject: "3 Article Outlines from Today's Data Files - July 15, 2026". SMTP confirmed with debug output showing all 3 attachments (9,243 / 10,803 / 11,928 bytes) and message ID `1MMX5X-1wQW0T2g6x-00Xzem`.
- **Tool loop warning fired** after 3 identical `browser_snapshot` calls. When snapshot returns truncated content and scrolling does not change the result, switch immediately to `browser_console` extraction. Do NOT repeat `browser_snapshot` more than twice.