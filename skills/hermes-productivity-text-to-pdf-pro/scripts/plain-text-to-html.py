#!/usr/bin/env python3
"""
Generalized plain-text tutorial → HTML parser for WeasyPrint PDF generation.
Handles: ALL-CAPS headers, === wrapped headers, PART dividers, Roman numeral sections,
decorative rulers (including ═ box-drawing), fenced/indented code blocks, bullets,
numbered items, checklists, bold lines, and normal paragraphs with inline markdown.

IMPORTANT: Consecutive paragraph lines are buffered into single <p> tags.
Do NOT emit one <p> per line — that produces fragmented, unreadable paragraphs.

Usage:
    python plain-text-to-html.py <input.txt> <output.html>
"""
import re
import html
import sys


def parse(src_path, out_path):
    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('\u2014', '\u2013')
    lines = text.splitlines()

    # --- Unified ruler regex (includes ═ U+2550) ---
    RULER_RE = re.compile(r"[═\-=\u2500\u2550]{3,}")

    # --- Extract metadata ---
    title_line = ""
    subtitle_lines = []
    what_bullets = []
    toc_items = []
    body_lines = []

    n = len(lines)
    i = 0

    # Skip initial empties / rulers
    while i < n and (not lines[i].strip() or RULER_RE.fullmatch(lines[i].strip())):
        i += 1

    # Title: either === Title === or bare first line
    if i < n:
        stripped = lines[i].strip()
        if stripped.startswith("=== ") and stripped.endswith(" ==="):
            title_line = stripped.strip("= ").strip()
        else:
            title_line = stripped
        i += 1

    # Collect subtitles / metadata until next landmark
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if RULER_RE.fullmatch(stripped):
            i += 1
            continue
        # Known landmarks stop subtitle collection
        if stripped in ("TABLE OF CONTENTS", "WHAT YOU WILL LEARN", "WHAT YOU'RE GETTING",
                        "=== WHAT YOU WILL LEARN ===", "=== WHAT YOU'RE GETTING ==="):
            break
        if re.match(r"^(PART\s+(ONE|TWO|THREE|FOUR|FIVE|SIX)\b|[IVX]+\.\s)", stripped) or \
           re.fullmatch(r"[A-Z][A-Z\s,:/'\-&]+(\?|:)?$", stripped) or \
           (stripped.startswith("=== ") and stripped.endswith(" ===")):
            break
        subtitle_lines.append(stripped)
        i += 1

    # Extract TABLE OF CONTENTS or WHAT YOU WILL LEARN
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        if stripped == "TABLE OF CONTENTS":
            i += 1
            while i < n and RULER_RE.fullmatch(lines[i].strip()):
                i += 1
            while i < n:
                s = lines[i].strip()
                if RULER_RE.fullmatch(s):
                    i += 1
                    continue
                if not s:
                    i += 1
                    continue
                if re.match(r"^(PART\s|===\s|[IVX]+\.\s|[A-Z][A-Z\s,:/'\-&]+(\?|:)?$)", s):
                    break
                toc_items.append(s)
                i += 1
            while i < n and RULER_RE.fullmatch(lines[i].strip()):
                i += 1
            break

        if stripped in ("WHAT YOU WILL LEARN", "WHAT YOU'RE GETTING",
                        "=== WHAT YOU WILL LEARN ===", "=== WHAT YOU'RE GETTING ==="):
            i += 1
            while i < n and RULER_RE.fullmatch(lines[i].strip()):
                i += 1
            while i < n:
                s = lines[i].strip()
                if RULER_RE.fullmatch(s):
                    i += 1
                    continue
                if not s:
                    i += 1
                    continue
                if s.startswith("-"):
                    what_bullets.append(s.lstrip("- ").strip())
                elif re.fullmatch(r"=+\s+.*\s+=+", s) or re.fullmatch(r"[A-Z][A-Z\s,:/'\-&]+(\?|:)?$", s):
                    break
                else:
                    what_bullets.append(s)
                i += 1
            while i < n and RULER_RE.fullmatch(lines[i].strip()):
                i += 1
            break

        # No TOC found — hit a body section header
        if re.match(r"^(PART\s+(ONE|TWO|THREE|FOUR|FIVE|SIX)\b|[IVX]+\.\s)", stripped) or \
           re.fullmatch(r"[A-Z][A-Z\s,:/'\-&]+(\?|:)?$", stripped) or \
           re.fullmatch(r"=+\s+.*\s+=+", stripped):
            break

        i += 1

    # Remaining lines are body
    body_lines = lines[i:]

    if not title_line:
        title_line = "Tutorial"

    # --- Build body HTML ---
    in_code_block = False
    in_bullet_list = False
    in_checklist = False
    in_indent_code = False
    indent_buffer = []
    body_parts = []
    para_buffer = []  # buffer consecutive paragraph lines into one <p>

    code_keywords = (
        "pip", "from", "import", "class", "def", "curl", "git", "npm",
        "uvx", "playwright", "cd ", "ls ", "rm ", "$ ", "echo", "cat",
        "mkdir", "touch", "chmod", "python", "node", "npx", "docker"
    )

    def flush_indent_code():
        nonlocal in_indent_code, indent_buffer
        if in_indent_code and indent_buffer:
            code_text = "\n".join(indent_buffer)
            code_text = html.escape(code_text)
            body_parts.append(f'<pre><code>{code_text}</code></pre>')
            indent_buffer = []
        in_indent_code = False

    def flush_para():
        nonlocal para_buffer
        if para_buffer:
            text = " ".join(para_buffer)
            body_parts.append(f"<p>{escape_inline(text)}</p>")
            para_buffer = []

    def close_all():
        nonlocal in_bullet_list, in_checklist, in_code_block
        flush_para()
        flush_indent_code()
        if in_bullet_list:
            body_parts.append("</ul>")
            in_bullet_list = False
        if in_checklist:
            body_parts.append("</ul>")
            in_checklist = False
        if in_code_block:
            body_parts.append("</code></pre>")
            in_code_block = False

    def escape_inline(p):
        p = html.escape(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
        p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
        return p

    for rawline in body_lines:
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

        if re.match(r"^PART\s+(ONE|TWO|THREE|FOUR|FIVE|SIX)\b", stripped):
            close_all()
            body_parts.append(f'<h2 class="part-h2">{html.escape(stripped)}</h2>')
            continue

        # Roman numeral sections: I., II., III., IV., V., VI., VII., VIII., IX., X.
        if re.match(r"^[IVX]+\.\s+.+", stripped) and len(stripped) > 5:
            close_all()
            body_parts.append(f'<h2>{html.escape(stripped)}</h2>')
            continue

        if re.fullmatch(r"=+\s+.*\s+=+", stripped):
            close_all()
            clean = stripped.strip("= ").strip()
            body_parts.append(f'<h2>{html.escape(clean)}</h2>')
            continue

        # ALL-CAPS headers (with or without trailing ?/:, may include &)
        if re.fullmatch(r"[A-Z][A-Z\s,:/'\-&]+(\?|:)?$", stripped) and len(stripped) > 3:
            close_all()
            body_parts.append(f'<h3>{html.escape(stripped)}</h3>')
            continue

        if re.match(r"^(Example\s+\d+|TIER\s+\d|Scenario\s+[A-Z]|Use\s|Do\sNOT\s|AFTER\s|THE\sPOWER|STEP\s+\d+|USE\s+CASE\s+\d+)", stripped):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue

        if re.fullmatch(r"\*\*[^*]+\*\*", stripped) and len(stripped) < 80:
            close_all()
            txt = stripped.strip("*")
            body_parts.append(f'<h4 class="bold-heading">{html.escape(txt)}</h4>')
            continue

        if stripped.startswith("☐ ") or stripped.startswith("✅ "):
            if not in_checklist:
                close_all()
                body_parts.append('<ul class="checklist">')
                in_checklist = True
            item = stripped[2:].strip()
            body_parts.append(f'<li><span class="cb">{stripped[0]}</span> {html.escape(item)}</li>')
            continue

        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            if not in_bullet_list:
                close_all()
                body_parts.append('<ul class="std">')
                in_bullet_list = True
            item = stripped[2:].strip()
            body_parts.append(f'<li>{html.escape(item)}</li>')
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            close_all()
            num, item = m.group(1), m.group(2)
            item_html = html.escape(item)
            item_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item_html)
            item_html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", item_html)
            body_parts.append(f'<p class="num-item"><span class="num">{num}.</span> {item_html}</p>')
            continue

        if stripped.startswith("Q: ") or stripped.startswith("A: "):
            close_all()
            label = stripped[:2]
            rest = stripped[3:]
            body_parts.append(f'<p><strong>{label}</strong> {html.escape(rest)}</p>')
            continue

        if line.startswith("    ") or line.startswith("\t"):
            stripped_inner = line.lstrip()
            looks_code = any(stripped_inner.startswith(kw) for kw in code_keywords) or stripped_inner.startswith("# ") or stripped_inner.startswith("$")
            if looks_code or in_indent_code:
                if not in_indent_code:
                    close_all()
                    in_indent_code = True
                indent_buffer.append(line)
                continue

        flush_indent_code()
        # Buffer consecutive paragraph lines into one <p> tag
        para_buffer.append(line)
        continue

    close_all()
    body_html = "\n".join(body_parts)

    # --- Assemble HTML ---
    what_items_html = "\n".join(f"<li>{html.escape(b)}</li>" for b in what_bullets)
    toc_html = "\n".join(f"<li>{html.escape(b)}</li>" for b in toc_items)
    subtitle_html = "<br/>".join(html.escape(s) for s in subtitle_lines)

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
.cover-wrap h1 span {{ font-weight: 300; }}
.cover-sub {{
  font-family: "Liberation Serif", Georgia, serif;
  font-size: 13pt; color: rgba(255,255,255,0.85); font-style: italic;
  margin: 4pt 0 6pt 0;
}}
.cover-sub2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 11pt; color: rgba(255,255,255,0.75);
  margin: 2pt 0 8pt 0;
}}
.cover-wrap hr {{
  border: none; border-top: 1.5px solid rgba(255,255,255,0.35);
  width: 100px; margin: 0 auto 12pt auto;
}}
.cover-meta {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt; color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0;
}}
.toc {{
  padding: 16pt 48pt 8pt 48pt;
}}
.toc h2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 13pt; color: #1b263b; margin: 0 0 7pt 0;
  border-bottom: 2px solid #415a77; padding-bottom: 3pt;
}}
.toc ul {{ margin: 0 0 4pt 0; padding-left: 18pt; }}
.toc li {{ font-size: 10.5pt; margin-bottom: 2pt; }}
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
h2.part-h2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 14pt; color: #1b263b; margin: 18pt 0 10pt 0;
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
  font-size: 11pt; color: #555; margin: 11pt 0 4pt 0;
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
  <p class="cover-tag">TUTORIAL</p>
  <h1>{html.escape(title_line)}</h1>
  <p class="cover-sub">{subtitle_html}</p>
  <hr/>
</div>
'''

    if toc_items:
        html_doc += f'''
<div class="toc">
  <h2>TABLE OF CONTENTS</h2>
  <ul>
    {toc_html}
  </ul>
</div>
'''
    elif what_bullets:
        html_doc += f'''
<div class="what-learn">
  <h2>WHAT YOU WILL LEARN</h2>
  <ul>
    {what_items_html}
  </ul>
</div>
'''

    html_doc += f'''
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
        print("Usage: python plain-text-to-html.py <input.txt> <output.html>")
        sys.exit(1)
    parse(sys.argv[1], sys.argv[2])
