---
name: windows-tutorial-file-decoding
description: Decode Windows .txt files that read_file flags as binary.
---

# Windows Tutorial File Decoding

## When to use
- Vinny points you at a tutorial/source `.txt` file on the Windows Desktop (e.g. `/mnt/c/Users/<user>/OneDrive/Desktop/<TUTORIAL>/...`) and `read_file` returns `"Binary file - cannot display"` or garbled/mojibake text.
- Any PhantomByte/Gumroad task that starts from a Windows-authored tutorial file (publishing, ideation, content writing).
- Trigger symptom: `file_size` is non-zero but `content` comes back empty, or text is full of `\x00`/CJK-looking mojibake.

## The core rule
Do NOT give up on the source because `read_file` reports binary. These files are almost always valid UTF-8 with a misdetected header, not corrupt. Decode programmatically via python3 in the terminal.

## Decode procedure

```python
# run in terminal from the tutorial directory
data = open(path,'rb').read()
print('BOM:', data[:4].hex())          # 486f7720 = 'How ' = plain UTF-8
for enc in ['utf-8','utf-16','utf-16-le']:
    try:
        t = data.decode(enc); print('decoded as', enc, len(t)); break
    except Exception as e: print(enc,'failed',e)
# If the head is garbled but the tail is readable English, cut to the clean start:
idx = t.find('How to')                 # or first real title phrase
clean = t[idx:] if idx>=0 else t
open('/tmp/<name>_clean.txt','w').write(clean)
```

Notes:
- UTF-16LE decode often fails with "truncated data" at the tail — that does NOT mean the file is UTF-16. Fall through to UTF-8.
- Garbled head + readable tail (UTF-16 `\x00` runs / CJK mojibake in the first lines, clean English after) means a misdetected header. Slice from the first real English title phrase.
- After slicing, use `sed -n 'N,MP' /tmp/<name>_clean.txt` (NOT `read_file`, which still flags it binary) to page through the content.

## Extracting product fields
- **Title/name:** from the first real heading after the garble (matches the tutorial's own title).
- **Price:** Vinny gives it in the task (e.g. `$14.99`); convert to cents (`1499`) for Gumroad. Do not guess from the file.
- **Summary/description source:** pull hooks and section lists from the cleaned body.

## Pitfalls
- The `$` in folder names (`... - $14.99 TUTORIAL`) is shell-interpreted. Always single-quote the path in terminal commands, never double-quote.
- `read_file` will keep flagging these as binary even after you know they're UTF-8 — don't retry it; use sed/python on the decoded temp copy.
- If every encoding fails and there's genuinely no clean English run, report the blocker to Vinny rather than fabricating content from the garbled bytes.
