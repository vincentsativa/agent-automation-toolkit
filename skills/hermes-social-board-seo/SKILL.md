---
name: social-board-seo
description: Analyze social-media boards (Pinterest, Reddit, YouTube playlists, etc.), extract pinned content themes, do platform-native keyword research via search autocomplete, and craft SEO-optimized titles, descriptions, and hashtag strategies for better discovery and engagement.
toolsets: [browser]
---

# Social Board SEO Optimization

Analyze pinned/saved content on social platforms, research native search keywords, and rewrite board metadata for maximum discovery.

## Triggers

- User provides a Pinterest board URL and asks for title/description SEO optimization
- "optimize this board for search" / "better SEO for my board" / "new title and description"
- Any social platform where content is organized into boards, collections, or playlists with keyword-searchable metadata
- **Niche market research:** "Is [topic] a large niche on Pinterest?" / "Is [topic] growing?" / "Should I start a board about [topic]?", even without an existing board URL

## Workflow

### Phase 0, Niche Market Research (no board URL needed)

Use when the user asks whether a topic has size or growth potential on Pinterest, without providing an existing board.

1. **Live Pinterest Trends data**, Navigate to `https://trends.pinterest.com/` and check the "Trends in the Spotlight" section. These are Pin-save-based trends with month-over-month % growth and absolute date ranges. Note: Pinterest Trends focuses Pin-save growth, so low volume niches won't appear here, absence from this list ≠ no audience.

2. **Search result density**, Navigate to `https://www.pinterest.com/search/pins/?q=<topic>` and observe:
   - Whether results load immediately (high supply) or sparsely (underserved)
   - Pin descriptions and alt text in results, real users pinning this topic or just spam
   - Sponsored content volume, advertisers spend where there's demand

3. **Search autocomplete**, Type your topic into Pinterest search and read the dropdown suggestions. These are **real user search terms** with platform-validated volume. Long-tail suggestions (e.g. "AI tools for business" vs just "AI") indicate sustained search demand. Note: autocomplete for short queries like "AI" can get hijacked by homonyms ("airport", "air fryer"), use 2-3 word queries to disambiguate.

4. **Pinterest Trends search trends**, The overview page carries a public preview table of trending keywords with weekly, monthly and yearly change, sourced from Pin saves, which is a strong intent signal. Read it off the page with the browser and `document.body.innerText`; the page is client-rendered, so a plain fetch returns only the shell. The FULL keyword dashboard is gated: "View search trends" navigates to `/search/?country=US` and bounces to an unauth modal without a logged-in account. Do not try to route around it (`/search-trends/` is a 404 and a `?keyword=` parameter on the overview is ignored). When the gate is in the way, use the autocomplete and density checks in steps 2 and 3 and say plainly that the full dashboard needs a login.

5. **Pinterest Predicts**, Check `https://business.pinterest.com/pinterest-predicts/` for the annual forecast (80% historical accuracy). Look for tech/AI/themed trend names like "Glitchy Glam", "Vamp Romantic", or "Extra Celestial" that signal adjacent demand.

6. **Third-party data triangulation**, Use DuckDuckGo lite searches (`https://lite.duckduckgo.com/lite/?q=<topic>`) to find Pinterest statistics pages with:
   - Category rankings (home décor, fashion, food are largest, compare your niche against these)
   - Referral traffic breakdowns (e.g., "Programming and Developer Software = 25.3% of desktop referrals" means tech audiences are on Pinterest even if content volume is lower)
   - Demographic data (Gen Z = 42% of MAUs and growing fastest)
   - Revenue/ad metrics that suggest platform investment direction

7. **Synthesis**, Answer the user's question directly with:
   - **Size assessment:** How does this niche compare to top categories? (Small, medium, large, underserved)
   - **Growth signal:** What data supports growth (Pinterest Trends MoM%, Predicts inclusion, third-party stat, advertiser activity)?
   - **Recommendation:** Should they invest time creating content in this niche? What's the angle?

## Existing Board Workflow

### Phase 1, Board Content Audit

1. **Navigate to the board URL** via `browser_navigate`
2. **Load the full board** by scrolling down until no more pins load (typically 3-5 scrolls for 50-150 pins)
3. **Extract pin content via `browser_console`:**
```javascript
(()=>{
  const pins=[];
  document.querySelectorAll('div[data-test-id="pin"]').forEach(el=>{
    const t=el.textContent?.trim();
    if(t&&t.length>30) pins.push(t.substring(0,300));
  });
  document.querySelectorAll('[data-test-id="pin-card-image"]').forEach(el=>{
    const a=el.getAttribute('alt')?.trim();
    if(a&&a.length>20&&!a.startsWith('More about')) pins.push(a.substring(0,200));
  });
  return JSON.stringify({count:pins.length,pins:pins.slice(0,30)});
})()
```
4. **Parse for themes:** Categorize pins into topic buckets (e.g., AI news, agentic AI, local/self-hosted AI, AI security, AI ethics, emerging tech)
5. **Count total pins** and note recency of activity

### Phase 2, Platform-Native Keyword Research

1. **Navigate to the platform's search interface**
2. **Type the primary topic** into search and observe autocomplete suggestions, these are **real user search terms** with platform-validated volume
3. **Note high-value terms** from autocomplete:
   - Long-tail variants (e.g., "generative AI tools" not just "AI")
   - Adjacent terms (e.g., "robotics," "quantum computing" when searching "artificial intelligence")
   - Trending modifiers (e.g., "2025," "tutorial," "tools")
4. **Do NOT substitute external keyword tools.** Platform autocomplete is more accurate for Pinterest's algorithm than third-party SEO tools.

**⚠️ Short-query autocomplete trap:** Very short queries (2-3 letters) like "AI" get hijacked by common word matches ("airport", "air fryer", "air dry clay", "aizen"). This is Pinterest's algorithm prioritizing lexical prefix matches over semantic relevance. To get niche-specific autocomplete data for short names:
   - Use 2-3 word queries instead ("AI tools", "artificial intelligence", "AI art")
   - Each disambiguated query reveals a different facet of the niche
   - Cross-reference results across multiple query variants to build the full picture

### Phase 3, Title & Description Crafting

**Title rules:**
- **Front-load the highest-value keyword**, Pinterest crawls left-to-right; the first 3-4 words carry the most weight
- **Include a secondary keyword** separated by punctuation for breadth
- **Add an emoji** in the first half, Pinterest is visual; emojis boost CTR in home feeds
- **Target 80-95 characters**, Pinterest truncates after ~100 in feed view
- **Format:** `[Primary Keyword] & [Secondary Keyword] | [Niche Modifier] [emoji]`
- Example: `AI News & Agentic Tech Hub | Machine Learning, Generative AI & Future Technology 🚀`

**Description rules:**
- **First 50 characters must contain the primary keyword**, this is what Pinterest shows as the snippet
- **Keyword density:** Work 4-6 distinct high-value terms into natural sentences. Think "discover agentic AI breakthroughs, machine learning trends, generative AI tools..."
- **Length: ~450-500 characters**, enough for algorithm indexing, not so long it gets cut off
- **Include a clear value proposition**, "your ultimate hub for..." / "discover..." / "stay ahead with..."
- **End with 6-8 targeted hashtags**, mix broad (`#artificialintelligence`) and niche (`#agenticai`, `#localai`)
- **Do NOT stuff keywords unnaturally.** Sentences should read as human copy, not as a tag list.

### Phase 4, Delivery Format

Present to the user as:
1. **New Title** (with character count annotation)
2. **New Description** (with character count annotation)
3. **Rationale section**, explain why each keyword was chosen and where it appears in the text. Reference the search autocomplete data as evidence.
4. **Hashtag strategy**, which tags were chosen and why (broad vs. niche, trending vs. evergreen)

### Phase 5, Optional Implementation Instruction

If the user wants to apply it immediately:
1. Provide the exact title and description as copy-paste ready
2. Include hashtag list as a separate block for easy copying
3. Optionally suggest 1-2 board cover image prompts that align with the keyword themes

## Pitfalls

- **Console extraction returns empty on Pinterest**, shadow DOM and lazy loading mean `querySelector` often misses pin content. Always use `browser_snapshot(full=true)` as the primary extraction method, and only use console queries for timestamps or verification.
- **Boards with many pins need multiple scrolls**, 3 scrolls may only reveal 20 pins; scroll until "Loading Pins" indicator disappears or the same pins reappear.
- **Don't trust the board's current description for keyword cues**, existing descriptions are often written for humans, not algorithms. Base keywords on what people actually search for (autocomplete), not the current metadata.
- **Pinterest hashtags are indexed differently than Instagram**, hashtags on Pinterest act more like keyword tags than social discovery. Include them, but keep them relevant. Irrelevant hashtags hurt algorithm placement.
- **Avoid over-optimization:** Titles that are pure keyword salad get demoted. A title like "Artificial Intelligence Machine Learning Generative AI Agentic AI Deep Learning Quantum Computing Robotics AI Ethics Future Technology Emerging Tech" will be penalized.

## Related Files

- `references/pinterest-seo-quick-reference.md`, Platform-specific algorithm notes, character limits, and indexing behavior
- `references/pinterest-search-research-example.md`, Annotated walkthrough of a real board audit with search autocomplete capture
- `references/pinterest-niche-research-reference.md`, Key Pinterest statistics for niche sizing (MAUs, category rankings, referral traffic, demographics, shopping metrics); use instead of re-scraping third-party stats pages
