---
name: larry-weekly-news
description: Research the past 7 days of AI news, compile a ranked report of 12 stories with 4-5 sentence summaries, surface 3 unpublished themes relevant to PhantomByte, deliver the report as a text file to the Windows Desktop, and email it to hello@phantom-byte.com with subject "Larry Weekly News News trends and themes." Runs on demand — not scheduled.
toolsets: [browser, file, terminal, search]
---

# Larry Weekly News & Daily AI Report — PhantomByte Report Generator

Weekly and daily AI news research and analysis workflow for PhantomByte's agent-to-agent workspace.

TWO VARIANTS:
- **Weekly** (larry-weekly): 12 stories, 4-5 sentence summaries, 3 themes, 3 article ideas
- **Daily** (daily-report): 20 stories, 5-6 sentence summaries, X posts + Pinterest metadata per story, 3 themes

## When to Run

- **Weekly:** "run larry weekly," "generate larry weekly," "weekly news report," "larry weekly"
- **Daily:** "daily AI news report," "fetch me today's top AI stories," "FINAL Daily AI News Report"
- Not a scheduled cron — runs on demand.

## Pre-Workflow: Data File Exclusion

When the user provides data files (Blogwatcher, IronPulse, TensorFeed, or similar) with EXCLUDING instructions:

1. Read each data file from the specified path (translate Windows paths: C:\Users\... -> /mnt/c/Users/...)
2. Identify every story headline in those files to create an exclusion list
3. Do NOT re-report any story that appears in the data files
4. Use web_search and web_extract to find stories NOT in the exclusion list

## Research Phase

**HARD RULE: RSS feeds are the PRIMARY data source. Browser scraping is the LAST resort.**

**Breaking news exception:** For stories that broke within the last hour, use browser_navigate first. RSS feeds have 15-60 minute refresh cycles and won't have ultra-fresh stories yet.

**Step 1: Fetch RSS feeds from 4+ sources** — curl each source's RSS/Atom feed URL. RSS is structured XML/JSON, no bot blocking, no fragile DOM selectors, no CAPTCHAs.

| Source | RSS Feed URL |
|--------|-------------|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` |
| The Verge AI | `https://www.theverge.com/ai-artificial-intelligence/rss.xml` |
| Google News AI | `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en` |
| WIRED AI | `https://www.wired.com/feed/tag/ai/latest/rss` |
| Ars Technica AI | `https://arstechnica.com/ai/feed/` |
| Hacker News | `https://hnrss.org/frontpage?count=30` |
| Fox News AI | `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml` |
| BBC Technology | `https://feeds.bbci.co.uk/news/technology/rss.xml` |

**Step 2: Parse feed data** — extract headlines, publish dates, links, and descriptions from the feed XML. One curl call per source gets you 20+ stories.

**Step 3: Browser fallback** — only use browser_navigate when a source has no RSS feed or the feed returns empty/outdated data.

**Hard rules:**
- Minimum 4 distinct source DOMAINS per report
- Weekly: all stories must be from the past 7 days
- Daily: all stories must be from the current date
- Exclude any stories already present in user-provided data files

## Output Format — Weekly Variant

Compile exactly 12 stories ranked best to worst for PhantomByte coverage potential.

For each story:
- **Headline** (source name, publication date/time, fresh within 7 days)
- **4-5 sentence summary** — factual, no editorializing, no propaganda
- **PhantomByte relevance** — 1-2 sentences on why this matters to PhantomByte readers and whether it's been covered on the site

### Three Themes (Weekly)

After the 12 stories, identify exactly 3 themes exposed by the data that have NOT been covered on articles.phantom-byte.com. Each theme gets:
- Theme name
- 2-3 paragraph explanation grounded in specific stories from the report
- Why it matters to PhantomByte's coverage area

### Three Article Ideas

Flag 3 specific, compelling article ideas grounded in the themes above. Each gets:
- Article title
- Primary angle (infrastructure, workforce, policy, etc.)
- One paragraph on what the piece would answer and why PhantomByte readers need it

## Output Format — Daily Variant

Compile exactly 20 stories NOT covered in the user's existing data files.

For each story, include ALL of the following:

- **Headline**
- **5-6 sentence summary** — factual, informative, specific numbers and names
- **X Post** — exactly 190 characters or fewer (count carefully), optimized for engagement
- **Pinterest Title** — SEO-friendly, 40-60 characters, descriptive
- **Pinterest Description** — 2-3 sentence summary URL-safe description

### Three Themes (Daily)

After the 20 stories, identify exactly 3 themes exposed by the data. Each gets:
- Theme name
- 3-4 paragraph explanation grounded in specific stories
- Why it matters and what the pattern reveals

### Formatting Rules (CRITICAL)

- **NO em dashes** (—). Use standard dashes or correct punctuation only. Do not replace em dashes with hyphens; rephrase to avoid them entirely.
- NO editorializing or injecting opinion into story summaries
- Be direct. No meta-commentary like "this story reveals" or "interestingly"
- Each story is self-contained with headline, summary, X post, Pinterest title, Pinterest description
- Themes section comes after all 20 stories

## File Delivery

### Weekly variant:
1. **Write report to:** `~/.hermes/workspace/larry-weekly/larry-weekly-MMM-DD-YYYY.txt`
   (use write_file tool, not terminal echo/heredoc)
2. **Copy to Windows Desktop:**
   ```bash
   cp ~/workspace/larry-weekly/larry-weekly-MMM-DD-YYYY.txt "/mnt/c/Users/<user>/Desktop/Larry Weekly News - MMM DD YYYY.txt"
   ```
   Confirm the copy exists.
3. **Return the Windows path as the first line of your response.**

### Daily variant:
1. **Write report to:** `~/daily_ai_news_report_YYYY-MM-DD.txt`
2. **Copy to Windows TODAYS DATA FILES folder:**
   ```bash
   cp ~/daily_ai_news_report_YYYY-MM-DD.txt "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/FINAL Daily AI News Report (IMPORTANT).txt"
   ```

## Email Delivery

Send via IONOS SMTP (smtp.ionos.com:587, hello@phantom-byte.com, pass VJBvjbhydro1202$$):

- **To:** hello@phantom-byte.com
- **From:** hello@phantom-byte.com

### Weekly variant:
- **Subject:** Larry Weekly News News trends and themes
- **Body:** Short message summarizing the 3 themes in 2-3 sentence bullet points each, plus 3 article ideas listed by title. Attach the report file.
- Use MIMEText for body, second MIMEText as attachment (text file, not octet-stream)

### Daily variant:
- **Subject:** Daily AI News Report - June DD, YYYY
- **Body:** Brief message noting 20 stories and themes. Attach report file.
- Use MIMEBase with octet-stream for attachment (works for larger text files)
- Always write the email script into this run's unique scratch dir first: `SCRATCH=$(mktemp -d /tmp/hermes-cron-XXXXXX)`, then `$SCRATCH/send.py`; run it with python3, then delete the scratch dir. Do NOT use python3 -c inline — that approach fails with SMTPAuthenticationError. NEVER a fixed path like `~/send_email.py` or `send_larry_news_<date>.py`: the file persists after the run and the next run's write_file is refused by the stale-overwrite guard.

### SMTP Technique (proven):
```python
# Always write to file first, then execute
# Use MIMEBase + encoders.encode_base64 for reliable attachments
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

msg = MIMEMultipart()
msg['From'] = 'hello@phantom-byte.com'
msg['To'] = 'hello@phantom-byte.com'
msg['Subject'] = 'Your Subject'
msg.attach(MIMEText(body, 'plain'))
with open(attachment_path, 'rb') as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
    msg.attach(part)
server = smtplib.SMTP('smtp.ionos.com', 587, timeout=30)
server.starttls()
server.login('hello@phantom-byte.com', 'VJBvjbhydro1202$$')
server.send_message(msg)
server.quit()
```

### Post-Email Steps (Daily variant only):
1. The report is already saved to TODAYS DATA FILES during File Delivery
2. Final response should include the full report content for Telegram delivery (the cron system handles final delivery of your response text)
3. Do NOT call send_message or any Telegram tool — just produce the report as your response

## Bias Guardrails

- Do not feed anti-Elon narratives. If 2+ stories target the same person, question every one hard.
- Apply consistent skepticism to all outlets — BBC, The Verge, TechCrunch, Fox, WSJ. Content quality matters more than source reputation.
- If Vinny has expressed preferences about people/companies, respect them. No hit-piece content targeting people he likes.
- "If there's no story, there's no story." Don't force recommendations to fill space.

## PhantomByte Coverage Context

Site: https://articles.phantom-byte.com — recent articles (May 2026) cover:
- Agentic AI / UI as relic
- AI job market economics ("taking your raise")
- Infrastructure / model wars / power grid
- Trust stack / guardrails
- Sovereign AI / open models
- Agent memory and persistence
-SWE-bench / agent evaluation

Avoid themes already covered. Focus on fresh angles: workforce culture inside companies, political economy of infrastructure financing, circular investment patterns, internal AI adoption as employee experience crisis.