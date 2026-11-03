# Pinterest Character Limits (verified July 2026)

Pinterest has hard truncation limits. Posts that exceed them are silently cut in the feed, so always verify programmatically before delivering.

## Limits
- Title: 100 characters max (truncates after 100).
- Description: 500 characters max (truncates after 500).
- X/Twitter posts: 190 characters max (regular account, not premium).
- No em dashes anywhere (carried from the global PhantomByte rules).

## Em dash detection (expanded)
The global "no em dash" rule also rejects these copy-paste leaks. Check all of them, not just U+2014:
- `-` (U+2014), `–` (U+2013), `―` (U+2014 variant), `‒` (U+2012)
- `─` (U+2500 box-drawing), appears when text is copied out of terminal/code blocks.

## Verification snippet
Run this in execute_code or a script after writing the posts file. It parses POST blocks, checks each title/description against the limits, and flags em dashes.

```python
import re

def verify(path):
    em = "\u2014"
    text = open(path, encoding="utf-8").read()
    posts = []
    for p in text.split("POST #")[1:]:
        num = re.match(r"(\d+)", p).group(1)
        title = re.search(r"Title:\s*(.+)", p).group(1).strip()
        desc = re.search(r"Description:\s*(.+?)(?:\n\n|\n=+|\Z)", p, re.S).group(1).strip()
        posts.append((num, title, desc))
    ok = True
    for num, title, desc in posts:
        t, d = len(title), len(desc)
        issues = []
        if t > 100: issues.append(f"TITLE>{t}")
        if d > 500: issues.append(f"DESC>{d}")
        if em in title + desc: issues.append("EMDASH")
        if issues: ok = False
        print(f"#{num}: title={t} desc={d} " + ("OK" if not issues else " ".join(issues)))
    print("All OK:", ok, "| em dash in file:", em in text, "| posts:", len(posts))

verify(r"C:\Users\<user>\pinterest_posts_2026-07-07.txt")
```

## Workflow
1. Write the batch to a .txt file.
2. Run verify() on it.
3. If any DESC is over 500, trim words (drop redundant "analysis", "and machine learning risk", "like CUDA did for AI compute" style clauses) and re-run.
4. Repeat until All OK is True.

## Batch X-post verification (same delivery, 190 cap)
When a cron asks for matching X posts alongside Pinterest, verify both in one pass. Use structured lists, not regex over the file, because the X text format (plain sentences) does not match the POST-block parser above.

```python
def emdash(s):
    return any(c in s for c in ['\u2014','\u2013','\u2012','\u2015','\u2500','-','–','―','‒'])

def verify_batch(pins, xposts):
    # pins: list of (title, description). xposts: list of strings.
    bad = 0
    for i, (t, d) in enumerate(pins, 1):
        flag = ""
        if len(t) > 100: flag += " TITLE_OVER"
        if len(d) > 500: flag += " DESC_OVER"
        if emdash(t) or emdash(d): flag += " EM_DASH"
        if flag: bad += 1
        print(f"PIN {i}: t={len(t)} d={len(d)}{flag}")
    for i, x in enumerate(xposts, 1):
        flag = ""
        if len(x) > 190: flag += " X_OVER"
        if emdash(x): flag += " EM_DASH"
        if flag: bad += 1
        print(f"X {i}: len={len(x)}{flag}")
    print("TOTAL ISSUES:", bad)
    return bad
```

Run `verify_batch()` and fix every flag. Re-run until TOTAL ISSUES is 0 before writing the final document. A single word swap after a pass can push a description over 500, so verify the final text, not an earlier draft.

## Why this matters
The "no character limit" guidance in older versions of this skill was wrong. Real Pinterest posts truncate at 100/500. A post that looked complete at 627 characters loses its closing hook question and follow prompt when truncated, killing engagement.

## Trimming Strategy (verified July 2026)

When a description is over 500 characters, you will likely need 3-8 iterations to get all 10 posts under the limit. Do not expect to nail it on the first pass. Use this priority-ordered trimming checklist:

### What to cut first (biggest savings, least semantic loss)

1. **Remove trailing clauses that restate the obvious.** "A must-read for anyone tracking AI developer tools" can become "A must-read for anyone tracking AI developer tools.", but if you need space, cut the whole sentence. The post already makes the case.

2. **Shorten company/product descriptions.** "the open-source tool for running LLMs locally" becomes "the tool for running LLMs locally" or "the standard for running Llama, Mistral, and DeepSeek on consumer hardware." Drop "open-source" when the context already implies it.

3. **Remove filler adjectives.** "massive botnets" becomes "botnets." "significant privacy and consent concerns" becomes "privacy concerns." The noun carries the weight.

4. **Merge two short sentences into one.** "This is the first attack capable of assembling massive botnets. Learn how to defend your AI coding tools." becomes "This is the first attack capable of assembling botnets. Learn to defend your AI coding tools.", or merge: "This is the first attack capable of assembling botnets. Learn to defend your AI coding tools."

5. **Drop "and" chains.** "for supply chain optimization, employee scheduling, and customer experience personalization" becomes "for supply chain, scheduling, and customer experience."

6. **Use shorter synonyms.** "demonstrates" becomes "proves." "represents" becomes "is." "utilizes" becomes "uses." "validates" becomes "proves."

7. **Remove "that" clauses where the meaning survives without them.** "The funding validates that local AI is the fastest-growing segment" becomes "The funding validates local AI as the fastest-growing segment."

8. **Cut trailing "Follow PhantomByte" if absolutely necessary**, but this is the last resort. The follow prompt drives engagement and is part of the required structure. Only cut it when every other option is exhausted and you are still over by 10-20 chars.

### What to never cut
- The concrete news hook (first sentence: who, what, number).
- The named company or product.
- The call to action / save prompt.
- Keywords that drive Pinterest SEO (artificial intelligence, machine learning, AI news, emerging technology, AI security, etc.).

### Iteration pattern
Write all 10 descriptions at full length first. Then verify. Then trim the worst offenders (the ones most over 500). Re-verify. Repeat. On average, 5-7 iterations are needed to get all 10 under 500. Do not try to trim every post to exactly 500 in one pass, trim the top 3-4 over-limit posts, re-verify, then trim the next tier. This converges faster than trying to fix all 10 at once.

### CRITICAL: Start short, expand to fill (added July 10, 2026)

Do NOT write long descriptions and then trim down. This session proved that iterative trimming from 600-700 chars is painfully slow (10+ iterations) and produces choppy, awkward prose.

**The correct approach:**
1. Write each description targeting 350-400 chars (lean, factual, no filler).
2. Verify all 10 are under 500.
3. Then expand each one with SEO keywords, follow prompts, and engagement hooks to approach 450-500.
4. Re-verify.

A 350-char draft gives you 150 chars of room for keywords, calls to action, and hooks. This approach converges in 2-3 iterations instead of 8-10. The prose also reads better because you are adding to a clean base rather than cutting away from bloated text.

**Session proof (July 10, 2026):** I spent 10+ iterations trying to trim 600-700 char descriptions down to 500. Each pass only shaved 10-20 chars. The final solution was to rewrite from scratch at 350-400 chars and then expand. The "write long, trim down" approach is a trap.

**Escape hatch:** If you are on iteration 4+ and still have posts over 500 chars, stop trimming. Delete the file and rewrite from scratch targeting 350-400 chars per description. It is faster to start over than to keep trimming. The sunk cost of the previous iterations is not worth the time.

### Pre-flight check: evergreen post first (added July 11, 2026)

Before writing a single description, write a 350-400 char draft of the evergreen post (#10) first. The evergreen post is consistently the hardest to fit because educational content is inherently longer. If you cannot fit the evergreen post at 350-400 chars, you will never fit it at 600+. Use the evergreen post as your canary, if it works, the rest will work. If it does not, adjust your approach before writing the other 9.

### Hard stop at iteration 4 (added July 11, 2026)

If you are on the 4th verification pass and any description is still over 500 chars, stop immediately. Delete the file. Rewrite from scratch targeting 350-400 chars per description. Do not attempt a 5th trimming pass. The sunk cost of previous iterations is not worth the time, and the prose quality degrades with each trim.

**Session proof (July 11, 2026):** I spent 15+ write_file calls trying to trim descriptions from 600-800 chars down to 500. The evergreen post (#10) was the last to converge and required 3 separate rewrites. The correct approach would have been to write the evergreen post first at 350-400 chars, verify it fits, then write the other 9. This session cost 15+ iterations because I wrote all 10 long first and then tried to trim them all simultaneously.

### MANDATORY: Programmatic verification before emailing (added July 11, 2026)

After writing all 10 posts and before emailing the file, you MUST run a programmatic len() check on every title and every description. Do not trust your own annotation. Do not assume a post fits because you wrote it to fit. The evergreen post (#10) is the most likely to exceed 500 chars, verify it first. If any post is over the limit, fix it before emailing. The user will not accept a file with posts that don't fit Pinterest's truncation limits.

**Session proof (July 11, 2026):** The cron job's agent wrote all 10 posts but the evergreen post (#10) had a 562-char description, 62 over the limit. The user had to catch this and demand a fix. The agent should have verified programmatically before emailing. This cost the user trust and time.
