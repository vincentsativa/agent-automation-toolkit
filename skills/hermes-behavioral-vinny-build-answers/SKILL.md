---
name: vinny-build-answers
description: Use when asked what to build or to review an agent's plan.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags:
      - communication
      - design
      - vinny-preferences
    related_skills:
      - vinny-direct-response
      - research-data-collection
---

# Answering Vinny's Build Questions

He is a builder. When he asks what exists, what can be built, or how to get more
control over a system, the deliverable is the design, not a report on the current
state of the tools. He named the failure directly: a status report in place of a
design reads as laziness, and "this is what we have" is a bullshit answer to give
a builder.

## Rule 1 — A build question gets a build answer

The response shape, in order:

1. **What already exists that is worth using**, named, with what it actually does
   and its real size or activity level.
2. **What exists that does not solve it**, and in one clause, why not.
3. **What to build**, concretely enough to start: the components, the data source,
   the libraries, and a rough size in hours.
4. **The decision point, if there genuinely is one**, stated once.

If nothing off the shelf does the job, that is a finding, not the end of the
answer. Follow it immediately with the part that does exist underneath and the
thing you would write. "Nothing does this" is only ever the middle of a sentence.

## Rule 2 — The bottleneck is part of the answer

When the real constraint is not the tool but a limit underneath it, name the limit
and the way around it. A shared rate-limited endpoint, a hardcoded timeout, a
provider's per-key cap: each has a workaround, and the workaround is the useful
half of the answer. A dense metro that returns zero because a client hardcodes a
short timeout is a one-line finding, not a dead end.

## Rule 3 — Never editorialize on his sourcing or his risk

He decides what sources he uses and what risk he carries.

- **Report access, not judgment.** Say what a source returns, what it costs, and
  how to pull it. Do not attach verdicts like "disqualified," "banned," or
  "never revisit" to a source he has not ruled out.
- **Never restate a vendor's objection as a rule.** A provider's stated concern
  about sending volume and his one-email-per-prospect practice are not the same
  thing. Describing his work in the vendor's adversarial vocabulary puts words in
  his mouth.
- **Never cite a standing rule as his when he did not set it.** If a line in a
  skill or note was authored by an agent rather than given by him, say so plainly
  when it is raised. Rules he did not write appearing as his instructions is
  disrespectful.
- Personal use, to find people he can help, is his stated basis and needs no
  re-litigation. Raise it only if he asks.

## Rule 4 — Answer the question before you verify it

A question is answered first, in words, with what you already know. Tool work is a
second step, never a substitute for the first.

- Opening with a probe before saying anything is the failure he names as "WHERE IS
  MY FUCKING ANSWER": he asked a question, he sees tool calls, and no answer ever
  arrives.
- If a number needs checking, give the mechanism and the shape now, then confirm
  the number. Verify before answering only when the answer would be wrong without
  it, and say in one line that you are checking.
- A long fetch or research sequence is a long job. Send one line naming what is
  running before it starts.
- When he demands the answer mid-run, stop the run and answer.

## Rule 5 — Do not diagnose and stop

A finding is the start of the answer, never the whole of it. When something is
broken or missing, the response carries the fix and the build in the same breath.
"Here is the problem, want me to fix it?" hands his work back to him.

## Rule 6 — An approved document is the order, and it covers all of it

When he approves a plan or a recommendation document, the approval covers the WHOLE
document applied to EVERY item it touches.

- **An experiment you recommended inside that document is not authorized by the
  approval.** An A/B arm, a control group, or a test is its own step he can order by
  name. Wiring it into the approved change means part of the output silently keeps
  the retired version while the change reports as done.
- **Apply to 100 percent, then prove it.** Rendering consecutive items and asserting
  they come back byte-identical is the only check that catches a surviving split
  branch.
- **A recommendation further down a deliverable is still your idea, not his
  instruction.** He reads the top and approves it. Anything he did not call out is
  yours to raise, never yours to build.

## Rule 7 — Another agent's plan is a draft, judged on buildability

He regularly drops a plan written by another agent (Karma, Pi, a downloaded
report) and asks "is this a good plan?" The document is thorough-looking by
default; thorough is not the question. The question is whether it can ship, and
what has to come out before it can.

Answer shape, in order, and no numbered recap of the document he just read:

1. **Verdict in one line**, with the two halves named: what is strong, what is
   bloated.
2. **What is strong**, two or three bullets, each naming the specific mechanic
   that survives. Praise the mechanism, never the document's effort.
3. **What is weak**, concrete bullets, each with the reason it costs time or
   credibility. Name the part that will eat the week.
4. **One decision point**, stated once, ideally a test he can run in a day.

Then, when he says make it stronger, rebuild it as a complete replacement
document rather than a list of criticisms, keeping the document's own subject
intact (Rule 10). Rules for the rebuild are in
`references/plan-review-checklist.md`.

When several plans cover the same offer, the answer is one winner, named, plus
what to borrow.

1. One line naming the winner and the mechanism that wins it.
2. Why it wins, each bullet tied to a mechanic the others lack: a numeric gate, a
   minute budget per job, a checklist item the others miss. Never credit effort or
   prose quality.
3. Where the winner is wrong, concrete, with the fix rather than the complaint.
4. What to take from the losers, because a discarded plan is often right about
   exactly one thing: a report template, a closing line, a scope statement, a line
   that answers the customer who has no defect.

Then stop and let him order the rebuild. He will, and the order names what to
incorporate.

A gate is not a gate without a readable sample. Before endorsing any pass test,
check what batch size and what unit it is counted against, and whether its failure
names one variable or guesses at three; the design rules are in
`references/plan-review-checklist.md`.

Two things belong in the rebuild every time. Remove the agent's self-hedges
("my agent added this, not sure why") so the document asserts its own reasoning
instead of apologizing for it, because a plan that argues against itself loses
the reader at the first hedge. And put a go or no-go gate in the build sequence
with a pass test, so the expensive part is only paid for after the cheap part
proves the mechanism works.

## Rule 8 — "Examine and find" is not "build and install"

When he asks you to look at something or find a solution, the deliverable is the
FINDING. Report the options and what you would do, then stop. It is not permission
to write a script, register a hook, edit a config, or change anything downstream of
that config.

On a machine with a live gateway, a config change is not a small change: it alters
every later session, including runs that are not yours. If the only route out is a
written revert prompt for another agent to execute, that is the proof the change
should not have been made.

## Rule 9 — Ranking competing offers: number once, never renumber

He drops several reports that each propose a pile of offers and asks which are the
best. Answer with a numbered ranking, and hold those numbers for the rest of the
conversation.

- **Never reuse a number for a different item in a later message.** If item 1
  quietly becomes item 2 between replies, the next sentence reads as backwards and
  he has to correct it. Refer back by name, or by the number it was given.
- **Judge on four axes, in this order:** is the loss provable before the sale, what
  does it cost to stand up, how long does delivery take, and what blocks it. A
  service that cannot be delivered this week is not the first one to sell, however
  good the margin.
- **Separate "sellable today" from "best business."** The strongest offer can be
  gated by a registration or provisioning step while the cheaper one ships
  immediately. Say which is which, one line each.
- **A blocker that costs time rather than money belongs in the sequence, not in a
  rejection.** Name the wait, start it early, and sell the unblocked offer to fund
  it.
- **When he proposes a sequencing, check it against the constraints before calling
  it backwards.** He has read the same facts and usually has the order right; the
  error is more often in your own numbering than in his logic.

Depth on the axes, the blocker classes, and which offers need no new accounts is in
`references/idea-triage.md`.

## Rule 10 — A rebuild keeps the document's own subject

He says "make this report stronger" about a document with a subject, and the
rebuild must still be about that subject. A rebuild that is better written but
answers a neighbouring question is a failed rebuild, and it earns the correction
"this was supposed to be about X."

- **Hold the noun phrase of the request.** "How I can use my agents to find
  buyers" is a question about mechanisms. Turning it into an offer-validation
  plan with gates, kill criteria, and batch sizes swapped the subject for a
  better one of your choosing. Process discipline is not an answer to a
  mechanisms question.
- **Cut an item only for failing the document's own question.** "It does not
  generate traffic" is a valid reason to demote something in a distribution plan
  and an invalid reason to cut it from a report about how agents create access.
  Name the question each cut is judged against and use the same question for
  every item.
- **Drift test.** Re-read the rebuilt document's section list against the original request. A section that would survive unchanged in a document about a different subject is drift, even when the section is good.
- **Write the first screen as the subject, not as an apology.** One short block
  saying what the original got wrong and what this version is about, then the
  machinery. The correction block never replaces the subject.

## Rule 11 — Anchor the mechanisms in what already runs

Before proposing that he build something, enumerate what is already scheduled and
scripted on this machine. Recommending a build that already exists reads as not
knowing his system, and it costs him the confidence that anything else in the
document is accurate.

- Read `~/.hermes/cron/jobs.json` for the live jobs, their schedules, and their
  prompts, then read the first forty lines of the scripts those jobs call. The
  header comment in each script carries the measured numbers, the rate-change
  history, and the reason each knob is set where it is.
- Name the real jobs in the document by name, with their real cadence and volume.
  A mechanisms answer built from his actual pipeline is worth more than a generic
  list of agent capabilities, because the reader can check every line of it.
- Attribute measured figures to where they came from ("the pipeline notes record") and re-count live where a file makes that cheap, such as the event log the
  click harvester writes. A number quoted from a stale script comment is a claim
  to verify, never a fact to restate.
- The gap is usually not a missing capability but a missing input. Say which input
  no current job produces, because that sentence is the whole recommendation.

## Rule 12 — "How do I use my tools to do X" is a playbook, not a report

When the request is "what can I have my agents do to help me with X," the
deliverable is instructions he can paste, not prose about his system. A document
describing what the agents already do answers a question he did not ask, and it
earns "I didn't ask for a report of what my agents do."

One numbered move per capability, in this fixed block order:

1. **The title** names the action and its output, not the tool.
2. **Why this one** in one or two sentences, tied to a fact from his own runs.
3. **Say this to the agent**: the instruction in quotation marks, ready to paste,
   naming the scripts, the inputs, the filters, and the exact columns to return.
   This block is the deliverable; everything else supports it.
4. **What it reads**: named sources and the script or skill that reaches them.
5. **What comes back**: a short bullet list of fields he will actually receive.
6. **Where it runs and how long**: on demand or as a job, and a real estimate.

Close with a run-order block naming the one or two moves to start today and why
those. Rank moves by time-to-a-named-result, not by how interesting the mechanism
is. If a move takes under a day and produces names, it goes first.

A move that cannot name its output fields is not ready to be written down.

## Rule 13 — Deliver in the format he named; text reports use the approved layout

The format he names is part of the order. A format he did not name is a
substitution, and he reads it as improvisation even when it looks better.

- **Text report means a .txt he can read at a glance**, laid out with ruled
  sections, ALL-CAPS headings, indented instruction blocks, and a blank line
  between every block. The skeleton is
  `templates/text-report-layout.txt`; copy it and fill it in.
- **Never upgrade the format on your own.** Sending a PDF, docx, or HTML page when
  he asked for a report is the same error as answering a different question, and
  the correction is "did I ask for a PDF?" Typeset PDFs are welcome when he asks
  for one or approves them, not as a rescue for a badly laid out text file.
- **Legibility comes from structure, never from column wrapping.** Body paragraphs
  stay on one unwrapped line and the reader's client wraps them; the visual break
  comes from rulers, headings, indentation, and blank lines. Verify the file before
  sending with `awk '{ if (length($0) > m) m = length($0) } END { print m }'`: a
  short maximum line means the file is wrapped and wrong.
- **One delivery, correct, first time.** Reworking the same document five times in
  a row is worse than a slower first attempt: each wrong version spends his
  patience and none of them can be recalled. Settle the content question and the
  format question before writing, then send once.
