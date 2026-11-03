# Mining an archive of idea reports

Use when one folder holds dozens or hundreds of generated reports and the ask is to pick the best few from all of them. The reports were written by different generations of the same generator, so the heading format drifts: `IDEA 1 (BEST) - PAID PRODUCT - $39`, `#1 - PAID PRODUCT ($34) - DEVELOPERS`, `#1. "Title"`, `TITLE:` on its own line, and bold variants. One regex matches one generation and silently loses the rest.

## 1. Walk the folder and filter by name

```python
files = sorted(glob.glob(os.path.join(D, "*.txt")))
files = [f for f in files if os.path.basename(f).startswith(("TutorialIdeas_", "daily tutorials", "Tutorial_"))]
```

Exclude the same folder's catalog snapshots and hand-written one-offs unless the user says otherwise. Read the two most recent reports in full first so the current format and the evidence language are fresh before parsing anything.

## 2. Extract with a ladder

Match headers, then fall back within the block:

```python
HDR = re.compile(r"^\s*(?:IDEA\s+#?\d+|#\d+)\s*(?:\(BEST\))?\s*[\.\-–:]?\s*(.*)$")
idx = [i for i, l in enumerate(lines) if HDR.match(l)]
```

Within each block, take the title from the first of:

1. `^\s*TITLE:\s*(.+)$` (may continue on the following line, so join while the next line is not a keyword such as `PRICE:`, `AUDIENCE:`, `LABEL:` and is not blank or a separator)
2. `^\s*Title:\s*["“]?(.+?)["”]?$`
3. the header remainder after stripping a leading `PAID PRODUCT ...` or `FREE ...` segment
4. the first non-separator, non-keyword line after the header, which covers formats that put the title on its own line in caps

Capture price from the header first, then any `$N` in the block; price is free when the label is free. Capture the evidence metadata with, in order:

```python
r"\((\d+) (?:separate |distinct )?files?,\s*(\d+)\+?\s*(?:references|mentions|sources)"
r"\((\d+) references?,\s*(\d+) files?\)"
r"evidence bar:\s*(\d+)\+?\s*sources? across (?:all )?(\d+) files"
r"(\d+)\+?\s*separate files"
```

Count bullet evidence lines as a floor (`^\s*[-•]\s*\w[\w\-\.]*\.(?:txt|md)`), because a block that lists five sourced quotes is better evidenced than one that claims numbers it does not show.

## 3. Gate on coverage

Print three numbers every run: blocks found, unique titles, distinct files that contributed at least one item. Compare the last one against the file count from the directory listing. Any file contributing zero is a missing format variant, not an empty report. A first pass that returns 21 items from 106 files is the failure mode this gate exists to catch.

## 4. Filter the junk before ranking

Drop a block when the extracted title is shorter than about 15 characters, has more than roughly 25 words, starts with `)` or `(`, or contains a rationale phrase such as `is the strongest because`, `beats #`, `is ranked last because`. Those are ranking summaries, not ideas, and they duplicate real items.

## 5. Deduplicate and score

Key on `re.sub(r"[^a-z0-9]", "", title.lower())[:60]`, keep the first occurrence, and append every date the key reappeared on. Then score on the four-part rule in SKILL.md when no numeric score exists, and keep the underlying counts so the report can show them rather than assert a rank.

## 6. What the ranking output has to contain

A reader should be able to start writing from the report alone: the angle as an argument, the quoted evidence with numbers, the deliverable list, the chapter outline, the nearest existing product and why this is not it, and the production estimate. State the closest miss and the reason it was dropped, because that is the line the user checks to decide whether the ranking was reasoned or arbitrary.
