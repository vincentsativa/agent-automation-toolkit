# Format G: Agent/Tutorial with markdown headers, CODE EXAMPLE fences, ballot-box items

Seventh tutorial format variant. Found in "Agent Containment Engineering" (`AGENT CONTAINMENT - $14.99 COMPLETE.txt`, a `.txt` inside a `- $29 TUTORIAL` folder). NOT handled by the existing parser scripts. Needs a custom parser.

## Document shape

1. **Cover block in body (MUST SKIP).** The source's first ~17 lines contain the SAME cover text the build script already generates: title, subtitle, "A PhantomByte Tutorial", the intro paragraph, `IN THIS TUTORIAL`, and the 7 TOC bullets, followed by a redundant full-title line, then `OVERVIEW`. If the parser runs over these, page 1 ends up with the cover content duplicated as plain body paragraphs AND 7 stray empty `•` list markers at the bottom of page 1. **Fix: cut `lines = lines[overview_idx:]`, find the line `OVERVIEW` and drop everything before it.** This is the single most important step for this format.

2. **Markdown-style headers** (not the ALL-CAPS / `===` / Roman-numeral styles of other formats):
   - `## N – Title`  -> `<h2>`  (regex: `^##\s+(\d+)\s*[–-]\s*(.+)$`)
   - `### N.N Title` -> `<h3>`  (regex: `^###\s+([0-9.]+)\s+(.+)$`)

3. **Fenced code blocks:** delimited by `--- CODE EXAMPLE: NAME ---` ... `---`. Toggle `in_code` on the opener line, capture the NAME (becomes an `<h4 class="codehead">` label), collect body until a line that is all dashes (`^-{3,}$`). 10 such blocks in this doc, including a large ASCII architecture diagram.

4. **Ballot-box items:** lines starting with `☐` (U+2610). These are bold quick-start headings and audit-checklist items. Emit `<p class="checkitem"><span class="box">☐</span> <strong>...</strong></p>`.

5. **Bullets:** `•` (U+2022) prefix. TOC bullets AND body bullets both use `•`.

6. **Italic footer:** last line `*PhantomByte – phantom-byte.com*` -> `<p class="footer">`.

7. **ALL-CAPS headers:** `OVERVIEW`, `ACTIONABLE TAKEAWAYS`, `THE QUICK-START – DO THIS FIRST` still use the plain ALL-CAPS rule; regex must include the en dash `–` in the allowed char set.

## Special chars present
- `–` en dash (U+2013), `•` bullet (U+2022), `☐` ballot box (U+2610).
- NO em dashes, NO `═` box-drawing rulers in this format.

## Null bytes in source
The `.txt` came from OneDrive and contained embedded NUL bytes (`file` reported "binary"). read_file refused it. Fix before parsing:
```bash
tr -d '\000' < "SRC.txt" > /tmp/clean.txt
```

## Verification false-positives (IMPORTANT)
- **`text-transform: uppercase` headings fool substring content checks.** `<h4 class="codehead">` labels are CSS-uppercased, so pymupdf extracts them as `CODE EXAMPLE: ACTION RATE LIMITER` (not the lowercase source text). A naive `'CODE EXAMPLE: Action Rate Limiter' in full_text` check reports "MISSING" even when content is present. Check code *content* (`class ActionLimiter`, `import boto3`, `AGENT PROCESS`) instead, or case-fold the search.
- **pypdf page-1 trailing `•` markers are an extraction artifact, not a bug.** pypdf `extract_text()` lists TOC list-marker glyphs at the end of the page even though they render inline. Don't chase them. Confirm real placement with pymupdf coordinate-aware extraction:
  ```python
  import fitz
  d = page.get_text('dict')
  for block in d['blocks']:
      for line in block.get('lines', []):
          for span in line.get('spans', []):
              if span['text'].strip() in ('•','☐'):
                  print(span['bbox'])
  ```
  Bullets at x≈60 aligned with list text = correct. Use pymupdf (`python3 -m pip install pymupdf`) for layout verification; pypdf for char counts / line counts.

## Known cover bug in the generated HTML (Aug 2026)
The build script that produces Format G's cover has a defect: it puts the real title into `<p class="cover-tag">` and the **subtitle + description joined into one run-on `<h1>`** via `<br>`:

```html
<p class="cover-tag">Agent Containment Engineering</p>
<h1>How to Sandbox, Monitor, and Stop Your Agent When It Goes Rogue<br>A technical containment playbook for developers running autonomous agents</h1>
```

User reported this as "you put the title and subtitle together making one run-on sentence." **Fix is a targeted edit to the existing HTML, not a parser rebuild:**
1. Split the `<h1>` down to just the title: `<h1>How to Sandbox, Monitor, and Stop Your Agent When It Goes Rogue</h1>`
2. Move the description into `<p class="cover-sub">...` with a terminal period: `<p class="cover-sub">A technical containment playbook for developers running autonomous agents. A PhantomByte Tutorial</p>`
3. Shrink the subtitle in CSS: `.cover-sub { font-size: 13pt ... }` → `10.5pt`, dim color to `rgba(255,255,255,0.75)`.
4. Re-render `weasyprint.HTML(existing.html).write_pdf(...)`.

Verify the split with pymupdf span extraction, the subtitle line should be a distinct span at the smaller size (11pt) below the 24pt title, not a 24pt continuation.

## Working parser
A complete working implementation is built from the shape above (custom `H2_RE`/`H3_RE`/`CODE_OPEN_RE`/`ALL_CAPS_RE` + ballot-box + bullet + cover-skip logic). Recreate it from the shape above rather than forcing `plain-text-to-html.py` or `build-agent-tutorial-to-html.py` onto it, both misclassify the `##`/`###` headers and the `☐` lines.
