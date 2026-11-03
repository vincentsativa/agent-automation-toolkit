---
name: phantombyte-ghostwriter-patterns
description: |
  Class-level skill covering the ghostwriter-terminal workflow for PhantomByte article production.
  Fact-checking against arXiv, email delivery via IONOS, X post optimization, and authority positioning.
---

# PhantomByte Ghostwriter Patterns

## When to Use
- Vinny gives you an outline and says "write me this story"
- The outline cites arXiv papers or data files that need fact-checking
- You need to email the finished draft to hello@example.com
- The article must position PhantomByte as an AI engineering authority

## Loading This Skill Without Getting Stuck

`skill_view(name='ghostwriter-terminal')` fails with "Ambiguous skill name" because two copies exist: the bare `ghostwriter-terminal` under `~/.hermes/skills/` and a second copy under `content-swarm/`. The same collision affects `phantom-byte` naming generally.

Do not retry the bare name. Either pass the categorized path, or read the file directly:

```
skill_view(name='content-swarm/ghostwriter-terminal')
read_file('~/.hermes/skills/content-swarm/ghostwriter-terminal/SKILL.md')
```

If a reference file is requested by a name that skill reports as missing, list what the skill actually ships before assuming the content is gone — the file may live in a sibling copy of the skill.

  ## arXiv Verification Recipe (single-pass extraction)

**Fetch with the Python `Fetcher` under the interpreter that actually has scrapling, not a bare `python3`.** Hermes's default `python3` is its bundled 3.14 build, while scrapling lives under `~/.local/lib/python3.12/site-packages`. A plain `python3 script.py` that does `from scrapling.fetchers import Fetcher` therefore fails with `ModuleNotFoundError`. Confirm the working interpreter once, then use it for every fetch in the run:

```bash
/usr/bin/python3 -c "import scrapling; print(scrapling.__version__)"
```

```python
# <this run's $SCRATCH/fetch.py>, run as: /usr/bin/python3 $SCRATCH/fetch.py
import sys
sys.path.insert(0, '~/.local/lib/python3.12/site-packages')
from scrapling.fetchers import Fetcher
for pid in ['2610.02503', '2610.02994']:
    p = Fetcher.get('https://arxiv.org/abs/' + pid)
    open(pid + '.txt', 'w').write(p.get_all_text())
```

Then `read_file` the saved text. This is verified on this machine as of October 2026: four arXiv abstracts pulled in one loop, about 5,000 characters each, authors, submission dates, and every measured number intact.

**Do NOT use `scrapling extract get` for this.** That CLI subcommand routes through scrapling's markdown converter and dies with `ModuleNotFoundError: No module named 'markdownify'`, leaving a 0-byte output file while still logging `Fetched (200)` and exiting 0. If you do use any CLI subcommand, check the OUTPUT FILE SIZE, not the exit code. Use the Python `Fetcher` plus `page.get_all_text()` instead; it needs no markdown dependency. One CLI call per paper, looped over the outline's IDs, puts every abstract on disk as plain text you can re-read and quote from. The same `extract get` command verifies a vendor blog or Hugging Face blog post, both of which render their full body text this way with no browser and no JS evaluation. This is the fast path for a traceability block that names four or five arXiv IDs.

When you do take the browser path, the `/abs/` page carries everything you need in one navigation: authors, submit date, and every hard number. Pull all of it in one call instead of reading a snapshot and paging around.

```
js("document.title")
js("document.querySelector('h1.title')?.innerText")
js("document.querySelector('blockquote.abstract')?.innerText")
js("[...document.querySelectorAll('.authors a')].map(a=>a.innerText).join(', ')")
js("document.querySelector('.dateline')?.innerText")
```

Rules that fall out of this:

- **The abstract is the authority, not the outline.** Outlines routinely drop author names entirely and misstate submission dates. Take both from the page.
- **Lift the precision the outline compressed away.** Abstracts carry confidence intervals, task families, benchmark names, and sample sizes that outlines summarize into a bare headline number. Include them. Stating the interval alongside the point estimate is what separates an authority piece from a re-summary of the same paper, and it costs one extra clause.
- **Respect the unit exactly.** A percentage-point gain is written "X percentage points", never as a multiplier, a "times better" multiple, or a fold-change. Converting a point gain into a multiplication turns a true statistic into a fabricated one. When an outline explicitly warns against a unit conversion, that warning is binding on the whole deliverable.
- **Outlines routinely cite a paper they got slightly wrong.** arXiv IDs, titles, and numbers in an outline are the author's transcription; the abstract is ground truth. Where they disagree, the abstract wins and the correction is silent (no note to the reader about the discrepancy).

## Fact-Checking arXiv Papers (Browser Path)

See `references/browser-verification-for-fact-checking.md` for the scrapling fetch patterns, the arXiv API shortcut for finding unnamed papers, the Hugging Face repo-name rule, and the vendor newsroom slug-extraction recipe.
When the outline cites specific arXiv papers, verify claims before writing:

1. Navigate to `https://arxiv.org/search/?query=[paper+title+keywords]&searchtype=all`
2. Confirm the paper exists and matches the outline's description
3. Click through to the abstract page (`https://arxiv.org/abs/[id]`)
4. Verify key numbers (variance, overhead reduction, call reduction, evidence rates) against the abstract
5. If the abstract does not contain the number, open PDF or HTML version
6. If still unreachable after 2-3 attempts, mark as unverifiable and omit

The browser path is faster than the API for spot-checking 3-5 papers because abstracts are human-readable without XML parsing.

## Fact-Checking Verification Pitfalls (July 2026)

- **TensorFeed outlines may conflate microbenchmark numbers with end-to-end results.** When an outline cites specific performance numbers from a paper, verify which experiment each number comes from. Example: in the Multiverse Computing distillation paper (arXiv:2608.03796), the "85.2 GiB to 5.45 GiB" memory reduction is from the isolated toy output-projection microbenchmark (Figure 3), while the "57 seconds to 12.2 seconds" step time and "4 nodes to 1 node" result are from the GPT-OSS-20B end-to-end distillation (Section 4.2). Presenting them as the same experiment is a factual error. Always map each number to its specific experimental section.
- **Google and DuckDuckGo bot detection on search queries.** Automated searches frequently trigger CAPTCHA or bot-protection pages (Google "sorry" pages, DuckDuckGo empty results). When this happens, switch to Bing News or Bing web search as the primary verification engine. Bing has proven more tolerant of automated queries for tech journalism verification.
- **Em dashes in source titles propagate into drafts.** Daily data files (blogwatcher dumps, TensorFeed reports) copy article titles verbatim from upstream publications. Those titles often contain `—` (em dash). When you transcribe the SOURCES section or quote a publication name, the em dash silently enters your draft. The pre-flight `grep -c '—'` check will catch it, but it is faster to sanitize in real time: replace `—` with `-` as you write, especially in the SOURCES section where you are quoting external titles verbatim.
- **Reuters / DataDome bot detection on direct article links.** Reuters articles frequently load a "DataDome Device Check" iframe that blocks content extraction. When this happens, rely on Bing News snippets (which often quote the Reuters headline and lede) or the daily data files as fallback. Do not spend more than one attempt on a Reuters article that hits DataDome.
- **Hugging Face blog listing page as fallback.** When a vendor blog post URL returns 404 (e.g., Liquid AI's slug mismatch), the Hugging Face blog listing page at `https://huggingface.co/blog` often still shows the article title, author, and date. This confirms the article's existence even when the direct URL is unreachable.
- **Hugging Face blog slug mismatch.** Direct guessed slugs like `/blog/idle-gpu-cost` often 404. The listing page shows the actual title and can help you construct the correct URL or confirm existence without needing the direct link.
- **TechCrunch article URLs frequently 404 or paywall.** Outlines citing specific TechCrunch URLs often return 404 even when the article was published. When a TechCrunch URL fails, search `techcrunch.com/?s=TOPIC` to confirm the article exists in search results. If confirmed, cite as "TechCrunch search confirmed; direct URL paywalled at time of verification." Do not fabricate a working URL.
- **Curl as fallback for TechCrunch verification.** When browser returns 404 on a TechCrunch article, a curl fetch may return the actual content if the 404 was bot-detection-related. Try: `curl -sL "URL" | grep -i "KEYWORD"`. If curl also returns 404 data, rely on search confirmation.
- **Daily data files may be missing on disk.** The outline may reference files like `ironpulse-2026-07-29.txt` or `tensorfeed_report_2026-07-29.txt` that are not present in the expected Desktop directory. When this happens, attempt web verification via Bing News. If both the data file and web search fail due to bot detection, treat the claim as unverifiable and omit it. Do not fabricate attribution.
- **TODAYS DATA FILES folder can be completely empty.** Vinny may keep the daily data drop in a different location or the folder may exist but contain no files. Do not stall or ask. Proceed with outline claims + browser verification of named sources only.
- **TODAYS DATA FILES folder is frequently empty.** Vinny often says: "Data files: ~\OneDrive\Desktop\TODAYS DATA FILES". That folder is frequently empty. When it is:
  1. Search the Desktop directly for dated ironpulse, tensorfeed, and blogwatcher files:
     ```bash
     ls /mnt~/Desktop/ | grep -E "(ironpulse|tensorfeed|blogwatcher|20-AI).*2026-08-09"
     ```
  2. Search the home directory and cron output directories:
     ```bash
     find ~/ -maxdepth 3 -name "*2026-08-09*" -type f
     find ~/.hermes/cron/output/ -name "*2026-08-09*" -type f
     ```
  3. If still not found, the outline-referenced daily data files simply do not exist on this machine. Fall back to web search for verification of the specific claims named in the outline. Do not block the writing task waiting for files that are not present.
  4. The outline may also reference specific filenames like "20-AI-News-Stories-2026-08-09.md" that do not exist anywhere on disk. Treat these as unverifiable via local files and verify through web search instead.
- **Meta AI newsroom URLs are unpredictable and frequently 404.** Guessed slugs like `about.fb.com/news/YYYY/MM/meta-ai-.../` often fail. When verifying Meta AI claims, check `ai.meta.com/blog/` first, or rely on daily data files (TensorFeed, blogwatcher) for corroboration. Do not fabricate URLs.
- **PDF URLs through a plain fetcher return raw PDF stream, not text.** When a verification source is a PDF (an industry report, an alliance specification, a standards slide deck), a plain fetch hands back the compressed PDF bytes as garbled text. Use `web_extract` for PDF URLs instead, and fall back to the publisher's HTML page for the same claim when the PDF yields nothing readable. The OpenADR Alliance site is the worked example: its specification page and 3.0 introduction page carry the protocol facts in clean HTML, while the linked PDFs do not.
- **A connect-level fetch failure is not a block.** When scrapling exits with `curl: (7) Failed to connect` after its own retries, the host never answered, so nothing is blocking you and a stealth fetch buys nothing. Run the same URL through `web_extract` before downgrading the claim: a different fetch path often reaches a host one client could not open. Only after both a scrapling fetch and an extract fail do you treat the claim as unverifiable. Do not record a domain as blocked from a connect error alone.
- **A news summary of the source is not the source.** Aggregators repackage the vendor's or researcher's original post and quietly drop specifics: one component of an attack chain, a named mechanism, a number, a qualifier. When the article leans on such a detail, confirm it in the original post and cite that post. A detail that exists only in the aggregator's version is unverified even when the aggregator's headline claim checks out. When you switch to the primary source mid-fact-check, update the SOURCES entry to match.
- **Same vendor, same day, two posts, two framings of one result.** A vendor often publishes a narrative post and an event post on the same date, and the same partner metric appears in both with different units or values (one post credited a partner with "24% more token throughput," the other with "23% better performance per watt"). Check both posts before citing, use the figure and framing the outline named, and do not blend the two into one claim.
- **Mine the arXiv abstract for the hook, not just to verify claims.** When the outline's framing is vague ("a sharp performance drop", "it breaks things") but the paper's abstract carries concrete, citable numbers, lead with those numbers. Verification is also an upgrade pass, not just a check. Session proof (Aug 25, 2026, Article 171): the Compaction Cliff outline opened with "a sharp performance drop," but the arXiv abstract (2608.22752) had the real hook: 53% of safety rules survive one compaction round, 10% after five. Leading with those two numbers made the opening far stronger than the outline's framing. If the abstract's stat is more specific than the outline's, use the abstract's number.
- **ArXiv `/abs/` page is the fastest verification path.** For arXiv papers, navigating directly to `https://arxiv.org/abs/<id>` loads the full abstract with all key numbers visible in the browser snapshot. This is faster and more reliable than opening the PDF or HTML version. Use `/abs/` as the primary check, fallback to PDF only if the abstract is insufficient.
- **ArXiv search result "More" link often fails.** arXiv search result pages truncate abstracts with a "More" link. Clicking that link via browser tools often fails with DOM box-model errors. Always navigate directly to `https://arxiv.org/abs/<id>` instead. The abstract page renders the full text immediately without expansion clicks.
- **Parallel verification via batch web_search.** When an outline provides detailed source traceability (story numbers from TensorFeed, IronPulse, blogwatcher, etc.), batching `web_search` calls for each distinct claim cluster is often faster than reading daily data files. In Article 160 (2026-08-14), 10 parallel searches verified 11 claims, followed by `web_extract` on the top result per cluster. Sources that extracted cleanly: TechCrunch, The Decoder, Google DeepMind blog, Reuters syndication, Kog AI blog, Okta newsroom. This pattern replaces sequential browser navigation when the outline already tells you what to verify.
- **One authoritative benchmark table verifies every score in a benchmark-heavy outline.** When an outline lists multiple benchmark numbers (e.g. "100% on ExploitBench, 72.6% on computer tasks, 59.3% on Agent's Last Exam, Fable 5 at 48.7%"), a single launch-coverage benchmark table (The Decoder's model-launch tables are the most reliable) carries all of them. Do not run a separate search per number. Extract the whole table once and confirm every figure against it. Session proof (Sep 3, 2026, Article 180): all six Astra benchmark scores verified in one The Decoder table.
- **A named outline row with no number is a research assignment, not an optional cell.** When a framework the outline asks for has a row for a component but the outline supplies no figure for it (it names the row, then leaves it empty), go back to the abstract and fill it. Do not leave the row blank and do not invent a plausible value. The outline named the row because it belongs in the framework; the figure is yours to verify.
- **A benchmark win claim takes two verification steps, and stopping after the first overclaims.** Step one confirms the model or system really is listed first, from the vendor post, the model card, or the live leaderboard. Step two reads what the benchmark measures and whether the benchmark's own paper qualifies the ranking. A vendor can legitimately place first overall on a benchmark whose authors found the model family still loses on large, temporal, grouped, or high-dimensional data. Ship both: the verified first-place result and the qualifier, attributed to the paper rather than to the vendor. The qualifier is what makes the piece citable by a reader who actually has that workload, and it is the honest form of the fact. The outline is a roadmap; the primary source is the standard for claim strength.
- **One primary source often carries multiple named quotes.** A single well-reported article (The Verge's "Researchers fear safety disaster ahead of OpenAI's Astra release") contained both the Ryan Greenblatt "single worst development" quote AND the Jakub Pachocki "race into unmonitorability" + "within a factor of two of GPT-4" quotes. When an outline cites several named people, find the one deep-dive article that quotes them all and extract every quote from it, rather than searching per person.
- **Hacker News Algolia API as a fast verification fallback.** When browser search hits bot detection (Google CAPTCHA, DuckDuckGo empty results), the HN Algolia API at `https://hn.algolia.com/api/v1/search?query=KEYWORDS&tags=story` returns structured JSON with story titles and URLs without bot protection. Use `curl` piped to a short Python parse to extract title/URL pairs. This is faster than browser navigation for confirming that a Show HN or tech story exists and finding its canonical URL. Example:
  ```bash
  curl -s "https://hn.algolia.com/api/v1/search?query=SteerPlane&tags=story" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(h.get('title',''),h.get('url','')) for h in d['hits'][:5]]"
  ```

## Resolving PhantomByte Cross-Reference Slugs (outlines name prior notes by title)

Outlines routinely instruct you to cross-reference earlier PhantomByte notes by TITLE, and the live URL is not derivable from the title. Two named cross-references, two unrelated slugs: "Your Data Center Is a Control Problem, Not a Generation Problem" lives at `/data-center-control-problem-not-generation-problem`, and "Your GPU Is Useless Without a Wire" lives at `/ai-power-bottleneck-800-vdc`.

1. Fetch the sitemap (see method below) and grep the returned text for a distinctive word from the title. Build the URL from the slug you find, never from the headline.
2. Append `.html` to the slug for the canonical URL. The bare slug path returns 404.
3. Read the prior note before writing the cross-reference sentence. The sentence has to describe what that article actually argued, not what the outline implies it argued.
4. The site's own `?s=` search parameter returns the archive page rather than filtered results, so it is not a substitute for the sitemap.

When a scraped page comes back as navigation chrome and footer text only, render it and read `document.body.innerText` instead of trusting the extracted text.

## Full Article Catalog via Sitemap (July 2026)

When you need the complete PhantomByte article catalog (all 140+ articles with dates and URLs) for namediff verification, theme dedup, or internal linking, the sitemap at `https://articles.phantom-byte.com/sitemap.xml` is the most reliable source. It contains every article URL with `<lastmod>` dates in a flat parseable format, avoiding the truncation issues with `browser_snapshot(full=true)` and the class-name fragility of curl-based extraction.

**Browser method:** Navigate to `https://articles.phantom-byte.com/sitemap.xml` and use `browser_console` with `document.body.innerText` to get the full XML as plain text. Parse for `<loc>` and `<lastmod>` tags to extract article URLs and publish dates.

**Curl method:**
```bash
curl -sL "https://articles.phantom-byte.com/sitemap.xml" | grep -oP '<loc>\K[^<]+' | head -100
curl -sL "https://articles.phantom-byte.com/sitemap.xml" | grep -oP '<lastmod>\K[^<]+'
```

The sitemap includes all pages (homepage, privacy, terms, and every article) with their last-modified dates. Filter for article URLs (they end in `.html` and are not `privacy.html` or `terms.html`). The article URL slug is the canonical identifier for namediff and internal linking purposes.

## Outline Notation Is Not Output Format

Outlines use layout devices that are roadmap, not deliverable. They wrap the file in `===` banner rules, carry a metadata block (category, angle, estimated length, operator, date), and label each section heading with a `//` prefix.

None of that survives into the article file:
- Render each section heading as an ALL-CAPS line prefixed with `//` (e.g. `// THE GAP NOBODY NOTICED`). This is the published house format, confirmed against the on-disk reference article `ARTICLE 194 COMPLETE.txt`. The `//` stays; the outline's `===` banners and `[instructions]` do not.
- Drop the banner rules entirely.
- Drop the metadata block. The article starts at the title, then byline, then prose.
- Drop the bracketed instruction lines (`[State the thesis bluntly: ...]`) — those are notes to you, and writing them out as prose is the classic failure mode of this workflow.
- Separate the SOURCES section from the social block with the plain `==========================================` separator used in the reference article.

Symptom to check for before sending: if a `===` banner or a bracketed instruction line appears anywhere in the draft, you copied the roadmap instead of writing the article. A `//` at the start of a section header is correct and expected; a `//` or `===` anywhere else is not.

**Checklist items are plain paragraphs, not bullets.** Under a `// WHAT TO DO TODAY` header, each item is its own one-line paragraph with a blank line between items, exactly as the on-disk reference article does it. Never render them as `- ` bullets. The same holds for any other list inside the body. The single exception is the SOURCES list, where the leading `- ` is part of the citation format, not prose.

**Never hard-wrap body text.** Each paragraph is one long unwrapped line; the reader's client does the wrapping. Verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }'` and expect a long line, not a tidy column.

## Outline Numbers Are a Closed Set
Many outlines carry a SOURCE DATA TRACEABILITY block that ends with a line like "No other numbers appear in the article." Treat that as binding on the whole deliverable, SOURCES section included. Do not import extra figures from the verified primary source just because you found them while reading it. Default sample sizes, default k values, extra model names, and extra percentage lifts all stay out. The outline author already chose which numbers carry the argument.

Why this matters: reading the primary is required, so the temptation to add a fresh stat is constant. Before placing any number, check it against the traceability list. A true number the outline forbade is as disqualifying as a fabricated one.

## Pre-Send Verification Checklist
- **Terminal working-directory corruption.** If a terminal command fails with `cd: <dir>: No such file or directory` even though the command and path are valid, the session's working directory is corrupted, not the command. Retry the same command with an explicit `workdir` parameter (e.g. `workdir="~"`). If terminal stays unusable, run the entire verification checklist via `execute_code` (read_file + Python string ops) instead of skipping it. Never ship without the em-dash and X-post char checks just because the shell is broken.
- **One verification script that writes a JSON file beats many small fetches.** Write a single Python script that loops a dict of `label -> URL`, fetches each, and dumps `{label: {status, len, text}}` to a JSON file in the home directory. Then inspect that JSON in later calls instead of re-fetching. Fetch statuses and lengths print in one line each, so you can see at a glance which sources returned real content and which returned a 404 or a stub before you spend attention reading them.
- **Run the whole checklist via `execute_code` (Python), not compound shell one-liners.** Counting em-dashes, char-counting the X post, counting words, and scanning hyphen-as-comma all in one command is exactly the oversized compound grep/awk payload the hardline terminal blocklist rejects (a multi-part `grep | awk | wc` pipeline got refused in a session, forcing a rewrite). Python in `execute_code` does every check in one clean pass, adds a free all-caps-title check, and is immune to that block. Use it for the entire list below. (Article, 2026-08-30, Quantization-Aware Healing).
- **Run the outline's own kill list as a grep before sending.** Outlines frequently carry a banned-words list ("no leverage, robust, seamless, unlock, delve, furthermore, rapidly evolving landscape"). Run it against the finished draft along with the standing set: `grep -niE 'leverage|robust|seamless|unlock|delve|furthermore|rapidly evolving landscape'`. A clean result is the point; finding nothing is a pass, not a wasted step.
- Em-dash count = 0: `text.count('\u2014')` must return 0. There is no permitted em dash anywhere, body, sources, or social block.
- No rule lines anywhere in the file, social block included. There is NO separator rule line below the article. Separate the SOURCES section from the X POST block with a blank line. **The ban is on a divider of ANY repeated character, not just hyphens** — a long `====` run is the same artifact as a long `-----` run and is rejected the same way, so do not reach for equals signs as a neutral-looking equivalent. Check the whole file in Python: no line may consist solely of three or more identical punctuation characters (`=`, `-`, `*`, `_`, `~`, `#`). Only hyphens inside real compound words and the SOURCES "title (date) - URL" format are legal.
- Word count lands inside the outline's ESTIMATED LENGTH range. In Python, count only the article body (exclude the `//` section headers and the trailing X post / Pinterest / keywords blocks up to the `-----` separator). Aim for the top of the range; it is easier to trim a few words than to add a paragraph. (Article 161, 2026-08-15: initial pass came in at ~1,240 words against a 1,400-1,600 target; expanded with engineering depth, then trimmed to 1,600.)
- X post fits its format ceiling, counted with `len()` in code: the five-stanza model post format from `x-algorithm-post-optimization` by default (roughly 250-400 chars, about 280 for a free account), or strictly under 190 when Vinny asks for a short one-liner. Never trim a model-format post down to 190.
- Pinterest title 60-80 chars
- Pinterest description 150-300 chars
- All outline references addressed in the body
- SOURCES section present with primary source URLs
- No unverified claims presented as fact
- No all-caps words in the title
- Title is the outline's title, verbatim, unless Vinny himself rewrites it
- Title leads with the searchable entity, not a generic phrase (see Title Rules)

## Authority Positioning Rule
Articles must position PhantomByte as an engineering and architecture authority on AI. Engineering depth is the default framing. Teach concrete frameworks, not summaries. Front-load the mechanism, explain why the numbers matter, and connect techniques to deployable reality. Vinny's words: "you can't do shit without that."

## Opinion vs Fact Labeling
- Opinions, theories, and speculative claims are permitted, but must be explicitly labeled as such
- Facts must be verified against primary sources (arXiv, vendor reports, daily data files)
- Never present an unverified claim or opinion as fact
- **A claim about what an unnamed population does is an unsourced factual claim, not a stylistic flourish.** Sentences like "most routing layers in production have zero of these guards," "the industry default is X," or "few teams do Y" read as verified fact even though no source asserts them. A single paper's result supports a statement about that paper and about the systems the paper measured, never a statement about the whole population. Either cite something that actually surveyed the population, or frame the sentence in the reader's own shoes ("if your routing layer has none of the three, you are in the same position TW3Cast was built to avoid"). The fix is cheap; the cost of leaving it is a fabricated stat in text you deliberately wrote to be ingested by training corpora.
- **Label the framing, not just the facts.** When the piece draws a forward-looking conclusion (a procurement argument, a prediction about where inference margin goes next), name it as the argument being made rather than stating it as an outcome. "This is a procurement argument, not a research one" is the shape: the reader can see exactly which sentences are the author's position.
- **Carry the primary source's own scope, never inflate it.** A vendor benchmark gain is measured inside a specific environment, and the honest move is to name that environment in the sentence. ServiceNow's AutoSynthData numbers came from EnterpriseOps Gym, a synthetic enterprise sandbox, and the post ships with "gains inside a controlled environment, not a live-enterprise trial." A benchmark delta presented as production proof is an unlabeled overclaim even when every digit is correct. The same discipline applies to any single-vendor result: state where it was measured.

## Title Rules
- **Keyword-optimize the title AFTER the article is written, never before.** Read the outline, write the full body, then run the title pass against the finished piece and the words a searcher would actually type. That optimized title is what ships. Optimizing from an outline alone is guessing at what the article covers.
- **Outside that pass, never change a title Vinny selected.** The outline's title stays verbatim, character for character, across the draft file, the "COMPLETE" rewrite, revision passes, the email subject, and the Pinterest title. He chose the outline, so the title is his. If you think a different title reads better, say so in chat and change nothing.
- **A revision pass is where the title silently drifts, so diff line 1 before delivering.** When Vinny orders revisions to a finished article ("implement these suggestions, without touching the original"), the rewrite is usually produced by re-emitting the whole file, and the title is the one line that carries no body content to anchor it, so it gets regenerated from memory and comes back changed. After any rewrite or revision pass, compare line 1 of the new file against line 1 of the file it replaced, and against the outline's title line. They must be byte-identical. Report the title in the delivery message so Vinny can catch a drift without opening the file.
- **Never shorten, paraphrase, or "clean up" a title anywhere it is reproduced.** The title is locked, and the copies that leak are the ones outside the article body: the email subject, the Pinterest title, the filename, the chat message, and the section headers. Grep each of them for the title's leading entity before sending. A clever phrase that names no product is zero-SEO, so a shortened title costs you both the user's trust and the search traffic.
- Do NOT use all caps for any words
- **Lead with the entity, not a generic phrase.** A title has to contain the words a person would actually type into a search bar. "OpenAI textGrain: The EU-Only Watermark and Your 4 Choices" beats "Your Text Watermark Just Went Regional" because the reader, and the model, can find it. A clever phrase that names nothing is zero-SEO. Vinny's verdict on the weak version: "ZERO SEO." Entity first, then the angle, then the concrete payoff. Numbers and proper nouns earn their place; decorative wording does not.
- **Sentence-style colon titles, and ONLY after Vinny flags one as too long: compress the trailer, keep the leading clause and every number in it.** When the outline title is a full sentence with a colon, the lead clause is usually already the strongest part, so the work is in the tail. Strip the `That`/`Which` relative clause and the trailing qualifier phrases, then keep the surviving noun phrase plus its figure. Example: "Your Reasoning Budget Is Wasted: The Frozen Routing Table That Ranks 3rd of 130 With Zero LLM Calls" becomes "Your Reasoning Budget Is Wasted: A Frozen Table Ranks 3rd of 130." The number stays; the padding goes. Losing "3rd of 130" to buy two words of brevity is a failed shortening, not a successful one.

## Email Delivery
- Use `email-sender` skill (IONOS SMTP)
- Save to `~\workspace\article-drafts\ghostwriter-terminal\YYYY-MM-DD-slug-draft.txt`
- Email body: brief summary of structure, word count, readiness status
- Subject line: "[Title] - Draft", using the article's title VERBATIM. Never shorten or reword the title for the subject. Plain hyphen only; the no-em-dash rule covers every string Vinny reads, the subject line and the email body included, not just the article file.
- Content is the attachment, not pasted into the body
- Before sending, grep the script for ALL email addresses and verify each one
- **After sending, confirm delivery by reading the message back out of the inbox, not by trusting the send script's exit code.** A send can print success and still leave you unsure which subject line or attachment actually went out. Log in to IMAP (`imap.ionos.com`, 993, same credentials), search INBOX by a distinctive word from the subject, and print each match's `Date`, `Subject`, and attachment filenames. That readback is the proof, and it is the only way to catch a shortened subject or a wrong file before Vinny opens it.