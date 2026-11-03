# User Sentiment Research, API Workflow & Pitfalls

Extracted from the "Nemotron Ultra" research session (June 4, 2026). Covers the working API-based workflow for finding real user opinions when search engines are blocked.

## The Problem
Search engines (Google, DuckDuckGo, Bing, Reddit) all CAPTCHA-block cloud IPs from moderate-depth queries. You get one chance before the browser kicks you to a CAPTCHA page. Never retry, pivot to APIs immediately.

## Working APIs (Ranked by Value)

### 1. HN Algolia, BEST source
- **Rate limit**: 10K+ req/hr, no auth
- **Stories**: `https://hn.algolia.com/api/v1/search?query=MODEL_NAME&tags=story&hitsPerPage=30`
- **Comments**: `https://hn.algolia.com/api/v1/search?query=MODEL_NAME&tags=comment&hitsPerPage=50`
- **Full thread**: `https://hn.algolia.com/api/v1/items/STORY_ID`
  - Returns full tree. `children[].text` = comment body, `children[].author`, nested `children[]` = replies
- **By points**: `&numericFilters=points>0`
- **What it yielded for Nemotron Ultra**: 9 stories, 16 comments. ~4 substantive user comments with real impressions. Comments were 2-3 sentences each; no deep multi-paragraph reviews exist because the model is too new.

### 2. HuggingFace API, Engagement proxy
- **Model search**: `https://huggingface.co/api/models?search=MODEL_NAME&sort=lastModified&direction=-1&limit=20`
- **Discussions**: `https://huggingface.co/api/models/ORG/MODEL/discussions?limit=30`
- **What it yielded**: 550B BF16 variant, 384 downloads, 70 likes. NVFP4 variant, 196 downloads, 60 likes. These numbers are low for a flagship model release, suggesting limited real-user adoption (too large for consumer hardware).

### 3. TensorFeed, Context signal
- `tf.news_recent(hours=72, limit=50)` then filter for model name
- **What it yielded**: Only 1 Nemotron article in the last 72 hours, a blog post about Nemotron 3.5 Content Safety (unrelated). The Ultra launch did not register strongly in technical feeds.

### 4. Reddit via pullpush.io, Unreliable from cloud
- `https://api.pullpush.io/reddit/search/submission/?q=QUERY&subreddit=SUBREDDIT&size=25`
- Timed out on Nemotron query. Reddit API blocks most cloud IPs. pullpush.io is slower and less reliable.

## What NON-WORKING looks like
- Google: `/sorry/index?continue=...` (CAPTCHA block)
- Reddit: `whoa there, pardner!` block with anti-bot code
- DuckDuckGo lite: "Unfortunately, bots use DuckDuckGo too", duck CAPTCHA
- Reddit JSON API: returns HTML login page, not JSON

## What WORKED for Nemotron Ultra specifically
```
HN Algolia stories query -> 9 hits, 22pts top story
  -> extracted 2 user comments: "fast inference is the key strength",
     "not as smart as Qwen/DeepSeek but best US open model"
HN Algolia full thread (item 48398107) -> 2 comments, 0 replies
HN comments query -> 16 hits, including:
  - bcatanzaro (NVIDIA engineer): "open data, open recipe, open technique"
  - throwa356262: "bigger than Qwen for same intelligence, key strength is inference speed"
  - adrian_b: "much better than all earlier US open models, but not as good as best Chinese"
  - diggan: discussion about Llama naming requirements in license
HF model search -> 20 variants found, ~384 downloads max
```

## Key Signals for Future Sessions

### "Thin but honest" reporting pattern
When a model is too big for consumer hardware (550B MoE, needs 8xH100), real-user sentiment will be thin. Say:
- "Only X substantive user comments found (model is newly released / requires 8xH100)"
- "Press has Y articles; real users are Z comments on HN and HF downloads of W"
- Do NOT fabricate "community sentiment" from 2 comments

### Two release tiers pattern
NVIDIA releases have a consistent shape:
1. Day 0-2: Press blitz with benchmark claims, ZDNet/VentureBeat/PRWeb coverage
2. Day 3+: Early HN users who ran it report actual inference speeds and quality comparisons
Future sessions looking at new NVIDIA models should expect this pattern.

### When the model has TWO versions
Nemotron branded models are confusing, there's:
- `Llama-3.1-Nemotron-Ultra-253B-v1` (older, Llama-based dense 253B)
- `Nemotron-3-Ultra-550B-A55B-BF16` (new, Mamba-Transformer MoE hybrid)
Users may be discussing either. Check the context. The 550B is the one announced at Computex 2026.