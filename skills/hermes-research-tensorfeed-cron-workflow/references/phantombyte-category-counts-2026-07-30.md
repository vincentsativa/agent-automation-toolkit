# PhantomByte Category Counts (as of July 30, 2026)

Scraped from https://articles.phantom-byte.com sidebar. Total: 145 articles.

| Category | Count | Coverage Level |
|---|---|---|
| AI Infrastructure | 60 | Heavy |
| AI Engineering | 23 | Well covered |
| AI Security | 19 | Well covered |
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

## Categories with ZERO articles (gaps)

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

## How to refresh

Navigate to https://articles.phantom-byte.com and extract from the sidebar `<li>` elements. The site is a static site (no JS rendering), so `browser_snapshot(full=true)` returns immediately in cron mode. Look for lines like:

```
▸ AI Infrastructure 60
▸ AI Engineering 23
```

## Usage

Use this reference to identify coverage gaps when recommending article topics. The "Categories with ZERO articles" list is the primary gap signal. Cross-reference against current news themes to find the most timely gaps.
