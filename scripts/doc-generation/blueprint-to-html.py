#!/usr/bin/env python3
"""Format D parser: blueprint/guide documents with PART/TIER headers, spec lists, [ ] checkboxes.
Handles: PART N: headers, TIER N: headers, === wrapped headers, bare ALL-CAPS headers,
[ ] checkboxes, • bullets, numbered items, indented code blocks, fenced code blocks,
sub-section headers (PHASE, WEEK, MINIMUM SPECS, PROS, CONS, etc.), and TOC extraction
from "This blueprint covers" paragraphs.

CRITICAL: Spec labels (CPU:/GPU:/RAM:/MOBO:/STORAGE:/PSU:/CASE:/COOLER:/COOLING:/TOTAL:)
must be rendered as <strong> bold labels, not plain paragraphs. Vinny rejected the first
version as "textual diarrhea" because spec lines were plain <p> tags.

Usage:
    python3 blueprint-to-html.py <input.txt> <output.html>
"""
import re
import html
import sys

def escape_inline(p):
    p = html.escape(p)
    p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
    p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
    return p

def parse(src_path, out_path):
    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace('\u2014', '\u2013')
    lines = text.splitlines()

    RULER_RE = re.compile(r"[═╔╗╚╝\u2550\-=\u2500]{3,}")
    PART_RE = re.compile(r"^PART\s+(\d+):\s*(.*)$")
    TIER_RE = re.compile(r"^TIER\s+(\d+):\s*(.*)$")
    ALLCAPS_RE = re.compile(r"^[A-Z][A-Z\s,:/'\-&()]+(\?|:)?$")
    ALLCAPS2_RE = re.compile(r"^[A-Z][A-Z\s,:/'\-&()]+[A-Z)]$")
    CHECKBOX_RE = re.compile(r"^\[( |x|X)\]\s+(.*)$")
    BULLET_RE = re.compile(r"^[•\-\*]\s+(.*)$")
    NUM_ITEM_RE = re.compile(r"^(\d+)\.\s+(.*)$")
    BOLD_LINE_RE = re.compile(r"^\*\*[^*]+\*\*$")
    SPEC_LABEL_RE = re.compile(r"^(CPU|GPU|MOBO|RAM|STORAGE|PSU|CASE|COOLER|COOLING|TOTAL):\s*(.*)$")
    SUBHEAD_RE = re.compile(r"^(PHASE \d+|WEEK \d+|MINIMUM SPECS|WHAT YOU CAN RUN|WHAT YOU CAN RUN ON APPLE SILICON|PROS|CONS|BEST FOR|CURRENT LINEUP|HARDWARE OPTIONS|POPULAR CONFIGURATIONS|WHAT IS IT|COST|PROVIDERS|SOVEREIGNTY LEVEL|QUICK START|FEATURES YOU GET|ALTERNATIVE|KEY CAPABILITIES|AGENT ARCHITECTURE PATTERN|EXAMPLE|CRITICAL|LAYER \d+):?$")

    # Extract metadata from first ~10 lines
    title_line = ""
    subtitle_line = ""
    author_line = ""
    body_start = 0
    n = len(lines)
    i = 0
    collected = 0
    while i < n and collected < 4:
        s = lines[i].strip()
        if not s or RULER_RE.fullmatch(s):
            i += 1
            continue
        if collected == 0:
            title_line = s
        elif collected == 1:
            subtitle_line = s
        elif collected == 2:
            author_line = s
        collected += 1
        i += 1
    body_start = i

    # Extract TOC bullets from "This blueprint covers" paragraph
    toc_bullets = []
    in_toc = False
    for rawline in lines[body_start:]:
        stripped = rawline.strip()
        if "This blueprint covers" in stripped:
            in_toc = True
            continue
        if in_toc:
            m = re.match(r"^[•\-\*]\s+(.*)$", stripped)
            if m:
                toc_bullets.append(m.group(1))
            elif not stripped:
                continue
            else:
                break

    # Parse body
    in_code_block = False
    in_bullet_list = False
    in_checklist = False
    body_parts = []

    def close_all():
        nonlocal in_bullet_list, in_code_block, in_checklist
        if in_bullet_list:
            body_parts.append("</ul>")
            in_bullet_list = False
        if in_checklist:
            body_parts.append("</ul>")
            in_checklist = False
        if in_code_block:
            body_parts.append("</code></pre>")
            in_code_block = False

    for rawline in lines[body_start:]:
        line = rawline.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            close_all()
            continue
        if RULER_RE.fullmatch(stripped):
            close_all()
            continue
        if stripped.startswith("```"):
            if in_code_block:
                body_parts.append("</code></pre>")
                in_code_block = False
            else:
                close_all()
                body_parts.append("<pre><code>")
                in_code_block = True
            continue
        if in_code_block:
            body_parts.append(html.escape(line))
            continue

        # PART headers
        m = PART_RE.match(stripped)
        if m:
            close_all()
            num = m.group(1)
            rest = m.group(2).strip()
            txt = f"PART {num}: {rest}" if rest else f"PART {num}"
            body_parts.append(f'<h2>{html.escape(txt)}</h2>')
            continue

        # TIER headers
        m = TIER_RE.match(stripped)
        if m:
            close_all()
            num = m.group(1)
            rest = m.group(2).strip()
            txt = f"TIER {num}: {rest}" if rest else f"TIER {num}"
            body_parts.append(f'<h3>{html.escape(txt)}</h3>')
            continue

        # Sub-section headers
        if SUBHEAD_RE.match(stripped):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue

        # ALL-CAPS headers
        if ALLCAPS_RE.match(stripped) and len(stripped) > 3:
            close_all()
            body_parts.append(f'<h3>{html.escape(stripped)}</h3>')
            continue
        if ALLCAPS2_RE.match(stripped) and len(stripped) > 5:
            close_all()
            body_parts.append(f'<h3>{html.escape(stripped)}</h3>')
            continue

        # Short bold lines
        if BOLD_LINE_RE.match(stripped) and len(stripped) < 80:
            close_all()
            txt = stripped.strip("*")
            body_parts.append(f'<h4 class="bold-heading">{html.escape(txt)}</h4>')
            continue

        # Checkboxes [ ] or [x]
        m = CHECKBOX_RE.match(stripped)
        if m:
            if not in_checklist:
                close_all()
                body_parts.append('<ul class="checklist">')
                in_checklist = True
            checked = m.group(1).strip()
            item = m.group(2).strip()
            cb = '<span class="cb">☐</span>' if checked == ' ' else '<span class="cb">☑</span>'
            body_parts.append(f'<li>{cb} {escape_inline(item)}</li>')
            continue

        # Bullets
        m = BULLET_RE.match(stripped)
        if m:
            if not in_bullet_list:
                close_all()
                body_parts.append('<ul class="std">')
                in_bullet_list = True
            body_parts.append(f'<li>{escape_inline(m.group(1))}</li>')
            continue

        # Numbered items
        m = NUM_ITEM_RE.match(stripped)
        if m:
            close_all()
            num, item = m.group(1), m.group(2)
            body_parts.append(f'<p class="num-item"><span class="num">{num}.</span> {escape_inline(item)}</p>')
            continue

        # Build spec labels: CPU:, GPU:, MOBO:, RAM:, STORAGE:, PSU:, CASE:, COOLER:, COOLING:, TOTAL:
        m = SPEC_LABEL_RE.match(stripped)
        if m:
            close_all()
            label = m.group(1)
            rest = m.group(2).strip()
            body_parts.append(f'<p class="spec"><strong>{label}:</strong> {escape_inline(rest)}</p>')
            continue

        # Indented continuation lines (continuation of spec lines, or indented code)
        if line.startswith("    ") or line.startswith("\t"):
            inner = line.lstrip()
            code_keywords = ("pip", "from", "import", "class", "def", "curl", "git", "npm",
                            "uvx", "playwright", "cd ", "ls ", "rm ", "$ ", "echo", "cat",
                            "mkdir", "touch", "chmod", "python", "node", "npx", "docker",
                            "ollama", "wget", "sudo", "export", "# ", "openclaw")
            if any(inner.startswith(kw) for kw in code_keywords):
                if not in_code_block:
                    close_all()
                    body_parts.append("<pre><code>")
                    in_code_block = True
                body_parts.append(html.escape(line))
                continue
            # Otherwise it's a continuation paragraph (indented continuation of spec description)
            close_all()
            body_parts.append(f'<p class="spec-cont">{escape_inline(inner)}</p>')
            continue

        close_all()
        p = escape_inline(line)
        body_parts.append(f'<p>{p}</p>')

    close_all()
    body_html = "\n".join(body_parts)

    # Build TOC HTML
    toc_html = ""
    if toc_bullets:
        toc_html = '<div class="what-learn">\n<h2>WHAT YOU WILL LEARN</h2>\n<ul>\n'
        for b in toc_bullets:
            toc_html += f'<li>{html.escape(b)}</li>\n'
        toc_html += '</ul>\n</div>\n'

    html_doc = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>{html.escape(title_line)}</title>
<style>
@page {{
  size: letter;
  margin: 0.9in 1in 1.1in 1in;
  @bottom-center {{
    content: counter(page);
    font-family: "Liberation Sans", Arial, sans-serif;
    font-size: 9pt; color: #666;
  }}
}}
@page:first {{
  margin: 0;
  @bottom-center {{ content: none; }}
}}
body {{
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 11pt; line-height: 1.55; color: #1a1a1a;
  margin: 0; padding: 0;
}}
.cover-wrap {{
  background: linear-gradient(150deg, #1b263b 0%, #415a77 80%, #556e8a 100%);
  color: #fff; padding: 34pt 48pt 28pt 48pt; text-align: center;
}}
.cover-tag {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 10pt; letter-spacing: 4px; text-transform: uppercase;
  color: rgba(255,255,255,0.65); margin: 0 0 14pt 0;
}}
.cover-wrap h1 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 24pt; font-weight: 700; color: #fff; line-height: 1.15;
  margin: 0 0 8pt 0;
}}
.cover-sub {{
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 12pt; color: rgba(255,255,255,0.85); font-style: italic;
  margin: 4pt 0 6pt 0;
}}
.cover-contact {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 10pt; color: rgba(255,255,255,0.7);
  margin: 2pt 0 10pt 0;
}}
.cover-wrap hr {{
  border: none; border-top: 1.5px solid rgba(255,255,255,0.35);
  width: 100px; margin: 0 auto 12pt auto;
}}
.what-learn {{
  padding: 16pt 48pt 8pt 48pt;
}}
.what-learn h2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 13pt; color: #1b263b; margin: 0 0 7pt 0;
  border-bottom: 2px solid #415a77; padding-bottom: 3pt;
}}
.what-learn ul {{ margin: 0 0 4pt 0; padding-left: 18pt; }}
.what-learn li {{ font-size: 10.5pt; margin-bottom: 2pt; }}
h2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 14pt; color: #1b263b; margin: 22pt 0 10pt 0;
  border-bottom: 2px solid #415a77; padding-bottom: 4pt;
  page-break-after: avoid;
}}
h3 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 12pt; color: #415a77; margin: 16pt 0 6pt 0;
  page-break-after: avoid;
}}
h4 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 11pt; color: #1b263b; margin: 11pt 0 4pt 0;
  page-break-after: avoid;
}}
h4.bold-heading {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 11pt; color: #1b263b; margin: 11pt 0 4pt 0;
  font-weight: 700;
  page-break-after: avoid;
}}
p {{
  text-align: justify; orphans: 3; widows: 3; margin: 5pt 0;
}}
p.spec {{
  margin: 2pt 0; padding-left: 0;
}}
p.spec-cont {{
  margin: 1pt 0 2pt 0; padding-left: 0; color: #333;
}}
pre {{
  background: #f4f6f8; border-left: 3px solid #415a77;
  padding: 7pt 9pt; font-family: "Liberation Mono", Consolas, monospace;
  font-size: 8.5pt; line-height: 1.35; white-space: pre-wrap;
  margin: 6pt 0;
}}
code {{
  font-family: "Liberation Mono", Consolas, monospace;
  font-size: 9pt; background: #eef0f3; padding: 1pt 3pt;
}}
pre code {{ background: transparent; padding: 0; font-size: 8.5pt; }}
ul.std {{ margin: 4pt 0 6pt 0; padding-left: 18pt; }}
ul.std li {{ margin-bottom: 2pt; font-size: 10.5pt; }}
ul.checklist {{ margin: 4pt 0 6pt 0; padding-left: 18pt; list-style: none; }}
ul.checklist li {{ margin-bottom: 2pt; font-size: 10.5pt; }}
.cb {{ display: inline-block; width: 13pt; }}
p.num-item {{ margin: 3pt 0; padding-left: 26pt; text-indent: -26pt; }}
span.num {{ display: inline-block; width: 22pt; font-weight: 700; color: #415a77; }}
strong {{ font-weight: 700; color: #1b263b; }}
</style>
</head>
<body>
<div class="cover-wrap">
  <p class="cover-tag">GUIDE</p>
  <h1>{html.escape(title_line)}</h1>
  <p class="cover-sub">{html.escape(subtitle_line)}</p>
  <p class="cover-contact">{html.escape(author_line)}</p>
  <hr/>
</div>
{toc_html}
<div style="padding: 0 48pt;">
{body_html}
</div>
</body>
</html>'''

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"HTML written to {out_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python blueprint-to-html.py <input.txt> <output.html>")
        sys.exit(1)
    parse(sys.argv[1], sys.argv[2])
