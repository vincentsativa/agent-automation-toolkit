---
name: blogwatcher
description: Monitor blogs and RSS/Atom feeds for updates using the blogwatcher-cli tool. Add blogs, scan for new articles, track read status, and filter by category.
version: 2.0.0
author: JulienTant (fork of Hyaxia/blogwatcher)
license: MIT
metadata:
  hermes:
    tags: [RSS, Blogs, Feed-Reader, Monitoring]
    homepage: https://github.com/JulienTant/blogwatcher-cli
prerequisites:
  commands: [blogwatcher-cli]
---

# Blogwatcher

Track blog and RSS/Atom feed updates with the `blogwatcher-cli` tool. Supports automatic feed discovery, HTML scraping fallback, OPML import, and read/unread article management.

## Hard Rules

### Dedup Against Existing Data Files (HARD RULE)
Before generating ANY report, read the files in `~/Desktop/TODAYS DATA FILES/` (and its OneDrive mirror `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\`). Extract the headlines already covered today. Only include stories NOT already present, do NOT duplicate what TensorFeed / Blogwatcher / IronPulse already reported that day.

### Excluded Stories (HARD RULE)
Check every candidate story against `references/excluded-stories.md` before including it. Current exclusions (MUST be skipped entirely, do not include, summarize, or mention): OpenAI rogue agent (all variants), Hugging Face breach (all variants), AI kill switch act stories, and any AI agent containment breach stories.

## Installation

Pick one method:

- **Go:** `go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest`
- **Docker:** `docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli`
- **Binary (Linux amd64):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **Binary (Linux arm64):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **Binary (macOS Apple Silicon):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_arm64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`
- **Binary (macOS Intel):** `curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_darwin_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli`

All releases: https://github.com/JulienTant/blogwatcher-cli/releases

### Docker with persistent storage

By default the database lives at `~/.blogwatcher-cli/blogwatcher-cli.db`. In Docker this is lost on container restart. Use `BLOGWATCHER_DB` or a volume mount to persist it:

```bash
# Named volume (simplest)
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# Host bind mount
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

### Migrating from the original blogwatcher

If upgrading from `Hyaxia/blogwatcher`, move your database:

```bash
mv ~/.blogwatcher/blogwatcher.db ~/.blogwatcher-cli/blogwatcher-cli.db
```

The binary name changed from `blogwatcher` to `blogwatcher-cli`.

## Common Commands

### Managing blogs

- Add a blog: `blogwatcher-cli add "My Blog" https://example.com`
- Add with explicit feed: `blogwatcher-cli add "My Blog" https://example.com --feed-url https://example.com/feed.xml`
- Add with HTML scraping: `blogwatcher-cli add "My Blog" https://example.com --scrape-selector "article h2 a"`
- List tracked blogs: `blogwatcher-cli blogs`
- Remove a blog: `blogwatcher-cli remove "My Blog" --yes`
- Import from OPML: `blogwatcher-cli import subscriptions.opml`

### Scanning and reading

- Scan all blogs: `blogwatcher-cli scan`
- Scan one blog: `blogwatcher-cli scan "My Blog"`
- List unread articles: `blogwatcher-cli articles`
- List all articles: `blogwatcher-cli articles --all`
- Filter by blog: `blogwatcher-cli articles --blog "My Blog"`
- Filter by category: `blogwatcher-cli articles --category "Engineering"`
- Mark article read: `blogwatcher-cli read 1`
- Mark article unread: `blogwatcher-cli unread 1`
- Mark all read: `blogwatcher-cli read-all`
- Mark all read for a blog: `blogwatcher-cli read-all --blog "My Blog" --yes`

## Environment Variables

All flags can be set via environment variables with the `BLOGWATCHER_` prefix:

| Variable | Description |
|---|---|
| `BLOGWATCHER_DB` | Path to SQLite database file |
| `BLOGWATCHER_WORKERS` | Number of concurrent scan workers (default: 8) |
| `BLOGWATCHER_SILENT` | Only output "scan done" when scanning |
| `BLOGWATCHER_YES` | Skip confirmation prompts |
| `BLOGWATCHER_CATEGORY` | Default filter for articles by category |

## Example Output

```
$ blogwatcher-cli blogs
Tracked blogs (1):

  xkcd
    URL: https://xkcd.com
    Feed: https://xkcd.com/atom.xml
    Last scanned: 2026-04-03 10:30
```

```
$ blogwatcher-cli scan
Scanning 1 blog(s)...

  xkcd
    Source: RSS | Found: 4 | New: 4

Found 4 new article(s) total!
```

```
$ blogwatcher-cli articles
Unread articles (2):

  [1] [new] Barrel - Part 13
       Blog: xkcd
       URL: https://xkcd.com/3095/
       Published: 2026-04-02
       Categories: Comics, Science

  [2] [new] Volcano Fact
       Blog: xkcd
       URL: https://xkcd.com/3094/
       Published: 2026-04-01
       Categories: Comics
```

## Export Workflow: Articles to Formatted Text File

When the user asks to see all stories from today (or this week) from blogwatcher, or to dump articles to a file:

1. **Locate the binary**, it lives at `~/blogwatcher-cli` (not in PATH, and NOT at `~/.blogwatcher-cli/blogwatcher-cli`). Use this full path for all commands:
   ```bash
   ~/blogwatcher-cli scan
   ~/blogwatcher-cli articles
   ~/blogwatcher-cli articles --all
   ```

2. **Run scan first** to catch latest articles:
   ```bash
   ~/blogwatcher-cli scan
   ```

3. **Get articles list**, use `~/blogwatcher-cli articles` to see unread articles. The output includes article ID, status, headline, blog name, URL, publication date, and categories.

4. **Per-source extraction:** Use `--blog "Blog Name"` filter to get articles from a specific source cleanly, rather than grepping the full output. This is faster and avoids truncation on large DBs:
   ```bash
   ~/blogwatcher-cli articles --blog "TechCrunch AI" | head -100
   ~/blogwatcher-cli articles --blog "The Decoder" | head -100
   ```
   Only fall back to `--all | grep "Published: YYYY-MM-DD"` when you need to query across all sources at once.

5. **Collect ALL unread articles from today** (published today or last 24h). Do NOT filter to a limited set like 12, give them all unless the user specifies a count.

6. **Write output to a text file** at `~/blogwatcher-dump-YYYY-MM-DD.txt`:
     - Format cleanly with headline, source, date, categories, and URL for each
     - Do NOT generate social media posts, rankings, or Pinterest/X content
     - Do NOT load or la use the `ironpulse` skill, this is a simple dump

### Pitfalls & User Preferences
- **Story Volume:** Do not aggressively truncate the results. If a scan returns hundreds of articles, provide a comprehensive report rather than a tiny curate selection, unless a specific count is requested. Avoid undershooting the delivery volume.
- **Stale Feed Backlog Detection:** Ben's Bites and AI Weekly (Substack-based feeds) often return 19-20 "new" articles per scan that span several weeks or months, not just the last 24 hours. Always check publication dates on articles from these sources before including them in a daily report. If the most recent article is 3+ days old, the entire batch is stale, skip the source for that day rather than wasting time filtering.
- **Hugging Face Volume:** The Hugging Face blog feed routinely returns 700-800+ new articles per scan (due to aggregating multiple blog series). Use `head -150` instead of `head -100` for this feed to avoid cutting off useful content mid-stream.
- **arXiv Dominance:** arXiv cs.AI alone pulls ~300-400+ articles per scan. For editorial briefs, skip arXiv entirely unless you need to hit 12+ industry headlines and fall short. For raw dumps, filter arXiv into its own section.
- **Article ID Indentation:** The `[ID] [new] HEADLINE` lines in `blogwatcher-cli articles --all` output are indented with leading spaces (typically 2 spaces). Regex patterns that expect `^\[(\d+)\]` will fail; use `^\s*\[(\d+)\]` or prefer the line-block extraction pattern that scans for `Published:` lines instead of parsing headers with regex.

6. **Send the file path** to the user via Telegram with the full path.

### Cron / Daily News Digest Workflow

When running blogwatcher as a scheduled cron job (no user present, autonomous execution):

1. **Find the binary.** The binary is at `~/blogwatcher-cli`. The DB is at `~/.blogwatcher-cli/blogwatcher-cli.db`. `which` may fail since it's not in PATH.

2. **Run scan:**
   ```bash
   ~/blogwatcher-cli scan
   ```

3. **Get all articles, filter by today's date.** With 2800+ articles in the DB, pipe through grep to isolate today's stories:
   ```bash
   ~/blogwatcher-cli articles --all | grep -B6 "Published: YYYY-MM-DD"
   ```
   (Replace YYYY-MM-DD with today's date like `2026-04-28`.)

4. **Parse with Python for large outputs.** The `articles --all` output can exceed 600K chars across 15K+ lines. Use a Python script with `re` modules to extract structured article data:
   - Match: `[ID] [new/read] HEADLINE`
   - Match subsequent `Blog:`, `URL:`, `Published:`, `Categories:` lines
   - Filter by `Published: YYYY-MM-DD` for today's date only

5. **Generate summaries** from each headline using the LLM's understanding of the story. Headlines are often self-explanatory enough for a 1-2 sentence summary. Do NOT web-scrape additional content.

6. **Output format**, write to `~/.hermes/cron/output/daily-ai-news-YYYY-MM-DD.txt`:
   ```
   AI DAILY NEWS HEADLINES
   Date: YYYY-MM-DD
   ====================================

   --- INDUSTRY NEWS ---

   HEADLINE
     Source: Blog Name
     URL: https://...
     Summary: 1-2 sentence summary of the story.

   --- ARXIV CS.AI RESEARCH PAPERS ---

   PAPER TITLE
     URL: https://arxiv.org/abs/...
     Summary: 1-2 sentence summary.

   ====================================
   Generated by Blogwatcher
   ```

7. **Separate industry news from arXiv papers**, filter by blog name containing "arXiv" vs. all other blogs. This gives cleaner sections.

8. **Ensure output directory exists:** `mkdir -p ~/.hermes/cron/output`

9. **Response protocol for cron jobs.** The user's instructions explicitly state: "In your final response, state ONLY the full file path, the number of stories collected, and a brief confirmation message. Do NOT output the article content." Follow these delivery rules:
   - Report: `\\wsl.localhost\Ubuntu\home\vincent\.hermes\cron\output\daily-ai-news-YYYY-MM-DD.txt`
   - Count: X total (Y industry news + Z research papers)
   - Brief confirmation sentence

## Editorial Intelligence Brief Workflow (Blogwatcher + Theme Discovery)

When the user asks for a blogwatcher run that produces editorial-style output (headlines with summaries, X posts, theme ideas, email delivery): NOT the raw dump (Export Workflow) and NOT the cron digest (Cron Workflow). This is a standalone editorial research brief.

### Full pipeline (one-shot, not cron):

1. **Scan:** `~/blogwatcher-cli scan`

2. **Date-filtered extraction via Python (preferred, 1 pass, all sources):** Run a Python script that captures the full `articles --all` output and filters by today's publication date. This is faster and more reliable than per-blog calls because many feeds return 0 fresh stories on a given day, and checking each source individually wastes tool calls.

   ```python
   import subprocess, re
   today = "YYYY-MM-DD"
   result = subprocess.run(['~/blogwatcher-cli', 'articles', '--all'],
                           capture_output=True, text=True, timeout=30)
   
   articles = []
   lines = result.stdout.strip().split('\n')
   for i, line in enumerate(lines):
       if f"Published: {today}" in line:
           start = max(0, i-4)
           block = '\n'.join(lines[start:i+1])
           articles.append(block)
   
   for a in articles:
       print(a)
       print("---")
   ```

   **Per-blog refinement (fallback, only when --all is truncated):** The date-filtered `--all` Python pass already captures complete article blocks (headline, blog, URL, published date, categories) for today's articles. Per-blog `--blog "Source Name"` calls are ONLY needed when the `--all` output itself is truncated (happens around 600K+ chars / 15K+ lines). Check the raw output length and whether it captured articles from 5+ sources cleanly before falling back.

   **SKIP per-blog refinement in most cases.** The `--blog` flag returns ALL unread articles for that source, not just today's. Sources like Wired Ideas (69+ unread) and The Decoder each produce thousands of lines of non-AI content (Dyson vacuums, soccer physics, home batteries, etc.) that must be filtered. This wastes tool calls and context. The Python `--all` date-pass is sufficient for headline extraction.

   **Important:** Never blindly run per-blog calls for all feeds, the date-filtered pass tells you which sources have fresh AI content worth drilling into; use that data directly.

3. **Supplement with TensorFeed**, also fetch `tf.news_recent(hours=24, limit=50)` from the TensorFeed API for additional headlines from Hacker News, ZDNet, WIRED, MIT Technology Review, and other sources the blogwatcher may not cover. TensorFeed's Hacker News articles (often 10-15 per day) are especially valuable since HN has no RSS feed in the blogwatcher config. Merge both lists, deduplicate by URL.

   **TensorFeed reliability pitfall:** In practice, `tf.news_recent(hours=24)` often returns 0-5 articles, not 21-50. On weekends or quiet news days it may return just 1 article that's already in the blogwatcher pool. Do NOT depend on TensorFeed for volume, the blogwatcher feeds are the primary source. TensorFeed is a supplement that may add 0-3 unique headlines on a good day. If it returns 0-1 articles, skip the merge and proceed with blogwatcher data alone. The 12-headline target should be achievable from blogwatcher feeds alone (this session: 17 headlines from 6 sources without TensorFeed).

4. **Select 12+ headlines.** Bucket by source. As of June 2026 most AI news feeds are active, do NOT default to assuming only 2-3 sources. Scan first, assess actual freshness. Fallback strategy for hitting 12+:
   - Take ALL available industry headlines regardless of source count
   - Only use arXiv papers if you're genuinely short (fewer than 12 industry headlines)
   - If combined total < 12, also scan the user's previously published content on articles.phantom-byte.com to identify if any old stories have new developments, don't fabricate headlines

5. **arXiv paper selection criteria** (use ONLY if needed to hit 12+; arXiv is a last resort, not a daily requirement), With ~70+ new arXiv papers daily, pick ones most relevant to Vinny's audience:
   - Keywords to target: agent, security, safety, reasoning, inference, hallucination, faithful, trace, adversarial, tool, orchestration, composition, multi-agent, coordination, memory, deterministic, liability, privacy, jailbreak
   - Skip papers on: materials science, molecular optimization, energy prediction, quantum (unless specifically called out), theoretical math proofs, domain-specific applications (radiology, finance, legal unless they intersect agent security)

6. **Write 4-5 sentence summaries.** For the 3-5 anchor stories that will drive your unwritten themes or are the biggest news of the day, use `delegate_task` with browser toolsets to browse the full article and return a rich summary. For the remaining ~10 stories, headline + source reputation + context is sufficient. See `references/parallel-browsing-pattern.md` for the parallel browsing pattern.

   **Concurrency limit: 3 tasks per call, not 9.** The system enforces `max_concurrent_children=3` for this user. To browse 9 articles, dispatch 3 rounds of 3 tasks each:
   ```python
   # Round 1: 3 most important stories
   delegate_task(tasks=[{...}, {...}, {...}])
   # Round 2: next 3 (while writing summaries from Round 1)
   delegate_task(tasks=[{...}, {...}, {...}])
   # Round 3: final 3
   delegate_task(tasks=[{...}, {...}, {...}])
   ```
   Do NOT attempt a single call with 4+ tasks, it will be rejected.

   **CRITICAL PITFALL: Subagent results may not return before you need to produce the final output.** Subagents run in the background and their results re-enter the conversation as new messages when they finish. There is no guarantee they complete before your current turn ends. Write summaries from your own knowledge of the headline + source context first. Treat subagent browsing results as optional enhancements that arrive later, do NOT block on them or structure your output around them. If you need summaries to complete the brief, write them yourself from available knowledge and let subagent results be a bonus.

7. **Write a 190-character X post** for each headline. Exact 190-char count is not enforced but must be tweet-length. Format naturally, don't pad or truncate awkwardly.

8. **Cross-reference against articles.phantom-byte.com**, browse the front page to see what Vinny has already published recently. Use the front-page snapshot from browser_navigate (usually sufficient). Extract article titles and dates. Identify 3 "unwritten themes", topics present in today's data that haven't been covered on PhantomByte. Each theme needs:
   - A provocative article title angle
   - Supporting sources from today's data
   - Explicit statement of why this hasn't been covered yet (cite the closest existing article with date and explain the difference)
   - See `references/phantombyte-coverage-gap-analysis.md` for the full workflow

9. **Write to file** at `~/blogwatcher-dump-YYYY-MM-DD.txt` with the full editorial brief format (see references/editorial-brief-format.md for the exact structure).

10. **Email the file** using the email-sender skill (attach the .txt file). Send to hello@phantom-byte.com.

11. **Copy to Windows Desktop folder**, when the user specifies a Windows path (e.g. `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\`), copy the file there:
    ```bash
    mkdir -p "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES"
    cp ~/blogwatcher-dump-YYYY-MM-DD.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/"
    ```
    Convert Windows paths to WSL paths: `C:\Users\...` → `/mnt/c/Users/...`

12. **Telegram the user** a brief confirmation that email was sent, do NOT paste the document content. Start with a clear summary line (e.g. "Editorial brief sent, 20 stories, 3 unwritten themes"). If the user said "do NOT spam telegram", keep it to one message only.

    **Cron/autonomous mode guard:** When running as a scheduled cron job (no user present), skip Telegram entirely. The cron delivery mechanism handles the final response. Do not attempt to send Telegram messages from a cron context, the user cannot see them in real time and the cron system delivers your final output to the configured destination automatically.

13. **DB cleanup**, purge old articles after scan to prevent stockpiling (see Database Cleanup section). Use the Python cleanup script: write to a file, run it, then delete the script.

14. **File cleanup**, remove the dump file (`~/blogwatcher-dump-YYYY-MM-DD.txt`) and this run's scratch dir (`$SCRATCH`) holding any helper or email script:
    - If the user explicitly says to clear/delete/clean up files: DO IT immediately, no confirmation needed
    - If the user says nothing about cleanup: do NOT delete, the files are evidence they may want to review
    - The "ask once" safety guard only applies in the default (no-instruction) case

### Known limitations
- `blogwatcher-cli articles` output is text-terminal formatted and may get truncated by the shell if there are 1000+ articles. For very large outputs, use `~/blogwatcher-cli articles | head -N` to paginate, or pipe through `grep` to filter by date.
- **`--all` output can exceed 600K chars and 15K lines** on a DB with 2500+ articles. Never try to read it whole in a single read_file or terminal call, always pipe through grep, or better, use a Python subprocess to capture and filter it programmatically.
- **Per-blog `head -N` can miss today's articles.** When a feed returns 20 articles but only the last 1-2 are from today, `head -100` still includes them because they're at the top (newest first). But if the feed has 200+ items and `head` truncates at 100, you may miss them. The date-filtered Python pass (step 2 in Editorial Brief workflow) avoids this entirely by filtering on the `Published:` field, which works regardless of how many older items precede today's.
- `which blogwatcher-cli` may fail, always check `~/blogwatcher-cli` directly and use the full path.
- The cron output directory `~/.hermes/cron/output/` must be created before writing.
- With arXiv cs.AI alone pulling ~400+ papers per scan, most daily stories will be arXiv research papers (50+), not industry news (~8). The volume ratio is roughly 4:1 arXiv-to-news on a typical day.
- **Feed staleness is variable, check each run.** Feeds go through dormant periods then come back. As of June 5, 2026, most feeds are active again (TechCrunch AI, The Verge AI, Ars Technica AI, Wired Ideas, Google AI, NVIDIA AI, Hugging Face, Ben's Bites, AI Weekly all producing new content). Do NOT assume only 2 sources are available, scan first, then assess what's actually fresh. The stale/dormant pattern is cyclical, not permanent.
- **Wired Ideas non-AI noise:** Wired Ideas produces 10-20+ new articles daily but only 1-2 are AI-related. The rest cover Dyson vacuums, soccer physics, security news, home batteries, EV interviews, noise for an AI editorial brief. The Python `--all` date-pass includes Wired Ideas in the pool automatically, so you see AI-relevant articles (Google liability ruling, Anthropic Fable shutdown) alongside everything else without wasting tool calls on per-blog filtering.
- **The Decoder is clean (noise-free):** Unlike Wired Ideas, The Decoder is a dedicated AI/tech news source. Every article it publishes is relevant. Do not skip it.

## RSS Feed Setup Reference

When setting up new AI news feeds, use this verified working list:

### Working AI News RSS Feeds

| Source | RSS URL |
|--------|---------|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` |
| Ars Technica AI | `https://arstechnica.com/ai/feed/` |
| AI News | `https://www.artificialintelligence-news.com/feed/` |
| MIT Tech Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed/` |
| Hugging Face | `https://huggingface.co/blog/feed.xml` |
| Google AI | `https://blog.google/rss/` |
| NVIDIA AI | `https://blogs.nvidia.com/feed/` |
| The Decoder | `https://the-decoder.com/feed/` |
| MarkTechPost | `https://www.marktechpost.com/feed/` |
| Wired Ideas | `https://www.wired.com/feed/category/ideas/latest/rss` |
| Ben's Bites | `https://www.bensbites.com/feed` (Substack) |
| AI Weekly | `https://aiweekly.co` (auto-discovers feed) |

### Sites Without RSS Feeds

These do not expose standard RSS/Atom feeds, do not waste time trying:
- Anthropic, OpenAI, DeepMind, a16z, VentureBeat AI, Stability AI, Lambda Labs, AI Magazine
- TLDR AI (blocked by Vercel bot protection)

### Setup Quick-Reference

1. Add feeds: `~/blogwatcher-cli add "Name" <RSS_URL>`
2. Initial scan: `~/blogwatcher-cli scan`
3. Clear backlog: `~/blogwatcher-cli read-all --yes`

### Troubleshooting Failed Feeds

- **"No feed or scraper configured"**: Try homepage URL instead of RSS URL, or the Substack `/feed` pattern for Substack sites
- **Bot protection (503/429)**: Server-side, not setup issue, retry later
- **No RSS available**: Remove and move on

## Python Parser Reference
See `references/python-parser-pattern.md` for a working script that extracts structured article data from `articles --all` output, including handling indented `[ID]` lines and date-filtering.

## Database Cleanup

### Critical: The Re-Import Loop Problem

If you **DELETE** articles from the DB without keeping their URLs, the next `scan` will re-discover and re-insert the same articles as "new", because the unique constraint on `url` no longer blocks them. This creates an infinite loop: cleanup deletes → scan re-adds → DB stays bloated.

**DO NOT use DELETE-only cleanup.** Use the two-phase approach instead.

### Cleanup After Editorial Brief

When the user says "clear all the blogwatcher files" or "don't stockpile old data" or any explicit cleanup instruction: DO delete the dump file and the run's scratch dir (which holds the email script) immediately. No confirmation needed, they gave the order. The default behavior ONLY requires confirmation when no cleanup instruction was given.

### Two-Phase Cleanup Script

A cleanup script lives at `scripts/blogwatcher-cleanup.sh` (moved from the old `blogwatcher-rss-setup` skill):

```bash
~/scripts/blogwatcher-cleanup.sh        # defaults: mark 7+ days read, purge 90+ days
~/scripts/blogwatcher-cleanup.sh 14 180  # custom: mark 14+ days read, purge 180+ days
```

The script runs two phases:
1. **Mark as read**, `UPDATE articles SET is_read = 1 WHERE is_read = 0 AND published_date < ?`, keeps URL rows (unique constraint blocks re-import) but hides old articles from listings
2. **Hard delete**, `DELETE FROM articles WHERE published_date < ?`, reclaims space for truly ancient data

### Cleanup Ordering (CRITICAL)

Cleanup MUST run AFTER the daily scan, not before:
- **11:00 AM**, Daily scan fetches new articles
- **11:05 AM**, Cleanup marks old articles as read and purges ancient ones

### Python Cleanup (preferred, portable, no external deps)

```python
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

days = int(sys.argv[1]) if len(sys.argv) > 1 else 2
db = str(Path.home() / ".blogwatcher-cli" / "blogwatcher-cli.db")
cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("DELETE FROM articles WHERE published_date < ?", (cutoff,))
deleted = cur.rowcount
print(f"Deleted {deleted} articles older than {cutoff}")
conn.commit()
conn.close()

# Vacuum in a separate connection
conn2 = sqlite3.connect(db)
conn2.execute("VACUUM;")
conn2.close()
print("VACUUM complete")
```

Run it:
```bash
python3 /path/to/cleanup.py
```

After cleanup runs, delete the cleanup script itself:
```bash
rm /path/to/cleanup.py
```

**Pitfall:** `sqlite3` may not be installed via apt. If `sqlite3` shell (CLI) is missing, use the Python `sqlite3` stdlib module instead, it's always available with Python.

## Notes

- Auto-discovers RSS/Atom feeds from blog homepages when no `--feed-url` is provided.
- Falls back to HTML scraping if RSS fails and `--scrape-selector` is configured.
- Categories from RSS/Atom feeds are stored and can be used to filter articles.
- Import blogs in bulk from OPML files exported by Feedly, Inoreader, NewsBlur, etc.
- Database stored at `~/.blogwatcher-cli/blogwatcher-cli.db` by default (override with `--db` or `BLOGWATCHER_DB`).
- Use `blogwatcher-cli <command> --help` to discover all flags and options.
