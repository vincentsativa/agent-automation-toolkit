# Multi-Source Exclusion + Parallel Delegation for 20-Story FINAL Reports

## When to Use This Pattern

When the user has multiple pre-existing data files (IronPulse, TensorFeed, Blogwatcher) and wants a consolidated FINAL report that:
- Excludes all stories already covered in those files
- Produces 20 fresh stories with 5-6 sentence summaries
- Includes X posts, Pinterest titles/descriptions, and 5 themes
- Saves to a specific OneDrive folder and emails as attachment

## The Proven Workflow (June 17, 2026)

### Step 1: Read All Data Files First

List the target directory to find all data files:
```bash
ls -la "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/"
```

Read each file with `read_file()` to build a mental exclusion list. Key stories to track:
- Headlines (exact match and topic match)
- Company names involved
- Key events (model releases, acquisitions, policy actions)
- Any story that would be a duplicate if covered again

### Step 2: TensorFeed API for Bulk Discovery (Fastest Path)

The TensorFeed API returns 49 articles in a single call, covering 10+ sources. This is much faster than browsing 4-5 sites sequentially.

```python
from tensorfeed_client import TensorFeed
tf = TensorFeed()
news = tf.news_recent(hours=24, limit=50)
articles = news['articles']  # 49 articles
```

Cross-reference each article's title against your exclusion list. Expect to find 25-30 candidates from 49 to get 20 fresh ones.

### Step 3: Parallel Browser Delegation for Deep Summaries

Use `delegate_task` with 3 parallel browser tasks per round. Each round takes 15-60 seconds. Chain 2-3 rounds for up to 9 deep summaries.

**Round 1** (3 tasks, ~60s):
```
delegate_task(tasks=[
    {"goal": "Browse {URL1} and return 6-8 sentence summary", "toolsets": ["browser"]},
    {"goal": "Browse {URL2} and return 6-8 sentence summary", "toolsets": ["browser"]},
    {"goal": "Browse {URL3} and return 6-8 sentence summary", "toolsets": ["browser"]},
])
```

**Round 2** (3 more tasks, ~60s):
Same pattern with the next 3 stories.

**Round 3** (3 more tasks, ~60s):
Same pattern with the next 3 stories.

Total: ~3 minutes for 9 deep summaries. For the remaining 11 stories, use TensorFeed snippet text + your knowledge to write 5-6 sentence summaries.

### Step 4: Handle Blocked Sources Gracefully

Some article URLs return 404 or bot challenges (Politico, Business Insider, PYMNTS, NYT, WaPo). For these:
1. Use the Google News snippet text (1-2 sentences visible)
2. Use the headline (which contains key information)
3. Use the source's editorial reputation for context
4. Write a 5-6 sentence summary from available metadata
5. Do NOT skip a fresh story just because its URL is blocked

### Step 5: Build the Report

Format requirements for FINAL reports:
- 20 stories, ranked best to worst
- 5-6 sentence summaries per story
- X post: exactly 190 characters
- Pinterest title + description per story
- 5 themes at the bottom (not 3)
- No em dashes anywhere
- File name: `FINAL Daily AI News Report (IMPORTANT).txt`

### Step 6: File Delivery + Email

```bash
cp ~/report.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/FINAL Daily AI News Report (IMPORTANT).txt"
```

Email via IONOS SMTP with the .txt file attached. Subject should include date. Body should have brief summary of themes + top stories.

## Pitfalls

- **Missing the exclusion step.** This is the most critical step. Without reading the data files first, you WILL duplicate stories.
- **Wrong file name.** The user specified exact casing: `FINAL Daily AI News Report (IMPORTANT).txt` with parentheses and exact spacing.
- **Em dashes.** The 5-6 sentence format tempts you to use punctuation shortcuts. Rewrite sentences properly.
- **Telegram spam.** For cron jobs, do NOT send Telegram messages unless explicitly told to. Deliver in the response body.
- **Forgetting Pinterest descriptions.** Each story needs a Pinterest title AND a description, not just an X post.
- **Delegate_task timeout on WSJ/paywalled articles.** WSJ articles consistently time out the browser subagent (60s+). Skip these for deep browsing and use snippet + headline only.
- **BBC article URLs.** BBC article URLs from Google News work but the page content is behind cookie consent. The browser snapshot + console extraction pattern works after accepting cookies.
