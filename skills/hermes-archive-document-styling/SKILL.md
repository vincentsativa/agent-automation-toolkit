---
name: document-styling
description: Re-style plain-text documents into branded visual PDFs. Extract brand colors from live websites, apply dark/light themes with proper typography, parse ASCII tables, preserve cover pages, and deliver professional-looking PDFs. Trigger when user asks to make a PDF look good, style a document, branded PDF, dark theme PDF, or reportlab styling.
references:
  - references/reportlab-dark-theme-template.py
  - references/phantom-byte-colors.md
  - references/weasyprint-light-professional.css
  - references/text-to-pdf-tutorial-parser.md
  - references/text-to-pdf-agent-research-format.md
  - references/text-to-pdf-agent-containment-format.md
  - references/text-to-pdf-fpdf2-fallback.md
scripts:
  - scripts/convert-text-to-html.py
  - scripts/reportlab-dark-pdf.py
  - scripts/plain-text-to-html.py
---

# Document Styling, Branded PDF Generation

## When to Use
- User says "make this PDF look nice"
- User says "style this document" or "rebrand this PDF"
- User provides a plain-text or notepad-looking document to make professional
- User says "incorporate brand colors" into a PDF
- User wants a dark-mode PDF or themed report

## Brand Color Extraction

Extract exact hex colors from a live brand website:

```javascript
// From browser_console + expression:
(() => {
  const bodyStyles = window.getComputedStyle(document.body);
  const links = document.querySelectorAll('a');
  const h = document.querySelector('h1, h2, h3');
  return {
    backgroundColor: bodyStyles.backgroundColor,   // e.g. rgb(10, 10, 10)
    textColor: bodyStyles.color,                     // e.g. rgb(224, 224, 224)
    headingColor: h ? window.getComputedStyle(h).color : null,
    allLinkColors: Array.from(new Set(Array.from(links).slice(0,10)
      .map(a => window.getComputedStyle(a).color))),
  };
})()
```

Convert `rgb()` to hex in Python:
```python
def rgb_to_hex(s):
    m = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', s)
    return f'#{int(m.group(1)):02X}{...}'
```

## Core Palette (PhantomByte Example)
```python
BG       = HexColor("#0A0A0A")   # page background
TEXT     = HexColor("#E0E0E0")   # body text
HEADING  = HexColor("#FFFFFF")   # section headings
ACCENT   = HexColor("#00FF88")   # accent / highlights
DIM      = HexColor("#555555")   # dividers / metadata
CODE_BG  = HexColor("#141414")   # code block bg
ACCENT2  = HexColor("#1A1A1A")   # table rows / alt bg
TABLE_HDR= HexColor("#0F0F0F")   # table header bg
```

## ReportLab Dark-Theme Build Pattern

### 1. Page Templates (Cover + Inner)
```python
from reportlab.platypus import PageTemplate, NextPageTemplate

def cover_cb(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0,0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Draw cover image full-bleed with preserveAspectRatio
    canvas.drawImage(cover_path, x, y, w, h,
                     preserveAspectRatio=True, anchor='c')
    canvas.restoreState()

def dark_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0,0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.restoreState()

frame = Frame(MARGIN, MARGIN-6, PAGE_W-2*MARGIN, PAGE_H-2*MARGIN+12)
cover_pt = PageTemplate(id='cover', frames=[frame], onPage=cover_cb)
inner_pt = PageTemplate(id='inner', frames=[frame], onPage=dark_bg)
doc.addPageTemplates([cover_pt, inner_pt])
```

### 2. Story Flow (Cover → Title → Content)
```python
story.append(NextPageTemplate('cover'))
story.append(Spacer(1, 0.5*inch))
story.append(PageBreak())
story.append(NextPageTemplate('inner'))

# Title page
story.append(Spacer(1, 1*inch))
story.append(Paragraph("TITLE", PH1_BIG))
story.append(Spacer(1, 0.4*inch))
story.append(Paragraph("Subtitle", PBody))
story.append(PageBreak())
```

### 3. Styles
```python
styles.add(ParagraphStyle("PBody",
    fontName="Helvetica", fontSize=10.5, leading=14,
    textColor=TEXT, spaceAfter=6, spaceBefore=1))
styles.add(ParagraphStyle("PH1",
    fontName="Helvetica-Bold", fontSize=17, leading=22,
    textColor=ACCENT, spaceAfter=10, spaceBefore=12))
styles.add(ParagraphStyle("PH2",
    fontName="Helvetica-Bold", fontSize=12.5, leading=16,
    textColor=HEADING, spaceAfter=6, spaceBefore=9))
styles.add(ParagraphStyle("PCode",
    fontName="Courier", fontSize=8.5, leading=11.5,
    textColor=ACCENT, backColor=CODE_BG,
    leftIndent=16, rightIndent=12, spaceAfter=4))
styles.add(ParagraphStyle("PBullet",
    fontName="Helvetica", fontSize=10, leading=13,
    textColor=TEXT, leftIndent=26, firstLineIndent=-12))
styles.add(ParagraphStyle("PCell",
    fontName="Helvetica", fontSize=8, leading=10,
    textColor=TEXT, spaceAfter=0))
```

### 4. ASCII Table Parser
```python
def parse_ascii_table(lines):
    sep = next((l for l in lines if "┼" in l), None)
    dividers = [i for i, c in enumerate(sep) if c in "┼┤├┬┴"]
    data = []
    for line in lines:
        if not line.startswith("│"): continue
        cells, prev = [], 1
        for pos in dividers + [len(line)]:
            cell = line[prev:pos].strip().strip("│")
            cells.append(cell)
            prev = pos + 1
        if any(cells): data.append(cells)
    return data

def make_reportlab_table(cells, styles):
    ncols = max(len(r) for r in cells)
    cw = (PAGE_W - 2*MARGIN) / ncols
    tbl_data = []
    for ri, row in enumerate(cells):
        row_p = []
        for ci, c in enumerate(row):
            if ri == 0:
                row_p.append(Paragraph(f'<b>{esc(c)}</b>', styles["PCell"]))
            else:
                row_p.append(Paragraph(esc(c), styles["PCell"]))
        while len(row_p) < ncols:
            row_p.append(Paragraph("", styles["PCell"]))
        tbl_data.append(row_p)
    t = Table(tbl_data, colWidths=[cw]*ncols, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HDR),
        ('TEXTCOLOR', (0,0), (-1,0), ACCENT),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (-1,-1), ACCENT2),
        ('GRID', (0,0), (-1,-1), 0.35, DIM),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t
```

### 5. Content Parser Heuristics

Detect blocks in flat text:
- **Code blocks**: indented lines starting with `ollama `, `hermes `, `curl `, `docker `, `pip `, `$>`, or env vars like `KEY=value`
- **Tables**: lines starting with `┌│├└┤┬┴┼`
- **Section headers**: `1.`, `2.`, etc. or `--- Step N:` or `TABLE OF CONTENTS`
- **Bullets**: lines starting with `✅ • ❌ ✓ ✗ - * ☐`
- **FAQ**: lines starting with `Q: ` or `A: `
- **Horz dividers**: lines of only `=` or `─` characters

## Dependency
```bash
pip install reportlab Pillow
# pdf2image optional if extracting from existing PDFs
pip install PyMuPDF  # for reading existing PDF content/images
```

## Alternative: WeasyPrint HTML→PDF (Simpler for Clean Text)

When you need a good-looking PDF from flat text quickly, without parsing ASCII tables into ReportLab objects, use **HTML + CSS → WeasyPrint**. This path produces cleaner output with far less code for text-heavy documents.

### For tutorial documents, use the text-to-pdf-pro parser
This skill absorbed the `text-to-pdf-pro` skill. For converting plain-text tutorials (not markdown, not structured PDF source) into formatted WeasyPrint PDFs with cover pages, topic lists, code blocks, and strict layout rules, see:

- `references/text-to-pdf-tutorial-parser.md`, state machine for tutorial plain-text documents  
- `references/text-to-pdf-agent-research-format.md`, Roman-numeral TOC / `═` ruler format
- `references/text-to-pdf-agent-containment-format.md`, Format G: markdown `##`/`###` headers, `--- CODE EXAMPLE: X ---` fences, `☐` ballot-box items, embedded-NUL source files, and two PDF-verification false-positives (uppercase headings, pypdf trailing bullets)
- `scripts/plain-text-to-html.py`, runnable parser

### For general text documents (this skill's original workflow)
See below for the general WeasyPrint workflow.

### Workflow
1. Read the source text
2. Build a single HTML document with embedded CSS (cover page, sections, code blocks, tables, footer)
3. Render to PDF with `python3 -m weasyprint input.html output.pdf`

### Key CSS Patterns
```css
@page {
  size: A4;
  margin: 2cm 2.2cm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #888; }
}

.cover-title { font-size: 26pt; text-align: center; margin-top: 5cm; }
.page-break { page-break-before: always; }

h2.section {
  font-size: 16pt; font-weight: 700;
  border-bottom: 2pt solid #0d1b2a;
  margin-top: 28pt; margin-bottom: 12pt;
}

pre {
  background: #f4f5f7; padding: 8pt 10pt;
  border-left: 3pt solid #0d1b2a; border-radius: 3pt;
  line-height: 1.4;
}

table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
th { background: #0d1b2a; color: white; padding: 6pt 8pt; }
td { padding: 5pt 8pt; border-bottom: 1pt solid #ddd; }
tr:nth-child(even) td { background: #f8f9fb; }

.fix-block {
  background: #fef6f0; border-left: 3pt solid #c0392b;
  padding: 8pt 10pt; margin: 6pt 0; border-radius: 3pt;
}
```

### Content Parsing (Python → HTML)
Map flat text patterns to HTML tags:
- `=== ... ===` → `<h2 class="section">`
- Lines of `=` or `─` → skip (decorative rules)
- Indented commands (code) → `<pre><code>...</code></pre>`
- Unicode box-drawing tables → `<table>` with header row
- `❌/✅` bullet lines → `<div class="fix-block">`
- Lines starting with `Q:` / `A:` → bold Q, regular A paragraphs
- TOC lines → `<ol><li>` or inline paragraphs

### WSL Gotcha
WeasyPrint must be run with the **system Python** (not the hermetic Hermes venv):

```bash
# Install (system-level):
pip install --break-system-packages weasyprint

# Run:
/usr/bin/python3 -m weasyprint input.html output.pdf
# NOT: python3 -m weasyprint  (this will look in the venv)
```

### When to Use HTML+CSS vs ReportLab
| Situation | Use |
|-----------|-----|
| Text-heavy document with sections, code blocks, tables | **WeasyPrint HTML→CSS** (simpler, faster) |
| Dark theme, branded colors, custom page backgrounds | Either works |
| Complex layouts, precise positioning, multi-column | **ReportLab** (more flexible) |
| Extraction from existing PDFs, mixed image+text | **ReportLab** |

## Worked Reference

For the PhantomByte Hermes Agent Guide PDF:
- Source: flat text file (665 lines, ASCII tables, code blocks)
- Cover: 1672×941 PNG, preserved as full-bleed using `preserveAspectRatio=True`
- Output: 13-page dark-themed PDF with green accents, proper readability
- Key fix for cover page: use `NextPageTemplate('cover')` → `PageBreak()` → `NextPageTemplate('inner')`, the cover template renders via `onPage` callback with the cover image, then a short `Spacer(1, 0.5*inch)` advances onto a page break. The `PageBreak()` transitions cleanly into inner pages. Spacer must be smaller than frame height (792pt) to avoid LayoutError.

## Pitfalls
- **Cosmetic cover fix = minimal edit, NOT a rebuild (Aug 2026).** When the user reports a small visual problem on an already-generated PDF (run-on title/subtitle, missing punctuation, wrong font size) and the generated HTML exists, do the **targeted edit to the existing HTML cover block + CSS and re-render**, do NOT rebuild the parser, rewrite the build script, or re-parse the source from scratch. Real failure: user said "just shrink the subtitle text and add punctuation"; the agent rebuilt the entire Format G parser pipeline instead and got "what in the good name of fuck are you doing", the trivial fix then worked in one pass. For a run-on cover, the real title often sits in `<p class="cover-tag">` while the `<h1>` holds subtitle+description joined by `<br>`; split the `<h1>` down to the title, move the description into `<p class="cover-sub">...` with a terminal period, shrink the subtitle font (`font-size: 13pt` → `10.5pt`, dim to `rgba(255,255,255,0.75)`), then re-render `weasyprint.HTML(existing.html).write_pdf(...)`. If the HTML is gone, hand-edit the cover from extracted PDF text, don't rebuild unless explicitly asked.
- **LayoutError on Spacer too large**: The cover page Spacer must be ≤ frame height minus margins (≈ 685pt). Use `Spacer(1, 0.5*inch)` not `Spacer(1, PAGE_H)`.
- **Cover image missing**: Always check `PIL` can load and `drawImage` path is absolute.
- **Table cell overflow**: Reportlab `Paragraph` wrapping requires `keepInFrame` if cells get huge; for most tables `PCell` at 8pt with `TOP` valign works.
- **Page template ordering**: `cover_pt` must be registered before `inner_pt`. If not, `NextPageTemplate('cover')` won't find it.

## Delivery

### Telegram PDF Delivery

When sending a generated PDF via Telegram:

1. **Copy to media cache first**, Telegram delivery only works from paths under `HERMES_MEDIA_ALLOW_DIRS`:
   ```bash
   mkdir -p ~/.hermes/media_cache
   cp "output.pdf" ~/.hermes/media_cache/
   hermes config set HERMES_MEDIA_ALLOW_DIRS ~/media_cache
   ```

2. **MEDIA tag must have text context**, A bare `MEDIA:/path` as the only message content fails silently. Always include text alongside:
   ```
   Here's your PDF.
   
   MEDIA:~/media_cache/output.pdf
   ```
   
   When the MEDIA tag is processed and stripped, the text still delivers. Without surrounding text, the message is treated as empty and discarded.

3. **Confirm delivery**, After sending, note the `message_id` in the success output. If the user says they didn't receive it, the issue is almost always (2), MEDIA tag as sole content.

### Alternative Delivery Methods
- Save to Desktop for user
- Email via `email-sender` skill when requested
- Do NOT paste PDF content into chat, send just the file path or email confirmation

### Pitfall: MEDIA-Only Messages
`send_message(message="MEDIA:/path/to/file")` returns success but the platform discards it because no deliverable text remains after the MEDIA tag is processed. Always pair MEDIA with a text sentence.