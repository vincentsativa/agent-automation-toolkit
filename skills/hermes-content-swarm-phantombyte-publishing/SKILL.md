---
name: phantombyte-publishing
description: End-to-end PhantomByte content lifecycle — write educational content, publish to Gumroad, and optimize discovery via social and search. Five-phase workflow covering barrier articles/tutorials, Gumroad product setup, board SEO optimization for Pinterest/Reddit/YouTube, article keyword research, and Pinterest pin scheduling.
tags: []
related_skills: []
toolsets: [file, web, browser]
---

# PhantomByte Publishing — Create → Publish → Optimize

> Class-level umbrella covering the full PhantomByte content pipeline:
> **Phase A** — Write educational content (barrier articles, tutorials, challenge guides)
> **Phase B** — Publish to Gumroad as digital products
> **Phase C** — Optimize social board metadata for search discovery (Pinterest, Reddit, YouTube)
> **Phase D** — Article keyword research with Google Trends
> **Phase E** — Pinterest pin creation and scheduling for product launches
> Trigger: any task involving PhantomByte content creation, Gumroad publishing, board SEO, or Pinterest pin scheduling.

---

## Phase A: Content Writing (Educational Tutorials & Barrier Articles)

> Formerly: `phantombyte-content-writing`

Educational content production for articles.phantom-byte.com — barrier articles, tutorials, and challenge guides.

### Trigger Phrases
- "write me a free tutorial outline for [BARRIER X / topic]"
- "write the tutorial and email it to me"
- Any BARRIER #N assignment with a problem/solution brief attached

### Two-Stage Workflow

#### Stage 1: Outline

When Vinny provides a barrier/problem statement with solution framing:

1. **Write the outline** — full section-by-section breakdown with content notes under each heading. Map the complete article structure.
2. **Save to** `~/.hermes/workspace/` as a `.txt` file
3. **Email it** to hello@example.com via email-sender skill with a brief summary body
4. **Reply in Telegram** confirming it was sent and briefly summarizing the structure
5. **Stop.** Wait for him to say "write the tutorial."

#### Stage 2: Full Tutorial

When Vinny says "write the tutorial and email it to me" (or "write me this tutorial"):

1. **Load the outline** from `~/.hermes/workspace/` — it was already emailed so you may need to read it from disk
2. **Write the full tutorial** — every section from the outline, fully written, with:
   - Headlines that hook
   - Full paragraphs, not placeholder text
   - Real examples from Vinny's actual PhantomByte/Hermes/IronPulse workflows
   - Conversational, direct tone — Vinny's voice
   - Attribution footer: `*PhantomByte • phantom-byte.com*`
3. **Save to** `~/.hermes/workspace/[slug]-tutorial.txt`
4. **Email it** with a concise summary body
5. **Reply in Telegram** with word count and structure confirmation

### Tone & Style

- **Vinny's voice:** Direct, conversational, zero corporate language. He says "you're not stupid" not "users may experience confusion." He says "damn that was fast" not "I appreciate the efficiency."
- **No AI-isms:** No "leverage," "synergy," "delve," "dive deep," "furthermore," "it's worth noting," "in today's rapidly evolving landscape." Kill all of these.
- **Short paragraphs.** 1–4 sentences. Break often.
- **Address the actual barrier.** The emotional objection, not just the technical gap. Name the feeling ("you're staring at a blinking cursor"). Validate it. Then solve it.
- **Include real workflows.** Vinny's IronPulse, PhantomByte publishing, Hermes self-debugging — these are proof, not filler. Use them.
- **End with a one-sentence close** that lands the point.
- **Checklist/checkbox format** for challenge-based content. ☐ symbols for gamified completion.

### Content Structure Patterns

#### Barrier Articles (like Barrier 8, 10)
```
Title: "What IS [X]? A Guide for People Who [real human situation]"
Hook: Name the feeling. Validate it. Promise the fix.
Sections:
  1. The 30-second answer (don't bury the lede)
  2. Kill wrong mental models first (what it ISN'T)
  3. Analogy that sticks (smart intern, GPS, etc.)
  4. How it works (simple diagram or numbered breakdown)
  5. Before/after examples (concrete, real)
  6. Vinny's actual workflows (proof, not theory)
  7. Address emotional objections ("I'm not technical," "what if it messes up")
  8. Quick win (first action in less than 5 minutes)
  9. Escalation path (what comes next)
  10. One-sentence close
```

#### 30-Day Challenge Articles
```
Same structure as barrier articles PLUS:
- 4-phase overview table
- 30 daily tasks with checkboxes
- "Why this matters" and "What you just learned" for each day
- "What comes after Day 30" reflection section
- Share/journey close
```

### Delivery (Phase A)

- **Always email.** Vinny wants the content in his inbox, not spammed into Telegram.
- **Email body:** Brief summary of structure, word count, readiness status. The content is the attachment.
- **Telegram:** "Sent. ~X,000 words — [structure bullet]. In your inbox." Nothing more.
- **SMTP:** IONOS via email-sender skill (smtp.ionos.com:587, hello@example.com)
- **Subject format:** "Barrier X: [Title] — [Outline/Tutorial]" or "[Topic] — Full Tutorial"

### Speed Note

Vinny values speed. "Damn that was fast" is the target reaction. When he says "write the tutorial," write it immediately — don't ask questions, don't re-load the outline unless you need to, just produce. The outline did the structural thinking. The tutorial is execution.

---

## Phase B: Gumroad Digital Product Publishing

> Formerly: `gumroad-publisher`

Create and manage Gumroad digital products via the Gumroad API v2. Covers product creation, description/summary writing, pricing, slug setup, and content updates.

### Credentials

Stored in `~/.hermes/credentials.md`:
- **Account:** phantombyteai.gumroad.com
- **Access Token:** `_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE`
- **API Base:** `https://api.gumroad.com/v2/`

### Workflow

#### 1. READ THE SOURCE MATERIAL

Read the markdown or text file containing the tutorial content. Extract:
- **Title** from frontmatter `title:` field or first heading
- **Subtitle** from frontmatter `subtitle:` field
- **Price** from frontmatter `gumroad_price:` field — convert dollar amount to cents (e.g. `$0.99` → `99`)
- **Content** for writing description and summary

Source files live on Windows at paths like `/mnt~/OneDrive/Desktop/PI TUTORIAL/...`

#### 2. CRAFT DESCRIPTION AND SUMMARY

**Custom Summary** (short, 1-2 sentences, appears under the product name):
- Hook: the problem the user is paying to solve
- What they get: the solution in plain terms
- Outcome: what changes for them after reading
- Max ~300 characters

**Description** (full product page body text):
- Opening hook contrasting two scenarios (without / with the solution)
- "What You'll Learn" bullet list showing specific skills
- Honest framing — note trade-offs, not just benefits
- End with price and guarantee
- Use hyphens (`-`) NOT em dashes (`—`) — Vinny rejects em dashes

**Em dash rule:** BEFORE sending any text to the Gumroad API, replace ALL em dashes with hyphens:
```
text = text.replace('\u2014', '-')
```
This applies to BOTH `custom_summary` AND `description` fields. Do not substitute en dashes; use plain hyphens.

#### 3. CREATE THE PRODUCT (POST)

```bash
curl -s -X POST "https://api.gumroad.com/v2/products" \
  --data-urlencode "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  --data-urlencode "name=<product name>" \
  --data-urlencode "price=<price in cents>" \
  --data-urlencode "custom_summary=<short summary>" \
  --data-urlencode "description=<full description>"
```

Required fields: `name`, `price`, `custom_summary`, `description`
Optional: `customizable_price=false`, `max_purchase_count=1000`

**CRITICAL: Use `--data-urlencode` for ALL fields, not `-d`.** The `&` character in product names (e.g. "APIs & Databases") and HTML special characters in descriptions (`<`, `>`, `&`) will be silently truncated or corrupted by plain `-d` because the shell interprets `&` as a parameter separator. `--data-urlencode` properly encodes these characters. Do NOT submit `permalink` on POST — it is silently ignored (see Pitfall 7).

#### 4. SET THE PERMALINK (PUT — required after POST)

Gumroad's API silently ignores the `permalink` field on POST. The product is created with an auto-generated slug. To set your desired URL slug, make a separate PUT immediately after creation using the product ID from the POST response:

```bash
curl -s -X PUT "https://api.gumroad.com/v2/products/<PRODUCT_ID>" \
  --data-urlencode "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  --data-urlencode "custom_permalink=<desired-slug>"
```

After this call, `short_url` will update to `https://phantombyteai.gumroad.com/l/<desired-slug>`.

#### 5. UPDATE OTHER FIELDS (PUT)

```bash
curl -s -X PUT "https://api.gumroad.com/v2/products/<PRODUCT_ID>" \
  --data-urlencode "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  --data-urlencode "name=<new name>" \
  --data-urlencode "description=<updated description>"
```

Always use `--data-urlencode` for all fields. Plain `-d` will corrupt any `&` character in the value (common in product names like "APIs & Databases" or HTML descriptions).

#### 6. MESSAGE VINNY ON TELEGRAM

After creating the draft, send Vinny a message on Telegram with:
- Product name
- Price
- Draft URL (from API response `short_url`)
- Status: "Draft — ready for you to upload the PDF, images, and final check before publishing."

### Pitfalls (Phase B)

1. **Em dashes in description/summary** — Vinny will reject the product and ask you to remove them. Always strip `\u2014` → `-` BEFORE the API call. Do this programmatically, not by hand.
2. **API returns product ID** — save it from the response (field `id`). You need it for PUT updates. If you don't save it, query the product list to find it.
3. **Price in cents** — Gumroad API expects cents. `$0.99` = `99`. `$9.99` = `999`. Read from frontmatter `gumroad_price:` field, strip `$` and `.`, parse as integer.
4. **Newlines in description** — shell `curl -d` accepts literal newlines in the string. No `%0A` or URL encoding needed. Keep the shell quoting consistent.
5. **Product starts as unpublished draft** — Vinny uploads the PDF and images, then publishes manually. Do NOT publish via API.
6. **`max_purchase_count` field** — set to a reasonable cap like 1000 to prevent unlimited free/ultra-low price abuse when running a promotional price.
7. **`permalink` ignored on POST** — Gumroad's API silently drops the `permalink` field during product creation. The response comes back with `custom_permalink: null` and an auto-generated `short_url` like `https://phantombyteai.gumroad.com/l/wteqxi`. Always follow POST with a PUT to set `custom_permalink=<desired-slug>`. Verify `short_url` in the PUT response shows your slug.
8. **`&` in product names/descriptions corrupts plain `-d`** — The `&` character is a shell parameter separator. When using plain `-d "name=APIs & Databases"`, the shell interprets `& Databases"` as a background process command, and curl only receives `name=APIs `. Always use `--data-urlencode` for ALL fields, not `-d`. This applies to POST (create) AND PUT (update) calls. The `&` character appears in product names like "APIs & Databases" and in HTML descriptions containing `&nbsp;`, `&amp;`, etc.
9. **Description may be silently dropped on POST** — The Gumroad API may return `"description":null` in the POST response even when you sent a valid description. This is a known API behavior. Always verify the description field in the response, and if null, follow up with a PUT to set it. Use `--data-urlencode` for the PUT as well.

### Verification

- API returns `"success":true`
- Product has correct `name`, `price`, `short_url`, `permalink`
- `published: false` (must be draft, not live)
- No em dashes in any text field

---

## Phase C: Social Board SEO Optimization

> Formerly: `social-board-seo`

Analyze pinned/saved content on social platforms (Pinterest, Reddit, YouTube playlists), research native search keywords, and rewrite board metadata for maximum discovery.

### Triggers

- User provides a Pinterest board URL and asks for title/description SEO optimization
- "optimize this board for search" / "better SEO for my board" / "new title and description"
- Any social platform where content is organized into boards, collections, or playlists with keyword-searchable metadata
- **Niche market research:** "Is [topic] a large niche on Pinterest?" / "Is [topic] growing?" / "Should I start a board about [topic]?" — even without an existing board URL

### Phase C-0 — Niche Market Research (no board URL needed)

1. **Live Pinterest Trends data** — Navigate to `https://trends.pinterest.com/` and check the "Trends in the Spotlight" section. These are Pin-save-based trends with month-over-month % growth and absolute date ranges. Note: Pinterest Trends focuses Pin-save growth, so low volume niches won't appear here — absence from this list ≠ no audience.

2. **Search result density** — Navigate to `https://www.pinterest.com/search/pins/?q=<topic>` and observe:
   - Whether results load immediately (high supply) or sparsely (underserved)
   - Pin descriptions and alt text in results — real users pinning this topic or just spam
   - Sponsored content volume — advertisers spend where there's demand

3. **Search autocomplete** — Type your topic into Pinterest search and read the dropdown suggestions. These are **real user search terms** with platform-validated volume. Long-tail suggestions (e.g. "AI tools for business" vs just "AI") indicate sustained search demand. Note: autocomplete for short queries like "AI" can get hijacked by homonyms ("airport", "air fryer") — use 2-3 word queries to disambiguate.

4. **Pinterest Trends search trends** — From the Trends page, click "View search trends" to see the trending search keywords dashboard. Pinterest's search trends are sourced from Pin saves — a strong intent signal.

5. **Pinterest Predicts** — Check `https://business.pinterest.com/pinterest-predicts/` for the annual forecast (80% historical accuracy). Look for tech/AI/themed trend names.

6. **Third-party data triangulation** — Use DuckDuckGo lite searches (`https://lite.duckduckgo.com/lite/?q=<topic>`) to find Pinterest statistics pages with:
   - Category rankings (home décor, fashion, food are largest)
   - Referral traffic breakdowns (e.g., "Programming and Developer Software = 25.3% of desktop referrals")
   - Demographic data (Gen Z = 42% of MAUs and growing fastest)

7. **Synthesis** — Answer the user's question with size assessment, growth signal, and recommendation.

### Phase C-1 — Existing Board Content Audit

1. **Navigate to the board URL** via `browser_navigate`
2. **Load the full board** by scrolling until no more pins load (typically 3-5 scrolls for 50-150 pins)
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
4. **Parse for themes:** Categorize pins into topic buckets
5. **Count total pins** and note recency of activity

### Phase C-2 — Platform-Native Keyword Research

1. **Navigate to the platform's search interface**
2. **Type the primary topic** into search and observe autocomplete suggestions — these are **real user search terms** with platform-validated volume
3. **Note high-value terms** from autocomplete:
   - Long-tail variants (e.g., "generative AI tools" not just "AI")
   - Adjacent terms (e.g., "robotics," "quantum computing" when searching "artificial intelligence")
   - Trending modifiers (e.g., "2025," "tutorial," "tools")
4. **Do NOT substitute external keyword tools.** Platform autocomplete is more accurate for Pinterest's algorithm than third-party SEO tools.

**⚠️ Short-query autocomplete trap:** Very short queries (2-3 letters) like "AI" get hijacked by common word matches ("airport", "air fryer", "air dry clay", "aizen"). Use 2-3 word queries instead ("AI tools", "artificial intelligence") to disambiguate.

### Phase C-3 — Title & Description Crafting

**Title rules:**
- **Front-load the highest-value keyword** — Pinterest crawls left-to-right; the first 3-4 words carry the most weight
- **Include a secondary keyword** separated by punctuation for breadth
- **Target 50 characters max** — Pinterest enforces a 50-character limit on board titles, not 100. Confirm length before presenting.
- **Format:** `[Primary Keyword] | [Secondary Keyword]`
- Example that works under 50: `AI News | Machine Learning & Emerging Tech`

**Description rules:**
- **First 50 characters must contain the primary keyword** — this is what Pinterest shows as the snippet
- **Keyword density:** Work 4-6 distinct high-value terms into natural sentences
- **Length: ~450-500 characters** — enough for algorithm indexing, not so long it gets cut off
- **Include a clear value proposition** — "your ultimate hub for..." / "discover..." / "stay ahead with..."
- **End with 6-8 targeted hashtags** — mix broad (`#artificialintelligence`) and niche (`#agenticai`, `#localai`)
- **Do NOT stuff keywords unnaturally.** Sentences should read as human copy, not as a tag list.

### Phase C-4 — Delivery Format

Present as:
1. **New Title** (with character count annotation — must be under 50)
2. **New Description** (with character count annotation)
3. **Rationale section** — explain why each keyword was chosen, referencing autocomplete data
4. **Hashtag strategy** — which tags were chosen and why

### Phase C-5 — Optional Implementation

If the user wants to apply it immediately:
1. Provide the exact title and description as copy-paste ready
2. Include hashtag list as a separate block for easy copying
3. Optionally suggest 1-2 board cover image prompts aligned with the keyword themes

### Pitfalls (Phase C)

- **Console extraction returns empty on Pinterest** — shadow DOM and lazy loading mean `querySelector` often misses pin content. Always use `browser_snapshot(full=true)` as the primary extraction method.
- **Boards with many pins need multiple scrolls** — 3 scrolls may only reveal 20 pins; scroll until "Loading Pins" indicator disappears or the same pins reappear.
- **Don't trust the board's current description for keyword cues** — existing descriptions are often written for humans, not algorithms. Base keywords on what people actually search for.
- **Pinterest hashtags are indexed differently than Instagram** — hashtags on Pinterest act more like keyword tags than social discovery.
- **Avoid over-optimization:** Titles that are pure keyword salad get demoted.
- **Board title limit is 50 characters, not 100.** If you suggest an 80+ char title, the user will correct you. Keep it under 50 from the first pass.

---

## Phase D: Article Keyword Research & SEO Targeting

> General keyword research for PhantomByte articles using Google Trends. Covers term discovery, competitive landscape analysis, and keyword tier strategy. Trigger: "do keyword research" / "research keywords for this article" / "what keywords should I target."

### Methodology

#### 1. Extract Candidate Keywords from the Article

Read the source article and extract:
- **Core concepts** — the central topic and unique angle (e.g., "agent degradation," "AgingBench")
- **Coined terms** — any new phrase the article itself introduces (e.g., "agent lifespan engineering," "hallucinated dependencies," "shadow dependency") — these are zero-competition gems
- **Named entities** — papers, benchmarks, companies, tools mentioned (e.g., "AgingBench," "ITBench-AA," "GEM MemState," "Aikido Security")
- **Adjacent concepts** — broader categories the article touches (e.g., "AI agent security," "LLM reliability," "AI supply chain security")

#### 2. Batch Query Google Trends

Navigate to `https://trends.google.com/trends/explore` with terms in batches of 4-5:

```
https://trends.google.com/trends/explore?q=term1,term2,term3,term4,term5&geo=US
```

Rules:
- **Batch by theme** — group related terms together for meaningful comparison
- **Start with core concepts** — establish the baseline volume for your primary angle
- **Then test broader terms** — see what umbrellas have search volume
- **Then test coined/long-tail** — confirm they're genuinely zero-volume (first-mover territory)
- **Use US geo** unless the article targets a specific non-US audience
- **Past 12 months** for trend analysis

#### 3. Extract Volume Data

From the Trends chart snapshot, read the **"Average" row** in the chart table:
- **40+** = Very high volume (will be heavily contested by major publishers and vendors)
- **30-39** = High volume, medium-high competition
- **20-29** = Medium volume, growing space, good primary target
- **10-19** = Lower volume, low competition, decent secondary
- **1-9** = Very low volume, emerging space
- **0** = Zero volume (brand new term, no one searching yet = maximum first-mover opportunity)

Also note **trend direction** from the monthly rows:
- **Steady baseline** — consistent search demand, established topic
- **Rising trajectory** — growing interest, good time to enter
- **Spiky** — event/launch driven (e.g., product announcements)
- **Flat at 0** — term hasn't been discovered yet by searchers

#### 4. Assess Competition

Combine Trends volume with domain knowledge:
- **Very High (40+):** Major security/tech vendors (CrowdStrike, Snyk, Datadog) plus tech media (Wired, TechCrunch, Ars Technica) likely publishing. Need exceptional content + backlinks to rank.
- **Medium-High (30-39):** Some established players, but room for a well-crafted piece. Good for H1/umbrella.
- **Medium (20-29):** Growing space, few entrenched competitors. PRIME TARGET for PhantomByte's current authority.
- **Low (1-19):** Emerging or niche. Good for body content and long-tail traffic. Can rank quickly.
- **Zero:** First-mover terms. PhantomByte can own the SERP before anyone enters.

#### 5. Synthesize Three-Tier Strategy

**TIER 1 — PRIMARY TARGETS** (optimize title, H1, URL, first 100 words, meta description):
- 2-3 terms with good volume (20+) that PhantomByte can realistically rank for
- 1-2 zero-competition coined terms that define the article's unique value

**TIER 2 — SECONDARY** (H2s, body content, semantic SEO):
- 3-5 terms that strengthen topical authority
- Related concepts that search engines expect to see in a comprehensive piece

**TIER 3 — TERTIARY / FUTURE** (tags, image alt text, long-tail):
- Niche terms for specific audience segments
- Forward-looking terms that will grow over time

#### 6. Save & Deliver

- **Save full report** as `~/keyword_research_[slug].txt`
- **Email** to hello@example.com with the file attached
- **Email body** concise summary: primary targets, secondary targets, strategic notes (critical window, unique angle)
- **Telegram** confirm: "Sent. [N] terms across 3 tiers — [primary highlights]. In your inbox."

### Google Trends Batch Queries Reference

| Batch Focus | Example Query Pattern |
|---|---|
| Core concept + broad umbrella | `AI agent degradation,AI agent reliability,agent lifespan engineering` |
| Security angle | `AI supply chain security,shadow dependency,hallucinated dependencies` |
| Tool/product names | `Claude Code security,Cursor AI security,AI coding assistant vulnerability` |
| Benchmarks/academic | `AgingBench,ITBench-AA,LLM reliability` |
| Adjacent + long-tail | `agent memory degradation,AI agent monitoring,agent dependency hallucination` |

### Pitfalls

1. **Trends bot detection is common and persistent** — Google Trends aggressively blocks automated queries. When this happens:
   - `browser_navigate` loads the page frame but chart data is inaccessible via `browser_console` (shadow DOM / protected rendering).
   - `vision_analyze` may be unavailable depending on the active model's vision capabilities.
   - Direct Trends API endpoints (`/trends/api/explore`) are fragile and prone to format changes.
   - **Fallback chain:** When all extraction methods fail, pivot to estimated assessments based on DuckDuckGo search density signals, autocomplete analysis, and verified market knowledge from HN/Reddit research. Document the estimation basis transparently in the report. Partial research with honest estimation is better than no research.
   - If you do get a clean Trends page loaded, `browser_console` queries for chart table rows often return null. The chart data is rendered in a way that resists standard DOM scraping.
2. **Zero-volume terms are NOT useless** — they're often the most valuable for a new publication. A term with volume 0 today becomes volume 20 in 6 months if PhantomByte is the one who defined it.
3. **Don't chase highest-volume terms** — PhantomByte is an emerging publication. Winning a "40" is a resource gamble. Winning a "20" or a "0" is a smarter allocation.
4. **Trends averages are relative, not absolute** — a term scoring "20" has half the relative volume of a term scoring "40" in the same comparison. The scale is relative to the highest term in the batch, not absolute search volume.
5. **Overlapping terms skew comparisons** — if two terms in the same batch are nearly synonymous (e.g., "AI agent" and "AI agents"), their volumes cannibalize each other in the comparison chart. Keep batches thematically distinct.

---

## Phase F: Product Ideation from Catalog Gap Analysis

> Generate paid tutorial ideas by analyzing the existing Gumroad catalog, identifying coverage gaps, and mapping beginner vs. developer/engineer tiers.

### Trigger Phrases

- "find me [N] tutorial ideas" / "give me [N] tutorial ideas for [audience]" / "what tutorials should I create next"
- "look at all the tutorials I have on Gumroad" + "find me [N] ideas"
- Any request to brainstorm paid products based on an existing free catalog

### Inputs

1. **The existing Gumroad catalog** — list all products via the Gumroad API v2 GET endpoint
2. **The new/just-uploaded tutorial** — read the user's uploaded content from the cache directory at `~/.hermes/cache/documents/`
3. **User's audience split** — typically two tiers: beginners (non-technical, can type a sentence but don't code) and developers/engineers

### Workflow

#### Step 1: Catalog the Existing Products

```bash
curl -s "https://api.gumroad.com/v2/products" -G \
  -d "access_token=_XrppXV5YPWu7FeqrA2dMh-zQ39Qe6sO2-rrqEzX5BE" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(f'{p[\"name\"]} | {p.get(\"custom_summary\",\"\")[:200]}') for p in d.get('products',[])]"
```

Capture: name, price (all currently free), short_url, and custom_summary for each product.

#### Step 2: Analyze the New Tutorial

Read the uploaded tutorial document and understand:
- The barrier it addresses (e.g., "I don't even know what an AI agent IS")
- The mental model it installs
- Where it leaves the reader — what's the next question they'd ask?

#### Step 3: Identify the Gap

The 7 free tutorials answer: "What is an agent and how do I install it?"
The paid tutorials should answer: "What do I actually DO with this thing?"

**Gap categories to check:**
- **Automation** — recurring workflows (email, research, social media, scheduling) — missing from free catalog
- **Memory/persistence** — teaching the agent to remember the user — not covered in free catalog
- **Developer depth** — skills, multi-agent orchestration, observability, custom tools, security — none of the free tutorials target developers specifically
- **Integration** — connecting the agent to external systems (APIs, databases, SaaS) — gap

#### Step 4: Structure the Ideas

Each idea must include:
- **Title** — clear, benefit-forward
- **Who it's for** — specific audience description
- **What it covers** — 5-7 bullet points of curriculum
- **Why it's a $50 value** — concrete time/money savings the user gets (e.g., "replaces 10-15 hrs/week," "replaces a $500-2K/mo VA")
- **Price anchor:** $9.99

**Formula for each:** Follow the same pattern Vinny's successful tutorial uses:
1. Kill the wrong mental model first
2. Give a concrete analogy
3. Show the architecture (simple diagram)
4. Before/after comparison
5. Real workflow examples
6. Address the emotional objection
7. End with a concrete action

#### Step 5: Split by Audience Tier

**Beginner (5 ideas):** For people who can type a sentence but don't code. Focus on outcomes, not mechanics. Examples: research automation, email assistant, memory lab, social media automation, cron for normal people.

**Developer/Engineer (5 ideas):** For people who write code and ship. Focus on architecture, extensibility, production readiness. Examples: custom skills, multi-agent orchestration, observability, custom tool building, security hardening.

#### Step 6: Deliver

1. **Save to file** at `~/[slug]-tutorial-ideas.txt`
2. **Email** to hello@example.com via email-sender skill with the file attached
3. **Telegram brief** — confirm sent with a summary of the split (5 beginner + 5 developer) and a note that each is $9.99 priced at $50 value

### Pricing Logic

- Free tutorials = awareness and trust (lower the barrier to entry)
- Paid at $9.99 = price feels like theft when the value is 5x that (replaces 10-50 hrs/month of manual work)
- No middle tier — either free or aggressively affordable premium

---

## Phase E: Pinterest Pin Creation & Scheduling

Create and schedule Pinterest pins for PhantomByte products and content. Called after a product is live on Gumroad or an article is published.

### Triggers

- "Make a Pinterest pin for [product/article]" or any scheduling request mentioning Pinterest
- After publishing a new Gumroad product or article — this is the final social promotion step
- User sets a schedule time (typically 12:00 PM noon)

### Pin Content Assembly

Before logging into Pinterest, assemble the pin content from the product page or article:

**Title:** Product/tutorial name, concise — matches the Gumroad listing title structure. Pinterest truncates after ~100 chars in feed view so front-load key terms.

**Description:** 1-2 sentence hook that:
- States the problem being solved ("Stop getting blocked...")
- Names the key technologies (Scrapling, Rotunda, etc.)
- Includes price ("$4.99") or link call-to-action
- Max ~500 characters

**Image:** Download the product's preview image from the Gumroad page. The image URL is in the page's `browser_get_images` output. Download via `curl -o ~/<slug>-pin-image.jpg <image_url>`. Pinterest pins require a square or 2:3 aspect ratio image.

**Link:** The product's Gumroad URL (e.g., `https://phantombyteai.gumroad.com/l/<slug>`)

**Board:** "AI & Emerging Tech Hub" (PhantomByteAI account)

### Login

**Critical pitfall: Pinterest credentials are NOT stored in credentials.md.** The PhantomByteAI Pinterest account (`pinterest.com/PhantomByteAI/`) was created via Facebook login which is no longer supported. The available email/password combos (`user@example.com`, `hello@example.com`) do not work for Pinterest login. The user must provide the correct login credentials before pin creation can proceed.

When credentials ARE available:
1. Navigate to `https://www.pinterest.com/login/`
2. Type email into the Email field
3. Type password into the Password field
4. Click "Log in" button
5. Wait for redirect to Pinterest home feed

### Create the Pin

1. **Navigate to board:** After login, navigate to `https://www.pinterest.com/PhantomByteAI/ai-emerging-tech-hub/`
2. **Click the "+" or "Create" button** to open the pin creator
3. **Upload image** — click the image upload area and provide the file path to the downloaded product image
4. **Enter title** in the title field
5. **Enter description** in the description field
6. **Enter destination link** — the full Gumroad URL
7. **Select board** — "AI & Emerging Tech Hub" (should auto-select if creating from the board page)

### Schedule for Future Publication

Pinterest allows scheduling pins hours/days in advance:
1. In the pin creator, look for a publishing time option (clock icon, "Publish later" toggle, or scheduling dropdown)
2. Select "Schedule" / "Publish later"
3. Set the date and time to the user's specified time (e.g., today at 12:00 PM)
4. Confirm the scheduled time appears correctly

### Pitfalls

- **No stored credentials:** Pinterest credentials are not in credentials.md. The account was created via Facebook (now deprecated). If login fails, tell the user and request the credentials.
- **Facebook login deprecated:** Pinterest no longer supports Facebook-based login. If the account was created via Facebook, the user must have already set an email/password through Pinterest's "Update login method" flow.
- **Image aspect ratio:** Pinterest prefers vertical 2:3 images. The Gumroad product preview may be horizontal (16:9-ish). Attempt to use it as-is — Pinterest usually crops it. If the user wants a proper pin image, they'll need to create one.
- **Scheduling time:** When the user says "schedule for today at 12:00 PM," always convert to the user's timezone (likely Eastern). Pinterest's interface shows the local time of the account.
- **Bot detection:** Pinterest login may hit bot detection in headless browsers. If the login page keeps refreshing or credentials are rejected, note the limitation and report to the user rather than repeatedly retrying.
- **No API-based pin creation:** Pinterest's v5 API requires a business account with app approval for pin creation. Stick to browser-based workflow unless the user provides API tokens.

---

---

## Phase G: Social Media & X Post Writing

> Create short-form social content for PhantomByte — X/Twitter posts, Pinterest titles and descriptions, and social media engagement questions. Covers character limits, tone injection, platform-specific formatting, and the daily cron workflow for question generation.

### Triggers

- "Write me a [N]-character X post about [topic] with [tone/angle]"
- "Write me a Pinterest title and description for [content]"
- Any request to create social media copy for PhantomByte content
- The daily "SOCIAL MEDIA QUESTIONS - 5PM" cron job (produces engagement hooks, not posts)

### Social Media Questions (Engagement Hooks)

> Used by the daily "SOCIAL MEDIA QUESTIONS - 5PM" cron job. These are NOT posts — they are provocative questions designed to drive engagement and replies on X/Twitter.

**Structure of a good question:**
1. Lead with a specific, concrete fact or event (named company, number, product, study)
2. Expose the contradiction, irony, or uncomfortable truth
3. End with a question that forces the reader to take a side or think

**Character limit:** 190 characters maximum. Count programmatically before delivering.

**Tone:** PhantomByte voice — short, direct, skeptical edge. No em dashes. Concrete names and numbers.

**Cron prompt pattern (the "SOCIAL MEDIA QUESTIONS - 5PM" job):**
```
Go look at the following data files, THEN produce 10 sharp, provocative social media questions for PhantomByte. Each question must be a complete, publishable question in PhantomByte voice — short, direct, skeptical edge, concrete names and numbers, no em dashes. Each question must be 190 characters or fewer. These are engagement hooks: they should make the reader stop, think, and want to reply. Lead with a specific fact or event, then ask the question that exposes the contradiction or the uncomfortable truth. After writing all 10, verify every single one is under 190 chars by counting programmatically. If any are over, shorten them. Deliver the final verified set.
```

**Pitfalls:**
- Do NOT confuse questions with posts. The cron is named "SOCIAL MEDIA QUESTIONS - 5PM" — it produces questions, not ready-to-post content. Changing it to produce posts violates the user's intent.
- A vague prompt ("find me 10 great questions") produces weak output. The prompt must specify: lead with a concrete fact, expose a contradiction, under 190 chars, verify programmatically.
- Questions that are just "What do you think about X?" without a specific fact or angle are too weak. Every question must earn its place with a named entity and a specific claim.

### X/Twitter Posts

**Character limit:** 190 characters maximum. Count programmatically before delivering.

**Tone injection:** When the user specifies a tone or angle (e.g., "with the tone 'why are Americans trying so hard to destroy American AI companies?'" or "with the tone 'they should have been doing this the whole time'"), embed that angle as the framing device. The tone is not a separate sentence — it colors the whole post.

**Structure:**
1. Lead with the news or claim — specific, concrete, named entities
2. Deliver the angle or punchline in the second half
3. End with a question or challenge to drive engagement
4. Optionally annotate with character count in the header: `POST 1 (189 chars):` followed by the post text on the next line (Format A). The old format `POST 1: ...\n<text>\n(189 chars)` (Format B) also works. The verify script now handles both.

**Punctuation rules (absolute):**
- No em dashes (—) or double hyphens (--). Use commas, colons, or periods instead.
- This applies to ALL social posts, not just articles.

**Verification:** After writing, count characters with `len(text)` and confirm under 190. If over, trim without losing the angle.

### Pinterest Titles & Descriptions

**Title:** Concise, front-loaded with key terms. Matches the content being promoted.

**Description format:** Summary of the content followed by a question. The question engages the reader and invites a click.

Example:
```
Title: 42 State AGs Just Launched the Biggest Attack on OpenAI Yet
Description: Subpoenas targeting ads, data, minors, and model sycophancy right before the IPO. Why are Americans trying so hard to destroy American AI companies?
```

### Pitfalls

- **190 characters is tight** — every word must earn its place. Cut adjectives and adverbs first. Use contractions. Drop filler phrases like "just," "yet," "really."
- **Tone must be embedded, not stated** — don't write "The tone of this post is X." Write the post so the tone is obvious from the content.
- **Pinterest description is not an X post** — it's longer, more descriptive, and ends with a question. Don't apply the 190-char limit to Pinterest descriptions.
- **Em dashes in social posts** — the user will correct you. Always use commas or periods instead.
- **Character count markers are often wrong** — when you write a post and annotate it with `(N chars)`, the actual `len()` count frequently differs from what you claimed. Always verify programmatically before delivering. Run the verification script in `scripts/verify-social-posts.py` against the saved file to catch mismatches.
- **"Half a million" costs 15 characters; "500,000" costs 7** — when every character counts under 190, use numeric forms over spelled-out numbers. "500,000" saves 8 characters over "half a million" with no loss of meaning.
- **Post rewrites can silently push you over the limit** — every time you edit a post to fix one issue (tone, accuracy, style), re-check the character count. A single word swap can add 5-10 characters and push you over 190. Always re-verify after any edit.

---

## Phase H: Article-to-Video Pipeline (MoneyPrinterTurbo)

> Convert a written PhantomByte article into a narrated video with stock footage, TTS voiceover, subtitles, and background music.

### Trigger

- "turn this article into a video" — after writing an article, Vinny wants a companion video
- Any request to generate a video from article text

### Requirements

- MoneyPrinterTurbo installed at `~/MoneyPrinterTurbo/` (already set up)
- For stock footage: free Pexels API key in config.toml, or use local video files

### Workflow

1. Read the article text from the saved file
2. Run the CLI with `--video-script "$(cat article.txt)"` — this bypasses the LLM entirely and uses Vinny's text directly as the script
3. Output is a 1080x1920 portrait video with TTS narration, subtitles, stock footage, and background music
4. Deliver the output path to Vinny

### Reference

`references/moneyprinterturbo-video-pipeline.md` — full CLI reference, voice options, pitfall documentation, and config details.

### Pitfalls

- **Local video files must be in `~/MoneyPrinterTurbo/storage/local_videos/`** — the tool rejects files outside this directory as a security measure.
- **Pexels API key is needed for stock footage** — without it, use `--video-source local`.
- **No LLM cost** when `--video-script` is provided. Vinny's article text is the script.

---

## Reference Files

The following reference files provide detailed session-specific examples, statistical data, and fallback procedures:

- `references/pinterest-search-research-example.md` — Annotated walkthrough of a real board audit with search autocomplete capture and keyword selection logic table
- `references/keyword-research-example-aging-agent.md` — Keyword research report template with Google Trends methodology and three-tier strategy
- `references/pinterest-niche-research-reference.md` — Key Pinterest statistics for niche sizing (MAUs, category rankings, referral traffic, demographics, shopping metrics)
- `references/google-trends-fallback.md` — Step-by-step fallback chain when Google Trends blocks automated extraction: simpler queries, DuckDuckGo search density, autocomplete analysis, transparent estimation methodology, and cross-reference triangulation
- `references/gumroad-api-curl-patterns.md` — Verified curl commands for Gumroad API v2 product creation, permalink setting, description updates, and tag handling. Covers the `--data-urlencode` requirement, `&` character corruption, and the description-null-on-POST quirk.
- `references/coverage-gap-analysis.md` — Browser-based technique for extracting article titles from articles.phantom-byte.com, categorizing coverage by theme, and identifying gaps for new article recommendations. Used when TensorFeed report analysis requires PhantomByte coverage intelligence.
- `references/article-selection-workflow.md` — Full workflow for scanning the published catalog, evaluating outlines against timeliness/narrative-continuity/gap-coverage criteria, making the recommendation, and revising outlines with Vinny's recurring editorial additions (Dario fraud, real mechanism, regulations are silly, open source wins, capability-based targeting).
