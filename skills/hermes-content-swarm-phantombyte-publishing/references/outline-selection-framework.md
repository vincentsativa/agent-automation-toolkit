# Outline Selection Framework — Which Article to Publish Next

A structured decision framework for choosing between multiple article outlines when Vinny asks "which should I write next?" Used when he provides 3-4 outlines and wants a recommendation grounded in site data.

## Decision Criteria (in priority order)

### 1. Timeliness / News Hook

The strongest article is the one that connects to the most urgent, breaking story. Check:
- What broke in the last 48 hours that the outline references?
- Is there a specific event (model release, paper, departure, IPO) that gives the article a "right now" hook?
- Does the outline reference a story that's still developing (high) or already played out (low)?

### 2. Site Coverage Gap

Check the category counts on articles.phantom-byte.com. The best next article:
- Strengthens a thin but strategically important category (e.g., AI Agents at 4 articles)
- OR deepens the strongest category (AI Infrastructure at 54) with a genuinely new angle
- Does NOT overlap with the most recent article's territory

### 3. Redundancy with Recent Articles

Check the latest 3-5 published articles. If an outline shares data sources, framing, or thesis with a very recent piece, it's a rehash. The reader just read that story.

### 4. Narrative Arc / Serial Continuity

PhantomByte is a daily serial. The best article:
- References and builds on previous Notes (interconnected brand authority)
- Completes a trilogy or extends a thread (e.g., models degrade → models get replaced → models train themselves)
- Rewards regular readers who follow the thread

### 5. Engineering & Architecture Focus

Vinny's positioning: "you can't do shit without engineering." Prefer outlines whose teaching goal is a concrete infrastructure framework over policy commentary or industry analysis.

## How to Discover Site State

From the homepage, run in browser console:

```javascript
// Get all article links with their categories
Array.from(document.querySelectorAll('article')).map(a => {
  const h3 = a.querySelector('h3');
  const cat = a.querySelector('[class*="category"], [class*="tag"]');
  return { title: h3?.textContent?.trim(), category: cat?.textContent?.trim() };
})
```

For category counts, click each category link in the sidebar and read the count from the snapshot.

## Example Application (July 11, 2026)

Four outlines evaluated:

| Criterion | Outline #1 (Inference Bill) | Outline #2 (Recursive Self-Improvement) | Outline #3 (Proactive Agents) | Outline #4 (Safety Exodus) |
|---|---|---|---|---|
| Timeliness | Medium — same data as today's article | HIGH — Sol/Luna broke July 10 | Medium — Context Graphs paper | Medium — departures are a pattern, not a single event |
| Site gap | Redundant with latest | Deepens Infrastructure (53) with new angle | Strengthens thin Agents (4) | Policy (6) is thin but not engineering |
| Redundancy | HIGH — same SK Hynix/Micron data as July 11 | LOW — completely new territory | LOW — Agents only has 4 articles | LOW — Policy only has 6 |
| Narrative arc | Standalone | Completes degradation → churn → self-improvement trilogy | Standalone | Standalone |
| Engineering focus | Medium — cost analysis | HIGH — infrastructure framework | HIGH — architecture pattern | LOW — incentive structures |

**Result:** Outline #2 wins on timeliness, narrative arc, and engineering focus with zero redundancy.
