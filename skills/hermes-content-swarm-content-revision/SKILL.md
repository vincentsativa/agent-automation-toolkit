---
name: content-revision
description: Apply external feedback to drafts. Only specified changes.
category: content-swarm
---

# Content Revision, Apply External Feedback to Draft Articles

Class-level skill for revising PhantomByte or other draft articles when Vinny provides a draft plus a set of revision recommendations from an external source (Gemini, a reviewer, an editor, etc.).

## Trigger

- Vinny provides a draft article file plus a list of revision recommendations
- The recommendations come from an external source (Gemini, Claude, a human editor)
- The instruction includes "implement ONLY the following recommendations" or similar

## Workflow

### Step 1: Read the Full Prompt Before Starting

Read the full prompt and the full article before making any changes. The user will specify exactly which recommendations to apply and which to skip. Read every item before starting, do not skim or assume you know the structure. Missing items from the prompt is the #1 failure mode.

**Critical sub-step:** Count the items. If the prompt says "implement the following 5 recommendations," you need to know there are 5 before you start. If you only see 2 at first glance, re-read. The prompt may have multiple sections, bullet points, or inline instructions that all count as separate items.

### Step 2: Understand the Scope

Identify what is being asked:
- Which specific recommendations to apply
- Which formatting constraints to respect (no em dashes, bold certain phrases, add transition sentences, etc.)
- What NOT to touch (the original content outside the specified changes)
- Whether existing paragraphs need to be **revised with new wording** (not just new content added)

### Step 3: Create a Mental Checklist

Before touching the file, enumerate every item that needs to be done. This is not optional, it is the only defense against missing items. Example checklist from a real session:
- [ ] Revise open-weights paragraph with new wording (swap out cloud endpoints, name Gemma/Qwen/DeepSeek, deploy on actual silicon)
- [ ] Add coding agent mention to multi-agent paragraph
- [ ] Bold "One stores. The other thinks."
- [ ] Bold "The architectural boundary enforces the security boundary."
- [ ] Add transition sentence between Code Mode and Coordination Layer

### Step 4: Apply Changes One at a Time

Use patch tool calls for each change. After each change, verify the result before moving to the next. This prevents cascading errors from a single bad edit.

**Patch-tool pitfalls when making targeted edits (learned applying multi-item briefs):**
- **`old_string` must be UNIQUE in the file.** `patch` fails with "Found N matches" when the anchor appears more than once (e.g. a bare `## Performance` or `## Pitfalls` heading that recurs). Fix: widen the anchor with surrounding context (the preceding subsection heading + a following bullet) until it's unique. Do NOT reach for `replace_all=true` for a one-off insert, it hits every occurrence.
- **When replacing a heading + body block, re-emit the FULL original body in `new_string`.** A replace that swaps `### C. <title>\n\n<intro sentence>` for just the heading silently DELETES the intro sentence. On multi-paragraph blocks, keep every original line in the replacement and only prepend/append your addition.
- **After the patch, read the file back** around the edit site to confirm the surrounding lines survived intact (not just that the tool returned success).

## Workflow

For **bold formatting** changes: verify the bold markers (`**text**`) are placed correctly and the surrounding punctuation is preserved. A bold phrase that includes a period or comma inside the markers will look wrong.

For **transition sentences**: place them at the exact boundary between the two sections. Read the last sentence of the preceding section and the first sentence of the following section to confirm the transition flows naturally.

For **revised wording** (replacing an existing paragraph with new content): read the old paragraph, then write the new one. Verify the new paragraph fits the surrounding context and doesn't repeat information already stated nearby.

### Step 5: Verify Completeness

After all changes are applied, re-read the original recommendation list and check each one off. If the list had 5 items and you applied 3, you missed 2. Do not deliver until every item is checked.

**Self-test:** "Can I name every item on the revision list and point to where it was applied in the file?" If not, you missed something.

### Step 6: Final Read-Through

Read the complete revised article to confirm:
- Every recommendation was applied
- Nothing outside the scope was changed
- All formatting constraints were respected
- No em dashes were introduced if the user banned them
- **No ALL-CAPS in the title.** This is a standing hard rule: "Do NOT use all caps in the title, I hate that shit." The title (the H1 / first line) must be normal case. Section headers in the body may be ALL-CAPS by design (that's a deliberate style device), but the TITLE itself never is. When revising, check the title line specifically, an ALL-CAPS title is a rule violation even if the body headers are ALL-CAPS on purpose.
- Bold formatting is applied exactly where specified
- Transition sentences flow naturally between their surrounding sections
- Revised paragraphs don't repeat information already stated nearby

### Step 7: Deliver

Save the revised version to the requested filename, in the same folder as the DRAFT he supplied unless he names another path, and deliver as instructed (email, Telegram, or both). A draft sitting on the Desktop means the COMPLETE goes beside it, even though older `ARTICLE ### COMPLETE` files live in the article-drafts folder; he opens the file from wherever he put the draft.

**Default delivery is EMAIL.** Vinny's standing preference is a `.txt` attachment to hello@phantom-byte.com, never the Desktop and never pasted in Telegram (the Telegram message is only a "doorbell" notifying him the email was sent). When he says "email it to me" or "send me the file," invoke the email-sender skill immediately and run the SMTP script. Do not substitute Desktop/Telegram delivery and do not wait to be reminded.

**SOCIAL POSTS ARE A REQUIRED DELIVERABLE, ALWAYS.** The X post, Pinterest title, Pinterest description, and quick keywords are NOT optional extras. They MUST be appended into the SAME .txt file as the article (after the body, in the social block described in the House layout section below) so they ride in the single emailed attachment. Do NOT email the article without them. Do NOT write them to a separate sidecar file. Verify the X post, Pinterest title (60-80 chars), and Pinterest description (150-300 chars) are present in the file BEFORE sending. The X post length is whatever shape you actually wrote: the five-stanza MODEL POST FORMAT in `x-algorithm-post-optimization` runs 150 to 280 characters, and the 190-character budget applies only to the single-blob one-liner variant. Do not cut a sound five-stanza post down to 190, and do not restate the wrong cap as a verification failure. Session proof (Sep 1, 2026, ARTICLE 178): emailing the article without the social section triggered a direct reprimand. The social section is part of the deliverable, never optional.

**NO SUBAGENTS. EVER.** This is a single-pass, your-own-output job. Do NOT call delegate_task, do NOT spawn subagents, do NOT delegate any part of the writing, revision, or delivery. Vinny has told us repeatedly: no subagents. Session proof (Sep 1, 2026): using a subagent during ARTICLE 178 triggered a direct reprimand. Write and deliver it yourself, in one pass.

## Recommendation shapes and how to implement each

Recurring reviewer recommendations and the exact implementation shape for each (add a contrast table, append a single edge-case sentence, add a depth mechanism paragraph, relocate a stat earlier, ground dense jargon, bridge a claim to its technical root cause). See `references/google-suggestion-patterns.md` before writing, and pick the matching pattern instead of inventing a shape.

**Additions-only revisions are not trimmed back into the outline's word band.** When the order is "implement these suggestions without touching the original," every original sentence stays byte-for-byte and the body necessarily lands above the band the outline set. Do not cut original prose to buy the count back, do not shrink the new blocks into stubs, and do not split the difference. Report the new count and say the rise is the additions, then stop. The band governed the first draft; it does not govern an ordered expansion.

**An in-place rewrite is not an addition, and the band still binds it.** When the recommendations replace whole paragraphs instead of appending blocks, the same gate that measured the draft measures the revision, so a body that lands above the ceiling is a failed deliverable rather than an accepted expansion. Close the overage inside the sentences you wrote and nowhere else: compress your own new phrasing until the body is back under the band, never take words out of a paragraph the recommendations did not name, and never drop a point they asked for. Every requested idea survives at the shorter length, because a first-draft block written to satisfy a reviewer is always longer than the idea inside it. Two rewritten paragraphs can carry a hundred words of overage; the fix is tightening those two, not touching the other twenty.

**An ordered expansion is new sections, not sentences wedged into old paragraphs.** When a reviewer asks for a whole missing dimension (the technical cause behind a commercial claim, the engineering controls that answer it, an audience the piece never named), give each one its own block at the seam where the argument needs it: after the claim it explains, before the section it sets up. Splicing new material into an existing paragraph makes the original sentence do work it was not written for, and the diff stops being a clean proof that nothing else moved.

## Critical Rules

1. **Apply ONLY the specified recommendations.** Do not touch anything outside the scope. Do not add your own improvements, polish, or fixes. "WITHOUT touching the original" means exactly that.

2. **Respect all formatting constraints.** If the user says "no em dashes," verify every new line you add. The patch tool does not auto-strip them. If they specify bold for certain phrases, apply it exactly. If they want a transition sentence between two sections, place it precisely there.

3. **Read the full article first.** A revision that references "the Coordination Layer section" only makes sense if you know where that section is and what it contains.

4. **Do not assume you know the structure** from the prompt alone. The article may have been edited since you last saw it, or you may never have read it before.

## Content Strategy: Optimize for the Distribution Model

When the revision source is a model (Gemini, Claude, etc.), understand what the model's feedback actually represents:

- **The model is a gatekeeper, not a critic.** Its opinion on quality reflects what the distribution algorithm rewards, not what makes good writing. Vinny's insight: "I can write the better article, but it won't be seen as much as the one Gemini views as more valuable."

- **Take the structural advice, filter the creative advice.** The model's suggestions about structure, keyword placement, formatting, and clarity are valuable because they reflect ranking signals. The model's suggestions about voice, tone, and creative choices are suspect, those are where your voice goes.

- **The goal is to inject your voice into the patterns the model ranks highly.** Not to write what the model wants, but to make the distribution machine work for you instead of against you.

- **When Vinny says "we always listen to Gemini about this type of thing,"** he means the structural and distribution-oriented feedback. The model determines whether the content gets seen. Ignore the taste, follow the math.

## House layout for ARTICLE ### COMPLETE .txt deliverables (match ARTICLE 194 COMPLETE)

Vinny's accepted final-article layout is the one in `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/ARTICLE 194 COMPLETE.txt`. Copy that shape exactly:

- **Full paragraphs, one paragraph per line, unwrapped.** Do NOT hard-wrap body text to a column width. Hard wrapping reads as "the text goes across half the page" and has drawn direct anger. Long lines are correct; a 1,000+ character paragraph line is normal here.
- **One blank line between blocks.** Headers get one blank line before and after.
- **Title on line 1, normal case, never ALL-CAPS.** Then ONE byline line: `By Vinny Barreca, PhantomByte. September 19, 2026.` Do not use separate `By` and `Date` lines.
- **Section headers are `// HEADER` in caps**, no trailing period, no leading space.
- **Social block**: a plain `==========================================` separator, then the labels `X POST`, `PINTEREST TITLE`, `PINTEREST DESCRIPTION`, `QUICK KEYWORDS` each alone on their own line, with the content under them. No `(190 characters max)` or similar scaffolding, and no `SOCIAL AND DISTRIBUTION` banner.

When producing a new `ARTICLE ### COMPLETE.txt`, read ARTICLE 194 COMPLETE first and mirror it. Verify before sending: `grep -n '^// '` (headers present, no leading spaces), `grep -c '^$'` (blank lines present, not zero), and confirm the longest paragraph line is in the hundreds of characters, not 79.

**Before writing ANY new article deliverable, read the most recent accepted one in the same folder and copy its shape.** Do not invent a house style from the skill text alone, and do not fall back on your own defaults for line length, byline, or section markers. The accepted deliverables are the specification. A quick way to confirm the shape of recent work, and to prove your own default is the outlier:

```bash
for f in $(ls -t /mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/*.txt | head -12); do
  ln=$(awk '{if(length($0)>m)m=length($0)}END{print m}' "$f")
  printf "%-70s longest=%s\n" "$(basename "$f")" "$ln"
done
```

If the recent files show longest lines in the hundreds of characters and your new file shows 79, your default is the bug. Fix it before delivering, not after he reads it.

## Pitfalls

- **A data-drop file's date is not the story's date.** A daily data drop is dated by collection, not by publication, so an item summarized in today's file can be a re-surfaced story with a months-old original: one entry dated the drop day traced to a source article published in June. Open the named outlet, and put the date and headline printed on the LIVE page into SOURCES. When the drop date and the live page disagree, the live page wins. Carrying the drop date forward as the story date writes a wrong fact into a revised article.
- **The data file's headline is a paraphrase.** Summary files condense and sometimes retitle an item. Cite the publication's own headline, author, and URL, and grep the saved page for the numbers you intend to reuse rather than trusting the summary's phrasing. Where the outlet's figure and the summary's figure differ, use the outlet's.
- **A URL carried in from an outline or a draft can be a guess.** Vendor and news blogs use long slugs that do not match the headline, so a guessed URL can 404 or land somewhere else. Search the outlet for the headline, take the canonical URL, then fetch that. Do not call a claim unverifiable on the strength of one guessed URL.
- **NEVER hard-wrap a delivered article to a fixed column width.** Column wrapping is the single most-repeated formatting failure on these deliverables. Write full paragraphs and let the reader's client wrap them. Also never post-process a finished .txt through a normalizer: it strips `//` markers, adds trailing periods to headers, and reflows the text.
- **When a deliverable comes back mangled, trace it through YOUR OWN scripts before blaming a tool or the environment.** The damage is almost always self-inflicted by a reflow or "repair" pass, not by an external normalizer. Owning the cause matters: blaming an unidentified external tool ends the investigation, so the real defect survives into the next delivery.
- **Pass an explicit `workdir` on the cleanup command that deletes your scratch dir.** The terminal session is persistent, so deleting the directory you are currently standing in leaves the shell with a dead cwd and the next command fails before it runs. Either run the cleanup from a stable directory or pass `workdir=~`.
- **NEVER post-process a finished .txt article through a reflow, unwrap, or "clean up" pass.** Those passes have destroyed the `//` section-header markers (turning `// HEADER` into ` HEADER.` with a leading space and trailing period), collapsed the blank lines between paragraphs into a wall of text, and re-imposed column wrapping. Always write the article fully formed in ONE `write_file` call with the exact intended formatting, headers included, then verify with `grep -n '^// '` plus a heading-orphan check (`grep -n '^ [A-Z]'`) before delivering. If a file does come back mangled, rebuild it from scratch with `write_file`, do NOT repair it with string passes.
- **A rewrite that collapses blank lines is a broken rewrite.** When rebuilding a formatted article programmatically, a dedupe pass over blank lines can strip the paragraph separation entirely, producing a wall of text. Verify `grep -c '^$'` is non-trivial (dozens of lines, not zero) before delivering.

- **Shortening / "shorten by X%" jobs: rewrite clean ONCE, don't trim word-by-word.** When Vinny says "shorten this by 30%" (or "make it fit"), compute the target up front (original_chars × (1−reduction), e.g. 3250 × 0.70 ≈ 2275), then write the whole document fresh against that number. Do NOT do incremental shaving passes against a running char counter, that loops forever, re-saves near-identical text repeatedly, and never converges. Fixed blocks (links, contact info, About boilerplate) barely shrink, budget them first, then cut body copy hard. Verify the final count in code, deliver ONE version, and move on.
- **"Done" / "stop" means stop, no more file touches, no more re-saves.** If Vinny calls a deliverable done or tells you to stop, DO NOT write to the file again, even to "fix" or "improve" it. Continuing to rewrite a file after he said done is a worse violation than the original miss. Acknowledge specifically, change behavior in the moment, and stop.
- **Missing items from the prompt**, the most common failure. After applying all changes, re-read the original recommendation list and check each one off. If you applied 2 of 4, you missed half the work.
- **Three or more insertions: drive them from one script that asserts every anchor, then diff.** Write a build script in a fresh scratch dir that reads the source, asserts `text.count(anchor) == 1` for each insertion point, applies each replace, and writes the new file. A paraphrased anchor matches nothing, the script exits clean, and a block goes missing while the file still looks finished; the assert turns that into a hard failure. Then prove scope with `diff` against the source, and read the hunk shape against the shape of the brief: an additions-only brief must show `NdM` hunks alone (lines added, nothing changed or deleted), while an in-place rewrite must show exactly one `NcN` changed-line pair per paragraph the recommendations named and no other hunk. Count it with `diff source new | grep -c '^[<>]'` and check the number against twice the paragraph count, so a stray edit anywhere else in the file shows up as arithmetic that does not close. Then re-check the source's size and `mtime` are unchanged. Patch-by-patch is fine for one edit; it is fragile at three.
- **Patch `old_string` not unique**, `patch` rejects a non-unique anchor ("Found N matches"). Widen the anchor with surrounding context. Don't `replace_all` a targeted insert.
- **Patch block-replace drops body text**, when swapping a heading + paragraph, re-emit the full original body in `new_string` or the intro sentence silently disappears. Verify by reading the edit site back after patching.
- **Patch 'Escape-drift detected' error on quoted text**, when `old_string`/`new_string` contain double-quote characters, the patch tool can reject with "Escape-drift detected: old_string and new_string contain the literal sequence '\"' but the matched region of the file does not." This is a serialization artifact, not a real mismatch. Fix: re-read the file with `read_file`, then reissue the patch passing the strings WITHOUT backslash-escaping the `"` characters. Do not add backslashes before quotes.
- **'Assumed knowledge' revisions**, when Google/editors flag acronyms (F1, KV cache, LLMs) for a specialized audience, define each on FIRST use only, inline in parentheses (e.g. "(F1 is the harmonic mean of precision and recall, ...)"), and do NOT re-define later uses. For metric-flip claims (e.g. a correlation that changes sign between panel sizes), add one clause explaining WHY the small sample created a false narrative so the number lands for a general reader.
- **Adding unrequested improvements**, the user's instruction "WITHOUT touching the original" means exactly that. Do not fix typos, rephrase sentences, or add content that wasn't requested.
- **Emailing an identical file framed as a completed revision**, if a recommendation is ALREADY satisfied in the draft, do NOT copy the file, email it, and present it as a finished revision. That wastes the user's time and reads as a fake change. Tell him up front: "this recommendation is already in the draft, nothing to change, want me to strengthen it anyway?" and let him decide before you email anything.
- **Re-sending the same unchanged file under new names**, if the user rejects a delivered file, STOP and figure out what's actually wrong before creating another copy. Do NOT keep `cp`-ing the draft to a new filename (COMPLETE, FINAL, REVISED) and re-emailing it, that's the same wrong file with a new name, and it compounds the trust damage. When the user says "it's wrong," the first move is to ask what specifically is wrong, or re-read the draft for a rule violation (ALL-CAPS title, em dashes, etc.), not to generate another identical copy. Three identical sends in one session is three too many.
- **Editing the original draft file in place**, when the task says "revise ONLY ... WITHOUT touching the original," copy the draft to the new filename FIRST, then apply every patch to the copy. Never run a patch against the draft file itself. If you accidentally edit the draft, revert it immediately before continuing.
- **"Move this earlier" / "highlight this earlier" is TWO edits, not one.** When a recommendation asks to surface an existing stat higher, you must both insert it in the earlier location AND revise the later paragraph that originally introduced it so it refers back instead of re-deriving the number. Doing only the insertion leaves the stat stated twice as if it were new, which reads as an authoring mistake. Preserve every remaining sentence of the later paragraph verbatim and change only its lead. Verify with `diff`, a relocation shows MORE than one changed line; a one-line diff means you built a duplicate.
- **Em dashes in revisions**, if the user says no em dashes, check every new line you add. The patch tool does not auto-strip them.
- **Assuming you know the structure**, read the full article first. A revision that references a section by name only makes sense if you know where that section is and what it contains.
- **Skipping the final read-through**, the most expensive mistake. A missing recommendation means a second round of edits and user frustration. Always do the final check.
