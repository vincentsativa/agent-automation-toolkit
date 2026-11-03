# Format E: Tutorial with `---` Rulers, Title-Case Headers, and Pipe Tables

A fifth plain-text document format confirmed in July 2026. Used for the "Your First Agent Cron Job" tutorial.

## Key differences from Formats A-D

| Feature | Format A (Tutorial) | Format B (Research) | Format C (Guide) | Format D (Blueprint) | **Format E (Cron Tutorial)** |
|---------|-------------------|-------------------|-----------------|---------------------|------------------------------|
| Rulers | `===` | `═` (U+2550) | `=` repeated | `===` | **`---`** |
| Section headers | `=== WRAPPED ===` | Roman-numeral `I.` | Both wrapped + ALL-CAPS | `PART N:` | **Title-case** (e.g. "Why This Matters More Than Better Prompts") |
| TOC | `WHAT YOU WILL LEARN` | `TABLE OF CONTENTS` | None | "This blueprint covers" | **None** |
| Tables | None | None | Pipe tables | None | **Pipe tables** |
| Code blocks | Indented + fenced | Indented + fenced | Indented ollama commands | Indented + fenced | **Mixed indentation** (some lines not indented) |
| Footer to strip | None | None | None | None | **"FOR PI CODING ONLY" section** |
| Metadata | Title + subtitle + reading time | Title + subtitle + metadata | Title + author + contact | Title + subtitle | **Title only** (no subtitle, no author) |

## Structure

```
Line 1: Title (bare, no wrappers)
[blank line]
[paragraphs]
[--- ruler]
[section header in title case]
[content]
[--- ruler]
[next section]
...
[--- ruler]
-----------------FOR PI CODING ONLY---------DO NOT INCLUDE INSIDE OF TUTORIAL--------------------
[X Post, Pinterest, Keywords — strip this entire section]
```

## Header detection

Headers are **title-case** lines that appear after `---` rulers. They are NOT ALL-CAPS, NOT wrapped in `===`, NOT Roman numerals. Examples:

- "Why This Matters More Than Better Prompts"
- "What Cron Actually Is (30 Seconds)"
- "STEP-BY-STEP IMPLEMENTATION: HOW TO BUILD IT" (ALL-CAPS variant)
- "METHOD 1: THE LOCAL HARDWARE ROUTE (Terminal, Linux, Mac, Pi)"

**Detection strategy:** Use an exact set of known header strings rather than regex pattern matching. The document has a fixed, known set of ~14 section headers. This avoids false positives from title-case paragraphs that aren't headers.

## Footer stripping

The document has a section starting with:
```
-----------------FOR PI CODING ONLY---------DO NOT INCLUDE INSIDE OF TUTORIAL--------------------
```

Everything from this line to the end of the file must be removed before parsing. Detect by searching for the substring "FOR PI CODING ONLY" combined with "DO NOT INCLUDE".

## Pipe table parsing

Same as Format C: lines starting and ending with `|`. First data row = `<thead>`, separator row (all `---` cells) skipped, subsequent rows = `<tbody>`.

## Code block detection

This format has code blocks with **mixed indentation** — some lines are indented 4 spaces, others are not indented at all. Example:

```
# agent_job.py
def run_agent():
    # 1. Define your agent prompt
    prompt = "Analyze the news and write a summary."
    ...
if __name__ == "__main__":
    run_agent()
```

**Detection strategy:** Use a keyword-based approach. Any line that starts with a known code keyword (`def`, `import`, `from`, `class`, `# `, `if __name__`, `return`, `with open`, `print`, etc.) OR is indented 4+ spaces should be treated as code. Buffer consecutive code lines together, including blank lines within the block. Close the code block on the first non-code, non-blank line.

**Keyword list for this format:**
```
pip, from, import, class, def, curl, git, npm, uvx, playwright, cd , ls , rm , $ , echo, cat,
mkdir, touch, chmod, python, node, npx, docker, crontab, # , response, prompt, with open,
if __name__, run_agent, f.write, open(, else:, elif, try:, except, return, print, self,
break, continue, while, for , import , from , pass, yield, raise, finally
```

## Cover page

No TOC/topic list section. Cover shows:
- TUTORIAL tag
- Title
- Decorative `<hr/>`
- Short description line (optional)

Then body content starts immediately in the padded div. No `what-learn` or `toc` div.

## See also
- `scripts/cron-tutorial-to-html.py` — runnable parser for this format (installed at `~/.hermes/skills/productivity/text-to-pdf-pro/scripts/cron-tutorial-to-html.py`)
