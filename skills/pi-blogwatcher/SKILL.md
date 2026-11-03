---
name: blogwatcher
description: >
  Monitor blogs and RSS/Atom feeds for new articles. Use when the user wants to add, remove, or list watched blogs/feeds, check for new posts, scan for updates, mark articles as read, get a digest of unread content, import/export OPML feed lists, export unread articles for pipeline processing, or backup/sync data to n8n. Triggers on phrases like "watch this blog", "any new posts?", "check my feeds", "mark as read", "list unread", "add feed", "remove feed", "blog digest", "feed update", "import OPML", "export feeds", "unread export", "backup to n8n", "sync with n8n", or "trigger workflow".
---

# BlogWatcher Skill

Monitor blogs and RSS/Atom feeds for new articles. All operations use Python scripts that handle fetching, parsing, storing, and deduplication. Includes n8n integration for backups and workflow automation.

## TRIGGER

Use this skill when the user:
- Wants to add a new blog/feed to monitor: "watch this blog", "add this feed", "subscribe to"
- Asks about new content: "any new posts?", "check my feeds", "what's new", "feed update"
- Wants to see unread articles: "list unread", "show me what I haven't read", "blog digest"
- Wants to mark content as read: "mark as read", "I've read this", "clear my unread"
- Wants to manage feeds: "remove this feed", "stop watching"
- Wants to import/export: "import OPML", "export my feeds", "backup my feeds"
- Wants pipeline integration: "export unread for processing", "give me JSON"
- Wants n8n backup: "backup to n8n", "sync with n8n", "trigger workflow"

## WORKFLOW

### Quick Reference

| Task | Command |
|------|---------|
| Initialize (first use) | `python scripts\db_init.py` |
| Add feed | `python scripts\feed_add.py --url <url> [--name <name>] [--category <tag>]` |
| Remove feed | `python scripts\feed_remove.py --id <id>` or `--url <url>` |
| Scan all feeds | `python scripts\feed_scan.py --all` |
| Scan one feed | `python scripts\feed_scan.py --id <id>` |
| List feeds | `python scripts\feed_list.py --feeds` |
| List unread | `python scripts\feed_list.py --unread` |
| Export unread JSON | `python scripts\feed_list.py --unread --export json` |
| Mark one read | `python scripts\feed_mark_read.py --id <article_id>` |
| Mark all read | `python scripts\feed_mark_read.py --all --confirm` |
| Import OPML | `python scripts\opml_import.py --file <path> [--category <tag>] [--confirm]` |
| Export OPML | `python scripts\opml_export.py --output <path>` |
| Backup to n8n | `python scripts\n8n_backup.py --all` |
| Trigger n8n workflow | `python scripts\n8n_backup.py --trigger-workflow <name> [--data <json>]` |

### Step 1: Initialize Database (First Use Only)

Before any other operation, ensure the database exists:

```bash
python scripts\db_init.py
```

Expected output:
```
[blogwatcher] Database ready.
```

**Note:** This is idempotent - safe to run multiple times. After first run, skip this step.

### Step 2: Add Feeds

When user provides a feed URL:

1. **Confirm with user** - Always verify the URL and optional category before adding
2. **Run the script:**

```bash
python scripts\feed_add.py --url <feed_url> --name <display_name> --category <tag>
```

Expected output:
```
[blogwatcher] Feed added: TechCrunch (https://techcrunch.com/feed/) [category: Tech]
```

### Step 3: Scan Feeds for New Articles

To fetch new articles from all feeds:

```bash
python scripts\feed_scan.py --all
```

Or scan a specific feed:

```bash
python scripts\feed_scan.py --id <feed_id>
```

Expected output:
```
[blogwatcher] Scanned: TechCrunch, 5 new articles
[blogwatcher] Scanned: The Verge, 3 new articles
```

**Report to user:** Summarize how many new articles were found per feed.

**Optional:** After scanning, offer to backup to n8n: "Would you like to backup the new articles to n8n?"

### Step 4: List Unread Articles

To show unread articles grouped by feed:

```bash
python scripts\feed_list.py --unread
```

Expected output:
```
=== TechCrunch (3 unread) ===
[1234] How transformers work
    https://example.com/post
    Published: 2026-04-18T14:00:00

=== The Verge (2 unread) ===
[1235] New AI model released
    https://theverge.com/ai-model
```

**For pipeline integration** (machine-readable JSON):

```bash
python scripts\feed_list.py --unread --export json
```

### Step 5: Mark Articles as Read

**Single article:**
```bash
python scripts\feed_mark_read.py --id <article_id>
```

**All articles in a feed:**
```bash
python scripts\feed_mark_read.py --feed-id <feed_id>
```

**ALL unread articles** (requires confirmation):
```bash
python scripts\feed_mark_read.py --all --confirm
```

### Step 6: OPML Import/Export

**Import from OPML** (Feedly, Inoreader export):

1. Show preview of feeds to be imported
2. Confirm with user
3. Run:

```bash
python scripts\opml_import.py --file <path_to_opml.xml> --category <tag> --confirm
```

**Export to OPML:**

```bash
python scripts\opml_export.py --output <path_to_output.opml>
```

### Step 7: n8n Backup & Workflow Integration

**Backup all data to n8n:**

```bash
python scripts\n8n_backup.py --all
```

**Backup only feeds:**

```bash
python scripts\n8n_backup.py --feeds
```

**Backup only unread articles:**

```bash
python scripts\n8n_backup.py --unread
```

**Trigger a specific workflow:**

```bash
python scripts\n8n_backup.py --trigger-workflow <workflow_name> --data '{"key": "value"}'
```

**Test n8n connection:**

```bash
python scripts\n8n_backup.py --test
```

**Configuration:**

n8n settings are stored in `config\n8n.env`:
- `N8N_API_URL` - Your n8n instance URL
- `N8N_API_KEY` - Your API key (stored securely)
- `N8N_WEBHOOK_BACKUP` - Webhook for feed backups
- `N8N_WEBHOOK_NEW_ARTICLE` - Webhook for new article notifications

## CRITICAL RULES

| Rule | Enforcement |
|------|-------------|
| **Run db_init.py first** | Always initialize database silently on first use, then skip |
| **Never hallucinate content** | Only present what scripts return - no invented summaries |
| **Confirm before adding feeds** | Always verify URL and category with user before calling feed_add.py |
| **Report scan results** | Always show per-feed article counts after scanning |
| **Group unread by feed** | Use feed_list.py --unread which groups by feed name |
| **Confirm --all operations** | Require explicit confirmation before marking ALL as read |
| **Never modify DB directly** | Only use scripts - never write to blogwatcher.db directly |
| **Preview OPML imports** | Show feed count and list before importing |
| **Use --export json for pipelines** | Machine-readable output for downstream processing |
| **Report errors** | Never silently fail - always show script error messages |
| **Sync to n8n** | Offer n8n backup after major operations (scan, import) |
| **Protect API keys** | Never expose n8n API key in output or logs |

## NEVER DO

- ❌ Never write directly to `data\blogwatcher.db`
- ❌ Never invent article summaries or content
- ❌ Never skip User-Agent headers (handled by scripts automatically)
- ❌ Never silently fail on network errors
- ❌ Never modify the Python scripts
- ❌ Never expose n8n API key in output

## FILE PATHS

- **Skill directory:** `~\.pi\agent\skills\blogwatcher\`
- **Database:** `~\.pi\agent\skills\blogwatcher\data\blogwatcher.db`
- **Log file:** `~\.pi\agent\skills\blogwatcher\data\blogwatcher.log`
- **n8n config:** `~\.pi\agent\skills\blogwatcher\config\n8n.env`
- **Command reference:** `~\.pi\agent\skills\blogwatcher\references\commands.md`
- **Schema reference:** `~\.pi\agent\skills\blogwatcher\references\feed-schema.md`

## REFERENCE POINTERS

For full command syntax and examples:
- **Commands:** `{baseDir}/references/commands.md`
- **Schema:** `{baseDir}/references/feed-schema.md`

## EXAMPLE INTERACTIONS

### Adding a feed
**User:** "I want to watch TechCrunch's AI section"
**Agent:** "I'll add the TechCrunch AI feed. The URL is `https://techcrunch.com/category/artificial-intelligence/feed/` - should I categorize it as 'AI' or 'Tech'?"
**User:** "AI please"
**Agent:** Runs `python scripts\feed_add.py --url https://techcrunch.com/category/artificial-intelligence/feed/ --name "TechCrunch AI" --category AI`

### Checking for new posts
**User:** "Any new posts from my feeds?"
**Agent:** Runs `python scripts\feed_scan.py --all` then reports: "Scanned 3 feeds: TechCrunch found 5 new articles, The Verge found 2 new articles, Wired found 1 new article."

### Getting unread digest
**User:** "What haven't I read yet?"
**Agent:** Runs `python scripts\feed_list.py --unread` and displays grouped list with article IDs for marking read.

### Exporting for pipeline
**User:** "Export my unread articles as JSON"
**Agent:** Runs `python scripts\feed_list.py --unread --export json` and returns the JSON output for downstream processing.

### Backing up to n8n
**User:** "Backup my feeds to n8n"
**Agent:** Runs `python scripts\n8n_backup.py --feeds` and reports: "Backup successful: 3 feeds sent to n8n"

### Triggering n8n workflow
**User:** "Send new articles to the notification workflow"
**Agent:** Runs `python scripts\n8n_backup.py --trigger-workflow notify-new-articles` and reports the workflow execution result.
