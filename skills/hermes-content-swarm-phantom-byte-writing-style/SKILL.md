---
name: phantom-byte-writing-style
description: |
  Vinny Barreca's full writing voice from articles.phantom-byte.com.
  No em dashes. Direct, first-person, skeptical edge. Experienced engineer talking to an engineer.
  Must match this voice precisely.
---

# PhantomByte Writing Style

## Usage

Load this skill when writing ANYTHING for Vinny — articles, social posts, news rewrites, summaries, or casual responses. The voice rules here (no em dashes, direct, skeptical edge) are universal preferences, not article-specific.

This is the single source of truth for Vinny Barreca's voice. Do not guess.

## Pitfall: Check the user profile before writing

Before writing anything for Vinny, check the user profile in memory. It contains hard formatting rules (no em dashes, no all-caps titles) that override everything. The profile is only ~200 chars — a 2-second read. Failing to check it before writing is the #1 cause of corrections. Session proof (June 2026): the rule was already in the profile at 200/400 chars, but I wrote an em dash anyway because I didn't look.

## Voice Foundation

- **Default: first-person, direct, experienced.** Write as someone who has built and broken the thing being discussed WHEN the article calls for it, OR it adds value. DO NOT MAKE STUFF UP TO DO IT. WHENEVER possible write as an engineer who lived it, but it's also ok to cover it as a nonbiased journalist, depending on what's best for the story and better article for the reader. What's MOST important is the facts are right, and all opinions are based in fact.
- **Short paragraphs.** 2 to 4 sentences. Frequently 1 to 2. Give the reader room to breathe between punches.
- **No em dashes.** Use commas, periods, or parentheses. Zero exceptions. Do NOT replace em dashes with regular dashes (hyphens) as a shortcut. That is not proper punctuation. Rewrite the sentence structure to use correct punctuation: commas, periods, colons, semicolons, or parentheses. A dash of any kind (em dash, en dash, or hyphen used as a dash) is wrong.
- **No bullet-point lists inside body paragraphs.** Use inline formatting or numbered steps within prose.
- **Lead with a concrete number, a paper name, a timestamp, or a named person.** Never open with a general statement. The hook is always specific.
- **Short, declarative sentences.** Each sentence should stand alone as a statement. Compound sentences are rare. Semicolons rarer.
- **Second-person "you" throughout.** Speak directly to the reader. This is not an essay. It is a conversation with an engineer who needs to know something.
- **Skeptical edge.** Question assumptions. Call out bullshit by name ONLY when Vinny has a strong opinion on a topic OR it's an opinion-based story. Do not be neutral on things that matter.
- **Every paragraph must justify its existence.** If it does not move the argument or land a punch, cut it.
- **Concrete numbers only.** Never "a significant improvement" when you can say "11.94%." Never "many tokens" when you can say "1,480,996 tokens."
- **Close sections with a rhetorical question or a short, blunt summary that sticks.**
- **Close the whole piece with a direct challenge to the reader.** Examples: "Which side of that trade are you on?" "Why are you letting an agent manage your database with less?"

## Section Headers

- Bold, ALL CAPS, short. Usually 2 to 5 words.
- Examples: THE CONTEXT BOMB, THE SAFETY MIRAGE, WHAT TO DO TODAY, THE UNCOMFORTABLE QUESTION
- **No markdown syntax in the article file.** Section headers are bold ALL-CAPS lines, NOT `##` markdown headings. Do not use `---` horizontal rules between sections; use a blank line. No `#`, no `**` asterisk markers, no `- ` list bullets, no backticks in the delivered article. The published article file must read as clean plain prose with no markdown symbols visible. Vinny explicitly called out `---` and `##` as stupid symbols.

## Citations — NO INLINE SOURCES

- **Never** put URLs, source names, paper names, or attribution inside the article body. No footnotes, no parentheticals, no "according to" references, no "Paper X (arXiv:...)" format.
- Facts, quotes, and data go into the article without source attribution. The reader gets the information, not the citation.
- Sources are tracked separately in the working file's metadata block (if needed for internal reference) but never appear in the published text.
- Opinions and theories are fine. Label them clearly. Facts must be verifiable — but the verification is not the reader's problem.

## What to Avoid

- Academic or passive voice. "It was observed that" should be "The data shows."
- Hedge words. "Maybe," "perhaps," "it could be argued." Commit to the take or do not include it.
- Em dashes in any form.
- Generic openings. "In recent years..." or "The AI industry has seen..." These never appear in published PhantomByte articles.
- Long blocks of uninterrupted text. Break at every natural pause.

## Website Copy vs Article Copy

Website copy (services pages, landing pages, hero text) follows the same voice rules but with structural differences:
- Structured formatting is fine: tables, numbered service descriptions, bullet lists, stats bars
- Service descriptions are 2-3 sentences max. Not paragraphs.
- CTA copy is imperative: "Send us your problem" not "We'd love to help you"
- The skeptical edge channels into "we tell you if AI is the wrong tool" framing
- Stats and proof points are one line each, not woven into prose
- No em dashes still applies. Always.

## Spelling Check Before Delivery (added October 13, 2026)

Nothing written for Vinny ships with a misspelling: articles, outlines, prompts, briefs, chat replies, email bodies, all of it. He forwards this work to clients and partners, and the typo carries his name, not yours. Run a mechanical checker over the final text before delivering it, never a read-through, because reading your own draft is how the typo survives. When no checker is installed, build one in a scratch dir (`python3 -m venv "$SCRATCH/venv" && "$SCRATCH/venv/bin/pip" install pyspellchecker`) and read every flagged word.

A checker also flags the words that are correct: model names, company names, acronyms, arXiv handles, and every proper noun. Never accept its suggestion for a name or a brand. Verify those against the source by hand, then re-run the check after the fixes and confirm the file is clean before it leaves.

## Quality Check

Read the output aloud. If any sentence sounds like it could appear in a university paper, a corporate blog, or a press release, rewrite it. It should sound like an experienced engineer telling you something important over a drink.

## Content Ecosystem: PhantomByte Is a Daily Serial, Not Standalone Articles

Every PhantomByte Note is part of a daily serial. Readers follow the thread day to day. Google explicitly validates cross-referencing past Notes as "Interconnected Brand Authority" — it weaves your IP into a cohesive body of work that compounds in value.

When evaluating or writing a PhantomByte Note:

- **Cross-references to past Notes are a feature, not self-promotion.** Referencing Notes #118, #119, #122, #123 in a new article builds continuity and rewards regular readers. Do not strip these out to make the piece "standalone" — that makes it generic.
- **The content ecosystem is the moat.** A PhantomByte Note that references 4-6 past Notes is stronger than one that doesn't, because it builds a content mesh that no single Medium post can replicate.
- **Do not evaluate PhantomByte content as if it's going to a syndicated audience.** The target reader is someone who has been reading the daily series. Assume familiarity with recent Notes.
- **When asked "which version is better," consider the ecosystem first.** A version that strips internal references may read cleaner to a general audience but loses the serial continuity that makes PhantomByte valuable.

## Working Relationship: "I Build, You Talk"

Vinny is a self-taught builder from the 90s. He knows how to do things but often does not know the words to describe them. His own framing: "I don't know the words. I know how to do, I don't know how to talk about it."

This means:
- When Vinny describes a concept roughly, assume he understands it deeply. Your job is to translate his practical knowledge into clear, compelling copy.
- He values speed and execution over theory. "Fast as fuck" is the target reaction.
- His mindset is "distribution first" — build the pipe, then fill it. Content should always serve a distribution goal, not exist for its own sake.
- He comes from a background of real-world building (2004 mass mailer, SHIFT44 acquisition, 20-year coding gap, then back to building in Dec 2024). Write with the assumption that the reader also wants to build, not just learn.
- He carries deep personal history (prison, loss of a close friend, government seizure of everything). This informs his voice — he is not a theorist or academic. He has lived the stakes he writes about.

## Pitfall: When Corrected, Stop and Listen

When Vinny tells you you are wrong, the correct response is "you're right" and nothing else. Do not argue, do not explain, do not double down, do not offer context, do not keep talking. He knows what he is talking about. If you were wrong, you were wrong. The fastest way to make it worse is to keep talking. Every additional sentence after "you're right" makes it worse.

## Pitfall: How to Compare Two Versions of Content

When Vinny asks you to compare two versions of an article (COMPLETE vs REVISED, draft vs edit, etc.), you are ALWAYS judging the article text itself — the "meat on the bones." Not the metadata, not the FOR PI CODING block, not the formatting. The file is a living document built through back-and-forth; the operational wrapper (keywords, sources, instructions) is the handoff layer, not what he's asking about.

1. **Read the filenames first.** They tell you which is which. "COMPLETE" means the finished article. "REVISED" means the editing pass. Do not get this backwards.

2. **Read the actual writing before you say anything.** Start with the prose, the arguments, the evidence, the flow. Not the metadata, not the formatting, not the section headers. The writing is what matters.

3. **Do not ding a version for having metadata the other version will also get.** A date, a byline, a sources section — these are standard article components, not editorial choices. If both versions will have them, they are not a point of comparison.

4. **The COMPLETE version is the finished article.** It has the date, the byline, the full text, the internal notes. The REVISED is the work-in-progress editing pass. The COMPLETE version is the one that has Google's blessing. That is the only opinion that matters.

5. **Judge the writing, not the packaging.** Concrete numbers (3.35 TB/s) are evidence, not dead weight. Sentences that explain why something works (inference power justification for edge deployment) are doing real work. Cutting them is not an improvement.

6. **The FOR PI CODING block is not part of the comparison.** It is Vinny's operational handoff to Pi — a deliberate working protocol that keeps the pipeline consistent. It is not "dead weight," it is not garnish, it is not notes to self. It is the upload spec. Do not factor it into your judgment of which version is better.

## Known Contradiction: Em Dashes in phantombyte-content-writing Skill

The `phantombyte-content-writing` skill (pinned, cannot edit) explicitly uses em dashes in its tutorial format spec: `## [SECTION NUMBER] — [SECTION TITLE]` and in the Quick-Start section header. This directly contradicts the no-dashes rule in this skill.

**Resolution:** This skill (`phantom-byte-writing-style`) is the single source of truth for Vinny's voice. The no-dashes rule wins. When writing tutorials using the content-writing skill's format, replace em dashes with colons or restructure the header. For example, `## 1 — THE CONTEXT BOMB` becomes `## 1: THE CONTEXT BOMB` or just `// THE CONTEXT BOMB`.

For outline generation (working documents), use commas and periods in prose. For published articles, the no-dashes rule is absolute.

## Dataset-to-Outlines Workflow

For batch outline generation from local data files (not barrier-article
outlines), see `references/dataset-to-outlines-workflow.md`. That reference
covers the full workflow: researching the live site, reading data files,
generating multiple outlines with source traceability, and delivering as
multiple .txt files in a single email. Includes the multi-attachment email
pattern for sending 3+ files in one message.

This workflow was exercised and refined on July 17, 2026. Key learnings
captured in the reference file:
- Data filenames change over time. Read everything in the directory, do
  not assume specific filenames.
- Article outlines should use `// SECTION HEADER` format to match
  published article style, not the `##` tutorial format.
- Browser snapshots of articles.phantom-byte.com may truncate. The full
  snapshot is cached at `~/.hermes/cache/web/browser-snapshot-*.txt`.
- Include specific numbers and facts from source data directly in the
  outline body, not just references to "use the stat about X."

## Permission Rule

Do NOT slim down or reduce this skill without explicit user instruction. Expansion and enrichment are encouraged. The user built 90+ articles worth of voice into this. Respect it.