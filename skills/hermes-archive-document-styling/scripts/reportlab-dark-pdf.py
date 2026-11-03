#!/usr/bin/env python3
"""
Reference script: Dark-themed branded PDF from flat text source.
Copy and modify brand colors/styles for each new document.
Requires: pip install reportlab Pillow
"""

import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, PageTemplate, NextPageTemplate
)

# ── Brand Palette ── (EDIT PER BRAND)
BG       = HexColor("#0A0A0A")
TEXT     = HexColor("#E0E0E0")
HEADING  = HexColor("#FFFFFF")
ACCENT   = HexColor("#00FF88")
DIM      = HexColor("#555555")
CODE_BG  = HexColor("#141414")
ACCENT2  = HexColor("#1A1A1A")
TABLE_HDR= HexColor("#0F0F0F")

PAGE_W, PAGE_H = letter
MARGIN = 0.82 * inch

# ── Helpers ──
def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def green(t):
    return f'<font color="{ACCENT.hexval()}">{esc(t)}</font>'

def hl_inline(text):
    for kw in ["ollama", "hermes", "docker", "curl", "pip"]:
        text = re.sub(rf'\b({re.escape(kw)})\b', green(r'\1'), text)
    return text

# ── Page callbacks ──
def dark_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.restoreState()

def make_styles(s):
    s.add(ParagraphStyle("PBody", parent=s["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=14, textColor=TEXT, spaceAfter=6))
    s.add(ParagraphStyle("PH1", parent=s["Heading1"],
        fontName="Helvetica-Bold", fontSize=17, leading=22, textColor=ACCENT, spaceAfter=10, spaceBefore=12))
    s.add(ParagraphStyle("PH2", parent=s["Heading2"],
        fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=HEADING, spaceAfter=6, spaceBefore=9))
    s.add(ParagraphStyle("PCode", fontName="Courier", fontSize=8.5, leading=11.5,
        textColor=ACCENT, backColor=CODE_BG, leftIndent=16, rightIndent=12, spaceAfter=4))
    s.add(ParagraphStyle("PBullet", parent=s["Normal"],
        fontName="Helvetica", fontSize=10, leading=13, textColor=TEXT,
        leftIndent=26, firstLineIndent=-12, spaceAfter=3))
    s.add(ParagraphStyle("PFaqQ", parent=s["Normal"],
        fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=ACCENT, leftIndent=12, spaceAfter=1))
    s.add(ParagraphStyle("PFaqA", parent=s["Normal"],
        fontName="Helvetica", fontSize=10.5, leading=13, textColor=TEXT, leftIndent=26, spaceAfter=6))
    s.add(ParagraphStyle("PCell", parent=s["Normal"],
        fontName="Helvetica", fontSize=8, leading=10, textColor=TEXT, spaceAfter=0))
    return s

# ── Parsers ──
def parse_blocks(lines):
    blocks = []
    text_buf = []; code_buf = []; table_buf = []
    in_code = False; in_table = False
    def ftxt():
        nonlocal text_buf
        if text_buf: blocks.append(("text", "\n".join(text_buf))); text_buf = []
    def fcode():
        nonlocal code_buf
        if code_buf: blocks.append(("code", "\n".join(code_buf))); code_buf = []
    def ftbl():
        nonlocal table_buf
        if table_buf: blocks.append(("table", list(table_buf))); table_buf = []

    for line in lines:
        s = line.rstrip("\n"); st = s.strip()
        if st == "": ftxt(); in_code=False; in_table=False; continue
        if len(st) > 24 and set(st).issubset({"=","─"}): ftxt(); blocks.append(("hr", None)); in_code=False; continue
        if s.startswith(("┌","├","└","│")):
            if not in_table: ftxt(); in_table = True
            table_buf.append(s); continue
        elif in_table: ftbl(); in_table = False
        if re.match(r'^\d+\.\s', st): ftxt(); blocks.append(("h1", st)); continue
        if re.match(r'^---\s+Step\s+\d', st, re.I) or st.upper() in {"WINDOWS:","MAC:","LINUX:","IMPORTANT:"}:
            ftxt(); blocks.append(("h2", st)); continue
        trimmed = s.lstrip(); indent = len(s)-len(trimmed)
        if indent >= 2 and any(trimmed.startswith(p) for p in ('# ','>','ollama ','hermes ','curl ','docker ')):
            if not in_code: ftxt(); in_code = True
            code_buf.append(trimmed); continue
        elif in_code and indent >= 2: code_buf.append(trimmed); continue
        elif in_code: fcode(); in_code = False
        if st.startswith(("Q: ","A: ")): ftxt(); blocks.append(("faq", st)); continue
        m = re.match(r'^(\s*)([✅•❌✓✗☐]|[\-\*])\s+(.*)$', st)
        if m: ftxt(); blocks.append(("bullet", m.group(2), m.group(3))); continue
        if re.match(r'^\s+\d+\.\s', s) or re.match(r'^\s+[–-]\s', s): ftxt(); blocks.append(("toc", st)); continue
        text_buf.append(s)
    ftxt(); fcode(); ftbl(); return blocks

def parse_ascii_table(lines):
    if not lines: return []
    sep = next((l for l in lines if "┼" in l), None)
    if not sep: sep = lines[0]
    divs = [i for i,c in enumerate(sep) if c in "┼┤├┬┴"]
    data = []
    for line in lines:
        if not line.startswith("│"): continue
        cells=[]; prev=1
        for pos in divs + [len(line)]:
            if pos > len(line): pos = len(line)
            cell = line[prev:pos].strip().strip("│"); cells.append(cell); prev=pos+1
        if any(c for c in cells): data.append(cells)
    return data

def make_table_obj(lines, styles):
    cells = parse_ascii_table(lines)
    if not cells: return Spacer(1, 0.1*inch)
    ncols = max(len(r) for r in cells)
    cw = (PAGE_W - 2*MARGIN) / ncols
    tbl = []
    for ri, row in enumerate(cells):
        r = []
        for ci, c in enumerate(row):
            p = Paragraph(f'<b>{esc(c)}</b>', styles["PCell"]) if ri == 0 else Paragraph(esc(c), styles["PCell"])
            r.append(p)
        while len(r) < ncols:
            r.append(Paragraph("", styles["PCell"]))
        tbl.append(r)
    t = Table(tbl, colWidths=[cw]*ncols, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HDR), ('TEXTCOLOR', (0,0), (-1,0), ACCENT),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('BACKGROUND', (0,1), (-1,-1), ACCENT2),
        ('GRID', (0,0), (-1,-1), 0.35, DIM), ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

# ── Build ──
def build(source_txt, out_pdf, cover_img=None):
    doc = SimpleDocTemplate(out_pdf, pagesize=letter,
                            rightMargin=MARGIN, leftMargin=MARGIN,
                            topMargin=MARGIN-10, bottomMargin=MARGIN-10)
    fmain = Frame(MARGIN, MARGIN-6, PAGE_W-2*MARGIN, PAGE_H-2*MARGIN+12, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    def cover_cb(canvas, doc):
        canvas.saveState(); canvas.setFillColor(BG); canvas.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
        if cover_img:
            iw, ih = 1672, 941  # adjust per actual image
            pr, ir = PAGE_W/PAGE_H, iw/ih
            if ir > pr: nh = PAGE_H; nw = iw*(PAGE_H/ih)
            else: nw = PAGE_W; nh = ih*(PAGE_W/iw)
            canvas.drawImage(cover_img, (PAGE_W-nw)/2, (PAGE_H-nh)/2, nw, nh, preserveAspectRatio=True, anchor='c')
        canvas.restoreState()

    cover_pt = PageTemplate(id='cover', frames=[fmain], onPage=cover_cb)
    inner_pt = PageTemplate(id='inner', frames=[fmain], onPage=dark_bg)
    doc.addPageTemplates([cover_pt, inner_pt])
    styles = make_styles(getSampleStyleSheet())
    story = []

    story.append(NextPageTemplate('cover'))
    story.append(Spacer(1, 0.5*inch))
    story.append(PageBreak())
    story.append(NextPageTemplate('inner'))

    # Title page
    story.append(Spacer(1, 1.0*inch))
    story.append(Paragraph("DOCUMENT TITLE", ParagraphStyle("", fontName="Helvetica-Bold", fontSize=30,
        leading=36, textColor=ACCENT, alignment=TA_CENTER)))
    story.append(PageBreak())

    with open(source_txt, "r", encoding="utf-8") as f: lines = f.readlines()
    for item in parse_blocks(lines):
        tag = item[0]
        if tag == "text":
            body = hl_inline(esc(item[1].strip()))
            for para in body.split("\n\n"):
                if para.strip(): story.append(Paragraph(para.strip(), styles["PBody"]))
        elif tag == "h1":
            m = re.match(r'^(\d+\.\s+)(.*)$', item[1])
            story.append(Paragraph(f'{green(m.group(1))}{esc(m.group(2))}' if m else esc(item[1]), styles["PH1"]))
        elif tag == "h2": story.append(Paragraph(esc(item[1]), styles["PH2"]))
        elif tag == "code":
            for cl in item[1].split("\n"): story.append(Paragraph(esc(cl), styles["PCode"]))
            story.append(Spacer(1, 0.05*inch))
        elif tag == "table":
            story.append(Spacer(1, 0.06*inch)); story.append(make_table_obj(item[1], styles)); story.append(Spacer(1, 0.1*inch))
        elif tag == "bullet":
            mk, ctx = item[1], item[2]
            color = ACCENT.hexval() if mk in ("✅","✓") else ("#FF4444" if mk in ("❌","✗") else TEXT.hexval())
            sym = {"✅":"&#x2705;","❌":"&#x274C;","☐":"&#x2610;","•":"&#x2022;","✓":"&#x2713;","✗":"&#x2717;","-":"&#x2022;","*":"&#x2022;"}.get(mk, "&#x2022;")
            story.append(Paragraph(f'<font color="{color}">{sym}</font> {esc(ctx)}', styles["PBullet"]))
        elif tag == "faq": story.append(Paragraph(esc(item[1]), styles["PFaqQ"] if item[1].startswith("Q:") else styles["PFaqA"]))
        elif tag == "toc": story.append(Paragraph(green(item[1]), styles["PBody"]))
        elif tag == "hr": story.append(Spacer(1, 0.12*inch))

    doc.build(story)
    print(f"PDF created: {out_pdf}")

if __name__ == "__main__":
    build("source.txt", "output.pdf", cover_img="cover.png")
