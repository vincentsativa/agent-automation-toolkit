# Data Corpus Evidence Method (Worked Example, Aug 1, 2026)

## Context

Task: "Generate 4 Tutorial Ideas from Data File" where the data file folder
is `C:\Users\<user>\OneDrive\Desktop\NEXT TUTORIALS TO WRITE\NEWEST TUTORIAL IDEAS`
containing 28 dated .txt files (July 5–31, 2026), each with prior tutorial
idea drafts generated from daily data drops.

The task required reading EVERY file, identifying recurring problems that
passed an evidence bar (2+ files OR 3+ mentions), and producing 4 ranked
tutorial ideas with source quotes.

## Method

### Step 1: Read all files programmatically

```python
import os
base = "/mnt/c/Users/<user>/OneDrive/Desktop/NEXT TUTORIALS TO WRITE/NEWEST TUTORIAL IDEAS"
files = sorted(os.listdir(base))
all_text = {}
for f in files:
    path = os.path.join(base, f)
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        all_text[f] = fh.read()
```

### Step 2: Define problem categories with keyword lists

```python
problems = {
    "agent_containment_sandbox_escape": [
        "sandbox", "containment", "escape", "rogue agent", "kill switch", ...
    ],
    "inference_cost_optimization": [
        "inference cost", "token cost", "cost crunch", "compression", ...
    ],
    # ... 13 total problem categories
}
```

### Step 3: Count file hits and total mentions per problem

For each problem category, iterate all files. If any keyword matches
(case-insensitive regex), mark the file as a hit. Sum total matches across
all files.

### Step 4: Apply evidence bar

A problem passes if:
- file_count >= 2 (appeared in at least 2 separate files), OR
- total_mentions >= 3 (mentioned at least 3 times across all files)

Discard everything below the bar.

### Step 5: Extract quotable evidence

Use `re.finditer(pattern, content, re.IGNORECASE)` with a context window
(e.g., `r'keyword.{0,200}'`) to pull specific quotes from each source file.
Record the filename and the quote text for each problem that passed the bar.

## Results (Aug 1, 2026)

| Problem Category | Files Hit | Mentions | Bar Passed |
|---|---|---|---|
| Beginner hardware/cost confusion | 28/28 | 201 | YES |
| Inference cost / model routing | 27/28 | 167 | YES |
| Model churn / model-agnostic | 27/28 | 91 | YES |
| Secrets leakage / supply chain | 27/28 | 147 | YES |
| Agent containment / sandbox escape | 22/28 | 296 | YES |
| Benchmark unreliability | 22/28 | 156 | YES |
| AI privacy erosion | 17/28 | 54 | YES |
| Agent safety / governance | 17/28 | 90 | YES |
| Agent memory architecture | 16/28 | 136 | YES |
| Chinese open-weight models | 15/28 | 127 | YES |
| Workforce displacement | 12/28 | 28 | YES |
| AI slop / code quality | 6/28 | 25 | YES |
| Zombie agent memory attack | 1/28 | 8 | NO (1 file) |

## Key Insights

- The top problem (agent containment, 22 files, 296 mentions) was driven
  by the OpenAI/Hugging Face breach story that dominated July data.
- "Beginner hardware confusion" hit all 28 files because the keyword set
  was broad (budget, local, run). Narrow the keywords if you need more
  precision.
- The zombie agent attack only appeared in 1 file and was correctly
  discarded despite 8 mentions in that file (failed the 2-file rule but
  passed the 3-mention rule, it was borderline and should be treated
  cautiously).
- Problems with high mention counts but low file counts may indicate a
  single-day story, not a recurring pain point. Weight file count over
  raw mention count when ranking.