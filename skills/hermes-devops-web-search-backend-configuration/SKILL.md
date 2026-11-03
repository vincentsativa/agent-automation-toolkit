---
name: web-search-backend-configuration
description: Use for configuring web search backend for one-off user queries.
trigger: "Configuring the web search backend, installing Keenable or Firecrawl, or setting up one-off web search."
---

# Web Search Backend Configuration

Configure web search backend for ONE-OFF queries (NOT cron).

**Core principle:** `web.backend` is for ad-hoc user questions only; cron jobs use their own dedicated pipelines (TensorFeed API, IronPulse browser, Blogwatcher RSS).

## Keenable

```
pip install hermes-keenable-web
hermes plugins enable keenable
hermes config set web.backend keenable
```

- Keyless, 1,000 req/hr.
- Capabilities incl. `search_web_pages`, `fetch_page_content`, date filters.
- X/Twitter caveats: single posts only, no threads/engagement/live.

## Firecrawl MCP (for JS-heavy: X.com, Reddit)

```
hermes mcp add firecrawl --url https://mcp.firecrawl.dev/v2/mcp
```

- Keyless (answer n, blank key, Y to enable).
- Free tier 1,000 pages/mo.

## Pitfalls

- Changes take effect next session only.
- Cron jobs ignore `web.backend`.
- MCP servers need restart.
