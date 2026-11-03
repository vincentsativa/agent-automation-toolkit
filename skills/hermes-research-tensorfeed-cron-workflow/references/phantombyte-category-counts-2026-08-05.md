# PhantomByte Category Counts (as of August 5, 2026)

Scraped from https://articles.phantom-byte.com via curl + regex on `data-cat` attributes (cron-safe method).
Total cards: 153.

| Category | Count | Coverage Level |
|---|---|---|
| AI Infrastructure | 63 | Heavy |
| AI Engineering | 23 | Well covered |
| AI Security | 22 | Well covered |
| AI Industry | 16 | Covered |
| AI Agents | 6 | Covered |
| AI Policy | 6 | Covered |
| AI Research | 3 | Light |
| AI & Society | 2 | Light |
| AI Privacy | 2 | Light |
| AI & Investing | 1 | Sparse |
| AI Collaboration | 1 | Sparse |
| AI Ethics | 1 | Sparse |
| AI News | 1 | Sparse |
| AI Strategy | 1 | Sparse |
| Cloud Infrastructure | 1 | Sparse |
| Industry News | 1 | Sparse |
| Industry Report | 1 | Sparse |

(Scrape also surfaces two non-category artifacts, `'+c+'` and `all`, which should be ignored when summing.)

## Categories with ZERO articles (primary gap signal for article recommendations)

- AI Hardware / Chip Design
- AI Energy / Compute Efficiency
- AI in Healthcare / Clinical
- AI in Science / Research Methods
- AI in Finance
- AI in Education
- AI in Legal / Regulation
- AI in Gaming / Entertainment
- AI in Manufacturing
- AI in Agriculture
- Open Source AI
- Model Architecture / Training Methods

## Drift from July 30, 2026 reference

- Total cards: 145 -> 153 (+8)
- AI Infrastructure: 60 -> 63
- AI Security: 19 -> 22
- AI Engineering: 23 (unchanged)
- AI Industry: 16 (unchanged)
- AI Research / AI & Society / AI Privacy / AI & Investing: unchanged

Refresh periodically by re-running the curl + `data-cat` regex scrape (see SKILL.md PhantomByte Category Checking section).

## Usage note (Aug 5, 2026)

When ranking 5 article recommendations, the zero-article categories (AI Energy, AI Hardware, Model Architecture, Open Source AI) are the strongest gap targets. Cross-reference the current news themes against these gaps: e.g. the AI Energy theme mapped cleanly to the zero-article AI Energy gap and became the #1 pick on timeliness + gap size + actionability. Existing articles already cover GPU utilization, KV cache cost, GPU kernel writing, routers-as-moat, agent runtimes, agent containment, and safety-benchmark critique — avoid re-treading those exact angles when a paper/news story appears to overlap.
