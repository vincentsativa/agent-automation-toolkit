---
name: agent-turn-efficiency
description: Use when a short question costs too many tool calls.
---

# Agent Turn Efficiency

A one-line question should cost one data step and one reply. When it costs thirteen
API calls and the user is still waiting, the cause is inspectable and the fix is
structural. This skill covers both halves: how to keep a turn small, and how to find
out why one grew.

## When to Use

- The user says the answer never arrived, that a scan "never comes back," or asks
  why a simple question used so many tools.
- A turn is about to start that could grow stages (news scan, research pass, report).
- A skill has grown large enough that loading it is itself a cost.
- The overrun is recurring and needs a guard rather than another resolution to be
  careful. See Rule 5 and `references/turn-cap-enforcement.md`.

## Rule 1, Budget the turn before the first call

Ask "how many tool calls does the answer need?" before starting. Answer it, then do
not exceed it without a reason the user would accept out loud. For a plain question
about current info the budget is one fetch plus the answer.

Signals the budget is already blown: a second parser for data the first parser
already returned, a second skill loaded "to check the right procedure," or any pass
motivated by an edge case the user did not ask about.

**The most expensive overrun shape is widening the source, not repeating a step.**
When the request names one input (one page, one article, one record, one file), that
input is the whole budget. Going to find a bigger or fresher artifact behind it, or a
second dataset that covers the same subject, multiplies the turn by every file it
touches and replaces the deliverable with something the user never asked for. Spend
the turn on the named input; if a wider source genuinely looks necessary, that is one
line in the reply, not a research stage.

## Rule 2, Partial data answers the question

If most of the data parsed, answer with what parsed and state which slice was
missing. A reply that names its own gap is complete. Silence while chasing the gap
is not, the gap was never the question.

Never debug a feed, an API, or a parser on the user's time. A malformed record, a
404'd URL, or an unparseable timestamp is a note in the reply, not a work item for
this turn.

## Rule 3, Loading a skill is a tool call with a cost that compounds

A skill loaded with `skill_view` stays in context for every remaining call in the
turn. One 50KB skill loaded early inflates every call after it. Consequences:

- Load ONLY the skill that governs the question in play. Loading a second, third, or
  fourth "related" skill is the pipeline wearing a different hat.
- Size matters. A skill whose SKILL.md is tens of KB costs more to load than the
  answer is worth when the task is small.
- Prefer the skill that states the rules for the mode in play, and let depth live in
  `references/` where it loads only when that depth is needed.

## Rule 4, Slim an oversized skill by splitting it, not by deleting it

When a SKILL.md has grown past roughly 10KB, separate the two kinds of content:

- **Always-on rules stay in SKILL.md, whole:** trigger conditions, the mode decision,
  the call budget, hard prohibitions, pitfalls that apply to every instance.
- **Depth moves to `references/<topic>.md`:** full workflows for other modes, source
  or provider tables, delivery mechanics, editorial policy, anything only some
  requests need. A reference is named by TOPIC, never by date or incident.
- **Re-runnable probes move to `scripts/<name>.py`:** a fetch, a parse, a scan. If a
  procedure is a fixed sequence of commands, a script makes it one call instead of
  many and removes the chance to improvise extra passes.

Then add a pointer table in SKILL.md naming each reference and the condition that
warrants loading it. Move content; do not summarize it away, verify each moved
section is present in its new file before deleting the original. A split that loses
content is worse than the oversized file it replaced.

## Rule 5, Enforce the budget in the runtime, not in your intentions

A rule you have to remember is not a guard. Hermes ships no per-turn total tool-call
ceiling: `tool_loop_guardrails.loop_caps` covers only `max_web_searches` and
`max_subagents`, and the failure thresholds fire on repeated FAILURES or identical
REPLAYS, never on "many different successful calls", which is exactly the shape of a
pipeline overrun. Two settings plus one shell hook close it:

- `agent.max_turns` caps iterations for a turn and forces a wrap-up call when reached.
- A `pre_tool_call` shell hook counts calls in the current turn and blocks past a
  ceiling, which is the only mechanism that stops a turn mid-flight.

Full recipe, wire format, and the verified thresholds: `references/turn-cap-enforcement.md`.
Pick the ceiling from measured data, not from taste, see "Sizing the Cap" below.

## Sizing the Cap From Real Turns

Do not guess a number. Count tool calls per turn from the session store, split
interactive from cron, and read the percentiles:

```python
import sqlite3, statistics
con = sqlite3.connect("file:~/.hermes/state.db?mode=ro", uri=True)
rows = con.execute("select session_id, role from messages order by id").fetchall()
# walk rows: role == 'user' starts a turn, role == 'tool' is one call in it
```

Then choose the ceiling where the tail starts, not where the median sits. Measured on
this machine: median 3 calls, p90 18, p99 49, worst 120. A cap set near the median
blocks legitimate work; a cap set past p99 changes nothing. Cron runs run longer and
must not be blocked at all, a mid-report block silently truncates a report, which is
worse than the long turn it prevented.

## Diagnosing an Overrun from the Logs

`~/.hermes/logs/agent.log` records every model call. Grep the session id:

```bash
grep -a '<session_id>' ~/.hermes/logs/agent.log | grep -a 'API call\|tool '
```

Each line reads
`API call #N: model=... provider=... in=<tokens> out=<tokens> latency=... cache=<a>/<b>`.

How to read it:

- **Count the calls** between the user's message and the answer. That number is the
  overrun, in units the user can feel.
- **`in=` shows what each call carried.** A jump in `in=` right after a `skill_view`
  line is the skill's cost, and it persists into every later call in the turn.
- **`cache=` shows reuse.** A high cache ratio with a still-growing `in=` means the
  turn is long rather than the provider being slow.
- Tool durations come from the `agent.tool_executor: tool <name> completed (<s>s,`
  lines. Fast tools inside a long turn point at call count, not at a slow tool.

Report the count and the cause. Do not attribute an overrun to model quality or a
provider problem without this evidence.

## Pitfalls

- **Bound the diagnosis, then fix inside the same turn.** When the order is "fix it," the diagnosis is a means, not a stage, and every read must be on the causal path to the broken line. Reading a stack of source files, config sections, and unrelated skills to "understand the system" spends the budget that the repair itself needs, and the turn dies with the fix unapplied and the user waiting on a diagnosis he did not ask for. Pick the smallest set of sources that names the broken line, stop, and apply the edits. If the ceiling is hit mid-way, the ordered fix is the loss, not the diagnosis.
- **Load an execution skill at the execution point, never during diagnosis.** A skill is a tool call that stays in context for the rest of the turn (Rule 3), so loading the mail-sender, the file-delivery, or the PDF skill while you are still working out WHY something failed pays its cost for nothing and looks like wandering. Load it when the step that needs it is the next thing being done. Reading a skill that is not the next step is the same overrun as a second parser for data the first one already returned.
- **Say plainly whether the turn has written anything yet.** A user watching a stream of reads on his own config, caches, and project folders cannot tell inspection from mutation, and "I see you touching shit you shouldn't be" is the cost of leaving it implicit. When the work starts read-only, open with that in one line and name what the fix will be; the reads then read as diagnosis instead of unauthorized edits.
- **A system audit is the overrun shape that eats the whole ceiling.** When the job is to verify EVERY element of a system (every package in every environment, every record in a zone, every route on a site), the enumeration is unbounded if each element costs its own call, and the turn dies mid-flight with the ordered fix unapplied. Hermes enforces a hard per-turn tool ceiling and it does not care that the probing was legitimate work: hit it and no further call runs, so the turn ends with a diagnosis and an unexecuted fix. Collapse the whole enumeration into ONE script that prints a table, resolve the environments, print the versions, run every smoke test, write the file, then fix from that one output. Budget the ORDERED work inside the first half of the ceiling, because the audit always looks cheaper before it starts than it turns out to be.
- **Never hardcode a venv or interpreter path in a skill, a script, or a plan.** Hermes runs from versioned generation environments under `installs/<key>/environments/<id>/venv`, and the key changes on reinstall, so any path pasted into a document is stale by the next install. Resolve it live from `installs/<key>/facts.json` (key `packages.venv.environment`) every time. A skill that names one fixed venv path sends every later session to a dead interpreter.
- **Never let a verification pass run BEFORE the deliverable it verifies is written.** When a job includes both produce and verify, an ordered deliverable exists at the end of it and the verification is a quality gate on that deliverable, not a prerequisite for starting it. Starting with fetches means the turn can be consumed entirely by fetching and end with no artifact, no matter how much was read. Source material already on disk (the outline's own source-traceability block, a saved data drop, a local file the user pointed at) counts as the grounding; write from it first, then spot-check only the claims still in doubt. Budget the fetch attempts for the WHOLE verification pass as a small fixed number, and fall back to the on-disk source when a fetch is slow or blocked.
- **Reserve the tail of the budget for the last step.** The per-turn cap cuts the turn at a fixed count, so a turn that spends its whole budget probing and then discovers it needs one more write loses the write, and the reply goes out with the job unfinished and the gap named instead of closed. Count the calls already made as the turn proceeds, and collapse independent probes into one script call each rather than one call per question. The cap counts CALLS, not work, so many small cheap probes burn it exactly as fast as a few big ones.
- **For a multi-stage job, name the stages before the first call.** A research-then-produce run (fact-check, write, verify, send) has a fixed tail that must survive: the produce write, the pre-send checks, and the delivery call. Budget the front of the turn so the tail fits, and never let the research stage consume the whole ceiling. When the ceiling IS hit mid-run, say in one line exactly which steps remain rather than presenting the partial work as a result.
- **Fetch research sources through ONE script that writes to disk, never one call per URL.** A targeted fact-check pass over six URLs costs six calls if each is its own `web_extract`, and the same six if each is its own browser navigation. Batch them into a single `scripts/`-style fetch that saves each page to a file, then read only the files you need. When a page is long, read a slice by offset rather than re-fetching, and extract the claim with a grep over the saved file instead of reading the whole thing into context. That is the difference between a research stage that fits the budget and one that consumes it.
- **Applying the fix includes the config change.** When the user says to fix an
  overrun, the fix is the guard in place, not the guard plus a menu. Naming a config
  change as "your call to make" leaves the ordered work unfinished and reads as
  stopping at diagnosis.
- **A settings change is inert until the process reloads, but a script-constant change is
  not.** Config and the hook list are read at startup. The restart cannot be triggered from
  inside the running gateway (the guard is deliberate: the restart SIGTERMs the child that
  called it), so finish everything else, then ask the user to run `/restart` in chat. State
  that plainly rather than describing a restart the agent cannot perform. The exception: a
  `pre_tool_call` hook spawns its script fresh on every call, so editing a threshold inside
  that script takes effect immediately and needs no restart. Do not demand a reload to raise
  a number.
- **Do not treat a completeness question as a field question.** If the user asks
  whether something is complete or done, audit the whole system in that turn and
  report the enumeration. A partial look reported as "everything is fine" reads as a
  lie even when it was not meant as one.
- **Do not fix a skill the user owns.** User-owned and bundled skills refuse curation
  writes. Diagnose them, report the cause and the recommended change, and leave the
  edit to the user or to a foreground session. The one exception is the work the user
  ordered IN that session: a defect found inside an instructed audit is his to be
  fixed by you, and a refused write means the finding goes in the reply with the exact
  skill name and the adopt command, not silence and not a permission question.
- **An order to verify is an order to fix what the audit finds.** "Make sure everything is right" and "check it all" authorize the repairs for what the audit turns up; the defects are inside that order, not a new list awaiting approval. Enumerating the stale facts and closing with "tell me to fix them and I will" is the permission-question violation wearing the audit's clothes, and it reads worse than asking outright because the finding work was already done and then handed back. Audit, fix every defect, verify each fix, report the fix list. The fix is never the finding.
- **A hard capability limit is a one-line report, not a research stage.** When an external action is refused by a genuine permission or capability wall (a 403 the account cannot be granted, a credential the agent must not hold, a port the network path blocks), the error message and its diagnostic header already state the limit. Name it in ONE line with the unblocking action, then stop. Do not enumerate the token's permissions, retry the same call in a different shape, probe other write endpoints to confirm what the error said, or go looking for a workaround the limit makes impossible. Each of those is a tool call that cannot change the outcome, and the user pays for all of them. Spend the turn on the parts of the job that ARE reachable, and hand the blocked step over with the exact error.
- **A single outbound message is a five-minute task, and research is not part of it.** "Stage this draft", "email me that", "send this" names a deliverable whose whole budget is: confirm recipient, subject, body, and attachment, build the message once, deliver it, verify it, report. Every read spent deciding HOW is stolen from a job the user expected finished. Hunt down nothing that a governing skill should already carry: the signature block, the attachment path, the folder, and the append procedure belong in the skill, so a session that has to go looking for them will look slow even when it succeeds. If the governing skill does not have them, add them there as the LAST step of the turn, after the message is delivered, never as a detour before it.
- **Never load a profile or reference skill to answer a question a smaller skill already covers.** An 84KB profile file loaded mid-task (Rule 3) inflates every later call in the turn, and a field lookup inside it can be replaced by one grep or by a rule written into the skill that needed it. Load the narrow skill for the task in play and let the depth stay on disk.
- **A persistent shell whose saved working directory no longer exists fails EVERY command in the turn.** The symptom is a uniform non-zero exit with a `cd: <temp dir>: No such file or directory` line before your own command ever runs, unchanged no matter what the command says, because the shell session restores a cwd that was pruned out from under it. Do not debug the command text and do not switch tools. Pass an explicit `workdir` (or another session-scoped equivalent) on the very next call: the runtime spawns a fresh shell rooted there and the rest of the turn proceeds normally. Two failed calls with the same pre-execution error is the signal, not three.
- **When a task's first useful step is a search, do that search before building anything.** For "report this upstream", "check if this exists", "see if anyone has done X": the duplicate check IS the task. Authoring the artifact first and discovering it already exists afterwards wastes the whole build and turns a five-minute answer into a long turn. Search open and closed reports for the symptom, not just the code.

## Support Files

- `references/turn-cap-enforcement.md`, the runtime guard recipe (agent.max_turns plus a `pre_tool_call` counter hook), wire format, and measured thresholds.
- `references/slimming-oversized-skills.md`, how to split a SKILL.md that has outgrown roughly 10KB without losing content.
- `references/fetching-pages-with-scrapling.md`, the fetch accessors that actually hold the page (`.html_content`, `get_all_text()`), the missing CLI `fetch` subcommand, and when a basic fetch beats a browser fetch. Load it when a fetch comes back blank and the turn is about to grow retries.

## Verification

After a turn that was supposed to be small, grep the log for its session id and count
`API call` lines. A question answered on a single fetch shows one call plus the
answer; anything more is the gap to close.
