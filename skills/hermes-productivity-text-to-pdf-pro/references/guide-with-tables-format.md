# Format C: Guide with Pipe Tables and Tier Headers

A third plain-text document format confirmed in June 2026. Used for the "Which Model Should I Run?" VRAM guide.

## Key differences from Format A and B

| Feature | Format A (Tutorial) | Format B (Research) | Format C (Guide) |
|---------|-------------------|-------------------|-----------------|
| Rulers | `===` | `═` (U+2550) | `=` repeated |
| TOC | `WHAT YOU WILL LEARN` bullets | `TABLE OF CONTENTS` Roman numerals | **No TOC section** — content starts immediately |
| Tables | None | None | **Pipe tables** (`\| col \| col \|`) |
| Section headers | `=== WRAPPED ===` | Roman-numeral `I.` | Both `=== WRAPPED ===` AND bare ALL-CAPS |
| Tier headers | None | None | `6GB VRAM: THE STRUGGLE TIER` pattern |
| Cheat sheet | None | None | Indented `ollama run` commands after bullet items |
| Metadata | Title + subtitle + reading time | Title + subtitle + metadata block | Title + author + contact on first 3 lines |

## Structure

```
Line 1: Title (bare, no === wrappers)
Line 2: Author line
Line 3: Contact line
[=== ruler]
=== SECTION HEADER ===
[content]
=== NEXT SECTION ===
...
```

## Header detection rules specific to Format C

### Tier headers
Lines matching `^\d+GB\s+VRAM` (e.g. "6GB VRAM: THE STRUGGLE TIER", "8GB VRAM: THE BEGINNER SWEET SPOT") should be `<h4>`.

### Standalone GPU tier labels in cheat sheet
Lines matching `^\d+GB\s+VRAM$` (exact, no colon) — these appear in the cheat sheet section as section labels. Also `<h4>`.

### Cheat sheet section labels
Lines like "GPU TIER → TASK → MODEL → QUANT → OLLAMA COMMAND" — `<h4>`.

### ALL-CAPS without trailing punctuation
Some headers like "WHEN TO IGNORE Q4 AND RUN Q8 (AND VICE VERSA)" don't end in `?` or `:`. The regex `[A-Z][A-Z\s,:/'\-()&]+[A-Z)]` catches these.

## Pipe table parsing

Tables are lines starting and ending with `|`. The parser must:

1. Detect `|` as first non-whitespace char → enter table mode
2. Skip separator rows (all cells contain only `---`)
3. First data row = `<thead>`, subsequent rows = `<tbody>`
4. Close table mode on first non-`|` line

## Cheat sheet indented commands

After bullet items like "- Chat: Llama 3.2 3B Q8", the next line is an indented `ollama run` command. These should NOT be treated as indented code blocks — they're plain paragraphs. The indented-code detection must check for command keywords (`ollama`, `pip`, `from`, `import`, etc.) and only enter code mode when those keywords are present.

## Cover page

No TOC/topic list section exists in this format. The cover shows:
- GUIDE tag (not TUTORIAL)
- Title
- Author (italic)
- Contact line
- Decorative `<hr/>`

Then body content starts immediately in the padded div. No `what-learn` or `toc` div.
