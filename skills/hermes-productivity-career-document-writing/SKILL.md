---
name: career-document-writing
description: Use when writing Vinny's resume, CV, or job answers.
trigger: "Vinny sends a resume/CV and asks if it is good or says rewrite it; Vinny asks for a resume, cover letter, capability statement, or consulting one-pager; a recruiter emails screening questions about a role and he wants answers drafted"
---

# Career Document Writing

Resumes, CVs, cover letters, and capability one-pagers for Vinny. The document is a claim about him that a stranger will check, so the governing rule is evidence, not adjectives.

## When to use
- Vinny sends a resume or CV (usually `.odt`/`.docx`/`.pdf`) and asks whether it is good, or says rewrite it.
- Vinny asks for a resume, cover letter, capability statement, or consulting/services one-pager.
- Vinny sends a resume or CV back with ONE change to make ("word this differently", "change X", "drop that") and send it to him. That is an edit, not a rewrite, see the targeted-edit procedure below.

## Rule 0, Evidence or omission

Every bullet must answer "how big, how many, how long, how much." Numbers come from a live query run in THIS session, never from memory, never from a number carried forward out of `references/vinny-system-evidence.md`. A resume figure is a checkable fact; an invented one is a falsification he gets caught holding in an interview. His own resume text drifts too, so a count written inside it (published pages, scheduled jobs, article numbers) is a claim to re-verify, never a source to copy: re-run the query and use the live number even when the resume already states one.

If revenue, client names, or headcount cannot be verified, leave them out of the document and name the gap to Vinny in ONE line at delivery. Never fabricate a metric to make a bullet look stronger, and never present a choice about it: state what is missing and offer to add it if he supplies it.

## Procedure

### 1. Read the source document
`read_file` inlines `.docx` and text-layer `.pdf`. `.odt` needs the extraction recipe in `references/document-format-extraction.md`. Never ask him to paste the contents of a document he already sent.

### 2. Audit before rewriting, lead with the verdict
The first sentence of the answer is the verdict: good, or not good and why. Then class the defects by kind, so he can see what is structural versus cosmetic:

- **No evidence**, categories and adjectives where results belong. "Built and operated X" with no scale is not a credential.
- **Missing timeframes**, a work item with no dates reads as unverifiable. "2004–Present" on the background line does not date the current work.
- **Keyword dump**, a 14-line capability list standing in for substance. Keywords belong in a labeled TOOLING block after the evidence, not in place of it.
- **Role ambiguity**, a document aimed at employment, contract work, consulting, and projects at once cannot be read as any of them.
- **Format defects**, typos in the name, stray leading spaces, `.odt` for ATS ingestion.
- **Verb and tense drift**, "experimented with" and "lessons learned" read hobbyist; mixed past/present tense on ongoing work.

### 3. Build the evidence inventory
Re-run the live queries in `references/vinny-system-evidence.md` for every claim the document will make. Counts drift; a stale number is a lie with a timestamp.

### 4. Draft top-down
Order that works for his material: name/title/contact line → SUMMARY (the framing paragraph) → SELECTED WORK with number-heavy bullets → topic sections (technical SEO, services) → TECHNICAL WRITING → TOOLING as labeled lines → BACKGROUND → AVAILABILITY.

### 5. Verify before delivering
- `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>`, longest line must be long (body paragraphs are one unwrapped line each). Article 14; a wrapped file is rejected on sight.
- Check the name and any roman numeral character by character. `III` written as `lll` is the single most damaging typo on a resume.
- Grep for banned words and characters before delivery.
- Confirm every figure in the document matches the query output from step 3.

### 6. Deliver
Email both formats in one message via the `email-sender` skill: `.docx` for ATS and Word, `.txt` for plain reading. Confirm to Vinny in chat with the SMTP id and a short list of what changed; do not paste the document into chat.

## Targeted edits to a document he already has

"Word this differently" is an edit, not an audit and not a rewrite. The document is already his; only the named text changes.

1. Copy the source to a fresh scratch dir (`SCRATCH=$(mktemp -d /tmp/hermes-resume-XXXXXX)`) and work on the copy. Never edit the file in the cache directory he sent, and never regenerate the document from a re-typed draft, regenerating loses his styling and silently rewrites lines he did not ask you to touch.
2. Make the substitution at the file level per `references/document-format-extraction.md` (byte-level edit of `word/document.xml`). Do not rebuild the `.docx` with a layout script when one string changed.
3. Assert the old string occurs exactly once before replacing, and afterwards grep the whole file for BOTH the new string and the old term. The old term must return zero hits everywhere in the document; a partial match elsewhere is a defect, not a detail.
4. Confirm no other paragraph changed: print the full paragraph list and compare it to the text extracted from the original. Report the diff as one old line and one new line.
5. Email both formats in one message via `email-sender` (`.docx` for ATS, `.txt` for plain reading) and report the SMTP id plus the one-line change. Do not paste the document into chat.

### Flagging content risk without stalling

Some lines on his resume carry a legal or reputational edge, and he knows better than you what he can survive on a background check. Edit what he named, then flag the risk in ONE line and offer the strictly-safer alternative.

- Do not silently soften wording he did not ask you to change, quietly laundering a line is a change he did not authorize.
- Do not stall the edit behind a question. Do the work, deliver it, then flag.
- A euphemism is not automatically safer than the plain phrase. Industry-standard terminology is a signal to anyone who reads that industry; if the term he asked for is still a signal, say which wording carries none and offer that as a single line.
- Never present a menu. One line naming the risk, one line naming the alternative he can ask for.

## The application email (the note that carries the resume)

A resume he sends for a role travels inside a short email. That email is a candidate's note, not sales copy, and it is a different genre from cold outreach even though both go to a stranger by email. Getting the genre wrong is the failure that costs him the role.

- **Do not run the `socratic-sales-outreach` method on it.** That skill is for prospects, and its moves read as vendor language to a hiring manager: offering a free teardown or findings sheet, "no obligation," "whether or not this goes anywhere," price-against-pain questions. A job application offering a prospective employer a deliverable reads as someone selling services rather than someone who wants the job. The close asks for the job, in the form of a short next step, not a favor he has to evaluate.
- **Open on the work, not on his interest.** The strongest line is a specific, checkable observation about the employer's own product, taken live in this session: a real count, a page title that promises something the page does not deliver, a visible gap. Then the plan, then the background that matches, then the resume.
- **Verify every number and page claim against a live fetch in this session before it goes in.** A company count, a job count, a page title, a zero-state report: all checkable by the recipient in five seconds, and all stale the moment they drift.
- **The signature block is mandatory and is not something to leave off.** Every message he sends carries:

```
Best,
Vinny Barreca
Phantom-Byte.com (https://Phantom-Byte.com)
Articles.Phantom-Byte.com (https://Articles.Phantom-Byte.com)
```

  Read it from a recent message in his `Sent Items` folder rather than reconstructing it, and in the HTML part turn both URLs into anchors with the bare address as the visible text.
- **Attach the resume.** Find his current one (for example `~/RESUME_Vincent_Barreca_AI_Systems_Builder.docx`) rather than asking him for it, and confirm the attachment is present on the stored message.

### Staging it as a draft

Unless he says send, stage it and let him press send. The full procedure, the field checks, and the read-back verification for a draft are in the `scheduled-mail-staging` skill.

- Build the body ONCE into a plain part and an HTML part from the same string, so the two cannot drift.
- Write the body you actually intend, then read it back off the server and report any wording difference from what was quoted in chat. Re-typing the body while writing the staging script silently rewrites sentences he already approved, and a change he did not authorize is the defect, not the delivery.

### When he orders the service offer into the letter

His instruction overrides the genre caution below. When Vinny says to tell the employer about a service he runs and link the page, put it in, and do not raise the "reads as selling" objection as a reason to hedge or ask. Frame it as evidence of live hands-on work rather than a pitch for side work: what the tool does, what it proves, and the mechanics behind it. Give the page as a bare URL on its own line so it is obviously a link. Fetch the page live in this session before quoting it, because pricing, turnaround, and deliverables drift.

### When he asks for a file on the desktop, not an email

"Put the text file on desktop" is a delivery order, not an email order. Write a plain `.txt` with body paragraphs as one unwrapped line each (Article 14), place it on the Windows desktop, and confirm the path in chat. Do not also stage or send email unless he asked for it. The Windows desktop is `/mnt/c/Users/<user>/Desktop/` for career documents, while the job reports that feed these applications sit beside it under `/mnt/c/Users/<user>/OneDrive/Desktop/`; when the destination is ambiguous, write where the most recent same-class deliverable already sits rather than picking blind.

## Answering a recruiter's screening questions (a different genre again)

A recruiter screening him by email asks a numbered list of capability questions and says "brief responses are fine." They are not fine. This is a technical interview conducted in writing, and the answers are read by someone comparing five candidates against a checklist. Deliver one text file he can paste from, and write it as the strongest technical answer per question.

1. **Get her exact wording first.** Fetch the full body, not the snippet. Answer in HER order, one headed answer per question, same nouns she used, so a reader scoring the checklist can find each one. Do not merge two questions into one answer and do not add questions she did not ask.
2. **Survey the real system before writing one sentence.** Never answer from memory of his stack. The checkable claims and their commands live in `references/vinny-system-evidence.md`; run the whole set plus the codebase-scale and execution-ledger queries now. Every number and every script name in an answer must come from output produced in this session.
3. **Lead each answer with the mechanism, then the result.** The pattern that lands: what the system does, in execution order, with the real module names, the real file, and the real count ("about 1,600 lines, with a 1,200 line test suite beside it"). A recruiter who has read forty answers of "strong Python skills" remembers the one that describes a gate chain and a 5 percent bounce circuit breaker.
4. **Name gaps inside the answer, in the middle of it.** This inverts the resume rule, where an unverifiable claim is simply omitted. In a screening email, volunteering "I have not administered Sitecore or AEM as a CMS administrator, and I would rather say that plainly than oversell it" buys credibility for every claim around it. Answer the gap with the transferable structure, then stop. Never let the omission do the work silently; the interviewer finds it at the technical stage and it reads as deception.
5. **Answer a doubt about him head on.** "You seem highly independent" is a real objection, not a courtesy. Do not politely agree with it. Name it, then show the structured part is already there (schedule, written standard, verification gate, documentation), and say what he wants from a team rather than what he would tolerate.
6. **Fold any extra depth into the answer it supports. Never an appendix.** When his instruction is "explain our content generation, the skills, the data collection, how we develop tone, the multi model selection," put each of those paragraphs INSIDE the numbered answer it argues for: data collection under Python automation, tone and voice under content QA, the skills library under role alignment, multi model selection under AI assisted development. A recruiter reads answers, not appendices, and she opened by saying brief responses are fine, so anything after the last answer is skimmed past or never seen. Never ask him whether to merge them and never hand him both an appendix and a choice; merge them, and drop the section heading so the document has exactly one answer per question he was asked. State the multi model selection as separated roles (mechanical reduction in code, independent ranking by more than one model on more than one harness, programmatic reconciliation) because that is the part that reads as engineering judgment rather than tool use.
   - **The document is in his first person, always.** These are his answers, sent under his name. No third-person reference to him anywhere ("Vinny asked specifically about..." is a defect, not a note), no bracketed asides addressed to the agent, no "paste this into the relevant answer" instructions left in the body. If a paragraph only makes sense as a note to you, it does not belong in the file. Grep the finished draft for his name and for any meta phrasing before delivering; the count must be zero.
   - **Never let the answers imply a model does everything.** He customizes every harness he runs, and a third of his scheduled work is script only. Say both plainly, because "my agent does it" undersells the engineering and is the first thing a technical screener will probe.
7. **Format and verify like any other career document.** Plain `.txt`, body paragraphs one unwrapped line each, no em dashes, no dash substitutions, headings and separators may be short. Verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>` and `grep -c $'\u2014\\|\u2013' <file>` returning 0 before delivering. Report the path in chat with a short map of what each answer covers; do not paste the file into chat.
   - **Email him the file as well, and prove it arrived.** "Did you email that to me" is the question he will ask, and a file written to disk is not an email. Send it to his own inbox as an attachment with a subject naming the version and what changed, then read it back from `INBOX` over IMAP and confirm the attachment size, the presence of the newly added passage, the longest line, and zero em dashes. A scripted SMTP send is not copied to `Sent Items`, so the delivered copy in `INBOX` is the only evidence that counts.


## Always-on rules

- **A message he sends carries his signature block.** Never stage or send an email on his behalf without it.
- **Never use "Founder."** He rejects the word. Use "Independent AI Systems Builder" or "Builder and operator."
- **No em dashes** anywhere in the document.
- **Never hard-wrap.** Body paragraphs are one long line; headings, separators, and bullets may be short. Verify with awk, never by eye.
- **`.docx` or text-layer PDF, not `.odt`.** Many ATS parsers fail on ODF.
- **Keep his voice, promote his strongest line.** The "this is a systems problem, not a model choice" framing is the best paragraph in his material and belongs in the SUMMARY at the top, not at the bottom under a closing header.
- **Rewrite means rewrite, not redesign the person.** Do not add sections, credentials, or framing he did not have and did not ask for.
- **One target.** A document aimed at every kind of engagement is read as none of them. If the headline is not a title a recruiter searches, say so in one line at delivery and proceed anyway, do not stall the work for a decision.
- **Do not undersell.** He owned a multi-million-dollar exit, runs a real multi-host agent fleet, and has published hundreds of original pages. State it plainly with numbers rather than hedging.
- **A limit named plainly beats scale implied.** When a posting asks for a scale he does not have (billions of messages, enterprise volume, a named platform's infrastructure), say the real scale in one sentence and pivot to diagnostic depth. Never let wording leave the reader free to infer a scale he cannot back.

## Reference files
- `references/vinny-system-evidence.md`, the verifiable claims about his system with the exact command that proves each one. Re-run every query before use.
- `references/document-format-extraction.md`, reading `.odt`/`.docx` sent by him, single-string edits to a `.docx` without a layout library, and generating a verified `.docx` from a plain-text draft.
