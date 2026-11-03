---
name: ghostwriter-terminal
description: |
  Vinny gives you a solid outline. You write the story. That's it.
  Single pass: outline → article → social post, Pinterest title/description, quick keywords.
  No style study, no research, no site reading.
---

# Ghostwriter Terminal

## Workflow

1. Read the outline Vinny gave you
2. Write the article (no em dashes)
3. Add: X post (190 chars), Pinterest title (60-80 chars), Pinterest description (150-300 chars), quick keywords
4. Save to `C:\Users\<user>\workspace\article-drafts\ghostwriter-terminal\YYYY-MM-DD-slug-draft.txt`
   - In WSL, the equivalent path is `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/`. Always translate Windows paths to `/mnt/c/` equivalents when writing files.
5. If Vinny asks to email the draft, use the `email-sender` skill to send it to hello@phantom-byte.com with the file attached. Do NOT paste the full article text into chat.
6. Deliver the Windows path

## Pre-Send Verification Checklist (Send-First Fix-Later Rule)

Never email the draft, then patch and re-email. Verify BEFORE sending:

1. **Em-dash count = 0**: Run `grep -c '—' /path/to/file.txt`. If output is not `0`, fix every occurrence before sending.
2. **X post under 190 chars**: Count characters including spaces.
3. **Title keyword-optimized after the body is written**, against the words a searcher would actually type. Keep the entity, the proper nouns, and the numbers. Never optimize before the article exists, and never let it become shortening into something generic. No all-caps words and no em dashes. See `title-formatting-rules.md` Rule 0 and Rule 0A. Report the final title in the delivery message.
4. **All outline references addressed in the body** (not just the sources section).
5. **Cross-references to prior PhantomByte articles** included where the outline names them.

THEN send.

## Fact-Checking Workflow (When Vinny Explicitly Requests It)

The default rule is no research loops. But if Vinny says "fact check it" or "use your browser skill to fill in the gaps":

1. **Identify every named claim** in the outline: specific people, quotes, dates, documents, numbers, URLs.
2. **Verify each with targeted searches** — not open-ended topic research. Check:
   - arXiv abs pages for papers (navigate directly to `https://arxiv.org/abs/<id>`, not search result "More" links)
   - Vendor sites for referenced reports
   - Daily data files (IronPulse, TensorFeed, blogwatcher) for supporting material
3. **If a claim cannot be verified** — omit it. Do not include unverified claims unlabeled. Adjust surrounding prose if the omission breaks the argument.
4. **Add a SOURCES section** at the end of the article listing every primary source URL used.

### Pitfalls

- **TechCrunch URL fragility.** TechCrunch slugs are auto-generated from headlines and can change between outline creation and verification. Multiple variants may all 404. The outline's guessed URL format is frequently wrong. Always check daily data files (IronPulse, TensorFeed, blogwatcher) for the actual canonical URL or shortened link (tcrn.ch) before marking a TechCrunch claim unverifiable. Session 2026-07-07 (Article 123): the Vercel CEO interview URL in the outline was a 404, but the interview content was fully reproduced in IronPulse with a tcrn.ch short link. Cite the daily data file as the corroborating source.

- **Dead outline URL rescue.** When a specific URL in the outline returns 404 or fails to load, do not mark the claim unverifiable immediately. Check the daily data files — they often reproduce the same announcement with correct sourcing. If the claim itself is confirmed there, cite the daily data file as the source. Only omit the claim if it cannot be corroborated by any primary source.

- **arXiv truncated abstracts.** arXiv search result pages truncate abstracts with a "More" link. Clicking that link via browser tools often fails with DOM box-model errors. Fix: navigate directly to `https://arxiv.org/abs/<id>` instead. The abstract page renders the full text immediately without expansion clicks. Session 2026-07-07 verified four papers this way in parallel (SwarmResearch 2607.02807, OCM 2607.02846, iFLYTEK-Embodied-Omni 2607.02542, Zombie Agents 2602.15654).

- **Vendor blog URL slug mismatch (especially NVIDIA).** Vendor announcement URLs often use long, non-obvious slugs that do not match the headline. NVIDIA, in particular, frequently uses descriptive slugs rather than short paths. The outline's guessed URL may 404 while the canonical URL lives in your daily data files. Always verify vendor URLs against the blogwatcher or IronPulse dump before marking them unreachable.

## If there's no outline

Ask for it. Don't proceed without it. Don't research, don't browse, don't study his site. Get the outline first.

## What stays out

No articles.phantom-byte.com. No style study. No research loops. No subagents. Outline in, article out.

Research exception: if the user explicitly requests fact-checking or browser research (e.g. "use your browser skill to fill in the gaps," "fact check it"), verify cited sources with targeted searches. Check arXiv for referenced papers, vendor sites for referenced reports, and any daily data files for supporting material. Do not perform open-ended topic research -- verify only the specific papers, entities, and claims named in the outline. See `references/research-playbook.md` for fast verification patterns and `references/arxiv-production-agent-cluster.md` for a pre-verified example of an arXiv source bank.