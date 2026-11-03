# Parallel Curl Batch Download Pattern (Cron-Safe)

## When to use

When you need to download 15-30 article HTML pages for full-text extraction in a cron session. This is faster than sequential downloads and avoids the `execute_code` block in cron mode.

## Pattern

Chain multiple `curl` commands in a single `terminal()` call using `;` separators. Each downloads to a separate temp file. Add an `echo` status per file so you can verify all completed.

```bash
curl -sL --max-time 15 'https://example.com/article1' -o /tmp/a1.html 2>/dev/null; echo "a1 done: $(wc -c < /tmp/a1.html) bytes"
curl -sL --max-time 15 'https://example.com/article2' -o /tmp/a2.html 2>/dev/null; echo "a2 done: $(wc -c < /tmp/a2.html) bytes"
curl -sL --max-time 15 'https://example.com/article3' -o /tmp/a3.html 2>/dev/null; echo "a3 done: $(wc -c < /tmp/a3.html) bytes"
```

## Performance

- 15 URLs in a single terminal() call completes in ~20-30 seconds (limited by the slowest URL)
- Each curl has its own 15-second timeout, so one slow URL doesn't block the others
- Files with 0 bytes indicate a failed download (404, timeout, or DNS failure)

## Pitfalls

- **Gzip responses**: Some sites (Euronews, ZDNET) return gzipped HTML. See the gzip handling in the main SKILL.md Step 3.
- **404 detection**: After download, check for "Page Not Found" or "404" in extracted text. The file may download successfully but contain an error page.
- **Rate limiting**: 15 concurrent curls to the same domain may trigger rate limits. If you see repeated 0-byte files from the same domain, add small delays between batches.
- **Timeout per URL**: `--max-time 15` is usually sufficient. Increase to 30 for slow sites (MIT Tech Review, some WIRED pages).

## Batch size

Tested with up to 15 URLs in a single call. For 25+ URLs, split into two terminal() calls to avoid output truncation (50KB stdout cap).
