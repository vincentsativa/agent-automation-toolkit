# Slimming an Oversized Skill

The worked procedure for Rule 4 in SKILL.md, with the checks that make the split
provably lossless.

## When a Split Is Warranted

A SKILL.md past roughly 10KB, or one that has accumulated sections for several
different modes, is a split candidate. The tell is that most of the body is not
needed for most requests: a news skill that is asked for headlines nine times out of
ten still ships the cron cadence, the email transport, the editorial policy, and the
full long-form workflow on every load.

Do not split a skill that is already lean. Splitting adds a pointer table and a
discovery step, which is a real cost for a file that was fine.

## Procedure

**1 — Read the whole file and list its headings.** Heading level tells you which side
of the line each section sits on. Top-level sections that describe a different MODE
are the candidates to move; subsections that constrain every mode stay.

**2 — Classify each top-level section as always-on or depth.**

Always-on, stays in SKILL.md:

- Trigger conditions and the phrase list that picks the mode.
- The mode decision itself, stated as a short if/else on the words in the request.
- The call budget for the cheapest mode, with its prohibitions listed explicitly.
- Hard rules that apply to every instance: exclusions, dedup requirements, never
  modify config without an explicit instruction.
- Pitfalls that cost time on any run.

Depth, moves to `references/`:

- Full step-by-step workflows for the heavier modes.
- Source, provider, or endpoint tables.
- Delivery and transport mechanics (SMTP, file paths, output formats).
- Editorial or policy material for downstream content work.
- Variant modes (weekly, consolidated, no-research).

**3 — Write the reference files first, before touching SKILL.md.** Name each by TOPIC:
`full-report-workflow.md`, `rss-sources.md`, `cron-and-delivery.md`,
`editorial-workflow.md`. Give each a one-line header saying it is loaded on demand
and the condition that warrants it.

**4 — Verify the move is lossless before deleting anything.** For each reference,
confirm the sections landed by probing for content unique to each moved block:

```python
full = "".join(open(p).read() for p in moved_reference_files)
for probe in ["<unique heading>", "<unique literal>", "<unique command>"]:
    assert probe in full, probe
```

Count bytes before and after. Moved bytes plus the new SKILL.md should account for
the original; a shortfall means a block was dropped.

**5 — Rewrite SKILL.md around the rules.** Keep the mode decision, the cheap-mode
budget with its prohibitions, the trigger discipline, and the pitfalls. Add a pointer
table:

```markdown
## References — Load On Demand Only

| File | Load when |
|---|---|
| `references/full-report-workflow.md` | Full report mode: file, Desktop copy, output format |
| `references/rss-sources.md` | Locating a feed, parsing it, or a browser fallback for one source |
```

Close with the negative: "Do NOT load the full-mode, cron, or editorial references
for a quick scan." A pointer table without that line gets ignored on the cheap path.

**6 — Extract any fixed command sequence into `scripts/`.** If a mode is "fetch these
then parse like so," that is one script, not a set of instructions to re-derive. A
script also caps the turn: one call replaces however many the instructions would
have taken, and it removes the opening for extra improvised passes.

## Fixing a Stale Source URL Inside a Moved Table

Feed and endpoint URLs rot. When auditing a source table, probe EVERY URL in it, not
just the ones the current task touches. A table can carry several dead entries while
the one feed in use works fine, so a task-driven probe certifies a table that is
mostly broken. Walk the whole list in one pass and print status plus item count per
URL.

A 404 on a documented feed is a silent failure: the scan returns nothing, the run
looks like a quiet news day, and the next pass starts hunting for another source. When
a documented path 404s, find the working one and record BOTH the working URL and the
fact that the old path is dead, so the next audit does not re-try it.

Sites restructure feeds more often than they advertise: a `/ai-artificial-intelligence/rss.xml`
style path can move to `/rss/ai-artificial-intelligence/index.xml` with no redirect.

## Parsing Dates Out of Feeds and Search Feeds

Use `email.utils.parsedate` for RSS and Atom timestamps, not a hardcoded
`strptime` format. Feeds write zones inconsistently — `+0000` in one item and the
literal `GMT` in the next — and `strptime`'s `%z` accepts the numeric form while
rejecting `GMT`. The failure is total and silent: every item is skipped, the count
comes back zero, and the run looks like a day with no news. Google News search feeds
are the common offender.

```python
import datetime, email.utils
d = datetime.datetime(*email.utils.parsedate(pub)[:6], tzinfo=datetime.timezone.utc)
```

Prove a parser on the real feed before trusting it: print how many items parsed
versus how many were skipped. Zero-parsed-with-zero-errors is the signature of a
format mismatch, not an empty feed.

## Pitfalls

- **A reference file must not become a session log.** No dates, no incident
  narration, no "observed on <date>". Distill to the rule and the mechanism.
- **Do not leave the pointer table incomplete.** A reference that exists on disk but
  is not named in SKILL.md will not be loaded, and the content is then effectively
  deleted while appearing present.
- **Do not split across skills.** Splitting one skill's body across several skills
  multiplies load cost and creates trigger collisions; the split is SKILL.md versus
  its own references.
- **Re-check the size after the split.** If the new SKILL.md is still large, the
  classification was wrong and more depth belongs in references.
