# Plain-Text Tutorial Parsing: State Machine Approach

This reference documents the parser approach for converting plain-text tutorial documents (non-markdown, non-HTML) into professionally formatted PDFs. The key challenge: plain text has no explicit structure markers — the parser must infer sections, headers, code blocks, lists, and checklists from content patterns alone.

## Two confirmed format variants

### Format A: Scrapling / Firefox Rotunda tutorial
`.txt` file with `===` decorative rulers, `=== ALL-CAPS HEADERS ===`, `PART ONE:`, and indented code blocks.

Features: ALL-CAPS section headers, `PART ONE:` dividers, decorative rulers (`===`, `---`, `───`), fenced code blocks (```), indented code blocks (4-space indent + command keywords), bullet lists (`- `), numbered lists (`1. `), checkboxes (`☐ ` / `✅ `), and sub-section lines (`Example 1 --`, `TIER 1 --`, `Scenario A --`).

### Format B: Agent-Powered Research tutorial
`.txt` file with ═ (U+2550) box-drawing rulers, Roman-numeral TOC and headers, TABLE OF CONTENTS landmark, tutorial metadata at top.

Features: ═ rulers, Roman-numeral top-level sections, `TABLE OF CONTENTS` landmark, STEP/USE CASE/OPTION sub-section markers.

## Shared detection rules

### Ruler regex
Must handle both formats: `[═\u2550\-=\u2500]{3,}`. Missing U+2550 leaves stray ruler lines rendered as paragraphs.

### TOC / topic list extraction
Two possible landmarks:
- **Landmark A:** `WHAT YOU WILL LEARN` or `=== WHAT YOU WILL LEARN ===` → follow by `- ` bullet items
- **Landmark B:** `TABLE OF CONTENTS` between ruler lines → follow by Roman-numeral lines (`I.  Title...`)

### Roman-numeral section headers
`^[IVXL]+\d*\.\s+.+` → emit as `<h2>` with full text including the Roman numeral.

## State machine design

```python
in_code_block = False     # fenced or indented
in_bullet_list = False    # - / * / •
in_numbered_list = False  # 1. 2. 3. (span-based, not <ol>)
in_checklist = False       # ☐ / ✅

def close_all():  # call before non-container elements
```

## Detection order (MUST be in this sequence)

1. **Empty lines** — close all containers, zero output. No `<p>&nbsp;</p>`.
2. **Decorative rulers** — `^[═\u2550\-=\u2500]{3,}$`. Skip entirely.
3. **Fenced code blocks** — lines starting/ending with ` ``` `.
4. **PART headers** — `^PART\s+(ONE|TWO|THREE|FOUR|FIVE|SIX)\b`. Emit `<h2>`.
5. **Roman-numeral section headers** — `^[IVXL]+\d*\.\s+[A-Z]`. Emit `<h2>`.
6. **Wrapped ALL-CAPS headers** — `=+\s+.*\s+=+`. Strip `=` wrappers → `<h2>`.
7. **ALL-CAPS headers** — `^[A-Z][A-Z\s,:/'\-]+(\?|:)$`. Emit `<h3>`.
8. **Sub-sections** — `^(Example \d+|TIER \d|Scenario [A-Z]|Use |Do NOT |AFTER |THE POWER|STEP \d+:|USE CASE \d+:|OPTION \d+:|PICK THIS|THE CHALLENGE|THE FINAL LINE|A HONEST NOTE|THE ONLY TOOL|Recommended |For the next)`. Emit `<h4>`.
9. **Short bold lines** — `^\*\*[^*]+\*\*$`, len < 80. Emit `<h4 class="bold-heading">`.
10. **Checklists** — starts with `☐ ` or `✅ `. `<ul class="checklist">`.
11. **Bullets** — starts with `- `, `* `, `• `. `<ul>`.
12. **Numbered items** — `^\d+\.\s+`. `<p class="num-item">`.
13. **Q&A pairs** — starts with `Q: ` or `A: `. `<p><strong>Q:</strong> ...</p>`.
14. **Indented code** — 4+ spaces + command keywords. `<pre><code>`.
15. **Normal paragraphs** — escape HTML first, THEN apply `**bold**`, `*italic*`, `` `code` ``.

## Cover page design (confirmed working)

Cover gradient + topic list on page 1 together. No forced page break.

```html
<div class="cover-wrap"> ...gradient + title... </div>
<div class="what-learn">
  <h2>IN THIS TUTORIAL</h2>
  <ul>...</ul>
</div>
```

```css
@page:first { margin: 0; @bottom-center { content: none; } }
.cover-wrap { background: linear-gradient(150deg, #1b263b 0%, #415a77 80%, #556e8a 100%); }
```

## Inline formatting helper
```python
def escape_inline(p):
    p = html.escape(p)
    p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
    p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
    return p
```

## Last-page check
```python
from pypdf import PdfReader
reader = PdfReader(pdf_path)
last_page = reader.pages[-1]
txt = last_page.extract_text()
lines = [l for l in txt.split('\n') if l.strip()]
if len(lines) < 12:  # force page-break before last major block
```

## Color palette
- Gradient: `#1b263b` → `#415a77`
- Code border: `3px solid #415a77`
- Section underline: `2px solid #415a77`
- Code bg: `#f4f6f8`
- Body: `#1a1a1a`

## See also
- `references/agent-powered-research-format.md` — Format B details (Roman TOC, ═ rulers, broader sub-section patterns)