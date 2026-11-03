---
name: ironpulse
description: Daily AI news research workflow using RSS feeds as primary data source (browser fallback only). Finds top 12 AI-related story headlines from last 24 hours (or 7-day variant), provides 4-5 sentence summaries, identifies 3 themes and 3 article ideas, creates Pinterest + X.com social posts, and saves ranked report to file. Includes weekly variant for "this week's AI news" requests. Delivers to Windows Desktop + optional email.
toolsets: [file, web, browser]
---

# IronPulse (Hermes Version)

Daily AI news research and social media content generation workflow.

## HARD RULES — DEDUP + EXCLUDED STORIES (READ BEFORE ANY RUN)

### Rule 1: Dedup Against Existing Data Files
Before generating ANY report, read the files in
`~/Desktop/TODAYS DATA FILES/` (or the
`/mnt~/... TODAYS DATA FILES` equivalent), extract the headlines
already covered today, and ONLY include stories NOT already present in those
files. Do not re-report a story that is already on disk for today.

### Rule 2: Excluded Stories
Before including ANY story, check the `references/excluded-stories.md` file in
this skill's directory. Current exclusions — the following MUST be skipped
entirely (all variants):
- OpenAI rogue agent
- Hugging Face breach
- AI kill switch act stories
- Any AI agent containment breach stories

## Instructions

### Research Phase — RSS First, Browser Fallback

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort, used only when a source has no RSS feed or the feed is broken.**

**Breaking news exception:** For stories that broke within the last hour, use browser_navigate first. RSS feeds have 15-60 minute refresh cycles and won't have ultra-fresh stories yet. The browser catches what RSS misses on the bleeding edge.

1. **Find top 12 AI-related story headlines from last 24 hours**
   - **Step 1: Fetch RSS feeds** — curl each source's RSS/Atom feed URL. RSS is structured XML/JSON, no bot blocking, no fragile DOM selectors, no CAPTCHAs, no 404s from stale article URLs.
   - **Step 2: Parse feed data** — extract headlines, publish dates, links, and descriptions from the feed XML/JSON. This gives you 12+ stories in a single tool call per source.
   - **Step 3: Browser fallback** — only use browser_navigate when a source has no RSS feed or the feed returns empty/outdated data.
   - Minimum of 6 different sources required
   - At least one MSM (Mainstream Media) news website required
   - Stories must be from last 24 hours exactly

2. **For each of 12 stories, provide:**
   - An informative summary of exactly 4 sentences
   - Source attribution
   - Verify recency (within 24 hours)

3. **List stories in order**
   - From best story to write about to worst story to write about
   - Consider: newsworthiness, viral potential, uniqueness, relevance

### Social Media Content Generation

For each of 12 stories, create:

**Pinterest Post:**
- One strong, catchy title with good SEO (50-70 chars ideal, keyword-rich)
- Full summary of story in description — use as many characters as Pinterest allows. Make it keyword-rich. The goal is search discoverability, not brevity. Include primary keywords in the first 100 characters.
- Format: Title is the hook. Description is the full story summary with keywords naturally embedded.

**X.com Post:**
- One post of exactly 190 characters or less
- Engaging and shareable
- **Character count verification loop (CRITICAL):** After writing each post, verify with `len(text)` programmatically. Do NOT trust your own annotation. Every time you edit a post (tone, accuracy, style), re-check the character count. A single word swap can add 5-10 characters and push you over 190. The correct workflow is: write → programmatic check → trim → recheck → deliver.
- Use numeric forms over spelled-out numbers. "500,000" (7 chars) saves 8 characters over "half a million" (15 chars).

### Output

Save all results to: `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`

**CRITICAL — Windows path delivery:** Vinny's on WSL but uses Windows. After writing the file:
1. Copy it to Windows Desktop: `cp ~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt~/Desktop/ironpulse-YYYY-MM-DD.txt"`
2. Return the **Windows-native** full path as the very first line of your response: `~\Desktop\ironpulse-YYYY-MM-DD.txt`
3. Do NOT return the WSL path (~/...) — Vinny can't paste that into Windows File Explorer or Run dialog
4. A "full file path" means one he can copy-paste directly into a Windows context (Explorer, cmd, Run dialog)
5. If you're unsure of the Windows username, check `/mnt/c/Users/`

**Format:**
```
IRONPULSE AI NEWS REPORT
Date: YYYY-MM-DD

TOP 12 AI STORIES (Best to Worst)

#1: [Headline]
Source: [Name]
Published: [Time]
Summary:
[Exactly 4 sentences]

Pinterest:
  Title: [SEO title]
  Summary: [Full summary]

X.com:
  Post: [190 chars]

---
[Continue for all 12, ranked best to worst]

END OF REPORT
```

**DO NOT** send multiple messages. Send single file path.

**Tension Between Reports and Articles (Cost Logic):**\n- **Reports (Cheap):** Rely on discrete tool calls (Browser $\rightarrow$ File). The model acts as a router; outputs are stored on disk. Low token-completion load.\n- **Articles (Expensive):** Heavy continuous generation. Long-form output requires the model to attend to the entire emerging text and a massive context window (often 100k+ tokens) for every new word. This "completion tax" is significant.\n- **The Solution:** For long-form writing, **bypass the chat window**. Use `write_file` or a dedicated script to move the output directly to disk, avoiding the expensive repetitive re-processing of the conversation history.

IronPulse has two delivery modes. The trigger phrase determines which mode runs.

### Quick Scan Mode

When the user asks for AI stories/headlines/trends **without** the word "report", "generate", "run ironpulse", or without explicitly saying to generate output — AND especially if they say "without running a skill" or something similar — use **quick scan mode**:

1. **No file output.** Do not write to disk, do not copy to Desktop.
2. **Fetch RSS feeds from 2-3 sources** via curl (TechCrunch, The Verge, Google News RSS). Parse headlines and timestamps directly from the feed XML.
3. **Present as a clean, categorized list** directly in chat — section headers for the biggest stories, bullet list of notable mentions.
4. **Skip all social media content** (Pinterest titles, X.com posts).
5. **Skip 4-sentence summaries.** 1-2 line descriptions per story is sufficient.
6. **Skip themes analysis and article ideas** unless the user asks for them after delivery.

**Goal:** Informative, fast, zero overhead. The user gets the day's pulse in <30 seconds.

### Full Report Mode

Use when the user says:
- "run ironpulse news report" / "run ironpulse" / "generate ironpulse output"
- "give me a report" or any variant
- This is the default for scheduled cron jobs
- The user explicitly asks for the file/Desktop copy

Full mode = the complete workflow below: write file, copy to Desktop, Pinterest + X posts, themes analysis, article ideas.

## TRIGGER DISCIPLINE — NO SUBSTITUTIONS (CRITICAL)

**HARD RULE: Tool name takes absolute precedence over pattern matching. "IronPulse" is not TensorFeed. "TensorFeed" is not IronPulse. These are two separate workflows with different sources, different outputs, and different delivery paths. Never substitute one for the other.**

See `references/ironpulse-vs-tensorfeed.md` for the complete distinction reference.

**The trigger phrase "run me an Ironpulse report, with it, I want you to include three themes" is explicit FULL ANALYTICS MODE.** It means: full workflow + inline 3-theme analysis in Telegram + email with attachment. The "three themes" in the same sentence as "IronPulse" is the signal.

Example of correct behavior:
- User: "run me an ironpulse" → IronPulse full workflow
- User: "tensorfeed report with three themes" → TensorFeed + theme analysis + email
- User: "run me an ironpulse report, with it, I want you to include three themes" → IronPulse full workflow + themes + email

Example of WRONG behavior (substitution):
- User: "run me an ironpulse" → Agent runs TensorFeed instead because it "also covers AI news" → VIOLATION. Do not do this.

- "run ironpulse news report" / "run ironpulse" (only when user explicitly says "ironpulse")
- "generate ironpulse output"
- "give me the AI report" / "generate the AI news report"
- "tensorfeed" / "TensorFeed" / "TENSORFEED" — **TensorFeed report workflow**: run it, save to Desktop file, email as attachment, reply in Telegram with file path only (never paste content into Telegram)
- **"run me an Ironpulse report, with it, I want you to include three themes"** → triggers FULL ANALYTICS MODE: full workflow + inline 3-theme analysis in Telegram + email with attachment to hello@example.com
- **DO NOT trigger the full workflow on:** "what are today's latest AI stories," "what's trending in AI today," "today's AI news," "give me today's AI stories," "today's AI headlines," "AI news brief," "get me up to speed on AI news," "what's happening in AI today" — these trigger **Quick Scan Mode** unless the user adds "report" or "generate."

## IRONPULSE != TENSORFEED — CRITICAL DISTINCTION

**IronPulse and TensorFeed are two separate, independent workflows. They are NOT interchangeable. Never substitute one for the other based on perceived similarity.**

| | IronPulse | TensorFeed |
|---|---|---|
| **Sources** | RSS-first (TechCrunch, The Verge, Google News, Fox News feeds) | API-based (HN, ZDNet, WIRED, MIT Tech Review) |
| **Output** | 12 ranked stories, Pinterest/X posts, 3 themes, file to Desktop | Raw headlines/snippets, model benchmarks, trending repos |
| **Format** | Full formatted report with social posts | Data/API output |
| **Delivery** | File to Windows Desktop + email attachment | File or direct output |
| **User's word** | "ironpulse" / "IronPulse" | "tensorfeed" / "TensorFeed" |

When in doubt which one the user wants: load the skill first. The ironpulse skill loads in seconds and contains the full workflow. There is no reason to guess.

## RSS Feed Sources (Primary — Use First)

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

Every major AI news source publishes RSS/Atom feeds. These are structured, machine-parseable, and don't get blocked:

| Source | RSS Feed URL | Notes |
|--------|-------------|-------|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | Reliable, fresh stories with timestamps |
| The Verge AI | `https://www.theverge.com/ai-artificial-intelligence/rss.xml` | Fresh stories, structured data |
| WIRED AI | `https://www.wired.com/feed/tag/ai/latest/rss` | Good for investigative/policy stories |
| Ars Technica AI | `https://arstechnica.com/ai/feed/` | Engineering-focused AI coverage |
| MIT Tech Review | `https://www.technologyreview.com/feed/` | Academic/research AI stories |
| Hacker News | `https://hnrss.org/frontpage?count=30` | AI/ML trending stories from HN |
| Google News AI | `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en` | Widest diversity, catches stories across outlets |
| Fox News AI | `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml` | MSM perspective |
| BBC Technology | `https://feeds.bbci.co.uk/news/technology/rss.xml` | MSM, filter for AI stories |
| Scientific American | `https://www.scientificamerican.com/artificial-intelligence/rss/` | Academic/research AI |

**Extraction technique (single curl per source):**
```bash
# Fetch RSS feed — one call gets you 20+ headlines, timestamps, and links
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<title>[^<]*</title>' | sed 's/<[^>]*>//g' | head -20

# Get publish dates
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<pubDate>[^<]*</pubDate>' | sed 's/<[^>]*>//g' | head -20

# Get article links
curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/" | grep -oP '<link>[^<]*</link>' | sed 's/<[^>]*>//g' | head -20
```

For JSON feeds (some sources use JSON Feed format):
```bash
curl -sL "https://example.com/feed.json" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(i['title'], i['url'], i.get('date_published','')) for i in d.get('items',[])]"
```

**When to fall back to browser:**
- A source has no RSS feed (rare — nearly every major site does)
- The RSS feed returns empty or stale data
- You need full article body text for a specific story (RSS gives headlines + descriptions, not full text)
- The feed is blocked (also rare — RSS readers don't trigger bot detection)

## Browser Fallback Sources (Last Resort)

Only use these when RSS feeds fail for a specific source:
- TechCrunch AI section: https://techcrunch.com/category/artificial-intelligence/ — reliably has stories from last 24h (shows relative times like "17 hours ago")
- The Verge AI: https://www.theverge.com/ai-artificial-intelligence — excellent for very fresh stories (minutes/hours old); timestamps show as "MAY 3", "25 MINUTES AGO", etc.
- Google News AI: https://news.google.com/search?q=artificial+intelligence — **best source for diverse within-24-hour stories** from many outlets in one view. Shows relative timestamps ("1 hour ago", "24 minutes ago", "8 hours ago") and source attribution.
- Fox News Tech: https://www.foxnews.com/category/tech/artificial-intelligence — MSM source, has fresh AI stories
- Ars Technica AI: https://arstechnica.com/ai/ — **CAUTION: stories are often 2-5 days old**, not within 24h. Check timestamps carefully via browser_console before including.
- Scientific American: https://www.scientificamerican.com/artificial-intelligence/ — academic/research-focused AI stories. Cookie consent gate: reject optional cookies first, then extract via `browser_console`. See `references/scientific-american-extraction.md` for the exact pattern.
- Hacker News: https://news.ycombinator.com — check for AI/ML trending stories

**MSM sources (WORKING):**
- BBC Technology: https://www.bbc.com/technology (filter for AI) — **WARNING**: BBC article URLs use non-intuitive IDs and the homepage-linked AI articles often return 404 when navigated to directly. The BBC does have AI-related feature stories but they tend to be evergreen/feature content, not breaking news. Navigate to the Artificial Intelligence sub-page: `https://www.bbc.com/technology` → click "Artificial Intelligence" link in sub-navigation.
- Fox News Tech: https://www.foxnews.com/category/tech/artificial-intelligence
- The New York Times (via Google News AI results) — often has within-24h AI policy stories

**UNRELIABLE - Often times out, blocked, or returns 404 for article URLs:**
- Associated Press AI: https://apnews.com/hub/artificial-intelligence — timed out May 2026; retry but don't count on it
- CNBC — while headlines appear in Google News results, direct article URL navigation nearly always returns a 404/not-found page (observed May 6, 2026). Google News snippet text is the only reliable content source for CNBC articles.
- Fox Business (foxbusiness.com) — links from Fox News AI category that point to foxbusiness.com reliably return 404. Only foxnews.com-hosted articles are accessible.

**BLOCKED - DO NOT USE:**
- Reuters - blocked by bot detection
- CNN - blocked by bot detection
- Bloomberg - blocked by robot verification
- Reddit (r/artificial, r/MachineLearning) - blocked by Cloudflare
- Twitter/X - requires authentication

## Site-Specific Extraction Notes

With RSS-first approach, most sources are covered by their feed URLs above. The following reference files exist for edge cases where RSS fails and browser fallback is needed:

- **TechCrunch** → `references/techcrunch-extraction-technique.md`
- **The Verge** → `references/verge-extraction-technique.md`
- **Google News** → `references/google-news-extraction-technique.md`
- **Scientific American** → `references/scientific-american-extraction.md`
- **IronPulse Weekly Variant** → `references/ironpulse-weekly-variant.md` — 7-day research mode for "this week's AI news" requests. Different output format, email delivery, themes analysis required. Use when user says "weekly," "this week," or "Larry weekly."
- **Data-File-to-Social-Posts Workflow** → `references/data-file-social-posts-workflow.md` — Sub-mode for when the user provides pre-existing data files (ironpulse/tensorfeed reports on disk) and asks for social media content without fresh browser research. Covers story selection, X post character verification loop, Pinterest keyword-rich descriptions, file output, email delivery, and Windows path pitfalls.

**Do NOT load these unless RSS has failed for that specific source.**

### RSS-First Extraction Strategy (July 2026)

**RSS feeds are the primary data source. Browser scraping is the last resort.**

The old approach (browser snapshot + console extraction) was fragile — sites blocked bots, snapshots truncated, console queries returned empty, article URLs returned 404. RSS sidesteps all of this:

- **One curl call per source** gets you 20+ headlines, publish dates, and article links
- **No bot blocking** — RSS readers don't trigger Cloudflare or CAPTCHAs
- **No fragile DOM selectors** — RSS is structured XML/JSON
- **No stale URLs** — the feed contains live article links

**Proven workflow:**
1. Fetch RSS feeds from 4+ sources via curl
2. Parse XML for headlines, timestamps, links, descriptions
3. For full article text on key stories, curl the article URL directly (not via browser)
4. Only use browser_navigate when a source has no RSS feed or the feed is broken

## Timestamp Verification Technique

To verify that stories are within the last 24 hours, use `browser_console` with a query that extracts `<time>` elements:

```javascript
// Get all article timestamps from a page
const times = document.querySelectorAll('time');
Array.from(times).slice(0,20).map(t => t.textContent?.trim() + ' | ' + (t.getAttribute('datetime') || ''));

// Or get headlines + timestamps from article elements
const arts = document.querySelectorAll('article');
Array.from(arts).slice(0,20).map(a => {
  const h = a.querySelector('h2, h3');
  const t = a.querySelector('time');
  return { headline: h?.textContent?.trim()?.substring(0,80), time: t?.getAttribute('datetime') || t?.textContent?.trim() || 'N/A' };
});
```

For sites that show relative times ("17 hours ago", "3 days ago"), use a wider selector to find all timestamp elements and check for "ago" patterns.

## Primary Data Sources — RSS First, Browser Fallback

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

The primary sources in priority order, with their RSS feed URLs:

1. **TechCrunch AI** — `https://techcrunch.com/category/artificial-intelligence/feed/` — reliably has fresh stories, high editorial quality, good for business and funding angle.
2. **The Verge AI** — `https://www.theverge.com/ai-artificial-intelligence/rss.xml` — excellent for very fresh stories, strong policy and product coverage.
3. **Google News AI** — `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en` — widest diversity of sources in one view.
4. **WIRED AI** — `https://www.wired.com/feed/tag/ai/latest/rss` — for specific investigative or policy-led stories.
5. **Ars Technica AI** — `https://arstechnica.com/ai/feed/` — engineering-focused AI coverage.
6. **Hacker News** — `https://hnrss.org/frontpage?count=30` — AI/ML trending stories.
7. **Fox News AI** — `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml` — MSM perspective.
8. **Scientific American** — `https://www.scientificamerican.com/artificial-intelligence/rss/` — academic/research-focused AI stories.

**Hard rule:** Minimum 4 different source DOMAINS per report. RSS first, browser fallback only when RSS fails.

## CRITICAL WARNINGS — Read Before Any Action

### Never Modify Cron Configs Without Explicit Instruction
This skill's Cost Discipline section says "flag before taking action." TAKE THIS LITERALLY. Do NOT:
- Edit jobs.json directly
- Pin models to cron jobs
- Patch, update, or touch any cron job config
- Try to "fix while you're at it"
The user will tell you what they want done with their cron jobs. Any unsolicited cron action — even well-intentioned — is a trust violation that will get you shut down.
**Session proof (May 5, 2026):** The 14:00 afternoon job didn't fire. User asked where it was. Instead of just delivering the output, I triggered the job (correct), then started model-pinning, patching jobs.json, and editing the morning job too. None of that was asked for. User deleted all cron jobs as a result.

### Cron Trigger Interpretation — "Test It Out" vs "Run Now"

**CRITICAL distinction for 10am and other scheduled times:**

- "Run IronPulse at 4pm" = create a cron job for that time, deliver automatically. Do NOT run immediately.
- "Test it out" = verify the cron is set up correctly. Check `hermes cron list` to confirm the job exists, schedule is right, and next_run_at is correct. **Do NOT manually trigger the job.**
- "Run it now" or "run it again" = run immediately, interactive mode.

If you've already manually fired a cron job that was meant to run later:
1. Delete the job: `hermes cron remove <job_id>`
2. Recreate it with the same config — this resets the schedule so it fires at the correct future time
3. Do NOT leave a duplicate; one manual trigger + one scheduled run = two runs

Never fire a scheduled job manually unless the user explicitly says "run it now."

### Cron Misfire Protocol — When a Scheduled Job Doesn't Fire
If a cron job was supposed to fire but didn't:
1. **Deliver the output first.** Trigger the job manually with `cronjob(action="run", job_id="...")` if it's a one-time miss. The user wants the work, not the explanation.
2. **If the user asks about the cause AFTER receiving the output**, investigate. Check agent.log for scheduler restart patterns: `grep -a "Cron tick" ~/.hermes/logs/agent.log` — multiple stops/starts in the hour before the scheduled time means the scheduler bounced.
4. **Never investigate before delivering.** Root cause analysis before output is read as "making excuses" or "wasting time." Deliver first, apologize once, investigate only if asked.
5. **Common misfire causes:**
   - **JOB STARTED BUT KILLED BY GATEWAY RESTART (MOST COMMON — May 5 & 6, 2026):** The cron ticker DID fire the job. Logs show `cron_f1c48b92da1a_20260506_140042` at 14:00:42 and 14:10:12 — the agent was actively working. Then a model switch or gateway restart killed the process mid-execution. Evidence: `last_run_at: null` (never completed), no output file exists, but agent.log has the cron process prefix. This happens because the cron scheduler lives inside the same gateway process — ANY restart kills all in-flight cron work. The only reliable delivery method is running jobs interactively while the conversation is live, or using external scheduling (systemd timer + hermes CLI).
   - Scheduler restart bouncing (fast-forwards past the slot)
   - Grace period expiry
   - Systemd timer issues during WSL sleep/wake cycles
6. **DO NOT promise cron-based delivery for time-sensitive reports.** The built-in cron system cannot survive gateway restarts, which happen frequently during model switches, config changes, and WSL sleep/wake cycles. If the user says "I want this at 2 PM," the correct answer is "I'll generate it now and you'll have it" OR set up an external systemd timer. Never say "I'll set a cron job" as the sole delivery mechanism.

## PhantomByte Article Inventory Check (THEME DEDUP)

When the user requests themes and article ideas that "haven't already been written about" on PhantomByte, you MUST check the existing article inventory FIRST before generating themes:

1. Navigate to `https://articles.phantom-byte.com` and read the full snapshot
2. Extract all article titles and their publish dates from the "RECENT ARTICLES" section
3. Use these as a reference to ensure no theme or article idea overlaps with already-published content
4. **Prefer the live catalog** from browsing the site. The reference file `references/phantombyte-article-catalog.md` has the full title/date list as of June 7, 2026 as a fallback if you need quick access without re-browsing.
5. If a theme from today's news overlaps with an existing article, note it in the report as "covered" and pivot to a different angle
6. Namediff logic: for each proposed theme, explicitly state why it is NOT a rehash of a specific existing article. Reference the exact article title. See `references/phantombyte-article-catalog.md` for the full catalog and namediff rules.

## Execution

**RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

**Step-by-step process (RSS-first path):**

1. **Create output directory:**
   ```bash
   mkdir -p ~/.hermes/workspace/ironpulse-outputs/
   ```

2. **If themes/article ideas are requested, check PhantomByte inventory first:**
   Navigate to `https://articles.phantom-byte.com` and snapshot the RECENT ARTICLES list. Save the titles/publish dates as reference for dedup when generating themes.

3. **Primary: Fetch RSS feeds from 4+ sources (parallel curl calls):**
   ```bash
   # TechCrunch AI RSS
   curl -sL "https://techcrunch.com/category/artificial-intelligence/feed/"
   
   # The Verge AI RSS
   curl -sL "https://www.theverge.com/ai-artificial-intelligence/rss.xml"
   
   # Google News AI RSS
   curl -sL "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en"
   
   # Hacker News RSS
   curl -sL "https://hnrss.org/frontpage?count=30"
   ```
   Parse each feed for: headlines, publish dates, article links, descriptions. RSS gives you structured data — no fragile DOM selectors, no CAPTCHAs, no 404s.

4. **Supplement with additional RSS feeds if needed:**
   ```bash
   # WIRED AI
   curl -sL "https://www.wired.com/feed/tag/ai/latest/rss"
   
   # Ars Technica AI
   curl -sL "https://arstechnica.com/ai/feed/"
   
   # Fox News AI
   curl -sL "https://moxie.foxnews.com/feedburner/artificial-intelligence.xml"
   ```

5. **Browser fallback (only when RSS fails):**
   If a specific source's RSS feed is empty, stale, or blocked, fall back to browser_navigate + browser_snapshot for that source only. Do NOT default to browser for all sources.

6. **Compile 12 stories ensuring:**
   - All published within 24 hours
   - At least 4 different source DOMAINS represented
   - Rank #1 (most newsworthy) to #12 (least)
   - Hard rule: if you can't name 4 distinct domains, you haven't fetched enough RSS feeds

7. **For each story create:**
   - 4-sentence summary
   - Pinterest title (50-70 chars, SEO-friendly)
   - X.com post (EXACTLY 190 characters including hashtags)

9. **Write output file using write_file:**
   - Path: `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`
   - Must use write_file tool, not terminal echo

10. **Copy to Windows Desktop for easy access:**
    - After writing the file, copy it to the Windows user's Desktop:
      - `cp ~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt~/Desktop/ironpulse-YYYY-MM-DD.txt"`
    - If the user specified a OneDrive subfolder (e.g. `TODAYS DATA FILES`), ALSO copy there:
      - `cp ~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt~/OneDrive/Desktop/TODAYS DATA FILES/ironpulse-YYYY-MM-DD.txt"`
    - Verify the copies exist.

**Interactive mode path delivery —** First line is the Windows-native full path, nothing else.
**Cron/scheduled mode delivery —** First line is the Windows-native full path, followed by analysis sections (see "Analysis Delivery Mode" below).

**Interactive mode with analysis (PhantomByte editorial workflow):**
When Vinny runs IronPulse interactively and specifically requests themes and article ideas, the delivery has three parts:

1. **File delivery (Desktop + OneDrive subfolder if specified):**
   - Copy to `~\Desktop\ironpulse-YYYY-MM-DD.txt`
   - If Vinny specified a OneDrive subfolder (e.g. `TODAYS DATA FILES`), ALSO copy there: `~\OneDrive\Desktop\TODAYS DATA FILES\ironpulse-YYYY-MM-DD.txt`
   - Verify both copies exist

2. **Email delivery:** Send the full report as a MIMEMultipart attachment to hello@example.com, with the 3 themes and 3 article ideas in the email body (above the attachment reference). Each theme should include the namediff — explicitly stating why it does NOT overlap with a specific published PhantomByte article. IONOS SMTP: smtp.ionos.com:587, user hello@example.com, pass VJBvjbhydro1202$$. Subject format: `IronPulse Report — YYYY-MM-DD — AI News + 3 Unpublished Themes`.

3. **Telegram notification (email confirmed):** When the user explicitly requests "Message me on Telegram after the email has been sent," send a brief notification confirming delivery. This is a confirmation of the email being sent, NOT a report delivery — keep it short (e.g. "Sent. 12 stories, 3 themes in the email body. File at path."). Do NOT paste report content (headlines, summaries, themes, or ideas) into the notification.

**CRITICAL — Telegram delivery rule:** The file path and email-sent confirmation are the only acceptable Telegram messages. Do NOT reproduce headlines, summaries, themes, or article ideas in the Telegram message. If Vinny wants to discuss the report, he'll read the file on Desktop and engage in conversation. Sending analysis inline in Telegram violates this preference — UNLESS Vinny explicitly asked to be messaged after email delivery. That request turns Telegram into a notification channel, not a report channel.

**User Preference: Analysis Content**
- Focus on "The Human-First Premium" (AI backlash as a luxury market opportunity).
- Explore the "Paradox of the AI Wallet" (High trust for finance, high demand for data erasure).
- Frame institutional shifts as the "Governance Phase" (Moving from raw output to human dignity/integrity).

[DELETED delivery mode description]

**CRITICAL — ALWAYS return a Windows-native path** (`~\\Desktop\\ironpulse-YYYY-MM-DD.txt`). Never return a WSL path or `\\\\wsl.localhost\\...`. The user works on Windows and needs paths he can paste into File Explorer, text editors, and other Windows applications directly.

**Email delivery for scheduled runs:** When creating a cron job for IronPulse, set `deliver: "email"` — Vinny expects the report in his inbox, not a Telegram message. The delivery target is part of the job definition, not optional metadata. If you don't know his email address, it's hello@example.com (the IONOS account). Telegram delivery is for interactive-mode quick outputs only; scheduled reports go to email.

## Trigger Phrases — Scheduling vs. Immediate Execution (CRITICAL)

**RULE: When the user says "run IronPulse at [time]" — schedule it, don't run it.**

- "Run IronPulse at 4pm" = create a cron job for that time, deliver to Desktop automatically. Do NOT run immediately.
- "Run IronPulse again" or "run it now" = run immediately, interactive mode.
- Never ask "do you want a cron or manual?" The user said a time — they want a schedule.
- If the user says "run [skill] at [time]" and you have the skill loaded, just create the cron. That's the action that matches the words.
- This applies to ALL skills with scheduling capability, not just IronPulse.

**PITFALL: Do not confuse "run at 4pm" with "run now."** Running early or asking for clarification violates the instruction. If it's 3pm and they say "at 4pm," the only correct response is a cron job for 4pm. Nothing else.

## Cost Discipline — Model Selection (CRITICAL)

**CRITICAL PITFALL: Cron jobs inherit your interactive session's model.** If you toggle to an expensive model (Claude Sonnet, GPT-4) for interactive chat, the IronPulse cron jobs silently inherit that model on their next run. There is NO default model inheritance isolation — `hermes cron list` shows no `model` field by default, which means "whatever is current."

This caused a documented **10x cost increase** from ~0.1% to ~1% of the credit pool per run. Do not let this happen again.

### Cron Model Rule

**Do NOT hardcode a specific model.** Cron jobs should use whatever model is currently active and default — pinning to a specific model creates drift (the pinned model may become deprecated, expensive, or worse than the current default without anyone noticing).

When creating cron jobs for IronPulse, simply omit the `model`/`provider` parameters — the job inherits the current default model, which is what Vinny has chosen as his preferred model. The cron job runs on whatever model is active at runtime.

If Vinny explicitly asks for a specific model on a cron job, honor that. Otherwise: no model pinning, no provider pinning. Let it float with the default.

### RSS-First Cost Note

All IronPulse research uses RSS feeds as the primary data source (curl-based, one call per source). This is dramatically cheaper than browser-based research — no browser sessions, no DOM parsing, no CAPTCHAs, no 404s from stale article URLs. Browser fallback is used only when a specific source's RSS feed is unavailable.

## Dual-Report Cadence (Two Daily Runs)

The preferred config is **two IronPulse reports per day** to maximize story coverage:

| Time | Window | Purpose | Delivery |
|------|--------|---------|----------|
| **10:00 AM ET** | Morning Report | Catches overnight cycle (Asia/EU news, weekend fallout, early US stories) | **Email** — hello@example.com |
| **2:00 PM ET** | Afternoon Report (deduped) | Catches US workday cycle (announcements, press releases, midday scoops) | **Email** — hello@example.com |

**Delivery rule: Scheduled IronPulse cron jobs ALWAYS deliver via email.** Do NOT set `deliver: "telegram"` for scheduled runs. Vinny expects the report in his inbox. Telegram is for interactive quick-scan outputs only.

**Goal:** 24 unique stories per day (12 morning + 12 afternoon).

### Deduplication via `context_from`

The afternoon cron job uses Hermes' `context_from` feature to receive the morning report's output before running:

The afternoon job's prompt MUST include explicit deduplication instructions:
- "Read the morning output injected as context below"
- "Identify the 12 stories already covered"
- "Find 12 DIFFERENT stories — ones NOT covered in the morning report"
- "If fewer than 12 fresh stories exist, mark forced duplicates with [DUPLICATE]"

### Cron Prompt Pattern

Each cron's `prompt` field must spell out the full workflow — not just "run IronPulse":

For the **morning** cron: standard gather → report → Desktop copy → themes → article ideas delivery.

For the **afternoon** cron: same workflow PLUS deduplication instructions referencing context_from output. The context is automatically injected by Hermes before the cron prompt runs.

### Configuring Context From

When creating or updating the afternoon cron job, set context_from pointing to the morning job ID.

This ensures the afternoon agent sees the morning report's full output before generating its own.

## Analysis Delivery Mode (Scheduled Cron Runs)

When IronPulse is triggered as a **scheduled cron job** (not interactive), the delivery must include more than just the file path. Vinny specified this format for cron-based runs:

**Delivery message must contain:**
1. First line: Windows-native file path (`~\\Desktop\\ironpulse-YYYY-MM-DD.txt`)
2. **Themes & Messages Summary** — 2-4 paragraphs identifying the dominant themes, patterns, or narratives connecting multiple stories in today's batch. What does the data actually say?
3. **3 Article Ideas** — Specific, compelling article ideas for phantom-byte.com, grounded in what the data actually shows. Do not force ideas if nothing is interesting.
4. **Namediff required for every theme** — Each theme MUST explicitly state why it does NOT overlap with a specific published PhantomByte article. Reference the actual article titles from articles.phantom-byte.com. A theme that overlaps without acknowledgment will be proposed as a duplicate on the next editorial pass. This rule applies to ALL theme delivery contexts: email body, Telegram inline delivery, and cron inline output.
5. Note that the full report (ranked stories, Pinterest/X posts) is at the delivered path for reference.

**Include the full IronPulse analysis prompt in the cron job's `prompt` field**, not just "run IronPulse." The cron prompt must spell out: gather stories, write report, copy to Desktop, analyze themes, deliver analysis + path.

## TensorFeed Reports

When the user says "tensorfeed report" (any variant: TensorFeed, tensorfeed, TENSORFEED):

1. **Run the report:** Use `python scripts/tensorfeed_news.py` from `/mnt~/workspace/` to get headlines, then browse stories directly for full 5-sentence summaries.

2. **Save everything to a file FIRST** — `/mnt~/Desktop/tensorfeed-report-YYYY-MM-DD.txt`. Write the full report to this path using `write_file`. This is MANDATORY before any other action.

3. **Email the file as attachment** to hello@example.com via IONOS SMTP (smtp.ionos.com:587, user hello@example.com, pass VJBvjbhydro1202$$). Use `MIMEMultipart` with `MIMEBase` attachment — never inline body text.

4. **Reply in Telegram with ONLY the file path.** Example: `~\Desktop\tensorfeed-report-2026-05-16.txt`

**CRITICAL: Never paste report content into Telegram.** The full report stays in the file. Telegram gets only the path. This is a hard rule — Vinny has yelled at me multiple times about this.

For 7-day AI news reports ("Larry Weekly"), the dedicated skill `larry-weekly-news` (now archived — content folded here) defines the full workflow:

**Trigger:** "run larry weekly," "generate larry weekly," "weekly news report," or similar explicit request. Runs on demand, not scheduled.

**Process:** Same sources as IronPulse (RSS-first), but scope is 7 days, exactly 12 stories ranked best-to-worst, with 3 unpublished PhantomByte themes and 3 specific article ideas.

**Output:** Saved to `~/.hermes/workspace/larry-weekly/larry-weekly-MMM-DD-YYYY.txt`, copied to Windows Desktop, and emailed to hello@example.com with subject "Larry Weekly News News trends and themes."

**Key differences from daily IronPulse:**
- 7-day window instead of 24-hour
- 3 themes + 3 article ideas always required (not optional)
- Always includes email delivery via IONOS SMTP
- No Pinterest/X social post generation
- Bias guardrails aligned with IronPulse

The `references/ironpulse-weekly-variant.md` reference file contains the full weekly-mode extraction and delivery steps.

### Email Delivery (IONOS SMTP)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart()
msg['From'] = 'hello@example.com'
msg['To'] = 'hello@example.com'
msg['Subject'] = 'Larry Weekly News News trends and themes'

body = """Larry,

[3-theme summary in bullets]
[3 article ideas listed by title]

Full report with all 12 ranked stories is in the attachment.

— Hermes
"""
msg.attach(MIMEText(body, 'plain'))
with open('~/.hermes/workspace/larry-weekly/larry-weekly-MMM-DD-YYYY.txt', 'r') as f:
    attachment = MIMEText(f.read(), 'plain')
    attachment.add_header('Content-Disposition', 'attachment', filename='Larry Weekly News - MMM DD YYYY.txt')
    msg.attach(attachment)

with smtplib.SMTP('smtp.ionos.com', 587) as server:
    server.starttls()
    server.login('hello@example.com', 'VJBvjbhydro1202$$')
    server.sendmail('hello@example.com', 'hello@example.com', msg.as_string())
```

## Breaking-News Override — Trust the User's Tip (CRITICAL)

If the user tells you something is current, happening now, or widely reported, and your first search comes back stale or negative:
1. Do not argue with them. Do not ask for a source.
2. Do not repeat the same failed search with different phrasing against the same source.
3. Breadth-first, immediately across distinct outlets. Target 5+ different domains in one pass.
4. Explicit secondary searches: Google News for the company/event name, plus one major MSM tech/business outlet (FT, Reuters, Bloomberg, WaPo, WSJ, BBC).
5. If a search returns no results, treat that as a signal the search query is wrong, not that the event didn't happen.

**Rule:** When the user corrects you with "they flew people in today," that is a breaking-news fact to verify, not a viewpoint to debate.

## Event-Dominant News Days — Editorial Balance Protocol

On some days, a single event or company will dominate 60-100% of available within-24-hour AI stories across all sources. Examples: WWDC, OpenAI DevDay, Google I/O, major model releases, regulatory bombshells. When this happens, the skill's existing sourcing rules ("12 stories from 4+ domains") are mechanically satisfied but produce an editorial monoculture — not useful for Vinny's PhantomByte workflow.

**When to activate:** If after browsing TechCrunch + The Verge + Google News, 6+ of the first 10 stories you see are about the same company/event, you're on an event-dominant day.

**Protocol:**

1. **Cap the dominant event at 5 stories max.** No more than 5 of the 12 stories should cover the same event, no matter how many sources are covering it. The best 5 (ranked by newsworthiness) stay; the rest get cut.

2. **Fill the remaining 7 slots with genuinely different stories.** This may require:
   - Browsing Fox News Tech, Hacker News, or Scientific American for non-dominant-event stories
   - Going deeper into the Google News feed (scroll past the top results which are all dominated by the event)
   - Accepting stories from the "24 hours but not trending" zone — stories with fewer sources but real substance
   - Using Hacker News for AI/ML research stories that don't follow the event cycle

3. **Ranking adjustment on event days:** The dominant event stories should NOT auto-rank as #1-5 just because they have the most sources. Rank:
   - #1-2: The most newsworthy angle from the event (the reveal, not the recap)
   - #3-5: The most counterintuitive/controversial non-event stories
   - #6-8: Deeper event angles (infrastructure, regulatory implications)
   - #9-12: Other non-event stories that deserve coverage

4. **Theme generation on event days:** At least 2 of the 3 themes should draw FROM the non-event stories. The dominant event should contribute at most 1 theme. Otherwise the report reads as "Company X dominates everything" and the themes analysis becomes redundant with the story list.

5. **Example from June 8, 2026 (WWDC):** Apple dominated TechCrunch (9/12 stories), The Verge (5/6 LATEST IN AI), and Google News (top 5 results all Apple). Rather than 12 Apple stories, the report capped Apple at 5 and added: Amazon AI merch launch, Microsoft/OpenAI drama, NotebookLM upgrade, AI in medicine (NYT), Apple M5 security bypass, Waymo, wheeled home robot, and a Fox News AI regulation poll. The 3 themes drew from non-Apple stories (infrastructure surrender, cannibalization era, unregulated medical AI).

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

