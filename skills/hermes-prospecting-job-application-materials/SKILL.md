---
name: job-application-materials
description: "Use when Vinny orders a cover letter or form answers."
version: 1.0.0
platforms: [windows, linux]
metadata:
  hermes:
    tags: [jobs, cover-letter, application, writing, portfolio]
    category: prospecting
---

# Job Application Materials

## When to use
Vinny forwards a job lead and orders the application writing: a cover letter, an answer to an application-form question such as "examples of work" or "why this role", or both at once. The deliverable is a single unwrapped .txt on his Desktop holding every part, ready to paste into the employer's form. Sibling skills: `job-lead-screening` (which leads to apply to) and `remote-jobs-search` (finding them). This one is the writing.

## The order of work (do not reorder)
1. Read the lead's posting or attached notes for the role's actual beats, pay range and stated process. Those are the employer's own words and they belong in the letter.
2. Write the file before doing link research. The letter does not depend on the links and it is most of the value. Put PART 1 (cover letter), PART 2 (form answers) and a short NOTES block into `~/Desktop/<company>-application.txt` immediately.
3. Fill the published-work links in ONE bounded pass. One command gathers the slugs, one command checks liveness, then pick. If that pass stalls, the document already exists with its sections in place.
4. Verify before delivering: em dash count zero, longest-line check, every quoted link returns 200.
5. Deliver the file path plus a `MEDIA:` line, and name in one line anything he must fill in himself.

Why this order: the failure mode is burning the whole session on link discovery and handing back an empty desktop. He gives minutes, not hours, and a document that exists minus one refined line beats a perfect plan with nothing on disk.

## Published-work links (his portfolio)
- His published articles live at `https://articles.phantom-byte.com/`. Slugs and canonical URLs are inside the HTML files in `~/articles-phantom-byte/*.html` on the `rel="canonical"` line. One command gets them all:

```bash
cd ~/articles-phantom-byte && grep -h canonical *.html | sed -E 's/.*href="([^"]+)".*/\1/' | sort -u
```

- Never grep the whole home tree for his URLs, and never invent a URL. A fabricated portfolio link is the worst possible output here.
- Check liveness in one loop, which takes seconds for the whole pick list: `code=$(curl -s -o /dev/null -w "%{http_code}" -L "$url")`, keep the ones printing 200.
- Pick three to five. When his published beat and the employer's beat do not overlap (a food, lifestyle or trade publication versus his technology and consumer-analysis beat), pick the pieces that demonstrate the transferable skill: a research-driven explainer that traces a consumer symptom to a supply-chain cause, a consumer-economics piece written for a general audience, a trend and culture piece sourced from real behaviour rather than press releases. Say in one line beside each link why it was chosen. State the gap honestly in the answer instead of implying a beat portfolio that does not exist.

## What every letter must carry
- Open with the asset that maps onto the employer's beats, never with the job title. His standing domain asset beyond writing: roughly two decades managing restaurants, which makes food, grocery, restaurant-supply, menu-economics and staffing coverage first-hand knowledge rather than researched guesswork. Reach for the domain asset first whenever the role is food, hospitality, retail, grocery or operations.
- Then the writing record: his published article count since March 2025 (verify the count against the live sitemap before citing it, since he publishes daily), research-first sourcing, writing to an editor-set word count, same-day revisions, comfort claiming assigned stories from a queue rather than waiting on pitch approvals.
- Then the operational close: fully remote and set up for it, hits deadlines without chasing, treats editorial notes as notes, welcomes a paid trial.
- Address the employer's stated process when the posting names one (a paid trial article, paid training, a short form). It proves he read the posting.

## Format rules (standing preferences, binding)
- Plain .txt, unwrapped: one paragraph per physical line, no columns, no tables, no folding. Verify with `awk '{ if (length($0) > m) m = length($0) } END { print m }' <file>`. A body-paragraph file whose longest line is under a few hundred characters is wrapped and wrong.
- No em dashes anywhere, headings included. Check with `grep -c "\u2014" <file>` and expect 0. A single em dash in a heading fails the whole document for him.
- Section the file: PART 1 cover letter, PART 2 the form answers, then a NOTES block listing the exact link verification result and anything he must fill in.
- The agent does not hold his email or phone. Leave one bracketed contact line at the top and flag it in the reply. Do not go digging through config for it and never invent one.
- Report the verification numbers and the file path, not a description of the document.

## Pitfalls
- Never end a turn on research with the file unwritten. Link discovery is not the deliverable; the document is.
- Do not rewrite the whole file for a one-character edit. Use patch. If write_file refuses a full rewrite as stale, read_file the current content once and retry the write, rather than patching blind.
- Do not claim a link is live without the status check, and do not quote a published-article count from memory.
- When the session went long and he is angry, the acknowledgement is one specific line naming what was done wrong, with the fix already applied in the same turn. No excuses, no restating the task back to him.
