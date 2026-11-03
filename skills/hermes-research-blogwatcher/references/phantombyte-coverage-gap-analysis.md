# PhantomByte Coverage-Gap Analysis for Editorial Briefs

Use this workflow when cross-referencing blogwatcher data against articles.phantom-byte.com to identify unwritten themes.

## Step-by-Step

1. **Navigate** to `https://articles.phantom-byte.com` in the browser. The front-page snapshot from `browser_navigate` is usually sufficient — it shows the last ~15 articles with titles and dates.

2. **Extract all recent article titles and dates** from the snapshot. Typical pattern: each `<article>` block contains an `<h3>` heading (the title), a date string (e.g. "June 8, 2026"), and the author name "Vinny Barreca".

3. **Categorize each existing article into a theme cluster.** PhantomByte categories observed:
   - Agent infrastructure / orchestration (e.g., "1,400-Line While Loop", "Aging Agent Problem")
   - AI security / attacker-LLM (e.g., "Autonomous Attacker", "Personality Jailbreak")
   - AI economics / business model (e.g., "$750 Copilot", "Wage Siphon")
   - Policy / geopolitics (e.g., "Geo-Blocking of Europe")
   - Model behavior / reasoning (e.g., "Calibration Tax", "93% Problem")
   - General industry / platform shifts (e.g., "Agent OS Wars", "Anthropic Paradox", "Prediction Reversal")
   - Privacy / detection / alignment (e.g., "Detection Delusion", "Total Recall")
   - Physical AI / robotics (e.g., factory automation, Prometheus "general engineer" — NO coverage as of June 2026)
   - Data center infrastructure siting / NIMBY / energy-water conflict (e.g., $130B blocked projects — NO coverage as of June 2026)
   - AI pricing / cost transparency / industry pricing wars (e.g., rate-limit banking, model throttling economics — "The $750 Copilot" is closest but covers one data point, not the systemic price war)

4. **Bucket today's headlines into the same categories.** For each candidate unwritten theme, identify which category it belongs to.

5. **Find the closest existing PhantomByte article** — scan for the most recent article in the same category. If a category has a very recent article (within 7 days), the new angle must be clearly distinct to justify writing again.

6. **Write the gap rationale** for each theme:
   > "The closest PhantomByte article is 'XYZ' (June N), which covers [specific angle]. The new angle is [different angle] — not a follow-up, but a [broader/narrower/different-dimension] take that hasn't been explored."

## Coverage Gap Analysis Template

For each of the 3 themes, include in the editorial brief:

```
Theme N: "PROVOCATIVE ARTICLE TITLE"

Angle: 3-4 sentence pitch.

Supporting sources:
- Headline (Source)
- Headline (Source)

Why it hasn't been covered: Cite closest existing PhantomByte article (title + date) and explain the difference.
```

## Pitfalls

- Do NOT re-read full article text unless you need its specific argument to compare against. The title and date alone is enough for gap analysis.
- If the front page only shows ~12 recent articles, that's enough data for gap identification. You don't need to paginate further.
- A theme is only "unwritten" if the angle is genuinely different from what exists. "Similar category but different specific story" is weak — the angle itself must be unique.
- Vinny writes daily. A category with no coverage in the last 14 days is a strong gap signal.
- If a category has 3+ articles in the last 7 days, that category is probably saturated — look for cross-category themes instead.