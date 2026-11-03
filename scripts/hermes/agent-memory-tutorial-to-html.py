#!/usr/bin/env python3
"""PhantomByte tutorial -> HTML for WeasyPrint PDF.
Format: markdown ## N / ### N.N headers, --- CODE EXAMPLE: X --- labels,
fenced ``` code blocks, ☐ checklists, - bullets. Strips distribution assets
(X POST / PINTEREST / KEYWORDS). Em dashes replaced with en dashes."""
import re, html

SRC = '/mnt/c/Users/<user>/OneDrive/Desktop/Give Your Agent a Memory/GIVE YOUR AGENT A MEMORY COMPLETE.txt'
OUT = '/tmp/agent_memory.html'

def esc(p):
    p = html.escape(p)
    p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
    p = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p)
    p = re.sub(r'`(.+?)`', r'<code>\1</code>', p)
    return p

def main():
    text = open(SRC, encoding='utf-8').read()
    text = text.replace('\u2014', '\u2013')
    lines = text.split('\n')

    # ---- pass 1: extract TOC bullets between "IN THIS TUTORIAL" and the
    # blank line that precedes the duplicated title / OVERVIEW section ----
    toc_items = []
    in_toc = False
    for i, raw in enumerate(lines):
        ln = raw.strip()
        if ln == 'IN THIS TUTORIAL':
            in_toc = True
            continue
        if in_toc:
            if ln.startswith('- '):
                toc_items.append(ln[2:].strip())
            elif not ln and toc_items:
                break  # blank line after bullets ends TOC
            elif ln and not ln.startswith('- ') and toc_items:
                break

    # ---- pass 2: build body, skipping cover block + TOC block + dist assets
    body = []
    in_code = False
    code_buf = []
    bullet_buf = []
    checklist_buf = []
    para_buf = []
    skip_dist = False

    # cover metadata lines 1-7 (skip), then intro starts at line 9
    body_start = None
    for i, raw in enumerate(lines, 1):
        if body_start is None:
            if i in (1,2,3,4,5,6,7):
                continue
            if raw.strip() == '':
                continue
            body_start = i
        break
    # simpler: start body index at line 9 (0-index 8), but skip metadata lines individually

    def flush_para():
        if para_buf:
            body.append('<p>' + esc(' '.join(para_buf)) + '</p>')
            del para_buf[:]
    def flush_bullets():
        if bullet_buf:
            body.append('<ul class="std">' + ''.join('<li>'+esc(b)+'</li>' for b in bullet_buf) + '</ul>')
            del bullet_buf[:]
    def flush_checklist():
        if checklist_buf:
            body.append('<ul class="checklist">' + ''.join('<li>'+esc(c)+'</li>' for c in checklist_buf) + '</ul>')
            del checklist_buf[:]

    # lines to skip entirely (cover metadata + TOC + duplicate title)
    skip_lines = set()
    in_toc = False
    for i, raw in enumerate(lines, 1):
        ln = raw.strip()
        if ln == 'IN THIS TUTORIAL':
            in_toc = True
            skip_lines.add(i)
            continue
        if in_toc:
            skip_lines.add(i)
            if ln.startswith('- '):
                continue
            if not ln:
                in_toc = False
            continue
        # metadata header lines
        if i in (1,2,3,4,5,6,7):
            skip_lines.add(i)
        # duplicate full title right after TOC
        if ln.startswith('GIVE YOUR AGENT A MEMORY:') and i > 20:
            skip_lines.add(i)

    for i, raw in enumerate(lines, 1):
        if i in skip_lines:
            continue
        ln = raw.strip()

        # distribution assets guard
        if ln.startswith('X POST:') or ln.startswith('PINTEREST') or ln.startswith('KEYWORDS:'):
            skip_dist = True
            flush_para(); flush_bullets(); flush_checklist()
            continue
        if skip_dist:
            if re.match(r'^##\s', ln):
                skip_dist = False
            else:
                continue

        if not ln:
            flush_para(); flush_bullets(); flush_checklist()
            continue
        if re.match(r'^[═\u2550\-=\u2500]{3,}$', ln):
            flush_para(); flush_bullets(); flush_checklist()
            continue
        if ln.startswith('```'):
            flush_para(); flush_bullets(); flush_checklist()
            if in_code:
                body.append('<pre><code>' + '\n'.join(code_buf) + '</code></pre>')
                code_buf = []; in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(raw)
            continue
        m = re.match(r'^---\s*CODE EXAMPLE:\s*(.*?)\s*---$', ln)
        if m:
            flush_para(); flush_bullets(); flush_checklist()
            body.append('<h4>' + esc(m.group(1)) + '</h4>')
            continue
        m = re.match(r'^##\s+(.+)$', ln)
        if m:
            flush_para(); flush_bullets(); flush_checklist()
            h = m.group(1).strip().upper()
            cls = ' style="page-break-before: always;"' if h in ('OPTIMIZATION OPPORTUNITIES', 'ACTIONABLE TAKEAWAYS') else ''
            body.append('<h2%s>' % cls + esc(m.group(1)) + '</h2>')
            continue
        m = re.match(r'^###\s+(.+)$', ln)
        if m:
            flush_para(); flush_bullets(); flush_checklist()
            body.append('<h3>' + esc(m.group(1)) + '</h3>')
            continue
        if re.match(r'^[A-Z][A-Z\s,:/\'&0-9$.\-]+$', ln) and len(ln) > 6:
            flush_para(); flush_bullets(); flush_checklist()
            cls = ' style="page-break-before: always;"' if ln == 'ACTIONABLE TAKEAWAYS' else ''
            body.append('<h3%s>' % cls + esc(ln) + '</h3>')
            continue
        if ln.startswith('\u2610') or ln.startswith('\u2611') or ln.startswith('[]') or ln.startswith('[ ]'):
            flush_para(); flush_bullets()
            checklist_buf.append(ln.lstrip('\u2610\u2611[] '))
            continue
        if ln.startswith('- ') or ln.startswith('* '):
            flush_para(); flush_checklist()
            bullet_buf.append(ln[2:].strip())
            continue
        flush_bullets(); flush_checklist()
        para_buf.append(raw.strip())

    flush_para(); flush_bullets(); flush_checklist()
    if in_code and code_buf:
        body.append('<pre><code>' + '\n'.join(code_buf) + '</code></pre>')

    toc_html = '<ul>' + ''.join('<li>'+esc(t)+'</li>' for t in toc_items) + '</ul>'

    css = """@page { size: letter; margin: 0.9in 1in 1.1in 1in;
      @bottom-center { content: counter(page); font-family:"Liberation Sans",Arial,sans-serif; font-size:9pt; color:#666; } }
    @page:first { margin:0; @bottom-center { content:none; } }
    body { font-family:"Liberation Serif",Georgia,serif; font-size:11.5pt; line-height:1.5; color:#1a1a1a; margin:0; padding:0; }
    .cover-wrap { background:linear-gradient(150deg,#1b263b 0%,#415a77 80%,#556e8a 100%); color:#fff; padding:36pt 48pt 26pt 48pt; text-align:center; }
    .cover-tag { font-family:"Liberation Sans",Arial,sans-serif; font-size:10pt; letter-spacing:4px; text-transform:uppercase; color:rgba(255,255,255,0.65); margin:0 0 14pt 0; }
    .cover-wrap h1 { font-family:"Liberation Sans",Arial,sans-serif; font-size:24pt; font-weight:700; color:#fff; line-height:1.15; margin:0 0 10pt 0; }
    .cover-sub { font-family:"Liberation Serif",Georgia,serif; font-size:12.5pt; color:rgba(255,255,255,0.88); font-style:italic; margin:4pt 0 12pt 0; line-height:1.4; }
    .cover-wrap hr { border:none; border-top:1.5px solid rgba(255,255,255,0.35); width:100px; margin:0 auto 12pt auto; }
    .cover-desc { font-family:"Liberation Sans",Arial,sans-serif; font-size:9.5pt; color:rgba(255,255,255,0.72); line-height:1.55; margin:0; }
    .what-learn { background:#fff; padding:20pt 48pt 6pt 48pt; text-align:left; }
    .what-learn h2 { font-family:"Liberation Sans",Arial,sans-serif; font-size:13pt; color:#1b263b; margin:0 0 7pt 0; border-bottom:2px solid #415a77; padding-bottom:3pt; }
    .what-learn ul { margin:0 0 4pt 0; padding-left:18pt; }
    .what-learn li { font-size:10.5pt; margin-bottom:3pt; color:#333; }
    .body { padding:0 48pt 28pt 48pt; }
    h2 { font-family:"Liberation Sans",Arial,sans-serif; font-size:14pt; color:#1b263b; margin:22pt 0 10pt 0; border-bottom:2px solid #415a77; padding-bottom:4pt; page-break-after:avoid; }
    h3 { font-family:"Liberation Sans",Arial,sans-serif; font-size:12pt; color:#415a77; margin:16pt 0 6pt 0; page-break-after:avoid; }
    h4 { font-family:"Liberation Sans",Arial,sans-serif; font-size:11pt; color:#1b263b; margin:12pt 0 5pt 0; font-weight:700; page-break-after:avoid; }
    p { text-align:justify; orphans:3; widows:3; margin:6pt 0; }
    pre { background:#f4f6f8; border-left:3px solid #415a77; padding:8pt 10pt; font-family:"Liberation Mono",Consolas,monospace; font-size:8.5pt; line-height:1.35; white-space:pre-wrap; margin:7pt 0; }
    code { font-family:"Liberation Mono",Consolas,monospace; font-size:9pt; background:#eef0f3; padding:1pt 3pt; }
    pre code { background:transparent; padding:0; font-size:8.5pt; }
    ul.std { margin:4pt 0 6pt 0; padding-left:18pt; } ul.std li { margin-bottom:3pt; font-size:11pt; }
    ul.checklist { list-style:none; margin:4pt 0 6pt 0; padding-left:4pt; }
    ul.checklist li { margin-bottom:5pt; font-size:11pt; padding-left:20pt; text-indent:-20pt; }
    ul.checklist li::before { content:"\\2610  "; color:#415a77; }
    strong { font-weight:700; color:#1b263b; }"""

    doc = """<!DOCTYPE html><html><head><meta charset="utf-8"/>
<title>Give Your Agent a Memory</title><style>%s</style></head><body>
<div class="cover-wrap">
  <p class="cover-tag">PHANTOMBYTE TUTORIAL</p>
  <h1>Give Your Agent a Memory: Persistent Context That Survives Sessions</h1>
  <p class="cover-sub">How to Build a Memory Architecture That Lets Your Agent Learn Across Every Session</p>
  <hr/>
  <p class="cover-desc">A PhantomByte tutorial on building persistent, retrievable agent memory that survives sessions.</p>
</div>
<div class="what-learn"><h2>IN THIS TUTORIAL</h2>%s</div>
<div class="body">%s</div>
</body></html>""" % (css, toc_html, '\n'.join(body))

    open(OUT, 'w', encoding='utf-8').write(doc)
    p = len(re.findall(r'<p>', doc))
    # content integrity: char count of body text
    bodytext = ' '.join(body)
    print(f"<p> tags: {p} | TOC items: {len(toc_items)}")
    print(f"body HTML chars: {len(bodytext)}")
    # verify distribution assets stripped
    low = doc.lower()
    print("X POST present:", 'x post' in low, "| PINTEREST:", 'pinterest' in low, "| KEYWORDS:", 'keywords' in low)
    print("em dash in HTML:", '\u2014' in doc)

if __name__ == '__main__':
    main()
