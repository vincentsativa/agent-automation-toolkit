---
name: phantombyte-article-revision
description: Edit a PhantomByte article per one external rec.
---

# PhantomByte Article Revision: DRAFT → ARTICLE N COMPLETE

**When to use:** Vinny hands you a PhantomByte DRAFT plus one external recommendation (a Google SEO review, a grader, a reviewer) and says "implement ONLY this, don't touch the original, no em dashes, email it back as ARTICLE N COMPLETE." This is a recurring class of task — the DRAFT→COMPLETE revision pass.

## Rules of the job (non-negotiable)

- **Change exactly the recommendations handed over, and nothing beyond them.** The note may arrive as a single item or as a numbered list of several. Implement every item on that list, no more and no fewer. Do not add, reword, or "improve" anything else, even if other fixes are tempting. Google reviews often read as "this is strong, but add X" — implement X, and Y when Y is on the list, and stop there.
- **Zero em dashes AND zero en dashes** in the output. Applies to your inserted block too. Verify with a search, don't assume.
- **Filename:** `ARTICLE N COMPLETE.txt` (note the space between "ARTICLE" and the number). The source is `ARTICLE N DRAFT 1.txt`.
- **Email it** to hello@phantom-byte.com (use the `email-sender` skill), subject = the filename exactly as handed over, signed "- Bill" with a hyphen. Confirm on Telegram without pasting document content. The no-em-dash rule covers the signature and the subject line too, because Vinny reads both.

## Verified workflow

1. `cp` the source draft into the drafts folder, beside the sibling COMPLETE files: `/mnt/c/Users/<user>/workspace/article-drafts/ghostwriter-terminal/ARTICLE N COMPLETE.txt`. That folder, not `$HOME`, is where every earlier `ARTICLE N COMPLETE.txt` lives and where Vinny goes looking for them. Copy first and patch the copy, so the source draft is never opened for writing.
2. `patch` (mode=replace) to insert exactly one block at a chosen anchor line — a unique sentence that precedes the insertion point.
3. **Prove the original is untouched:** `diff ARTICLE N COMPLETE.txt <original path>`. Output must show ONLY the inserted lines (e.g. `47,84d46`), nothing else. Any deleted/modified original line means you went too far — revert and redo.
4. **Prove zero dashes:** `search_files` for `—` (em) and `–` (en) in the output file. Both must return 0 matches.
5. Write the send script into a fresh `SCRATCH=$(mktemp -d ~/cache/scratch/<job>-XXXXXX)` directory for this run, never a fixed or reused path (a stale file from an earlier run trips the overwrite guard and kills the send), and never inline `python3 -c`, which fails SMTP auth with IONOS. Audit every email address in the script, send once, confirm on Telegram, then delete the scratch directory.

## Google's recurring "bridge theory to code" recommendation

Google repeatedly tells PhantomByte that conceptual security/architecture articles read as thought-leadership and should become bookmarkable engineering resources by injecting a short, practical code block (non-commodity content / original engineering value). The fix: add a `// THE GUARDRAIL IN CODE`-style section with a working example of the concept the article only described verbally. This is the single most common Google recommendation on PhantomByte articles.

See `references/google-editorial-recommendation.md` for the known-good reusable guardrail code block that satisfied this recommendation, plus full pitfalls detail.

## Pitfalls

- **`execute_code` may be BLOCKED** in cron/background contexts (approvals gate). Do not route around the guard; use `terminal` cp + `patch` + `search_files` for this workflow instead.
- **The terminal guard sometimes misreads a `diff`/`grep` command** as a gateway-restart attempt and blocks it. If that happens, fall back to `search_files` (dash sweeps) and `patch`/`read_file` to verify.
- **Do not paste document content into the Telegram confirmation** — just confirm the email was sent.
- **Verify before emailing.** The whole point of the job is "don't touch the original." The diff is the proof, and `md5sum` on both files is the second half of it: the hash must be unchanged on the source and different only by your inserted block on the COMPLETE copy. Never skip either check.
- **Both edits go in the same turn the email goes out.** A revision whose file was written but never sent is an unfinished job, and the turn ceiling can cut a long patching run before the send. Keep the edit count low, batch the verification into one script that prints the diff, the dash counts, the body word count, and the social-block presence together, then send in that same turn.
