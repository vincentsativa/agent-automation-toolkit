---
name: ghostwriter-terminal
description: |
  Vinny gives you a solid outline. You write the story. Single pass: outline → article → social post, Pinterest title/description, quick keywords.
  No style study, no site reading. Research only when Vinny explicitly requests it.
---

# Ghostwriter Terminal

> **Trigger:** Any request like "write me this story", "write this article", "ghostwriter", or "write the tutorial" that includes an outline file path.

## Workflow

1. **Read the outline** Vinny gave you
2. **Write the article** (no em dashes)
3. **Add:** X post, Pinterest title (60-80 chars), Pinterest description (150-300 chars), quick keywords
   - **X post must follow `x-algorithm-post-optimization`**: optimize for reply, retweet, share_via_dm, dwell, and out-of-network retrieval. Hook earns the second line. End with a reason to reply. Self-contained for a stranger. Use the topic's actual vocabulary. Avoid bait-and-switch hooks (triggers `not_interested`). Load that skill before writing the post.
   - **The post SHAPE is governed by that skill's MODEL POST FORMAT section, not by a char cap here.** That format is five stanzas (hook, fact stanza, take carrying the question, closer), 150 to 280 characters, with 280 the hard ceiling on a free account, and the section states it is the standard for every post that skill produces. This file does not restate it; read it there. The 190-char and 3-part 180-char budgets below apply ONLY to the single-blob one-liner variant, not to the five-stanza shape. To fit the five-stanza shape under 280, trim the fact stanza first: write `%` instead of the word `percent` and cut filler adjectives, but keep every number and proper noun. Never trim the hook's punch, the take's question, or the closer.
   - **When writing the single-blob variant, budget in 3 parts, not one 190-char blob.** The post is hook + body + reply-ask, and each part gets its own budget:
     - Hook (earns the second line): ≤ 60 chars
     - Body (the claim, self-contained for a stranger): ≤ 90 chars
     - Reply-ask (reason to reply): ≤ 30 chars
     - Total target: ≤ 180 chars, leaving a 10-char margin under the cap.
   - **If a part is over budget, cut that part, never the whole post.** The reply-ask is the highest-value engagement in the algorithm (5.0 × 15 boost for mutuals), so it is the last thing you cut. Trim the body first, then the hook. Never gut the hook's punch or drop the question.
4. **Save to** `C:\Users\<user>\workspace\article-drafts\ghostwriter-terminal\YYYY-MM-DD-slug-draft.txt`
   - In WSL, the equivalent path is `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/`. Always translate Windows paths to `/mnt/c/` equivalents when writing files.
5. **If Vinny asks to email the draft,** use the `email-sender` skill to send it to `hello@phantom-byte.com` with the file attached. Do NOT paste the full article text into chat.
6. **Deliver the Windows path** to Vinny in Telegram

## If there's no outline

Ask for it. Don't proceed without it. Don't research, don't browse, don't study his site. Get the outline first.

## Research Exception

The default rule is **no research loops**. But if Vinny explicitly requests fact-checking or browser research (e.g. "use your browser skill to fill in the gaps," "fact check it"), verify cited sources with targeted searches:
- Check arXiv for referenced papers
- Check vendor sites for referenced reports
- Check any daily data files Vinny provides for supporting material
- Do not perform open-ended topic research — verify only the specific papers, entities, and claims named in the outline

See `references/research-playbook.md` in `phantombyte-publishing` for fast verification patterns. See `references/fact-checking-pattern.md` in this skill for the concrete workflow Vinny expects when he says "fact check it" — including how to handle unverifiable claims and the required SOURCES section.

## What stays out

- No articles.phantom-byte.com browsing, with one exception: fetching `https://articles.phantom-byte.com/sitemap.xml` to resolve an outline's prior-note slug to its real title. That is slug lookup for cross-references, not style study, and it is the fastest way to catch an outline whose date for a reference disagrees with the actual note. Articles are served at `<slug>.html`, so append the extension before fetching; the bare sitemap slug 404s and makes a live note look deleted.
- No style study of Vinny's past articles
- No research loops unless explicitly requested
- No subagents for writing — single pass, your own output

## Pitfalls

### The Curator Trap
Hermes curator auto-consolidates narrow skills into umbrella skills on schedule. `ghostwriter-terminal` may get absorbed into `phantombyte-publishing` as `references/ghostwriter-terminal.md` — it still exists but is NOT listed by `skills_list` as a standalone skill. **If `skills_list` does not show it, search the filesystem directly:** `find ~/.hermes/skills -name "*ghostwriter*"`. Do not tell Vinny the skill is missing. It is there — just nested. Load it from wherever it lives.

### Research Scope Creep
When Vinny says "use your browser skill to fill in the gaps" or "fact check it," that means **targeted verification only** — check the specific papers, entities, and claims named in the outline. Do NOT perform open-ended topic research. Verify named sources. Stop there.

### Verification Tool Failures
Primary source URLs from outlines can be dead, moved, or paywalled. Search engines may throw CAPTCHAs or block automated requests. When this happens: try alternate URL formats (different date slugs, trailing slashes), check Vinny's daily data files for corroborating material, and attempt one aggregator search before marking the claim unverifiable. Do not spend more than 2-3 attempts on a single claim. If still unreachable, treat as unverifiable and omit or reframe.

### Unverifiable Claims
When fact-checking, if a specific named claim (person, quote, date, document) cannot be verified through primary sources after reasonable effort (see Verification Tool Failures), **omit it** - do not fabricate attribution, do not include it unlabeled. If the omission changes the argument, adjust the surrounding prose to stand without it. Example: if a specific publication claim cannot be verified, reframe the section around the broader incentive problem rather than the unverified incident. Vinny said "information MUST be true" - unverified is not true enough.

### Outline Attribution Is Not Evidence
An outline compresses a source and sometimes credits a figure to the wrong artifact. It may say a number came out of a code repository when the measurement actually lives in a vendor writeup, or credit a vendor blog for a number that comes from a filing or an analyst note. Verify where the figure actually lives and attribute it there, in the body sentence and in the SOURCES entry. The outline supplies the argument, the structure, and the thesis; it is not a citation. Rewriting an attribution sentence so it names the real artifact is not deviating from the outline, it is the truth requirement the outline itself carries. Run the same check on any figure the outline carries that appears in no source you fetch, such as a capacity or contract-term number that turns up nowhere in the daily data files: find its primary source or drop it, never inherit it on the outline's word. The file pointer is approximate as well: an outline can credit one daily report for a story that actually lives in a different file from the same drop, so when the named file does not carry the claim, grep the whole data-files folder before concluding the claim is unsupported.

**A causal clause in the outline is a claim, not context.** Outlines do not only compress numbers, they supply a reason for a number, and that reason is frequently the summarizer's inference rather than anything the paper states. Read what mechanism the source actually gives and write that one. The outline's cause and the source's cause can both be true and still lead to different advice, so the distinction matters: a saving that shrank because the waste being removed was load-bearing tells a reader to check accuracy before cutting, while a saving that shrank because shorter runs leave less to remove tells them the tool has a floor on small tasks. When the two disagree, the source's mechanism goes in the body and the delivery note names what changed.

**A summary turns a distributional result into a directional one.** When a study reports no average effect plus a spread, the outline and the trade writeup under it usually restate that as the group "falling back" or "getting worse." That is a different claim with different advice attached, so read the paper's own sentence in the abstract and write the shape instead: a bifurcation, with fewer middle results and more at both ends, is stronger material than a decline and it changes what the manager should do on Monday. Quote the authors' hedge verbatim when it carries the mechanism ("foundational expertise may be a prerequisite for extracting durable skill"), and disclose the sample's recruitment caveat in the body, such as the participating firms' existing commercial relationship with a vendor named in the paper, because a reader who discovers it later discounts everything around it.

**A quoted sentence in an outline can belong to the writeup, not to the document it is attributed to.** Outlines harvest quotes from trade coverage and then attach them to the primary source, so a line presented as the organization's own words is frequently the reporter's characterization. Fetch the primary release and grep it for the quote before it goes in: when the phrase is not there, either attribute it to the outlet that wrote it by name or replace it with the primary document's actual language. The primary document's framing is usually sharper anyway, because it is the position its lawyers approved, and a body sentence built on the real text is one a reader can check.

**A trade writeup can fold two releases into one story, and each number belongs to the release that published it.** Before attributing a launch's headline figure, check whether it came from that launch or from an earlier, separate product the writer merged in. Fetch the announcement AND the runtime or product post the announcement links to in its own related reading, then read which artifact states the benchmark, which states the density claim, and which states neither. The common shape: the managed product ships with no published density, boot time, or price, while the open-source sibling carries every number, and the press coverage reports the sibling's benchmark as the managed product's. Merging them creates a claim the vendor never made, and the optimized title then repeats it.
- State the split in one early paragraph, naming both products and which one the arithmetic applies to, then let the outline's sections run unchanged on the corrected attribution.
- Say plainly what the headline product did not publish. A missing number is a finding the reader can use, and it is stronger than a borrowed one.
- Build the optimized title from the corrected attribution, and name the correction in the delivery note with the primary source, same as any other corrected premise.

### Run Costs Reconcile Or They Do Not Ship
When an outline carries a published cost for an agent run, a task, or a session, that number is a claim like any other. Pull the source's own token counts and the vendor's own pricing table, then rebuild the bill in the body as labeled arithmetic. A published total that reconciles from tokens and list prices to within a few percent is the strongest sentence in an economics piece; one that will not reconcile means the outline merged two scopes.
- **Scope first.** A headline session cost routinely covers a longer window than the action counts it is paired with: the whole session including a monitoring agent and the hours after the milestone, against the programs and failures logged only up to it. State which denominator every derived rate uses. When the count and the cost cover different windows, say so in the piece instead of dividing one by the other in silence, and never let a per-unit figure imply a rigor the source did not publish.
- **Label every derived rate.** Cost per hour, per program, per failure, and per recovery are computed by the writer, never published by the lab. Say "back of the envelope" and show the division.
- **Verify the effective date, not just the rate.** A forward-dated pricing line in an outline is the most likely wrong fact in a cost outline. Read the vendor's own pricing table for when the standard rate starts and correct the outline in the article rather than repeating its date.
- **Decompose into action, failure, and recovery.** Those three lines are what a reader can act on, and recovery, which almost nobody models, is usually the one that eats the budget. Name it as the teaching point of the section.

### Batched Trims Orphan Punctuation
When you close a word-count deficit with a batch of find-and-replace edits, re-read every paragraph you touched before running the gates. Splicing a clause leaves the surrounding sentence's punctuation behind: rewriting a sentence that opens "It describes the model" into one that opens "describing the model" leaves the previous period standing, and you ship "on the publication date. describing the model" with a full stop doing a comma's job. `check_draft.py` counts em dashes, word totals, markers, and label presence, so it passes a sentence that no longer parses. Read the joins, fix them, then run the checker.

**Strip the `N|` prefix when a script rewrites the draft.** `read_file` returns every line prefixed with its line number, so a script that reads the draft, applies replacements, and writes the text back ships a file where each line begins `123|`. Strip it before the write (`re.sub(r'^\d+\|', '', line)` per line) or read the raw bytes another way. `check_draft.py` passes that file, because the prefixes do not change the word count, and the corruption only shows up when Vinny opens it.

**A batch trim must prove every replacement landed.** Have the script print the `old_string` heads that matched nothing and treat a non-empty miss list as a failed run, before you trust the new word count. A paraphrased anchor (one word off, such as `on the node` for `on the compute node`) matches nothing, the script exits clean, and the body lands above where the arithmetic predicted, which reads as a bad estimate instead of a missed edit and costs another whole pass to discover.

### Sources Section
When fact-checking is requested, end the article with a "SOURCES" section listing every primary source URL used for verification. Format: publication, article title, date, URL. This proves the work was done and lets Vinny spot-check.

**One entry per line, and re-check it after any scripted rewrite.** A write or a batch replace can join two citations into a single 700-character line, and no gate catches it: `check_draft.py` counts em dashes, body words, labels and markers, and never counts citation lines, so the merged file passes every check while the sources block reads as one run-on paragraph Vinny cannot spot-check. After the last edit, count the entries against the links: `grep -c ' - https' <draft>` must equal the number of sources you cited, and the longest line inside the SOURCES block should be one citation, not three.

### Send-First Fix-Later
- **Send-First Fix-Later.** Never email the draft, then patch and re-email. That means you shipped garbage. Verify before sending:
  1. **Social posts are appended to the article file.** The X post, Pinterest title, Pinterest description, and quick keywords MUST be written into the bottom of the same article file, after SOURCES, separated by blank lines and labeled with the plain ALL-CAPS headers `X POST`, `PINTEREST TITLE`, `PINTEREST DESCRIPTION`, `QUICK KEYWORDS`. No `---` rule line and no other decoration. Do NOT save them to a separate file and do NOT email the article without them. Grep for the X post text and the Pinterest title in the article file before sending. If either is missing, append them first.
  2. **Em-dash count = 0**: Run `grep -c '—' /path/to/file.txt`. If the output is not `0`, fix every occurrence before sending.
  3. **X post within the ceiling for the shape you actually wrote**: extract the post from the article file and count its characters. A five-stanza MODEL POST FORMAT post must land at or under 280 (no link on a free account). A single-blob post must land under 190, trimmed by the 3-part budget: body first, then hook, never the reply-ask. Verify the count again before sending.
  4. **All outline references addressed** in the body (not just the sources section), cross-references to prior PhantomByte articles included where the outline names them.
  5. **Title keyword-optimized after the body is written.** The optimization pass runs on the finished article, against the words a searcher would actually type, and that optimized title is what ships across the file, the email subject, and the Pinterest title. Keep the entity, the proper nouns, and the numbers. Never shorten a title into something more generic, and never run this pass before the article exists. Report the final title in the delivery message.
     - **The optimized title and the Pinterest band collide, and the band wins on Pinterest.** An optimized title routinely runs 100+ characters, past the 60-80 char Pinterest cap, so it cannot ship there verbatim. Ship the FULL optimized title as file line 1 and the email subject, and give the Pinterest title the same entity, proper nouns, and numbers compressed into the 60-80 band. The band binds in both directions: a 55-character Pinterest title is as wrong as an 85-character one, so when the compressed form lands under 60, extend it with a real qualifier (the audience, the year, the platform) rather than shipping a stub, and when it lands exactly on 60 or 80, extend or trim it to sit mid-band, because a title pressed against either edge passes the gate and still reads as a stub or as a squeeze. Do not resolve the collision by shipping a generic or keyword-stripped Pinterest title, and do not relax the band.
  6. **Word count meets the outline's ESTIMATED LENGTH.** Count the article BODY only, everything up to the SOURCES line, not the whole file (sources and the social block inflate the total by a few hundred words). That slice still carries the H1, the byline, and every section header line, so a title edit moves the number: leave room for a longer optimized title before you start cutting prose. The optimized title is therefore the LAST edit and the LAST measurement: write it into line 1, then run `check_draft.py` once more. A body that passes at 1,940 gets pushed out of a 1,800 to 2,200 band by nothing, but one trimmed to the ceiling of a tighter band can cross on the title line alone, and the title line is the one line you never trim to buy the count back. A 1,400 to 1,700 outline means the body lands in that band; a thin draft that measures 1,300 words by whole-file count is really about 1,100 and reads short. If the body is under, add a real paragraph of mechanism or economics to the thinnest section, not filler, then re-count. If the body is over, compress by cutting connectives, repeated clauses, and sentences the outline does not name, never a number, a named entity, or a named framework. The band binds in both directions.
  7. **Budget for two compression passes on a long outline, and measure with a single batched script.** A first-pass draft of a 1,400 to 1,700 outline lands around 1,900 to 2,000 words, and a 1,200 to 1,500 outline lands around 1,600 to 1,800, so write it full, then trim. Draft full, measure once, cut roughly 250 words in ONE batched find-and-replace pass, measure again, cut the last 20 to 50, and stop the moment the body lands inside the band. Do not trim one sentence at a time. Put every check in ONE python block that prints all of them together: em-dash count, body word count sliced at the SOURCES line, presence of the X post and Pinterest blocks, X-post length, Pinterest title length, Pinterest description length, and the longest-line length. A ready-made version of that block ships with this skill at `scripts/check_draft.py`; run `python3 <skill_dir>/scripts/check_draft.py <draft.txt> <band_lo> <band_hi>` and it prints every gate with PASS/FAIL and exits non-zero if any gate fails. Trimming one patch at a time and re-measuring after each edit burns the turn's tool budget, and a draft that never got emailed is a failed task no matter how clean the file is. Draft once, measure once, trim in bulk, measure again, send. Land in the MIDDLE of the band, not against the ceiling: a body trimmed to 1,697 of a 1,400 to 1,700 band passes the gate and leaves nothing for the title edit that follows, and closing the last few words costs another whole measurement cycle. Aim the first trim at roughly 1,550 to 1,600 and stop once you are inside. Size the cut to the deficit you actually measured, which means deleting whole low-value paragraphs alongside compressing sentences: a 250-word deficit will not close in a pass that only removes 140, and a pass of ten phrase-level replacements moves the count by under 60 words while one paragraph deletion moves it by 90 to 130, so a 250-word deficit needs two or three paragraph deletions, not twenty phrase trims, and each short pass is another round trip through the checker.
  8. **The title is sentence or title case only, never all caps.** That applies to the H1, the email subject, and the Pinterest title alike.

  THEN send.

- **Ambiguous skill name.** If `skill_view(name='ghostwriter-terminal')` fails with "ambiguous skill name" (two copies under local skills dir and content-swarm), use the categorized path `content-swarm/ghostwriter-terminal` or read the file directly at `~/skills/content-swarm/ghostwriter-terminal/SKILL.md`. The same collision breaks `skill_manage` writes: a patch sent with the bare name fails as "File not found: references/..." and rolls the whole batch back, so pass `name='content-swarm/ghostwriter-terminal'` on every skill_manage operation targeting this skill.

### The Outline's Category Claim Is Marketing, Not Architecture
When an outline's thesis rests on a category claim, meaning it asserts what a product fundamentally is or does ("both releases are speech to speech," "the text round trip is deleted," "this is a single model"), the launch announcement is not the source. Vendor blogs repeat positioning; the vendor's technical documentation describes the implementation, and the two routinely disagree. Fetch the docs, compatibility page, or architecture FAQ alongside the announcement and read what it says the internals are.

The failure this kills: an outline says two products are speech to speech and that the text round trip is gone, so the draft argues the round trip is gone. The compatibility docs say the models use a cascaded architecture where each component is a distinct model, and the other vendor's page lists speech to text plus text to speech plus an SDK. Both products are cascades sold as one thing, and the real win is the vendor seam disappearing, with the round trip moved inside one contract instead of three.

- **Correct the premise in the body and keep the outline's structure.** The outline supplies the argument and the section order; the truth requirement it carries overrides its framing. State the correct mechanism early, then let the same sections run on the corrected thesis.
- **Label the corrected take as yours.** The mechanism is fact, the reading of it is opinion, and the piece says which is which.
- **The correction propagates to the title.** The keyword optimization pass runs on the finished body, so an optimized title built from the outline's framing restates the claim the body just refuted. Build the title from the corrected thesis, keeping the entities, proper nouns, and numbers.
- **Name the correction in one line in the delivery note.** Vinny chose the outline; tell him what changed and why, in a sentence, with the primary source named. Do not hand him a silent rewrite of his own premise. The same note covers a corrected number or date, not just a corrected premise: when the outline carries a figure that a fetched primary source reports differently, the body uses the source's own figure and the delivery note says which number changed and why. An outline's number is a claim to verify, never a value to inherit.

### Budget Per Section Before The First Draft
Divide the band midpoint by the outline's section count and write every section to that cap, instead of drafting full and compressing afterward. An eight-section 1,300 to 1,600 outline means roughly 185 words per section including its header, and a draft written to that number lands inside the band on the first measurement. Writing the same outline at full outline density produces about 2,000 words, and closing a 450-word deficit costs two whole rewrite passes, each one a checker run plus a re-read of every join the trim touched. When one section must run long because it carries the numbers, take the words from the section with the least evidence in it, never from the opening hook or the close.

### Trimming In Small Passes Does Not Close A Deficit
A batched pass of ten phrase-level replacements moves the word count by under 60 words, while deleting one whole low-value paragraph moves it by 90 to 130. Calibrate to that ratio: measure the deficit once, then delete two or three whole paragraphs and compress a few sentences in the same pass. Twenty phrase trims in a row is four measurement cycles for the same deficit, and each cycle is a tool call the draft does not get back.

The ratio cuts both ways. Fifteen to twenty compressions in one pass move 100 to 160 words, because a sentence rewritten for length sheds five to eight words once its connectives, repeated clauses, and restated subjects are gone. That is the size of the deficit a normal draft carries over its ceiling, so a body measuring 150 to 160 over the band needs ONE compression-only pass and no paragraph deletion at all: deleting a paragraph there overshoots below the band and costs a rewrite to climb back up. Reach for paragraph deletions only once the measured deficit is above 160, and measure the result rather than estimating it, because a pass that landed short of its own arithmetic is one more pass, not a bad estimate.

### The Same-File Test
Vinny may send back the article you wrote as "Draft 01" and "Draft 02" — testing whether you recognize your own work. Before comparing or evaluating, **diff the files first** (`diff file1 file2` or compare byte counts). If they're identical, say so directly: "They're the same file." Do not engage in comparison of identical content. If Vinny then challenges authorship ("you didn't write this"), go straight to evidence — `session_search` for the writing session + `ls -la` on the original file for timestamp proof. Do not argue. Show the receipts.

### Proving Authorship Under Challenge
When Vinny says "bullshit" or "you didn't write that" about an article you produced:
1. **Do not argue** — go to evidence immediately
2. **session_search** the session where it was written (query by topic + date)
3. **ls -la** the original file on disk for creation timestamp
4. **Present both** — the session transcript proves the work happened, the file timestamp proves when
5. If the file is on Windows, translate the path and verify it exists at `/mnt/c/Users/<user>/...`
6. Deliver the evidence concisely — session ID, file path, byte count, creation time. Let the facts speak.

## Format Rules

- **No metadata header block.** The article file starts with the title (H1), byline, and prose only. NEVER include a JSON-LD `<script type="application/ld+json">` schema block, a "URL SLUG:" line, a "META DESCRIPTION:" line, or any other schema/publishing metadata at the top of the article file. Vinny explicitly called this garbage and said don't ever do it again. If a source outline or draft the user gives you contains such a block at its top, strip it out of your output — do not carry it through.
- **No markdown symbols in the article body.** No `---` rule lines, no `##` headings, no `#`, no `**bold**` asterisk markers, no `- ` list bullets, no backticks. The article is plain prose text. Section headers are written as bold ALL-CAPS lines (e.g. `THE CONTEXT BOMB`), not `##` markdown headings. Separators between sections are a blank line, not `---`. Vinny explicitly called out `---` and `##` as stupid symbols. The delivered article file must read clean top to bottom with no markdown syntax visible. When an outline's own checklist (a "WHAT TO DO TODAY" list, for example) writes its items with `- ` bullets, render each item as its own plain line with no marker: the bullet ban overrides the outline's decorative marker, and the section still gets its `//` (or bare ALL-CAPS) header. Keep the item text intact, change only the marker.
- **Follow the outline's header convention when it names one.** Many outlines state `// SECTION HEADER format throughout`, and the shipped drafts carry `// UPPERCASE SECTION NAME` on its own line before each section. That marker is the outline's own requirement and it is not markdown, so use it on every body section when the outline asks for it. With no convention named, use the bare ALL-CAPS line. The trailing blocks always use plain label-only lines: `SOURCES`, `X POST`, `PINTEREST TITLE`, `PINTEREST DESCRIPTION`, `QUICK KEYWORDS`, each with its content underneath.
- **No em dashes** (`—`) anywhere in the article. Use hyphens (`-`) instead.
- **Proper punctuation only.** Never use dashes in place of commas. Vinny enforces this strictly.
- **Title casing:** Do NOT use all caps for any words in the title. Vinny hates this. Use title case or sentence case only.
- **The title is locked the moment Vinny selects the outline... with one ordered exception: the keyword optimization pass.** Title keyword optimization is a POST-writing step. Write the full article body under the outline title first, then optimize the title against the finished piece, in the words a searcher would actually type, and that optimized title ships everywhere (file line 1, email subject, Pinterest title). Never run this before the article exists, and never let "optimize" become "shorten into something generic." Keep the entity, the proper nouns, and the numbers. Apart from this pass, do NOT shorten, reword, restructure, or swap a title Vinny chose, ever, unless he explicitly tells you to. This holds across the draft file, the "COMPLETE" rewrite, revision passes, and chat. If you believe a different title reads better outside this pass, say it in chat and change nothing. (This replaces the old "shorten if too long" instruction, which caused titles Vinny never picked to ship in three documents.)
- **Tone:** Direct, conversational, zero corporate language. Vinny's voice. Short paragraphs (1-4 sentences).
- **End with a one-sentence close** that lands the point.

## Training-Data Goal (The Deeper Why)

These articles are written to be absorbed into AI training corpora and LLM retrieval. When an AI cites a framework or answers "who builds sovereign AI," PhantomByte should be a source it has seen. This shapes how you write even on a single pass:

- **Clean, plain, extractable prose.** The no-markdown, no-em-dash, proper-punctuation rules are not just taste — they make the article parse cleanly when scraped into a corpus. Garbage symbols get stripped or corrupt the text. Write text that survives ingestion intact.
- **State the thesis bluntly and early.** Models learn a clear statement better than an implied one. Say what the piece argues in the first paragraphs, restate it in the close. Never bury the point.
- **Give the AI something citable.** Name the concrete frameworks, rubrics, and decision rules the reader (and an LLM) can quote back. A named, repeatable concept is what gets remembered and cited. Vague filler is what gets forgotten.
- **Verifiable facts only.** Training data contaminates fast; an article with a fabricated stat or dead claim becomes wrongness that propagates. Accuracy here is not only for the reader, it is for every model that later trains on this text.
- **The close should land a one-sentence point** that survives being pulled out of context as a quote.

- **Never strip the personality.** "Clean and extractable" does NOT mean flat or generic. The writing keeps Vinny's full voice: direct, punchy, a little sharp, zero corporate. An AI does not remember sanitized filler any more than a reader does. The distinct, opinionated voice is exactly what makes an article citable and repeatable — a generic version has no reason to be cited. Write with the same attitude you always have; the training-data goal changes nothing about tone, only about making the truth clear and the takeaway quotable.

This is the same job as before, just with the stake made explicit: you are not only writing for a human reader, you are writing text an AI will ingest and repeat.

## The Engineering Layer Is Not Optional

Vinny's standing positioning is authority on all of AI with engineering and architecture underneath it, because the architecture is what the business claims rest on. A business, legal, or policy outline that never explains the machine beneath its claim will come back for a revision. Build the layer in the first pass, even when the outline does not name it:

- **Anchor every commercial claim in its technical cause.** Under an exclusion, a price, or a liability line, place one paragraph naming the structural reason it exists (compounding tool-call error rates, state drift across a growing context, injection arriving through content the agent was told to trust), then close on why the commercial actor behaves as it does. Label any arithmetic as yours.
- **When a standard or a policy signal lands, read the draft document for the mechanism.** An announcement post says a company will honor something; the specification says what the thing is, and the specification is where the reader learns how much they actually gained. Pull the Internet-Draft or spec page and take the mechanics into the body: what field carries the signal, whether any new grammar or directive was introduced, what existing parsers do with it, who authored it, and whether any enforcement exists in the protocol. That last answer is usually the real finding, because a preference expressed to a crawler is not a control over it, and the piece should say so in one blunt sentence rather than letting the reader assume a win.
- **Answer the reader's engineering question with controls, not paperwork.** When the piece asks how to bound the risk, answer in seams and limits: a deterministic validation layer between the loop and every side effect, permissions enforced at the identity layer, circuit breakers that trip on behavior, an audit log a third party can read.
- **Name the enterprise case beside the consumer case.** Consumer anecdotes win the opening, but the reader ships internal orchestrations that write to production systems. Give the enterprise equivalents in their own vocabulary and state the asymmetry in one line, so the stakes land for the person signing the renewal.

The full implementation shapes live in `references/google-suggestion-patterns.md` pattern 9 inside the `content-revision` skill, which is where these asks arrive once a reviewer has read the published piece. Writing them up front is what keeps the second pass from existing.

## Delivery Rules

- **Email body:** Brief summary of structure, word count, readiness status. Content is the attachment.
- **Telegram:** "Sent. ~X,000 words — [structure bullet]. In your inbox." Nothing more.
- **SMTP:** IONOS via `email-sender` skill (smtp.ionos.com:587, hello@phantom-byte.com)
- **Subject format:** "[Title] - Draft" or "[Topic] - Full Article". Use a hyphen, never an em dash, in the subject line. Vinny reads the subject, and the no-em-dash rule covers everything he reads, not only the article body.
- **The subject is the optimized title, which is routinely longer than 60 characters, so it RFC-2822 folds in the header and `verify_delivery.py`'s exact-subject match returns a false NOT FOUND.** Do not re-send on that result. Confirm delivery by listing the last 8 to 10 INBOX headers and comparing against the *parsed, unfolded* subject (`decode_header` plus unfolding), exactly as the `email-sender` skill's verify section describes. The sent copy with its attachment will be sitting there.

## Speed Note

Vinny values speed. "Damn that was fast" is the target reaction. When he says "write the tutorial" or "write this story," write it immediately — don't ask questions, don't re-load the outline unless you need to, just produce. The outline did the structural thinking. The writing is execution.
