# Editorial Brief with Themes, Full Cron Pipeline

Full reference for a cron-mode editorial brief job that produces a themed
news report with email delivery. Combines blogwatcher scan + theme discovery
+ article themes + cleanup in one scheduled run.

## Pipeline Overview

1. **Scan news sources** (blogwatcher or RSS-first)
2. **Select 30 stories** ranked best-to-worst (industry news + arXiv fallback)
3. **Discover 5 unwritten article themes**, topics present in today's data
   that PhantomByte has NOT yet covered, each with a namediff (explicit
   statement of why it differs from the closest existing published article)
4. **Write the report** to a file
5. **Email delivery** as attachment via IONOS SMTP
6. **Cleanup**, mark/purge stale articles and remove temp files

## 30-Story Report Rules

- Exactly 30 stories, ranked best-to-worst
- 5-6 sentence summaries for the top anchor stories
- Cross-reference `articles.phantom-byte.com` to find the 5 unwritten themes
- Each theme MUST have a namediff referencing the closest existing article
  title and date, explaining the difference

## Theme Discovery (Unwritten Themes)

1. Extract all recent PhantomByte article titles + dates
2. Compare against today's data to find topics not yet covered
3. Each theme needs:
   - A provocative article title angle
   - Supporting sources from today's data
   - Explicit namediff vs closest existing article

## Cron Execution Notes

- **No delegate_task for browsing**, subagent results may not return before
  the cron session ends. Use sequential browsing or curl extraction.
- **No execute_code** if blocked in cron, use read_file / terminal /
  write_file instead.
- **Email delivery**, write report to file first, attach via SMTP script.
- **Telegram notification**, put the notification in the FINAL response;
  do NOT call `hermes send --to telegram`.
- **Cleanup** runs AFTER the scan, not before.

## Delivery Format

- Subject line includes the date
- Body: count + top themes summary
- Attachment: the full 30-story report file
- Sign appropriately for the job (e.g. "- Bill")
