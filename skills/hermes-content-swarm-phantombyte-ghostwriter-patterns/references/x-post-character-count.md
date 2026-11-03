# X Post Character Count — Reliable Verification

The pre-send checklist requires the X post to fit the ceiling of the format in play, not a single fixed number:

- **Default, the five-stanza model post format** in `x-algorithm-post-optimization` (hook line, dense fact stanza, take line carrying the real question, blunt closing contrast). That shape runs roughly 250-400 characters and needs about 280 to fit a free X account. Count it with `len()` and treat 280 as the ceiling. Do not trim a model-format post down to 190.
- **Short one-liner, only when Vinny asks for one:** strictly `< 190`, where 190 itself is too long.

The failure mode is counting by eye or by awk/sed extraction off a long article file, which miscounts and costs several edit iterations before the post fits.

## Proven method (Article 163, 2026-08-16)

The article file contains the post inline between `X POST:` and `PINTEREST TITLE:`
markers, on a long file with line-number prefixes. awk/sed extraction there returned
misleading counts (235, 229, 210, 205) that all looked plausible by eye. The only
reliable check is to collapse the post to a single string and run `len()` in code:

```python
post = "Your agent burns tokens on tool calls, not reasoning. Paying frontier rates for plumbing is a design error. NVIDIA shipped a 30B exec model with 3B active params. Your execution tier?"
print(len(post))  # must be < 190
```

## Rules that came out of it

1. Treat "under 190" as `< 190`, not `<= 190`. If the count equals 190, trim one word.
2. Do not trust awk/sed extraction or terminal `wc -c` on a line-numbered file.
   Collapse the post into a clean single string and count that string.
3. Iterate down in small steps and re-count after every edit until strictly under 190.
4. Keep the reply bait (ends with a reason to reply) even while trimming — do not
   sacrifice the engagement hook just to hit the count.
