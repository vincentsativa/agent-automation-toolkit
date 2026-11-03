#!/usr/bin/env python3
"""
STOP BURNING TOKENS tutorial -> HTML for WeasyPrint PDF.
Custom parser for a "=== ALL-CAPS ===" tutorial with fenced code blocks (----).
Strips the DISTRIBUTION ASSETS section and its TOC entry per user request.
"""
import re
import html as html_mod

SRC = "/mnt/c/Users/<user>/OneDrive/Desktop/Stop Burning Tokens - $24.99/STOP BURNING TOKENS - COMPLETE.txt"
OUT = "/tmp/doc.html"

with open(SRC, "r", encoding="utf-8") as f:
    text = f.read()

# Mandatory: em dash -> en dash
text = text.replace("\u2014", "\u2013")

lines = text.split("\n")

# Strip everything from the DISTRIBUTION ASSETS header onward.
# Also drop its numbered TOC entry.
CUT_MARKER = "DISTRIBUTION ASSETS"
end_idx = None
for i, ln in enumerate(lines):
    if ln.strip() == CUT_MARKER:
        end_idx = i
        break
if end_idx is not None:
    lines = lines[:end_idx]

# Remove the numbered TOC entry "14. Distribution Assets"
filtered = []
for ln in lines:
    if re.match(r"^\s*\d+\.\s+Distribution Assets\s*$", ln):
        continue
    filtered.append(ln)
lines = filtered


def escape_inline(p):
    p = html_mod.escape(p)
    p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    p = re.sub(r"`(.+?)`", r"<code>\1</code>", p)
    return p


RULER_RE = re.compile(r"^[═\u2550\-\=\u2500]{3,}$")
CODE_FENCE_RE = re.compile(r"^-{40,}$")  # 80-hyphen code delimiters
H2_WRAPPED_RE = re.compile(r"^===\s*(.*?)\s*===$")
SUB_H3_RE = re.compile(r"^\d+\.\d+\s+.*$")
H4_RE = re.compile(
    r"^(STEP\s+\d+|PHASE\s+\d+|TIER\s+1(?:\.\d)?|WHAT YOU NEED|WHAT TO TRACK|"
    r"LOGPROB-BASED|CONSISTENCY CHECKING|THE FAILURE|THE FIX|CACHE QUANTIZATION|"
    r"CONTEXT WINDOW DISCIPLINE|PREFIX CACHING|SESSION REUSE|CONTINUOUS BATCHING|"
    r"BATCH SIZE TUNING|THE ECONOMICS|REQUESTS BY TIER|ESCALATION RATE|"
    r"FALSE ESCALATION RATE|FALSE ACCEPTANCE RATE|COST PER REQUEST|TOTAL SAVINGS|"
    r"LATENCY BY TIER|INGRESS|CONFIDENCE PROBE|DECISION GATE|ESCALATION$|LOGGING$|"
    r"COST TRACKER|CLASSIFICATION / EXTRACTION|SUMMARIZATION / FORMATTING|"
    r"CODE GENERATION|PLANNING / REASONING|MEMORY:|SPEED:|QUALITY:|WHEN TO USE:)"
)
BULLET_RE = re.compile(r"^[-*•]\s+")
NUM_ITEM_RE = re.compile(r"^\d+\.\s+")

# Cover title handling
TITLE_H1 = "STOP BURNING TOKENS: A DEVELOPER'S GUIDE TO MODEL ROUTING THAT ACTUALLY CUTS COSTS"
TITLE_SUB = "A Developer's Guide to Confidence-Threshold Routing, Quantization, and Production Cost Optimization"

# Extract IN THIS TUTORIAL bullets for the cover topic list.
cover_toc = []
in_toc = False
for ln in lines:
    s = ln.strip()
    if s == "IN THIS TUTORIAL":
        in_toc = True
        continue
    if in_toc:
        if s == "OVERVIEW" or re.match(r"^===\s*[A-Za-z]", s):
            break
        m = BULLET_RE.match(ln)
        if m:
            cover_toc.append(escape_inline(ln[m.end():].strip()))
        elif s:
            cover_toc.append(escape_inline(s))

body_html = []
in_code = False
code_buf = []
bullet_buf = []
para_buf = []


def flush_para():
    global para_buf
    if para_buf:
        body_html.append("<p>" + " ".join(para_buf) + "</p>")
        para_buf = []


def flush_bullets():
    global bullet_buf
    if bullet_buf:
        items = "".join(f"<li>{b}</li>" for b in bullet_buf)
        body_html.append(f"<ul class=\"std\">{items}</ul>")
        bullet_buf = []


def close_all():
    global in_code, code_buf
    flush_bullets()
    flush_para()
    if in_code:
        body_html.append("<pre><code>" + "\n".join(code_buf) + "</code></pre>")
        in_code = False
        code_buf = []


for ln in lines:
    stripped = ln.strip()

    # Empty line: close containers, produce nothing.
    if not stripped:
        close_all()
        continue

    # Code fence delimiters (long hyphens)
    if CODE_FENCE_RE.match(ln) and len(stripped) >= 40:
        flush_bullets()
        flush_para()
        if in_code:
            body_html.append("<pre><code>" + "\n".join(code_buf) + "</code></pre>")
            in_code = False
            code_buf = []
        else:
            in_code = True
        continue

    if in_code:
        code_buf.append(ln)
        continue

    # Decorative ruler (===)
    if RULER_RE.match(ln):
        close_all()
        continue

    # Wrapped ALL-CAPS header === ... ===
    m = H2_WRAPPED_RE.match(stripped)
    if m:
        close_all()
        title = m.group(1).strip()
        body_html.append(f"<h2>{escape_inline(title)}</h2>")
        continue

    # Sub-section 1.1 etc
    if SUB_H3_RE.match(stripped):
        close_all()
        body_html.append(f"<h3>{escape_inline(stripped)}</h3>")
        continue

    # Sub-sub headings
    if H4_RE.match(stripped):
        close_all()
        body_html.append(f"<h4>{escape_inline(stripped)}</h4>")
        continue

    # Bullets
    if BULLET_RE.match(ln):
        flush_para()
        item = escape_inline(ln[re.match(r"^[-*•]\s*", ln).end():])
        bullet_buf.append(item)
        continue
    if NUM_ITEM_RE.match(ln):
        close_all()
        m = NUM_ITEM_RE.match(ln)
        num = m.group(0).strip()[:-1]
        rest = escape_inline(ln[m.end():])
        body_html.append(
            f"<p class=\"num-item\"><span class=\"num\">{num}.</span>{rest}</p>"
        )
        continue

    # Normal paragraph line: buffer, join consecutive lines into one <p>.
    para_buf.append(escape_inline(stripped))

close_all()

cover_toc_html = "".join(f"<li>{b}</li>" for b in cover_toc)

CSS = """
@page {
  size: letter;
  margin: 0.9in 1in 1.1in 1in;
  @bottom-center { content: counter(page); font-family: "Liberation Sans", Arial, sans-serif; font-size: 9pt; color: #666; }
}
@page:first { margin: 0; @bottom-center { content: none; } }
body { font-family: "Liberation Serif", Georgia, serif; font-size: 12pt; line-height: 1.55; color: #1a1a1a; margin: 0; padding: 0; }
.cover-wrap { background: linear-gradient(150deg, #1b263b 0%, #415a77 80%, #556e8a 100%); color: #fff; padding: 34pt 48pt 26pt 48pt; text-align: center; }
.cover-tag { font-family: "Liberation Sans", Arial, sans-serif; font-size: 10pt; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,0.65); margin: 0 0 14pt 0; }
.cover-wrap h1 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 26pt; font-weight: 700; color: #fff; line-height: 1.18; margin: 0 0 10pt 0; }
.cover-sub { font-family: "Liberation Serif", Georgia, serif; font-size: 13pt; color: rgba(255,255,255,0.9); font-style: italic; margin: 4pt 0 10pt 0; line-height: 1.4; }
.cover-wrap hr { border: none; border-top: 1.5px solid rgba(255,255,255,0.35); width: 100px; margin: 0 auto 10pt auto; }
.cover-desc { font-family: "Liberation Sans", Arial, sans-serif; font-size: 10pt; color: rgba(255,255,255,0.75); line-height: 1.6; margin: 0; }
.what-learn { text-align: left; padding: 16pt 48pt 0 48pt; }
.what-learn h2 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 13pt; color: #1b263b; margin: 0 0 8pt 0; border-bottom: 2px solid #415a77; padding-bottom: 4pt; }
.what-learn ul { margin: 4pt 0 0 0; padding-left: 20pt; }
.what-learn li { font-size: 11.5pt; margin-bottom: 4pt; }
.body-inner { padding: 4pt 48pt 24pt 48pt; }
h2 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 15pt; color: #1b263b; margin: 22pt 0 10pt 0; border-bottom: 2px solid #415a77; padding-bottom: 4pt; page-break-after: avoid; }
h3 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 13pt; color: #415a77; margin: 16pt 0 6pt 0; page-break-after: avoid; }
h4 { font-family: "Liberation Sans", Arial, sans-serif; font-size: 12pt; color: #1b263b; margin: 11pt 0 4pt 0; font-weight: 700; page-break-after: avoid; }
p { text-align: justify; orphans: 3; widows: 3; margin: 6pt 0; font-size: 12pt; }
pre { background: #f4f6f8; border-left: 3px solid #415a77; padding: 8pt 10pt; font-family: "Liberation Mono", Consolas, monospace; font-size: 8.5pt; line-height: 1.35; white-space: pre-wrap; margin: 8pt 0; }
code { font-family: "Liberation Mono", Consolas, monospace; font-size: 10pt; background: #eef0f3; padding: 1pt 3pt; }
pre code { background: transparent; padding: 0; font-size: 8.5pt; }
ul.std { margin: 6pt 0 8pt 0; padding-left: 20pt; }
ul.std li { margin-bottom: 3pt; font-size: 11.5pt; }
p.num-item { margin: 3pt 0; padding-left: 26pt; text-indent: -26pt; }
span.num { display: inline-block; width: 20pt; font-weight: 700; color: #415a77; }
strong { font-weight: 700; color: #1b263b; }
"""

html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>STOP BURNING TOKENS</title>
<style>{CSS}</style>
</head>
<body>
<div class="cover-wrap">
  <p class="cover-tag">Developer Tutorial</p>
  <h1>{TITLE_H1}</h1>
  <p class="cover-sub">{TITLE_SUB}</p>
  <hr/>
  <p class="cover-desc">By Phantom-Byte.com</p>
</div>
<div class="what-learn">
  <h2>IN THIS TUTORIAL</h2>
  <ul>{cover_toc_html}</ul>
</div>
<div class="body-inner">
{''.join(body_html)}
</div>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_doc)

# Pre-flight checks
import re as _re
p_count = len(_re.findall(r"<p>", html_doc))
print(f"Cover TOC items: {len(cover_toc)}")
print(f"<p> tags: {p_count}")
print(f"<pre> blocks: {html_doc.count('<pre>')}")
print(f"HTML chars: {len(html_doc)}")
print(f"Source chars: {len(text)}")
