---
name: ironpulse
description: AI news research workflow. Quick scan answers "what's the AI news today" in one fetch; full report writes the ranked 30-story file, themes, and article ideas. Use when Vinny asks for AI news or says "ironpulse."
toolsets: [file, web, browser]
---

# IronPulse

AI news research and PhantomByte content generation.

> **Distinction:** This is the RSS-first AI news workflow. It is NOT TensorFeed (API-based news from HN/ZDNet/etc.). See `references/ironpulse-vs-tensorfeed.md`.

## Pick the mode from the words. No third mode, no improvised pipeline.

### Quick Scan Mode — DEFAULT for a question in chat

Triggers: "what are the top AI news stories today," "today's AI news," "today's AI headlines," "what's trending in AI today," "AI news brief," "give me today's AI stories," "what's happening in AI today," "get me up to speed on AI news." Any plain question about the day's AI news, with no request for a file, report, themes, or ideas.

**HARD RULE — ONE PASS, THEN ANSWER.** A quick scan is one data step and one reply:

1. **ONE `terminal` call**: `python3 ~/.hermes/skills/content-swarm/ironpulse/scripts/quick_scan.py` — fetches TechCrunch AI, WIRED AI, and Google News AI, prints `<age>h | <source> | <headline>` for everything inside 24 hours, newest first. It runs in under a second and takes no arguments.
2. **Answer in chat** from that output. 1-2 lines per story, grouped by importance.

Do not write your own fetch script or re-parse the feeds by hand; the script is the fetch. Its parser uses `email.utils.parsedate`, because Google News timestamps end in `GMT` and `strptime`'s `%z` rejects them.

Do NOT do any of the following in a quick scan. Each one is a violation:

- Do NOT load skills beyond `ironpulse` and the constitution. `scrapling`, `tensorfeed`, `hermes-agent`, and any other skill are extra tool calls the user did not ask for.
- Do NOT run a second, third, or fourth parsing or extraction pass. If the first pass printed titles and timestamps, that IS the data.
- Do NOT fetch article bodies, open a browser, or extract full text.
- Do NOT write a file, copy to Desktop, or email anything.
- Do NOT produce Pinterest titles, X posts, 4-sentence summaries, themes, or article ideas.
- Do NOT check the PhantomByte catalog or run dedup against data files.
- Do NOT use browser tools, scrapling, or web_search for a scan; plain `curl` on the feed URLs is the whole job.

**Target: two tool calls total — ONE script run, ONE answer. Zero other tool calls.** If you have made 3 data calls on a quick scan, you have already failed the mode. If a feed 404s or returns nothing recent, say so and move on with the feeds that worked. Never debug a feed at the user's expense.

### Full Report Mode

Triggers: "run ironpulse," "run ironpulse report," "generate ironpulse output," "give me a report," the file/Desktop copy, or a scheduled cron run. Also triggered by "run me an ironpulse report, with it, I want you to include three themes" — that is full workflow + inline themes + email.

Full mode = ranked story file + Desktop/OneDrive copy + Pinterest and X posts + themes + article ideas.

**Load `references/full-report-workflow.md` for the full-mode steps.** Summary of the path:

1. Fetch RSS feeds from 4+ sources (minimum 4 distinct domains), last 24 hours only.
2. Compile and rank 30 stories, best to worst.
3. Write `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`, then copy to the Windows Desktop and the OneDrive `TODAYS DATA FILES` folder. Verify the copies.
4. Add the Pinterest title and X post per story.
5. Themes and article ideas: load `references/editorial-workflow.md`.
6. Delivery: first line is the Windows-native path. Do not paste report content into Telegram.
7. Email when the run requires it: `references/cron-and-delivery.md`.

## Trigger Discipline

- "ironpulse" means this skill. "tensorfeed" means TensorFeed. Never substitute one for the other. Confusing them is the most common failure of this skill.
- Before generating any report that could duplicate the day's other outputs, dedup against `~/Desktop/TODAYS DATA FILES/` and check `references/excluded-stories.md`.
- Honor the theme count the user names. Three means three, five means five. Default for full reports is 3.
- Do not modify cron jobs. `references/cron-and-delivery.md` states the rule and the reason.
- Scheduled runs are not interactive runs: load `references/cron-and-delivery.md` before touching a cron, a delivery target, or the email step.

## References — Load On Demand Only

| File | Load when |
|---|---|
| `references/full-report-workflow.md` | Full report mode: file, Desktop/OneDrive copy, output format, social posts |
| `references/rss-sources.md` | Locating a feed, parsing it, or falling back to a browser for one source |
| `references/cron-and-delivery.md` | Scheduled runs, dual-report cadence, cost discipline, IONOS SMTP email |
| `references/editorial-workflow.md` | Themes, article ideas, PhantomByte dedup, post-delivery discussion |
| `references/ironpulse-vs-tensorfeed.md` | Unsure which of the two workflows was requested |
| `references/ironpulse-weekly-variant.md` | "this week," "weekly," "larry weekly" |
| `references/excluded-stories.md` | Before including any candidate story |
| `references/pre-existing-data-consolidation.md` | "excluding the stories in the following data files" |
| `references/multi-source-editorial-synthesis.md` | Article ideas drawn from IronPulse plus other data sources |
| `references/phantombyte-article-catalog.md` | Theme dedup fallback when the live catalog can't be read |

Do NOT load the full-mode, cron, or editorial references for a quick scan.

## Pitfalls

- **NEVER HARD-WRAP A DELIVERED FILE (Article 14).** Every body paragraph, every summary, every `Sources:` line is ONE long unwrapped line. No 79 columns, no 80 columns, no wrapping the source list to fit a page. The single most repeated way this skill has been failed is wrapping the leading `Sources:` block across several ~100-character lines while the rest of the file is fine. That alone is a rejected deliverable.
  Verify EVERY file before delivery, both the workspace copy and each Windows copy:
  ```bash
  awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>
  ```
  The longest line must be LONG (several hundred characters). If the longest line is ~80-120, the file is hard-wrapped and it is WRONG. Fix it before delivering, never after. A wrapped file is rejected on sight.
- **Quick-scan creep is the known failure.** A plain news question has turned into 4 skills and 5 parsing rounds before the user got an answer. The mode above is the fix; follow it literally.
- The feed XML must be parsed directly. Do not use `get_all_text()` on a feed, and do not pipe curl into a scraper.
- Some feeds are gzip-compressed; check for the `\x1f\x8b` magic bytes before parsing.
- Report files for email delivery use `.txt`; files meant only for reading on disk use `.md`.
- Never write a helper script to a fixed path. Use a fresh `mktemp -d` scratch dir each run.
