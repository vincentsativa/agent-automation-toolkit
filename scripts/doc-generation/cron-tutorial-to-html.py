#!/usr/bin/env python3
"""
Clean parser for "Your First Agent Cron Job" tutorial.
Handles: --- rulers, pipe tables, code blocks, bullet lists, numbered lists.
Strips the "FOR PI CODING ONLY" footer.
"""
import re
import html
import sys


def parse(src_path, out_path):
    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace('\u2014', '\u2013')
    lines = text.splitlines()

    # --- Strip the "FOR PI CODING ONLY" section ---
    cutoff = None
    for i, line in enumerate(lines):
        if "FOR PI CODING ONLY" in line and "DO NOT INCLUDE" in line:
            cutoff = i
            break
    if cutoff is not None:
        lines = lines[:cutoff]

    RULER_RE = re.compile(r"^---+$")

    # --- Exact list of section headers in this document ---
    SECTION_HEADERS = {
        "Why This Matters More Than Better Prompts",
        "What Cron Actually Is (30 Seconds)",
        "Why Agents and Cron Were Made for Each Other",
        "The Daily Briefing Agent: Your Phone Becomes Smarter Than You",
        "Chaining Agents: Research, Write, Publish, Repeat",
        "Watchdog Patterns: Let the Agent Watch So You Do Not Have To",
        "Cron Syntax Without the Pain: Copy and Paste These",
        "Why Separate Agents Keep Context Clean",
        "STEP-BY-STEP IMPLEMENTATION: HOW TO BUILD IT",
        "METHOD 1: THE LOCAL HARDWARE ROUTE (Terminal, Linux, Mac, Pi)",
        "METHOD 2: THE NO-CODE / VISUAL PIPELINE ROUTE (n8n)",
        "The Master Key: Chaining via the Local File System",
        "Getting Started: Your First Three Cron Jobs",
        "The Real Lesson",
    }

    CODE_KEYWORDS = (
        "pip", "from", "import", "class", "def", "curl", "git", "npm",
        "uvx", "playwright", "cd ", "ls ", "rm ", "$ ", "echo", "cat",
        "mkdir", "touch", "chmod", "python", "node", "npx", "docker",
        "crontab", "# ", "response", "prompt", "with open", "if __name__",
        "run_agent", "f.write", "open(", "else:", "elif", "try:", "except",
        "return", "print", "self", "break", "continue", "while", "for ",
        "import ", "from ", "pass", "yield", "raise", "finally",
    )

    def looks_like_code(s):
        return any(s.startswith(kw) for kw in CODE_KEYWORDS)

    def is_clearly_not_code(s):
        """Returns True if line is definitely not code (section header, ruler, etc.)"""
        if not s:
            return False
        if RULER_RE.match(s):
            return True
        if s in SECTION_HEADERS:
            return True
        if s.startswith("|") and s.endswith("|"):
            return True
        if s.startswith("- ") or s.startswith("* ") or s.startswith("• "):
            return True
        if re.match(r"^\d+\.\s+", s):
            return True
        if s.startswith("```"):
            return True
        return False

    # --- Parse ---
    title_line = ""
    i = 0
    n = len(lines)

    # Title is first non-empty line
    while i < n and not lines[i].strip():
        i += 1
    if i < n:
        title_line = lines[i].strip()
        i += 1

    # Skip subtitle/metadata until first ruler
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if RULER_RE.match(s):
            i += 1
            break
        i += 1

    if not title_line:
        title_line = "Your First Agent Cron Job"

    # --- Build body HTML ---
    in_fenced_code = False
    in_code_block = False
    in_bullet_list = False
    in_table = False
    code_buffer = []
    body_parts = []

    def close_all():
        nonlocal in_bullet_list, in_table, in_code_block, code_buffer
        if in_code_block and code_buffer:
            code_text = "\n".join(code_buffer)
            body_parts.append(f'<pre><code>{html.escape(code_text)}</code></pre>')
            code_buffer = []
        in_code_block = False
        if in_bullet_list:
            body_parts.append("</ul>")
            in_bullet_list = False
        if in_table:
            body_parts.append("</tbody></table>")
            in_table = False

    def escape_inline(p):
        p = html.escape(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\*(.+?)\*", r"<em>\1</em>", p)
        p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
        return p

    while i < n:
        line = lines[i].rstrip("\n")
        stripped = line.strip()
        i += 1

        # --- Fenced code blocks ---
        if stripped.startswith("```"):
            if in_fenced_code:
                body_parts.append("</code></pre>")
                in_fenced_code = False
            else:
                close_all()
                body_parts.append("<pre><code>")
                in_fenced_code = True
            continue

        if in_fenced_code:
            body_parts.append(html.escape(line))
            continue

        # --- Empty lines ---
        if not stripped:
            if in_code_block:
                code_buffer.append("")
                continue
            close_all()
            continue

        # --- Ruler ---
        if RULER_RE.match(stripped):
            close_all()
            continue

        # --- Section headers ---
        if stripped in SECTION_HEADERS:
            close_all()
            body_parts.append(f'<h2>{escape_inline(stripped)}</h2>')
            continue

        # --- Pipe table ---
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                close_all()
                body_parts.append('<table><thead><tr>')
                in_table = True
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(c.replace("-", "").strip() == "" for c in cells):
                body_parts.append("</tr></thead><tbody>")
                continue
            row_cells = "".join(f"<td>{html.escape(c)}</td>" for c in cells)
            body_parts.append(f"<tr>{row_cells}</tr>")
            continue

        if in_table:
            body_parts.append("</tbody></table>")
            in_table = False

        # --- Bullet list ---
        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("• "):
            if not in_bullet_list:
                close_all()
                body_parts.append('<ul class="std">')
                in_bullet_list = True
            item = stripped[2:].strip()
            body_parts.append(f'<li>{escape_inline(item)}</li>')
            continue

        # --- Numbered items ---
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            close_all()
            num, item = m.group(1), m.group(2)
            body_parts.append(f'<p class="num-item"><span class="num">{num}.</span> {escape_inline(item)}</p>')
            continue

        # --- Code block detection ---
        is_indented = line.startswith("    ") or line.startswith("\t")
        is_code_keyword = looks_like_code(stripped)

        if is_indented or is_code_keyword:
            if not in_code_block:
                close_all()
                in_code_block = True
                code_buffer = [line]
            else:
                code_buffer.append(line)
            continue
        else:
            # Not code, if we were in a code block, close it
            if in_code_block:
                close_all()

        # --- Normal paragraph ---
        close_all()
        body_parts.append(f'<p>{escape_inline(line)}</p>')

    close_all()
    body_html = "\n".join(body_parts)

    # --- Assemble HTML ---
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
.cover-wrap hr {{
  border: none; border-top: 1.5px solid rgba(255,255,255,0.35);
  width: 100px; margin: 0 auto 12pt auto;
}}
.cover-meta {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt; color: rgba(255,255,255,0.7); line-height: 1.6; margin: 0;
}}
h2 {{
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 14pt; color: #1b263b; margin: 22pt 0 10pt 0;
  border-bottom: 2px solid #415a77; padding-bottom: 4pt;
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
  font-family: "Liberation Sans", Arial, sans-serif;
  font-size: 9.5pt;
}}
th {{
  background: #415a77; color: #fff; padding: 5pt 8pt;
  text-align: left; font-weight: 700;
}}
td {{
  padding: 4pt 8pt; border-bottom: 1px solid #d0d5dd;
}}
tr:nth-child(even) td {{ background: #f4f6f8; }}
</style>
</head>
<body>
<div class="cover-wrap">
  <p class="cover-tag">TUTORIAL</p>
  <h1>{html.escape(title_line)}</h1>
  <hr/>
  <p class="cover-meta">Learn how to schedule AI agents to run automatically, deliver daily briefings to your phone, chain research into writing, and build watchdog alerts that monitor anything while you sleep.</p>
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
        print("Usage: python cron-tutorial-to-html.py <input.txt> <output.html>")
        sys.exit(1)
    parse(sys.argv[1], sys.argv[2])
