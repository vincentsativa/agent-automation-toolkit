# Document Format Extraction and Generation

## Reading a document Vinny sends

`read_file` inlines `.docx`, `.pdf`, `.xlsx`, and `.pptx`. It does NOT inline `.odt` (OpenDocument). Do not ask him to paste the contents — extract it.

### .odt (OpenDocument Text)

An `.odt` is a ZIP. The text lives in `content.xml` with paragraph boundaries as tags, so strip tags after turning `</text:p>` and `</text:h>` into newlines:

```python
import zipfile, re, html

z = zipfile.ZipFile(odt_path)
xml = z.read('content.xml').decode('utf-8')
xml = re.sub(r'</text:(p|h)>', '\n', xml)     # paragraph and heading breaks
xml = re.sub(r'<text:tab/>', '\t', xml)
xml = re.sub(r'<text:line-break/>', '\n', xml)
xml = re.sub(r'<text:s[^>]*/>', ' ', xml)      # runs of spaces
xml = re.sub(r'<text:span[^>]*>', '', xml)
text = html.unescape(re.sub(r'<[^>]+>', '', xml))
text = re.sub(r'\n{3,}', '\n\n', text).strip()
print(text)
```

Run this through `execute_code` rather than a shell heredoc: the regex escaping survives, and the extracted text lands in context without a quoting fight. Preserve the original line structure — it is how you spot stray leading spaces and missing sections in the audit.

Inspect the archive contents first if the text comes back empty:

```python
print(zipfile.ZipFile(odt_path).namelist())
```

## Editing one string inside an existing .docx

Pick the method by scope. Restyling a document means rebuilding it with python-docx; changing one string means a byte-level edit of `word/document.xml` and nothing else. Do not reach for a layout library when one phrase changed — it is slower, it can fail on unrelated imports, and it re-lays-out text he did not ask you to touch.

`zipfile` from the standard library is enough, and it preserves every other part of the file byte for byte:

```python
import zipfile, os

src, out = '/path/source.docx', '/path/edited.docx'
OLD = 'the exact old phrase from the document'
NEW = 'the exact new phrase'

zin = zipfile.ZipFile(src, 'r')
zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == 'word/document.xml':
        n = data.count(OLD.encode('utf-8'))
        if n != 1:
            raise SystemExit('ABORT: expected 1 occurrence, found %d' % n)
        data = data.replace(OLD.encode('utf-8'), NEW.encode('utf-8'))
    zout.writestr(item, data)
zout.close(); zin.close()
```

Rules that make this safe:
- Search for the phrase inside a single `<w:t>` run, not across runs. Word can split one sentence into several runs mid-phrase, and a phrase that spans runs will return zero matches. Read the raw XML around the target first and copy the old string out of it rather than off the rendered page.
- Abort when the count is not exactly 1. Two occurrences means one of them is somewhere you did not look.
- Re-open the output and grep it for the OLD term and the NEW term. Zero hits for the old term, the new term present. Then read the paragraph list back and confirm nothing else moved.
- Keep `[Content_Types].xml` first in the archive. `infolist()` preserves the original order, so rewrite from `infolist()` and never from a hand-built name list.

### Do not use a docx library to inspect text either

`read_file` already inlines `.docx` as text, and `document.xml` is greppable straight out of the ZIP for a raw-string check. Importing python-docx to answer "what does this paragraph say" adds nothing.

## Generating a .docx from a plain-text draft

Write the draft as `.txt` first (single unwrapped line per body paragraph), verify it, then transform it into `.docx`. Do not hand-build the docx and the text separately — they drift.

Style map that produces a clean, ATS-parseable result: name bold ~17pt, title line bold ~11pt, contact line ~10pt, section headings bold ~11.5pt in a dark accent color with space before, `- ` lines converted to `List Bullet` paragraphs, everything else a normal 10.5pt Calibri paragraph with modest space after. Set margins to 0.6in top/bottom and 0.75in left/right.

### Interpreter trap on this machine

`python3` resolves to Hermes's bundled interpreter (3.14) while `pip install` writes to the user's 3.12 site-packages. `pip install python-docx` can report "Requirement already satisfied" and `python3 -c "import docx"` still fail with `ModuleNotFoundError`. Do not conclude the package is missing and do not reinstall in a loop.

Fix: run the docx script with the system interpreter and put the user site-packages on the path.

```python
import sys
sys.path.insert(0, '~/.local/lib/python3.12/site-packages')
from docx import Document
```

```bash
/usr/bin/python3 /path/to/make_docx.py
```

If the import still fails on `from lxml import etree`, do not reinstall lxml and do not loop on it: that path only matters when you are REBUILDING a document. For a one-string edit, drop python-docx entirely and use the `zipfile` recipe above.

### Verify the generated docx

Never claim the `.docx` is correct without reading it back. Print every paragraph with its style name and compare against the source text:

```python
from docx import Document
for p in Document(out_path).paragraphs:
    if p.text.strip():
        print(p.style.name, '|', p.text)
```

This catches the two silent failures: bullets that did not become list items, and a heading that absorbed the paragraph below it.
