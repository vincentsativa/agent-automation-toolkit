# Model-Spec Verification, Verified Mirror Sources (Aug 3, 2026)

Session-tested fallback chain for model-launch stories when the primary source
404s or bot-blocks. Captured so future reports don't re-discover the working
mirrors or risk fabricating specs.

## Primary-source failures observed this day
| Source | Failure |
|--------|---------|
| Reuters | "Please enable JS and disable any ad blocker" (bot-block) |
| SCMP | 404 "Page Not Found" on guessed article slug |
| WSJ | paywall timeout (do not attempt) |

## Working mirrors for Chinese model launches (fetch cleanly, carry full wire copy)
- Channel News Asia, channelnewsasia.com/east-asia/...
- ET EnterpriseAI, enterpriseai.economictimes.indiatimes.com/news/industry/...
- Daily Sabah, dailysabah.com/business/economy/...
- pressnewsagency.org
- devdiscourse.com/article/technology/...

## Confirmed figures, DeepSeek V4-Flash & Alibaba Qwen3.8-Max (Aug 3, 2026)
DeepSeek V4-Flash:
- $0.14 per million input tokens, $0.28 per million output tokens
- avg 3 cents/test (Artificial Analysis) vs 86c Kimi K3, $1.86 GPT-5.6 Sol, $3.15 Claude Fable 5
- Intelligence Index 50/100 (ties Gemini 3.6 Flash; 1 behind Meta Muse Spark 1.1 and GLM-5.2)
- V4-Pro (stronger) in preparation, no date

Alibaba Qwen3.8-Max:
- 2.4T total params; mixture-of-experts activating ~95B at a time
- 1M-token context; text+image+video
- Highest-ranking Chinese text model on Arena.AI; #2 globally on vision leaderboard
- vs Moonshot Kimi K3 (2.8T params, 1M context)

## Method
1. `web_search` model name + "pricing" or "parameters" or key claim.
2. `web_extract` top mirrors; prefer wire-copy carriers above.
3. Extract exact per-token prices, params, MoE active params, benchmark scores.
4. Never fabricate; if no verified number, keep summary qualitative.
