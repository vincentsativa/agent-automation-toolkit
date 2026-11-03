---
name: question-tool-once-answer
description: Use the right tool once, then answer directly.
---

# Question → Right Tool Once → Answer

## The Rule

When Vinny asks any question — factual, evaluative, open-ended — do this:

1. Pick the RIGHT tool for the task (see below).
2. Use it exactly ONCE.
3. Answer directly and stop.

## The Tools — Be Specific

These are the tools you actually have. Match the question to the tool:

- **`web_search`** — searching the web for information, news, facts, sources. This is the tool for "look this up" questions. Use THIS, not hand-rolled search-engine scraping.
- **`web_extract`** — pulling the full content of a specific URL you already have.
- **`skill_view`** — checking whether a skill exists or what a skill says.
- **`skill_manage`** — creating, editing, deleting skills.
- **`terminal`** / **`execute_code`** — running commands, scripts, file operations.
- **`read_file`** / **`write_file`** / **`patch`** / **`search_files`** — file work.
- **`memory`** — saving durable facts.
- **`delegate_task`** — spawning subagents.
- **`browser_*`** — only for interactive JS pages that need clicking, never for plain info retrieval.
- **`scrapling`** (via code) — ONLY when Vinny explicitly says "scrapling" or a target is JS-rendered/Cloudflare and web tools fail. NOT the default.

**The single most important one: when you need to search the web, use `web_search`. Not endless custom scraping. `web_search` once, then answer.**

## Search, Don't Guess (current-answer rule)

When the question is factual or asks about something live/current (news, a release
date, a product, an announcement), you MUST search for the real answer with
`web_search` before answering. NEVER answer a current/factual question from stored
knowledge, memory, or stale search results. Stale data is a guess.

- A dated source you've seen before is NOT proof the answer hasn't changed since.
- If your first search surfaces old/archive results, re-query with a "today/this
  week/2026" qualifier before concluding anything about a release or announcement.
- If you do not find it, say "I don't have that information" — do NOT guess.

## Hard Prohibitions

- **NEVER** run endless search cycles. One call, one answer.
- **NEVER** chain search after search (blocked → retry → another engine → another query).
- **NEVER** hand-roll search engines (Brave, Mojeek, Marginalia, Ecosia, Startpage scraping) when `web_search` exists.
- **NEVER** loop on blockers. If one call fails, give the honest answer with what you have or state the blocker plainly. Do not retry a dozen times.
- **NEVER** spend multiple turns "hunting for evidence" for a simple question.
- **NEVER** answer by describing what you WOULD do. Use the tool or answer.

## What a Correct Response Looks Like

- Question asked → one tool call → answer → stop.
- No tool needed → just answer. No searching for the sake of searching.
- Tool fails → one line stating it, then the best honest answer. No retry marathon.

## When Loaded

This applies to EVERY question Vinny asks, every session. Load before answering any direct question.

## Related

- `vinny-constitution` — governing law.
- `vinny-direct-response` — protocol for direct evaluation questions about his work.
- `scrapling-or-death` — scrapling's actual role (explicit request or JS/Cloudflare target only).
