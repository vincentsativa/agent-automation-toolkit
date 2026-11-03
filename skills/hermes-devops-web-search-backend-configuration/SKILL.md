---
name: web-search-backend-configuration
description: Use for configuring web search backend for one-off user queries.
trigger: "Configuring the web search backend, installing Keenable or Firecrawl, or setting up one-off web search."
category: devops
---

# Web Search Backend Configuration

Configure web search backend for ONE-OFF queries (NOT cron).

**Core principle:** `web.backend` is for ad-hoc user questions only; cron jobs use their own dedicated pipelines (TensorFeed API, IronPulse browser, Blogwatcher RSS).

## Keenable

```
# Check first: current builds BUNDLE the plugin (listed as `web-keenable`, or `web/keenable`
# on a git install). If it is already there, the pip step is unnecessary.
hermes plugins list | grep -i keenable

# Only when the plugin is absent, install into the SAME python hermes runs from
# (NOT system pip, PEP 668 blocks it, and a different venv won't be discovered).
# Find it via the first line of the launcher: head -3 $(which hermes) | grep -o '/[^ ]*python3'
~/.hermes/hermes-agent/venv/bin/pip install hermes-keenable-web

hermes plugins enable keenable --no-allow-tool-override
hermes config set web.backend keenable
```

- Plugin name is `keenable` (entrypoint `hermes_agent.plugins`), NOT `web-keenable`. The plugin LIST may render it as `web-keenable` or `web/keenable` while `plugins enable` still takes `keenable`.
- Verify with a real query, not a config read: `hermes -z "Search the web for X and reply with one result title and its URL" --yolo`. A clean config with no live result means the adapter never loaded.
- Keyless, 1,000 req/hr.
- Capabilities incl. `search_web_pages`, `fetch_page_content`, date filters.
- X/Twitter caveats: single posts only, no threads/engagement/live.
- `web.backend: keenable` covers BOTH search and extract via fallback (no need to set search_backend/extract_backend).
- Windows agent: use `venv/Scripts/pip.exe` and `venv/Scripts/hermes.exe` under the Windows HERMES_HOME (e.g. `/mnt/c/Users/<user>/AppData/Local/hermes/`).

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
