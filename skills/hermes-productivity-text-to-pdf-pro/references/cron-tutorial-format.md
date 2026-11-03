# Format C: Cron Tutorial / Title-Case Headers with Pipe Tables

This reference documents a third plain-text tutorial format discovered during the "Your First Agent Cron Job" PDF conversion.

## Key differences from Format A and B

| Feature | Format A | Format B | Format C |
|---------|----------|----------|----------|
| Rulers | `===`, `───` | `═` (U+2550) | `---` |
| Section headers | ALL-CAPS or `=== WRAPPED ===` | Roman numerals (I., II.) | Title-case ("Why This Matters...") |
| Tables | None | None | Pipe tables (`\| col \| col \|`) |
| Footer to strip | None | None | "FOR PI CODING ONLY" section |
| Code blocks | Fenced (```) + indented | Indented only | Indented + keyword-detected |

## Detection strategy for Format C

### Section headers
Not ALL-CAPS, not Roman numerals, they're title-case phrases. Use an **exact match set** rather than regex patterns:

```python
SECTION_HEADERS = {
    "Why This Matters More Than Better Prompts",
    "What Cron Actually Is (30 Seconds)",
    "Why Agents and Cron Were Made for Each Other",
    ...
}
```

This is more reliable than trying to regex-match title-case headers, which would collide with normal paragraphs.

### Pipe tables
Lines starting and ending with `|` are table rows. Separator rows (`|---|---|`) close the `<thead>` and open `<tbody>`.

```python
if stripped.startswith("|") and stripped.endswith("|"):
    cells = [c.strip() for c in stripped.split("|")[1:-1]]
    if all(c.replace("-", "").strip() == "" for c in cells):
        # separator row, close thead, open tbody
    else:
        # data row
```

### Footer stripping
Scan for a line containing both "FOR PI CODING ONLY" and "DO NOT INCLUDE", truncate all lines after it.

### Code block detection
This format has code blocks where some lines are indented (4 spaces) and some are not (e.g. `def run_agent():` starts at column 0, but `    prompt = ...` is indented). Use a **keyword-based** approach:

```python
CODE_KEYWORDS = ("pip", "from", "import", "class", "def", "curl", "git",
                 "npm", "uvx", "playwright", "cd ", "ls ", "rm ", "$ ",
                 "echo", "cat", "mkdir", "touch", "chmod", "python",
                 "node", "npx", "docker", "crontab", "# ", "response",
                 "prompt", "with open", "if __name__", "run_agent",
                 "f.write", "open(", "else:", "elif", "try:", "except",
                 "return", "print", "self", "break", "continue",
                 "while", "for ", "import ", "from ", "pass", "yield",
                 "raise", "finally")
```

Buffer consecutive lines that are either indented OR start with a code keyword. Blank lines inside the buffer are kept (they're part of the code). Close the buffer when a non-code, non-indented line is hit.

### Cover page
This format has no "WHAT YOU WILL LEARN" or "TABLE OF CONTENTS" section. The cover just has the title + a short description paragraph. No topic list needed.

## CSS additions for pipe tables

```css
table {
  width: 100%; border-collapse: collapse; margin: 8pt 0;
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt;
}
th {
  background: #415a77; color: #fff; padding: 5pt 8pt;
  text-align: left; font-weight: 700;
}
td {
  padding: 4pt 8pt; border-bottom: 1px solid #d0d5dd;
}
tr:nth-child(even) td { background: #f4f6f8; }
```

## Pitfalls

1. **Blank lines inside code blocks**, The code block in this tutorial has blank lines between function body and `if __name__`. The parser must NOT close the code block on empty lines when `in_code_block` is True. Empty lines should be appended to the buffer, not trigger `close_all()`.
2. **Non-indented code lines**, `def run_agent():` and `if __name__ == "__main__":` are not indented but are code. The keyword-based detection catches these.
3. **Pipe table separator rows**, `|---|---|---|` must be detected and handled (close thead, open tbody), not rendered as a data row.
4. **Asterisks in cron expressions**, `0 8 * * *` gets mangled by inline markdown processing (`*...*` becomes `<em>`). The cron expression lines in this document are plain paragraphs, not code, they need to be escaped but NOT have their `*` treated as emphasis. The `escape_inline()` function's `\*(.+?)\*` regex will match `* * *` patterns. **Fix:** escape the line first with `html.escape()`, then only apply the bold/italic/code regexes. Since `html.escape` converts `*` to `*` (it doesn't), the real fix is to NOT apply the italic regex to lines containing cron expressions. A simpler approach: apply inline formatting only to lines that don't match `\d+ \*` patterns.

## See also
- `scripts/cron-tutorial-to-html.py`, working parser for this format
- `references/plain-text-tutorial-parsing.md`, Format A and B details
