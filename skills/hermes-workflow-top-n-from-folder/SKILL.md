---
name: top-n-from-folder
description: Extract top N ranked items from dated report files.
trigger: "find top 5 money making ideas, top N from folder, compile ranked items from reports, pick the best N tutorials from an idea archive"
---

# Top-N From Folder

Read a folder of dated report files, extract every ranked item with its score or evidence counts, deduplicate by title keywords, sort by strength, and compile a summary with full implementation plans. The reports in one folder were usually produced by several generations of the same generator, so treat format drift as the default condition and parse with a ladder.

## Procedure

1. **List the folder** with `os.listdir` (Python) or `ls` (shell). Identify the report files by name pattern (e.g. `high-value-money-making-opportunities-YYYY-MM-DD.txt`).

2. **Read the most recent 3-4 reports fully.** Do not sample randomly or rely on memory. The catalog is on disk and must be walked each time.

3. **Extract every item with a format ladder, not one regex.** Older and newer reports in the same folder use different headings, so match in order and fall through: `^IDEA \d+`, `^#\d+`, `^# \d+\.`, then a `Title:` or `TITLE:` line inside the block. Capture rank, title, price, paid or free label, and the evidence metadata when present (`(N files, M references)`, `(N references across M files)`, `evidence bar: N sources across M files`). The working ladder, dedupe and scoring code is in `references/idea-archive-extraction.md`.

4. **Validate the extraction count before trusting it.** A parser that matches one generation of the report format returns a plausible-looking subset and raises no error, so a single regex quietly drops most of the corpus. Print blocks found versus files scanned and confirm every file contributed at least one item; a file that yields zero means the ladder is missing a format, not that the file is empty. Then spot-read two or three blocks to confirm titles are titles and not body prose.

5. **Deduplicate by title keywords.** Normalize titles to lowercase alphanumeric, take first 60 chars as a key. Keep the highest-scored instance of each unique key, and record every date the idea reappeared on.

6. **Sort by score descending.** Take the top N requested. When the source files carry no numeric score, rank on these four in order: measured evidence (a controlled study or a quantified result beats a directional claim), cross-file spread (how many separate news files said it), gap against what already exists, and buyer urgency (did the buyer already live the failure, or must they be convinced it exists).

7. **Check the live catalog when the items are product ideas.** Never rank an idea against another idea alone. Pull the published product list from the Gumroad API v2 first (see `tutorial-ideas-from-data-files`), because an idea can be the best-evidenced item in the folder and still be a near-duplicate of something already selling. Note the nearest existing product and the distinction in one line per pick, and say plainly when an idea was dropped for crowding a product rather than for weak evidence.

8. **Read the theme history, not just the evidence.** An idea that reappears across many dates carries proven durability, but an idea that has been proposed repeatedly and never shipped is a signal of low appetite, not a winner. Both facts belong in the ranking rationale.

9. **For each top-N item, read the FULL body** from its source file. Save it for the summary, and re-read the quoted evidence rather than paraphrasing from the extract line.

10. **Compile the summary report.** For each item include: rank, title, score, source date, what it is (2-3 sentence summary), who pays (buyer profile), price, step-by-step implementation plan (Day 1 through Day 7, validation threshold, expansion path), and boundaries (what must not be promised).

**When the ask is "the best N tutorials to write"**, the per-item block changes to: the angle in one paragraph (the argument, not the topic), the evidence that makes the angle hold with quoted numbers, what the reader builds as a concrete deliverable list, a chapter outline with one line of content per chapter, the distinction from the nearest existing product, and build notes (stack, day count, price, who buys). The angle is the product, so a block that only restates the title has failed.

11. **Add a Best Bet section.** Pick the highest-scored item. Explain why it beats the others: trigger specificity, buyer signal clarity, delivery speed, and cost to close.

12. **Verify the document is not wrapped.** Body paragraphs go out as one long line each and the reader's client wraps them. Check with `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>`: a short maximum means the file was column-wrapped and is wrong. Hyphens only, never em dashes.

13. **Spell-check the body and the attachment before sending**, then deliver per user instruction: email via SMTP if requested, then notify on Telegram after. Read the delivered copy back over IMAP and confirm the attachment name before calling it sent.

## Pitfalls

- **A single-format parser is a silent data loss bug.** Match with a ladder of heading patterns and gate on every file contributing at least one item. The first pass on a 106-report archive returned 21 of 490 items and looked like a clean result.
- **Do not parse ranking-rationale sections as items.** Lines like "Idea 1 (6 references, 2 files) is the strongest because..." restate an idea and inflate both the count and the dedupe set. Drop blocks whose title is a sentence fragment or contains "is the strongest because".
- **Terminal cd failures in WSL:** If `terminal()` commands fail with `cd: /tmp/hermes-cron-XXXXXX: No such file or directory`, switch to `execute_code` (Python) for file listing and reading. The stale cron scratch dir breaks the shell's working directory; Python's `os.listdir` and `os.path.exists` bypass it. Passing an explicit `workdir` also clears it.
- **Do not rely on memory of past sessions** for what is in the folder. Walk the disk each time.
- **Every stat must trace to a data file.** When summarizing, cite the filename and date for any number or trigger event.
- **The summary is a new document, not a copy-paste.** Distill each opportunity to its actionable core. Do not reproduce the full original text.
