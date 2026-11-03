# Google Suggestion Patterns (Aug 18 2026)

Two recurring Google/Gemini revision suggestions and how to implement them cleanly
without touching the original prose. Both are structural additions, not rewrites.

Most asks below are additive. Patterns 10 and 11 are the other kind: a paragraph the
recommendation names gets rewritten in place, every sentence replaced. Treat that as its
own shape, because a rewrite changes the body's word count and an addition's word count
is already accounted for elsewhere in SKILL.md.

## 1. "Visual Structural Layer" / "Quick Contrast Table"

Google asks to add a contrast table so a core structural difference "pops visually
for fast-skimming readers."

Implementation:
- NEVER render a markdown pipe table in a delivered PhantomByte .txt article. The format
  rules ban markdown symbols in the body, so a `|---|---|` row ships as literal garbage in
  the file he reads. The "contrast table" ask means a plain-text visual: aligned columns
  with ASCII spacing, or two labeled blocks stacked with a blank line between them. Pick
  the shape that survives being read as plain text. For the two-mechanism version of this
  ask, use pattern 6 below.
- Place the visual at the top of the relevant section, immediately after the section's intro
  sentence, before the body paragraphs.
- Cells are terse short phrases, not full sentences. Mirror the article's own
  terminology so the table and the surrounding prose agree.
- The no-em-dash rule applies INSIDE table cells too. Check every cell.
- Verify the intro sentence still flows into the table (no dropped sentence).
- Do NOT rephrase the section's existing paragraphs, the table is additive.

Worked example (ARTICLE 164, GPU scheduler):
| | FIFO Allocation | Constraint-Aware Allocation |
|---|---|---|
| Ordering | First come, first served | Priority across the whole horizon |
| Batch work | Waits for gaps that never come | Gets contiguous blocks in the troughs |
| Real-time inference | Fixed reservation holds GPUs all day | Elastic capacity from the gaps |
| Idle capacity | Stranded and reserved, not free | Reclaimed and placed in priority order |
| Latency | Protected by holding hardware hostage | Enforced inside the same optimization |

## 2. "Addressing Latency/Edge Cases" / "Single Sentence"

Google asks to add "a single sentence explaining how X guarantees Y during edge case Z
to preempt skepticism from risk-averse engineers."

Implementation:
- Append ONE sentence to the end of the most relevant existing paragraph.
- Do NOT add a new paragraph. Do NOT restate the whole mechanism.
- Use the article's own mechanism vocabulary (e.g. "re-prices the horizon in the same
  pass," "pulls capacity out of the lowest-priority batch work first").
- Name the specific guarantee (e.g. "p99 latency inside its SLA guardrail") so the
  objection is answered in place.
- No em dashes.

Worked example (ARTICLE 164): appended to the penalty-pricing paragraph:
"When a sudden traffic surge hits, the allocator re-prices the horizon in the same
pass and pulls capacity out of the lowest-priority batch work first, which is what
keeps p99 latency inside its SLA guardrail without pre-reserving GPUs that sit idle
the rest of the day."

## 3. "Add the missing engineering mechanism" (depth suggestions)

The most common shape now: the reviewer accepts the article and asks for one added
mechanism paragraph that connects a stated claim to the control plane. Typical asks are
"name the telemetry interface between the grid signal and the scheduler," "note the
state-recovery cost of shifting work," and "describe how a workflow degrades on purpose."

Implementation:
- Add ONE paragraph or sentence per suggestion, inside the section the suggestion names.
  Do not open a new top-level section for a depth suggestion, and do not restructure the
  article around it.
- Ground the added claim in a primary source (the vendor's own engineering blog, the
  standards body's own page) and add that source to SOURCES. If the added material is
  your own design guidance rather than a sourced fact, label it as opinion in the
  sentence itself.
- Every pre-existing paragraph stays byte-for-byte. Depth suggestions are additive.

## 4. "Move this stat earlier" / "Highlight this earlier" (relocation suggestions)

A relocation suggestion is TWO coordinated edits, never one insertion. Implement both,
or the stat appears twice and reads as an authoring mistake.

Implementation:
- Insert the stat into the earlier paragraph the reviewer names, using the article's own
  existing wording for the number so the two mentions agree.
- Revise the later paragraph that originally introduced it so it now refers back (for
  example "come back to the defect rate from the top of this piece") instead of
  re-deriving it. Keep every remaining sentence of that paragraph byte-for-byte; only
  the lead sentence changes.
- Restating the value is fine. Re-introducing it as new information is not.
- No em dashes in the inserted clause.
- The diff after a relocation shows more than one changed line. A single-line diff means
  you duplicated the stat instead of relocating it. Fix before sending.

Worked shape (a defect-rate stat moved into the hook): the hook gained one closing
sentence carrying the rate, and the later section's lead changed from "The number that
makes this concrete is the defect rate. Agents that falsely claimed full coverage missed
planted defects at roughly 1.8 times the rate..." to a callback such as "Now come back to
the defect rate from the top of this piece, because that is where the cost lands." The
three sentences that followed stayed identical.

## 5. "Unpack this, it gets technically dense" (jargon grounding)

Reviewers flag a section that jumps from prose into mechanism vocabulary with no bridge.
The fix is ONE grounding sentence, placed inside the dense paragraph right after the
mechanism is named, before the sentence that draws the conclusion from it.

Implementation:
- Open with a plain-language signal ("Put plainly,") then say what the mechanism does in
  terms a reader who has never built one can picture. Name the concrete operation and the
  concrete benefit, then stop.
- Keep the surrounding sentences byte-for-byte. The grounding sentence is additive and
  must not replace the mechanism sentence it explains.
- Do not expand into a tutorial. One sentence, then back to the argument.

Worked shape: a paragraph introducing cut-point replay gained (between the mechanism
sentence and the conclusion) "Put plainly, cut-point replay lets a developer mock the
non-deterministic LLM calls from the recording while the surrounding code runs live, so
the test exercises your real pipeline instead of a frozen transcript." The conclusion
sentence that followed was unchanged.

## 6. "Add an ASCII trace" / "give readers a visual anchor"

Reviewer asks for a short ASCII visual contrasting two mechanisms so a dense explanation
lands at a glance. This is the .txt-safe version of the contrast-table ask.

Implementation:
- Three elements, no more: a labeled OLD path, a labeled NEW path, and one line under each
  naming what changed. A third block is fine only if the article already contrasts three.
- Label the paths in caps inside parentheses, e.g. `OLD PATH (regex engine, one character at a time)`.
- Show the flow with arrows and bracket tokens (`text  -->  [ scan ] --> [ scan ]  -->  pre-tokens`),
  then a second line of plain words explaining the gain in the same vocabulary the prose uses.
- No markdown table syntax, no backticks, no em dashes. Verify by reading the block back as
  plain text: if a reader would see `|---|` on the page, it is wrong.
- Place it inside the named section, directly after the paragraph that introduces the mechanism
  it visualizes, and leave every surrounding paragraph byte-for-byte.

## 7. "Bridge a cost stat to the layer under discussion"

Reviewer asks to make an existing hardware-cost stat land on the section's own component
rather than sitting as a generic aside.

Implementation:
- Add ONE paragraph at the end of the named section, after the stat paragraph, before the
  section's closing line.
- Connect the two in three moves: name the physical dependency (the component being discussed
  is kept alive by the thing that got expensive), state the waste in that currency, and name
  the second benefit of fixing it (optimizing the component also lowers the expensive
  resource you have to provision).
- Reuse the stat's existing numbers and wording so the two mentions agree. Do not restate the
  figure as new information.
- The stat's own paragraph stays untouched; this is additive.

## 8. "Isolate the punchline for pacing"

Reviewer says the closing question is sharp and should hit harder.

Implementation:
- Split the closing paragraph so the question sits alone on its own line, with a blank line
  before and after it, and the setup sentence ends on the preceding line with a period.
- Keep both halves of the original sentence, and keep the section's following close
  paragraph exactly where it was. This is a line-break change, not a rewrite.
- The isolated punchline line WILL be short. That is correct here even though body paragraphs
  must never be short-wrapped: a one-line rhetorical question is a pacing device, not a
  paragraph. Do not let a wrap check flag it.

## 9. "Bridge the business claim to the engineering, then to the enterprise"

The engineering-audience gap review arrives as three asks on one article, and each has its own
shape. The article argued a legal, commercial, or policy point and never explained the machine
underneath it, so the reviewer says it reads as thought leadership for a business audience.

### 9a. Anchor the commercial claim in its technical root cause

Place ONE paragraph directly under the paragraph that states the commercial mechanism (under the
bucket, the exclusion, the pricing line), before the next structural block. Name the concrete
failure properties rather than the category word, then close on why the commercial actor behaves
as it does.

Worked shape (insurance exclusions): reasoning loops that revisit a step until they find an
unmodeled path, tool-call error rates that compound across a run so twenty calls at two percent
each leave a third of runs with a bad step, state space drifting as the context window fills so
the model that passed an eval at forty thousand tokens is a different system at four hundred
thousand, and indirect prompt injection arriving inside a document the agent was told to read.
The closing sentence states the underwriter's reason: no engineer can hand over a confidence
interval on any of it, so the exclusion is arithmetic, not caution.

Rules: the compounding figure must be your own labeled arithmetic (per-call rate, call count,
resulting share of runs), never an unlabelled statistic. Keep it to one paragraph. The paragraph
that states the mechanism stays untouched.

### 9b. Give the asks a section that answers them in code

When the article asks a question on the reader's behalf ("how do you bound the blast radius"),
add a section between that question and the checklist section, headed like any other, that
answers it in controls rather than paperwork. Four controls is the working length: a
deterministic validation layer between the agent loop and every side effect, permissions enforced
at the identity layer rather than in the prompt, circuit breakers that trip on behavior rather
than error codes, and an action log an auditor can read unaided. State in the opening sentence
what the controls buy, in the article's own currency (each one moves a failure mode out of the
excluded bucket), so the section ties back to the framework instead of reading as generic advice.

Rules: name the seam (no model output reaches an API directly), not the product category. Keep
each control to a short paragraph that says what it is and what it prevents. Do not turn it into
a tutorial with code the article cannot support, and do not disturb the checklist section below
it.

### 9c. Extend the example set to the enterprise reader

When the article's cases are consumer or consumer-integration workflows, add ONE paragraph at the
end of that section that names the enterprise equivalents in the reader's own vocabulary: internal
orchestrations that write to production databases, procurement agents that issue purchase orders,
planners that reroute inventory across regions, multi-agent pipelines where one subagent's output
becomes the next one's instruction. Then state the asymmetry in one line, sized in the reader's
currency: a personal agent that misfiles a complaint is a support ticket, an orchestration with
write access is a balance sheet event, and the policy was written for the support ticket.

Rules: name mechanisms, not vendors. Keep the section's existing paragraphs and closing line
byte-for-byte, and let this paragraph sit before the next section header.

## 10. "Do not bury this limit" / "clarify the threshold"

The reviewer says a caveat the article already makes is stuck where no reader will act on
it, usually as the last clause of a paragraph about something else. The fix is to promote
it in place and give it a decision, not to add a second paragraph saying it again.

Implementation:
- Rewrite that one paragraph, opening with the limit and its consequence. Drop whatever
  framing sentence the caveat was hiding behind; the paragraph no longer needs one.
- Convert the caveat into an adopt/skip rule in the reader's own terms: below the
  threshold the tool is overhead plus a new failure mode, so the reader should keep the
  simpler path, and the threshold is a number to test against rather than a rule to copy.
- Name the source's caveat as the source's, especially when it argues against the product
  that published it. A limit the vendor disclosed about its own product is the most
  credible sentence available, and losing it to save words is a bad trade.
- Keep every number and proper noun from the original clause. If the paragraph ran long,
  cut the framing, not the figures.
- This is a rewrite, so it moves the body's word count. Compress the new phrasing rather
  than trimming a paragraph the recommendation did not name.

## 11. "Tighten the pivot" / "make the distinction clear"

A closing section recommends a second vendor's guidance and the connection reads as a
list of two unrelated moves. The reviewer wants the mechanism split named before the
argument starts.

Implementation:
- State the split in two short parallel sentences, each naming what that vendor actually
  changes: one changes how the work is executed, the other changes how the system is
  structured. Name the mechanism, not the product category.
- Then place both on the axis the article already established, in the article's own
  currency, with one clause each: what the first one cuts, what the second one cuts. If
  the piece has a named bottleneck or toll, both sentences end on it.
- Keep the second vendor's evidence and its failure case. A pivot that drops the caveat
  to make the parallel tidy is the wrong trade, and the caveat is usually what keeps the
  section from reading as a vendor endorsement.
- Do not add a new section for this. It is one paragraph, rewritten in place.

## Proving the original was untouched when the additions land in several places

Patching a copy gets fragile once the revision adds blocks in 2+ spots. Writing the
finished file whole is fine, but prove the source was not touched either way:
- Record the source file's size and `md5sum` BEFORE writing anything.
- After the write, re-run `ls -la` and `md5sum` on the source and confirm both are
  unchanged, and confirm the new file contains every original paragraph.
- Sweep the new file for forbidden characters (em dash, en dash), markdown symbols
  (leading `#`, `**`), and ALL-CAPS words in the title, and re-count the X post
  characters, all before sending.
- The output path may be a Windows path (e.g. the Desktop) rather than the drafts
  directory. Write it where it was asked, and use the requested filename as the email
  subject when the user names the file.
