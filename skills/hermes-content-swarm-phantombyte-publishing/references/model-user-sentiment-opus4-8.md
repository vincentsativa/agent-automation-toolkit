# Claude Opus 4.8 — User Sentiment Reference (May 2026)

## Source
Collected May 29, 2026 from HN #48311647 (1730pts, 1346 comments), Ask HN #48316636, Andon Labs, Gertlabs, Marginlab, Simon Willison.

## Key Finding: Sharply Divided Consensus
There is NO unified take. Some users call it the best model in months. Others say it's unusable. The split correlates with task type.

## Research Method for Future Work
1. Find the main HN launch thread via Algolia: `/api/v1/search?query="Claude Opus 4.8"&tags=story`
2. Fetch comment sentiment via `delegate_task` to extract structured positives/negatives
3. Cross-reference with Andon Labs (Vending-Bench), Gertlabs (coding evals), Marginlab (SWE-Bench-Pro pre-release tracking)
4. Check for Ask HN threads ("Is X broken?") — these surface the strongest negativity

## Common Research Sources
- **Hacker News**: Algolia API with `tags=comment&numericFilters=points>0` for top comments
- **Simon Willison's blog**: "modest but tangible improvement" — good neutral baseline
- **Andon Labs**: Alignment + Vending-Bench evaluations
- **Gertlabs**: Independent coding benchmark evals
- **Marginlab**: SWE-Bench-Pro tracker (detected pre-release degradation)
- **Reddit**: r/ClaudeAI for community sentiment
- **lmsys Chatbot Arena**: ELO scores from human votes
