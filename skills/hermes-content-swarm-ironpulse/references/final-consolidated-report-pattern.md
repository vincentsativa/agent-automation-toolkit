# Final Consolidated Report Pattern

## When to Use

When IronPulse or a similar cron job requires producing a "FINAL" daily AI news report that:

1. **Excludes stories from pre-existing data files** (other sources already covered those)
2. **Combines/consolidates** multiple source streams into one master report
3. **Requires larger format** than standard IronPulse (20 stories, 5-6 sentence summaries)
4. Requires specific file naming: `FINAL Daily AI News Report (IMPORTANT)`

This is a cron-specific variant, not a standard interactive run.

## Workflow

### Phase 1: Read Existing Data Files First

Before any research, read ALL data files in the target directory to identify stories that MUST be excluded:

```python
# Query pattern: search for files in the target folder
search_files(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES", target="files", pattern="*")

# Read each file with read_file to build the exclusion list
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/blogwatcher-dump-YYYY-MM-DD.txt")
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/ironpulse-YYYY-MM-DD.txt")
read_file(path="/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/tensorfeed_report_YYYY-MM-DD.md")
```

Build a list of topics/headlines to avoid. The goal is to find stories NOT covered in those files.

### Phase 2: Find Fresh Stories (TensorFeed API + Browser Delegation)

Do NOT use `web_search()` for the final consolidated report. Use a two-phase approach: TensorFeed API for bulk headline discovery, then parallel browser delegation for deep article summaries.

**Phase 2a: Bulk headline discovery via TensorFeed API (fastest path).**

The TensorFeed API returns 49+ articles in a single call, covering Hacker News, The Verge, WIRED, Ars Technica, ZDNet, TechCrunch, NVIDIA Blog, Hugging Face Blog, arXiv, and more. This is significantly faster than browsing multiple sites sequentially.

```python
# Run via execute_code or terminal
from tensorfeed_client import TensorFeed
tf = TensorFeed()
news = tf.news_recent(hours=24, limit=50)
articles = news['articles']  # 49 articles with title, source, snippet, URL
```

Cross-reference each article's title and topic against your exclusion list. You need 20 fresh stories, so expect to find 25-30 candidates from the 49 to account for exclusions and blocked-source articles.

**Phase 2b: Deep article summaries via parallel browser delegation.**

Once you have 20+ candidate stories, use `delegate_task` with 3 parallel browser tasks per round to fetch full article content. Each round completes in ~15-60 seconds. Chain 2-3 rounds for up to 9 deep summaries. For the remaining stories, use the TensorFeed snippet text plus your knowledge to write 5-6 sentence summaries.

Goal template for each delegate task:
```
"Browse {URL} and return a 6-8 sentence detailed summary covering the core claim, key data points, and implications."
```

**Fallback: Google News AI via browser (if TensorFeed is unavailable).**
Navigate to Google News AI search and extract headlines:

```python
browser_navigate(url="https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en")
```

**Critical: Google News snapshot truncation.** The accessibility snapshot routinely truncates at ~8000 chars (1200+ lines hidden). Immediately after navigating, call `browser_console(expression='document.body.innerText.substring(0, 50000)')` to get the full page text. This captures all headlines, timestamps, and source attribution that the snapshot suppressed. Parse the body text output directly.

**Secondary route: TechCrunch AI category.**
Navigate to `https://techcrunch.com/category/artificial-intelligence/` and call `browser_snapshot(full=true)`. TechCrunch timestamps show relative times ("1 hour ago", "5 hours ago") which makes freshness verification easy.

**Building the story pool:**
For each candidate headline found, check against your exclusion list. Ask: "Is this headline or topic already covered in any data file?" If yes, skip it. You need 20 unique stories, so you may need 30+ candidates to find 20 fresh ones.

### Phase 2b: Article Detail Extraction (404/Bot Handling)

Once you have candidate headlines, you need 5-6 sentence summaries. This is the hardest part because many sources block automated access:

**Sources that reliably work for article detail:**
- TechCrunch (article URLs from category page are accessible)
- The Verge (article URLs from category page are accessible)
- Breaking Defense (direct navigation works)
- Tom's Hardware (direct navigation works)

**Sources that block or 404 (as of June 2026):**
- Politico (Cloudflare bot challenge)
- Business Insider (404 on article URLs, but headline + image present on the 404 page)
- PYMNTS (all article URLs return 404)
- CalMatters (article URLs return 404)
- CSO Online (all Foundry sites return 404: CIO, InfoWorld, Network World)
- inc.com (DataDome device check blocks)
- The Washington Post (paywall blocks full access)
- The New York Times (paywall blocks full access)

**Technique for blocked sources:**
You can construct reasonable 5-6 sentence summaries from:
1. The Google News snippet text and headline
2. The ironpulse/brain digest data files that already covered the topic (if the topic appears in the data files but the specific headline/angle is different, treat as fresh)
3. The source's name and reputation for context
4. The timestamp to confirm freshness

When direct navigation is impossible, note the source and the access limitation, but still produce the summary from available metadata. Do NOT skip a fresh story just because its article URL returns a 404.

### Phase 3: Output Format (Differs from Standard IronPulse)

| Element | Standard IronPulse | Final Consolidated Report |
|---------|-------------------|--------------------------|
| Story count | 12 | 20 |
| Summary length | 4 sentences | 5-6 sentences |
| Themes | 3 | 5 |
| X post length | 190 chars | 190 chars |
| Pinterest | Title + description | Title + description |
| File name | `ironpulse-YYYY-MM-DD.txt` | `FINAL Daily AI News Report (IMPORTANT).txt` |
| Delivery folder | Desktop + optional OneDrive subfolder | Specified OneDrive folder |

### Phase 4: File Delivery

Copy to the exact Windows path the user specified:

```bash
cp ~/output.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/FINAL Daily AI News Report (IMPORTANT).txt"
```

**Verify** the file exists after copying — confirm the exact filename matches what the user requested, including any "(IMPORTANT)" suffix and exact casing.

### Phase 5: Email + Telegram

1. Send the report as an SMTP attachment to hello@phantom-byte.com
2. For cron runs, report completion directly in the response (do NOT spam Telegram)
3. If user explicitly says "Message me in telegram after the email," send a short confirmation only — never paste report content into Telegram

## Formatting Rules (User Preference)

- **No em dashes** of any kind. Not even as replacements. Use commas, periods, or parentheses only.
- **Punctuation must be correct** — do NOT just replace em dashes with hyphens or dashes. Rewrite the sentence structure properly.
- **X posts must be 190 characters or fewer**
- **Pinterest title + description** for every story
- **5 themes** at the bottom (not 3)
- **Story counts of exactly 20** (not 12)

## Theme Structure

Each theme should be 2-4 paragraphs in the report body, explaining what the data shows across multiple stories. Themes should connect disparate stories into a coherent narrative, not just summarize single events.

## Reference File: Source Health

For an up-to-date list of which sources are accessible vs. blocked (with fallback tactics), see `references/final-report-source-health.md`. Consult this file before attempting to navigate to article URLs.

## Common Pitfalls

- **Missing the exclusion step.** Reading the data files to build the exclusion list is the most critical step. Without it, you'll duplicate stories already covered.
- **Using delegate_task when forbidden.** The user may explicitly ban subagents (e.g. "Do NOT use delegate_task or spawn any subagents. NO EXCUSES"). When this happens, fall back to the `references/pre-existing-data-consolidation.md` variant -- work entirely in the current session with direct tool calls, doing fresh browser research to find stories NOT in the data files.
- **Wrong file name.** The user specified `FINAL Daily AI News Report (IMPORTANT).txt` -- exact casing, exact parentheses, exact spacing.
- **Em dashes creeping in.** The writing-style skill says no em dashes, but double-check every sentence because the 5-6 sentence format tempts you to use punctuation shortcuts.
- **Telegram spam.** For cron jobs, do NOT send Telegram messages unless explicitly told to. Deliver in the response body.
- **Forgetting Pinterest descriptions.** Each story needs a Pinterest title AND a description (summary of the story), not just an X post.
- **"Excluding" means find fresh stories, not pick from the data files.** When the user says "EXCLUDING the stories included in the following data files," the data files are your EXCLUSION LIST. You must do fresh research to find stories NOT in any of those files. Do NOT treat the data files as your source material. The pre-existing-data-consolidation.md reference covers this case in detail.
- **Theme count mismatch.** The user may specify a different number of themes (e.g. 3 instead of 5). Honor the user's specified count, not a hardcoded default.