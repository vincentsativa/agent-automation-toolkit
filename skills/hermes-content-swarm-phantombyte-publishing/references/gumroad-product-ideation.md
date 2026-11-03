---
name: gumroad-product-ideation
description: Analyze a Gumroad product catalog, identify coverage gaps, research market demand, and generate new product ideas with pricing and positioning.
trigger: "user asks to analyze Gumroad tutorials/products, find gaps, generate product/tutorial ideas, or 'what should I make next' for their Gumroad store"
---

# Gumroad Product Ideation

## When to use
- Vinny asks to analyze his Gumroad catalog and suggest new tutorial/product ideas
- Vinny says "what should I make next" or "find gaps in my catalog"
- Any request to generate product concepts for his Gumroad store based on existing catalog + market research

## Vinny's Store
- Store URL: `https://phantombyteai.gumroad.com`
- Creator name: Vincent Sativa
- Brand: PhantomByte
- Typical pricing: $0.99–$4.99 for existing tutorials; $9.99 target for new premium tutorials

## Vinny's Product Formula
Every tutorial should follow this structure:
1. Kill the wrong mental model first
2. Give a concrete analogy
3. Show the architecture (simple diagram)
4. Before/after comparison
5. Real workflow examples from Vinny's actual use
6. Address the emotional objection ("I'm not technical enough" / "This will break")
7. End with a concrete action the user can take right now

## Workflow: Catalog Analysis → Gap Analysis → Market Research → Ideation

### Phase 1: Extract Existing Catalog
1. Navigate to `https://phantombyteai.gumroad.com` with browser
2. Use `browser_console` to extract product links:
   ```js
   Array.from(document.querySelectorAll('article a[href*="/l/"]')).map(a => ({title: a.textContent.trim(), url: a.href}))
   ```
3. For each product, curl the page and grep the meta description:
   ```bash
   curl -sL "<product_url>" | grep -oP '<meta name="description" content="\K[^"]+' | head -1
   ```
   Alternative: use `browser_navigate` + `browser_console` with `document.querySelector('article')?.innerText`

### Phase 2: Analyze Coverage and Identify Gaps
- Map each existing product to its category: setup, activation, coding, scraping, debugging, etc.
- Identify what's MISSING: daily workflows, specific automation recipes, power-user features
- The gap is usually between "how to install" and "what to actually DO with this daily"
- Beginners need: specific outcome-driven workflows (email, social media, research, scheduling, memory)
- Developers need: production-grade scaling, security, custom tools, observability, orchestration

### Phase 3: Market Research
- Hit HN Algolia API for real pain points:
  ```bash
  curl -sL "https://hn.algolia.com/api/v1/search?query=AI+agent+<topic>+problem&tags=story&hitsPerPage=10&numericFilters=created_at_i>1750000000"
  ```
- Check Reddit r/AI_Agents for beginner struggles and developer frustrations
- Look for YC-funded companies solving the same problem — validates market demand
- Identify what people are actually complaining about, not what you assume they want
- **Also check independent evaluators** — Andon Labs, Gertlabs, Marginlab, Simon Willison for model/tech-specific sentiment
- **Cross-reference with HN comments on launch threads** (use Algolia comment search with `tags=comment&numericFilters=points>0`) for real user praise/criticism
- **Model/product research tip:** The main HN launch thread often has 1000+ comments. Use `delegate_task` to have a sub-agent extract structured user sentiment (complaints vs praise) from it in parallel while you do other research.
- See `references/model-user-sentiment-opus4-8.md` for a worked example of this research pattern.

### Phase 4: Generate Product Ideas
For each idea, produce:
- **The Problem It Solves:** Real pain point backed by market research, not speculation
- **The Tutorial Covers:** Concrete, numbered list of what the buyer learns
- **The $50 Value:** Why $9.99 feels like theft — time saved, money saved, alternatives comparison
- **Target Buyer:** Specific persona (not "everyone")

Format: Two sections — Beginner (outcome-driven workflows) and Developer/Engineer (production-grade scaling)

### Product Positioning Philosophy (Vinny's Approach)
- **Small specialized models > one giant model.** Vinny's setup: Flash for 90% of work, Kimi for most of the rest, Pro and Gemma for edge cases. Position tutorials around this philosophy — teach users to match the tool to the task, not chase the biggest model.
- **"If I'm not building a rocket, I don't need superhuman intelligence."** The value proposition for $9.99 tutorials is efficiency and correctness, not bleeding-edge capability. Users need something that can "read right and follow directions."
- **Manual model control is a feature, not a limitation.** Vinny prefers choosing his own models. Auto-routing is for onboarding only — and should be educational, not opaque. Every routing decision should teach the user why that model was chosen so they can eventually graduate to manual control. This is a product angle: "auto-routing with transparency — train users to become power users."
- **Efficiency is the differentiator.** The market is bifurcating into "bigger models" vs "efficiency." Local inference, distillation, agentic patterns that do more with fewer tokens — that's the lane.
- **The cost-conscious user is Vinny's buyer.** He spent $3/week on Ollama Pro and had everything done. That's the demo — people who want maximum output per dollar, not unlimited spend on the frontier.

### Phase 5: Deliver
- Write to a `.txt` file with clear formatting
- Email to `hello@phantom-byte.com` using the `email-sender` skill (do NOT paste content into Telegram chat)
- Use subject line: "X Tutorial Ideas — $9.99 / $50 Value Each"

## Pitfalls
- Do NOT reuse old output from previous sessions — always do fresh browser extraction of the current catalog
- Do NOT skip market research — Vinny wants data-backed ideas, not guesses
- Do NOT price below $9.99 for new tutorial ideas — that's his target price point
- The existing catalog changes over time — always re-extract before analyzing
- Do NOT fabricate market data or HN comments — use real API results only
