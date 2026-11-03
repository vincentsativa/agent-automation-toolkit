---
name: phantombyte-content-writing
description: Write PhantomByte educational content - tutorials, barrier articles, challenge guides from Vinny's brief problem statements. Two-stage process first outline then email, then full tutorial then email on signal.
toolsets: [file, web]
---

# PhantomByte Content Writing

Educational content production for articles.phantom-byte.com, barrier articles, tutorials, and challenge guides.

## Trigger Phrases
- "write me a free tutorial outline for [BARRIER X / topic]"
- "write the tutorial and email it to me"
- Any BARRIER #N assignment with a problem/solution brief attached

## Two-Stage Workflow

### Stage 1: Outline

When Vinny provides a barrier/problem statement with solution framing:

1. **Write the outline**, full section-by-section breakdown with content notes under each heading. Map the complete article structure.
2. **Save to** `~/.hermes/workspace/` as a `.txt` file
3. **Email it** to hello@phantom-byte.com via email-sender skill with a brief summary body
4. **Reply in Telegram** confirming it was sent and briefly summarizing the structure
5. **Stop.** Wait for him to say "write the tutorial."

### Stage 2: Full Tutorial

When Vinny says "write the tutorial and email it to me" (or "write me this tutorial"):

1. **Load the outline** from `~/.hermes/workspace/`, it was already emailed so you may need to read it from disk
2. **Write the full tutorial**, every section from the outline, fully written, with the exact format specified below
3. **Save to** `~/.hermes/workspace/[slug]-tutorial.txt`
4. **Email it** with a concise summary body
5. **Reply in Telegram** with word count and structure confirmation

## EXACT TUTORIAL FORMAT, Follow This Precisely

Every PhantomByte tutorial must match the layout of the reference document ("Hardening Your Agent Against Prompt Injection: The 2026 Defense Playbook"). This is the canonical format. Do not deviate.

### Page 1, Header Block

```
PHANTOMBYTE TUTORIAL

[TITLE, Bold, attention-grabbing, benefit-driven]
[Subtitle line, clarifies scope or audience]

A PhantomByte Tutorial
```

Then immediately: a **real-world hook paragraph** that names a specific event, statistic, or scenario. Ground it in something concrete (a vulnerability, a news event, a common failure). This is not generic, it's specific and alarming/urgent.

### "IN THIS TUTORIAL" Section

```
IN THIS TUTORIAL
• [Section 1]
• [Section 2]
• [Section 3]
• ... (all sections listed as bullet points)
```

### Full Title Repetition

Repeat the full title on its own line, then:

```
OVERVIEW
```

2–3 paragraphs of context. The first paragraph names a specific real event or data point. The second explains why this matters. The third frames the solution.

### "THE QUICK-START – DO THIS FIRST" Section

```
THE QUICK-START – DO THIS FIRST

If you cannot implement all [N] layers today, start here. These [N] controls stop 90%
of real-world attacks and take under an hour to deploy.
☐ [ACTION ITEM 1, bold header then description]

[Description paragraph]
☐ [ACTION ITEM 2, bold header then description]

[Description paragraph]
...
```

Each action item is a ☐ checkbox with a **bold header** followed by a short description paragraph. Use the em dash ( – ) not a hyphen.

### Body Sections

Use numbered sections with the format:

```
## [SECTION NUMBER], [SECTION TITLE]
```

Within sections, use subsection numbering:

```
### [MAJOR NUMBER].[SUBNUMBER] [SUBSECTION TITLE]
```

Subsection content: bold headers for key concepts, short paragraphs (1–4 sentences), real examples.

### Code Examples

When including code, use this exact header format:

```
--- CODE EXAMPLE: [Name] ---
```

Then the code block. Include a `# Usage:` comment at the end showing how to call it.

### Checklists

Use ☐ symbols for action items and checklists throughout. Not dashes, not asterisks. ☐.

### "ACTIONABLE TAKEAWAYS" Closing Section

End every tutorial with:

```
ACTIONABLE TAKEAWAYS
```

Then 4–6 short, punchy paragraphs that summarize the key points. Each paragraph is a standalone takeaway, no sub-headers, just bold conviction statements. End with a final line that lands the point.

### Footer

```
*PhantomByte • phantom-byte.com*
```

### Formatting Rules

- **ALL CAPS** for major headers: PHANTOMBYTE TUTORIAL, IN THIS TUTORIAL, OVERVIEW, THE QUICK-START – DO THIS FIRST, ACTIONABLE TAKEAWAYS
- **Bold** for section titles within body text
- **☐ checkboxes** for action items, never dashes or asterisks
- **Short paragraphs**, 1–4 sentences, break often
- **Code blocks** with `--- CODE EXAMPLE: Name ---` headers
- **Numbered subsections** (1.1, 1.2, etc.) for body content
- **Em dash** ( – ) for section separators, not hyphens
- **Real, specific examples**, name actual tools, events, versions, dates
- **No AI-isms**, no "leverage," "synergy," "delve," "dive deep," "furthermore," "it's worth noting," "in today's rapidly evolving landscape"

## Tone & Style

- **Vinny's voice:** Direct, conversational, zero corporate language. He says "you're not stupid" not "users may experience confusion." He says "damn that was fast" not "I appreciate the efficiency."
- **No AI-isms:** No "leverage," "synergy," "delve," "dive deep," "furthermore," "it's worth noting," "in today's rapidly evolving landscape." Kill all of these.
- **Short paragraphs.** 1–4 sentences. Break often.
- **Address the actual barrier.** The emotional objection, not just the technical gap. Name the feeling ("you're staring at a blinking cursor"). Validate it. Then solve it.
- **Include real workflows.** Vinny's IronPulse, PhantomByte publishing, Hermes self-debugging, these are proof, not filler. Use them.
- **End with a one-sentence close** that lands the point.
- **Checklist/checkbox format** for challenge-based content. ☐ symbols for gamified completion.

## Content Structure Patterns

### Barrier Articles (like Barrier 8, 10)
```
Title: "What IS [X]? A Guide for People Who [real human situation]"
Hook: Name the feeling. Validate it. Promise the fix.
Sections:
  1. The 30-second answer (don't bury the lede)
  2. Kill wrong mental models first (what it ISN'T)
  3. Analogy that sticks (smart intern, GPS, etc.)
  4. How it works (simple diagram or numbered breakdown)
  5. Before/after examples (concrete, real)
  6. Vinny's actual workflows (proof, not theory)
  7. Address emotional objections ("I'm not technical," "what if it messes up")
  8. Quick win (first action in less than 5 minutes)
  9. Escalation path (what comes next)
  10. One-sentence close
```

### 30-Day Challenge Articles
```
Same structure as barrier articles PLUS:
- 4-phase overview table
- 30 daily tasks with checkboxes
- "Why this matters" and "What you just learned" for each day
- "What comes after Day 30" reflection section
- Share/journey close
```

## Delivery

- **Always email.** Vinny wants the content in his inbox, not spammed into Telegram.
- **Email body:** Brief summary of structure, word count, readiness status. The content is the attachment.
- **Telegram:** "Sent. ~X,000 words, [structure bullet]. In your inbox." Nothing more.
- **SMTP:** IONOS via email-sender skill (smtp.ionos.com:587, hello@phantom-byte.com)
- **Subject format:** "Barrier X: [Title], [Outline/Tutorial]" or "[Topic], Full Tutorial"

## Speed

Vinny values speed. "Damn that was fast" is the target reaction. When he says "write the tutorial," write it immediately, don't ask questions, don't re-load the outline unless you need to, just produce. The outline did the structural thinking. The tutorial is execution.
