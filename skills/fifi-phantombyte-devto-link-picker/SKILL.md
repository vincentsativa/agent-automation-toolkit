---
name: phantombyte-devto-link-picker
description: Use when picking a Phantom Byte link for a dev.to post.
version: 1.0.0
author: Vinny Barreca
license: MIT
metadata:
  hermes:
    tags: [seo, content, devto, phantom-byte, link-picker]
    related_skills: [phantombyte-publishing, phantombyte-distribution-seo]
---

# Pick the Phantom Byte link for an external post

## When to Use

Vinny shares a dev.to (or similar) post and asks which Phantom Byte article to
link at the bottom, how to phrase the footer link, or both. Also use when he
asks for a related-article recommendation for any externally published piece.

## Steps

1. Extract the archive: `web_extract(["https://articles.phantom-byte.com/"])`.
   The page lists every article as title + URL + summary, newest first.
   The extraction truncates at ~50K chars (head + tail, full text saved to a
   file). If the match may be older, read the saved file with `read_file` to
   scan the middle instead of concluding the article doesn't exist.
2. Match on the SETUP, not just keywords. The best match shares the post's
   thesis shape: same controlled-comparison framing, same number pattern, same
   failure mode. Example: a post built on "same model, same tasks, same tools,
   only the architecture changed" matched article #239 whose hook is literally
   "Same task. Same model. Same tools" (36 requests / 3.1M tokens vs 2 / 61K).
   Keyword overlap alone ("agent", "tokens") is a weak match.
3. Pick one best match and name a runner-up if a plausible second exists
   (e.g. a token-cost angle vs a harness angle). Vinny chooses.
4. Write the footer: headline link first with one sentence carrying its hook
   number, then an optional one-line homepage link ("More field notes on ... at
   articles.phantom-byte.com"). Also offer a minimal one-paragraph version.
   Copy must reuse the post's own phrasing where natural (it makes the two
   pieces read as one series).
5. Report: best match (title + URL + why in one line), runner-up if any, then
   the footer text in full and short versions.

## Tags (a separate ask, run only when tags are requested)

dev.to takes max 4 tags, lowercase letters only. Verify candidates against the
API instead of writing them from memory:

```bash
# existence: does the tag directory know this tag? (pages 1..7 cover the set)
curl -s -H 'User-Agent: hermes' 'https://dev.to/api/tags?per_page=100&page=1'
# activity: newest articles carrying the tag
curl -s -H 'User-Agent: hermes' 'https://dev.to/api/articles?tag=<tag>&per_page=10'
```

- A tag is real only if it appears in `/api/tags`. Invented or pluralized
  spellings (`aiagents`, `genai`, `llms`) return `exists=False` there.
- Rank existing tags by `published_at` of their newest article. A tag whose
  newest post is months old is dead (a stale `artificialintelligence` sat next
  to a hot `ai`), skip it and prefer the live sibling.
- Shape: one broad reach tag plus topical anchors fills the 4 slots. Report the
  rejected candidates with the one-line reason.

## Verifying a published post

- Feed: `GET /api/articles?username=<account>&per_page=5`, returns
  `tag_list` but NOT `body_markdown`.
- Full body (footer-link checks): `GET /api/articles/<id>`, take the `id`
  from the feed response.
- Tag searches carry no `x-total-count` header; don't plan volume counts on it.

## Pitfalls

- Never link the homepage alone when a deep link exists.
- Don't fabricate article numbers or hooks: every title/URL/hook number must
  come from the extracted page, quoted as returned.
- dev.to allows max 4 tags; if only a link was asked for, do not pick or attach
  tags, that is a separate ask. When tags ARE asked, use the Tags section.
