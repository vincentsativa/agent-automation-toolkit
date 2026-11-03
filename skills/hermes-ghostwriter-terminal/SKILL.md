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
2. Write the article (no em dashes). **Use the outline's title verbatim until the body is finished.**
2b. **Then optimize the title for keywords.** This is a POST-writing step: it runs on the finished article, against words a searcher would actually type, and the optimized title is the one that ships. Keep the entity, the proper nouns, and the numbers; the goal is findability, not brevity. Report the final title to Vinny.
3. Add: X post (190 chars), Pinterest title (60-80 chars), Pinterest description (150-300 chars), quick keywords
4. Save to `C:\Users\<user>\workspace\article-drafts\ghostwriter-terminal\YYYY-MM-DD-slug-draft.txt`
   - In WSL, the equivalent path is `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/`. Always translate Windows paths to `/mnt/c/` equivalents when writing files.
5. If Vinny asks to email the draft, use the `email-sender` skill to send it to hello@phantom-byte.com with the file attached. Do NOT paste the full article text into chat.
6. Deliver the Windows path

## FORMATTING — NON-NEGOTIABLE

- **NEVER hard-wrap. Never 79 columns. Never any column width.** Write each paragraph as ONE long line and let the reader's client wrap it. A column-wrapped .txt enrages Vinny; assume any wrapped file is rejected on sight.
- Do not run a finished article through any formatter, normalizer, or reflow pass. Write it correct in one `write_file` call.
- Layout template: match `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/ARTICLE 194 COMPLETE.txt`. Title line 1 in normal case, one byline line (`By Vinny Barreca, PhantomByte. September 19, 2026.`), `// HEADER` in caps for sections, one blank line between blocks, full paragraphs unwrapped, then a plain `==========================================` separator and the social block labeled `X POST`, `PINTEREST TITLE`, `PINTEREST DESCRIPTION`, `QUICK KEYWORDS` each on its own line.
- Pre-send check: `grep -n '^// '` shows every header with no leading space, `grep -c '^$'` is non-zero, and the longest paragraph line is in the hundreds of characters, not 79.

## If there's no outline

Ask for it. Don't proceed without it. Don't research, don't browse, don't study his site. Get the outline first.

## What stays out

No articles.phantom-byte.com. No style study. No research loops. No subagents. Outline in, article out.

Research exception: if the user explicitly requests fact-checking or browser research (e.g. "use your browser skill to fill in the gaps," "fact check it"), verify cited sources with targeted searches. Check arXiv for referenced papers, vendor sites for referenced reports, and any daily data files for supporting material. Do not perform open-ended topic research -- verify only the specific papers, entities, and claims named in the outline. See `references/research-playbook.md` for fast verification patterns and `references/arxiv-production-agent-cluster.md` for a pre-verified example of an arXiv source bank.