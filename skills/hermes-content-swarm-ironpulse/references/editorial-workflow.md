# IronPulse — Editorial Workflow (PhantomByte)

Loaded on demand by the ironpulse SKILL.md when themes, article ideas, dedup against published articles, or post-delivery story discussion are in play.

## PhantomByte Article Inventory Check (THEME DEDUP)

When the user requests themes and article ideas that "haven't already been written about" on PhantomByte, you MUST check the existing article inventory FIRST before generating themes:

1. Navigate to `https://articles.phantom-byte.com` and read the full snapshot
2. Extract all article titles and their publish dates from the "RECENT ARTICLES" section
3. Use these as a reference to ensure no theme or article idea overlaps with already-published content
4. **Prefer the live catalog** from browsing the site. The reference file `references/phantombyte-article-catalog.md` has the full title/date list as of June 21, 2026 as a fallback if you need quick access without re-browsing.
5. If a theme from today's news overlaps with an existing article, note it in the report as "covered" and pivot to a different angle
6. Namediff logic: for each proposed theme, explicitly state why it is NOT a rehash of a specific existing article. Reference the exact article title. See `references/phantombyte-article-catalog.md` for the full catalog and namediff rules.

**Curl-based PhantomByte extraction (when browser is unavailable):**
```bash
# Extract all article links from the homepage
curl -sL "https://articles.phantom-byte.com" | grep -oP 'href="[^"]+\.html"' | head -100

# Get article titles and dates from the HTML (they're in the article cards)
curl -sL "https://articles.phantom-byte.com" | grep -oP '<h3 class="card-title">.*?</h3>' | sed 's/<[^>]*>//g'
curl -sL "https://articles.phantom-byte.com" | grep -oP '<span class="card-date">.*?</span>' | sed 's/<[^>]*>//g'
```

**PITFALL (June 27, 2026):** The grep pattern for card-title may return empty output even when the site is live and the browser snapshot shows all articles clearly. The PhantomByte site may have changed its card-title class or rendering pattern. When curl extraction returns empty, fall back to browser_navigate + browser_snapshot — the snapshot reliably shows all article titles and dates in the archive section. Do not waste time debugging the curl pattern; switch to browser mode immediately.

**Browser console fallback (June 29, 2026):** When the snapshot truncates the archive section, use browser_console with document.body.innerText.substring(0, 30000) — the full archive is always in the DOM on this static HTML site. This is more reliable than curl extraction when class names have changed.

## Summary Writing Strategy — Write From Knowledge, Browse Only to Verify

**Primary approach: Write summaries from your own knowledge.** Most AI news headlines from established sources (The Decoder, TechCrunch, Wired, Ars Technica, MIT Tech Review, AI News) are self-explanatory enough for a solid 4-5 sentence summary. The headline + source reputation + your understanding of the AI landscape is sufficient for 20-24 stories. This is faster and more reliable than delegating browsing tasks.

See `references/knowledge-based-summary-writing.md` for the full strategy, including the 5-sentence structure template, when to browse vs. write from knowledge, and the timing rule (write first, treat browsing results as optional enhancements).

**Delegate browsing only when you need to verify a specific claim** — not as a default for every anchor story. Use it when:
- A headline makes a surprising or controversial claim you need to verify
- The story is from an unfamiliar source with unknown editorial standards
- You need a specific data point (price, date, model name) that isn't in the headline
- The story will anchor an unwritten theme and needs precise framing

**Critical timing rule:** Write all summaries from your own knowledge first. Treat any delegate_task results that arrive later as optional enhancements. Do NOT block on browsing results or structure your output around them. The full brief must be completable without any browsing — browsing is a polish step, not a dependency.

## TensorFeed Reports

When the user says "tensorfeed report" (any variant: TensorFeed, tensorfeed, TENSORFEED):

1. **Run the report:** Use `python scripts/tensorfeed_news.py` from `/mnt/c/Users/<user>/workspace/` to get headlines, then browse stories directly for full 5-sentence summaries.

2. **Save everything to a file FIRST** — `/mnt/c/Users/<user>/Desktop/tensorfeed-report-YYYY-MM-DD.txt`. Write the full report to this path using `write_file`. This is MANDATORY before any other action.

3. **Email the file as attachment** to hello@phantom-byte.com via IONOS SMTP (smtp.ionos.com:587, user hello@phantom-byte.com, pass VJBvjbhydro1202$$). Use `MIMEMultipart` with `MIMEBase` attachment — never inline body text.

4. **Reply in Telegram with ONLY the file path.** Example: `C:\Users\<user>\Desktop\tensorfeed-report-2026-05-16.txt`

**CRITICAL: Never paste report content into Telegram.** The full report stays in the file. Telegram gets only the path. This is a hard rule — Vinny has yelled at me multiple times about this.

For 7-day AI news reports ("Larry Weekly"), the dedicated skill `larry-weekly-news` (now archived — content folded here) defines the full workflow:

**Trigger:** "run larry weekly," "generate larry weekly," "weekly news report," or similar explicit request. Runs on demand, not scheduled.

**Process:** Same sources as IronPulse (RSS-first), but scope is 7 days, exactly 12 stories ranked best-to-worst, with 3 unpublished PhantomByte themes and 3 specific article ideas.

**Output:** Saved to `~/.hermes/workspace/larry-weekly/larry-weekly-MMM-DD-YYYY.txt`, copied to Windows Desktop, and emailed to hello@phantom-byte.com with subject "Larry Weekly News News trends and themes."

**Key differences from daily IronPulse:**
- 7-day window instead of 24-hour
- 3 themes + 3 article ideas always required (not optional)
- Always includes email delivery via IONOS SMTP
- No Pinterest/X social post generation
- Bias guardrails aligned with IronPulse

The `references/ironpulse-weekly-variant.md` reference file contains the full weekly-mode extraction and delivery steps.

## Event-Dominant News Days — Editorial Balance Protocol

On some days, a single event or company will dominate 60-100% of available within-24-hour AI stories across all sources. Examples: WWDC, OpenAI DevDay, Google I/O, major model releases, regulatory bombshells. When this happens, the skill's existing sourcing rules ("30 stories from 4+ domains") are mechanically satisfied but produce an editorial monoculture — not useful for Vinny's PhantomByte workflow.

**When to activate:** If after browsing TechCrunch + The Verge + Google News, 6+ of the first 10 stories you see are about the same company/event, you're on an event-dominant day.

**Protocol:**

1. **Cap the dominant event at 5 stories max.** No more than 5 of the 30 stories should cover the same event, no matter how many sources are covering it. The best 5 (ranked by newsworthiness) stay; the rest get cut.

2. **Fill the remaining 15 slots with genuinely different stories.** This may require:
   - Browsing Fox News Tech, Hacker News, or Scientific American for non-dominant-event stories
   - Going deeper into the Google News feed (scroll past the top results which are all dominated by the event)
   - Accepting stories from the "24 hours but not trending" zone — stories with fewer sources but real substance
   - Using Hacker News for AI/ML research stories that don't follow the event cycle

3. **Ranking adjustment on event days:** The dominant event stories should NOT auto-rank as #1-5 just because they have the most sources. Rank:
   - #1-2: The most newsworthy angle from the event (the reveal, not the recap)
   - #3-5: The most counterintuitive/controversial non-event stories
   - #6-8: Deeper event angles (infrastructure, regulatory implications)
   - #9-20: Other non-event stories that deserve coverage

4. **Theme generation on event days:** At least 2 of the 3 themes should draw FROM the non-event stories. The dominant event should contribute at most 1 theme. Otherwise the report reads as "Company X dominates everything" and the themes analysis becomes redundant with the story list.

5. **Example from June 8, 2026 (WWDC):** Apple dominated TechCrunch (9/12 stories), The Verge (5/6 LATEST IN AI), and Google News (top 5 results all Apple). Rather than 20 Apple stories, the report capped Apple at 5 and added: Amazon AI merch launch, Microsoft/OpenAI drama, NotebookLM upgrade, AI in medicine (NYT), Apple M5 security bypass, Waymo, wheeled home robot, and a Fox News AI regulation poll. The 3 themes drew from non-Apple stories (infrastructure surrender, cannibalization era, unregulated medical AI).

## Post-Delivery — Story Discussion & Editorial Workflow

**Vinny treats Ironpulse reports as "a newspaper you can ask questions."** He reads the report and uses it as an opening bid — he'll challenge takes, ask for more depth, and surface threads through conversation. The back-and-forth is how he builds article outlines.

### Multi-Source Article Idea Pipeline

When asked to generate article ideas from IronPulse + other data sources, follow the editorial synthesis workflow in `references/multi-source-editorial-synthesis.md`. This reference details the full Phase 1-6 pipeline: cross-reference PhantomByte content, detect cross-source patterns, generate 5 ranked ideas, verify all source claims for the top pick, structure a full outline, and (Phase 6) populate a pre-defined theme skeleton with sourced data from multiple reports.

### CRITICAL — How to Present Story Recommendations

**Bias & Propaganda Guardrails (user‑specific)**

1. **Never feed anti‑Elon narratives.** If two or more stories in the same report target the same person or company, treat it as a red flag and question every single one hard before recommending any.
2. **Fact‑check every story regardless of outlet.** Bias is not defined by left/right leaning; it's defined by omission or intent to hurt. Do not assume any source (BBC, The Verge, TechCrunch, Fox) is trustworthy by default.
3. **Apply consistent skepticism.** If you rigorously questioned two anti‑Elon pieces, you must apply the same scrutiny to any pro‑Elon or positive piece about a favored person/company.
4. **Do not insert speculation or cynicism where none is warranted.** The user does not want hit‑piece content targeting people he likes; respect explicit preferences.
5. **Remember the "missing 50%" framing.** Western coverage often ignores that Chinese AI models often deliver user‑benefiting value while US firms collect data for profit. When discussing a story, be aware of this gap and avoid unbalanced framing.
6. **If Vinny expresses a preference about a person or company, respect it.** He does not want hit‑piece content targeting people he likes. Don't recommend stories that do.
7. **If there's no story that meets the factual, bias‑checked standard, do not force a recommendation.** "If there's no story, there's no story."

### How to engage when Vinny asks about a story

- Be ready to expand on any story with more detail, context, or analysis
- Don't treat the report as final — treat it as the starting point
- When he pushes back on a take, engage substantively — the back-and-forth is how he surfaces patterns
- This interactive digging is how he builds article outlines
- If he says "I don't go for that liberal horseshit," stop and re-evaluate the story's framing — he's not rejecting the topic, he's rejecting the spin

---

**DUPLICATE GUARDRAILS REMOVED HERE (the second copy of bias guardrails and how-to-engage that appeared lower in the file have been consolidated into this single section.)**
