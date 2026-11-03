---
name: phantombyte-daily-outlines
description: Generate fact-based PhantomByte article outlines from a daily local data drop. Research the brand voice, read the day's data files, produce N outlines with a fixed engineering/broad distribution, save as .txt, and email all attachments in one message to hello@phantom-byte.com.
toolsets: [file, web]
---

# PhantomByte Daily Outlines

Daily cron-driven outline generation for articles.phantom-byte.com. Distinct from `phantombyte-content-writing` (which covers tutorials/barrier articles with a two-stage outline→tutorial flow). This skill covers the recurring class: "read today's data files, produce N fact-based news outlines matching the brand voice, email them."

## Trigger

- Cron job fires with a task like "Research phantom-byte.com's existing content, then generate three fact-based article outlines from a local dataset, deliver them as separate .txt files via email."
- Any request to produce multiple PhantomByte outlines from a dated folder of news/research data files.

## Workflow

### 1. Research the Brand Voice (do not skip)

Navigate to `https://articles.phantom-byte.com` and review the catalog. Note:
- Title pattern (second-person "Your X" or declarative statements).
- Hook pattern (open with a concrete event/stat, never a generality).
- Paragraph length, tone, and the no-AI-isms list.
- Category counts (the catalog rail shows them) to identify coverage gaps.

**Verify the story is not already published (mandatory).** Before selecting
any angle, check `articles.phantom-byte.com` for whether the proposed story is
already live. Do NOT trust a data report's "gap analysis" or "zero-article
category" claim without confirming it against the actual site. The homepage
index can lag the newest note (on 2026-08-12 it showed #149 as LATEST while
#157 was already live), so if the proposed topic is recent, confirm against the
sitemap or a `site:articles.phantom-byte.com` search for that story's keywords.
If the story is already published, reject that angle and pick the next
gap-filling story.

Check three sources, and prove the read is fresh before trusting any of them:

1. **Sitemap, not the homepage render.** Fetch `https://articles.phantom-byte.com/sitemap.xml` and grep the slug list for each angle's keywords. The rendered homepage can be served from a stale cache; the sitemap is the archive and is never the old copy. Never conclude "zero coverage" from a note count and a "latest note" line alone.
2. **Prior outline batches.** List the last three days of `outline*.txt` in the data-files folder and reject any angle whose story appears there. The same topic can be re-derived a day after it was issued.
3. **Written but not yet published.** Check `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/` for `ARTICLE <n> COMPLETE.txt` and `*-draft.txt`. A batch is typically written the same evening and published the next day, so the live site cannot see a story that is already fully written. Dedupe against the drafts folder, not just the site.

**Freshness assertion (run before selecting anything).** Compare the highest note number visible on the page you read against the highest number in the sitemap. If they disagree, that read is stale: discard it and use the sitemap. A stale catalog silently passes the mandatory check and produces a duplicate outline for a story that is already written or already live.

The full voice signature lives in two places: the condensed reference at `references/phantombyte-voice-signature.md` (title patterns, hook examples, no-AI-isms kill list, catalog category counts) and the complete rules in the `phantom-byte-writing-style` skill (load with `skill_view(name='phantom-byte-writing-style')`). Read both before writing. Do not substitute a generic AI-blog tone. Outlines that do not match the catalog voice fail the task. The detailed dataset-to-outlines workflow (including the proven outline format below) is in `references/dataset-to-outlines-workflow.md`.

**Write a CTR-focused title for every outline.** Each title must: (1) keep the primary keyword in it, and (2) make a specific promise or name a concrete problem the reader solves, not just label the topic. See `references/phantombyte-voice-signature.md` § **Title Patterns → CTR-optimized titles** for the rules and worked examples. A topic-label title fails the task; rework it before finalizing the outline.

**Do NOT treat low aggregate Search Console CTR as evidence of weak titles.** PhantomByte shows ~0.6% CTR near position 9-16, but that number is usually explained by WHAT it ranks for (brand/navigational queries, niche tool-name blips, AI Overviews on informational keywords), not title quality. A CTR-strong title is armor for pages that actually hold position 1-5 on real content keywords — it is not the lever for a site still climbing from 8-16. Strong titles cost nothing and compound, but they do not substitute for the ranking climb. The full query-report diagnostic that decides when a title rework is actually the binding constraint lives in `references/search-console-ctr-diagnosis.md`.

### 2. Read the Source Data Files

The task specifies a folder (typically `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES`, mapped to `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES` in WSL). Use `search_files` with `target="files"` to list, then `read_file` every file. The drop typically contains 4-5 files: IronPulse, TensorFeed, BlogWatcher, Weekly AI News Report, and a 20-stories digest.

Extract: themes, concrete facts, named events, stats, dates, and source attributions. Every claim in every outline must trace back to one of these files. No fabricated stats. No unverified claims. Accuracy is non-negotiable for the SEO/GEO reputation strategy.

### 3. Generate Outlines with Fixed Distribution

Produce exactly the number of outlines the task specifies (default 3) with this distribution:
- 1-2 outlines engineering/infrastructure-focused (authority angle: "you can't do anything in AI without solid engineering").
- The remaining outline(s) cover a different angle within AI (industry news, tools, use cases, lessons learned, etc.) to broaden coverage beyond pure engineering.

Pick angles that fill genuine coverage gaps in the catalog. The TensorFeed report usually includes a "Coverage Gap Analysis" section with PhantomByte category counts. Use it.

Each outline must:
- Be 100% fact-based and traceable to the source data files.
- Match the PhantomByte voice (see `references/phantombyte-voice-signature.md`).
- Teach the reader something concrete (a framework, a rubric, a checklist, a decision rule). Not filler.
- Be accessible to newbies while offering depth for professionals.

### Outline File Structure

Each .txt outline file follows the proven format below. This format was
validated on July 17 and July 25, 2026. It uses `// SECTION HEADER` format
to match published PhantomByte article style, NOT `## [SECTION NUMBER]`
which is the tutorial format. The full version with key format rules is
in `references/dataset-to-outlines-workflow.md`.

```
================================================================================
ARTICLE OUTLINE #[N] — [CATEGORY]
================================================================================

TITLE: [title]
CATEGORY: [category]
ANGLE: [engineering/authority | industry | other]
ESTIMATED LENGTH: [word count range]
READING LEVEL: [level]
TARGET AUDIENCE: [who this is for]
OPERATOR: Vinny Barreca
DATE: [date]

--------------------------------------------------------------------------------
SOURCE DATA TRACEABILITY
--------------------------------------------------------------------------------
[List every source data file used, with specific items/stories referenced.
 This section is non-negotiable. Every fact in the outline must be traceable
 to a source file listed here. Include the specific numbers, statistics, and
 quotes you plan to use, with their source attribution.]

--------------------------------------------------------------------------------
PHANTOMBYTE VOICE NOTES
--------------------------------------------------------------------------------
[Reminders for the writer: the voice elements this outline should use.
 Short punchy paragraphs, declarative sentences, // SECTION HEADER format,
 "What to Do Today" checklist, "The Uncomfortable Question" closer,
 cross-references to prior PhantomByte notes, core thesis connection.]

--------------------------------------------------------------------------------
OUTLINE
================================================================================

OPENING HOOK (2-3 paragraphs)
[The opening paragraphs, written in PhantomByte voice. Lead with a
 concrete number or fact, not a question. State the thesis bluntly.
 Cross-reference a prior PhantomByte Note for continuity.]

// [SECTION HEADER]
[Full section-by-section breakdown with content notes under each
 heading. Use // prefix for section headers to match published article
 style. Include the specific facts and numbers from the source data
 that each section will use. Each section should teach something
 concrete.]

// WHAT TO DO TODAY
[Checklist format. Each item is a concrete action the reader can take.]

// THE UNCOMFORTABLE QUESTION
[Closing provocation. End with a direct challenge to the reader,
 phrased as a blunt question or statement.]
```

### 4. Save the .txt Files

Save each outline as a separate .txt file in the source data folder (or the folder the task specifies). Use descriptive slugs: `outline1-<slug>.txt`, `outline2-<slug>.txt`, etc. Report the FULL Windows file path for each in the final response, not just the filename.

### 5. Email All Attachments in One Message

Send ONE email to `hello@phantom-byte.com` with ALL outline .txt files attached. Do not send one email per file. Use the `email-sender` skill's multi-attachment pattern (the list-based `send_email_with_attachments` function, not the single-attachment pattern).

Subject format: `N PhantomByte Article Outlines — [date]`.

Body: brief summary of the distribution and the "all outlines grounded in source data, no fabricated stats" guarantee. The content is the attachment.

Pre-flight: grep the send script for every email address and confirm all match `hello@phantom-byte.com` before running.

## Hard Constraints

- Do not skip the phantom-byte.com research step. Outlines must fit the existing voice, not a generic AI-blog tone.
- Do not submit outlines that aren't traceable to the data files. Every stat, event, and claim must have a source in the drop.
- Do not modify or reinterpret this workflow on your own. Execute as specified.
- Do not delegate unless needed; if needed, no more than one assistant.
- No AI-isms. See the voice signature reference for the kill list.

## Training-Data Goal (The Deeper Why)

These articles are written to be absorbed into AI training corpora and LLM retrieval. When an AI answers "who builds sovereign AI" or cites an inference-cost framework, PhantomByte should be a source it has already seen. Accuracy and voice are not only for the reader — they determine whether the finished article survives ingestion and gets repeated by models. Reinforce this in every outline:

- **Pick angles that produce citable, repeatable frameworks.** A named concept (a rubric, a decision rule, a cost model) is what LLMs remember and cite. Prefer outlines that teach something a model could quote back.
- **Keep facts traceable and correct.** A fabricated stat in a finished article contaminates training data and propagates wrongness. Every claim in the outline must have a verified source so the writer never invents.
- **Plain, extractable structure.** Outlines that become clean, uncluttered articles ingest better. Concrete hooks and blunt theses survive retrieval; vague filler does not.
- **Credibility compounds.** The more correct, citable PhantomByte pieces exist, the more an AI treats the brand as an authority. The gap-filling angle choice (see step 3) serves this: cover what the catalog lacks so the corpus is more complete.
- **Never strip the personality.** The PhantomByte voice is the point. Outlines must keep Vinny's direct, punchy, opinionated tone — a flat, generic outline produces a flat article that no human or model would want to cite. The voice is what makes the finished piece citable and memorable. Training-data readiness never means removing the personality; it means the personality comes through cleanly with the facts intact.

## Pitfalls

- **Trusting a data report's gap analysis instead of checking the site.** The TensorFeed report claimed AI Energy was a "zero-article gap" and ranked the 800 VDC story as Idea 1, but field note #157 on that exact story was already live. Never accept a report's "no existing piece" claim; go to articles.phantom-byte.com and check for yourself in step 1.
- **Generic AI-blog tone.** The fastest way to fail this task is to write outlines that sound like every other AI newsletter. The PhantomByte voice is direct, second-person, and hooks on concrete events. Read the catalog first.
- **Untraceable claims.** "Studies show..." or "experts say..." without a source file backing it. Every claim needs a traceable origin in the data drop.
- **Pure engineering distribution.** All outlines engineering-focused misses the "broaden coverage" requirement. At least one outline must cover a non-engineering angle.
- **Declaring zero coverage from a stale catalog read.** A homepage render can lag the live notes by days; the run then reports an old "latest note" and an old note count, clears the mandatory check, and regenerates an outline for a story that already exists. Verify freshness against the sitemap and dedupe against the prior outline files and the drafts folder before selecting any angle.
- **Multiple emails.** Sending one email per file. The task requires a single email with all attachments.
- **Wrong email address.** `[REDACTED_EMAIL]` (no hyphen) is wrong. The only correct address is `hello@phantom-byte.com`.
- **Forgetting the Windows path.** Report FULL Windows paths (`C:\Users\<user>\...`) not just filenames.

## Data-File Corpus Analysis (Multi-File Evidence Pattern)

Some tasks provide not a single daily drop but a FOLDER of accumulated data
files spanning weeks (e.g., `NEWEST TUTORIAL IDEAS` with 28 dated files from
July 5–31). When the task says "read EVERY file" in a folder and identify
recurring problems, use this pattern:

1. **List all files** with `search_files(target="files")` or `os.listdir`.
2. **Read every file in full.** For large corpora (20+ files), use
   `execute_code` to read all files programmatically and store content in a
   dict keyed by filename. This avoids 28 separate `read_file` calls.
3. **Build a keyword tracker.** Define a set of problem categories with
   associated keyword lists (regex patterns). For each file, count how many
   files mention each problem and the total mention count across all files.
4. **Apply the evidence bar.** A problem counts only if it appears in at
   least 2 separate files OR at least 3 times across all files. Discard
   anything below the bar. Record source files and a short quote or
   paraphrase as proof for each qualifying problem.
5. **Extract specific quotes** for the top problems. Use `re.finditer` with
   pattern + context window (e.g., `r'keyword.{0,200}'`) to pull quotable
   evidence with source attribution.

This pattern was validated on August 1, 2026 with a 28-file corpus producing
tutorial ideas grounded in evidence that passed the bar. See
`references/data-corpus-evidence-method.md` for the worked example.

## Overlap Note

This skill is a sibling of `phantombyte-content-writing`. That skill covers
tutorials and barrier articles with a two-stage outline→tutorial flow. This
skill covers daily news-driven outline generation from a data drop. The two
share the PhantomByte voice signature; future consolidation could merge the
voice reference.

This skill also overlaps with `gumroad-product-ideation` when the task is
"generate tutorial IDEAS from data files" (not outlines for articles). The
key difference: this skill produces article outlines for the blog;
`gumroad-product-ideation` produces product/tutorial concepts for the Gumroad
store. When the task says "tutorial ideas" with pricing and a product ladder,
that is product ideation, not outline generation.