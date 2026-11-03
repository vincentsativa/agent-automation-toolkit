# Diagnosing a Low Aggregate CTR in Search Console

When the site's overall Google Search Console CTR looks low (e.g. ~0.6%), do NOT jump to "rewrite all titles." Low aggregate CTR is usually an artifact of WHAT the site ranks for, not title quality. Diagnose before acting.

## Root cause

Search Console averages CTR across ALL impressions. When the impression base is dominated by brand queries and hyper-niche navigational blips (a few people searching an obscure tool name you wrote about once), the average drops even when every individual query's CTR is healthy. The denominator is the wrong kind of traffic.

## The diagnostic (before touching any titles)

1. Open **Search results → Performance → Queries** tab in Search Console.
2. **Sort by Impressions (high → low).** This comes FIRST. Anything under ~100 impressions over 90 days is noise, ignore it entirely. Its CTR is meaningless (a "20% CTR on 5 impressions" is a sample-size mirage).
3. Read position and CTR TOGETHER for the top high-impression queries:
   - **Brand/navigational query at position 1-3** (e.g. the site's own name): healthy CTR, but it is navigational, not money. Not a fixable lever.
   - **Real non-brand product/tool query at position 5-15 with real volume**: worth climbing. Holding page one on a genuine keyword on a new domain is a real trust signal, the template to replicate.
   - **High-volume informational keyword at position 1-5**: ONLY here is CTR/title the binding constraint.
4. If the top of the list is all brand + tiny navigational blips, the site has NO real content-keyword volume yet. That is a **ranking-volume problem, not a CTR problem.** The lever is climbing positions / compounding trust, not rewriting titles.

## Why this matters

On an early-days site averaging position 8-16, low CTR is expected (bottom of page one, plus AI Overviews absorbing informational demand). Recommending a title rework there mis-directs effort: the query base doesn't convert anyway, and titles only fire when real content keywords hold positions 1-5. The honest read is often simply "it's still climbing."

## Rules

- Never diagnose low CTR as a title problem without reading the Query composition first. Sort by impressions; drop sub-100-impression noise.
- A single low-impression query's high CTR proves nothing about titles. It is a sample-size mirage.
- In a saturated niche, the broad high-volume keywords stay locked by dominant authorities regardless of trust. The winnable ground is specific named-tool / named-product / named-incident queries where a trusted page can hold positions 1-3. Climbing 16→9 on one real product keyword is the template; plant many of those, not the generic keywords.
- A CTR-strong title is still worth generating for future articles (it costs nothing and compounds), but it is armor for pages that later hold position 1-5, not the current binding constraint.
