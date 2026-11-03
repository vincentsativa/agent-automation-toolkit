# Weekly Report Variant — 30 Stories, 5 Themes, PhantomByte Dedup

Use when the user asks for "weekly AI news," "this week's AI stories," "last 7 days," or any 7-day-window request. Combines TensorFeed API breadth with parallel browsing for depth.

## Differences from Daily Report

| Dimension | Daily (default) | Weekly | 
|---|---|---|
| Time window | 24 hours | 168 hours (7 days) |
| Story count | 24 | 30 |
| Themes | 3 | 5 |
| PhantomByte dedup | Optional | MANDATORY — each theme must include a namediff explaining why it's NOT covered by an existing article |

## Workflow

### Phase 1: Pull TensorFeed Data (7-day window)

```python
import sys
sys.path.insert(0, '/mnt/c/Users/<user>/workspace/scripts')
from tensorfeed_client import TensorFeed
tf = TensorFeed()
result = tf.news_recent(hours=168, limit=80)
articles = result['articles']  # access .articles key, not direct iteration
```

The `limit=80` is important — with a 7-day window you need overage to find 30 relevant stories after filtering out duplicates, opinion pieces, and low-quality sources.

### Phase 2: Check PhantomByte Inventory

Navigate to `https://articles.phantom-byte.com` and extract titles. The most reliable extraction method is reading the browser_navigate output directly (the snapshot from navigation includes all article titles with dates). Do NOT rely on browser_console querySelector — it frequently returns empty on this site.

**Snapshot-first extraction** — the `browser_navigate` response itself includes structured article data with headings and datetimes. Read that directly rather than calling `browser_snapshot(full=true)` separately.

### Phase 3: Parallel Browsing for Detailed Summaries

Use `delegate_task(tasks=[...])` with up to 3 concurrent browser tasks to get full article summaries. Chain 2-3 rounds for 6-9 detailed summaries. Target the top 10-12 stories for full browsing — the remaining stories can be summarized from TensorFeed snippets alone.

### Phase 4: Theme Identification with Dedup

For each of the 5 themes, write a short namediff explaining why it does NOT overlap with an existing PhantomByte article. Reference the actual article title and publish date. Example format:

```
THEME 3: The Local AI Hardware Revolution
Why It's New: PhantomByte's "Agent OS Wars" (Jun 4) covered software platform competition. 
This theme is about hardware form factor race: RTX Spark (1 petaflop Windows PCs), 
DGX Station (20 petaflop deskside), NVIDIA OpenShell sandboxed runtime.
```

### Phase 5: Report File

Write to `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\weekly-ai-news-report-YYYY-MM-DD.txt`

### Phase 6: Email

Subject: `Weekly News trends and themes`
Email body: Brief summary of what the data says this week + the 5 themes listed as bullets. Full report attached.