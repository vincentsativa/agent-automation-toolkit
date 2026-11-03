# Agent-Powered Research Tutorial, Format Variant

This reference documents the second distinct tutorial file format (June 2026), which differs from the Scrapling/Rotunda tutorial format.

## Source layout

```
══════════════════════════════════════════════════
AGENT-POWERED RESEARCH: FROM QUERY TO REPORT, HANDS-FREE
(Even If You've Never Used an AI Agent)
A Complete Beginner's Guide to AI Research Automation
══════════════════════════════════════════════════

Estimated Reading Time: 18 minutes
Word Count: ~3,400
Difficulty: Beginner (zero coding required)

══════════════════════════════════════════════════
TABLE OF CONTENTS
══════════════════════════════════════════════════

I.   The 3-Hour Problem vs. The 5-Minute Solution
II.  What Is an Agent, Really? (No Jargon, I Promise)
III. Choosing Your Agent: Three Honest Options
IV.  The Workflow: Query → Report (Step-by-Step)
V.   Real-World Use Cases (Copy-Paste Prompts Included)
VI.  Common Beginner Mistakes (And How to Avoid Them)
VII. The Real Unlock: Chaining Agents for Unfair Output Quality
VIII.The 5-Minute Habit: Start Today
IX.  Resources & Further Reading

══════════════════════════════════════════════════
I. THE 3-HOUR PROBLEM VS. THE 5-MINUTE SOLUTION
══════════════════════════════════════════════════

[paragraphs...]

═ third-level ===
═╤══════════════════════════════════════════════════════
STEP 1: CRAFT THE MISSION PROMPT (NOT A CHAT PROMPT)
───────────────────────────────────────────────────────

[content...]

USE CASE 1: THE FREELANCER
──────────────────────────

══ ABOUT THIS TUTORIAL ══
```

## Key differences from Scrapling format

| Feature | Scrapling format | Agent-Research format |
|---|---|---|
| Ruler chars | `===` (plain equals) | `═` (U+2550 box-drawing) |
| TOC landmark | `=== WHAT YOU WILL LEARN ===` or `=== WHAT YOU'RE GETTING ===` | `TABLE OF CONTENTS` between ruler lines |
| TOC items | Plain `- bullet` list | Roman-numeral lines (`I.`, `II.`, etc.) |
| Top-level sections | `PART ONE:` / `PART TWO:` | `I. THE 3-HOUR PROBLEM...` (Roman numeral + text) |
| Sub-section markers | `Example 1`, `TIER 1`, bold inline | `STEP 1:`, `USE CASE 1:`, `OPTION 1:`, `PICK THIS:`, `THE CHALLENGE`, `THE FINAL LINE`, `A HONEST NOTE` |
| Section dividers | `──────────────────` (solid line) | `══════════════` between major sections, `──────────────────` between sub-sections |
| Tutorial metadata | At very end after `ABOUT THIS TUTORIAL` | At very top (reading time, word count, difficulty) |
| Footer | Heavy ruler + END OF CHAPTER | About box with author/version/date/license |

## Parser modifications needed

### Ruler regex
Use `[═\u2550\-=\u2500]{3,}`, must include the box-drawing character U+2550.

### TOC extraction
Look for `TABLE OF CONTENTS` between ruler lines (not just `WHAT YOU WILL LEARN`). Extract Roman-numeral lines that follow. Render under cover with heading `IN THIS TUTORIAL`.

### Roman-numeral headers
Pattern: `^[IVXL]+\d*\.\s+.+`, detect lines like `I. THE 3-HOUR PROBLEM...`, strip the Roman numeral prefix + period, emit as `<h2>` with the full text including the numeral (e.g. "I. THE 3-HOUR PROBLEM VS. THE 5-MINUTE SOLUTION").

### Broader sub-section detection
Add to the `h4` detector regex:
- `STEP \d+:`
- `USE CASE \d+:`
- `OPTION \d+:`
- `PICK THIS`
- `THE CHALLENGE`
- `THE FINAL LINE`
- `A HONEST NOTE`
- `THE ONLY TOOL`
- `Recommended `
- `For the next`

### Inline formatting
Numbered TOC items, section intro text, and code-like inline items need `**bold**` and `*italic*` inline regex parsing. Apply after HTML escaping.

## Cover metadata
Place the metadata trio (reading time, word count, difficulty) in a single line under the cover gradient: `Estimated Reading Time: 18 minutes • Word Count: ~3,400 • Difficulty: Beginner (zero coding required)`