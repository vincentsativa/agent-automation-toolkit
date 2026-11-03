# Board Audit & Restructure Workflow (proven 2026-08-02 on PhantomByte)

Reusable procedure for turning a catch-all Pinterest board into a keyword-focused board
set. Use when handed a board URL and asked to audit/optimize it.

## Diagnose the catch-all board first
A catch-all board (multiple search intents in one title/description) ranks for NONE of
them. Pinterest associates a board with a coherent topic cluster; 5+ unrelated keyword
families in one board = diluted relevance everywhere.

Signs it's a catch-all:
- The board's own description lists 5+ unrelated keyword families (e.g. "agentic AI,
  machine learning, generative AI, AI security, local AI, robotics, quantum computing").
- Bucketing every pin into its search intent yields 4+ distinct buckets.

## Steps
1. **Bucket every pin by search intent** (AI news/agents, robotics/physical AI, AI
   hardware/business, AI tools, AI security/local AI, quantum/emerging tech).
2. **Scan for duplicate pins** — same pin text 2+ times in one board. Pinterest flags
   duplicates as spam and can temporarily block pin creation. Surface this as the
   FIRST action item (remove dup before any restructure).
3. **Restructure one-board-per-keyword**, with an ORDERED launch plan (Priority 1 first,
   1-2 boards at a time; never create all at once). Repurpose the original board as its
   namesake cluster only; MOVE pins out to their new homes.
4. **Validate demand on-platform:** `https://www.pinterest.com/search/pins/?q=<topic>`
   — dense + competitive results = huge validated demand. Capture autocomplete early;
   login/signup modals block further autocomplete after ~1 query.
5. **Deliverable format that works:**
   - Headline finding stated bluntly (the one-board problem)
   - Intent-bucket table (search intent vs what it is)
   - Ordered board restructure plan
   - Copy-paste-ready rewritten titles + descriptions per board (front-load keyword,
     focused cluster, no keyword salad)
   - Pin-level fixes (one keyword per pin, title front-load, first-50-char snippet,
     alt text, no dups, 2:3 ratio)
   - Step-by-step morning action plan
   - Email the full doc (email-sender skill) + one-line Telegram notification only
     (Vinny works from email, not chat pastes)

## Post-split: update the daily Pinterest cron to route posts to boards

After new keyword boards exist, the DAILY Pinterest cron prompt must be updated or every
generated pin still targets only the main hub. The proven cron prompt change (job
`9d9b840ce8e2`, "DAILY Pinterest Posts 5:45PM"):

- Replace the single-board URL at the top with ALL board URLs (main hub + each new board),
  so the agent checks what's already posted across all of them.
- Add an explicit routing rule: each of the 10 posts gets labeled `BOARD:` and is assigned
  to EXACTLY ONE board by topic.
- Routing default: **main board by default**; only route to a focused board when the
  story/article genuinely matches that one topic (e.g. an AI agents tutorial → AI Agents
  board, an AI tools guide → AI Tools board). Keep focused boards keyword-pure; don't turn
  them into mini catch-alls.
- Keep the rest of the cron intact (email the doc to hello@phantom-byte.com, Telegram note
  only, 10 posts ranked best-to-worst, no em dashes).

Same rule applies to Vinny's articles: main board by default; focused board only when the
article's topic clearly matches that one board.

## Worked example (PhantomByte AI board, 2026-08-02)
Board: "AI News | Machine Learning & Emerging Tech" (396 pins) — was 6 boards in one.

Keyword-validated board map (Priority order for PhantomByte funnel):
- P1: **AI Tools for Business** — "AI tools" / "AI tools for business" (massive demand,
  highest purchase intent; validated dense results wall)
- P1: **AI Agents** — "AI agents" / "AI agent" (Hermes/orchestration content lives here)
- P1: **Robotics & Physical AI** — "robotics" / "humanoid robots"
- P2: **AI for Developers** — "AI development" / "programming AI" (tutorials)
- P2: **AI Security** — "AI security" / "local AI Ollama"
- P2: **AI News** — "AI news" / "artificial intelligence" (time-sensitive news)
- P3: **Quantum Computing** — "quantum computer" (small niche, long tail)

Sample rewritten board metadata (copy-paste ready):

**AI Tools for Business:**
> Title: `AI Tools for Business & Productivity [2026]`
> Desc: "Discover the best AI tools for business, productivity, marketing, and work in
> 2026. From generative AI writing and design tools to automation, research, and SEO
> software, this board curates the top AI tools every entrepreneur, freelancer, and
> business owner should know. Save the tools that save you time and grow your business
> with artificial intelligence."

**AI Agents:**
> Title: `AI Agents & Automation [Guide]`
> Desc: "Everything about AI agents, agentic AI, and intelligent automation. Learn how
> autonomous AI agents work, explore agent frameworks and pipelines, and master building
> reliable AI agent systems. A practical guide for developers and builders creating the
> future of artificial intelligence with agents that actually deliver."

**Robotics & Physical AI:**
> Title: `Robotics & Physical AI [Humanoid Robots]`
> Desc: "The future of robotics and physical AI. Explore humanoid robots, real-time
> safety systems, robot automation, and how artificial intelligence is moving from
> software into the real world. For anyone following humanoid robotics, industrial
> automation, and AI hardware breakthroughs like NVIDIA's physical AI stack."
