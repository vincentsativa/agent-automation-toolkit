# IronPulse Weekly Variant, 7-Day Research Mode

## When This Applies

When the user asks for "weekly" AI news (last 7 days, not last 24 hours), or "top stories this week," or any variant that implies a weekly rather than daily window, this is the **IronPulse Weekly Variant**. It differs from the standard IronPulse daily workflow in output format, depth, and analytical scope.

## How It Differs From Daily IronPulse

| Aspect | Daily IronPulse | Weekly IronPulse |
|--------|----------------|-----------------|
| Time window | Last 24 hours | Last 7 days |
| Story count | 12 | 12 |
| Output format | Ranked list + social posts | Ranked list + themes + article ideas |
| Social content | Pinterest + X posts | **None**, skip entirely |
| Summary length | Exactly 4 sentences | 4-5 sentences |
| Theme analysis | Only in cron mode | **Required**, 3 themes, grounded in data |
| Article ideas | Only in cron mode | **Required**, 3 ideas, not on PhantomByte |
| Delivery | File + Desktop | File + Desktop + **email to hello@phantom-byte.com** |

## Output Format (Weekly Variant)

```
LARRY WEEKLY NEWS, WEEK OF [DATE RANGE]
Report Date: [Today's Date]
Sources: [List primary sources]

═══════════════════════════════════════════════
TOP 12 AI STORIES ([Date Range])
Ranked Best to Worst for PhantomByte Coverage
═══════════════════════════════════════════════

#1, [HEADLINE]
Source: [Source Name] | Published: [Relative time]
[4-5 sentence summary]
Relevance to PhantomByte: [2-3 sentences on why this matters to PhantomByte's coverage areas]

---

[Repeat for all 12]

═══════════════════════════════════════════════
THREE THEMES EXPOSED BY THE DATA
(Not Yet Covered on PhantomByte)
═══════════════════════════════════════════════

THEME 1: [NAME], [2-3 paragraph analysis]
THEME 2: [NAME], [2-3 paragraph analysis]
THEME 3: [NAME], [2-3 paragraph analysis]

═══════════════════════════════════════════════
THREE ARTICLE IDEAS
(Not Yet on articles.phantom-byte.com)
═══════════════════════════════════════════════

ARTICLE IDEA 1: "[Headline Suggestion]"
Angle: [Category], [2-3 sentence pitch connecting to PhantomByte's coverage]
[Expand on why this story matters to the PhantomByte reader]

ARTICLE IDEA 2: ...
ARTICLE IDEA 3: ...

---

END OF REPORT
```

## Research Strategy (Weekly)

The 7-day window means stories may appear across multiple visits. Use RSS feeds as the primary data source:

1. **TechCrunch AI RSS**, `https://techcrunch.com/category/artificial-intelligence/feed/`, 5-8 stories
2. **The Verge AI RSS**, `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`, 3-5 stories
3. **Google News AI RSS**, `https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en`, supplement for MSM diversity
4. **Fox News AI RSS**, `https://moxie.foxnews.com/feedburner/artificial-intelligence.xml`, 1-2 stories
5. **Hacker News RSS**, `https://hnrss.org/frontpage?count=30`, AI/ML trending stories
6. **Ars Technica AI RSS**, `https://arstechnica.com/ai/feed/`, engineering-focused stories

**4+ distinct domains required.** RSS first, browser fallback only when RSS fails.

## Theme Analysis Method

1. After collecting all 12 stories, look for **patterns across multiple stories**, not just individual story themes
2. Ask: what do 3+ stories this week have in common? That's a theme
3. For each theme, verify it hasn't been covered on PhantomByte by checking articles.phantom-byte.com
4. Each theme should have: a name, 2-3 paragraphs of analysis, and specific story anchors from the report

## Article Idea Method

1. Ideas must flow directly from the theme analysis, not be arbitrary
2. Each idea needs: a headline suggestion, a category tag, a 2-3 sentence pitch, and a concrete reason it hasn't been covered
3. Verify against PhantomByte's recent articles (last 2 weeks minimum) before finalizing
4. Prioritize ideas that connect infrastructure/investment themes with workforce/economics, PhantomByte's sweet spot

## Email Delivery (Weekly Variant)

**Required for weekly variant, not part of daily IronPulse.**

Subject line: `Larry Weekly News News trends and themes`

Body should contain:
- Brief intro noting the report is attached
- Summary of the 3 themes (1-2 sentences each)
- The 3 article ideas (1 sentence each + full list)
- Note that full report with all 12 ranked stories is attached

Email credentials: IONOS SMTP, smtp.ionos.com:587, user hello@phantom-byte.com, pass [from memory]. Send to hello@phantom-byte.com (self-send for agent-to-agent file hub).

Python email code, use `MIMEText` (NOT `MimeText`):

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# NOT: from email.mime.text import MimeText  ← this import fails
```

## Cross-Checking Against PhantomByte

Before finalizing themes and article ideas, browse or snapshot articles.phantom-byte.com and verify:
- None of the 3 themes have been covered in the last 2 weeks
- None of the 3 article ideas overlap with recent headlines from the site
- If a theme overlaps with recent PhantomByte content, note it and pivot to the next most interesting pattern

## Trigger Phrases for Weekly Variant

- "weekly AI news" / "this week's AI news"
- "top AI stories this week" / "most important AI news this week"
- "find me the top 12 AI stories from the last 7 days"
- Any request that says "weekly" or "this week", even if it doesn't say "run ironpulse"
- "Larry weekly" / "Larry's weekly", referring to the agent-to-agent weekly news format