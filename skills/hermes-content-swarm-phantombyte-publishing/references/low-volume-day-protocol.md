# Low-Volume Day Protocol for Editorial Briefs

When running a blogwatcher editorial brief on a weekend, holiday, or any day where only 2-3 of 13+ feeds produce fresh content, follow this protocol.

## The Pattern (Verified July 11, 2026, Saturday)

On July 11, 2026 (Saturday), only 3 of 13 feeds had articles published that day:
- The Decoder (6 AI articles)
- Wired Ideas (1 AI article out of 12 total)
- TechCrunch AI (1 article)

The remaining 10 feeds (Ars Technica AI, MIT Tech Review AI, Google AI, NVIDIA AI, The Verge AI, AI News, Ben's Bites, AI Weekly, Hugging Face, arXiv) had zero articles from July 11.

## What to Do When Today Alone Is Insufficient

### 1. Expand the window to yesterday

When today's date yields fewer than 12 AI-relevant headlines, include yesterday's articles from feeds that are normally active. This is the primary fallback, not arXiv papers, not TensorFeed.

**How to do it:** After the initial `--all` date-filtered pass for today, run a second pass for yesterday's date. Merge the results, deduplicate by URL, and include yesterday's articles in the brief.

**Mark them clearly:** Add a `(Yesterday)` tag after the source name for any article not from today:
```
[5] OpenAI admits it "didn't get everything quite right" with ChatGPT Work launch
    Source: The Decoder (Yesterday)
```

### 2. Do NOT pad with arXiv papers

The blogwatcher skill's rule still applies: arXiv is a last resort, not a daily requirement. Even on a low-volume day, do not add arXiv papers to reach an arbitrary count. A tight 8-10 headline brief is better than a padded 12-headline one.

### 3. Do NOT pad with non-AI content

Wired Ideas produces 10-20 articles daily but only 1-2 are AI-related. On a low-volume day, the temptation is to include borderline articles (space probes, dog food, hiking boots, concert reviews) to fill space. Resist. Only include articles genuinely relevant to an AI/tech audience.

### 4. Do NOT pad with stale content

If a feed's most recent article is 3+ days old, skip the entire source. Do not include "close enough" articles from 2 days ago to inflate the count. The yesterday-expansion only applies to feeds that had articles yesterday, not feeds that haven't published in days.

### 5. Note the low volume in the brief

Add a line at the top of the editorial brief:
```
Note: Low-volume day, only X of 13 feeds had fresh content. Brief expanded to include yesterday's articles from active feeds.
```

### 6. The 3 unwritten themes requirement still stands

Even with only 8-10 headlines, you can identify 3 themes. The themes may be narrower or more speculative, but the cross-reference against PhantomByte's archive is still valuable. If genuinely only 1-2 themes emerge, note that and deliver what you have.

### 7. Do not fabricate headlines or themes

If the data doesn't support 3 themes, deliver 2. The user would rather see honest scarcity than manufactured insight.

## Why This Matters

The blogwatcher skill's editorial brief workflow assumes most feeds are active (based on June 2026 observations). But weekends consistently produce fewer articles. Without this protocol, the agent either:
- Pads with arXiv papers (bad, dilutes the brief)
- Pads with non-AI content (worse, wastes the user's time)
- Pads with stale content (worst, erodes trust)
- Or delivers a thin brief and looks incompetent

The yesterday-expansion is the cleanest fix: it adds real, relevant, recent content without sacrificing quality.

## Example: July 11, 2026 Brief

- Today's articles: 8 AI-relevant headlines (6 Decoder + 1 Wired + 1 TechCrunch)
- Yesterday's articles added: 5 from The Verge AI + 2 from Google AI
- Total: 15 headlines from 5 sources
- Result: Clean brief, no padding, 3 unwritten themes identified
