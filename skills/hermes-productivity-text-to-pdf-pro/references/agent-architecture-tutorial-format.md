# Format F: Tutorial with MODULE Headers, Multi-Line Title, and Pipe Tables

A sixth plain-text document format confirmed in July 2026. Used for the "Building Model-Agnostic Agent Architecture" tutorial.

## Key differences from Formats A-E

| Feature | Format A (Tutorial) | Format B (Research) | Format C (Guide) | Format D (Blueprint) | Format E (Cron) | **Format F (Agent Architecture)** |
|---------|-------------------|-------------------|-----------------|---------------------|-----------------|-----------------------------------|
| Rulers | `===` | `═` (U+2550) | `=` repeated | `===` | `---` | **`═` (U+2550)** |
| Section headers | `=== WRAPPED ===` | Roman-numeral `I.` | Both wrapped + ALL-CAPS | `PART N:` | Title-case | **`MODULE N:` headers** + ALL-CAPS sub-headers |
| TOC | `WHAT YOU WILL LEARN` | `TABLE OF CONTENTS` | None | "This blueprint covers" | None | **`WHAT YOU WALK AWAY WITH`** (bullet list with continuation lines) |
| Tables | None | None | Pipe tables | None | Pipe tables | **Pipe tables** |
| Code blocks | Indented + fenced | Indented + fenced | Indented ollama commands | Indented + fenced | Mixed indentation | **Fenced only** (```python) |
| Metadata | Title + subtitle + reading time | Title + subtitle + metadata | Title + author + contact | Title + subtitle | Title only | **Multi-line title** (3 lines) + metadata (reading time, word count, difficulty) |
| ALL-CAPS regex | Standard | Standard | Standard | Standard | N/A | **Extended** — includes `$`, digits, periods for headers like "WHY THIS COMMANDS $14.99" |
| Bullet continuations | No | No | No | No | No | **Yes** — indented continuation lines merge into previous `<li>` |
| Checklist items | `☐ ` / `✅ ` | `☐ ` / `✅ ` | None | `[ ]` | None | **`- [ ]`** markdown-style checklists |
| Cover title | Single H1 | Single H1 | Single H1 | Single H1 | Single H1 | **Split H1 + subtitle** — first 2 lines in H1, rest in cover-sub |

## Structure

```
═══════════════════════════════════════════
BUILDING MODEL-AGNOSTIC AGENT ARCHITECTURE
A Complete Engineering Guide to ...
Intelligent Routing
═══════════════════════════════════════════

Estimated Reading Time: 35 minutes
Word Count: ~6,800
Difficulty: Intermediate to Advanced

═══════════════════════════════════════════
THE PROBLEM
═══════════════════════════════════════════

[content]

═══════════════════════════════════════════
WHAT YOU WALK AWAY WITH
═══════════════════════════════════════════

- A provider-abstraction interface you can drop into an existing agent.
- Working swap code: move from one model vendor to another without rewriting
  prompts or tool calls.
- ...

═══════════════════════════════════════════
MODULE 1: WHY SINGLE-PROVIDER STACKS ARE A LIABILITY
═══════════════════════════════════════════

**The 12-Month Lead Is Now a 7-Week Lead**

[content]

═══════════════════════════════════════════
WHY THIS COMMANDS $14.99
═══════════════════════════════════════════
```

## Cover title handling (CRITICAL)

Multi-line titles (3+ lines) must be split into H1 + subtitle. Do NOT join all lines into one H1 — the user rejected this as unreadable.

```python
# Split: first 2 lines = H1, rest = cover-sub
if len(title_parts) >= 2:
    main_title = title_parts[0] + " " + title_parts[1]
    if len(title_parts) > 2:
        subtitle = " ".join(title_parts[2:])
```

The `<title>` tag uses `main_title` only (not the full joined string).

## Header detection

Three levels:

1. **MODULE N: headers** — `MODULE 1: WHY SINGLE-PROVIDER STACKS...` → `<h2>`
2. **Wrapped ALL-CAPS** — `=== THE PROBLEM ===` or `════ WHY THIS COMMANDS $14.99 ════` → `<h2>` (strip `═= ` wrappers)
3. **ALL-CAPS sub-headers** — `THE PROBLEM`, `WHAT YOU WALK AWAY WITH`, `WHY THIS COMMANDS $14.99` → `<h3>`
4. **Bold short lines** — `**The 12-Month Lead Is Now a 7-Week Lead**` → `<h4 class="bold-heading">`

## ALL-CAPS regex for this format

Extended to include `$`, digits, and periods:

```python
r"[A-Z][A-Z\d\s,:/'\-&$.]+(\?|:)?$"
```

This catches headers like:
- `WHY THIS COMMANDS $14.99` (contains `$` and `.`)
- `MODULE 1: WHY SINGLE-PROVIDER STACKS ARE A LIABILITY` (caught by MODULE pattern first)
- `WHAT YOU WALK AWAY WITH` (standard ALL-CAPS)

## Bullet continuation lines

The "WHAT YOU WALK AWAY WITH" section has multi-line bullets where the continuation is indented:

```
- A provider-abstraction interface you can drop into an existing agent.
- Working swap code: move from one model vendor to another without rewriting
  prompts or tool calls.
```

The parser must detect indented lines following a bullet and merge them into the previous `<li>` element. Detection: `rawline.startswith("  ") and in_bullet_list and stripped`.

## Pipe table parsing

Same as Format C/E: lines starting and ending with `|`. First data row = `<thead>`, separator row (all `---` cells) skipped, subsequent rows = `<tbody>`.

## Code block detection

This format uses **fenced code blocks only** (```python ... ```). No indented code blocks. The parser should handle empty lines inside fenced blocks without closing the block.

## Cover page

- TUTORIAL tag
- H1 with first 2 lines of title
- cover-sub with remaining title lines (subtitle)
- Decorative `<hr/>`
- cover-meta with metadata (reading time, word count, difficulty)
- "WHAT YOU WILL LEARN" section with bullet items

## Last-page handling

The final section ("WHY THIS COMMANDS $14.99") is preceded by a checklist. If the last page has fewer than ~12 lines, force a page-break before the checklist to push it to a fresh page with the closing section.

## See also
- `scripts/build-agent-tutorial-to-html.py` — runnable parser for this format
