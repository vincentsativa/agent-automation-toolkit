# Scientific American AI Extraction Technique

## Status: Working Source (Cookie Consent Required)

Scientific American (scientificamerican.com) has AI stories that are accessible via browser but gated by a cookie consent dialog.

## Access Pattern

1. **Navigate** to the article URL
2. If a cookie consent dialog appears, **reject optional cookies** — look for a "Reject optional cookies" or "Reject all" button in the dialog
3. After rejecting, wait for the article body to render
4. Use `browser_console` with `document.body.innerText.substring(0, 20000)` to extract the full article text, or use `browser_snapshot(full=true)`

## Cookie Consent Dialog Elements

The dialog is an explicitly-rendered `<dialog>` element with:
- heading "Your privacy, your choice"
- buttons: "Manage preferences", "Accept all cookies", "Reject optional cookies"

The "Reject optional cookies" button is typically ref=e5 or close to it in the snapshot. Click it and the article body loads.

## What Works

- Full article text extraction via `browser_console` after dismissing cookie consent
- Article body contains complete text with section headers, source quotes, and bylines
- Timestamps are present in article metadata (usually shown as "June 5, 2026" format)

## What Does Not Work

- Snapshot before cookie dismissal — only shows the dialog
- Direct console extraction before cookie rejection — body is empty or gated
- `browser_snapshot(full=true)` after dialog dismissal — body may still be truncated by snapshot limit

## Stories Found

Scientific American articles appearing in IronPulse reports tend to be academic/research-focused AI stories rather than breaking product news. Example that worked:
- Anthropic recursive self-improvement warning (June 5, 2026) — full text extracted successfully