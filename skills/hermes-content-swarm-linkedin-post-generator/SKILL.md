---
name: linkedin-post-generator
description: Use when Vinny asks for a LinkedIn post.
category: content-swarm
---

# LinkedIn Post Generator

## When to Use

Load this when Vinny asks for a LinkedIn post, "what would be good to post about on LinkedIn", "something to post on LinkedIn", or when he forwards third-party posting advice (his own AI chat, a course, a blog) and asks whether it is right. The fact-check answer has to come out the same every time, so it lives here.

Not this skill: syndicating a finished PhantomByte article (`article-syndication`), or X posts (`x-algorithm-post-optimization`).

Vinny posts on LinkedIn while job hunting. Hiring managers and technical peers are the readers. That changes the job: the post has to demonstrate senior judgment without announcing that it is a portfolio piece. A post that says "I led the migration" reads as a resume line. A post that inverts a deployment order and names the failure mode reads as the person who would have caught it.

## Inputs

- Topic source is the day's local drop, `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/`. Read every file in it, not just one.
- The `outlineN-*.txt` files are the strongest pool because they already carry a thesis, verified numbers and source traceability. `tensorfeed_report_*.txt` and `ironpulse-*.txt` corroborate the figures and supply alternates.
- **Read the article file that is publishing tonight and exclude its subject entirely.** When he names an off-limits file, that file's whole theme is out, not just its headline. Pick a different outline, and do not slide into a neighbouring angle on the same subject.
- Compare the surviving outlines on transferability. An industry or physical-AI story that yields a discipline the reader can apply travels further than a finance story that reads like news commentary. The one that shows how he reasons under ambiguity wins.
- The subject is not always the data drop. He sometimes names his own artifact instead, a repo he just published, a script, a pipeline. Then the artifact is the source and the post has to prove its claims from it. See "When He Hands You a Repo or a Live Artifact" below.

## Post Shape

- **No required length.** A post runs as long as the argument needs and no longer. 200 to 300 words is a house starting range that has worked for one claim plus one framework. It is not a target to hit, not a spec, and not a platform recommendation. A post with a numbered sequence and a bulleted evidence list lands near 290 to 330, and a post making a single point can land at 150. Both are correct.
- Open on a specific claim with a number or a named decision in the first line. Never open on a general statement, and never open with the framing device ("here is a lesson from").
- Explain the mechanism in the middle and name the failure mode plainly: most teams skip to the last stage, the incident report blames the model, the model was fine.
- Give the reader something to do: a short sequence, the evidence gates, the questions to demand before advancing.
- Close on a challenge to the reader, one sentence, second person, PhantomByte manner.
- Short paragraphs, one idea per block, with a single line break between beats. **One sentence per block is the default, not two.** Split any paragraph that carries two moves: the first line of a post gets read on a phone, and a dense block is where a reader stops. Break long explanatory sentences at their joints (the prompt, the loop, the multiplier, the consequence each become their own line) rather than leaving three clauses in one block.
- Close with 3 to 4 targeted hashtags on the last line, after the closing question and nothing below them. Pick tags that describe the audience the post is aimed at (a domain tag, a role tag, a technology tag), not tags that describe the news. Four is the working number; more reads as spam and fewer forfeits discovery.
- Structural cores get a list, the argument stays prose. A sequence of stages, a set of gating metrics, or a checklist of what to demand becomes a numbered list when order matters and bullets when it does not. Keep the reasoning in prose around the list. What to avoid is a list buried inside an argumentative paragraph; the visible skeleton is what makes the post skimmable on mobile, and he asks for it on revision when it is missing.
- Name the actor, never "the thing". Concrete nouns carry the authority: the agent, the harness, the incident report, third party APIs. "Wire the thing into production" reads like a summary of someone else's work; "wire the agent into production" reads like the person who has done it.
- No em dashes, no en dashes, no hyphens standing in for dashes. No markdown headers in the post.
- Follow `phantom-byte-writing-style` for voice. It governs every word.

## Length: What Is and Is Not True

**Nothing dictates the length, not LinkedIn and not this skill.** The 200 to 300 word range is a house starting point for a post that carries one claim and one framework. It is not a rule, not a quality bar, and not something to report as met or missed. Length follows the content: add a numbered sequence and a bulleted evidence list and the draft runs longer, cut to a single point and it runs shorter. The only real ceiling is 3,000 characters.

Never repeat the claim that LinkedIn recommends 200 to 300 words. There is no such recommendation, and saying there is puts a fabricated authority in his mouth in front of hiring managers.

- The only length figure LinkedIn publishes is the 3,000 character cap, with text folding behind See More at roughly 140 characters. Lead with the sentence that has to survive the fold.
- Ranking is LLM and GPU based, confirmed on LinkedIn's own engineering blog on March 12, 2026, scored on what a post is about plus how members interact with it over time. No word count target is published anywhere.
- The 1,900 to 2,000 word figure that circulates as "ideal LinkedIn length" comes from a study of LinkedIn articles and newsletters, not feed posts. Confusing the two formats is the most common way this advice gets garbled.
- Engagement by format runs against plain text: native documents and multi image posts average well above text posts. Text is worth using because it is the cheapest format to carry an argument to a technical audience, not because the platform rewards it.

Numbers, wording and source URLs live in `references/linkedin-platform-facts.md`. Re-check them there before quoting any of it again.

## When He Hands You an Outline File

He sometimes names an `outlineN-*.txt` in the prompt instead of asking you to choose one. That file is a spec for a 1,300 to 1,600 word article, complete with `// SECTION HEADER` blocks and a WHAT TO DO TODAY checklist. Do not write the article, and do not write a post that walks the outline section by section. Compressing the outline is the job:

- The outline's opening hook is usually already the post's first line. Take it, tighten it so the claim and the attribution both survive the 140 character fold, and cut any second paragraph that only restates it.
- Two or three of the middle sections collapse into one prose block that explains the mechanism. Pick the section that teaches the reader why the thing works (the oracle explanation, the cost model), not the one that narrates the timeline. Timeline goes in a single sentence.
- Keep the action list as the numbered sequence, trimmed to what a reader can do this week. Drop items that only make sense inside a full article.
- Keep the closing question. It is already in his voice and needs no rewriting.
- Drop every `//` header, the reading time, the category line and the cross-references to other Notes. Those belong to the article, and on LinkedIn they read as pasted blog scaffolding.

## When He Hands You a Repo or a Live Artifact

Sometimes the subject is not a news story or an outline but his own work: a repo he published the night before, a script, a pipeline. The post then has one job, which is to prove the thing exists and does what the post says, read from the artifact itself. Treat it as a pinned post: a hiring manager gives it about eight seconds and clicks through only if the first line earns it.

- **Read the artifact through its API, not its rendered page.** For a GitHub repo: `gh repo view OWNER/REPO --json name,description,licenseInfo,createdAt,primaryLanguage,stargazerCount,url` for the license, creation date, language and star count; `gh api repos/OWNER/REPO/readme --jq '.content' | base64 -d` for the README; `gh api repos/OWNER/REPO/git/trees/HEAD?recursive=1 --jq '.tree[] | select(.type=="blob") | "\(.path)  (\(.size // 0)b)"'` for the real file inventory. A repo published hours ago can lag on the rendered page while the API already has it.
- **Every count in the post comes off that read, and every claim in the post names a file that actually does it.** A line about comparing an attachment's length to the file on disk is only honest if the read-back script exists and does that. Put the one-claim-per-file mapping in the report.
- **When the README's own count and the tree disagree, the tree wins** for a file count. The README is still the best source for what the repo is for, and quoting its own rounded number ("112 skills") beats a loose recount.
- **Never claim adoption, scale, or a team.** Read the star count, and keep it out of the post when it is low. The post argues from the engineering, never from traction.
- **The URL sits in the body above the closing question,** because the hashtags own the last line and nothing may sit below them.
- **Open on the failure the artifact neutralises,** with the counts as the qualifier line that keeps the claim concrete inside the fold. That two line hook is the whole decision a stranger makes before expanding.
- **Shape:** claim line, the mechanism (why the failure happens, not what the tool is), two or three concrete read-backs as separate one-sentence blocks, the rules that fell out of building it as a numbered list, a line on what is not the interesting part, the URL, the closing challenge question, four tags.
- **The dated report for this class carries:** the post, why the shape fits a pinned post, the facts read live with the file each claim maps to, the platform fact-check that decided the length, a NOT CLAIMED list (stars, scale, unattended operation), the measurements, and posting notes.

## Fact-Check Discipline

- Every figure in the post gets verified against the original reporting, not against the data file. The data file is a lead. Open the outlet that broke the story and confirm the number, the attribution and the timeframe. This step has caught errors.
- The data file's own summary line is not verification. Grep the report for the story, then scrape the publisher.
- **Attribute the claim to the entity the publisher names, not the one the aggregator implies.** A data file's summary can drop a parent company, so a product reads as belonging to the wrong firm. Read the publisher's own sentence and use that entity in the post, or use the executive's name and skip the company entirely when the product's ownership is not load bearing.
- **Carry the outlet's own hedge word into the post.** When the original says "reportedly," the post says "reportedly"; the qualifier is the difference between a sourced claim and one the reader can disprove. Note in the report which figure rests on secondary reporting rather than a first party disclosure.
- **Name a sponsor out loud in the post when the argument favours the sponsor.** A sponsored analysis inside a reputable outlet still counts as a source for its metric, but the sponsorship makes the recommendation self-interested, so the post states it in one clause and then makes the arithmetic stand on its own.
- A named framework or rubric may be his own reasoning, and usually should be. Present it as reasoning. Never attribute his rubric to the company in the story, and never put words in an executive's mouth that the reporting does not support.
- When he asks whether third-party advice is right, answer the fact-check separately from the writing. Say which part holds, which does not, and what the evidence shows. Do not soften a wrong claim into "partly right".
- No invented first-person experience. If a line would require him to have personally run something he has never described, cut it and make the point in second person.
- **Read the source's own limits section before asserting a claim.** A responsible disclosure or benchmark ends with what it did not test, and those sentences decide what the post may say. A vendor caveat such as one artifact not being retested in a later run means that artifact gets attributed to the original capture in the post, or gets dropped, never stated as current. Carrying the caveat into the report file as a NOT CLAIMED list is how the post stays defensible when someone checks it.
- Note the difference between the article's framing and what the source supports. An outline can reach for a second paper to explain a pattern; that second paper's numbers need their own verification before they appear in a post, and skipping it is cheaper than defending it.

## Web Research

Scrapling first, per the constitution. `Fetcher.get(url, timeout=30)` works on publisher pages, LinkedIn's engineering blog, LinkedIn Help, Hootsuite and Socialinsider, and it is faster than `StealthyFetcher`.

Search engines are the failure point: DuckDuckGo HTML serves a bot challenge, Google serves a verification interstitial, Mojeek returns 403, and Bing returns unrelated or generic results under `StealthyFetcher`. Do not burn calls re-trying them. Use `web_search` for discovery only, then scrape the publisher URL it returns with scrapling and read the actual text. Disqualify SEO counter and character-counter pages on sight: no named human author means no citation, however confident the number looks.

### Getting the Article Body Off a Publisher Page

`Fetcher.get(url).get_all_text()` on a news site returns the article wrapped in navigation, topic chips, newsletter promos and footer link farms, so the paragraph you need can sit past the first few thousand characters of junk. Do not conclude the page is empty or the fetch failed when the head of the text looks like menu links.

- Extract paragraphs directly and drop the short ones: `p.css("p")` then keep only nodes whose `get_all_text().strip()` is longer than about 40 characters, joined with newlines. Nav and promo links are almost always shorter than a real sentence, so the length filter removes them without a selector per site.
- This works unchanged on Business Insider and MIT Technology Review; expect each publisher to differ in chrome, not in structure, so reach for the paragraph filter before writing per site selectors.
- Print one URL per clearly labelled block, and fetch the batch in a loop that prints as it goes. A single `print(t[:4500])` per URL inside a loop means the last page scrolls the earlier ones out of view in the tool result, which then reads as a fetch failure for the pages that worked.
- The byline, the date and the author's name sit in that extracted text; take them from there for the report rather than reconstructing attribution from memory.

### Capturing His Voice From the Live Site

When the instruction is to match his voice, read the site rather than working from the style skill alone. `https://articles.phantom-byte.com/sitemap.xml` returns the whole archive as dated URLs, newest first, so pick two recent notes from the same category as the topic and read them whole.

- The article body begins after the `// field note NNN` marker in `get_all_text()`. Everything before it is navigation, archive lists and promo blocks, so slice from that marker and print the first few thousand characters of each note.
- Read two notes, not one. The first gives the rhythm, the second confirms it is the house style and not one piece's mood.
- Read the opening paragraphs and the section transitions. That is where the short declarative sentences, the one line definition and the blunt thesis live.
- Do not copy site furniture into the post: the promo blocks, the article index, the share row and the field note number are page chrome, not voice.

## Delivery

1. `SCRATCH=$(mktemp -d /tmp/hermes-linkedin-XXXXXX)`. Never a fixed path.
2. Write the post alone to `post.txt`, and the post plus the fact-check to a dated report file (`linkedin-post-YYYY-MM-DD.txt`). Both get emailed. Build the report as its own file and copy `report.txt` to the dated name, never the reverse: copying `post.txt` over the dated name ships the bare post twice and loses the fact-check. Check the dated file's first line before attaching it. For a post about his own artifact, the dated report also names the file behind each claim and carries a NOT CLAIMED list, so anyone who opens the artifact finds the post defensible.
3. Verify before sending: `wc -w post.txt` and record the count, reporting what the draft came to rather than a pass or fail against 200 to 300, plus `wc -m` against the 3,000 character cap, which is the only real limit. Then a grep for `[\x{2013}\x{2014}]` and for ` - ` to prove no dash punctuation, and `awk '{ if (length($0) > m) m = length($0) } END { print m }'` on the report to prove nothing was hard-wrapped. Also measure the hook: print the combined length of the first two non-blank lines and confirm it fits the fold (about 125 characters with margin), because a first draft can clear 140 on screen only by luck.
4. Spell check both with pyspellchecker in a venv, passing a LIST of words to `spell.unknown(...)` and sanity-checking the checker against `"teh receve"` first. Expect proper nouns, brands and jargon to come back; verify those by hand. `rollout`, `LLM`, `GPUs`, `LinkedIn` and author surnames flag every time. British spellings (`behaviour`, `licence`, `organisation`) do not flag because they are real words, and they are wrong for a US audience: grep the draft for `our` and `ise` endings and convert them.
5. Email through the `email-sender` skill, TO and FROM `hello@phantom-byte.com`. Subject short enough not to fold, under roughly 60 characters.
6. Verify delivery by reading the INBOX copy back with `scripts/verify_recent_headers.py --contains "<fragment>"` and confirming the attachment filename. Report only what it printed.
7. Telegram notice is a doorbell: what was sent, the subject, and the one-line fact-check verdict. Do not paste the post into chat.

## Revisions

He revises by downloading the emailed file and sending back a change list, each item with the reason behind it. Treat every item as an order, not a suggestion.

- Apply each item literally and completely. "Tighten this noun" means find every instance of the vague phrasing, not the first one.
- The core survives unless he says to change it: the thesis, the verified statistic, and the closing call to action stay untouched. Reformatting is not a licence to rewrite the argument.
- Every original constraint still holds after the edit. Reformatting into lists changes the word count, so re-run `wc -w` and the dash grep and the spell check on the revised text; a list conversion has pushed a draft past the ceiling before.
- Add a WHAT CHANGED section to the delivered file that names each instruction and what changed for it, so he can check the work against his own list in one pass.
- Name the file `<base>-revised.txt` and put "Revised" in the subject. A revised copy must not be mistakable in the inbox for the draft it replaces, and the IMAP read-back is matched on that subject.
- The Telegram notice reports what changed in two or three lines. Still no paste of the post.

### Formatting revision items he sends

He forwards platform-optimization notes and expects them applied as written, not judged. Three of them recur, and each has a mechanical check so the reply can state a number instead of an impression.

- **More whitespace.** Break every block that carries two sentences into separate lines, and split the long explanation blocks at their joints. Verify by counting the longest block in sentences, not by eye; nothing should run past two sentences and most should run one.
- **Hook above the fold.** The first two VISIBLE lines are what a phone shows before See More, so measure them together against roughly 140 characters and leave margin, targeting about 125. Count only non-blank lines: the blank line between the hook and its qualifier still consumes characters in the rendered post, so add it back when reporting the figure. Do the arithmetic in python over `[x for x in text.split('\n') if x.strip()]` and print the combined length, then quote that number in the report. When the two lines overflow, shorten the first line and rewrite the qualifier line to say the same thing in fewer words; do not delete the qualifier, since it is often what keeps the claim honest (a retail value disclosure is not cash spend).
- **Hashtags.** 3 to 4 on the last line, after the closing question, drawn from the tags he names when he names them, otherwise the audience's tags.

Applying these changes the character and word counts and can push a block count up, so re-run the `wc -w`, `wc -m`, dash grep and spell check afterward and restate all of them in the report. The report's own numbers must match the file that is attached: patch the copy first, then re-measure, then write the numbers down.

## Pitfalls

- Do not paste the finished post into Telegram. He asked for email, and the notification is not the delivery.
- Do not pick a topic because it is trending. Pick the one that lets a hiring manager see how he reasons.
- Do not let the framework be the entire post. A rubric with no evidence behind it is a listicle. One verified number before the rubric, one after.
- Do not re-run the sender after a clean send. The IMAP read-back is the verification, not a second email.
- Do not answer the fact-check from memory of what the platforms say. The whole reason this skill exists is that the popular 200 to 300 word claim is fabricated and gets repeated unless it is checked.
