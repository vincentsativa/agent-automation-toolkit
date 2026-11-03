---
name: pinterest-board-dedup-scrape
description: Check Pinterest boards for posted pins before a daily batch.
---

# Pinterest Board De-dup Scrape

Use when a cron job (or any automated task) must write a daily Pinterest post batch and needs to check which stories are ALREADY pinned before creating new ones. This is a pre-write dedup gate, not a manual browser pass.

## Why it matters
Duplicate Pins are the #1 way a re-activated Pinterest account gets spam-flagged and temporarily Pin-creation-blocked. A daily cron must never re-pin a story already posted this cycle. The interactive browser console extraction approach returns empty on Pinterest (shadow DOM + lazy loading), so a cron needs a scrapling-based path.

## Method (RSS feed — CURRENT, verified Aug 15 2026)

The scrapling regex below is **BROKEN against the current Pinterest page structure** (verified Aug 15 2026): the board page's embedded `pins` object only contains image metadata (`id`, `image_signature`, `images`) — pin titles/descriptions are loaded lazily and are NOT in the initial HTML, so the old regex returns 0 matches on a 1.2MB page. **Use the RSS feed instead** — it is lightweight, free, no browser, no JS, and returns the ~25 most recent pin titles per board in ~0.4s each with a plain urllib GET.

```python
import urllib.request, re, html
UA = {"User-Agent": "Mozilla/5.0"}
url = f"https://www.pinterest.com/{PROFILE}/{slug}.rss"
req = urllib.request.Request(url, headers=UA)
with urllib.request.urlopen(req, timeout=30) as r:
    body = r.read().decode("utf-8", "ignore")
titles = re.findall(r"<title>(.*?)</title>", body, re.S)
# First <title> is the board name itself; the rest are pin titles.
pin_titles = [html.unescape(t.strip()) for t in titles[1:] if t.strip()]
```

A ready-to-run script lives at `~/.hermes/scripts/pinterest_dedup.py`. It has TWO modes:

- **Pre-write (no args):** fetches all 7 PhantomByteAI boards and prints each already-pinned title prefixed with its board label. The DAILY Pinterest Posts cron attaches this script so its output is injected into the agent's prompt as context.
- **Post-write HARD GATE (arg = path to posts file):** reads the agent's just-written posts file, fetches the live already-pinned titles, and **removes** any post whose story matches an already-pinned story (via distinctive entity tokens in `STORY_KEYS`). Rewrites the file in place. This is deterministic — it does NOT rely on the model's judgment.

**The hard gate is MANDATORY in the cron (Step 4).** The cron prompt instructs the agent to run `python3 ~/.hermes/scripts/pinterest_dedup.py ~/pinterest_posts_YYYY-MM-DD.txt` AFTER writing the file and BEFORE emailing. Whatever survives is what gets emailed. Do not re-add removed posts.

**Why the hard gate exists (Aug 17 2026):** the soft gate (print titles, ask the flash model to cross-check) failed — the model re-picked the same stories (NVIDIA safety system, Kimi K3, Meta Muse Glimmer, model routing, Jensen Huang) across 3+ consecutive days. The model skipped the semantic cross-check. The hard gate removes the model from the dedup decision entirely.

## Method (scrapling — LEGACY, do not use)

```python
from scrapling.fetchers import StealthyFetcher
import re
sf = StealthyFetcher()
page = sf.fetch(board_url, headless=True, network_idle=True, timeout=60000)
txt = page.body.decode('utf-8','ignore')
# Pin titles live in embedded JSON strings in the raw HTML, not the rendered DOM.
titles = re.findall(r'"(?:title|description|grid_title|pin_description)":"((?:[^"\\]|\\.){15,300})"', txt)
# decode \\uXXXX escapes on each match
```

## Pitfalls

- **Posts are STORY SUMMARIES, not generic evergreen clickbait (CRITICAL — Sep 3, 2026).** The daily cron's deliverable is 10 posts, each summarizing a specific story from today's data files. The model drifted into writing canned textbook definitions ("This evergreen guide explains...", "What Is X?", "How X Works") that could apply to any day, and Vinny rejected the whole batch as trash. Every post MUST name a real story, company, model, or number from the data. The reader must be able to tell which news story the pin is about. If the story is a tutorial/explainer, summarize what it actually teaches and tie it to the specific event or trend that makes it relevant today. Never open with "This evergreen guide..." or "What Is...". Evergreen is a last-resort fallback only when every story in the data files is already pinned. This rule is encoded in the cron prompt AND in the `writing-style` skill's Pinterest Posts section — keep both in sync.
- **The scrapling regex is broken (Aug 15 2026).** The board page's `pins` object only embeds image metadata, not titles. Use the RSS feed method above. Do not burn a StealthyFetcher render on a board page — it returns 0 titles and costs ~60s.
- **RSS returns only the ~25 most recent pins per board.** That is enough for a daily dedup gate (a story pinned more than ~25 posts ago is old news and won't be re-proposed), but it is not a full board history. If you need the complete board, you must paginate the RSS or use the API.
- **`Fetcher()` (non-stealth) returns 200 but its response object has NO `css_first` / `css` methods.** You must regex the raw HTML. Use `StealthyFetcher` to render the JS SPA and read `page.body` bytes.
- **Pinterest is a JS SPA.** The pin text is not in the initial DOM. Extract from embedded JSON strings (`"title":"..."`, `"grid_title":"..."`) via regex over the full HTML dump.
- **Filter out junk pins.** Boards contain Amazon/hardware product pins (NVIDIA DGX Spark, MacBook Pros, monitors), affiliate links, and unrelated saved items. Normalize only the PhantomByte story titles before checking duplicates.
- **Build a normalized title set**, then cross-check each planned post. If a story is already pinned, drop it or swap in a different fresh story from the daily data files.

## Verification
After the dedup check, run the standard Pinterest character-limit verification (title <= 100, description <= 500, no em dashes) on the batch before emailing. See the `writing-style` skill's `references/pinterest-limits.md` for the programmatic check.

## Board Assignment (MANDATORY — Aug 15 2026)

The daily Pinterest cron's PRIMARY deliverable is an email that tells Vinny **which post goes on which board**. This was missing for 6 consecutive runs — the email listed posts with no board mapping, and Vinny called it out. This is now a hard requirement encoded in the cron prompt.

The 7 PhantomByteAI boards (slug → label, must match the dedup script and the cron prompt):
1. `ai-news-machine-learning-emerging-tech` → **Main AI News**
2. `ai-agents-automation-guide` → **AI Agents**
3. `ai-tools-for-business-productivity-2026` → **AI Tools**
4. `ai-for-developers-programming-ai-tutorials` → **AI for Developers**
5. `agent-security-prompt-injection-sandboxing` → **Agent Security**
6. `robotics-physical-ai-humanoid-robots` → **Robotics & Physical AI**
7. `quantum-computing-explained` → **Quantum Computing**

Match each story to the board whose topic fits best:
- AI agent story → AI Agents
- security / prompt-injection / sandboxing → Agent Security
- robotics / humanoid / physical AI → Robotics & Physical AI
- quantum → Quantum Computing
- developer / programming / tutorial → AI for Developers
- business / productivity tool → AI Tools
- general AI news → Main AI News

Spread posts across boards sensibly — never all 10 on one board. The email body MUST list each post as `[BOARD NAME] — Post title` followed by the description. A post with no board assignment is a failure.

## Cron Execution Discipline (CRITICAL — Aug 7, 2026)
The daily Pinterest cron failed twice in a row with "Response remained truncated after 4 continuation attempts" because it burned its entire tool budget before reaching the email step. Root cause: it visited all 5 boards in the browser, then wrote each of the 10 posts with separate write/patch iterations. Context ballooned past 110K tokens, the model truncated, and the email never sent.

The fix (encoded in the cron prompt) — apply to ANY daily batch cron that produces a multi-item document and emails it:
- **Do NOT visit Pinterest boards in the browser during the cron.** Dedup against already-posted pins is a separate pre-write gate (this skill). Visiting boards in the cron wastes context and tool budget.
- **Write ALL posts in a SINGLE `write_file` call** to the date-stamped file. Do NOT write one file per post. Do NOT iterate with `patch` per post. One write, then one verification pass.
- **Cap total tool calls** (the working prompt uses 15). This forces the agent to batch work instead of iterating.
- **Prioritize the email step.** The email is the primary delivery; the Telegram message is just a doorbell ("Email sent with today's Pinterest posts."). If budget runs low, email first, refine never.
- **Verify programmatically with `len()`** that every title <= 100 and every description <= 500 in a single pass, then fix over-limit posts with one patch call.

The failure signature in logs: `RuntimeError: Response remained truncated after 4 continuation attempts` with `last_status: error` on the job, and the file existing on disk but never emailed. If you see that, the job ran out of budget before delivery — the fix is to shrink the tool-call footprint, not to re-run the same prompt.

## Cost Honesty (CRITICAL — Aug 7, 2026)
When diagnosing a cron failure, do NOT reach for `agent.max_turns` as the fix. The Pinterest failure was context bloat, not a tool-call ceiling — raising max_turns did nothing and only increased token spend on every run. Two hard rules:
- **Never claim a config change "won't cost more" when it will.** Raising `agent.max_turns` increases tokens on every run. The user pays for AI usage. A false reassurance about cost is a lie he will catch.
- **If a knob is not the actual fix, revert it.** Do not leave it raised and call it harmless. The user has a photographic memory and tracks what you said vs. what was true.
- **Never claim a fix works without testing it.** Run the job, confirm `last_status: ok`, then report. Untested "fixed" claims are how trust dies.

## Related
- `references/board-list-extraction.md` — extract a profile's full board list (names + slugs) via scrapling when auditing board coverage or deciding what board to create next. Non-obvious regex pairing (name + href per-card) with the JS-noise and offset-pairing pitfalls documented.
- `references/pinterest-char-limit-real-data.md` — real trimming pass data from a 10-post batch that was drafted over 500 chars. Concrete convergence counts and the exact phrasing moves that free 60-110 chars per description. Confirms the "start short, expand to fill" rule.
- `pinterest-academy` — governing Pinterest playbook (cadence, SEO, re-activation rules)
- `social-board-seo` — board audit and keyword research mechanics (interactive/browser path)
