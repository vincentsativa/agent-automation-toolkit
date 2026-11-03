#!/usr/bin/env python3
"""convert-text-to-html.py

Reads a flat text file (e.g. a notepad-style guide), detects structure,
and emits a clean HTML document ready for WeasyPrint PDF generation.

Usage:
    python3 scripts/convert-text-to-html.py input.txt output.html
    python3 -m weasyprint output.html output.pdf

Assumes the text file has:
- Decorative ===== separators  (skipped)
- Numbered section headers like "1. WHAT IS HERMES AGENT?"
- Sub-sections like "--- STEP 4A: ... ---"
- ASCII tables using box-drawing characters
- Indented code blocks
- Bullet lines starting with • or -
- Q: / A: FAQ lines
- Checklist lines with ☐ or ✅
"""
import re, sys

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

SECT_MAP = {
    'WHAT IS HERMES AGENT': "What Is Hermes Agent? (And What It's NOT)",
    'WHAT YOU CAN ACTUALLY DO WITH IT': "What You Can Actually Do With It",
    'SYSTEM REQUIREMENTS': "System Requirements",
    'STEP-BY-STEP INSTALLATION': "Step-by-Step Installation",
    'SETTING UP OLLAMA (YOUR FREE AI BRAIN)': "Setting Up Ollama as Your Provider (This Is the Key Step)",
    'YOUR FIRST CHAT': "Your First Chat",
    'GOING BEYOND: CONFIGURING OTHER PROVIDERS': "Going Beyond: Configuring Other Providers",
    'ADVANCED SETUP: OPEN WEBUI FOR A CHATGPT-LIKE INTERFACE': "Advanced Setup: Open WebUI for a ChatGPT-Like Interface",
    'SECURITY & SAFETY SETTINGS EVERY BEGINNER MUST KNOW': "Security & Safety Settings Every Beginner Must Know",
    'THE MOST COMMON MISTAKES (AND HOW TO FIX THEM)': "The Most Common Mistakes (And How to Fix Them)",
    'FREQUENTLY ASKED QUESTIONS': "Frequently Asked Questions",
    "WHAT'S NEXT? YOUR LEARNING ROADMAP": "What's Next? Your Learning Roadmap",
    'QUICK REFERENCE CHEAT SHEET': "Quick Reference Cheat Sheet",
    'RESOURCES & LINKS': "Resources & Links",
}

def is_section_header(stripped):
    if not stripped:
        return False
    m = re.match(r'^(\d+)\.\s+(.+)', stripped)
    if not m:
        return False
    title = m.group(2)
    return title.startswith(tuple(SECT_MAP.keys())) or title.isupper()

def parse_ascii_table(lines):
    parsed = []
    for line in lines:
        s = line.strip()
        if not s or s[0] in '┌├└':
            continue
        cells = [c.strip() for c in s.split('│') if c.strip() not in ('', '─')]
        if cells:
            parsed.append(cells)
    return parsed

def html_table(rows):
    if not rows:
        return ''
    out = ['<table>']
    out.append('<thead><tr>')
    for cell in rows[0]:
        out.append(f'<th>{escape(cell)}</th>')
    out.append('</tr></thead>')
    out.append('<tbody>')
    for row in rows[1:]:
        out.append('<tr>')
        for cell in row:
            out.append(f'<td>{escape(cell)}</td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)

CSS = open('~/skills/creative/document-styling/references/weasyprint-light-professional.css').read()

def build_html(content_lines):
    parts = [f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Guide</title><style>{CSS}</style></head><body>']

    i = 0
    state = 'cover'

    while i < len(content_lines):
        raw = content_lines[i]
        stripped = raw.strip()

        # Skip decorative rules
        if stripped.startswith('===') or (set(stripped) <= set('=─') and len(stripped) > 3):
            i += 1
            continue
        if stripped.startswith('───') or (set(stripped) <= set('─') and len(stripped) > 3):
            i += 1
            continue

        # Cover page
        if state == 'cover':
            if "THE ULTIMATE BEGINNER'S GUIDE TO HERMES AGENT" in stripped:
                parts.append('<div class="cover"><h1>The Ultimate Beginner\'s Guide to Hermes Agent</h1>')
                i += 1
                continue
            if 'Run Your Own AI Agent for FREE with Ollama' in stripped:
                parts.append('<div class="tagline">Run Your Own AI Agent for FREE with Ollama</div>')
                i += 1
                continue
            if 'By PhantomByte.com' in stripped:
                parts.append('<div class="meta">By PhantomByte.com</div></div>')
                i += 1
                continue
            if stripped == 'TABLE OF CONTENTS':
                state = 'toc'
                parts.append('<div class="page-break"></div><h2 style="margin-top:0;">Table of Contents</h2>')
                i += 1
                continue
            i += 1
            continue

        # TOC
        if state == 'toc':
            if stripped == '':
                i += 1
                continue
            m = re.match(r'^(\d+\.\s)(.+)', stripped)
            if m:
                parts.append(f'<div class="toc-item"><span class="toc-num">{m.group(1)}</span>{m.group(2)}</div>')
                i += 1
                continue
            state = 'body'
            parts.append('</div>')
            parts.append('<div class="page-break"></div>')

        # Section headers
        if is_section_header(stripped):
            m = re.match(r'^(\d+)\.\s+(.+)', stripped)
            title = m.group(2)
            mapped = SECT_MAP.get(title, title.title() if title.isupper() else title)
            parts.append(f'<h2>{escape(mapped)}</h2>')
            i += 1
            continue

        # Sub-section --- ... ---
        m = re.match(r'^---\s+(.+?)\s+---$', stripped)
        if m:
            parts.append(f'<h3>{escape(m.group(1))}</h3>')
            i += 1
            continue

        # ASCII tables
        if stripped.startswith(('┌', '├', '└', '│')):
            table_lines = []
            while i < len(content_lines) and content_lines[i].strip().startswith(('┌', '├', '└', '│')):
                table_lines.append(content_lines[i].rstrip())
                i += 1
            rows = parse_ascii_table(table_lines)
            parts.append(html_table(rows))
            continue

        # Code blocks
        is_code = False
        if stripped and (raw.startswith('  ') or raw.startswith('\t')):
            code_kw = ['$', 'curl ', 'pip ', 'ollama ', 'hermes ', 'docker ', 'python3 ', 'iex ', 'wsl ', 'source ', 'cat ', 'echo ', 'cd ', 'ls ', 'rm ', 'mkdir ', 'git ', 'npm ', 'npx ', 'uv ', 'open-webui', 'modelfile']
            if any(k in stripped.lower() for k in code_kw) or stripped.startswith('# ') or stripped.startswith('// ') or raw.startswith('    '):
                is_code = True

        if is_code:
            code_lines = []
            while i < len(content_lines):
                cl = content_lines[i]
                if cl.rstrip() == '':
                    if i + 1 < len(content_lines) and (content_lines[i+1].startswith('  ') or content_lines[i+1].startswith('\t')):
                        code_lines.append('')
                        i += 1
                        continue
                    else:
                        break
                if cl.startswith('  ') or cl.startswith('\t') or cl.strip().startswith('# '):
                    code_lines.append(cl.rstrip())
                    i += 1
                else:
                    break
            if code_lines:
                parts.append(f'<pre>{escape("\n".join(code_lines))}</pre>')
            continue

        # Bullet lists
        if stripped.startswith(('• ', '- ', '* ')) or raw.startswith('  • ') or raw.startswith('    • ') or raw.startswith('  - ') or raw.startswith('    - '):
            parts.append('<ul>')
            while i < len(content_lines):
                bl = content_lines[i]
                if bl.rstrip() == '':
                    if i + 1 < len(content_lines) and (content_lines[i+1].strip().startswith(('• ', '- ', '* ')) or content_lines[i+1].startswith('  • ') or content_lines[i+1].startswith('    • ') or content_lines[i+1].startswith('  - ') or content_lines[i+1].startswith('    - ')):
                        i += 1
                        continue
                    else:
                        break
                content = bl.lstrip()
                if content.startswith('• ') or content.startswith('- ') or content.startswith('* '):
                    content = content[2:]
                parts.append(f'<li>{escape(content)}</li>')
                i += 1
            parts.append('</ul>')
            continue

        # Checklist items
        if stripped.startswith(('☐ ', '✅ ')):
            parts.append('<ul>')
            while i < len(content_lines):
                nl = content_lines[i]
                nl_stripped = nl.strip()
                if nl_stripped.startswith(('☐ ', '✅ ')):
                    sym = '☐' if nl_stripped.startswith('☐') else '✅'
                    parts.append(f'<li>{sym} {escape(nl_stripped[2:])}</li>')
                    i += 1
                elif nl.rstrip() == '':
                    if i + 1 < len(content_lines) and content_lines[i+1].strip().startswith(('☐ ', '✅ ')):
                        i += 1
                        continue
                    else:
                        break
                else:
                    break
            parts.append('</ul>')
            continue

        # FAQ Q: / A:
        if stripped.startswith('Q: ') or stripped.startswith('A: '):
            prefix = stripped[:2]
            content = stripped[3:]
            tag = '<strong>Q:</strong>' if prefix == 'Q:' else '<strong>A:</strong>'
            parts.append(f'<p>{tag} {escape(content)}</p>')
            i += 1
            continue

        # All-caps short indented subheadings
        if stripped.isupper() and 3 < len(stripped) < 50 and raw.startswith('  '):
            parts.append(f'<h4>{escape(stripped)}</h4>')
            i += 1
            continue

        # Regular paragraph
        if stripped:
            parts.append(f'<p>{escape(stripped)}</p>')

        i += 1

    parts.append('</body></html>')
    return '\n'.join(parts)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 convert-text-to-html.py input.txt output.html')
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        lines = f.read().replace('—', '–').split('\n')
    html = build_html(lines)
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {len(html)} chars to {sys.argv[2]}')
