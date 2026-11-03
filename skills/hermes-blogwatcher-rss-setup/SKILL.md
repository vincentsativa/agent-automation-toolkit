---
name: blogwatcher-rss-setup
description: Install and configure blogwatcher-cli for AI news RSS monitoring. Includes working feed URLs, troubleshooting failed feeds, cleanup workflow, and cron job orchestration.
toolsets: [terminal]
---

# Blogwatcher RSS Setup

Install blogwatcher-cli and configure AI news RSS feeds with known-working URLs.

## Installation

**Binary (Linux amd64):**
```bash
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C ~ && chmod +x ~/blogwatcher-cli
```

Use `~/blogwatcher-cli` for all commands (no sudo install needed).

## Working AI News RSS Feeds

These feeds have been verified working:

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

## Sites WITHOUT RSS Feeds

These sites do not expose standard RSS/Atom feeds and will fail auto-discovery:

- Anthropic, OpenAI, DeepMind, a16z, VentureBeat AI, Stability AI, Lambda Labs, AI Magazine
- TLDR AI (blocked by Vercel bot protection)

**Do not waste time trying to add these**, they require HTML scraping configuration with `--scrape-selector` which is fragile and site-specific, or are blocked by bot detection.

## Setup Workflow

**1. Add all working feeds:**
```bash
~/blogwatcher-cli add "TechCrunch AI" https://techcrunch.com/category/artificial-intelligence/feed/
~/blogwatcher-cli add "The Verge AI" https://www.theverge.com/rss/ai-artificial-intelligence/index.xml
~/blogwatcher-cli add "Ars Technica AI" https://arstechnica.com/ai/feed/
~/blogwatcher-cli add "AI News" https://www.artificialintelligence-news.com/feed/
~/blogwatcher-cli add "MIT Tech Review AI" https://www.technologyreview.com/topic/artificial-intelligence/feed/
~/blogwatcher-cli add "Hugging Face" https://huggingface.co/blog/feed.xml
~/blogwatcher-cli add "Google AI" https://blog.google/rss/
~/blogwatcher-cli add "NVIDIA AI" https://blogs.nvidia.com/feed/
```

**2. Initial scan:**
```bash
~/blogwatcher-cli scan
```

**3. Clear backlog (start fresh):**
```bash
~/blogwatcher-cli read-all --yes
```

## Ongoing Usage

| Command | Purpose |
|---------|---------|
| `~/blogwatcher-cli scan` | Check all feeds for new articles |
| `~/blogwatcher-cli articles` | List unread articles |
| `~/blogwatcher-cli blogs` | List tracked feeds |
| `~/blogwatcher-cli read-all --yes` | Mark all as read |
| `~/blogwatcher-cli remove "Name" --yes` | Remove a feed |
| `~/scripts/blogwatcher-cleanup.sh` | Two-phase cleanup (see Database Cleanup below) |

## Database Cleanup Strategy

The blogwatcher SQLite DB uses a **UNIQUE constraint on article URLs**. This matters for how you clean up old articles.

### The Re-Import Loop (Critical Pitfall)

If you **DELETE** articles from the DB, you remove their URL records. On the next `~/blogwatcher-cli scan`, those feeds will re-discover and re-insert the same articles as "new", because the unique constraint no longer blocks them. This creates a cycle: cleanup deletes → scan re-adds → DB stays bloated.

**DO NOT use DELETE-only cleanup.** The old approach of `DELETE FROM articles WHERE published_date < ?` causes this loop.

### Two-Phase Cleanup (reference: `scripts/blogwatcher-cleanup.sh`)

The correct approach uses a two-phase script at `~/scripts/blogwatcher-cleanup.sh`:

**Phase 1, Mark as Read (retention window, default 7 days):**
```sql
UPDATE articles SET is_read = 1 WHERE is_read = 0 AND published_date < ?
```
This keeps the URL row in the DB (the unique constraint still blocks re-import), but marks it read so it won't show up in article listings. The scan sees the URL exists and skips it.

**Phase 2, Hard Delete (archival limit, default 90 days):**
```sql
DELETE FROM articles WHERE published_date < ?
```
Truly ancient data gets purged to prevent unbounded DB growth. 90 days is a safe default, far enough out that re-import is unlikely to matter.

**Usage:**
```bash
# Default: mark 7+ days as read, purge 90+ days
~/scripts/blogwatcher-cleanup.sh

# Custom: mark 14+ days as read, purge 180+ days
~/scripts/blogwatcher-cleanup.sh 14 180
```

### Cron Job Ordering (Critical)

**Cleanup MUST run AFTER the daily scan, not before.**

- **11:00 AM**, Daily scan fetches new articles (`~/blogwatcher-cli scan`)
- **11:05 AM**, Cleanup marks old articles as read and purges ancient ones

If cleanup runs before the scan, it marks articles as read that haven't been reported yet. If it uses delete-only (old approach), the scan immediately re-adds them. The sequence matters.

### Database Schema Reference

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    blog_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,       -- <-- This constraint prevents re-import
    published_date TIMESTAMP,
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    categories TEXT,
    FOREIGN KEY (blog_id) REFERENCES blogs(id)
);
```

## Troubleshooting Failed Feeds

If a feed shows "No feed or scraper configured":

1. **Try the homepage URL instead of RSS URL:**
   ```bash
   ~/blogwatcher-cli remove "Blog Name" --yes
   ~/blogwatcher-cli add "Blog Name" https://example.com
   ```

2. **For Substack sites (Ben's Bites, etc.):** Use `https://[subdomain].substack.com/feed`

3. **If still failing, check for bot protection:** Sites behind Vercel Security Checkpoint or Cloudflare may block RSS access entirely.

4. **If the site has no RSS**, remove it and move on.

5. **Transient HTTP errors (503, 429):** These are server-side, not setup problems. Just re-run the scan.

## Database Location

`~/.blogwatcher-cli/blogwatcher-cli.db` (SQLite, persists across sessions)
