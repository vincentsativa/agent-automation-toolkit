# Daily Data Workflow

## How the Day Works

Cron jobs dump data files to the user's Windows desktop throughout the day. The data lands in:

```
C:\Users\<user>\OneDrive\Desktop\TODAYS DATA FILES
```

From WSL, this is: `/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES`

## The Core Principle: The Data Leads

The data tells its own story. You do not decide what to write about. You read the data, synthesize it, see what it exposes, and write about that.

- Never pre-commit to an article sequence or outline before reviewing the day's data.
- When Vinny says "let's see what the data says," he means it literally.
- Outlines from previous days are reference material, not commitments. Tomorrow's data may expose a completely different story.

## Standard Data Files

| File | Source | Contents |
|---|---|---|
| `ironpulse-YYYY-MM-DD.txt` | IronPulse | Top 12-20 ranked AI news stories with Pinterest/X post copy |
| `tensorfeed_report_YYYY-MM-DD.txt` | TensorFeed | 15-25 deep story summaries, 3 emerging themes, 3-5 article recommendations with coverage gap analysis |
| `blogwatcher-dump-YYYY-MM-DD.txt` | Blogwatcher | Editorial brief with headlines and unwritten themes with namediffs |
| `20-AI-News-Stories-YYYY-MM-DD.md` | Aggregated | Consolidated 20-story digest with Pinterest/X copy and 3-5 synthesis themes |
| `What are today's top 30 AI-related story headlines.md` | BuildFastWithAI | Ranked top-30 with 5 exposed themes, inline footnote citations |
| `Weekly_AI_News_Report_YYYY-MM-DD.txt` | TensorFeed weekly | 30 ranked stories with 5 themes |

## When Vinny Asks About Outlines

If Vinny asks "which outline should we write next" or similar, the correct answer is: "Let's see what today's data says first." Do not recommend a sequence or lock in a plan. The data may expose something stronger than yesterday's outlines.
