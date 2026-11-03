# Real trimming sequence confirming the 500-char limit (Aug 5, 2026)

See writing-style/references/pinterest-limits.md for the check snippet. This
captures the actual trimming pass data from a real daily batch.

A full 10-post batch drafted at 572-607 chars per description was over the 500
limit on every post. It took 5 trimming passes to converge. The skill's
"start short, expand to fill" rule exists precisely to avoid this.

Rewrite-to-~440-490 converged in 3 passes (5 under, then 9 under, then all 10).
Verified final counts: 439, 473, 464, 491, 487, 500, 476, 499, 488, 496.

Freeing 60-110 chars per post:
1. Drop redundant keyword triplets (keep two of three).
2. One follow CTA per post, not two.
3. Remove filler adjectives ("a real conversion lever", not "a real traffic and
   conversion lever").
4. Shorten compound phrases.
5. Always programmatic len() check every pass; a word swap adds 5-10 chars.

Evergreen (#10) is the canary and the hardest to fit; check it first.
