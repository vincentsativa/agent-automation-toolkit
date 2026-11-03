---
name: keyword-research-seo
description: Do keyword research for PhantomByte articles using Google Trends — identify high, medium, and low competition targets with search volumes, trends, and strategic recommendations. Email report to Vinny.
trigger: "vinny asks for keyword research, SEO research, keyword targets, what keywords to target for an article"
---

# Keyword Research & SEO Workflow (PhantomByte)

## Trigger Conditions
- Vinny says "do keyword research" or "keyword targets" for an article
- Vinny asks "what keywords should I target" or similar
- Any request to analyze SEO/search terms for a written piece

## Email Target
- **To:** hello@example.com
- **Subject:** "Keyword Research: [Article Title]"

## How The Report Is Consumed (read before writing a single field)

Vinny hands the finished report to his coding agent, who uploads the article to the site. Every recommended slug, meta description, tag, and URL is a value that gets PASTED VERBATIM, not a suggestion for a human to interpret. Write each one as a literal string and verify it before it ships.

Timing, confirmed by Vinny: keyword research runs the day before publication and the article posts the following morning. Write the CRITICAL WINDOW advice for a next-day publish, and treat the Trends snapshot as one day ahead of the live page.

## HARD RULE: NEVER INSTRUCT AN EDIT TO VINNY'S FINISHED ARTICLE (standing order, Oct 15 2026)

The report is a research instrument, never an editing order. Any line in it that tells an agent to change prose Vinny has already written is a failed report, and a violation of his explicit standing order.

- Metadata only on an existing article. URL slug, meta description, tags, and link targets are the only things a report may recommend for a piece that already exists. Prose, structure, paragraph order, opening lines, and quotation formatting are untouchable. Report the measurement, name the consequence, stop.
- **DO NOT TOUCH MY TITLE. EVER. PERIOD. FULL STOP.** (Vinny's standing order, Oct 19 2026, stated in exactly those words.) The report carries his title verbatim and stops there.
- Every GEO checklist item, required-term placement, blockquote request, statistic request, table request, and "terms in the first 100 words" line is WRITE-TIME advice. It appears in a report only when the article does not exist yet, and it is addressed to the writer before the draft, never to an editor of a finished or published draft.
- Never phrase an edit as optional, suggestive, or deferential ("say the word if you want it edited" is still an instruction to edit). Never label his prose a defect, a miss, or an omission that needs correcting.
- Cite only rules that actually exist in the loaded skills. Never invent a policy, a ban, or a "golden rule" to justify a recommendation. A fabricated rule is a second failure on top of the first.
- When a measurement conflicts with his existing prose, the prose wins. State the reading, state the tradeoff in one line, and leave the decision to him.

## Prerequisite Skill

Before starting research, load the `phantombyte-distribution-seo` skill with `skill_view(name='phantombyte-distribution-seo')`. Its GEO and E-E-A-T framework informs the keyword strategy: high-value targets are terms that signal Experience, Expertise, Authoritativeness, and Trust, and the report should recommend content structures (quotations, statistics, citations) that boost AI search visibility.

## Research Steps

### 1. Extract concepts from available material
**If a finished article exists:** Read the full article text. Extract core concepts, unique terms, and any brand-new phrases the author coined. These coined terms are the highest-value targets (zero competition, first-mover advantage). This is a measurement pass only: read his prose as the fixed input, never as something to revise.

**If only a topic/title/outline concept exists (no full article yet):** Extract keywords from:
- The working title and subtitle
- The proposed angle or "Why" statement
- Likely subject matter, tools, frameworks, or brands the tutorial will cover
- Any coined or branded phrases in the concept description

In topic/outline mode, expect fewer concrete coined terms upfront. Run the research anyway — the Trends data will reveal which adjacent terms have traction and may reshape the final title or H2 choices.

### 2. Google Trends analysis
Navigate to `https://trends.google.com/trends/explore` and run queries in batches of up to 5 terms per URL, targeting US, Past 12 months, Web Search.

Design your own batches of up to 5 terms per URL based on the article's actual keywords. Group by theme:

Batch 1 - Core article concepts (the big umbrella terms, unique coined terms, paper names)
Batch 2 - Adjacent/benchmark terms (benchmarks cited, vendor names, frameworks)
Batch 3 - Niche/defense/ecosystem terms (the specific technical terms from the article: defense strategies, technical mechanisms, uncommon frameworks, governance terms, OIDC/SLSA jargon). Not limited to hardware, whatever is specific to this article's technical depth.


EXAMPLE for an inference-architecture article:
- Batch 1: `test-time scaling`, `best-of-N sampling`, `LaneRoPE`, `inference-time compute`, `AI inference architecture`
- Batch 2: `Mixture-of-Experts agentic coding`, `ITBench-AA`, `agentic AI benchmark`, `collaborative inference`, `k8s SRE AI`
- Batch 3: `NVIDIA Dynamo`, `AI factory`, `Laguna model`, `NVIDIA GB300`, `parallel reasoning AI`

### 3. For each Trends result, capture:
- The "Average" value shown in the table (higher = more volume)
- The trend direction (rising, flat, seasonal, spiky)
- The relative position vs other terms

### 4. Classify into three tiers:

**TIER 1: HIGH COMPETITION (Avg 25+ on Trends)**
- Umbrella terms with strong volume
- Lots of entrenched players (enterprise vendors, major pubs)
- Use sparingly, primarily as metadata/seo umbrella
- A run can legitimately have NO Tier 1 term, and reporting one that does not exist is worse than reporting none. When nothing reaches the band, keep the section and write NONE, then state the run's largest reading and its index so the writer can see the ceiling: "No term reached Avg 25; the largest was distributed training at avg 17, and the run's only 100 peak is a one-week spike on a flat 14 baseline." Add the strategic consequence in one line (the coined units carry the strategy because there is no umbrella term to ride). Never delete the Tier 1 heading on a low-volume run, because its absence reads as an unfinished report.

**TIER 2: MEDIUM COMPETITION (Avg 10-25 on Trends)**
- Good volume, growing interest
- Fewer entrenched players
- PRIMARY TARGETS for article: optimize URL and metadata.

**TIER 3: LOW/NO COMPETITION (Avg 0-9 on Trends)**
- Brand new or coined terms
- Zero SERP competition
- CRITICAL TARGETS — first-mover advantage, limited window
- Typically: paper names, coined phrases, benchmark names
- The 5-9 band is where spiky low-week-count terms and plain descriptors land, so read `nz_weeks` and `full53` beside the Average before tiering: 5 nonzero weeks out of 53 is a blip, 30 nonzero weeks is a real baseline. Tier 3 by volume is not Tier 3 by importance. The article's own coined unit and its plain-English head term belong in the PRIMARY targets even when they read in this band, because exact-phrase fit with zero competition beats a bigger number owned by another field. Tier on the normalized index, then promote on headability, and state which property set each placement. When the report tiers on a normalized index instead of raw Averages, scale the band boundaries by the same factor and write the scaled bands into the methodology: with the reference term set to 100, Tier 1 is 96 and above, Tier 2 from 38 to 95, Tier 3 below 38. Reading index figures against the raw 25 and 10 bands mis-tiers every term by nearly 4 to 1 and turns a healthy Tier 3 term into a reported Tier 1. Those scaled bands hold only when the reference term is itself a Tier-1-volume term, so the 100 represents real demand. When the calibration reference is a micro-volume term instead (a niche technical phrase reading raw 3 in a batch where its comparable peers read 1 to 41), do NOT scale the bands: report every converted reading in that batch's own raw units and tier on the standard 25 and 10 thresholds, stating in the methodology that the scale is the like-for-like calibration batch and naming the reference term. Scaling the bands to 96 and 38 around a micro reference would print a term with 3 percent of the batch's volume as a reported Tier 1.

### 5. Identify the unique angle
What does THIS article have that competitors don't? (e.g., security hook vs academic hook, vendor angle vs engineering angle). This is the differentiator for SEO strategy.

### 6. Identify the critical window
New papers/benchmarks/terms typically get picked up by major pubs (VentureBeat, Ars Technica, Wired, The Register) within 4-6 weeks. State the window explicitly.

### 7. Compile the report
Write a full report to the user's home directory (`~` on Linux, `$HOME` on Windows Msys) named `keyword_research_[shortname].txt` containing:
- Methodology note
- Tier 1 breakdown (terms, volume, competition, use)
- Tier 2 breakdown
- Tier 3 breakdown
- Strategic recommendations (primary, secondary, tertiary)
- Additional notes (backlink opps, internal linking, timing)

### 7b. FORMAT THE REPORT (MANDATORY — DO NOT SKIP)
Run the deterministic formatter on the compiled report BEFORE emailing it:

```bash
python "~/AppData/Local/hermes/scripts/format_keyword_report.py" "~/keyword_research_<shortname>.txt" "~/keyword_research_<shortname>.txt"
```

This step exists because Article 193's report shipped malformed (Sep 16 2026):
the header collapsed onto one 114-char line, the title rule was 64 chars while
section rules were 80, METHODOLOGY used short `-` rules instead of `=` rules,
sections opened with a rule and had no closing rule, `--` was used as
punctuation, and three orphaned `URL:` labels dangled above their own links.
Hand-placing separators and hand-wrapping lines always fails this way. Never
skip the normalizer and never hand-fix the file.

The script enforces: every divider exactly 80 `=`; a closing rule under every
section title; header fields each on their own line; links left whole and
aligned under their own list item; `--` converted to `: ` (never a dash as
punctuation); no orphaned `URL:` labels; no doubled blank lines.

It enforces width on rules that EXIST and never creates a missing one. A report
written with no `=` rules at all still prints `clean:` and `lost=0 gained=0`, so
the gate is silent while the document ships with zero section separators. It
also does not collapse a duplicated pair. Write one rule above and one below
every section heading at write time, keep exactly one rule under the header
block, and after the run count the rule lines: two per section and nothing
adjacent. Verified output from a correct run reads `lines: N, longest prose
line: X chars` plus the two gate lines, and a `rules: {}` or `rules: {0}` reading
from your own inspection means none were written.

CRITICAL: the prose is UNWRAPPED on purpose. Every paragraph and list item is
one physical line and soft-wraps in the reader to fill the full window. Do NOT
re-wrap prose to 80 columns and do NOT "fix" long lines in a report. The
80-char limit applies ONLY to the `=` divider rules. Hard-wrapping the prose is
what made Article 193's report render as text across half the page (Sep 16
2026), and Vinny rejected it twice. The `longest prose line: N chars` figure in
the script output is expected and correct, not a defect.

It self-validates and prints a content-integrity check. You MUST read that
output before emailing:

- `clean:` on its own line = pass.
- `lost=0 gained=0` = pass. Any nonzero count means the formatter dropped or
  invented content; STOP and fix the script before sending anything.

Do not email a report until the formatter reports both `clean:` and
`lost=0 gained=0`.

### 7c. ADD THE EXACT PUBLISHING FIELDS BLOCK (MANDATORY, DO NOT SKIP)

The report goes to a coding agent that pastes its strings straight into the CMS, so every field the uploader needs appears as a literal, verified value and never has to be reconstructed from prose. Add an `EXACT PUBLISHING FIELDS` section immediately before TITLE NOTES containing Vinny's existing title copied verbatim from his draft, the URL slug, the meta description as one copy-paste string, the byline, and a pointer to the tag list.

**TITLE NOTES explains the measurement behind the title he already wrote, and nothing else.** It may say which terms that title carries, what the launch curve looks like, and which tier the terms in it sit in. It never proposes different wording, never calls his wording a tradeoff to reconsider, and never names a title the uploader could paste instead. If the measurement favors terms his title does not carry, state where those terms go (meta description, body, tags, links) and stop.

**Count the meta description on the FINAL string and print the number.** The `(150-160 chars)` label is a claim about the content, not decoration. A report once shipped a 165-character description under a 150-160 label because the description was edited after it was written and nobody recounted. Compute the length with a tool, adjust the wording until it lands inside the band, and label the section with the real count, for example `(150-160 characters, verified 150)`. Never estimate a character count by eye and never edit the description after counting it.

**Keep counts consistent across the whole report.** When one section states how many sources the article cites and another lists verified URLs, the numbers must agree, or the section must say explicitly what each one counts (the article's own source list versus the report's verified live URLs). A report that says "cites six sources" beside eight listed URLs reads as an error to whoever pastes it, and the uploader is the one who sees it first.

**A draft's own SOURCES list often names an internal research pipeline, and that is not a citable public source.** Drafts generated from the daily Trend research carry entries like the TensorFeed daily report and the Blogwatcher daily dump beside the real paper and trade-press URLs. Those are internal pipelines, not pages a reader can open, so they do not count toward the verified-URL total and a published source list must not carry them. State the split explicitly: name how many entries the draft's source list holds, how many are public and verified, and which entries the writer should drop or replace with the public story they point to. Silently counting them inflates the number the uploader sees.

**Write the required-in-opening terms as their own line.** When the report says the first 100 words must contain certain terms, state that as a separate instruction line rather than appending it to the title line, so a paste of the title field cannot swallow it. This line exists only on a PRE-DRAFT run. If the article already exists, the report states which of those terms the opening already carries and stops; it never asks for the opening to be changed (see the HARD RULE).

### 7d. EIGHT TRAPS THAT BREAK THE REPORT AFTER IT IS WRITTEN (CHECK ALL EIGHT)

**1. The formatter MERGES the EXACT PUBLISHING FIELDS block into one physical line.** The unwrapper only starts a new line for a known field prefix (`Date:`, `Article:`, `Author:`) and for numbered or bulleted items. The publishing-fields lines (`Title and H1...`, `H1...`, `URL slug:`, `Meta description...`, `Byline:`, `Required terms...`, `Tag list:`) match none of those, so they collapse into a single 900-character line, and the uploader's paste of the title field then swallows the slug, the meta description, and the byline behind it. Fix: put a BLANK LINE between every field in that block. A blank line ends a block, so the unwrapper leaves each field on its own line, and the block survives re-formatting. Writing them on consecutive lines does not survive. The same rule applies to the report header: `Title:`, `Byline:`, `Date:` and any other header field written on consecutive lines merge onto shared physical lines (`Title: ... Byline: ...`, `Date: ... Piece: ...`), so a paste of the title swallows the byline. Put a blank line between every header field too, run the formatter again, and re-read the first twelve lines. The report label (for example `KEYWORD RESEARCH REPORT: ARTICLE 226`) and the article subtitle below it merge into one line for the same reason, so give them a blank line between them as well. A merged label reads as a title that begins with the internal file label, which is the first thing the uploader sees. After running the formatter, read the block back and confirm each field is its own line; the `longest prose line: N chars` figure will be dominated by a collapsed block when this has happened.

**2. Every count in the methodology must be computed from the saved JSON, never estimated.** Terms measured, batches run, and how many related-query clusters came back populated are all facts sitting in the run's output JSON. Read the file and count them before writing the methodology line. A plausible-looking estimate ("forty-four terms across eight batches") can be wrong in both numbers and a reader who compares it against the tier list sees an error. Count unique `term` keys for the term total, count the batch keys for the batch total, and count how many batches returned a payload carrying a `term` key versus an `error` key. Do the same for any claim the report makes about how many clusters were empty, unread, or polluted.

**3. Any edit made after the last formatter run invalidates both the formatting and the meta-description count.** The character count is a claim about the final string, so patching the report by hand (fixing a count, adding a source note, correcting a field) means the string may have changed and the label may now be false. Re-run the formatter and re-count the description after every hand edit, and only then email. The formatter is idempotent on a clean file, so re-running it costs seconds.

**4. Restructuring the report after a first write makes `write_file` refuse, and the fix is to delete the file, not to name a second one.** `write_file` blocks an overwrite when this task has not read the file's full current content, and that guard fires even on a report this same session just wrote whenever the write is not the immediately preceding operation on it. The reflex fix of writing to a fresh filename leaves two report files in the home directory, and the one with the canonical name is the stale one. For a file this session authored, run `rm -f` on the target path from `terminal` and then write: a path that no longer exists is a create, so the guard cannot fire, and the canonical name holds the final version. Reserve the fresh-filename rule for files other agents own.

**5. Consecutive non-blank lines inside a section collapse into ONE line, so paragraphs written as consecutive lines become a single giant paragraph.** The unwrapper joins every line of a block into one physical line per item, and it only starts a new item at a numbered line, a bullet, a URL, or a `Date:` / `Article:` / `Author:` prefix. A METHODOLOGY written as six consecutive lines therefore ships as one 2,000-character block. Fix: put a BLANK LINE between every paragraph you intend to stand alone, before running the formatter, exactly as trap 1 requires between publishing fields. The `longest prose line: N chars` figure is the tell: a few hundred characters is one paragraph, a couple of thousand means paragraphs have merged, and the fix is one more formatter run after splitting them.

**6. A line that is a bare URL is indented to the content column of the last numbered item, so a standalone link picks up stray indentation.** The formatter aligns bare URLs under the nearest preceding numbered list item, which is right inside a links list and wrong for a single URL under its own section heading when a numbered section came before it. Fix: label the line (`Canonical URL: https://...`) so the formatter treats it as prose, and put a blank line after that label, or it merges with the sentence that follows it. Inside a numbered links list the opposite holds: the bare URL on its own line is the CORRECT form, its own line starts a new unwrap item so it stays whole, and the indent is what aligns it under its entry. Label only the standalone case, and write each links-list entry as the item text on one line with its URL on the next.

**7. A header line beginning with `Article:` or `Author:` is DUPLICATED into an orphan label.** The formatter's header pass splits on those two prefixes as field markers, so `Article: <title>` ships as a bare `Article:` line followed by the full `Article: <title>` line, and `Author: <name>` does the same. It passes `clean:` and `lost=0 gained=0` because the duplicate is an added token, not a lost one, so the integrity gate does not catch it. Write the header as `Title: <article title>` and `Byline: <name>` instead, keep `Date:` (it is a genuine field marker and stays on its own line), and read the first twelve lines back after the formatter run. Full rule in `document-delivery-formatting`.

**8. The tier list can end up shorter than the measurement, because a term gets discussed in STRATEGIC RECOMMENDATIONS and never tiered.** A report can name a term repeatedly in the primary and secondary target paragraphs while the numbered Tier 3 list skips it, and every count in the report then disagrees with the JSON by exactly the number of skipped terms. A term mentioned inside a recommendation is not a tier entry. Gate it mechanically before emailing: run `scripts/check_tier_completeness.py <trends.json> <report.txt>`, which prints the unique measured terms, the ones absent from the report, and the numbered entry count per tier section, and require the numbers to agree: unique terms measured equals total numbered tier entries. Fix a missing entry in its correct position, renumber the entries after it, then re-run the formatter (trap 3) before sending.

The gate also OVERCOUNTS and still prints `PASS`, so read the per-tier counts and not just the total. The script counts every line matching `^\d+\. ` as a tier entry until it reaches a line starting with `STRATEGIC RECOMMENDATIONS` or `CRITICAL WINDOW`. When those headings are missing, or sit after the BACKLINK OPPORTUNITIES and INTERNAL LINKING lists, every numbered link entry is counted as a Tier 3 term: a report with 26 tier entries prints `TIER 3 numbered entries: 32` and passes on `total >= unique terms` alone. Rule: write `STRATEGIC RECOMMENDATIONS` immediately after the last tier section and before any other numbered list, then require each section's count to match its own list (for example 2, 7 and 17 summing to 26). A total that is larger than the unique-term count is a section-ordering defect, not a healthy run.

A fourth numbered section is legitimate and still breaks the per-section reading: a `FLOOR TERMS AND UNPLACED READINGS` list placed between Tier 3 and STRATEGIC RECOMMENDATIONS is counted into Tier 3, so a run with 3 Tier 1, 9 Tier 2, 14 Tier 3 and 10 floor entries prints `TIER 3 numbered entries: 24`. That count is the checker's, not an error, and the gate still passes when the total equals the unique-term count. Require two things instead: every measured term appears in exactly one numbered section, and the report states the real split so the reader is not told the tier list is ten entries longer than it is. The cleanest shape is to fold floor terms and unplaceable terms INTO the numbered Tier 3 list with `floor, raw N` or `unplaceable, raw N` in their entry title rather than giving them a fourth section: the per-section count then equals that section's own list, the counts sum to the unique-term total exactly, and the qualifier in each title line keeps a zero-volume entry from reading as a missed opportunity.

### 8. Email it
Use the email-sender skill to send to hello@example.com with:
- Subject: "Keyword Research: [Article Title]"
- Body: Quick summary with primary targets, critical window, unique angle
- Body also states the metadata-only position in one line (that no sentence of the draft is proposed for edit) and repeats any source-list reading the report records, plus any link-target reading it records (a named prior article whose live on-page title differs from the headline the draft quotes), so the email and the attached report cannot be read as disagreeing
- Attachment: The full report file (brief body only, never the report text)
- Every number in the email body must come from the same source as the report's numbers, because the body and the attachment are read side by side. A body line that says "twenty terms measured" beside a report that says twenty-four is a defect the reader finds in ten seconds.
- If an email ships with an internal inconsistency, do not explain it in chat and stop: send a corrected copy immediately, with `(corrected)` appended to the subject, a first line that names exactly what changed and states that it supersedes the earlier send, the fixed attachment, and an IMAP readback proving the new attachment bytes and the changed content are in the inbox.

## Run Order and Timing Budget (READ THIS FIRST, BEFORE THE RESEARCH STEPS)

A keyword run is a 3 to 4 minute task. It took 21 minutes on Article 207 (Sep 30,
2026) because of five avoidable costs, and still 20 minutes after that because
the fixed cooldowns (8s per batch, 120s per retry, 3s per link) were sized for
the old DOM-scraping path, not the internal API. Each cost has a hard rule now.

**Drive the whole run from `scripts/kw_run.py`, not from ad hoc calls.** One
`browser_exec` call per phase, four phases total:

```python
exec(open(r"~\AppData\Local\hermes\skills\content-swarm\keyword-research-seo\scripts\kw_run.py", encoding="utf-8").read())
warm()                                   # 1 navigation, helpers, ONE proof read
run(BATCHES, OUT)                        # EVERY timeseries batch in this call
related(PAIRS, OUT_REL)                  # EVERY related-query pair in this call
verify(URLS, OUT_LINKS)                  # EVERY link in this call
```

**Probe the CDP port before `warm()`, because `warm()` cannot tell you the browser is not there.** A `browser_exec` call against a dead port fails at the harness level with `BU_CDP_URL=http://127.0.0.1:9223 unreachable` and burns 30 seconds of startup wait before it says so. One terminal call first:

```bash
curl -s --max-time 5 http://127.0.0.1:9223/json/version || powershell -Command "Start-Process -FilePath 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ArgumentList '--remote-debugging-port=9223','--user-data-dir=~\AppData\Local\chrome-kw','--no-first-run','--no-default-browser-check','about:blank'"; sleep 8; curl -s --max-time 5 http://127.0.0.1:9223/json/version
```

`Start-Process` detaches properly; a Chrome started from `terminal(background=true)` or `cmd //c start` can print `DevTools listening` and still be dead by the next call. Recovery detail lives in `browser-exec-recovery`.

**Rule 1: never spend a call on a sleep.** Article 207 burned 220 seconds in two
standalone cooldown calls. Cooldowns belong INSIDE the batch loop in `run()`,
where they cost wall time but no round trip.

**Rule 2: wait 45 seconds after a 429, never 70 or 120.** Measured (Oct 3
2026): the API path sustains 15+ back-to-back batches at 1-second spacing with
zero 429s, so a 429 is rare; when one lands, 45 seconds clears it. The driver's
gap is adaptive (1s default, x4 up to 8s only on sustained 429s), so a healthy
run never pays a cooldown and a throttled run backs off automatically.
`RETRY_WAIT = 45` is the default in the driver.

**Rule 3: warm() takes ~5 seconds.** One navigation, helper definition, and one
proof read absorbs the cold start. Measured per-call costs (Oct 3 2026): a
Trends batch costs 0.2-0.3 seconds, a related pair 0.1-0.2 seconds. Per-batch
wall time is dominated by the gap, which is why `GAP_BATCH = 1` and
`GAP_PAIR = 0.5` are the defaults. If `warm()` cannot get a clean read after one
45-second retry, the block is hard: say so rather than grinding through
retries.

**Rule 4: one call per phase, not one call per batch.** Article 207 split 19
batches across five calls and the related passes across four more. Every extra
call resends the conversation and the tab state; the driver writes each result to
disk as it lands, so a long single call loses nothing a split run would keep.

**Rule 5: size the batch list once, and put the highest-value terms in the first
batch.** The first batch is the one that survives a mid-run failure, so it holds
the article's core terms. Three to five terms per batch; no mega-term shares a URL
with technical terms (see the anchor-crush rule in `browser-exec-recovery`).

**Draft the batch list from the article's own QUICK KEYWORDS block, coined
phrases included, and probe the coined terms as their own all-zero batch.** A
finished draft usually ends with a QUICK KEYWORDS line, and every coined phrase
in it (the article's named units and decision rules) is a target the report must
carry a measurement for. Coined candidates belong together in ONE batch of
candidates only, because a batch whose members are all literal zero has no live
term for the relative index to normalize against, so a term that is genuinely all-zero stays at zero. That safety ends the moment one member has a single nonzero week: the index forces that one week to 100 and prints its batch-mates as 46- and 5-style averages that read like volume, when all they are is one week of demand. Read `nz_weeks` in the same breath as the Average in every coined batch, and treat `nz_weeks = 1` as a brand-new term on its launch spike whatever number it printed. Never park a live, low-volume term you care
about in that batch (it becomes the lone live member, its peak is forced to 100,
and its number is meaningless in the flattering direction).

**A coined batch whose members have MANY nonzero weeks is not a coined batch, and its own-batch Averages must never be tiered.** The failure mode: three coined phrases came back at 21, 49 and 13 in their own batch, which reads as real demand, while the same three read 2, 3 and 1 beside a live anchor at 26. Because the relative index normalises to the batch's largest member, a batch of three inherited-meaning phrases simply re-expresses their ratios to each other and multiplies every one by whatever the top member's true volume is; the numbers can be 10 to 20 times the like-for-like read and nothing in the payload flags it. `nz_weeks` in the twenties or higher is the tell that the wording already lives in the world under another meaning, so the coinage owns none of that volume. Re-read every coined phrase beside a live anchor before it is tiered, report the like-for-like figure as the magnitude and the own-batch figure as shape only, and when both related-query lists are empty say plainly that the volume belongs to an inherited meaning, so the term is body-and-tag use and never the H1.

**If the coined candidates only surface while writing the report, relaunch the
browser and run ONE all-zero probe batch rather than shipping them as
unmeasured.** The driver supports this directly: `warm()` then `run(COINED, OUT)`
in a single `browser_exec` call, against a fresh JSON path. Two constraints: do
all Trends work for that probe before any link verification, because `verify()`
moves the tab off the `trends.google.com` origin and wipes the helpers, and close
and verify the browser again afterward (remaining: 0 plus the port probe).
Labeling a draft's own coined phrase as "not measured this run" is the failure
this prevents, because the coined unit is the piece's flagship target and the
writer treats the label as a reason to demote it.

**Plan the bridge overlap while the batch list is still being drafted, not at
analysis time.** Any batch meant to be tiered against the others must share at
least one live term with another batch, because a shared term is what converts
one batch's units into the other's (see the chained-index rule below). Two
batches drafted with no shared term are unreconcilable: their numbers can only be
reported own-batch, and noticing that after the run costs a whole extra
calibration batch. Before running, check the drafted list for at least two
independent bridges and add one live overlap term to any batch that has none.

**A bridge batch that carries a dominant anchor alongside the terms being converted proves NOTHING about those terms, so never build the conversion that way.** The bridge term's stability (identical Average in both batches) certifies the bridge term's own magnitude and nothing else. Inside the bridge batch the anchor crushes every batch-mate to a floor, so the factors computed from them disagree wildly: a measured bridge carried one term at 45 in both batches, exactly, while the four terms being transferred came back about 3.1x lower than their peer batch with factors spread from 2.75 to 3.4. That spread is anchor-crush noise dressed as a conversion, and averaging it produces a scale nobody measured. Design the bridge batch so the terms being converted sit within a few times the bridge term's volume, or accept that it converts only itself, and when a stable bridge does land beside crushed batch-mates, report the bridge reading as proof of that term's magnitude and take the other terms' magnitude from their own comparable batch instead. Check the spread inside every calibration batch before you use a single factor from it: when its top member is more than about 4x its next member, that batch is an anchor batch and converts only itself, whatever stability its bridge showed.

**Rule 6: keep related-query pairs at TWO terms.** Three-term related calls
repeatedly returned `Runtime.evaluate timed out` and left the helper undefined
for the next call, costing more than the pair count saved.

**Rule 7: batch the link verification too.** Every backlink and every internal
link goes into ONE `verify()` call with title and body text read back per URL. A
scripted 200 is not verification and neither is a slug that looks right. The list
must be COMPLETE before the browser work for the run ends, and that includes the
external authority citations the BACKLINK section needs (government frameworks,
standards bodies, official documentation) alongside the article's own arXiv and
trade-press sources. Derive the internal-link candidates from the site sitemap
with a non-browser `curl` first and pick the external pages from the article's own
concepts, then verify every URL in one call and only then run the kill script.

The main-domain sitemap is navigation only; the article index is the content
subdomain. Harvest candidates by grepping the article sitemap against the
article's own themes, which is one command and returns a handful of real targets
out of a couple hundred pages:

```bash
curl -s https://articles.phantom-byte.com/sitemap.xml -o sitemap.xml
grep -o '<loc>[^<]*</loc>' sitemap.xml | sed 's|<loc>||;s|</loc>||' \
  | grep -iE 'consent|copyright|ownership|licens|worker|labor|privacy|dataset|shutdown'
```

Swap the grep alternation for the concepts of the piece. Every hit still needs
its `<title>` read back in the verify call before it goes in the report.
Discovering a missing backlink after the browser is closed costs a full relaunch
and invalidates the close-then-verify sequence already reported done.

A long `verify()` call can start returning `Page.navigate timed out after 5s waiting for the daemon` partway through its URL list, which is a render timeout and not proof the page is dead. Do not close the browser on that output: re-verify only the timed-out URLs in a SECOND `verify()` call with `settle=3`, and treat a URL as broken only when the retry fails too. Check each returned title against the headline being cited before it goes in the report, because a 404 page renders a title and a body as well.

**Rule 8: calibration and confirmation batches belong to the Trends phase, so they run BEFORE `verify()`.** The phase list above is the happy path; any second pass over already-measured terms to chain the scales, or to re-measure a candidate that a dead-weight or anchor-heavy batch flattered, is still Trends work and must land before the link sweep. `verify()` navigates the tab to each source URL and moves it off the `trends.google.com` origin, which wipes the `__trends` and `__related` helpers, so a batch issued after it dies on its first term. Plan the order as warm, then every batch, then every related pair, then every calibration and confirmation batch, then verify last. Batch the calibration terms several to a URL and drive them in one call, the same as the primary batches. Design the calibration as ONE or TWO batches that each carry the run's SAME two bridge terms plus the terms whose magnitude matters, so a single batch both converts several primary batches onto the reference scale and validates itself: when the two bridges convert at factors within a few percent of each other, the chain is a measurement rather than a single point of failure. A calibration batch that shares only ONE live term with the reference scale cannot validate itself through its bridge, so validate it through a RATIO instead: any two terms present in both scales give a normalization-free ratio, so compute that ratio in each scale and confirm the batch when they agree. Measured: a hardware batch whose only shared term with the reference scale was `tokens per second` was confirmed by the tokens-per-second to KV-cache ratio holding at 0.684 inside it against 0.680 on the reference scale, a 0.5 percent agreement. Report the ratio beside both conversion factors, and treat a single-bridge batch as unconfirmed until a ratio or a second term confirms it. **Two calibration batches built around the SAME single bridge term validate each other when that term returns an identical Average in both, and that is the cheapest confirmation available.** Measured: two calibration batches each carried one shared bridge plus four terms needing a like-for-like read, and the bridge returned an identical Average in both, so the two batches share one scale and the terms in either convert at one factor. Confirm the result on the terms, not on the bridge: two terms carried independently by a primary batch and by a calibration batch converted to the same index reading, which is what turns the factor into a measurement. **Put the reference term itself INSIDE the bridge batch, because that turns the conversion into an identity check instead of arithmetic.** A bridge batch that carries the reference term plus terms of comparable volume needs no factor at all when the reference returns the identical Average: the batch is already on the reference scale and every member is read directly. Measured shape: a five-term batch of the reference at 44 beside terms reading 14, 20, 11 and 19 returned the reference at 44 exactly, and the two terms that also had own-batch readings converted at 1.70 and 1.71, which is a measurement rather than a guess. The same test doubles as the discard rule: when the reference term returns a DIFFERENT value in a bridge batch than in every other batch that carried it, the batch is an anchor batch, the anchor crushed the reference along with every batch-mate, and the whole batch is discarded rather than converted. A batch that read the reference at 3 beside a 42 anchor is not a fifteenfold finding, it is a composition artifact, and taking any factor from it rescales every term it touched. Reference terms of comparable volume to the terms being converted are the only bridge members that produce a usable read.
**A calibration batch built around one anchor term INFLATES that anchor, so its own magnitude comes from a batch with comparable peers and only its RATIOS come from the calibration.** The calibration's value is that its small members are measured against a known live term on one scale; the anchor itself sits alone above a field of 0-to-3 readings, which is the micro-volume shape read in the flattering direction. Measured: the bridge read 13 in an anchor-heavy core batch, 28 in a batch of comparable peers, and 59 in both calibration batches. The 28 set the tier, the 59 was used only as the divisor that placed the four small terms, and the report stated which read governed which property. Tiering the calibration figure as the anchor's volume would have promoted a mid-volume term on a number produced by its own batch composition. This is also where a term that a dominant anchor crushed to a floor gets its real reading, because a calibration batch of comparable-volume terms is the like-for-like read the own batch could not give, and the two readings are reported side by side with the like-for-like one setting the tier. A calibration batch issued after `verify()` dies on its first term with `globalThis.__trends is not a function`, because `verify()` left the tab on the last source URL; `run()` re-navigates to the Trends origin and redefines the helpers when it sees that error, and calling `warm()` first is the manual equivalent.

Budget to expect when this is followed (measured Oct 3 2026): warm 5s, 19
batches at 1-second gap about 30 seconds, 13 related pairs about 15 seconds,
link verification of 20 URLs about 1 minute (1.5s settle, adaptive retry for
slow-rendering titles), formatting and email about 1 minute. Roughly 3 to 4
minutes total. A run that exceeds 6 minutes is off this budget and the cause is
almost always a split phase or a standalone sleep.

## Close the Browser (MANDATORY — do not skip)
After all Trends batches are done, close the automation Chrome and VERIFY it is actually gone. Run from `terminal`:

```bash
powershell -ExecutionPolicy Bypass -File "~/kill_chromekw.ps1"
sleep 3; curl -s --max-time 3 http://127.0.0.1:9223/json/version || echo "port 9223 dead"
```

The script kills every chrome-kw PID and prints `remaining: N`. Success requires BOTH: `remaining: 0` in the script output AND `port 9223 dead` from the curl. One kill pass is NOT enough when multiple named `browser_exec` sessions were used (kw_b2/kw_b3 fresh sessions spawn extra Chrome children). Session proof (Sep 3 2026): a single kill left Chrome running and Vinny caught it. Always run the script and verify both conditions before reporting done.

## Pitfalls
- **A term that anchors its own batch reads its highest number there and a lower one beside comparable terms, and BOTH belong in the report.** A term reading 39 own-batch, 12 like-for-like, 3 beside a dominant anchor, and 40 in a batch where it was the largest member has no single true number: report the like-for-like read as the tier figure, the own-batch read as the shape read, and discard every anchor-crushed read as a floor. Say in the tier entry which read set the tier so the writer is not left resolving two numbers with no instruction. The same term can also read differently in two comparable batches, which is measurement noise, not a contradiction; give the range.
- **Report cross-batch magnitudes on ONE chained index, and name the reference term in the methodology.** A report drawing its terms from five or six batches cannot tier them on raw Averages, because a raw Average only means something against the batch-mates beside it. Bridge the batches through shared terms (a term read in two batches converts one batch's units into the other's), normalize the whole run to one named reference term, and write that term into the methodology line. Cross-validate the chain with at least two independent bridges; two bridges that agree are a measurement, one bridge is a single point of failure. **Pick the bridge by STABILITY, not by size: the best bridge is the term that returns the identical Average in every batch that carried it, even when it is not the largest term in the run.** A bridge is only a conversion factor while the term's own reading is stable, so prefer a term reading the same value in three or four separate batches over a bigger one that moves. A term whose reading swings by 4x or more between batches is measuring a news cycle rather than a baseline (a political or finance phrase that spikes in one month) and is unusable as a bridge in either direction: convert through the stable term, report the volatile term's own-batch reading as shape, and say in the entry that its volume is event-driven. Build one deliberate five-term ALL-LIVE confirmation batch that carries the run's big candidates plus the stable bridge term together, because that single batch both anchors the index and converts every other batch's scale in one call. Tier on the normalized index and keep the own-batch reading for shape only. Full mechanic in `browser-exec-recovery`, `references/trends-data-triage.md`. This is what stops a run of low-volume terms from being tiered on numbers that were never comparable in the first place. Anchor the index to a term measured in the run's ALL-LIVE batch, meaning every member is off the floor and none is a literal zero (`AI jobs` at 45 beside `AI agents` 32, `AI coding` 18, `AI skills` 12, `AI productivity` 8 in the measured case): that batch is the only one whose internal ordering is trustworthy, so its largest member is the honest 100. Never anchor to a term whose only reading came from a zero-heavy batch, because its peak was forced to 100 by the arithmetic and the anchor inherits the artifact. The reference term and the headable target are separate properties, and one term can hold both roles at once in opposite directions: `AI insurance` read a stable raw 55 in four batches, which made it the honest 100 for the whole run, while its clusters came back ai car insurance 100, life insurance 70, ai auto insurance 54 and ai united insurance 40, which disqualified it from any headline or meta use. Use such a term as the scale and still tier it by use in Tier 3 with the disqualifier in its entry title, then say in the methodology that the 100 is a scale reference rather than a target. Discarding a disqualified term as an anchor throws away the only stable bridge in the run, and promoting it because it anchored the index puts car-insurance shoppers on the page. Report every term that sits at the detection floor (average 0 or 1) with its own-batch read, its like-for-like read and its `nz_weeks`, and give it NO index number: index arithmetic on a rounded-to-zero value prints a two-digit figure for a term with no measurable demand, and a reader cannot tell that number from a real reading. Write in the methodology that floor terms are excluded from the index for that reason.
- **A live term with a stable reading can still be unplaceable on the index, and the answer is no index number plus the reason, never an averaged factor.** Stability across batches (the same Average three times) proves the reading is trustworthy in its own units; it does not create a bridge. When the only batches that term ever shared with the reference scale were ones it dominated, its batch-mates there were crushed to 1 or 2 and the implied conversion runs into the hundreds, so the magnitude simply cannot be placed. Write the raw reading, the week count, the three identical occurrences, and one line naming the crushed crossing terms and the factor that rules the conversion out. Do not average the crushed factors, do not print an implied index, and do not demote the term to the detection floor: it is live and it is a good tag target, it just has no place on this scale.
- **A Tier 1 candidate measured in a batch carrying near-zero batch-mates needs a confirmation read, and the confirmation read is what feeds the publishing fields.** See the four-zeros rule in the `browser-exec-recovery` skill (its `references/trends-data-triage.md`): the own-batch Average flatters a term when its batch-mates are dead weight and compresses every live term when they are not. Re-run the candidate beside at least two terms that actually carry volume, print both readings, and say which one carries shape and which carries magnitude. Promoting a primary target on a flattered number is the failure this prevents. Baseline, Article 204: `agent harness` read 40 in its own batch and 14 beside four live terms, and the same term read 2 in a batch anchored by MCP at 46 (an anchor-crushed read to discard). Two mechanics that fall out of the same confirmation read: (a) a spiky micro-term re-read beside terms an order of magnitude larger reports `nz_weeks` of 1 or 2 where its own batch reported 9, because Trends returns integers and its sub-unit weeks round to zero on the larger scale; the own-batch read carries the shape (how many weeks it is genuinely alive) and the like-for-like read carries the magnitude, so report both and name which read set the tier rather than treating the shrunken week count as a change in the term; the same integer rounding can flatten a whole term, so a term that shows one nonzero week in the finer-scaled batch and a literal zero `full53` beside live peers is a micro-volume term on its rising edge, never a coined zero, and both readings go into the report; (b) one confirmation batch can carry the bridges at the same time, so size it as the run's calibration batch (its two shared bridge terms plus the candidate) and a single call converts the primary batches onto the reference scale AND confirms the candidate, which is the cheapest way to satisfy Rule 8.
- **A confirmation call that dies on a rotated Trends token is not a data failure.** A call returning a parse error on terms you already measured means the token rotated between calls. No term may depend on such a call: every term it covered must already have a successful reading from an earlier batch, and the report must say so rather than silently dropping the terms. Keep helper definition and every read on the SAME tab.
- **Tier placement uses the own-batch reading for shape and the related-query cluster for headability, and the confirmation reading for magnitude.** State in the methodology which read governs which property, or the writer and the uploader cannot act on the report. A few on-topic terms with own-batch numbers below the tier band belong in the tier whose use they earn when the report says why.
- **A term that reads above a tier band but whose related-query clusters do not confirm the article's meaning is tiered by USE, not by its number, and that covers TWO shapes, not one.** A large Average with a long nonzero-week history proves the phrase has search volume, not that it carries the meaning the article needs: the same wording is often owned by an established field (a recovery agent in collections or towing, a commodity price term, speech to speech owned by consumer text-to-speech and public-speaking demand). The clusters are the only evidence that resolves which meaning the volume belongs to, and they disqualify a term in either shape: (a) BOTH lists come back empty, so nothing confirms the article's meaning; or (b) both lists come back POPULATED WITH ANOTHER MEANING, which is stronger evidence than an empty block and must never be read as a match just because the block has rows in it. Shape (b) is the one that slips through: `speech to speech` read Average 64, index 100, nonzero in all 53 weeks, and its top list was text to speech 100, speech therapy 18, to be or not to be speech 17, text to voice 14, freedom of speech 15, with fish audio and tts on the rising list. A title built on it ranks for people looking for a free TTS site. In both shapes the term is body-use-only and never goes in a title or H1, including when it is the run's largest reading.
  Place it in the tier its USE earns rather than the tier its number suggests, and put the disqualifier in the numbered entry's own title line ("agent recovery cost, 56 raw, disqualified from headline use", "speech to speech, index 100, disqualified from headline use") so a two-digit number sitting in Tier 3 reads as a deliberate verdict instead of an error. Give the reading, the week count, the latest value, the cluster rows that set the verdict, and the collision risk in the entry prose, then state the use in one line.
  When shape (b) empties the Tier 1 band, write Tier 1 as NONE anyway and put the disqualified term's index in the Tier 1 paragraph as the run's ceiling together with the one line explaining why it is not headable. Do not list a term in Tier 1 and disown it in the same entry; the floor of that section is on-topic volume, and a big number owned by another field is not on-topic volume.
  A term can also be fully ON topic and still carry definitional intent rather than the article's angle: an umbrella read whose top cluster rows are `what is <term>` and `<term> meaning` is real volume for the metadata and the tag list, but a reader typing it wants the definition, not the argument, so it holds its tier and goes to the meta description and tags instead of the H1. That is a placement decision, not a disqualification, and the numbered entry says which one it is in its own title line.
  **A MIXED cluster is a third case, and it HOLDS its tier instead of being demoted.** When the top rows split between the article's meaning and an unrelated one, the term is both the subject's own vocabulary and a collision: it keeps the tier its number earns, carries the disqualifier in its entry title line ("disqualified from headline use, apparel collision"), and its use is set to body, meta description and tags. A short acronym collides most easily with a consumer brand: RAG read 68 with every week nonzero and its top rows were rag bone 100, rag and bone 82, rag and bone jeans 20, do rag 29, rag company 22, rag doll 21, old rag 16, while the AI rows sat in the minority at ai rag 48, what is rag 38, rag in ai 18 and the whole rising list was clean technical demand (rag architecture +130%, rag system +110%, agentic rag +100%). Judge on the split: the bare token goes to body and metadata, the clean long form (here retrieval augmented generation) takes the slug, and the term never drops out of the report just because its headline use is disqualified.
- **An empty related-query block on a live term is not a failed read when the batch's other terms returned populated clusters.** Genuine empties sit beside live payloads in the same call and mean the term has no related demand of its own, which is normal for implementation terms readers search under the provider's name (context caching, per-task cost ledger). Re-read only a MISSING key before the browser closes; an empty list that came back with a successful batch is a finding.
- **A large long-history Average with BOTH related lists empty is a different animal from a small implementation term's empty block: the volume cannot be attributed to the article's meaning, so the name is body-only.** GRACE benchmark read 35 with 36 nonzero weeks and returned nothing on either list, twice. A phrase that broad and that old with no query cluster of its own is carrying an acronym shared with another field (a satellite mission, a clinical trial in the measured case), so the paper's own benchmark is not what anyone is typing. Never put such a name in a slug or title on the strength of its Average, never count its volume toward the article's on-topic reading, and say in the numbered entry that the volume cannot be attributed so the reader sees a verdict rather than a missed opportunity.
- **Trends pads on-topic cluster lists with generic sampler noise, so filter those rows before reading intent.** A live and fully on-topic block returned data governance 100, what is ai governance 58, ai governance framework 28 rising, and beneath them, in the same payload, best pizza near me, how to bake a cake, how to make sushi, cheapest flights to tokyo and top tourist attractions in paris. Those are the sampler's filler rows and they appear beside genuine rows on a term that is a clean match. Drop `near me`, recipe, travel-itinerary and other consumer-local queries before judging a cluster, or an on-topic term reads as polluted and gets demoted for nothing. Decide on the top rows: a top list whose leading three or four rows all carry the article's own vocabulary is a match whatever filler sits under it.
- **A draft's source URLs may be written without the double slash after the scheme, and that form does not resolve.** Auto-generated drafts emit `https:domain/path` beside correctly formed entries in the same list, and every one of them is one paste away from shipping as a dead link. Verify the string you actually print, state the split in SOURCE LIST READING (the draft's form does not resolve, the verified canonical forms are the ones printed in BACKLINK OPPORTUNITIES), and let the uploader paste the verified form. The draft's own text is not the report's to rewrite, so the reading names the form rather than editing his source list.
- **When the draft's own source list points at a hub page, record the hub in SOURCE LIST READING and keep it out of BACKLINK OPPORTUNITIES.** A newsroom index, section landing page or tag page resolves fine and is still not a story URL. Verify that it loads, state in the reading that it is a hub rather than the specific release so the statistic it supports cannot be confirmed from it, and do not list it under backlink opportunities, because every entry there is a recommendation and must be a specific story. Never invent a plausible release URL to stand in for it: an unverified slug pasted by the uploader is worse than a named hub, and the draft's own link is not the report's to change.
- **Windows path mismatch when emailing the report (CRITICAL):** The email-sender skill's Python script uses Windows Python, which does NOT understand MSYS paths (`/c/Users/...`). When you write the report file with `write_file` (which accepts MSYS paths fine), the attachment path you pass to the email script must be a raw Windows path like `r'~\keyword_research_...txt'`. If you pass an MSYS path, `os.path.exists()` returns False inside the script and the email sends without the attachment. Always construct the attachment path as a raw Windows string or use `os.path.join(os.path.expanduser('~'), ...)` which resolves to the correct Windows path.
- Google Trends has aggressive bot detection. Five patterns of failure with solutions:
  1. **429 (Too Many Requests)** — Cloudflare block. **BEST WORKAROUND:** Use direct URL-param navigation (`https://trends.google.com/trends/explore?q=term1,term2,term3,term4,term5&geo=US`) instead of navigating to the base page and typing into the searchbox. The URL-param approach bypasses the bot detection entirely on most retries. If that also gets 429'd, retry once — a fresh session often clears it.
  2. **"Oops! Something went wrong"** after page loads — the page rendered before the error, so the data is already in the DOM. Use `browser_console` with expression `document.body.innerText` (or similar DOM selectors) to extract the table and chart data from the already-loaded page before the error overlay wipes it.
  3. **Partial data only from first batch** — Accept it. The first batch (core article terms) is the most important. Design batch 1 to contain the highest-value terms.
  4. **URL-param navigation succeeds but snapshot shows empty/partial** — the data is there in the DOM even if the accessibility snapshot doesn't show it. Always call `browser_console(expression='document.body.innerText.substring(0, 10000)')` immediately after a successful URL-param load to extract the Trends table data.
  5. **Date param in URL gets rejected** — the browser can't parse date-override params like `&date=today%2012-m`. Omit the date/time params entirely and just use `&geo=US` (or omit geo too). The defaults (Past 12 months, Web Search, Worldwide) are usually correct for Vinny's research anyway.
- Coined terms will show "Avg 0" on Trends — that's CORRECT, not an error. Zero competition is the opportunity.
- **"Insufficient data" message (new pattern):** Some coined/niche terms show "Hmm, your search doesn't have enough data to show here" instead of Avg 0. This is the SAME signal as Avg 0 — zero competition, first-mover opportunity. Do not skip these terms. They appear in the Trends UI as a warning banner rather than a table row. Capture them in Tier 3 as coined/insufficient-data terms with a note about the first-mover window.
- Always load batches in priority order: batch 1 = core article concepts (highest value), batch 2 = adjacent/benchmark terms, batch 3 = hardware/ecosystem terms. If you only get one batch, you got the most important one.
- Don't skip Tier 3 terms even though they show zero volume — they're the highest value.
- Always include a note about the "critical window" for first-mover terms. Without it, the user doesn't know the urgency.
- **Include the actual URL for every source in the BACKLINK OPPORTUNITIES section** (and any external source cited in the article). Vinny wants the link-out URLs listed in the report so he can see exactly where the article links out. Format each backlink as: source name -- why high-authority -- full URL. Do not just name the source; give the clickable URL.
- **To resolve a draft's bare-domain or generic citation, harvest the outbound anchors of the primary announcement page instead of searching for the story.** A vendor, lab, or press writeup almost always links its own sources directly, so read `document.querySelectorAll('a')` hrefs on that page and filter them for the subject's domain: one read yields the exact study URL, the platform's own write-up, and any related press release, and it works even when the publisher's site refuses scripted clients. That is how a draft entry that carries only `https://asana.com` becomes the specific announcement URL. Every URL the harvest returns still needs its own page read (title plus opening body text) before it goes in the report, because a link on a page is not a verified link.
- **A 200 on a JavaScript-shell publisher is not proof of the story, because the shell answers 200 on every path.** Some vendor blogs (Google Cloud Blog is the measured case) serve an identical client-side app at any URL: `curl`, a feed, and the automation browser all return HTTP 200 with the generic `<title>Google Cloud Blog</title>` and no server-rendered headline, and the app itself sometimes renders `There's been an error loading the blog` instead of the post. A scripted 200 there proves nothing about the specific page. Verify through one of two secondary reads before the link ships: (a) open the sibling page in the same family and read its in-body anchors for the exact URL, because the anchor text carries the real headline, or (b) fetch the Wayback capture of the same URL with `curl -sL "http://web.archive.org/web/2026/<url>"` and read its `<title>`, which is the live headline at capture time. Record in the source-list reading which URLs were confirmed by page render and which by anchor or archive, and never call a shell-only URL verified on its status code.
- **Every source link MUST work AND point to the specific story (CRITICAL).** No generic links. A bare homepage, section hub, tag page, newsroom index, search result, or "find it here" placeholder is a failed link. Each URL must resolve (HTTP 200, no redirect that dumps the reader on a generic page) to the exact article, paper abstract, announcement, or data page being cited. Verify each link live before writing the report and drop or replace any that fail. The same rule applies to external citations recommended in the GEO checklist. If the source is an arXiv paper, link its abstract page; if a vendor announcement, link that post; if government data, link that dataset or report. Never ship an unverified or generic URL.
- **When two bridges between the same two batches disagree by an order of magnitude, the batch with the zero-heavy members is entirely rescaled and NONE of its numbers may be tiered.** Bridge factors are only evidence while both ends sit above the floor: a batch that read a term at 52 against three literal zeros and later read the same term at 1 beside a live peer is inflated roughly fiftyfold, and every batch-mate inherits that factor (the measured case had one term at peak 100 in its own batch and peak 3 in a comparable one, a 33-fold disagreement). Do not average the two factors, do not report a range, and do not call the term uncertain: discard the zero-heavy scale outright, use the like-for-like read as the magnitude, and keep the own-batch `nz_weeks` for shape. This is the mechanism behind a coined phrase printing an impressive average in its own batch while carrying almost nothing in the world.
- **A batch made entirely of micro-volume terms flatters every member, and it is a THIRD shape from the zero-heavy batch and the anchor-crushed batch.** When a batch's largest member is itself a floor-level term, nothing in it was ever normalized against real demand, so it prints Averages in the 20s and 30s that read like a healthy Tier 2 cluster while the same terms sit at 0 or 1 beside any term with genuine volume. The tell is a batch where every member shows a long nonzero-week history (30 to 50 weeks) at mid-double-digit Averages but no member has ever been measured against a live anchor: long weeks prove the phrase is searched, not that it is searched much. Re-read that cluster beside one live term in a separate batch before tiering any of it, report the like-for-like reading as the magnitude, keep the own-batch reading for shape and the internal ordering only (the ranking inside such a batch is trustworthy even when the numbers are not), and give the terms no index number. Article's-own-head-term cases land here often: a niche implementation phrase can be the exact phrase the piece is about and still belong at the detection floor, in which case it is a primary target on exact-phrase fit, not on volume.
- **A term ending in `review` collects consumer product-review demand whatever technical noun precedes it, so the token alone disqualifies a headline use.** `AI code review` measured index 20 with 44 raw in two batches and every week nonzero, and its related block returned ai news today 100, medvi 67, embody 47, gate review 46, saily review 43, surfshark review 40, nordvpn review 35, bet365 review 33, with the rising list all Breakout consumer-product queries. The volume is shoppers comparing subscriptions, so a title built on it ranks for the wrong intent however technical the wording looks. Check every `review`, `price`, `deal`, `best` and `vs` term's cluster before it goes near a slug, and keep the disqualifier visible in the numbered entry's title line. A term naming a traded company or its ticker is the same class: those searches are for the price move, not the mechanism, so an equity phrase keeps the tier its volume earns and is disqualified from headline and slug use with that reason written into its entry., so its headline can cover a different item than the claim the draft attributes to it, and that is a reading rather than a broken link.** The issue URL still resolves and still carries the date and curator, so check it against the article's own claim before treating it as verified for that claim: read the page head, and when its opening item is a different story, record it in the report as a source-list reading (what the page head shows, and that the attributed figure was not present in the captured text), with the verified public URL for the story kept beside it. Never convert that reading into a verdict on his prose, never call the source wrong, and never drop the entry: the digest may carry the figure further down its page.
- **A wire-service citation (Reuters, AP, Bloomberg) is usually resolved through a syndicating station copy, and that copy is the verifiable public URL.** The wire's own domain frequently does not surface through the search index, so a query for a Reuters story returns station pages (kfgo.com, whbl.com and similar) carrying the identical story with a `By Thomson Reuters` byline and the wire dateline. Verify the station page like any other source: read its title, byline and opening body text, keep it, and name the station and the wire in the SOURCE LIST READING ("the Reuters originals did not come back from the index, so the wire copy carried by <station> was verified"). Do not drop the entry because the origin domain is missing, and never present the station page as a reuters.com URL.
- **A search-index result that lands on an SEO republication of the same headline is not the authoritative page, so resolve to the original outlet and verify that instead.** Aggregator and rewrite domains republish a story within hours under the same headline, and their titles rank beside the original in a naive query. Take the URL whose domain is the outlet the draft names, and when only a rewrite site comes back, resolve the original through a site-scoped query or the outlet's own sitemap before falling back.
- **An outlet page whose headline and slug name one agency or state while its body names the one the draft cites is verified, not broken, and the mismatch is recorded as a reading.** Measured case: the GovTech URL slugs `kentucky-sheriff-nixes-ai-assisted-report-writing-after-trial` and its on-page `<title>` reads Kentucky Sheriff, while the body attributes the decision to the Ulster County Sheriff's Office, which is the agency the draft names. The page is the correct source for the claim. Read the opening body text, not just the title, before judging a source, then state in the SOURCE LIST READING what the headline says, what the body says, and that the page is the right source. Never drop the entry, and never tell Vinny a citation is wrong on the strength of a title alone.
- The unique angle must be article-specific. Identify what THIS article has that competitors don't (community angle vs industry angle, security hook vs academic hook, vendor angle vs engineering angle). Do not reuse stale differentiators from past sessions.
- Internal linking suggestion: cross-link to related PhantomByte articles to build content clusters. Check the article's own citations and references for natural link targets.
- **A draft that names a prior PhantomByte article by headline may not match any live slug, because a draft headline is often a working title.** Resolve it against the site sitemap to the closest live URL, read that page back to confirm it, and tell the writer to quote that page's ACTUAL on-page title or drop the named headline. Pointing a citation at an article whose on-page headline does not match the one the draft quotes is the failure this prevents, and a draft source list that names articles without URLs must be resolved before the report ships.
- On-page GEO checklist (WRITE-TIME ONLY, per the September 2026 strategy update. Vinny writes articles but had been omitting these, so a report written BEFORE the draft exists must call them out explicitly). These five items are advice to the writer ahead of the draft. They are never issued against a finished or published article, and a report on existing prose carries no edit instruction of any kind (see the HARD RULE above):
  1. 3-8 EXTERNAL citations to primary sources (vendor announcements, papers/arXiv, official docs, government data). Descriptive anchor text, never keyword-stuffed. Cite at the point of claim, not a footer link dump. This is the KDD 2024 "Cite Sources" method (+27% AI visibility).
  2. 3-5 INTERNAL links to related PhantomByte articles with real anchor text. Fixes the orphan-page problem (Sep 2026 audit found articles had ZERO internal article links — all 189 pages only reachable via sitemap).
  3. At least one blockquote from an authoritative source and at least one named statistic (the two best GEO methods).
  4. Quotable self-contained first sentences per paragraph; a table or list where content supports it.
  5. Include a "GEO On-Page Checklist" section in every PRE-DRAFT keyword report listing these 5 items so the writer sees them at write time, not after publication. A report on an article that ALREADY exists carries no GEO checklist section and no write-time advice of any kind: it ends at TAGS, and the uploader receives tier data, publishing fields, title notes and link targets only.
- Retrofit Mode (existing-article audit): When Vinny says "run the audit" or asks which existing articles need fixes, crawl all sitemap URLs and score each article on: external citation count (target 3-8), internal article link count (target 3-5), blockquote presence, statistic presence, table/list presence. Rank worst-first and report which articles to retrofit in priority order. Retrofit Mode runs ONLY when Vinny explicitly asks for the audit, and even then its output is a scored findings list for HIM to act on: name the gap, cite the reading, and stop. It never carries an edit instruction, never rewrites one of his sentences, never labels his prose defective, and no agent applies a retrofit to any article without his direct order on that article. This is the one place a report may name what an existing article lacks, and it still proposes no prose change. Baseline finding (Sep 6, 2026 audit): sample articles averaged 1 external link (self-referential only), 0 internal article links, 0 blockquotes, 0 tables.
- See `references/example_report_data_center_war.txt` for a full worked example of a keyword research report with all sections (tier breakdown, critical window, backlink opportunities, recommended URL/meta).
- See `references/synthetic_data_paradox_trends_data.txt` for a real-world Trends data capture from Article 100 (synthetic data / model collapse / ICML 2026 paper). Useful as a comparison baseline for future AI-training-infrastructure keyword research.
- See `references/report_template_750_rack.txt` for a full report template with all sections (recommended URL, meta description, backlink opportunities, internal linking, tags). Use this as the canonical structure for all future keyword research reports.

## Integration With Outlines
When keyword research is requested alongside an article outline (not just for a finished article), the keyword research and outline are **interleaved outputs**:

1. Run keyword research first. Use the data to inform the outline.
2. Embed the keyword tier data directly into the outline document so the writer has strategic targets without cross-referencing a separate file.
3. In the outline, explicitly map:
   - **Primary targets** → URL slug, first 100 words, meta description
   - **Secondary targets** → H2 headings, body content, semantic SEO
   - **Tertiary targets** → tags, image alt text, long-tail anchors
4. Include a `Keyword Research Summary` block near the top of the outline with the 3-tier breakdown.
5. Add an `SEO Integration Map` in the writer notes listing exactly where each target term should appear.

This prevents the common failure mode where keyword research gets emailed as a separate file and the outline writer never sees it.

### Standalone Report Format (when NOT paired with an outline)
If producing a standalone keyword research file, structure it like this:

```
PRIMARY TARGETS (optimize URL slug, first 100 words, meta description):
  1. [term] — [volume], [competition note], [why]
  2. [term] — ...

SECONDARY (H2s, body content, semantic SEO):
  3. [term] — ...
  4. [term] — ...

TERTIARY / FUTURE (tags, image alt text, long-tail):
  5. [term] — ...
```
