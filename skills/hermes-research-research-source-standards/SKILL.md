---
name: research-source-standards
description: Source quality rules for research, no Wikipedia, no propaganda outlets, prefer primary verifiable sources, vet before citing
category: research
---

# Research Source Standards

## When to Use
- Any task involving research, fact-finding, citations, or external information
- User asks "is this true", "find data on X", "what's the latest on Y"
- User references a model release, company news, or product announcement
- Any web search or browser-based fact gathering

## Hard Rules

### 0. RSS-First Research Methodology (CRITICAL)

**RSS/Atom feeds are the PRIMARY data source for any research task. Browser scraping is the LAST resort.**

**Why:** RSS feeds are structured XML/JSON, don't trigger bot blocking or CAPTCHAs, return headlines/dates/links in a single curl call per source, and don't suffer from stale 404 URLs. Browser scraping is fragile, sites block bots, snapshots truncate, console queries return empty, article URLs rot. RSS sidesteps all of this.

**The rule:**
1. Before any `browser_navigate` or `web_search` for research, ALWAYS check for an RSS/Atom feed first.
2. Fetch feeds via `curl -sL <feed_url>`, one call per source gets you 20+ stories.
3. Parse the feed XML/JSON for headlines, publish dates, article links, and descriptions.
4. Only fall back to browser_navigate when a source has no RSS feed or the feed is empty/stale.
5. "The good data has RSS", if a source doesn't publish an RSS feed, it's usually not worth scraping anyway.

**Breaking news exception:** For stories that broke within the last hour, use browser_navigate first. RSS feeds have 15-60 minute refresh cycles and won't have ultra-fresh stories yet. The browser catches what RSS misses on the bleeding edge. This is the one case where browser takes priority over RSS.

**Agent role distinction:** Bill (Linux cron) = autonomous pipeline. Scheduled batch research, RSS-first at scale. WSL/Frank = interactive right hand. Development, writing, technical work. Windows agent = social media, random life things. The RSS-first rule applies most strictly to Bill's autonomous runs. For interactive sessions (WSL/Windows), use judgment, RSS for routine gathering, browser for breaking news or when the user asks about something live.

**RSS feed discovery pattern:**
```bash
# Common RSS feed locations to try:
curl -sL "https://example.com/feed/"
curl -sL "https://example.com/feed.xml"
curl -sL "https://example.com/rss/"
curl -sL "https://example.com/rss.xml"
curl -sL "https://example.com/atom.xml"
curl -sL "https://example.com/feed/rss/"

# JSON Feed format:
curl -sL "https://example.com/feed.json"

# Check page HTML for feed links:
curl -sL "https://example.com" | grep -oP 'type="application/rss\+xml"[^>]*href="([^"]+)"' | sed 's/.*href="//;s/".*//'
```

**Extraction technique (single curl per source):**
```bash
# RSS XML, extract headlines
curl -sL "https://example.com/feed/" | grep -oP '<title>[^<]*</title>' | sed 's/<[^>]*>//g' | head -20

# Get publish dates
curl -sL "https://example.com/feed/" | grep -oP '<pubDate>[^<]*</pubDate>' | sed 's/<[^>]*>//g' | head -20

# Get article links
curl -sL "https://example.com/feed/" | grep -oP '<link>[^<]*</link>' | sed 's/<[^>]*>//g' | head -20

# JSON Feed format
curl -sL "https://example.com/feed.json" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(i['title'], i['url'], i.get('date_published','')) for i in d.get('items',[])]"
```

**When browser fallback is acceptable:**
- A source has no RSS feed (rare, nearly every major site does)
- The RSS feed returns empty or stale data
- You need full article body text for a specific story (RSS gives headlines + descriptions, not full text)
- The feed itself is blocked (also rare, RSS readers don't trigger bot detection)

**This rule applies to ALL research tasks, IronPulse, Larry Weekly, TensorFeed, ad-hoc questions, and any other information-gathering request.**

### 1. Never Answer Technology Questions From Training Data (CRITICAL)
When the user asks a question about technology, tools, platforms, best practices, data, metrics, algorithms, industry standards, or any fast-moving domain, **assume your training data is out of date and research from live sources before answering.** Even if your training cutoff ended yesterday, technology changes too fast to trust static knowledge.

**The failure (July 2026):** User asked "How many times a day should I post on Pinterest to build up my account?" I answered from training data (3-5/day for new accounts, ramping to 10-15/day) without checking. The user corrected: "When I ask questions like that you should always assume you don't have the full picture and look." I then researched Pinterest's official help center, business site, and Academy, none of them publish posting frequency recommendations. The numbers I gave were community consensus, not platform policy.

**The rules:**
1. **Default assumption: you don't have the full picture.** Even if the question seems simple or the answer seems obvious from general knowledge.
2. **Research from the platform's own sources first**, official docs, help centers, business sites, creator hubs, academies. These are the only authoritative sources for platform-specific information.
3. **If the platform doesn't publish the answer, say so.** "Pinterest does not publish a recommended posting frequency" is a valid answer. Do not substitute community consensus or third-party data as if it were official.
4. **Cite what you found and where.** If you found nothing, say "I checked [source A], [source B], and [source C], none of them address this."
5. **Do not answer from training data alone for any question where the answer depends on current platform policy, algorithm behavior, or industry standards.** These change too frequently for training data to be reliable.
6. **Self-test:** "Could this answer change based on a platform update in the last 6 months?" If yes, research it. If no, still consider whether the user would benefit from a verified source.

### 1.5 Sweeping Market Claims Are Research Claims (CRITICAL)
"X is dead", "X is saturated", "there are no good options for X" are factual claims about a current market. A casual, conversational question does not lower the evidence bar; a confident dead-end verdict reads as fact and kills the user's follow-through, so an unsourced one costs more than an honest "I have not checked".

1. Assert a sweeping market verdict only with live sources, or label it explicitly as an unverified read ("my impression, not checked").
2. When the user pushes back skeptically ("really?", "there aren't any?"), treat it as a correction signal: re-verify the specific claim against live sources instead of restating it more confidently.
3. When the user's stated constraint is "no account-building" or "no profile-building", distinguish creating an account from building reputation. Qualification-based routes (applications, assessments, staffing firms, vetted networks) need an account but not months of seller history; dismissing them over the account requirement manufactures a false dead end.
4. In recommendation-list deliverables, verify each entry against its live official page and mark per entry what was verified (entry path, current listings) versus what is not guaranteed (acceptance, assignment volume, earnings). Present routes, not promises.

### 2. Never Fabricate (CRITICAL)
**Never invent specifics from general trends.** If you don't have verified source material for a factual claim, say so. Do NOT:

- Extrapolate version differences from naming conventions ("5.2 must have bigger context than 5.1")
- Deduce model capabilities from what you'd *expect* in an update ("it probably has better coding")
- Bridge gaps with plausible-sounding fiction when no source exists
- Present general improvement trends as concrete feature differences

**What happened (June 2026):** User asked for GLM-5.1 vs GLM-5.2 differences. I had no primary source but instead of saying "I don't have that information," I extrapolated from what a typical model update would include, bigger context, better coding, new parameters, and presented it as fact. The user caught it immediately and had to call me out. **Extrapolation is fabrication.**

**The rule:** If you can't find a primary-source answer, your only acceptable answers are:
- "I don't have that information, let me look it up" (then actually look)
- "I checked and found nothing definitive on that"
- "I can only find X, Y, Z, here are the sources"

Anything else is manufacturing facts.

**Self-test before every factual statement:** "Could I point to a specific source URL or document line for this claim?" If no, don't say it.

### 3. No Wikipedia
Wikipedia is never an acceptable source. Do not cite it, reference it, or use it as a research starting point. The user considers it unreliable. If a search result points to Wikipedia, skip it and find the primary source.

### 4. No Propaganda or Biased Sources
The user wants facts, not narratives. Avoid:
- Editorialized news outlets presenting opinion as fact
- PR-heavy corporate announcements as sole sources without cross-referencing
- Politically motivated reporting on either side
- Any source that frames rather than reports

### 4.5 NO AI-GENERATED CONTENT FARMS OR LOW-CREDIBILITY BLOGS (CRITICAL)
**Never cite AI-generated review sites, SEO content farms, or low-credibility blogs as evidence.** These fabricate "I tested it" claims, invent ratings, and produce confident prose about products they have never touched. They are indistinguishable from real reviews unless you check whether a human actually did the work.

**The failure (Aug 15, 2026):** User asked what happened to AI.com. I cited agent-finder.co and aitooldiscovery.com as "independent reviews" proving the product worked. Both were AI-generated content farms, agent-finder.co literally disclosed "Atlas researched and drafted this article using AI-assisted tools." The user had actually signed up after the Super Bowl and was still on a waitlist; no one on the internet had gotten an agent. I presented fabricated reviews as fact over the user's real experience. The user's verdict: "You talk out of all sides of your ass."

**The rules:**
1. **A review is only evidence if a real person tested the product.** If a site discloses AI-assisted drafting, or reads like generic SEO filler, it is NOT a source, it is content marketing.
2. **Check for the disclosure.** Sites that say "researched and drafted using AI tools," "AI-assisted," or have no named human author/editor are automatically disqualified.
3. **The user's direct experience is the ground truth.** If the user tells you a product doesn't work, and a "review" says it does, the user wins. Do not argue with the user using content-farm prose.
4. **When the user says "no one on the internet has X," verify against real user evidence** (HN Algolia, Reddit via pullpush, official forums), NOT SEO review sites. If real users confirm the waitlist/no-access reality, report that.
5. **Credible sources only:** official company announcements, primary documentation, established trade press with named human journalists, government data, academic sources, and real user communities (HN, Reddit, official forums). Blogs and content farms are not credible.
6. **Self-test before citing any review:** "Did a named human actually test this, or is this AI-generated SEO content?" If you cannot confirm a human tested it, do not cite it.

### 2.6 Back Up Interesting Claims With a Credible Source (CRITICAL)
**When you find something interesting, verify it against a credible source before reporting it.** People write anything for clicks, and ranking page one on Google does NOT mean a claim is accurate. Search ranking is a popularity/SEO signal, not a truth signal.

**The rules:**
1. **Page-one ranking ≠ accuracy.** A result being first on Google, keenable, or firecrawl means it won the SEO game, not that it's true. Treat high ranking as a reason to be MORE skeptical, not less.
2. **Interesting claims need corroboration.** If a claim is surprising, dramatic, or convenient, find a second credible source that independently confirms it before repeating it. One source, especially a low-credibility one, is not enough.
3. **People write for clicks.** Sensational, contrarian, or shocking content is often fabricated or exaggerated to drive engagement. Assume the worst until a credible source backs it up.
4. **The pipe is full of crap by design.** Search tools return whatever is out there, SEO sludge, AI filler, content farms. The agent is the filter. Treat every scraped result as guilty until proven credible.
5. **If you cannot back an interesting claim with a credible source, say so.** "I found this claim but couldn't verify it with a credible source" is an honest answer. Reporting an unverified interesting claim as fact is fabrication.

### 4.6 Verify the Qualifier Attached to a Number, Not Just the Number (CRITICAL)
**A headline figure is almost always an extreme, a percentile, or a top-decile stat. Lifting it as the typical case turns a true number into a false claim.** Read the source's own sentence and reuse its wording for the qualifier, and carry that qualifier into anything you write.

**The rules:**
1. **Find the source sentence, not the headline.** Headlines drop qualifiers by design. If the article says "the 90th percentile exceeded $7,000 a day" and "the median was over $600 a day," writing that "researchers spend $7,000 a day" is wrong even though the number is real and appears in the source.
2. **Read the qualifier pairs that get swapped:** percentile vs median vs mean, per-employee vs per-company vs total, calendar month vs fiscal quarter vs trailing average, top 1 percent vs all customers, peak vs sustained, tokens vs requests, gross vs net.
3. **Confirm the qualifier before writing the claim.** Most false claims in a fact-checked article come from a correct number attached to the wrong qualifier, not from an invented number, so the qualifier check is the highest-yield step in the whole verification pass.
4. **Verify the outline's framing date, not just its numbers.** An outline that says a paper or report "landed this morning" is describing when the digest carried it, not when it was published. Read the source's own date line (for arXiv, the Submission history block on the abstract page) and write the true date. A framing date is a factual claim like any other, and in a piece whose value is that nothing in it is false, a wrong date poisons the whole article.
5. **Fetch the full text, not only the abstract.** For arXiv, `https://arxiv.org/html/<id>v1` carries what the abstract omits: the mechanism step by step, thresholds and quantiles, the experimental setup (engine and kernel versions, GPU model), secondary benchmarks, and the authors' own Limitations section. Caveats an author states are verified facts and belong in operator-grade coverage, attributed to the authors. Build the piece from the body, not from the digest's summary of the abstract.
6. **Verify derived and implied claims too.** When an outline stitches a claim from two sources, or states a consequence the paper only implies, check the consequence separately instead of repeating the outline's phrasing.
7. **Fetch primary sources text-first before reaching for the browser.** For arXiv, news outlets, and vendor blogs, `python3 -c "from scrapling.fetchers import Fetcher; print(Fetcher.get('<url>', timeout=45).get_all_text()[:3000])"` gets the body in one call. If the head of the output is nav and menu chrome, slice from a known body marker (for arXiv, slice from the word `Abstract`) rather than printing the head. **A 200 with an empty body means the fetch was blocked, not that the page is thin.** Cloudflare and PerimeterX fronted sites (vendor blogs, GitHub, MarkTechPost) hand the plain `Fetcher` a 200 and `len(page.text) == 0` without raising an error. Check the length, and on empty re-fetch the same URL with `StealthyFetcher().fetch(url, headless=True, network_idle=True)`. Write the fetched text to a file and read it back in pages instead of printing one slice, since the section you need may sit past the cut. **A connect-level failure is a different animal from a block.** When scrapling dies with `curl: (7) Failed to connect` (after its own retries), the host never answered, so there is no block to defeat and stealth fetching buys nothing. Run that URL through `web_extract` before downgrading the claim: a different fetch path often reaches a host one client could not open. Do not mark a domain blocked, and do not call a claim unverifiable, until both a scrapling fetch and an extract have failed. **Resolve which interpreter carries scrapling before concluding it is unavailable.** The managed project venv and the default `python3` are not guaranteed to have it; check each interpreter directly, run probes from a neutral cwd so a local directory name cannot shadow the import, and if only the system interpreter has it, reach it from inside the probe script (`sys.path.insert(0, "/usr/lib/python3/dist-packages")`) instead of reinstalling anything. One failed import proves something about one interpreter, not about the tool. **Write fetch output to `.txt`, not `.md`.** The scrapling CLI's Markdown writer imports `markdownify` lazily in `scrapling/core/shell.py::_convert_to_markdown`; when that package is absent the fetch still succeeds (the log shows `Fetched (200)`) but the `.md` file is written empty. A 0-byte output file is therefore NOT evidence the site blocked you. Either use `scrapling extract get <url> out.txt --ai-targeted`, which returns the readable body text directly and is what article and research workflows actually want, or `pip install markdownify` into the live scrapling environment. **Read the logged status code line, not just the emptiness of the file.** The CLI prints the real status per URL, so `Fetched (404)` means the slug is wrong (find the canonical URL by headline search) while a 403 or an interstitial means the site is fighting you (work the blocked-page ladder). A guessed article slug is the usual cause of a 404 on an outlet that is otherwise fetchable, and a 404 error body renders full site chrome, so a status-blind text dump of it looks like a successful fetch.

### 4.7 Verify the Outline's Paraphrase Before Reusing It (CRITICAL)
**A summary of a source is not the source. Paraphrase compresses nouns, units, and scale, and the compressed version is wrong in a way that reads perfectly plausible.** When you are handed an outline, brief, or data file that summarizes a document, open the document before you reuse the summary's phrasing.

**The rules:**
1. **Check the noun, the unit, and the scale.** A source describing N modules inside a single software suite becomes "N platforms" in a paraphrase. A raise described as a share placement plus a convertible bond sale becomes "a funding round." Both are wrong as written, and neither looks wrong on the page.
2. **Write the source's version, even when it contradicts the outline.** Then tell the user what changed and why in one line. A silent correction hides the fact that the outline was wrong; a narrated one lets them fix the outline.
3. **Name the document, not just the issuer.** Cite joint advisories by number plus issuing agencies and date. "A government report" is not spot-checkable; an advisory ID is.
4. **Attribute allegations as allegations.** Anything sourced to a government advisory or a company threat report gets "the agencies alleged" or "the company assesses" plus one plain sentence saying it is not an adjudicated finding. Do this in the body, not in a footnote.
5. **List only what the deliverable cites.** In a SOURCES or references section, read the list back and confirm every entry has a matching claim above it. Drop what you checked but did not use. One unfindable entry discredits the whole list.
6. **A news summary of the source is not the source.** Aggregators repackage a vendor's or researcher's original post and quietly drop specifics: an attack-chain component, a named mechanism, a number, a qualifier. When the article leans on such a detail, confirm it in the original post and cite that post. A detail that exists only in the aggregator's version is unverified even when the aggregator's headline claim checks out. When you switch to the primary source mid-fact-check, update the SOURCES entry to match.

Full procedure, including the paraphrase traps seen in practice and the step order for going from a daily data file to the numbered primary document: `references/primary-document-verification.md`.

8. **Get the canonical URL from a headline search, then fetch it. Do not guess slugs or loop.** Trade-press URLs carry a section path and numeric story id, `/<section>/<yyyy>/<mm>/<dd>/<slug>/<storyid>`, so a guessed short slug (`/<yyyy>/<mm>/<dd>/<shorthandle>/`) 404s, and a site's own search endpoint (The Register's `/Search/?q=`) can 404 as well. Search the article headline in quotes, take the canonical URL from the result, and fetch that. The same applies to vendor docs: many docs sites publish a plain-text index at `https://docs.<vendor-domain>/llms.txt` listing every doc page, so one fetch returns the real URLs for primitives, pricing, and capability pages instead of you guessing `/pricing` or `/docs/...` paths. Two failed URL guesses on the same claim means stop guessing and search.
9. **A 404 still renders site chrome, so read the status, not just the text.** An error page from a large outlet returns the full nav, the topic list, and a column of current headlines; a status-blind text dump of it looks exactly like a successful fetch of a real article. Print the status code alongside the body in any batch fetch and check it before trusting a single sentence.

9. **When every search engine is CAPTCHA-blocked, resolve a headline through the outlet's own search endpoint.** `scrapling extract get "https://www.tomshardware.com/search?searchTerm=<headline words>" out.html` then `grep -oE 'href="https://www.tomshardware.com/[a-z0-9/-]+"' out.html | sort -u` and filter the slugs for the story's distinctive words. Fetch as `.html`, never `.txt`, text mode strips the markup and every href with it. Most trade press (Tom's Hardware, The Verge, Future plc titles) exposes `/search?searchTerm=`, so one request returns the true canonical slug for a story that is only hours old, which is exactly what a SOURCES section needs.
10. **Google News RSS confirms a headline's existence and attribution when the article body is unreachable.** `scrapling extract get "https://news.google.com/rss/search?q=<story keywords>&hl=en-US&gl=US&ceid=US:en"` returns the headline near word for word with its publication and date. Use it to corroborate that a story named in a data file is real and correctly attributed, then cite the publication rather than the aggregator. The feed is Atom-shaped, one `<title>` and one `<link>` per line, so parse it line by line instead of with an `re.findall(r'<item>...')`, which returns zero matches.

### 4.8 State the Maturity of Thin Sources (CRITICAL)
**An early demo, an unbenchmarked product, and a vendor's launch page are three different weights of evidence. Reporting them with the same confidence flattens the difference the reader needs most.**

**The rules:**
1. **Say what the source is.** An unbenchmarked experiment gets "early experiment, not a benchmarked product." A Hacker News submission gets its live point count rather than being implied to be an established artifact.
2. **Fetch the live signal at verification time.** HN's Algolia API (`https://hn.algolia.com/api/v1/search?query=<terms>&tags=story`) returns `points`, `num_comments`, `created_at`, and the canonical `https://news.ycombinator.com/item?id=<objectID>` URL in one call, so the maturity line and the citation URL come from the same fetch instead of from memory.
3. **Never list a source in a references section that you did not open.** A line naming a publication with no URL is unverified attribution wearing verified attribution's clothes. If the item was known only through a data file, cite the data file with its date.
4. **Use the source's wording, not the outline's paraphrase.** Summaries compress nouns, units, and scale; when the primary source has the exact phrase or figure, the deliverable carries the source's version, and a substantive disagreement means the sentence gets rewritten. Tell the user what changed in one line rather than correcting it silently.

### 4.9 A Vendor's Own Comparison Table Is a Claim, Not a Measurement (CRITICAL)
**The headline number in a technical article is usually the vendor's self-report. State it as reported, and get one independent reproduction before asserting it as the state of the art.**

**The rules:**
1. **Separate the two kinds of number.** A vendor's headline benchmark score, its cost-per-query figure, its latency figure, and its "versus the old way" multiplier all come from the same marketing table and all carry the same weight: a claim. Write them as "the vendor reports X" or "reports X" rather than as bare fact.
2. **Get one independent reproduction.** A third-party tutorial, an independent write-up, or a competitor's audit that reprints the same figure is enough. One is sufficient; it converts the vendor's claim into a corroborated one and lets the article drop the hedge.
3. **The competitor rows inside a vendor table are the vendor's numbers too.** A "us versus them" accuracy spread frames both sides. Check the competitor's own published result or an independent benchmark before repeating the comparison as a market fact.
4. **Report the benchmark's own coverage and provenance.** A score claimed on the full benchmark outranks one claimed on a two-thirds subset, and a score measured on a sample outranks one nobody can inspect. Note the vendor open-sourced its evaluation separately from whether the number is independently reproduced; those are different questions.
5. **The vendor's own concessions are the most valuable lines on the page.** A cost figure, a latency figure, or a "not recommended for" note that the vendor volunteers is the honest half of the article and is safe to state directly, attributed to the vendor. Quote it rather than inventing your own caveat.
6. **Cross-check the vendor's own pages against each other.** A repo README, a blog post, and a docs pricing page often disagree on the same figure because they were updated at different times. Read all of them and use the specific page that owns the number (pricing lives on the pricing page, indexing cost lives in the post that introduced the feature). When the marketing path for pricing 404s, try the documentation host's equivalent path before treating the number as unavailable.
7. **Pull live repository counts at verification time, from the counter elements.** Star, fork, and watcher counts change hourly and any figure carried over from an outline, a search snippet, or another outlet's older piece is stale. Read the named counter elements on the repo page rather than regexing the whole page, which returns unrelated numbers, and state the count as of the moment checked.
8. **Extract a repo's README from the rendered repo page, not the raw host.** A request for the README on a raw-content host can return an empty body with a success status, which reads like an empty file and is really a blocked fetch. Fetch the repo page and read its rendered README container. The rendered page also yields the relative links the README points at (benchmark repos, docs subdomains, the author's own blog), which is usually where the figures behind the headline number actually live.

### 5. Prefer Primary Sources
Rank sources by reliability:
1. Official or Direct, company press releases, official documentation, government data, academic preprints on arxiv or similar, raw datasets
2. Industry-standard, reputable trade publications, peer-reviewed journals, official APIs
3. Cross-verified, only cite a secondary source when two independent reliable sources agree on the same facts

### 6. Verify Before Citing
- If a model release is announced, link to the actual announcement page
- If citing a benchmark score, link to the paper or official blog
- If a date or version number matters, confirm it from the source, do not guess or extrapolate

### 7. User-Provided Source URLs Are Authoritative (CRITICAL)
When the user hands you a direct source URL (an X post, a link, a page) as evidence for a claim, that URL is the primary source and is authoritative. Verify the URL itself with `web_extract`, do NOT let stale search results override it.

**The failure (Aug 14, 2026):** User said "GLM-5.3 just dropped" and dropped the official Z.ai X link. The agent ran `web_search`, found only Aug-3 "not released" pages, and told him it hadn't dropped. The link proved it was live. The search results were stale; the link was current. The user's reaction: "did you really think id give you bs?"

**The rules:**
1. When the user provides a source URL, `web_extract` that URL FIRST. The answer is in the source, not in a re-query.
2. Search results are a discovery aid, not a verdict. A dated "not released" page from days ago does not override a live official announcement the user just linked.
3. If the URL is inaccessible, say so plainly, do not substitute a stale "not released" conclusion from search.
4. Official release-notes pages and model hubs can lag the actual announcement (the X post / blog goes live first). Check the user's link before trusting an index page that says "not released."

This complements Rule 5 in `no-extrapolation-rule` (user-stated facts are facts): a user-provided source is the strongest form of that, verify it, don't argue with it.

## Temporal Relevance (CRITICAL for "today" queries)

When the user asks about something "today," "reported today," "happening now," or "any issues today," temporal scoping is the #1 priority. Do NOT surface results from last week, last month, or "still open" issues from April as if they're today's news.

### Rules
1. **Filter by creation date, not just relevance.** On GitHub issues, use `sort:created-desc` and check the "opened Xh ago" / "opened Xd ago" labels. Anything older than 48 hours is NOT "today" unless the user explicitly asks for ongoing/historical context.
2. **When the user says "today," they mean today.** Do not lead with last week's news even if it's the most prominent result. Lead with what was filed/updated today, then mention older items as secondary context only if relevant.
3. **GitHub issues workflow for "today" queries:**
   - Use `is:issue sort:created-desc` (no `is:open` filter, closed issues from today are also relevant)
   - Scan the first page for items opened "Xh ago" or "Xd ago", anything "1w ago" or older is not today
   - If the first page has no today items, say "nothing reported today", do not pad with last week's items
4. **HN Algolia for "today" queries:**
   - Use `&tags=story&hitsPerPage=20` and check `created_at` fields
   - Filter to the last 24-48 hours by checking timestamps
5. **When you must mention older items** (e.g. a chronic issue that's still open and relevant), clearly label them: "Nothing new today. The most relevant ongoing issue is #XXXX from [date], still open."
6. **User frustration signal:** If the user says "I will be angry if you tell me about last week's shit," you already led with stale data. The fix is to always sort by creation date descending and check timestamps before reporting.

### Pitfalls
- GitHub's default sort is by relevance, not date. Always add `sort:created-desc` explicitly.
- "1w ago" means 7+ days old, not today.
- A popular/upvoted issue from last week is still last week's news. Popularity ≠ recency.
- When search engines are blocked (common), GitHub issues sorted by date is often the most reliable "today" signal available.

## Output Standards
- When providing factual answers, reply should feel definitive, not hedged
- If the user asks "did X happen," find a yes-or-no backed by a primary source
- If you cannot find a primary source, say so and offer to dig deeper, do not fabricate from secondary sources
- No editorial framing, no "interestingly," no "notably", just the facts

## Model/Product Research Pattern
When investigating a new model release (e.g. "Nemotron Ultra"), use this specific workflow:

### A. General Research
1. **Find the main launch thread** via HN Algolia: `/api/v1/search?query="Model Name"&tags=story`
2. **Check for Ask HN threads**, these surface strongest negativity
3. **Extract comment sentiment** from the main thread. Use `delegate_task` for large threads.
4. **Cross-reference independent evaluators**:
   - Andon Labs, alignment evaluations
   - Gertlabs, independent coding benchmark results
   - Marginlab, SWE-Bench-Pro pre-release tracking
   - Simon Willison's blog, neutral baseline
   - lmsys Chatbot Arena, ELO scores from human votes
5. **Note what benchmarks the company omitted** since the previous release.
6. **Check HN comments sorted by points** using Algolia: `tags=comment&numericFilters=points>0`

### B. User Sentiment Research (Not Press), CRITICAL WHEN USER SAYS "PEOPLE, NOT JOURNALISTS"
When the user asks for what *users* are saying (not journalists/influencers/media), do NOT rely on search engines. They surface press, not user opinion. Use this API-first workflow:

1. **HN Algolia for real user comments**, best source for informed technical user sentiment:
   - Stories: `curl -s "https://hn.algolia.com/api/v1/search?query=MODEL_NAME&tags=story&hitsPerPage=30"`
   - Comments: `curl -s "https://hn.algolia.com/api/v1/search?query=MODEL_NAME&tags=comment&hitsPerPage=50"`
   - Full thread: `curl -s "https://hn.algolia.com/api/v1/items/STORY_ID"`, parse `children` for comments
   - No auth needed; almost never blocked

2. **HuggingFace API**, download counts, likes, discussions as objective user-interest proxies:
   - Models: `curl -s "https://huggingface.co/api/models?search=MODEL_NAME&sort=lastModified&direction=-1&limit=20"`
   - Discussions: `curl -s "https://huggingface.co/api/models/ORG/MODEL/discussions?limit=30"`
   - Compare HF engagement vs HN buzz vs press hype, report all three

3. **Reddit via pullpush.io** (when Reddit blocks direct requests):
   - `curl -s "https://api.pullpush.io/reddit/search/submission/?q=QUERY&subreddit=SUBREDDIT&size=25"`
   - Expect Reddit to block raw API from cloud IPs, have fallback ready

**Reddit is a dead end for GEO/distribution, not just research.** Reddit declared war on AI (blocked crawlers, locked down the API), so nothing posted there gets picked up by AI search. Content on a platform that blocks AI access won't be cited by any generative engine, regardless of human traffic. Don't recommend Reddit as a GEO/distribution channel, spend that effort where the AI can actually read you.

4. **TensorFeed** for contextual news + model data:
   - `tf.news_recent(hours=72, limit=50)` then filter articles by model name
   - Aggregates from technical sources, not mainstream press

5. **Search engines often fail**, Google, Reddit, and DuckDuckGo all CAPTCHA-block cloud IPs. Pivot immediately to APIs (steps 1-4). Do not retry the search engine more than once.

6. **Distinguish two tiers**, NVIDIA especially has:
   - The "press drop" (marketing, benchmarks, journalists), announces first
   - The "user reality" (inference speed, quant quality, actual quality vs alternatives), emerges days/weeks later from HN and HF
   - Report BOTH but label them clearly: "Press says" vs "Real users report"

7. **Filter out press/reviewer noise aggressively**: ignore TechCrunch, The Verge, Ars Technica, VentureBeat, YouTubers, and press-release reprints. A "user" runs the model or builds with it, not someone who read the press release.

### B2. Model-vs-Model Head-to-Head (When Asked "Is X Better Than Y?")

When asked "is X better than Y?", do NOT pick a winner from vibes. The honest answer is often "they share no like-for-like benchmarks", that IS the finding. Workflow:

1. **Check for direct head-to-head tests**, n=1, directional, label the limitation clearly.
2. **Pull a consolidated leaderboard**, e.g. OrcaRouter blended rank, to compare across a common scale.
3. **Look for the "reasoning budget trap"**, one model may burn its token cap reasoning on easy tasks, making it look worse on trivia-heavy evals while excelling on hard reasoning.
4. **Separate vendor-reported from independent**, flag any unverifiable numbers as vendor-reported.
5. **Check per-task fit**, a single benchmark doesn't generalize across tasks.
6. **Fetch the independent evaluator's own head-to-head page when one exists.** Artificial Analysis publishes a per-pair comparison at `https://artificialanalysis.ai/models/comparisons/<slug-a>-vs-<slug-b>` (also try the `-vs-<name>-max-effort` form, since effort level is part of the slug) which returns on one page the intelligence index, input/output/cache-hit price, cost per task, output tokens per task, output speed, time to first token, end-to-end response time, parameter counts, and the open-weights flag plus license. One fetch of that page beats stitching a table from two vendor pages, and it is the evaluator's measurement rather than either lab's self-report. Treat the pricing rows as list price at the time measured.
7. **End on test-your-workload**, offer to draft the A/B test that answers it for the user's actual use case.

**Anti-patterns:**
- Claiming "X is better for writing" with no prose benchmark
- Broad superiority from one agentic benchmark
- Naming a winner with zero shared evaluations

### C. News Timeline Reconstruction (When Search Engines Are Blocked)

When you need to reconstruct a chronological sequence of events for a breaking AI/tech news story and all search engines are CAPTCHA-blocked, use HN Algolia as a timeline source:

1. **Single broad query**: `curl -s "https://hn.algolia.com/api/v1/search?query=TOPIC&tags=story&hitsPerPage=50"`, returns up to 50 story titles with timestamps
2. **Sort chronologically** from the `created_at` fields to build the timeline
3. **Identify inflection points** from titles alone, release dates, jailbreaks, government actions, company responses, user backlash
4. **Fetch key stories** for details: `curl -s "https://hn.algolia.com/api/v1/items/STORY_ID"`
5. **Fetch the article** from the story's `url` field if accessible

This works because HN Algolia is never blocked and has excellent coverage of AI/tech news. See `references/news-timeline-reconstruction.md` for a full worked example (Fable 5 timeline, June 2026).

## Search Engine Fallback: DuckDuckGo HTML Endpoint

**Preferred over curl: use scrapling `Fetcher` for DDG.** `https://html.duckduckgo.com/html/?q=QUERY` works through scrapling's `Fetcher` with `referer='https://www.google.com/'`, and returns parseable text via `get_all_text()`. This bypasses the CAPTCHA that raw cloud-IP curl hits. The curl variant below is the fallback when scrapling is unavailable.

When Google and DuckDuckGo hit challenges, use the **DuckDuckGo HTML endpoint**, a separate endpoint that serves plain HTML results and is sometimes still reachable:

```bash
curl -sL "https://html.duckduckgo.com/html/?q=YOUR+QUERY+HERE" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  2>/dev/null | sed 's/<[^>]*>//g' | grep -i -E 'pattern1|pattern2' | head -40
```

**Why this works:** The main DuckDuckGo search page (`duckduckgo.com/?q=...`) serves JS-heavy content and triggers CAPTCHAs from cloud IPs. The `html.duckduckgo.com/html/` endpoint returns plain HTML with no JS and is treated differently by their bot detection, so it is a useful fallback. It is still bot-detected from some cloud IPs and will return a "Select all squares containing a duck" challenge, so do not treat it as guaranteed.

**Try Bing first for plain-text results.** `https://www.bing.com/search?q=QUERY` returns readable result text (titles, URLs, snippets, and news entries) via the same scrapling `Fetcher` call and is the most tolerant of automated queries. Order of attempts: Bing, then DDG HTML endpoint, then APIs. Do not cycle engines more than twice before pivoting to an API or fetching the vendor or outlet URL directly.

**The plain `Fetcher` is enough for Bing, and it is the first thing to try the moment another engine challenges.** `Fetcher.get("https://www.bing.com/search?q=<terms>")` returns 200 with the full SERP as readable text, no stealth fetcher and no browser required. Three rules for using it well: search keyword phrases rather than natural-language sentences, because a full-sentence query returns dictionary and encyclopedia filler instead of the answer; treat the AI-content disclaimer in Bing's own footer as noise, since it says nothing about the accuracy of the sources linked above it; and remember `site:domain.com <terms>` plus quoted phrases both work. Bing is also the practical route to a `site:` search on any domain when other engines are challenging, which is how you resolve a canonical URL or count a source's coverage. The always-loaded `scrapling` skill lists bing.com as CAPTCHA-blocked in its known-blocking list; that entry is wrong and has not been correct in this environment.

**Extraction pattern:** Strip HTML tags with `sed`, then grep for relevant patterns. The results are plain text with URLs embedded in `<a>` tags. For cleaner extraction of titles + URLs:

```bash
curl -sL "https://html.duckduckgo.com/html/?q=QUERY" \
  -H "User-Agent: Mozilla/5.0" | \
  sed -n 's/.*<a[^>]*class="result__a"[^>]*>\(.*\)<\/a>.*/\1/p' | head -20
```

**Limitations:** No pagination, no date filtering, no image results. Use for quick fact-finding and headline discovery only. For deep research, pivot to APIs (HN Algolia, TensorFeed, HF API) as described in the user sentiment section.

## Building a Monetization or Opportunity Plan From Live Vendor Pricing

When the deliverable is a business plan, a service catalog, a pricing model, or a "what could I sell" report, the credibility of every number rests on it having been read off the vendor's own page during that session, not recalled. The failure mode is a plan that looks thorough and carries stale or invented prices, which is worse than an obviously thin one because it gets acted on.

**The rules:**
1. **Every price is fetched live, and the report says so.** Read each cost anchor off the vendor's own pricing page in the same session and state the date the prices were read. Vendor list price is exactly the kind of number that changes quietly, and a plan built on last quarter's tier names or a withdrawn plan is indefensible when the buyer checks.
2. **Fetch pricing pages directly rather than searching for them.** `Fetcher.get("https://<vendor>/pricing")` works for most SaaS vendors and returns 200 with the tier table. Do not search for "how much does X cost" and quote the snippet; snippets are stale and lose the per-unit qualifier.
3. **Pull the market's own price anchor, not your own guess.** Freelance and agency marketplaces publish their cost guides (Upwork hosts per-deliverable project ranges and hourly bands; Fiverr shows live gig floor prices). One fetch of the marketplace's own page yields both the professional price band and the cheap floor, and the gap between them is usually the single most important commercial fact in the plan. A price recommendation with no marketplace anchor is an opinion.
4. **Match tool cost to the delivery substrate you recommend.** Quote the tier the client would actually run, at the billing cadence you name: note whether each figure is monthly or billed-annually, since the same plan is often 20 percent cheaper annually and the difference compounds across a client base. Prefer free or self-hostable tiers as the delivery layer where they exist, because a service business's margin is decided by the substrate it standardizes on.
5. **Attribute every recurring figure and say who pays it.** In a service plan, distinguish the client's own monthly software cost from the implementer's cost. Conflating them inflates the margin and makes the plan fail on contact with a buyer.
6. **When a headline statistic cannot be verified at the source, cut it and route around it.** A widely repeated number whose primary source is paywalled or unreadable (a gated journal article, a report behind a form) does not get repeated on the strength of secondary citations. State in one line that the source is gated so the number is not being used, then design the deliverable so the client's own data proves the claim instead. This preserves the report's honesty without weakening the argument.
7. **Score on stated criteria and let the arithmetic rank.** When asked to rank candidates, publish the criteria, score every candidate on them, and sort by the total. Do not hand-tune the order afterward. If the ranking contradicts your prior expectation, say so explicitly and explain what the arithmetic surfaced, because that discrepancy is usually the most valuable finding in a comparison deliverable.

## Breaking Rumor Verification ("I saw this on X, is it true?")
When Vinny asks whether a rumor he saw on X is true (an acquisition, a deal, a
release), the crux is labeling **reported vs confirmed**. Anonymous-sourced
reporting ("The Information reported, citing a person familiar with the deal")
is NOT confirmation, even when the headline says "agreed to buy." Check the
companies' own channels (blog, changelog, CEO's X) for silence, track the
escalation timeline, and deliver ONE verdict naming exactly what would
constitute confirmation. Full workflow + worked example (NVIDIA/Hugging Face,
Aug 2026) in `references/breaking-rumor-verification.md`.

## Pitfalls
- **When every direct fetch of an outlet is blocked, the search-result description for that article often carries the full factual payload** (figures, dates, direct quotes, and the primary documents it links to). Treat it as the verification source of record for those specific claims and cite the original publication, rather than grinding the recovery ladder to re-fetch a body you already effectively have. One headline search per blocked outlet beats five fetches, and the search result usually also yields the canonical URL for the page you could not open.
- **A vendor's marketing page can 403 while the vendor's own document CDN serves fine.** Vendor blog and announcement pages are usually the most protected surface a company owns, and scripted fetchers hit 403 on them routinely, but the CDN behind the same company (technical-report PDFs, system cards, model cards) usually answers a plain `web_extract` on the direct file URL. When an outline cites a vendor announcement that will not load, pivot to the technical document for the same release. It states the claim more precisely than the blog post did, it carries the numbers the blog rounded off, and it is the stronger citation regardless.
- **A vendor's headline benchmark or cost figure is a self-report until independently reproduced.** See §4.9. Do not state a vendor's own comparison-table number as the state of the art, and do not repeat its competitor rows as market data.
- **Live repository counts go stale in hours.** Read the counter elements on the repo page at verification time and state them as of that check. Never carry a star count forward from an outline or another outlet's piece.
- **An empty body with a success status is a blocked fetch, not a thin page.** This applies to raw-content hosts as much as to the sites §4.6.7 covers. Check the text length, and if it is empty, fetch the rendered page variant (for a repository, the repo page's README container) instead of concluding the content does not exist.
- Wikipedia as "starting point" is still unacceptable. The user blacklisted it, period.
- AI-generated review sites and SEO content farms are NOT sources. They fabricate "I tested it" claims. Check for AI-drafting disclosures and named human authors before citing any review. (See §4.5.)
- Aggregator echo chambers, 10 blogs all citing the same press release is not 10 sources.
- Assuming recency equals accuracy, breaking news is often wrong. Wait for verification.
- Hedging, "might have been released" vs checking the actual announcement page. Always check.
- Model confusion, when asked about specific model versions (e.g. "Opus 4.8"), go to the company newsroom or official blog, do not guess or extrapolate from naming conventions.
- **Stale working titles in outlines/source docs.** When an outline or source document names an article by title (especially a prior article in a serial, e.g. "Note #160, Your Cost Curve Just Broke"), that title may be a working title or outdated. Verify the live page title and URL before citing it in a SOURCES section or cross-reference, and use the live title in the deliverable. A search for the outline's title usually surfaces the real page; if the title differs, trust the live page. Do not propagate the stale working title.
- Paywalled/JS-heavy articles, many news sites (Korea JoongAng Daily, Substack, Bloomberg) serve content via JS rendering that curl can't extract. The HN story title + comments may be sufficient context. If you need the article body, try the browser tool or accept that the title-level timeline is enough.
- HN Algolia story titles can be editorialized, they reflect the submitter's framing, not necessarily the article's headline. Cross-check with the linked article URL when possible.
- Do NOT retry the same blocked search engine more than once. If Google blocks you, don't try Google again, pivot to DDG HTML endpoint or APIs immediately.
- The DDG HTML endpoint returns results in a different order/ranking than the main DDG search. Accept this, blocked search is worse than imperfect search.
- **A same-day launch's named outlet URL is often dead while search returns only aggregators.** For a product announcement named in an outline, the outlet itself may 404 the same day and search may surface only repost sites with no named human author. Do not cite an aggregator to fill that gap. The full vendor text lives on the wire: pull the Business Wire release, or its syndicated copy on Yahoo Finance, and cite the release plus the vendor's own repo or docs page. A vendor statement is a primary source; a site that merely reprinted it is not.
