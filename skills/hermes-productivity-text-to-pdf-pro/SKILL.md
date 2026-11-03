---
name: text-to-pdf-pro
description: Convert text documents, guides, and markdown into professionally formatted PDFs. Covers parsing, HTML styling, WeasyPrint rendering, table/code formatting, cover pages, and optional email delivery.
trigger: "user asks to convert text to PDF, make a PDF, format a guide as PDF, create a professional PDF, or email a PDF"
---

# Text-to-PDF Pro Skill

## When to Use
- Converting `.txt`, `.md`, or plain-text documents into polished PDFs
- Formatting guides, reports, or documentation for delivery
- Emailing the final PDF via IONOS SMTP
- Replacing em dashes, fixing typography, styling tables and code blocks

## Prerequisites
- `weasyprint` Python package: `pip install weasyprint`
- Working SMTP credentials (if emailing)
- Fonts: Liberation Serif/Sans/Mono (fallback to Georgia/Arial/Consolas)

## CRITICAL RULES (Read Before Acting)

1. **ALWAYS use the WeasyPrint HTML->CSS pipeline.** When this skill is loaded, follow it exactly. Do NOT write custom PDF scripts from scratch (fpdf2, reportlab, manual page-drawing). Raw fpdf2 has repeatedly failed for this user's tutorial documents -- dropped sections, wrong page counts (4 pages instead of 6+), broken typography, and was explicitly rejected. WeasyPrint + inline CSS is the only path consistently approved. Body text: minimum 11pt serif, line-height 1.45-1.55.

2. **Cover is a compact banner, NOT a full page.** The cover should be a gradient banner at the top of page 1 with the title, subtitle, description, and Steps 1-2 inline. Step 3 starts on the next page. Do NOT use `height: 100vh` or `page-break-after: always` on the cover. The cover should take up about 1/4 to 1/3 of page 1, with the body content flowing naturally below it on subsequent pages.

   **NEW COVER TEMPLATE:**
   ```html
   <div class="cover">
     <p class="cover-tag">PhantomByte</p>
     <h1>Fix Your Email Deliverability</h1>
     <p class="cover-sub">The Complete SPF, DKIM &amp; DMARC Setup Guide</p>
     <hr/>
     <p class="cover-desc">A practical field manual. Run the checker. Find the matching section. Do the steps. Verify. Done.</p>
     <div class="cover-steps">
       <h4>Before you start, do these three things:</h4>
       <p><strong>Step 1.</strong> Run the PhantomByte checker at phantom-byte.com/email-domain-checker. Save your results.</p>
       <p><strong>Step 2.</strong> Identify your DNS provider (where you edit DNS records). Check the list in Step 2 below.</p>
     </div>
   </div>
   <div class="content">
     <h3 class="step">STEP 3. IDENTIFY EVERY SERVICE THAT SENDS MAIL AS YOUR DOMAIN</h3>
     ... step 3 content ...
   </div>
   ```

   The `.cover` class uses `padding: 24pt 40pt 20pt 40pt; margin-bottom: 18pt;`, no forced page breaks. The `.content` div holds all body content starting from Step 3.

3. **Body content div goes AFTER cover-wrap, not inside it.** The HTML structure for page 1 is:
   ```html
   <div class="cover-wrap">
     <p class="cover-tag">...</p>
     <h1>...</h1>
     <p class="cover-sub">...</p>
     <hr/>
     <p class="cover-desc">...</p>
   </div>
   <div class="what-learn">
     <h2>IN THIS GUIDE</h2>
     <ul>...TOC items...</ul>
   </div>
   <div style="padding: 0 48pt 24pt 48pt;">
     ...article body (h2, h3, p, pre, ul, table)...
   </div>
   ```
   The cover-wrap div is self-contained with just the gradient content. The TOC and body are separate divs below it. Do NOT nest the body inside the cover-wrap -- that puts the article text on the gradient background and looks wrong. The gradient should only cover the top portion of page 1 (title, subtitle, description). The body text gets a clean white background.

4. **No half-pages, no forced page breaks.** PART ONE, PART TWO, etc. are styled `<h2>` headings with a colored underline -- not chapter breaks. Let natural pagination handle everything. Do not add `page-break-before: always` between sections unless the last page is genuinely empty (less than ~12 lines).

5. **Blank lines produce ZERO output.** Never emit `<p>&nbsp;</p>` for empty source lines. WeasyPrint renders them as stray bullets at the bottom of pages. Empty lines should close all open containers and produce no HTML output at all.

6. **Dense, tight layout.** Prefer efficient packing over spacious whitespace. 11pt body + 1.45-1.55 line-height + standard margins fills pages naturally. Don't add extra padding trying to "look nice."

7. **Last page must be substantial.** After generating the PDF, extract text from the last page. If it has fewer than ~12 lines of real content (just a header + trailing bullets or footer), force a page-break before the last major content block and re-generate.

8. **Multi-line titles must be split into H1 + subtitle on the cover.** When a tutorial has a title that spans 3+ lines, do NOT join them all into one H1. Split: first 2 lines go in `<h1>`, remaining lines go in `<p class="cover-sub">`. A single-line H1 that wraps across the page is unreadable and will be rejected.

## Pre-processing

### Em Dash Replacement (CRITICAL -- User Preference)
```python
text = text.replace('\u2014', '\u2013')  # em dash -> en dash
```
Do this BEFORE splitting into lines. The user explicitly hates em dashes. They must NEVER appear in any output -- PDFs, titles, descriptions, body text, anything. Always replace with en dashes, hyphens, or commas. This applies to both source text AND any text you generate yourself (cover descriptions, metadata, titles).

## Parsing Workflow

### Step 1: Read the source
```python
with open(src_path, 'r', encoding='utf-8') as f:
    text = f.read()
```
Always use `utf-8`.

### Step 2: Extract cover/TOC bullets
Tutorials have TWO possible TOC landmarks:

**Landmark A:** A line like `WHAT YOU WILL LEARN` or `=== WHAT YOU WILL LEARN ===`, followed by bullet items and then a section divider.

**Landmark B:** A line like `TABLE OF CONTENTS` between decorative rulers, followed by Roman-numeral TOC entries (`I.   The 3-Hour Problem...`).

Extract the bullets/items that follow either landmark. These get rendered under the cover gradient on page 1. The section heading should use `IN THIS TUTORIAL` (not always `WHAT YOU WILL LEARN`).

### Step 3: Parse body -- detection order (CRITICAL)

Scan line-by-line with these states:
```python
in_code_block = False     # fenced or indented
in_bullet_list = False    # - / * / bullet
in_numbered_list = False  # 1. 2. 3. (uses span-based rendering, not <ol>)
in_checklist = False      # checkbox / checkmark
```

Check in this **exact order** to avoid mis-classification:

1. **Empty lines** -- `close_all()`, produce zero output
2. **Decorative rulers** -- `^[═\\u2550\\-=\\u2500]{3,}$`. Skip entirely (no `<hr/>`). Close open containers and continue. **Must include ═ (U+2550) -- some tutorial files use box-drawing characters, not plain hyphens/equals.**
3. **Fenced code blocks** -- lines starting/ending with triple backticks. Toggle `in_code_block`.
4. **PART headers** -- `^PART\\s+(ONE|TWO|THREE|FOUR|FIVE|SIX)\\b`. Emit `<h2 class="part-h2">`. **No forced page break.**
5. **Roman-numeral section headers** -- e.g. `I. THE 3-HOUR PROBLEM...` or `VIII. THE 5-MINUTE HABIT...`. Detect via `^[IVXL]+\\d*\\.\\s+[A-Z]`. Emit `<h2>`. These appear in tutorial files that use Roman numerals for top-level sections.
6. **Wrapped ALL-CAPS section headers** -- `=+\\s+.*\\s+=+` (e.g. `=== THE 30-SECOND ANSWER ===`). Strip the `=` wrappers and emit as `<h2>`. These appear frequently.
7. **Plain ALL-CAPS section headers** -- `^[A-Z][A-Z\\s,:/'\\-&]+(\\?|:)?$` (e.g. "WHAT IS SCRAPLING?", "WHERE TO GET IT", "RESOURCES & LINKS", "POST-SETUP: MODEL EXPANSION PLAN"). Emit `<h3>`. The regex must include `&` for documents with ampersands in headers, and make trailing `?`/`:` optional for headers like `RESOURCES & LINKS` that have no punctuation.
8. **Sub-sections** -- broader patterns: `^(Example \\d+|TIER \\d|Scenario [A-Z]|Use |Do NOT |AFTER |THE POWER|STEP \\d+:|USE CASE \\d+:|OPTION \\d+:|PICK THIS|THE CHALLENGE|THE FINAL LINE|A HONEST NOTE|THE ONLY TOOL|Recommended |For the next)`. Emit `<h4>`.
9. **Short bold lines** -- `^\\*\\*[^*]+\\*\\*$` and `len < 80`. Emit `<h4 class="bold-heading">`.
10. **Checklists** -- starts with checkbox or checkmark. Buffer into `<ul class="checklist">`.
11. **Bullets** -- starts with `- `, `* `, or bullet. Buffer into `<ul class="std">`.
12. **Numbered items** -- `^\\d+\\.\\s+`. Emit `<p class="num-item">` with `<span class="num">`.
13. **Q&A pairs** -- starts with `Q: ` or `A: `. Emit `<p><strong>Q:</strong> ...</p>`.
14. **Indented code** -- consecutive lines starting with 4+ spaces containing command keywords (`pip`, `from`, `import`, `class`, `def`, `$ `, `curl`, `git`, `npm`, `uvx`, `playwright`, `# `). Buffer as `<pre><code>`.
15. **Normal paragraphs** -- everything else. Buffer consecutive paragraph lines and join them into a single `<p>` tag. Do NOT emit one `<p>` per line -- that produces fragmented, unreadable paragraphs where every sentence starts on a new line. Escape HTML entities first, THEN apply `**bold**`, `*italic*`, `` `code` `` inline formatting. Flush the paragraph buffer on any non-paragraph element (header, code block, list, ruler, empty line). **REAL INCIDENT (Aug 2026):** emitting one `<p>` per source line made every wrapped sentence its own block -- Vinny called it "the text is laid out funny... sentences are split up." The `<p>` count was 568 (one per line) and the PDF inflated from 23 to 33 pages. After joining consecutive lines into single paragraphs, `<p>` count dropped to 143 and the doc was 23 pages. **Bullets follow the same rule:** accumulate consecutive `- ` items into ONE `<ul class="std">`, do NOT call flush per item or you get one list per bullet.

### Step 4: Build HTML with inline CSS

**NEW COVER TEMPLATE (compact banner + inline steps):**

The cover should be a compact banner at the top of page 1, NOT a full page. Steps 1-2 go inline in the cover area. Step 3 onward flows on the next page.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>...</title>
<style>
@page {
  size: letter;
  margin: 0.8in 0.8in 1in 0.8in;
  @bottom-center {
    content: "Page " counter(page);
    font-family: "Liberation Sans", Arial, sans-serif;
    font-size: 9pt;
    color: #666;
    margin-bottom: 0.3in;
  }
}
body {
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #1a1a1a;
  margin: 0;
  padding: 0;
}
.cover {
  background: linear-gradient(150deg, #2d1b4e 0%, #5c3d8a 60%, #9D4EDD 100%);
  color: #fff;
  padding: 24pt 40pt 20pt 40pt;
  margin-bottom: 18pt;
}
.cover-tag {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 10pt;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
  margin: 0 0 8pt 0;
}
.cover h1 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 22pt;
  font-weight: 700;
  color: #fff;
  line-height: 1.15;
  margin: 0 0 6pt 0;
}
.cover-sub {
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 12pt;
  color: rgba(255,255,255,0.9);
  font-style: italic;
  margin: 4pt 0 10pt 0;
}
.cover hr {
  border: none;
  border-top: 1.5px solid rgba(255,255,255,0.4);
  width: 100px;
  margin: 0 auto 10pt auto;
}
.cover-desc {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt;
  color: rgba(255,255,255,0.75);
  line-height: 1.5;
  margin: 0;
}
.cover-steps {
  margin-top: 10pt;
  padding-top: 8pt;
  border-top: 1px solid rgba(255,255,255,0.3);
}
.cover-steps h4 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 10pt;
  color: rgba(255,255,255,0.9);
  margin: 0 0 4pt 0;
  font-weight: 700;
}
.cover-steps p {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt;
  color: rgba(255,255,255,0.75);
  line-height: 1.4;
  margin: 2pt 0;
}
.content {
  padding: 0 48pt;
}
.cover-wrap .what-learn { text-align: left; margin-top: 20pt; }
.cover-wrap .what-learn h2 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 13pt; color: rgba(255,255,255,0.9); margin: 0 0 7pt 0;
  border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 3pt;
}
.cover-wrap .what-learn ul { margin: 0 0 4pt 0; padding-left: 18pt; }
.cover-wrap .what-learn li { font-size: 10.5pt; margin-bottom: 2pt; color: rgba(255,255,255,0.85); }
.cover-tag {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 10pt; letter-spacing: 4px; text-transform: uppercase;
  color: rgba(255,255,255,0.65); margin: 0 0 14pt 0;
}
.cover-wrap h1 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 28pt; font-weight: 700; color: #fff; line-height: 1.15;
  margin: 0 0 8pt 0;
}
.cover-sub {
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 13pt; color: rgba(255,255,255,0.85); font-style: italic;
  margin: 4pt 0 12pt 0;
}
.cover-wrap hr {
  border: none; border-top: 1.5px solid rgba(255,255,255,0.35);
  width: 100px; margin: 0 auto 12pt auto;
}
.cover-desc {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt; color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0;
}
h2 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 14pt; color: #1b263b; margin: 22pt 0 10pt 0;
  border-bottom: 2px solid #415a77; padding-bottom: 4pt;
  page-break-after: avoid;
}
h3 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 12pt; color: #415a77; margin: 16pt 0 6pt 0;
  page-break-after: avoid;
}
h4 {
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 11pt; color: #1b263b; margin: 11pt 0 4pt 0;
  font-weight: 700;
  page-break-after: avoid;
}
p {
  text-align: justify; orphans: 3; widows: 3; margin: 5pt 0;
}
pre {
  background: #f4f6f8; border-left: 3px solid #415a77;
  padding: 7pt 9pt; font-family: "Liberation Mono", Consolas, monospace;
  font-size: 8.5pt; line-height: 1.35; white-space: pre-wrap;
  margin: 6pt 0;
}
code {
  font-family: "Liberation Mono", Consolas, monospace;
  font-size: 9pt; background: #eef0f3; padding: 1pt 3pt;
}
pre code { background: transparent; padding: 0; font-size: 8.5pt; }
ul.std { margin: 4pt 0 6pt 0; padding-left: 18pt; }
ul.std li { margin-bottom: 2pt; font-size: 10.5pt; }
p.num-item { margin: 3pt 0; padding-left: 26pt; text-indent: -26pt; }
span.num { display: inline-block; width: 22pt; font-weight: 700; color: #415a77; }
strong { font-weight: 700; color: #1b263b; }
table {
  width: 100%; border-collapse: collapse; margin: 8pt 0;
  font-size: 9.5pt;
}
th {
  background: #1b263b; color: #fff; padding: 5pt 7pt;
  font-family: "Liberation Sans", Arial, sans-serif;
  text-align: left; font-weight: 600;
}
td { padding: 4pt 7pt; border-bottom: 1px solid #ddd; }
tr:nth-child(even) td { background: #f4f6f8; }
</style>
</head>
<body>
<div class="cover-wrap">
  ... cover content (tag, h1, subtitle, hr, desc, what-learn with TOC) ...
</div>
<div style="padding: 0 48pt; page-break-before: always;">
  ... parsed body content ...
</div>
</body>
</html>
```

### Step 5: Render and verify
```python
from weasyprint import HTML
HTML('/tmp/doc.html').write_pdf('/tmp/doc.pdf')

from pypdf import PdfReader
reader = PdfReader('/tmp/doc.pdf')
print(f"Pages: {len(reader.pages)}")
# Extract last page text -- if <12 lines, force page-break before last major block and re-render
```

### Step 6: Email (if requested)
Use the `email-sender` skill. Write the SMTP script to a file, then execute it. Do NOT use `python3 -c "..."` inline -- that fails with `SMTPAuthenticationError`.

## Pitfalls

1. **WeasyPrint not installed in correct venv** -- always `pip install weasyprint` in the active Python environment. Verify with `python3 -m pip show weasyprint`.
2. **PEP 668 prevents system `pip3` install** -- On Debian/Ubuntu, `pip3 install foo` fails with PEP 668 message. Use `uv pip install weasyprint pypdf` instead.
3. **`python3 -c` inline fails for SMTP** -- write script to a `.py` file first.
4. **Em dashes leaking through** -- global `.replace('\u2014', '\u2013')` on source text. The user explicitly hates em dashes. This replacement is mandatory, not optional. Also check any text you generate yourself (cover descriptions, metadata, titles) for em dashes.
5. **Code blocks eating adjacent paragraphs** -- only consume clearly code lines (indented + command keywords). Stop on first non-matching line.
6. **Missing fonts** -- ensure `libpango` / `fonts-liberation` packages are present on Linux.
7. **Half blank pages** -- never use `min-height: 80vh` in CSS (invalid in WeasyPrint). Use padding on the cover container instead.
8. **Windows-path source files** -- Always check both the literal path AND the parent directory. OneDrive Desktop folders on Windows may have different names than the file implies. Use `ls -la '/mnt/c/Users/*/OneDrive/Desktop/' | grep -i <keyword>` to discover actual locations.
9. **Cover + TOC on separate pages** -- Putting the cover on page 1 and the table of contents on page 2 was explicitly rejected. They belong on the same page without a forced break.
10. **Writing custom PDF scripts instead of using WeasyPrint** -- Raw fpdf2 or manual page-drawing code has repeatedly failed for this user's tutorial documents: dropped sections, wrong page counts, typography issues, explicit rejection every time. When `text-to-pdf-pro` is loaded, the WeasyPrint HTML/CSS pipeline is mandatory.
11. **Not reading `references/` files before coding** -- This skill ships with reference files for each document format. Writing a parser from scratch without reading the relevant reference has produced broken section detection and missing content. Always load every linked reference file before writing implementation code.
12. **Assuming all tutorials use "WHAT YOU WILL LEARN"** -- Some tutorials have a "TABLE OF CONTENTS" section with Roman-numeral items instead. Detect either landmark. Failing to detect TOC produces empty topic lists and breaks the cover layout.
13. **Missing box-drawing character in ruler regex** -- Decorative rulers in some tutorial files use ═ (U+2550) instead of = or -. A regex limited to `[\\-=\\u2500]{3,}` misses them. Use `[═\\u2550\\-=\\u2500]{3,}`.
14. **`page-break-inside: avoid` on code blocks causes half-blank pages** -- When a `<pre>` block is too large for the remaining space on a page, WeasyPrint pushes the ENTIRE block to the next page while the heading introducing it stays behind. Result: a page with nothing but a lone heading and 2-3 lines. Never apply `page-break-inside: avoid` to code blocks in WeasyPrint. Let them split naturally across pages.
25. **TOC items must be extracted BEFORE building the cover HTML.** If the cover HTML is assembled first and the TOC items are extracted from a second pass over the source, the TOC list will be empty. Extract all TOC items (Part headers, Roman-numeral entries, or bullet items) in the first pass over the source lines, before any HTML is emitted. The cover div and TOC list are built together in one f-string.

26. **CRITICAL: Do NOT overcomplicate the layout.** The user wants a simple structure: gradient cover at the top of page 1, TOC below it, body flows naturally. Do NOT add forced page breaks, do NOT nest the body inside the cover-wrap, do NOT add min-height or other hacks. If the user says "get closer to the end of the page" or "page one is blank", the fix is to REMOVE the forced page break, not to restructure the entire HTML. Run the script, check the output with PdfReader, and make ONE small adjustment. If you need more than 2 iterations, you are overcomplicating it.

27. **CRITICAL: Verify your own output before sending to the user.** After generating the PDF, check page 1 content with PdfReader. If page 1 has fewer than 20 lines of content or has a forced page break pushing body to page 2, fix it before emailing. Do not send broken output and wait for the user to tell you it's wrong. The user checks your work and will fire you if you keep sending garbage.
16. **Last page sparseness: force page-break before the last major content block.** After rendering, check the last page with `PdfReader`. If it has fewer than ~12 lines of real content, identify the last major content block (e.g. "D. Recommended Reading" or "Resources & Links") and add `style="page-break-before: always;"` to its heading. Re-render and verify. This pushes the block to a fresh page where it fills out properly.
17. **Pipe tables in markdown source need manual HTML rendering.** WeasyPrint does not render markdown pipe tables. The parser must detect lines starting with `|`, collect them into a buffer (header row, separator row, data rows), and emit `<table><thead><tr><th>...</th></tr></thead><tbody><tr><td>...</td></tr></tbody></table>`. Flush the table buffer on the first non-pipe line. Table cells split on `|` with `[1:-1]` slice to strip leading/trailing pipes.
18. **Generic parser fails on guide documents with tables** -- The `plain-text-to-html.py` script collects everything before the first `===` wrapped header into the subtitle field, leaving the body empty. Guide documents have title + author + contact on the first 3 lines, then a ruler, then body content. Use `guide-to-html.py` for this format instead.
19. **Forgetting to apply page-1 cover style for title/subtitle** -- The cover needs the TUTORIAL tag, h1 title, italic subtitle line, then the metadata line (reading time, word count, difficulty). All in the gradient cover-wrap div before the what-learn section.
20. **ALL-CAPS header regex missing `&` and optional trailing punctuation** -- Blueprint-style documents have headers like `RESOURCES & LINKS` or `POST-SETUP: MODEL EXPANSION PLAN`. The old regex `[A-Z][A-Z\\s,:/'\\-]+(\\?|:)$` misses `&` and lines without trailing `?`/`:`. The updated regex is `[A-Z][A-Z\\s,:/'\\-&]+(\\?|:)?$`.
21. **Blueprint/guide documents (Format D) need their own parser** -- Documents with `PART N:` headers, `TIER N:` headers, `[ ]` checkboxes, and spec-list sections (CPU:/GPU:/RAM:) are not handled by `guide-to-html.py` or `plain-text-to-html.py`. Use `scripts/blueprint-to-html.py` for this format. Key differences: PART headers use decimal numbers (0, 1, 2...) not Roman numerals; TOC is extracted from "This blueprint covers" paragraph bullets; sub-section headers include PHASE, WEEK, MINIMUM SPECS, PROS, CONS, BEST FOR, CURRENT LINEUP, etc.; code keywords include `wget`, `sudo`, `export`, `openclaw`.
22. **Spec labels must be rendered as bold labels, not plain paragraphs** -- Vinny rejected the first PDF as "textual diarrhea" because spec lines were plain `<p>` tags. The `blueprint-to-html.py` script must detect lines matching `^(CPU|GPU|MOBO|RAM|STORAGE|PSU|CASE|COOLER|COOLING|TOTAL):\\s*(.*)$` and emit `<p class="spec"><strong>Label:</strong> value</p>`. Indented continuation lines (the pipe-separated details on the next line) should be `<p class="spec-cont">` so they visually group with the spec label.
23. **Format E (tutorial with `---` rulers and title-case headers) needs a custom parser** -- The generic `plain-text-to-html.py` script does NOT handle `---` rulers (it only matches `===` and `═`), does NOT detect title-case section headers (it only matches ALL-CAPS and Roman-numeral patterns), and does NOT handle mixed-indentation code blocks where some lines lack 4-space indentation. When a document uses `---` as section dividers and has title-case headers like "Why This Matters More Than Better Prompts", write a custom parser that: (a) uses an exact set of known header strings, (b) detects `---` as a ruler, (c) uses keyword-based code block detection (not just indentation), and (d) strips any "FOR PI CODING ONLY" footer section. See `references/tutorial-with-pipe-tables-format.md` for the full format spec.
24. **Format F (tutorial with MODULE headers, multi-line title, bullet continuations) needs a custom parser** -- Documents with `MODULE N:` headers, multi-line titles (3 lines joined), `WHAT YOU WALK AWAY WITH` bullet sections with continuation lines, and ALL-CAPS headers containing `$` and digits (e.g. "WHY THIS COMMANDS $14.99") are NOT handled by any existing parser. The `plain-text-to-html.py` script fails because: (a) it doesn't detect MODULE headers, (b) it doesn't merge bullet continuation lines, (c) its ALL-CAPS regex doesn't include `$` or digits, and (d) it doesn't handle `═`-wrapped ALL-CAPS headers. Use `scripts/build-agent-tutorial-to-html.py` for this format. See `references/agent-architecture-tutorial-format.md` for the full format spec.

## CRITICAL: Content Integrity Verification

**After generating the PDF, verify content integrity before sending to the user.** Page count alone is not sufficient, a PDF can have the right number of pages but be missing all the prose content. This is the single most common failure mode and the one that costs the most trust.

### What to check

1. **Total character count**, Extract all text from the generated PDF and compare its length to the source document. If the PDF has significantly fewer characters (e.g. 16K vs 44K), the parser is dropping content. This is a hard failure, do not send.

2. **Page 1 content**, Extract text from page 1. It should have at least 20+ lines of real content (cover + TOC + body). If it has fewer, the layout is broken.

3. **Last page content**, Extract text from the last page. If it has fewer than ~12 lines of real content, force a page-break before the last major content block and re-render.

4. **Spot-check prose**, Look for at least one paragraph of narrative text in the PDF output. If the PDF only has headers, code blocks, and bullet lists but no prose paragraphs, the parser is dropping body text.

### Common causes of content loss

- **Malformed HTML structure**, If the cover-wrap div is not properly closed, or if the body content is nested inside it incorrectly, WeasyPrint may silently drop content. Always verify the HTML structure by checking the generated HTML file.
- **Paragraphs being skipped**, If the detection order is wrong, prose paragraphs may fall through all detection rules and be silently dropped. The "normal paragraph" catch-all (step 15) must be the LAST rule in the detection order.
- **Empty-line handling**, Empty lines should close all open containers and produce zero HTML output. Do NOT emit `<p>&nbsp;</p>` for empty lines, WeasyPrint renders them as stray bullets.
- **Parser only rendering headers/code/lists**, If the detection rules are too aggressive, only headers, code blocks, and bullet items get emitted. Prose paragraphs that don't match any rule are silently dropped. Always check the generated HTML file for `<p>` tags before rendering the PDF. If there are 0 or very few `<p>` tags but the source has hundreds of lines of prose, the parser is broken.

### Verification code snippet

```python
from pypdf import PdfReader
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# Check total content
print(f"PDF chars: {len(full_text)}")
print(f"Source chars: {len(source_text)}")
if len(full_text) < len(source_text) * 0.5:
    print("WARNING: PDF has less than 50% of source content, content may be missing")

# Check page 1
page1 = reader.pages[0]
p1_lines = [l for l in page1.extract_text().split('\n') if l.strip()]
print(f"Page 1 lines: {len(p1_lines)}")
if len(p1_lines) < 20:
    print("WARNING: Page 1 has very few lines, layout may be broken")
```

### Pre-flight HTML check (BEFORE rendering PDF)

Before calling `HTML(html_path).write_pdf()`, check the generated HTML for `<p>` tags:

```python
with open(html_path, "r") as f:
    html = f.read()
p_count = len(re.findall(r'<p>', html))
print(f"<p> tags in HTML: {p_count}")
if p_count < 10 and source_has_prose:
    print("WARNING: Very few <p> tags, parser may be dropping prose")
```

This catches content loss before the 30-second WeasyPrint render, not after.

### HARD RULE: Verify before sending. Never ship broken output.

**This is the single most important rule in this skill.** The user will fire you if you keep sending garbage. Every PDF you generate must pass ALL of the following checks before you email it or deliver it:

1. **Character count check**, PDF text length must be at least 50% of source text length. If not, the parser is dropping content. Fix the parser, do not send.
2. **Page 1 check**, Page 1 must have 20+ lines of real content. If not, the layout is broken (forced page break, empty cover, etc.). Fix the layout, do not send.
3. **Paragraph check**, The HTML must have `<p>` tags. If there are 0 or very few `<p>` tags but the source has hundreds of lines of prose, the parser is broken. Fix the parser, do not send.
4. **Last page check**, Last page must have 12+ lines of real content. If not, force a page-break before the last major content block and re-render.

**If any check fails, fix the root cause and re-generate. Do not send the broken PDF and wait for the user to tell you it's wrong. Do not ask the user to describe what's wrong, look at the output yourself and fix it.**

### Reference: The Harness Effect disaster (what not to do)

In a real session, this skill was used to convert a 711-line tutorial (44K chars) to PDF. The result was a 13-page PDF with only 16K chars, the parser dropped every paragraph of prose. Only headers, code blocks, and bullet lists survived. The user had to send both the broken and working PDFs for the agent to even notice the content was missing.

**Root cause:** The parser's detection rules were too aggressive. Prose paragraphs that didn't match any specific rule (header, code, bullet, table) were silently dropped. The agent checked page count and last-page line count but never verified total character count or checked for `<p>` tags in the HTML.

**The fix that would have caught it:** Running the pre-flight HTML check (checking for `<p>` tags) before rendering the PDF. The HTML had 0 `<p>` tags for the first 2000 chars of body content because the parser was only emitting `<h2>`, `<h3>`, `<pre>`, and `<li>` elements.

**The cost:** 6 iterations, the user's trust, and a constitution being written because the agent couldn't be trusted to do a simple PDF conversion correctly.

## CRITICAL: User Correction Protocol

**When the user says "remove X" or "change Y": do exactly that and nothing else.**
- If they say "remove the three # marks on page 2" -- remove only `###` marks. Leave the text as plain text. Do NOT wrap it in `<h3>` tags.
- If they say "remove this section" -- remove only that section. Do not touch headers, formatting, or content they didn't mention.
- Never "improve" formatting or structure beyond what was explicitly asked.

**Stripping heading markers:**
- `###` removal = strip the `### ` prefix, keep content as plain paragraph text. Do NOT convert to `<h3>`, bold, or any HTML tag.
- The only exception is `#` and `##` lines (H1/H2) which remain as styled headings.
- Verify by extracting text from the output PDF -- if header text that should be plain is still rendered as heading, fix it.

## Spec labels (CPU:/GPU:/RAM: etc.) -- CRITICAL for readability

Blueprint/guide documents with build spec lines like `CPU:    AMD Ryzen 5 7600X...` MUST render the label in **bold** (`<strong>Label:</strong>`), not as plain `<p>` text. Vinny rejected the first PDF as "textual diarrhea" because spec lines were indistinguishable from body text.

The `scripts/blueprint-to-html.py` script handles this via `SPEC_LABEL_RE`:
```python
SPEC_LABEL_RE = re.compile(r"^(CPU|GPU|MOBO|RAM|STORAGE|PSU|CASE|COOLER|COOLING|TOTAL):\s*(.*)$")
```
Matched lines become `<p class="spec"><strong>Label:</strong> value</p>`.
Indented continuation lines (the pipe-separated details on the next line) become `<p class="spec-cont">` so they visually group with the spec label.

The CSS for these classes:
```css
p.spec { margin: 2pt 0; padding-left: 0; }
p.spec-cont { margin: 1pt 0 2pt 0; padding-left: 0; color: #333; }
```

## Reference Files
- `references/plain-text-tutorial-parsing.md` -- full state machine approach for non-markdown tutorial documents (.txt files with ALL-CAPS headers, PART dividers, decorative rulers, indented code blocks, bullet lists, checkboxes, numbered items, Q&A pairs, and sub-section lines).
- `references/agent-powered-research-format.md` -- second tutorial format variant: Roman-numeral TOC, ═ rulers, TABLE OF CONTENTS landmark, broader sub-section patterns (STEP:, USE CASE:, OPTION:).
- `references/guide-with-tables-format.md` -- third format variant: guide documents with pipe tables, tier headers (`6GB VRAM: THE STRUGGLE TIER`), cheat sheet sections, and no TOC/topic list. Title + author + contact on first 3 lines.
- `references/cron-tutorial-format.md` -- fourth format variant: title-case section headers, pipe tables, keyword-based code block detection (handles mixed indented/non-indented code lines), and "FOR PI CODING ONLY" footer stripping.
- `references/blueprint-guide-format.md` -- fourth format variant: long-form blueprint/guide documents with PART N: and TIER N: headers, [ ] checkboxes, spec-list sections (CPU:/GPU:/RAM:), and TOC extracted from "This blueprint covers" paragraphs.
- `references/tutorial-with-pipe-tables-format.md` -- fifth format variant: tutorial with `---` rulers, title-case section headers, pipe tables, mixed-indentation code blocks, and a "FOR PI CODING ONLY" footer to strip.
- `references/agent-architecture-tutorial-format.md` -- sixth format variant: tutorial with MODULE N: headers, multi-line title, bullet continuation lines, pipe tables, ALL-CAPS headers with $/digits, and ═-wrapped headers.
- `scripts/plain-text-to-html.py` -- runnable parser script for Format A (tutorials). Pass it `input.txt` and `output.html`.
- `~/.hermes/scripts/sbt-tutorial-to-html.py` -- reusable parser for `=== ALL-CAPS ===` tutorials with `----` (80-hyphen) fenced code blocks, `1.1`-style sub-sections, and numbered TOC. Handles paragraph buffering (consecutive lines joined into one `<p>`), bullet grouping, and optional section stripping (edit `CUT_MARKER` to drop a trailing section like "DISTRIBUTION ASSETS"). Proven on the "STOP BURNING TOKENS" tutorial (23 pages).
- `scripts/guide-to-html.py` -- runnable parser script for Format C (guides with tables). Handles pipe tables, tier headers, cheat sheet indented ollama commands, and the 3-line metadata header.
- `scripts/blueprint-to-html.py` -- runnable parser script for Format D (blueprint/guide documents). Handles PART N:, TIER N:, [ ] checkboxes, spec lists, and "This blueprint covers" TOC extraction.
- `scripts/cron-tutorial-to-html.py` -- runnable parser script for Format E (cron tutorial with `---` rulers, title-case headers, pipe tables, mixed-indentation code blocks, and "FOR PI CODING ONLY" footer stripping).
- `scripts/build-agent-tutorial-to-html.py` -- runnable parser script for Format F (agent architecture tutorial with MODULE headers, multi-line title, bullet continuations, pipe tables, and extended ALL-CAPS regex).