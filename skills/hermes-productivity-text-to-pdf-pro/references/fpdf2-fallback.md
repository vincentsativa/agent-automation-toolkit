# fpdf2 Fallback Renderer

Use when WeasyPrint is unavailable, overkill, or when you want to build a PDF entirely in Python without generating an intermediate HTML file.

## When to use
- The system does not have WeasyPrint or its C dependencies (Pango, Cairo).
- The hermes-agent venv is already available and `pip3 install fpdf2` works there.
- You need a small number of pages (≤10) with a dark gradient cover and clean sections.

## Install

```bash
~/.hermes/hermes-agent/venv/bin/pip3 install fpdf2
```

Then run scripts with `~/.hermes/hermes-agent/venv/bin/python3`.

## Key rendering patterns (proven May 28 2026)

### Fonts
Load from `/usr/share/fonts/truetype/dejavu/`:
- `DejaVuSans.ttf` (regular)
- `DejaVuSans-Bold.ttf`
- `DejaVuSans-Oblique.ttf`
- `DejaVuSansMono.ttf`

Register with `pdf.add_font("Reg", "", path, uni=True)` etc.

### Dark gradient cover
Draw a gradient by stacking thin horizontal `pdf.line()` calls with interpolated RGB:
```python
def gradient(x, y, w, h, c1, c2, steps=120):
    for i in range(steps):
        t = i/steps
        r = c1[0] + (c2[0]-c1[0])*t
        g = c1[1] + (c2[1]-c1[1])*t
        b = c1[2] + (c2[2]-c1[2])*t
        pdf.set_draw_color(int(r),int(g),int(b))
        pdf.set_line_width(0.5)
        yy = y + h*i/steps
        pdf.line(x, yy, x+w, yy)
```

### Bold interleaving inside `write()`
fpdf2 `write()` cannot switch styles mid-call natively; you must toggle the font face between fragments:
```python
def bold_write(txt, size, base_style=""):
    parts = re.split(r"(\*\*[^\*]+\*\*)", txt)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("Reg", "B", size)
            pdf.write(lh, part[2:-2])
        else:
            pdf.set_font("Reg", base_style, size)
            pdf.write(lh, part)
```

### Pagination guard
Prevent section headers or code blocks from stranding at the bottom of a page:
```python
def ensure_space(needed):
    if pdf.get_y() + needed > PAGE_H - BOTTOM_MARGIN:
        pdf.add_page()
```

### Quote box with accent bar
Draw a 1.3mm vertical blue line on the left, then wrap italic text next to it.

### Code block
Gray fill rectangle + left border + monospace lines.

## Pitfalls
- `pdf.add_font(..., uni=True)` shows DeprecationWarnings but is still required for Unicode; the deprecation is not yet enforced.
- `ln=1` in `pdf.cell()` is also deprecated in fpdf2 ≥2.5.2 but still works; ignore the warning for now.
- Do NOT use `pdf.set_font("Reg", "BI", size)` unless you registered a Bold+Oblique font face explicitly; use "B" then "I" toggles instead.
- System `pip3` may fail with PEP 668; always target the hermes-agent venv `pip3`.
