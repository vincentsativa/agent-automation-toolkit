# Blueprint / Guide Format (Format D)

A fourth plain-text format variant: long-form guide documents with PART headers, TIER headers, spec-list sections, checkboxes `[ ]`, and a TOC extracted from a "This blueprint covers" paragraph.

## Source document
The Sovereign AI Stack Blueprint (Revised & Expanded Edition) — 870 lines, 34KB.

## Key differences from other formats

| Feature | Format A (Tutorial) | Format C (Guide) | Format D (Blueprint) |
|---|---|---|---|
| TOC source | `WHAT YOU WILL LEARN` bullets | None (3-line metadata) | "This blueprint covers EVERY path" paragraph bullets |
| Section headers | Roman numerals or `===` wrapped | `===` wrapped | `PART N:` and `TIER N:` |
| Sub-headers | `Example N`, `TIER N` | `6GB VRAM:` tier labels | `PHASE N:`, `WEEK N:`, `MINIMUM SPECS`, `WHAT YOU CAN RUN`, `PROS`, `CONS`, `BEST FOR`, `CURRENT LINEUP`, `HARDWARE OPTIONS`, `POPULAR CONFIGURATIONS`, `WHAT IS IT`, `COST`, `PROVIDERS`, `SOVEREIGNTY LEVEL`, `QUICK START`, `FEATURES YOU GET`, `ALTERNATIVE`, `KEY CAPABILITIES`, `AGENT ARCHITECTURE PATTERN`, `EXAMPLE`, `CRITICAL`, `TOTAL`, `LAYER N:` |
| Checkboxes | `☐` | None | `[ ]` and `[x]` |
| Spec lists | No | No | Yes — CPU:/GPU:/RAM:/STORAGE:/PSU:/CASE:/COOLER: lines with pipe-separated values |
| Code keywords | Standard set | Standard set | Adds `wget`, `sudo`, `export`, `openclaw` |

## Detection rules specific to this format

### PART headers
```
^PART\s+(\d+):\s*(.*)$
```
Emit as `<h2>`. Note: uses decimal numbers (0, 1, 2...) not Roman numerals.

### TIER headers
```
^TIER\s+(\d+):\s*(.*)$
```
Emit as `<h3>`.

### Sub-section headers (comprehensive list)
```
PHASE \d+, WEEK \d+, MINIMUM SPECS, WHAT YOU CAN RUN,
WHAT YOU CAN RUN ON APPLE SILICON, PROS, CONS, BEST FOR,
CURRENT LINEUP, HARDWARE OPTIONS, POPULAR CONFIGURATIONS,
WHAT IS IT, COST, PROVIDERS, SOVEREIGNTY LEVEL, QUICK START,
FEATURES YOU GET, ALTERNATIVE, KEY CAPABILITIES,
AGENT ARCHITECTURE PATTERN, EXAMPLE, CRITICAL, TOTAL, LAYER \d+
```
Emit as `<h4>`.

### Checkboxes
```
^\[( |x|X)\]\s+(.*)$
```
Render as `<ul class="checklist">` with `<span class="cb">☐</span>` or `<span class="cb">☑</span>`.

### TOC extraction
Look for the phrase "This blueprint covers EVERY path to sovereignty:" (or similar). Collect the `•` bullet items that follow it until a blank line or section header.

### Spec list lines
Lines like `CPU:    AMD Ryzen 5 7600X...` with pipe-separated values (`$200 | AM5 platform...`) are rendered as `<p class="spec"><strong>CPU:</strong> value</p>` — the label MUST be bold. Indented continuation lines (the next line with `$200 | ...`) become `<p class="spec-cont">` so they visually group with the spec label. This is CRITICAL — Vinny rejected the first PDF as "textual diarrhea" because spec lines were plain `<p>` tags with no bold labels.

## Script
`scripts/blueprint-to-html.py` — runnable parser for this format. Usage:
```
python3 scripts/blueprint-to-html.py <input.txt> <output.html>
```

## Page layout notes
- **PART 1 must start on page 2.** After the cover + TOC on page 1, add `style="page-break-before: always;"` to the `<h2>PART 1: ...</h2>` heading. Vinny explicitly specified that page 2 should begin with "PART 1: HARDWARE – THE COMPLETE OPTIONS MATRIX" followed by the intro paragraph and TIER 0.
- **RESOURCES & LINKS should be on its own page.** Add `style="page-break-before: always;"` to the `<h3>RESOURCES & LINKS</h3>` heading so the last page has substantial content (20+ lines) instead of just a footer.
