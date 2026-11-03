# Article URL Naming Convention (articles.phantom-byte.com)

## Pattern

All articles use **kebab-case.html** — lowercase, hyphens only, no underscores, no special characters, no trailing slashes.

## Examples from the Archive

| Article Title | URL Slug |
|---|---|
| The Memory Chip Is the Real Bottleneck | `memory-chip-real-ai-bottleneck.html` |
| Your Agent's Harness Is Your Real Model | `agent-harness-real-model.html` |
| Your Agent's Memory Is Too Slow to Think | `your-agents-memory-is-too-slow-to-think.html` |
| Your Agent Is a Monolith. Give It a Shepherd. | `orchestrator-pattern-shepherd-agent-architecture.html` |
| Seven Weeks at the Top, Then Irrelevant | `model-churn-seven-weeks.html` |
| The Pipeline That Trained the Machines Is Closing | `mechanical-turk-shutdown-end-human-data-labor-ai.html` |
| Your Agent Is the Tool Operator Now | `your-agent-is-the-tool-operator-now.html` |
| Your Agent Needs a Preflight Check | `your-agent-needs-a-preflight-check.html` |
| The Tokenmaxxing Hangover | `tokenmaxxing-hangover-stack-survival.html` |
| The $750 Jetson Orin Nano Rack | `the-750-jetson-orin-nano-rack-beats-cloud-ai-inference.html` |
| Verifying Agents Is Now Harder Than Generating Them | `verifying-agents-is-now-harder-than-generating-them.html` |

## Rules

1. **Full title slugged** — the slug is the full article title converted to kebab-case, not a shortened version. Recent articles use the complete title.
2. **No article number** — slugs do not include the article number (e.g., `#124` is not in the URL).
3. **No date prefix** — slugs do not include dates.
4. **No trailing slash** — the URL ends with `.html`, not `/`.
5. **No underscores** — use hyphens only.

## How to Discover the Convention

From the homepage, run in browser console:

```javascript
Array.from(document.querySelectorAll('a'))
  .map(a => a.href)
  .filter(h => h.includes('.html'))
  .slice(0, 20)
```

This returns all article URLs on the page, revealing the naming pattern.
