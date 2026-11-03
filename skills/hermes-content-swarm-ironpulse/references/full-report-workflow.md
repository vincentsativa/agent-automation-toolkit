# IronPulse — Full Report Workflow

Loaded on demand by the ironpulse SKILL.md when the request is a full report (file to Desktop, social posts, themes, article ideas). A quick scan does NOT need this file.

## Instructions

### Research Phase — RSS First, Browser Fallback

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort, used only when a source has no RSS feed or the feed is broken.**

**Breaking news exception:** For stories that broke within the last hour, use browser_navigate first. RSS feeds have 15-60 minute refresh cycles and won't have ultra-fresh stories yet. The browser catches what RSS misses on the bleeding edge.

1. **Find top 30 AI-related story headlines from last 24 hours**
   - **Step 1: Fetch RSS feeds** — curl each source's RSS/Atom feed URL. RSS is structured XML/JSON, no bot blocking, no fragile DOM selectors, no CAPTCHAs, no 404s from stale article URLs.
   - **Step 2: Parse feed data** — extract headlines, publish dates, links, and descriptions from the feed XML/JSON. This gives you 20+ stories in a single tool call per source.
   - **Step 3: Browser fallback** — only use browser_navigate when a source has no RSS feed or the feed returns empty/outdated data.
   - Minimum of 6 different sources required
   - At least one MSM (Mainstream Media) news website required
   - Stories must be from last 24 hours exactly

2. **For each of 30 stories, provide:**
   - An informative summary of exactly 4 sentences
   - Source attribution
   - Verify recency (within 24 hours)

3. **List stories in order**
   - From best story to write about to worst story to write about
   - Consider: newsworthiness, viral potential, uniqueness, relevance


### Output

Save all results to: `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`

**CRITICAL — Windows path delivery:** Vinny's on WSL but uses Windows. After writing the file:
1. Copy it to Windows Desktop: `cp ~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt/c/Users/<user>/Desktop/ironpulse-YYYY-MM-DD.txt"`
2. Return the **Windows-native** full path as the very first line of your response: `C:\Users\<user>\Desktop\ironpulse-YYYY-MM-DD.txt`
3. Do NOT return the WSL path (~/...) — Vinny can't paste that into Windows File Explorer or Run dialog
4. A "full file path" means one he can copy-paste directly into a Windows context (Explorer, cmd, Run dialog)
5. If you're unsure of the Windows username, check `/mnt/c/Users/`

**Format:**
```
IRONPULSE AI NEWS REPORT
Date: YYYY-MM-DD

TOP 30 AI STORIES (Best to Worst)

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
[Continue for all 30, ranked best to worst]

END OF REPORT
```

**DO NOT** send multiple messages. Send single file path.

**Tension Between Reports and Articles (Cost Logic):**
- **Reports (Cheap):** Rely on discrete tool calls (Browser $\rightarrow$ File). The model acts as a router; outputs are stored on disk. Low token-completion load.
- **Articles (Expensive):** Heavy continuous generation. Long-form output requires the model to attend to the entire emerging text and a massive context window (often 100k+ tokens) for every new word. This "completion tax" is significant.
- **The Solution:** For long-form writing, **bypass the chat window**. Use `write_file` or a dedicated script to move the output directly to disk, avoiding the expensive repetitive re-processing of the conversation history.

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
   curl -sL "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
   
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

6. **Compile 30 stories ensuring:**
   - All published within 24 hours
   - At least 4 different source DOMAINS represented
   - Rank #1 (most newsworthy) to #30 (least)
   - Hard rule: if you can't name 4 distinct domains, you haven't fetched enough RSS feeds

**Step-by-step process (curl fallback path — when browser is unavailable):**

1. **Create output directory:**
   ```bash
   mkdir -p ~/.hermes/workspace/ironpulse-outputs/
   ```

2. **Check PhantomByte inventory via curl:**
   ```bash
   curl -sL "https://articles.phantom-byte.com" | grep -oP '<h3 class="card-title">.*?</h3>' | sed 's/<[^>]*>//g'
   curl -sL "https://articles.phantom-byte.com" | grep -oP '<span class="card-date">.*?</span>' | sed 's/<[^>]*>//g'
   ```

3. **Extract TechCrunch article URLs and fetch each story:**
   ```bash
   curl -sL "https://techcrunch.com/category/artificial-intelligence/" | grep -oP 'href="https://techcrunch\.com/2026/[^"]*"' | sort -u | head -15
   ```
   For each URL, fetch headline, datetime, and body text. See `references/techcrunch-extraction-technique.md` for full details.

4. **Extract Verge AI stories:**
   ```bash
   curl -sL "https://www.theverge.com/ai-artificial-intelligence" | grep -oP 'href="/[^"]*"[^>]*>' | grep -v 'static\|rss\|favicon\|font\|next\|css\|legal\|auth' | grep '^href="/[a-z]' | sort -u | head -30
   ```
   Filter for `/ai-artificial-intelligence/` paths. Fetch each for headline, publishedAt, and body. See `references/verge-extraction-technique.md`.

5. **Extract Google News AI stories:**
   ```bash
   curl -sL "https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en" | grep -oP 'aria-label="[^"]*"' | head -20
   ```
   Parse aria-labels for headline, source, and timestamp. See `references/google-news-extraction-technique.md`.

6. **Supplement with additional sources** (BBC, Fox News, etc.) via curl to reach 30 stories and 4+ domains.

7. **Compile 30 stories ensuring:**
   - All published within 24 hours
   - At least 4 different source DOMAINS represented
   - Rank #1 (most newsworthy) to #30 (least)
   - Hard rule: if you can't name 4 distinct domains (e.g. TechCrunch, The Verge, WIRED, Fortune), you haven't done enough browser research

8. **For each story create:**
   - 4-sentence summary
   - Pinterest title (50-70 chars, SEO-friendly)
   - X.com post (EXACTLY 190 characters including hashtags)

9. **Write output file using write_file:**
   - Path: `~/.hermes/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt`
   - Must use write_file tool, not terminal echo

10. **Copy to Windows Desktop for easy access:**
    - After writing the file, copy it to the Windows user's Desktop:
      - `cp ~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt/c/Users/<user>/Desktop/ironpulse-YYYY-MM-DD.txt"`
    - If the user specified a OneDrive subfolder (e.g. `TODAYS DATA FILES`), ALSO copy there:
      - `cp ~/workspace/ironpulse-outputs/ironpulse-YYYY-MM-DD.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/ironpulse-YYYY-MM-DD.txt"`
    - Verify the copies exist.

**Interactive mode path delivery —** First line is the Windows-native full path, nothing else.
**Cron/scheduled mode delivery —** First line is the Windows-native full path, followed by analysis sections (see "Analysis Delivery Mode" below).

**Interactive mode with analysis (PhantomByte editorial workflow):**
When Vinny runs IronPulse interactively and specifically requests themes and article ideas, the delivery has three parts:

1. **File delivery (Desktop + OneDrive subfolder if specified):**
   - Copy to `C:\Users\<user>\Desktop\ironpulse-YYYY-MM-DD.txt`
   - If Vinny specified a OneDrive subfolder (e.g. `TODAYS DATA FILES`), ALSO copy there: `C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES\ironpulse-YYYY-MM-DD.txt`
   - Verify both copies exist

2. **Email delivery:** Send the full report as a MIMEMultipart attachment to hello@phantom-byte.com, with the 3 themes and 3 article ideas in the email body (above the attachment reference). Each theme should include the namediff — explicitly stating why it does NOT overlap with a specific published PhantomByte article. IONOS SMTP: smtp.ionos.com:587, user hello@phantom-byte.com, pass VJBvjbhydro1202$$. Subject format: `IronPulse Report - YYYY-MM-DD - AI News + 3 Unpublished Themes`.

3. **Telegram notification (email confirmed):** When the user explicitly requests "Message me on Telegram after the email has been sent," send a brief notification confirming delivery. This is a confirmation of the email being sent, NOT a report delivery — keep it short (e.g. "Sent. 30 stories, 3 themes in the email body. File at path."). Do NOT paste report content (headlines, summaries, themes, or ideas) into the notification.

**CRITICAL - Telegram delivery rule:** The file path and email-sent confirmation are the only acceptable Telegram messages. Do NOT reproduce headlines, summaries, themes, or article ideas in the Telegram message. If Vinny wants to discuss the report, he'll read the file on Desktop and engage in conversation. Sending analysis inline in Telegram violates this preference — UNLESS Vinny explicitly asked to be messaged after email delivery. That request turns Telegram into a notification channel, not a report channel.

**User Preference: Analysis Content**
- Focus on "The Human-First Premium" (AI backlash as a luxury market opportunity).
- Explore the "Paradox of the AI Wallet" (High trust for finance, high demand for data erasure).
- Frame institutional shifts as the "Governance Phase" (Moving from raw output to human dignity/integrity).

[DELETED delivery mode description]

**CRITICAL — ALWAYS return a Windows-native path** (`C:\\Users\\<user>\\Desktop\\ironpulse-YYYY-MM-DD.txt`). Never return a WSL path or `\\\\wsl.localhost\\...`. The user works on Windows and needs paths he can paste into File Explorer, text editors, and other Windows applications directly.

**Email delivery for scheduled runs:** When creating a cron job for IronPulse, set `deliver: "email"` — Vinny expects the report in his inbox, not a Telegram message. The delivery target is part of the job definition, not optional metadata. If you don't know his email address, it's hello@phantom-byte.com (the IONOS account). Telegram delivery is for interactive-mode quick outputs only; scheduled reports go to email.
