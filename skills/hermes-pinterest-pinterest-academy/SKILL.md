---
name: pinterest-academy
description: "Use for Pinterest tasks and Pinterest cron jobs."
toolsets: [browser]
---

# Pinterest Academy Playbook (Official Pinterest Teaching)

This is the governing skill for ALL Pinterest work. Source: Pinterest's own official Creator Academy (create.pinterest.com) and Pinterest Business Help Center (help.pinterest.com). When Pinterest's official docs and any third-party advice conflict, Pinterest's word wins. Do not improvise SEO tactics that contradict these rules.

## Source Documents (pulled 2026-08-02)
- **Creator Academy Fundamentals** — https://create.pinterest.com/fundamentals/
- **Pin performance & distribution** — https://help.pinterest.com/en-gb/business/article/pin-performance-and-distribution

## The Core Truth (what the algorithm actually does)
- Pinterest distributes Pins to people based on **engagement** (search, save, click). As users search/save/engage, Pinterest learns what's relevant and shares more of it. Engagement preferences change over time.
- **There is NO set engagement window.** A Pin can gain traction hours, days, months, or YEARS after publishing. New Pins can blow up instantly, or old Pins can suddenly resurge. This is why Vinny's 7-year-old Pins still get views.
- Pins last forever. High-quality, relevant Pins resurface seasonally and compound long-term.

## Three Pillars (from Creator Academy Fundamentals)

### Pillar 1 — Make a Plan
- **Trend tools:** use Pinterest Trends + Pinterest Predicts to get ahead of what people search for.
- **Audience insights:** if any Pins/boards are published, review Pinterest Analytics BEFORE creating anything new. (Requires a free business account.)
- **Content calendar:** post a MIX of content types and cover key moments.
- **Content goals:** define a measurable objective for each Pin, and add a clear call to action (site link, affiliate link, or more).

### Pillar 2 — Create Impactful Content
- **Pin formats:** use a mix of image Pins, video Pins, and collages. Select the format that fits the idea.
- **Boards:** group Pins into well-structured, themed collections so people can discover and engage.
- **Creative best practices:** compelling, high-quality, mobile-friendly visuals. Most audience is mobile → use a vertical aspect ratio.
- **Shoppable/monetization:** affiliate links, product tags, product Pins to drive clicks to shop.

### Pillar 3 — Optimize for Success
- **Audit:** review Pins and boards at a regular cadence. Refresh standout content; update or remove low-performing/outdated assets.
- **Test:** run A/B tests on copy, visuals, formats. Apply learnings to future content.
- **Strategy tweaks:** revisit analytics; apply high-engagement themes and refined targeting to new content.
- **Repurpose:** refresh assets (resize, reformat, renew with design touches) to extend reach. Use automated cross-posting.

## Distribution Best Practices (from Pin performance & distribution)

### Troubleshoot a performance drop — check ALL of these first
1. **Include saved Pins:** tick "Include saved Pins" under Data in Analytics Overview to see all your stats (published + saved).
2. **Claim your website:** verify your domain. Without it, all content counts as "saved" and won't be highlighted in analytics. Also unlocks rich pins.
3. **Create your own Pins:** publish fresh original Pins, don't just save others' Pins.
4. **Quality Pins:** high-quality images/videos. Blurry or distorted = people can't see the idea. **Recommended aspect ratio: 2:3** for images and videos 15–60s long.
5. **Create regularly:** create Pins frequently and consistently. **Aim for original content weekly.** You can schedule Pins up to 2 weeks in advance.
6. **Avoid duplicate Pins:** do NOT repeatedly save the same Pin or re-upload content that already exists on Pinterest. This triggers **spam flagging and temporary Pin-creation blocks.** (This is the #1 way re-activated accounts get throttled.)

### Improve performance — creation
- **Create inspiring content:** solid lighting, great framing, high-res assets, stylized effects, and/or text overlay. Vertical aspect ratio (mobile audience).
- **Encourage saves:** include a call to action to save and follow. Saves/follows = more distribution.
- **Add context to Pins:** add title, description, link; strong video thumbnail; save to a RELEVANT board; tag relevant topics; list ingredients/instructions where applicable.
- **Use images AND videos:** review analytics, make more of what the audience saves/engages with most.
- **Match audience language:** Pins in the wrong language get less engagement.
- **Create trending content:** use Pinterest Trends, the search bar, and the creator hub for rising topics and seasonal changes.
- **Add a Save button** to the website so people can save directly from the site.
- **Create an ad** from a Pin to reach a wider targeted audience (awareness / clicks / sales).

### Improve performance — review & iterate
- **Review Pin stats** (individual) and **Analytics overview** (overall): saves, Pin clicks. Tick "Include saved Pins."
- **Audience Insights:** see which Pins/topics/formats resonate; produce more that encourages saves.
- **Conversion Insights:** see which Pins drive conversions; create more like those or promote them.
- **Optimize your content:** put relevant keywords in Pin title, Pin descriptions, board titles, board descriptions, and the website URL. Add topic tags when publishing NEW Pins.

## SEO Keyword Rules (what official docs state + operational practice)
Pinterest is a **search engine, not social media.** Treat every board and Pin like a Google landing page.
- **One board = one keyword/intent.** Don't mash topics into one board.
- **Board titles & descriptions carry keywords** and get indexed. Write board descriptions like SEO copy, not captions.
- **Pin title:** front-load the primary keyword; Pinterest reads left-to-right. Add a secondary keyword separated by punctuation.
- **Pin description:** primary keyword in the FIRST ~50 chars (the snippet shown in search); 4-6 distinct high-value terms in natural sentences; end with relevant hashtags. ~450-500 chars.
- **Alt text is indexed.** Put the keyword in the image alt text.
- **Hashtags are keyword tags, NOT social discovery** like Instagram. Keep them relevant — irrelevant hashtags hurt placement. Do NOT keyword-stuff hashtags.
- **Do NOT keyword-stuff** titles or descriptions. Pure keyword salad gets demoted. Human-readable copy that includes the keyword.
- **Optimize existing Pins:** keywords can be added to previously published Pins' titles/descriptions to revive them.

## Cadence Rules
- **3-5 fresh Pins/day** for an active account (matches Pinterest "create regularly" + avoids the spam flag from flooding).
- **Fresh original Pins, not repins** — repins don't move the algorithm the same way.
- **Consistency beats volume** — daily beats weekly bursts, always.
- **Never flood** a re-activated/dormant account with 10+ Pins/day; that trips spam filters (see duplicate/spam rule above).
- Use the 2-week scheduling window to batch-create and schedule ahead.
- **Index lag:** new pins can take time to get pushed; old pins keep paying out for years. Patience is the strategy.

## Pinterest Trends: what is reachable without a login

The page is client-rendered: a plain fetch returns HTTP 200 with only the shell text ("Pinterest Trends"), so a scraping tool reads as empty and looks like a block. Drive it with the browser and read `document.body.innerText`.

- **Public on `https://trends.pinterest.com/`:** Trends in the Spotlight (5 items with MoM % and category), the Moments calendar with Rising/Approaching labels, Shopping trends (top 10 categories by outbound-click change), a preview search-trends table with weekly/monthly/yearly change, and a region switcher across 25+ markets. That is enough to answer seasonal and category questions.
- **Gated: the full keyword dashboard.** The "View search trends" control goes to `/search/?country=US` and the app bounces to `?showUnauthModal=true` without a logged-in Pinterest account. Report the gate; do not guess routes (`/search-trends/` is a 404) and do not expect a URL shortcut (`?keyword=...` on the overview is ignored).
- **Keyword-level demand without a login:** use Pinterest search autocomplete plus result density, per `social-board-seo`. That is the working substitute, not a workaround on the trends page.

## Keyword research for one pin (tech and AI links)

When Vinny hands over a link and wants a title and description, demand data comes FIRST, before a word of copy is written. Procedure:

1. **Run the metrics endpoint on the candidate set**, in one call, before drafting: `python3 ~/.hermes/scripts/pinterest_trends.py --terms "<8-16 candidate phrases>"`. Use human search phrasing ("python", "developer", "programming"), never headline phrasing.
2. **Expect the AI vocabulary to be absent.** Pinterest has no measurable volume for "ai automation", "ai agents", "ai tools", "automation", "chatgpt", "workflow automation", "artificial intelligence". A missing term is a fact about demand, not a failed query, so re-running it or hunting another endpoint is wasted effort.
3. **Build the keyword set from what does measure.** The developer vocabulary carries the volume: `programming` (the one reliably RISING term), `python`, `developer`, `software engineer`, `computer science`, `terminal`, `github` (trending down, use as a secondary only). Measure again at post time rather than quoting this list from memory.
4. **Front-load the board's own keyword, then carry the measured terms.** The title leads with the subject the target board owns, and the secondary slots go to phrases that actually register volume. Never substitute a trending term for a term that describes the link; that trades placement for nothing.
5. **Say the absence out loud in the reply.** One line stating which candidate terms had no Pinterest volume, so Vinny sees the copy was built on data instead of vibes.

**Verify the copy mechanically before sending.** Print `len(title)` and `len(desc)` for the exact strings being delivered and show the counts: title 80-95 chars (hard limit 100), description 430-500 (hard limit 500), primary keyword inside the first 50 characters of the description. Drafting to a guessed length and handing it over unmeasured is how over-limit copy ships.

**A pin needs exactly one board answer, not a menu.** Pick the one live board whose owned keyword the pin targets, name it with its slug, and give one sentence of why. Naming two plausible boards and letting Vinny choose is a violation of the single-keyword rule, not helpfulness.

## Vinny's Account Context
- Old account, ~10M views/month ~7 years ago, abandoned, reactivated March 2026. Domain authority survived the dormancy (old Pins still get views). Treat as a reactivated account that must rebuild momentum steadily.
- Goal: funnel traffic to Sovereign AI Stack. Pinterest has real purchase-intent buyers and a decade-long content tail.
- The SEO changes locked in mid-August 2026 (pre-write dedup gate + per-post board assignment on the daily cron) are working. Keep them going. Consistency and correct board placement compound. Do not regress to flood-posting or unassigned pins.

## Live boards (SOURCE OF TRUTH — fetch, never guess)

**Account profile is `PhantomByteAI`** (NOT `phantombyte`, which is a different dormant account). Board slugs 404 on the wrong profile.

There are exactly SEVEN live boards holding pins. Any answer about "which board" comes from this list and nowhere else:

1. `ai-news-machine-learning-emerging-tech` → AI News | Machine Learning & Emerging Tech
2. `ai-agents-automation-guide` → AI Agents & Automation [Guide]
3. `ai-tools-for-business-productivity-2026` → AI Tools for Business & Productivity [2026]
4. `ai-for-developers-programming-ai-tutorials` → AI for Developers & Programming AI [Tutorials]
5. `agent-security-prompt-injection-sandboxing` → Agent Security: Prompt Injection & Sandboxing
6. `robotics-physical-ai-humanoid-robots` → Robotics & Physical AI [Humanoid Robots]
7. `quantum-computing-explained` → Quantum Computing [Explained]

**Refresh the live list in one command before answering any board question:**

```python
import urllib.request, re, html
UA = {"User-Agent": "Mozilla/5.0"}
PROFILE = "PhantomByteAI"
for slug in BOARDS:  # the seven slugs above
    url = f"https://www.pinterest.com/{PROFILE}/{slug}.rss"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "ignore")
    t = [html.unescape(x.strip()) for x in re.findall(r"<title>(.*?)</title>", body, re.S) if x.strip()]
    print(t[0], len(t) - 1)  # board title + pin count
```

A ready-to-run script already does this: `~/.hermes/scripts/pinterest_dedup.py` (no args = list every board and its pinned titles). Run it instead of hand-rolling.

**Never answer a Pinterest board question from memory or from a "planned boards" list.** If a board is not in the seven above, it does not exist yet. The earlier draft of this skill listed Agent Skills, AI Agent Skills, Skill Library, Skill Retrieval, Agent Harness, and Context Engineering as boards; NONE of those are live, and answering from that list produced a wrong board recommendation on ARTICLE 195. Delete that habit: fetch, then answer.

## Routing a pin to a board (single-keyword rule)

Route every pin to the live board whose topic it actually targets. Never invent a board and never route to a generic bucket:
- agent architecture, harnesses, orchestration, multi-agent → **AI Agents & Automation [Guide]**
- security, prompt injection, sandboxing, agent containment → **Agent Security: Prompt Injection & Sandboxing**
- tutorials, developer tooling, programming, model internals → **AI for Developers & Programming AI [Tutorials]**
- business, productivity, SaaS tools, platform moves → **AI Tools for Business & Productivity [2026]**
- robotics, humanoids, physical AI, chips-for-robots → **Robotics & Physical AI [Humanoid Robots]**
- quantum → **Quantum Computing [Explained]**
- general lab/frontier news with no agent or developer angle → **AI News | Machine Learning & Emerging Tech**

Do not create thin new boards. Only add one when volume can sustain 3-5 fresh pins per day across the set; start lean.
One board equals ONE keyword and ONE intent. This is the highest-leverage board setup. Do not blend topics into a single board and do not route a pin to a board whose keyword it does not target.

Rules for every board:
- **Board title = the exact keyword, front-loaded.** The primary keyword is the first words of the title. A fuller variant is allowed only if the keyword still leads and reads naturally (e.g. "Agent Skills for Engineers" still fronts "Agent Skills"). Do not title a board with a keyword it does not own.
- **Board description written like SEO copy** (per the SEO Keyword Rules above), not a caption: primary keyword, 4-6 high-value terms, value proposition, hashtags.
- **Route every pin to the board whose keyword it targets.** If a pin targets a term not owned by a board, either create a board for it or route to the closest keyword-matching board. Never dump onto a generic board.
- **Do not create thin boards that starve pin volume.** Only add a board when you can sustain 3-5 fresh pins per day across the set. Too many low-activity boards looks dormant. Start lean, add boards as volume supports them.

Established live boards: see the **Live boards (SOURCE OF TRUTH)** section above. That list of seven is the only one. Do not maintain a separate "planned" list here; a board that is not one of the seven live boards does not exist.

## Reading a Pinterest analytics export (audit, then CHANGE the cron)

**An analytics question from Vinny is an instruction to change the cron, not a request for a report.** Do the audit, then apply the change to the job in the same turn and verify it landed. Never end with "want me to apply it?" and never hand back a list of recommendations as the deliverable.

Audit order, and the mechanics for each step are in `references/analytics-audit.md`:

1. **Weekly impressions buckets first.** Day-level numbers swing; four weekly sums show whether reach is rising or decaying. Exclude any day the export footer flags as an estimate before quoting a spike.
2. **Per-board RATES, not totals.** Divide engagement, Pin clicks, and Saves by each board's own impressions. The board carrying the most impressions is often not the board with the best rate.
3. **Outbound clicks ÷ Pin clicks.** That ratio is the only number that says whether traffic actually leaves Pinterest. Saves and engagement feed distribution but do not move a visitor to the site.
4. **The Canonical column is the claimed-domain flag.** A pin row reads Yes only when its destination domain is claimed by the account.
5. **A pin's destination URL is not in the export.** Read it off the pin page's embedded JSON (`"link"`, `"domain"`, `"linkDomain"`), never off the analytics table.
6. **Measure what the cron actually shipped before changing it.** Count over-limit titles and descriptions across the recent posts files by date, not by eyeballing one file (snippet in the reference).

## Pinterest Trends check: the mandatory step in the daily cron

The Pinterest Posts cron must check live Pinterest trend data every run and let it steer story choice and keywords. Trend data lives at trends.pinterest.com.

**Access facts (verified live, Nov 2 2026):**
- The trends page is client-rendered, so scrapling returns only the title "Pinterest Trends". Do not conclude the site is blocked.
- The keyword search-trends dashboard (`/search/`) requires a logged-in account and bounces to an unauth modal. Never rely on it in a cron.
- The public JSON endpoints work with plain HTTP, no login and no cookies: `/latest_available_date/`, `/top_trends_filtered/`, `/metrics/`. `/resource/ApiResource/` paths (featured topics, moments) return 403 without a CSRF token, so do not use them.
- `/metrics/?terms=a,b,c&country=US&end_date=<latest>&days=90&aggregation=2&normalize_against_group=false&predicted_days=0` returns a weekly count series plus WoW/MoM/YoY growth **only for terms Pinterest has measurable volume for**. A term that comes back missing has no demand signal; it is not an error.
- `/top_trends_filtered/?lookbackWindow=2&endDate=<latest>&rankingMethod=3&country=US&trendsPreset=N&numTermsToReturn=20` where preset 1 = seasonal/upcoming, 2 = popular evergreen, 3 = breakout (fastest growing), 4 = full trending-searches list.
- Term volume from the lists is not comparable to the metrics counts; they use different normalization. Use lists for shape and seasonality, metrics for demand per term.

**The script:** `python3 ~/.hermes/scripts/pinterest_trends.py` prints the latest data date, the four trend lists, and (with `--terms "a,b,c"`) a demand line per term with direction. Use `--terms-file` for long lists. It exits 2 on fetch failure.

**Matching trend to story: three legitimate uses, nothing else:**
1. **Story choice:** between similarly strong stories, prefer the one whose search phrase has measurable volume, and prefer RISING over FLAT over FALLING.
2. **Keyword placement:** put the reported phrase in the title and in the first ~50 characters of the description.
3. **Seasonal angle:** use a SEASONAL or BREAKOUT term only when it honestly describes the story's own subject.

**Forbidden:** stating a trend percentage in a post, writing that anything is "trending on Pinterest", bolting a seasonal term onto an unrelated story, inventing a trend, or claiming the check ran when it did not. Candidate phrases must be human search phrasing ("humanoid robot"), never headline phrasing.

## The daily Pinterest Posts cron — gates are hard, never escapable

- **Title 100 chars, description 500 chars.** Over-limit text is silently truncated in the feed, so an over-limit post is a broken post. Any prompt wording that permits the email to go out carrying an over-limit post is a defect and gets deleted.
- **Cap loops, never gates.** Wording like "verify once, then proceed regardless", "send it anyway even if a post is over the limit", or "at most 2 execute_code calls" is an escape hatch, and the run takes it. Phrase the check as: rewrite the offending post SHORT from scratch, re-run the check, repeat until it reports zero violations.
- **Rewrite, do not trim.** Trimming an over-limit description degrades the prose and burns iterations. Write a fresh 380 to 420 char description for that post.
- **The board separator in the delivered file is a hyphen, never an em dash** ("[BOARD NAME] - Post title").
- **Board names inside a cron prompt are a claim, not the source of truth.** Verify them against the seven live board titles before trusting a job to route pins. Shorthand names ("Main AI News", "AI Tools") drift from the real titles and will route to boards that do not exist.
- **Read the job's real prompt before saying what the cron does.** A question like "does the cron check trends?" is answered from the `prompt` field in `~/.hermes/cron/jobs.json`, never from this skill, the job's name, or the script it runs. This skill states the policy; the prompt is what actually executes. See `hermes-cron-troubleshooting` for the read.
- **Changing the prompt is `hermes cron edit <job_id> --prompt "$(cat <file>)"`, then read the job back and assert exactly one job record changed.** See `hermes-cron-troubleshooting` for the backup and blast-radius proof.

## Enforcement
For ANY Pinterest task (audit, keyword research, board setup, pin copy, cron jobs), follow THIS skill's rules before acting. If a task needs live Pinterest data (trends, autocomplete, board audit), use the `social-board-seo` skill for the research mechanics, but keep THIS playbook as the governing ruleset. Never contradict Pinterest's official rules.
