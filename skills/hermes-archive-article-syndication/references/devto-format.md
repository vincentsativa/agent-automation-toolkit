# dev.to (Forem) Format

## Frontmatter

dev.to reads YAML frontmatter from a markdown file pasted into its editor.

```yaml
---
title: The article headline
description: One or two sentences. Drives the feed snippet and the meta description.
tags: mcp, ai, agents, programming
published: false
canonical_url: https://articles.phantom-byte.com/<slug>.html
---
```

- `canonical_url` is mandatory. It is what protects the original's SERP position.
- `published: false` lets Vinny open it as a draft, check it, then publish. Never flip it
  to true or publish on his behalf.
- `tags` is capped at 4 for the frontmatter line. More than 4 is rejected or truncated.

## Tag Selection

Pick tags that match how the post will be discovered, not how it was filed internally.
For agent and MCP content the working set is `mcp`, `ai`, `agents`, `programming`. Confirm
against the platform's tag listings rather than inventing tags, since an unknown tag has
no follow surface behind it.

## Link Attributes (verified in rendered markup)

In-body outbound links on a dev.to post carry:

```
rel="noopener noreferrer"
```

No `nofollow`, no `ugc`, no `sponsored`. Author body links are followed.

Contrast with the platform that most people assume dev.to behaves like. Medium tags user
content with `nofollow` and `ugc`. Do not carry that assumption over, and do not carry the
 dev.to result over to the next platform either. Probe each one.

The practical consequence: the value is per-post and gated on engagement. Templated
sitewide links (sidebar, feed, bio, footer) pass essentially nothing regardless of rel,
which is why a cross-post nobody reads is worth nothing even with a followed link in it.

## Relative Internal Links

PhantomByte source articles link to sibling Notes with relative paths:

```
some-related-note.html
```

Pasted into dev.to, that resolves against dev.to and 404s. Convert to full absolute
`https://articles.phantom-byte.com/...` URLs, or delete the sentence that carried it.

## What to Strip

The published source carries a subscribe block, a Buy Me a Coffee link, and a Gumroad
catalog pitch. None of it survives the move. Replace with one closing paragraph that
links the original article and the catalog.

## Voice Checks Before Delivery

- No em dashes, en dashes, or hyphens used as dashes anywhere in the body.
- Section headers are bold and short, matching the source article.
- No inline source attribution or URLs added that were not in the original.
- Numbers stay exact. Do not round a benchmark result while adapting.
