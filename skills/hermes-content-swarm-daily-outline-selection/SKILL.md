---
name: daily-outline-selection
description: Use when Vinny drops article outlines and asks which to write next. GEO/architecture-first selection, not news-urgency selection.
trigger: "Vinny provides 2-3 article outlines and asks which to write next, or which article to prioritize."
category: content-swarm
---

# Daily Outline Selection

Workflow for when Vinny drops 2-3 article outlines and asks which to write next.

## Gate: this workflow runs only on an explicit ask

**A dropped outline file is not an order.** When outlines arrive as attachments with no question attached (no "which do I write", no "rank these", no "pick"), the correct move is to say nothing was asked and ask what he wants, or simply wait. Do NOT start fetching the site, ranking, or writing anything on the inference that the ritual was implied.

**Nothing gets written to his machine without the request.** Step 6's file write to the agent-knowledge-base repo is part of the workflow, not permission to run it. No decision file, no commit, no push, and no scratch writes into any tracked repo until he asks for the selection.

If the ask is ambiguous, one short question beats a silent run: "Want the selection, or something else with these?"

## The Selection Lens (learned 2026-08-16)

**Vinny's goal is maximum visibility via GEO (Generative Engine Optimization) and long-term architectural authority — NOT short-term traffic spikes.** Optimize for the metric Vinny explicitly named, not for clickbait recency.

The wrong lens (which caused a real miss on 2026-08-16): ranking a LiteLLM supply-chain breach post above the execution-layer architecture split because the breach was "urgent" and "high-hook." Google corrected this. A news-recap incident post decays the moment patches land and credentials rotate. It is NOT the authority signal.

The correct hierarchy — in order of weight:

1. **GEO rewards structural standards, not news recaps.** Does the outline define a permanent engineering framework (a reference blueprint) that AI engines will index and cite for years? Or is it a time-stamped incident recap? Prefer the blueprint. Security panic and breaking-news urgency decay fast; frameworks are indexed for years.

2. **Building a core thesis is not content cannibalization.** If an outline *synthesizes* prior PhantomByte notes into a production blueprint and adds a new primitive (a hardware spec, a new model, a new pattern), it is NOT duplicate content. Unifying previous concepts into one coherent blueprint is how domain authority compounds. Only reject true overlap (repeating the same standalone claim with no new primitive or synthesis).

3. **It must fulfill the core engineering mandate.** Vinny's mission: show nobody can accomplish anything in AI without core engineering and architecture. Prefer the outline that changes how developers *design* systems (architecture, routing, compute, code level) over one that is incident-response remediation (rotate keys, check dependencies, run an audit). The architecture piece directly proves the mandate; the incident piece is maintenance.

4. **The architecture outlasts the vendor.** Do not discount an outline because it names a specific current product (e.g. Nvidia Nemotron 3.5 Lightning). That product is merely the real-world proof of concept for a *permanent* shift in runtime design. The timeless pattern (e.g. cheap execution model + frontier reasoning model + router) stays relevant no matter who wins the benchmark race next year. Judge the underlying pattern, not the vendor.

5. **Category balance is the tiebreak.** After the four lenses, look at what category the last 5-7 notes were. Four straight notes in one category means some other spine of the site has been idle for over a week, and a strong outline in the starved category wins the tie. A daily serial that keeps its infrastructure, engineering, and security spines all fed reads as authority across the whole field; one that runs four security notes in a row reads as a security blog.

## Steps

1. **Load the live site and the sitemap.** Both come through scrapling into this run's scratch dir:

```bash
SCRATCH=$(mktemp -d ~/cache/scratch/ph-XXXXXX)
scrapling extract get "https://articles.phantom-byte.com" "$SCRATCH/home.txt"
scrapling extract get "https://articles.phantom-byte.com/sitemap.xml" "$SCRATCH/sitemap.txt"
```

Note the note count the console prints ("NOTES: N"), the latest title, and the recent 5-7 titles with their categories. The homepage lists only a subset and can lag, so the sitemap is the real archive: the full slug list, 220+ articles, each slug a compressed statement of its topic.

2. **Grep the slug list for the topic keywords of every outline before ranking anything.**

```bash
grep -o 'https://articles.phantom-byte.com/[^ ]*' "$SCRATCH/sitemap.txt" | grep -v -E '/$|privacy|terms'
```

Then filter those slugs per outline keyword set: voice, speech, audio, determinism, reproducib, arxiv, preprint, review, verif, research, latency, train, gpu, cluster, energy. This converts "is this a coverage gap?" from a guess into a count, and it is the number to check the outline's own gap claim against.

3. **Read each outline** — extract core thesis, category fit, data density, cross-reference potential, actionability.

4. **Rank on the four lenses above**, in the order given: (1) structural framework vs news recap, (2) genuine synthesis vs true overlap, (3) systems-engineering mandate fit, (4) timeless pattern vs vendor-specific claim. Then apply lens 5, category balance, as the tiebreak.

5. **Deliver pick + why + publishing order.** Explicitly state which metric you optimized for and why. If the pick looks "less urgent," say why GEO/authority outweighs urgency. Answer with one pick, one order, and the reasons, never a menu of trade-offs.

6. **Save the decision to the agent-knowledge-base repo** at `/mnt/c/Users/<user>/agent-knowledge-base/lessons-learned/outline-selection-YYYY-MM-DD.md`. The repo lives on the Windows side; that mount path is how WSL reaches it. `git add` and `git commit` the file, then attempt `git push`. If the push is refused for repository access rights, the local commit is the deliverable: say so in one line and stop.

## Pitfalls

- **Optimizing for short-term traffic instead of GEO/architecture.** The #1 failure mode. A breach/incident post gets clicks now and decays. A framework post gets indexed and cited for years. Vinny asked for the latter.
- **Treating synthesis as cannibalization.** Unifying prior notes into a production blueprint with a new primitive is authority-building, not duplication. Do not reject it for "overlap" with an earlier note.
- **Discounting a pattern because it names a vendor.** The product is proof-of-concept; the architectural pattern is the durable asset. Judge the pattern.
- **Always load the live site** (changes daily). Confirm against the sitemap, not just the homepage index.
- **No pure policy/industry gossip without an engineering angle.**
- **A news hook is a bonus, not the deciding factor.** It only wins a tie after the four lenses are applied.
- **Trusting an outline's own coverage claim.** Every outline arrives asserting its gap, in the form "the archive has no voice note at all" or "thin category, 3 notes in the archive." Verify both directions against the sitemap slugs before reasoning from them. A claimed vacuum can be real (zero voice, zero determinism across 224 URLs) and a claimed thin category can already be saturated by notes that never use the outline's own keyword, e.g. four verification notes hidden behind slugs like `the-verification-bottleneck-...` and `verifying-agents-...`. The overlap test is a slug grep, not a reading of the outline's self-description.
- **Ranking without pulling the recent category run first.** Three good outlines ranked in isolation produce a pick that piles onto a category already covered four days running. Get the last 5-7 titles and their categories before ranking, not after.
- **Answering with options instead of a pick.** He asked which one and why. A menu of trade-offs hands the decision back to him and stalls the pipeline. One pick, its publish order, and the reasoning behind it.
- **Running the workflow off a bare attachment.** Seeing outline `.txt` files arrive without a question is not a request for selection. Inferring the ritual and starting the fetch, the ranking, and the repo write is acting on your own initiative, and it gets interrupted. Wait for the ask.
- **Ranking an outline whose topic is already written or already published.** Before ranking, check the outline topic against the published slug list AND against what is already drafted or written: the last few days of `outline*.txt` in his TODAYS DATA FILES folder, and `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/` for `ARTICLE <n> COMPLETE.txt` and `*-draft.txt`. A batch can contain a repeat of a topic whose article was written the evening before and published the same day; that outline is dead on arrival and must be named as such instead of ranked.
