---
name: devto-article-generator
description: Use when Vinny asks for a dev.to article.
category: content-swarm
---

# dev.to Article Generator

## When to Use

Load this when Vinny asks for a dev.to article or post, usually "write me a short article for dev.to similar to what we do with the LinkedIn skill," and names an `outlineN-*.txt` plus the site to match. Also load it when he asks to repurpose one of the daily outlines for a developer platform.

Not this skill: a LinkedIn post (`linkedin-post-generator`), the full site article (`phantombyte-content-writing`), or X posts (`x-algorithm-post-optimization`). The three share voice and fact-check discipline; they differ in length, format and how the file is delivered.

## Read First

- `phantom-byte-writing-style` governs every word. Second person, short declarative paragraphs, no em dashes or any dash as punctuation, no hedging, no invented experience.
- The live site for tone, not the style skill alone. `https://articles.phantom-byte.com/sitemap.xml` lists the archive newest first; scrape two recent notes from the same category and slice from the `// field note NNN` marker. Read the first few thousand characters of each, not the whole archive page.
- The named outline file in `.../<user>/OneDrive/Desktop/TODAYS DATA FILES/`. Its own body carries verified numbers and a section skeleton, and its `WHAT TO DO TODAY` block is usually already the checklist the post needs.

## Length

An outline is written for a 1,800 to 2,200 word site article. A dev.to piece is the compression of it, roughly 800 to 1,000 words, and that is a working range rather than a target to report against. Keep the hook, the mechanism section that explains why the thing behaves this way, the named framework as a numbered list, one context section with the strongest supporting number, the action checklist, and the closing question. Drop anything that only exists to pad a site article: timelines, second papers, restated claims.

Report the actual `wc -w` and `wc -m`. Do not write the site length because the outline says so.

Trim by measuring per paragraph, never by feel. Print an index, a word count and the first 70 characters of every paragraph, choose the fat ones by number, then rewrite the finished file in one call. A chain of `patch` calls on an article file is how paragraphs get fused: a patch whose match ends at a paragraph boundary takes the blank line with it, and a mis-scoped patch can duplicate a section header outright. Two or more cuts means one `write_file`, not four patches.

```python
from hermes_tools import read_file
import re
raw = re.sub(r"^\s*\d+\|", "", read_file(path)["content"], flags=re.M)
for i, p in enumerate(x for x in raw.split("\n") if x.strip()):
    print(i, len(p.split()), p[:70])
```

Cut a repeated idea before you cut a number. When the numbered framework and the checklist make the same point, the framework loses it: the checklist is the part he acts on, and a duplicated action reads as padding at this length.

## File Shape

The article file holds the BODY ONLY. No title line, no YAML front matter, no metadata block. dev.to puts the title in its own field, so a title line pasted into the body renders as a duplicated first paragraph. The title, tags and posting steps go in the email body and the report.

Markdown is correct here, unlike the site article. dev.to renders it, so use `## SECTION HEADER` in ALL CAPS, one list for the numbered sequence, and one fenced code block for the visual break. No horizontal rules, no bold markers around body text, no tables.

- Visual break: ship at least one labeled snippet by default, on every piece, including a business or industry analysis. dev.to's readers are individual contributors, backend engineers and hands-on builders: they follow budgets, but they trust a piece that shows the mechanism, and a market story with no artifact reads as a press release to them. Two shapes cover almost every outline. A mechanism block sits in the mechanism section and shows the request path in code (a routing policy that compares a model's probability against a configured threshold). A criteria block sits where the article discusses evaluation and shows the shape of the file that defines a good output (what a session must do, what makes it fail). Both are in `references/illustrative-code-anchors.md`, copy and adapt rather than composing from scratch. Prefer the code block to an ASCII diagram: box drawing wraps badly on a phone while a code block scrolls in dev.to's renderer. Label it illustrative in the sentence above it, keep it around ten lines, and state any deliberate omission in the paragraph after, or a reader reads it as a bug. Then make the block earn its place: the paragraph after it names the one line that matters ("that number is your token bill in one place") and why changing it is invisible without the eval set. A snippet with no sentence pointing at the important line is decoration.

- Title: front-load the claim, keep it under roughly 55 characters so it survives a card, and put the surprising number or the wrong assumption in it. A full site title with a colon and a subclause does not fit.
- Tags: four, lowercase, audience-level rather than news-level, and he names the set when he revises. Default for an inference or serving piece is `ai, devops, architecture, performance`: the role, the domain, the workload, and the constraint. Reach for `llm` only when the platform tag needs the technology named and nothing better fits.
- Canonical URL: leave it unset until the PhantomByte version of the piece is live, then point dev.to at it. Never invent a URL to fill the field.

## Structure That Lands

1. Hook on the number, two or three sentences, then the cost to the reader. The counter that lies is a better opening than a setup question.
2. The experiment or mechanism section, naming the instrument that made the finding visible and defining the one term a reader will not know.
3. The accounting section: what the wrong measurement does to the reader's dashboards, autoscaler and budget. That is the part that makes it their problem.
4. The named framework as a numbered list, one line each, then the ordering rule in prose. Give the reader a line they can quote in a design review.
5. Why this is the common case, with one verified scale number and one sentence on load-shape variance.
6. The checklist, five items, each a thing to do this week rather than a thing to believe.
7. The closing question in second person.

## Revision Pass

He sends revisions back as a bulleted critique, sometimes titled "Vulnerabilities to Fix," sometimes a plain list of observations. Every bullet is an order. Apply all of them in one pass, re-verify, and email the revised files with a subject that says "revised." Do not answer a revision with an explanation of why the draft was fine.

- A bullet asking for "tactile artifacts," "a code or config anchor," or "how it works under the hood" means one thing: add a mechanism section that reduces the system to named parts (gateway, policy, trace store, eval sample, in that order), plus a labeled snippet of each structural artifact the article already mentions by name. More adjectives is not the fix.
- A bullet about audience alignment is a request to shift the verbs. Speak to the builder who will configure the thing, and give them one line they can repeat in a design review ("The model is a parameter. The threshold is the architecture."). Turn at least one checklist item into something an individual contributor can do this afternoon rather than a budget exercise for a manager.
- Keep every number that survived the fact check. A revision never buys permission to drop figures, and the business spine stays intact even when the feedback is all about engineering depth.
- The length range yields to the revision. Adding a mechanism section and two snippets took a 1,034 word piece to 1,277: tighten the prose in the same pass to hold the growth down, then report both counts and name what caused the increase. Never refuse requested material to defend a word target.
- Label every block illustrative above the fence, and repeat in the report that the snippets assert structure and never results.
- Re-verify after the rewrite, not before: balanced fences, every python block passing `ast.parse`, dash scan, and the spell check. An edit is exactly when a block breaks.
- Bump the report title to a revision label and add a WHAT CHANGED section that names each requested fix and the section it landed in. He should be able to confirm compliance by reading the report alone.

## Fact-Check Discipline

Every figure gets re-read at the publisher, never taken from the data file. That step catches drift and stale links.

- For an arXiv paper, the `/abs/` abstract repeats every headline percentage, the submission date and the author count. `page.css("blockquote.abstract")[0].get_all_text()`. Confirm each figure the outline attributes to the paper in one pass.
- Carry the paper's conditionals verbatim into the post. "Coalescing delivered every call unless cancellation had already aborted the running execution" is the sentence that makes the recommendation honest; dropping the clause turns a measured result into a free win you cannot defend.
- A figure you derived by division (tokens per day over daily users) is arithmetic, not a quote. Label it in prose with "which works out to about" and keep the two published inputs in the same paragraph so a reader can redo it.
- A 404 on a data file link is a stale slug, not a missing story. The 404 page's most-read module usually carries the live URL. See the linkedin-post-generator skill's web research notes, in the section on a publisher URL that 404s.
- Keep the paper's own hedge and the publisher's attribution. No inline sources, links, paper names or author names in the body; the traceability lives in the report.
- A publisher page carrying an updated timestamp has drifted since the data file was written. Reaction numbers go first: a stock move the outline quotes can be gone or restated on the live page, so re-read it and drop the outline's figure rather than carrying a number the article no longer states.
- A figure that is simply absent from the page on fetch is a dropped claim, not a scraping problem. Confirm each outline number is actually present before writing it, and put every absence in the report's NOT CLAIMED list with the reason.
- When the outline paraphrases a detail from the source, take the publisher's wording and not the outline's summary. A looser paraphrase in the outline ("dietary preference") is usually wider than the source ("vegan preference"), and the narrower word is the accurate one.
- Cross-references to earlier PhantomByte notes stay in prose with no links. Naming the prior note is continuity; linking it is a source citation the house style forbids.

## Delivery

1. `SCRATCH=$(mktemp -d /tmp/hermes-devto-XXXXXX)`. Never a fixed path.
2. Write the body to `devto-post.md` and a dated report `devto-article-report-YYYY-MM-DD.txt`. The report carries the title, the tags, the measurements taken from the attached file, the fact check per claim, a NOT CLAIMED list, and the posting steps. Text report layout is ruled sections, ALL-CAPS headings, indented blocks, blank lines, and no hard wrapping. Article 14 of the constitution applies to every line of it; author each paragraph as one unwrapped line and the `awk` max-length check will pass honestly.
3. Verify before sending: `wc -w`, `wc -m`, a grep for `[\x{2013}\x{2014}]` and for ` - `, the `awk` max-length check, and pyspellchecker over a word LIST, sanity-checked first against `"teh receve"`. Also count the fence lines: an odd number of ``` markers means a block never closed. Parse every python block, so the snippet cannot paste as a syntax error. Expect `vllm`, `prefill`, `autoscaler`, `idempotency`, `workflow`, the split halves of hyphenated compounds (`multi` from `multi-agent`), and model names to flag; verify those by hand and change nothing.
4. Email through `email-sender` to `hello@phantom-byte.com` with both files attached. The subject states what it is and stays under roughly 60 characters so the IMAP match does not fold.
5. Read the INBOX copy back with `scripts/verify_recent_headers.py --count 5` and confirm both attachment filenames on the newest message. Report only what it printed.
6. The Telegram notice is a doorbell: what was sent, the subject, title, tags, and the one-line fact-check verdict. Do not paste the article.

## Pitfalls

- Do not put the title on line one of the article file. It duplicates in the editor and he has to delete it before publishing.
- Do not carry the outline's `// SECTION HEADER` format onto dev.to. Markdown H2 in ALL CAPS is the platform form; `//` reads as a comment artifact.
- A `patch` that lands near or across a fenced block can fuse the block's last comment line into the next statement, and the snippet then reads as one long comment with no `policy =` line at all. After any edit to an article file, re-read the region and confirm the fence markers are balanced and every python block parses. The same hazard fuses a paragraph onto the one below it when the match ends at a blank line, which is why two or more cuts belong in one `write_file`, not a chain of patches.
- Before rewriting an article file this session already wrote, `read_file` it in full. `write_file` refuses a stale overwrite, and one read is cheaper than a refused write plus a retry.
- Do not invent a code block, a config snippet or a benchmark table to make the piece feel native to dev.to. If a snippet is needed, it is illustrative and labeled as such, never presented as output of the paper's experiments. A labeled illustrative gateway pattern he asked for is not the same thing as a fabricated benchmark; ship the former, never the latter.
- Do not sell one remedy as the fix. These outlines usually carry three with different failure modes, and the value is the ordering rule, not a favorite.
- Do not drop the numbers to save words. Cut the explanation around them instead; a dev.to reader will forgive brevity and not vagueness.
- Do not cite an aggregator's summary line, and do not quote a figure you could not reopen at the publisher. If the publisher page will not load, drop the figure or attribute it to the entity that disclosed it and note the gap in the report.
- Fix hyphenation by hand, never with one global find and replace. A bulk `single agent` to `single-agent` pass also rewrites the noun usages, so "beat the single agent" becomes "beat the single-agent" and the file needs a second corrective pass. A compound takes a hyphen as a modifier (`single-agent baseline`, `multi-agent orchestration`) and none as a noun (`beat the single agent`, `the only arm to beat the baseline`); write the form you want the first time, or re-read every hit in context after replacing.
- Never repair wrapping with a mechanical line-join over a ruled report. A joiner cannot tell a wrapped paragraph from a rule line or a heading, so it fuses `----` plus the heading plus the body into one line and leaves the report worse than the wrapping did. Author every paragraph unwrapped in the first write, check with `awk '{ if (length($0) > m) m = length($0) } END { print m }'`, and if the check fails, rewrite the offending block by hand instead of joining lines.
