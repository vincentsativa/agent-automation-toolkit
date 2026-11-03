#!/usr/bin/env python3
"""
Format C parser: guide documents with pipe tables, tier headers, cheat sheets.
Handles: === wrapped headers, bare ALL-CAPS headers, pipe tables, tier headers
(6GB VRAM: ...), cheat sheet indented ollama commands, bullet lists, numbered items.

Usage:
    python3 guide-to-html.py <input.txt> <output.html>
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

    RULER_RE = re.compile(r"[═\u2550\-=\u2500]{3,}")

    # Extract title, author, contact from first 3 non-empty non-ruler lines
    title_line = ""
    author_line = ""
    contact_line = ""
    body_start = 0
    n = len(lines)
    i = 0
    collected = 0
    while i < n and collected < 3:
        s = lines[i].strip()
        if not s or RULER_RE.fullmatch(s):
            i += 1
            continue
        if collected == 0:
            title_line = s
        elif collected == 1:
            author_line = s
        else:
            contact_line = s
        collected += 1
        i += 1
    body_start = i

    # Parse body
    in_code_block = False
    in_bullet_list = False
    in_table = False
    body_parts = []

    def close_all():
        nonlocal in_bullet_list, in_code_block, in_table
        if in_bullet_list:
            body_parts.append("</ul>")
            in_bullet_list = False
        if in_code_block:
            body_parts.append("</code></pre>")
            in_code_block = False
        if in_table:
            body_parts.append("</tbody></table>")
            in_table = False

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

        # === WRAPPED ALL-CAPS HEADERS ===
        m = re.fullmatch(r"=+\s+(.+?)\s+=+", stripped)
        if m:
            close_all()
            body_parts.append(f'<h2>{html.escape(m.group(1))}</h2>')
            continue

        # ALL-CAPS sub-headers (with or without trailing ?/:)
        if re.fullmatch(r"[A-Z][A-Z\s,:/'\-()]+(\?|:)?$", stripped) and len(stripped) > 3:
            close_all()
            body_parts.append(f'<h3>{html.escape(stripped)}</h3>')
            continue
        # ALL-CAPS without trailing punctuation (e.g. "WHEN TO IGNORE Q4 AND RUN Q8 (AND VICE VERSA)")
        if re.fullmatch(r"[A-Z][A-Z\s,:/'\-()&]+[A-Z)]", stripped) and len(stripped) > 5:
            close_all()
            body_parts.append(f'<h3>{html.escape(stripped)}</h3>')
            continue

        # Sub-section lines
        if re.match(r"^(TRAP\s+\d+|STEP\s+\d+|70B REALITY CHECK|THE RULE|RECAP|OUTPUT)", stripped):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue
        # Tier headers: "6GB VRAM: THE STRUGGLE TIER"
        if re.match(r"^\d+GB\s+VRAM", stripped):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue
        # Cheat sheet GPU tier labels: "6GB VRAM" (standalone)
        if re.fullmatch(r"\d+GB\s+VRAM", stripped):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue
        # "GPU TIER → TASK → MODEL → QUANT → OLLAMA COMMAND"
        if stripped.startswith("GPU TIER"):
            close_all()
            body_parts.append(f'<h4>{html.escape(stripped)}</h4>')
            continue

        # Short bold lines
        if re.fullmatch(r"\*\*[^*]+\*\*", stripped) and len(stripped) < 80:
            close_all()
            txt = stripped.strip("*")
            body_parts.append(f'<h4 class="bold-heading">{html.escape(txt)}</h4>')
            continue

        # Pipe tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(re.fullmatch(r"-+\s*", c) for c in cells):
                continue
            if not in_table:
                close_all()
                body_parts.append('<table><thead><tr>')
                for c in cells:
                    body_parts.append(f'<th>{html.escape(c)}</th>')
                body_parts.append('</tr></thead><tbody>')
                in_table = True
            else:
                body_parts.append('<tr>')
                for c in cells:
                    body_parts.append(f'<td>{html.escape(c)}</td>')
                body_parts.append('</tr>')
            continue

        # Bullets
        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            if not in_bullet_list:
                close_all()
                body_parts.append('<ul class="std">')
                in_bullet_list = True
            item = stripped[2:].strip()
            body_parts.append(f'<li>{escape_inline(item)}</li>')
            continue

        # Numbered items
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            close_all()
            num, item = m.group(1), m.group(2)
            body_parts.append(f'<p class="num-item"><span class="num">{num}.</span> {escape_inline(item)}</p>')
            continue

        # Indented code (4+ spaces with command keywords)
        if line.startswith("    ") or line.startswith("\t"):
            code_keywords = ("pip", "from", "import", "class", "def", "curl", "git", "npm",
                            "uvx", "playwright", "cd ", "ls ", "rm ", "$ ", "echo", "cat",
                            "mkdir", "touch", "chmod", "python", "node", "npx", "docker",
                            "ollama")
            inner = line.lstrip()
            if any(inner.startswith(kw) for kw in code_keywords) or inner.startswith("# "):
                if not in_code_block:
                    close_all()
                    body_parts.append("<pre><code>")
                    in_code_block = True
                body_parts.append(html.escape(line))
                continue

        close_all()
        p = escape_inline(line)
        body_parts.append(f'<p>{p}</p>')

    close_all()
    body_html = "\n".join(body_parts)

    # Assemble HTML
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
p.num-item {{ margin: 3pt 0; padding-left: 26pt; text-indent: -26pt; }}
span.num {{ display: inline-block; width: 22pt; font-weight: 700; color: #415a77; }}
strong {{ font-weight: 700; color: #1b263b; }}
table {{
  width: 100%; border-collapse: collapse; margin: 8pt 0;
  font-size: 9.5pt; font-family: "Liberation Sans", Arial, sans-serif;
}}
th {{
  background: #1b263b; color: #fff; padding: 5pt 6pt;
  text-align: left; font-weight: 700;
}}
td {{
  padding: 4pt 6pt; border-bottom: 1px solid #d0d5dd;
}}
tr:nth-child(even) td {{ background: #f4f6f8; }}
</style>
</head>
<body>
<div class="cover-wrap">
  <p class="cover-tag">GUIDE</p>
  <h1>{html.escape(title_line)}</h1>
  <p class="cover-sub">{html.escape(author_line)}</p>
  <p class="cover-contact">{html.escape(contact_line)}</p>
  <hr/>
</div>
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
        print("Usage: python guide-to-html.py <input.txt> <output.html>")
        sys.exit(1)
    parse(sys.argv[1], sys.argv[2])
