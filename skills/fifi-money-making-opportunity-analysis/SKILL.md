---
name: money-making-opportunity-analysis
description: Use when picking best money making ideas from the archive.
trigger: "user asks to find/choose/rank the best money making ideas from the data files or the MONEY MAKING OPPORTUNITIES folder"
version: 1.0.0
author: Vinny Barreca / Hermes
license: Internal
metadata:
  hermes:
    tags: [research, reporting, email]
    related_skills: [email-sender, email-sender-cron]
---

# Money-Making Opportunity Analysis

## When to Use

- Vinny points at the MONEY MAKING OPPORTUNITIES folder (or "the data files")
  and asks for the best N ideas, a ranking, or a pick against criteria.
- A best-of selection from the idea archive is requested for email delivery.
- NOT for generating the daily reports themselves (that is the cron job's
  prompt), and NOT for emailing generally (that is `email-sender`).

Class: Vinny hands over the idea archive (a FOLDER, never a single file) and
names criteria (e.g. simple to implement, high demand, easy to show value).
Deliverable is a ranked pick with rationale and implementation steps, emailed
via the `email-sender` skill.

## Procedure

1. **Resolve the input.** The named path is usually a folder:
   `C:\Users\<user>\OneDrive\Desktop\MONEY MAKING OPPORTUNITIES\`. Always list
   it first (`search_files(target='files')`), it holds dated daily reports
   (`money Making opportunity -YYYY-MM-DD.txt`) plus best-of compilations
   (`best-7-money-making-ideas-*.txt`). The folder name has changed before;
   verify, never assume. Read the full parsing recipe in
   `references/archive-format.md`.

2. **Parse programmatically, never by reading files into context.** The
   archive is 600KB+ across a dozen files. Use `execute_code` to split every
   file on `^#\s*(\d+)[.:]?\s*(.+)$` and pull any `Score: N/25` from each
   section body. Print a compact title/score index, then read only the full
   bodies of the top candidates.

3. **Dedupe before ranking.** The same idea recurs across days under
   near-identical titles (PERMIT CLOCK: OPEN PERMIT CLEANUP vs OPEN PERMIT
   CLOSE OUT). Group by normalized title prefix and keep the max score.

4. **Rank against the criteria he named this time, in his order.** The
   archive's own `/25` score is a tiebreaker and a candidate filter, not the
   answer, his criteria override it. When criteria are given, each surviving
   pick must clear every one.

5. **Read the full section of the top 4-6 candidates before choosing.** Score
   lines do not carry implementation burden; the body sections (PRODUCT OR
   SERVICE, IMPLEMENTATION GUIDE, REVENUE OPPORTUNITY, risks) do. Selection
   on scores alone is a wrong-answer machine.

6. **Write the report** (`top-N-money-making-ideas-YYYY-MM-DD.txt` in
   `C:\Users\<user>\`, never overwrite an existing one, version suffix):
   - The idea, stated plainly (what it is, who buys, price).
   - Why it is a good idea: one block per named criterion, each backed by
     the specific fact from the archive (numbers, buyer lists, proof assets).
   - Steps to implement: keep the archive's day-by-day plan when present.
   - A short runners-up section naming near misses and why they lost.

7. **Deliver by email** per the `email-sender` skill: report content in the
   body AND attached as a file (reports go in the body; only articles are
   brief-body-attach-only). Confirm sent on Telegram in one short message -
   do not paste the report into chat.

## Pitfalls

- A blank line separates `# N. TITLE` from its `Score:` line in most files,
  so a regex requiring `TITLE\nScore` matches zero ideas and the parse looks
  empty, split on the heading first, then search the body for the score.
- `Score:` appears only in some files; a missing score means the file predates
  scoring, not that the idea is weak. Filter on scores only after confirming
  most files carry them.
- Files are plain text with `\r\n` line endings and a `====` banner format -
  no markdown, no JSON. Do not reach for markdown parsers.
- The user may name the folder path with no extension; treat a directory
  listing as step one rather than failing to open a "file".
