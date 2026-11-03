# Pre-Existing Data Source Consolidation Variant

## When to Use

Use this variant when the user provides pre-existing data files (blogwatcher dumps, ironpulse reports, tensorfeed reports) and says "EXCLUDING the stories included in the following data files." The data files define what is ALREADY COVERED. Your job is to do fresh research to find stories NOT in any of those files.

This is distinct from the standard `final-consolidated-report-pattern.md` workflow, which assumes TensorFeed API + browser delegation for fresh story discovery. This variant covers the case where the user explicitly bans delegate_task and you must do all research directly in the current session.

## Trigger Signals

- User says "excluding the stories included in the following data files"
- User provides file paths to pre-existing data files
- User says "fetch me today's top stories" but also provides data files
- The task is a cron job that has data files already on disk

## CRITICAL INTERPRETATION: "Excluding" Means Find FRESH Stories

**When the user says "EXCLUDING the stories included in the following data files," they mean: the data files define what is ALREADY COVERED. Your job is to find stories NOT in any of those files.**

This is the opposite of treating the data files as your source material. The data files are your EXCLUSION LIST. You must do fresh research to find stories that do not appear in any of the provided files.

**Wrong interpretation:** "The data files are my source. I'll pick 20 from them."
**Correct interpretation:** "The data files tell me what's already been covered. I need to find 20 different stories from fresh research."

## Workflow

### Phase 1: Read All Pre-Existing Data Files (Build Exclusion List)

Read every data file the user specified. Build a comprehensive list of story headlines, topics, and subjects that are ALREADY COVERED and must be EXCLUDED.

```python
# Read all data files to build the exclusion list
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/blogwatcher-dump-YYYY-MM-DD.txt")
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/ironpulse-YYYY-MM-DD.txt")
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/tensorfeed_report_YYYY-MM-DD.txt")
```

Extract every headline and topic from each file. This is your exclusion list.

### Phase 2: Fresh Research to Find Stories NOT in the Exclusion List

When the user says "excluding the stories included in the following data files," the data files define what is ALREADY COVERED. You MUST do fresh browser research to find stories that do NOT appear in any of the provided files.

**Key insight:** The data files together may cover 40+ stories. You need 20 that are DIFFERENT. This means you need to browse multiple sources (TechCrunch, The Verge, Google News, WIRED, Hacker News, etc.) to find stories that none of the data files covered. Expect to browse 4-6 sources to find 20 fresh stories.

**If fewer than 20 fresh stories exist in the news cycle:** Supplement with the best stories from the data files that are most newsworthy, but mark them clearly as [ALSO IN DATA FILES] in the report. The user's primary instruction is to find fresh stories, but if the news cycle is thin, some overlap is unavoidable.

### Phase 3: Story Selection and Deduplication

1. From your fresh research, compile a list of candidate stories
2. Cross-reference each candidate against the exclusion list (headlines and topics from the data files)
3. Select the top 20 stories that are NOT in any data file
4. For each story, write a fresh 5-6 sentence summary based on your research
5. If a story appears in multiple research sources, use the best source and merge unique details

### Phase 4: Output Format

| Element | Standard Final Report | Pre-Existing Data Variant |
|---------|---------------------|--------------------------|
| Story count | 20 | 20 |
| Summary length | 5-6 sentences | 5-6 sentences |
| Themes | 5 | 3 (unless user specifies otherwise) |
| X post | 190 chars | 190 chars |
| Pinterest | Title + description | Title + description |
| File name | `FINAL Daily AI News Report (IMPORTANT).txt` | User-specified format (e.g. `20-AI-News-Stories-YYYY-MM-DD.md`) |
| Research method | TensorFeed API + browser delegation | Pre-existing data files only |

### Phase 5: File Delivery

Write to the exact path the user specified. Common patterns:

```bash
# Dated filename on Windows Desktop
/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/20-AI-News-Stories-YYYY-MM-DD.md
```

### Phase 6: Email + Telegram Notification

1. Send the report as an SMTP attachment to hello@phantom-byte.com
2. In Telegram, send ONLY a brief confirmation that the email was sent, never paste report content

## Critical Constraints

### No delegate_task or subagents

When the user explicitly says "Do NOT use delegate_task or spawn any subagents. NO EXCUSES," honor this absolutely. All work must be done in the current session with direct tool calls.

### Fresh research IS required

When the user says "excluding the stories included in the following data files," the data files define what is ALREADY COVERED. You MUST do fresh browser research to find stories NOT in any of those files. The data files are your exclusion list, not your source material.

Exception: If the user also says "Do NOT use delegate_task or spawn any subagents" AND the news cycle is thin, you may need to supplement with stories from the data files. In that case, mark them clearly as [ALSO IN DATA FILES].

### File format follows user specification

The user may specify a specific filename format (e.g. `20-AI-News-Stories-YYYY-MM-DD.md`). Honor the exact format, including file extension (.md vs .txt), date format, and naming convention.

### Punctuation rules

- No em dashes of any kind
- Use commas, periods, or parentheses instead
- Rewrite sentence structure to avoid dashes entirely, do NOT just replace em dashes with hyphens
- X posts must be 190 characters or fewer
- Pinterest title + description for every story

## Common Pitfalls

- **Treating data files as source instead of exclusion list.** The most critical mistake. "Excluding the stories in the following data files" means the data files tell you what's ALREADY COVERED. You must do fresh research to find stories NOT in those files. Do NOT pick stories from the data files.
- **Using delegate_task when forbidden.** The user may explicitly ban subagents. Read the full prompt before starting.
- **Wrong file extension.** The user specified `.md` (markdown) not `.txt`. Check the exact extension. The user may specify `.md`, `.txt`, or another format -- honor the exact extension they provide.
- **Telegram spam.** Send only a brief email-sent confirmation in Telegram. Do not paste story content.
- **Missing the exclusion instruction.** "Excluding the stories included in the following data files" means the data files define what's already covered. Build your exclusion list from them, then find fresh stories.
- **Theme count mismatch.** The user may specify a different number of themes (e.g. 3 instead of 5). Honor the user's specified count, not a hardcoded default. Check the user's prompt for the exact theme count requested.
