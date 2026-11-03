---
name: article-syndication
description: Cross-post or promote published articles off-site (dev.to, daily.dev, X, Pinterest).
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Distribution, Syndication, Backlinks, SEO, Cross-Posting]
---

# Article Syndication to External Platforms

Take a published article and produce a platform-correct copy for a third-party publishing site. The point is a second audience plus a followed link back to the original, without the copy ever competing with the original in search. Applies to dev.to, Medium, Hashnode, and any platform where the article is republished rather than linked.

Related: `phantom-byte-writing-style` governs the voice (no dashes of any kind, section-header style). `phantombyte-distribution` covers on-site SEO/GEO. This skill covers the off-site copy only.

## When to Use

- "Write me a dev.to post for this article" / "cross-post this to [platform]"
- "Which of my articles should I post about on [daily.dev / X / Pinterest]?" / "write me a post for it that links to the full story"
- "Write me a HackerNoon post for the following: <URL>" / any platform submission for a named source
- "How often should I post to dev.to?"
- "Are those good backlinks?" / "Does that link count?"
- "Write me a bio for [platform]"
- Any request to republish articles.phantom-byte.com content elsewhere

## Procedure

### Step 1: Fetch the source article in full

Use scrapling, not web_search, not curl to search engines. Read the whole body before writing anything: headline, subtitle, section structure, code blocks, tables, numbers.

**The source Vinny names is the ONLY source, and this rule overrides every shape, template, or example elsewhere in this skill and in any other skill.** When he writes "write me a [platform] post for the following: <URL>", that URL, and only that URL, is the material. Do not go find a bigger or fresher dataset behind it, do not re-run a scanner, do not re-measure a number, do not pull a different artifact from a project folder, and do not swap in figures he did not name. If the named source carries no numbers, the post carries no numbers. Discovering that a larger dataset exists is not a reason to use it; it is the failure mode this rule exists to stop. If a wider set genuinely looks necessary, say one line and stop. Never spend the task on work he did not order, and never present unrequested analysis as diligence.

### Step 2: Adapt, do not rewrite

The syndicated copy is an adaptation. Keep the argument, the numbers, and the code blocks. What changes:

1. **Frontmatter for the target platform.** For dev.to: `title`, `published: false`, `description`, `tags` (max 4), `canonical_url`. Hand it over unpublished so Vinny reviews it.
2. **Canonical URL is mandatory.** Point it at the original articles.phantom-byte.com URL. This is the entire reason cross-posting is safe: it tells Google the original is authoritative. Without it the copy competes with your own SERP.
3. **Rewrite every relative internal link to absolute.** Source articles link to sibling Notes as relative paths (`some-note.html`). Left as-is they resolve against the new host and 404. Convert the ones worth keeping to full `https://articles.phantom-byte.com/...` URLs or cut them.
4. **Add one or two in-body links back to the original and to related Notes.** See the backlink section below for why body links and the canonical tag are not the same thing.
5. **Strip the subscribe block, the coffee link, and the catalog pitch.** Re-point the footer at the original article and the product catalog in one closing paragraph.
6. **Keep the voice rules.** No em dashes, en dashes, or hyphens used as dashes. Bold short section headers.

### Step 3: Cadence

Two to three posts per week, spaced every 3 to 4 days. Three is the ceiling. A batch published the same day reads as spam to both the algorithm and the community. For a large archive, spread it chronologically and treat it as a long drip rather than a dump.

On engagement-ranked platforms the hour matters more than the volume. The front page is decided by reactions and comments in the first couple of hours, so post mid-morning Eastern on a weekday.

Publish the original first and let it index before the copy exists. Days later, not minutes.

### Step 4: Backlink value, verified not assumed

Do not answer "are these good backlinks" from reputation. Fetch a live article on the platform and read the `rel` attribute on an in-body outbound anchor. Run `scripts/check-link-rel.py`.

Verified result for dev.to (Forem): in-body outbound links carry only `rel="noopener noreferrer"`. No `nofollow`, no `ugc`, no `sponsored`. They are followed links, which is unusual for a user-content platform and is why dev.to has real SEO reputation.

What that is worth, honestly:

- **Domain authority is genuinely high and the domain is indexed aggressively.** A followed link from a body is a legitimate signal.
- **Sitewide and templated links carry almost nothing.** Sidebar, feed, bio, and post-template links are not the value. Per-post body links are.
- **The value is conditional on engagement.** A post with single-digit views passes nearly nothing. Two posts a week that get read beat ten that do not.
- **Canonical and a body hyperlink are different things.** Canonical is metadata that protects your SERP. A body anchor is an actual link. Use both on every cross-post.

Re-verify per platform. Attribute behavior changes.

### Step 5: Platform bio

The platform bio is a keyword surface, not a personality statement. Name the subjects the posts are actually about, then give one reason to click through. Write as a single sentence or two, roughly 150 to 180 characters so it fits under a 200-character cap.

### Step 6: Link-and-mention posts (daily.dev, X, Pinterest, LinkedIn)

Not every platform wants the article. Some want a short post that carries the link back to the original, and those are a different deliverable from a syndicated copy: no canonical tag, no full body, and the platform's own algorithm decides reach. Produce ONE package file per article holding every version, so nothing ships as a loose paragraph in chat.

**Pick the article by what is already published on the target platform, never by freshness alone.** Fetch the target profile, list what is already posted, and choose an article whose subject is untouched by all of it. Then confirm the article is not already in the target board or feed. A post that repeats a subject already posted is worth nothing to the platform.

**The strongest pick is the article whose prediction today's news just confirmed.** A news hook that ratifies something the archive already argued gives the post a real reason to exist and makes the archive look prescient rather than reactive. When a daily data file is in the task, search it for that ratification before choosing.

**Use today's data file for the new facts, and attribute them by outlet.** Pull the specific figures, dates, and outlet names into the post, and state plainly which facts are new. Do not invent a hook and then hunt for a source to prop it up.

**Per-platform shape:**
- *daily.dev*: clickable title plus a short body that stands alone, then the link. Tag list at the end.
- *X*: the version that fits the character budget. Count it before delivering and count the URL as 23 characters (see `x-algorithm-post-optimization` for the scoring rules).
- *Pinterest*: always name the board and say why it fits, drawn from the live board list in `pinterest-academy`, and state that the pin is not a duplicate.

**Fetching the target profile:** `scrapling extract fetch "<profile-url>" out.html --network-idle --wait 8000`. A plain `get` returns the page shell with the post list unrendered; the stealthy browser fetch renders it. Grep the saved HTML for the post permalinks to enumerate what is already published. On daily.dev the permalinks look like `/posts/<slug>--<id>`; grab every one before choosing.

**daily.dev renders the profile as a Next.js SPA, not as post permalinks.** A stealthy fetch returns the page shell plus an embedded `__NEXT_DATA__` JSON blob; the visible post titles are in the rendered text (strip tags and dedupe lines), and there may be no `/posts/<slug>--<id>` permalinks in the HTML at all. Enumerate by extracting the visible post titles in order, not by grepping for a permalink pattern, so a zero-permalink page is not misread as a zero-post page.

**When Vinny asks for the "words to mask the link" with SEO in mind:** the deliverable is the post body PLUS the exact anchor-text phrase to hyperlink, never the raw URL as the anchor. The anchor must carry the target article's keyword phrases (its subject vocabulary) so the link passes them; give a shorter alternate anchor for length-limited platforms. State that the anchor is the hyperlink text on any platform where markdown links or link cards are supported.

**Scrapling import note:** the sandbox interpreter in `execute_code` does not have scrapling. Run scrapling scripts from `terminal()` with `~/venv/bin/python`, where scrapling is installed. Also: scrapling's `.text` can come back empty on a JS-rendered page even when `.body` is full, when `page.text` looks blank, read `page.body` or strip tags from it instead of concluding the fetch failed.

## Pitfalls

- **A profile page fetched without a browser is not evidence the account is empty.** An unrendered shell shows zero posts; a stealthy fetch of the same URL shows all of them. Never conclude "nothing posted yet" from a plain fetch.
- **Never assert a platform's link attributes from reputation.** "UGC platforms nofollow everything" is false for dev.to and false elsewhere. Probe a live article first.
- **Check every factual absolute in the finished draft against the primary source before delivering it.** A mechanism list, a platform count, or a record string that merely sounds right is the sentence a technical reader checks first, and one wrong clause makes the numbers around it suspect too. Re-read the artifact, do not trust the draft's own paraphrase of it.
- **Match every time phrase to the artifact.** "Two weeks ago" over a scan run two days ago is a false statement in the first line, and it is the kind of error a reviewer catches before any of the analysis.
- **Never ship a syndicated copy with relative internal links.** They resolve against the new host and land on 404s.
- **Never omit `canonical_url`.** Omitting it turns your own syndication into duplicate-content competition against articles.phantom-byte.com.
- **Never publish the syndicated copy through the API or UI on Vinny's behalf.** Hand him the file with `published: false`.
- **Do not strip the cross-references to past Notes.** They are the serial continuity, and they are what the syndicated copy adds beyond a plain repost.
- **Do not dump an archive.** Cadence is the constraint, not supply.

## Support Files

- `scripts/check-link-rel.py`, fetch a live article from any platform and print the `rel` on each in-body outbound link. Run this before answering any question about whether a platform's links count.
- `references/devto-format.md`, dev.to frontmatter fields, tag rules, and the verified link-attribute result.
- `references/dailydev-format.md`, daily.dev post shape, the character budget for the title and body, tags, and how to enumerate what a profile has already posted.
- `references/hackernoon-format.md`, HackerNoon Story Settings fields (title 60 to 100 characters, meta 120 to 160, exactly 8 tags at 30 characters each, First seen at, TL;DR cap), the rejection list worth pre-checking, submission mechanics, and the pre-send verification pass for a finished draft.
