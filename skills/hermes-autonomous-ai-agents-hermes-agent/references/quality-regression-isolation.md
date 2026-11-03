# Quality Regression Isolation Playbook

When user reports "model X got worse" or "every model sucks," isolate before touching config.

## Step 1: Check gateway logs for errors

```bash
grep -i -E "error|fail|timeout|429|503|truncat" ~/.hermes/logs/gateway.log | tail -30
```

If logs are clean but quality is bad, proceed to direct API test.

## Step 2: Direct API isolation test

```bash
# Verify API is alive and model list is sane
curl -s -w "\nHTTP %{http_code}" --max-time 15 https://ollama.com/v1/models \
  -H "Authorization: Bearer $API_KEY"

# Test a completion (simple math, verifies basic reasoning intact)
curl -s -w "\nHTTP %{http_code}" --max-time 45 https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-v4-pro", "messages": [{"role": "user", "content": "What is 17 * 23? Just the number."}], "max_tokens": 200}'
```

**Interpretation:**
- HTTP 200 + correct answer (391) → model is fine, problem is in Hermes config or context
- HTTP error → provider is down or auth invalid
- HTTP 200 + wrong answer → model is quantized/broken upstream

## Step 3: If model is fine, check Hermes config

Read `~/.hermes/config.yaml`. Key suspects:
- `model.default`, which model is actually running?
- `agent.reasoning_effort`, "low" on reasoning models like DeepSeek v4 produces weak output
- `streaming.enabled`, off makes responses feel dead/stilted
- `display.show_reasoning`, false hides the model's reasoning chain (may make answers look shallow)

## DeepSeek v4 quirk: reasoning field

DeepSeek v4 returns a `reasoning` field separate from `content` in its completion response. With low `max_tokens`, the model may only output reasoning and never reach the `content` field. Hermes may also strip reasoning from display if `show_reasoning: false`. This makes the model appear dumber than it actually is, the reasoning happened, you just can't see it.

Example response with reasoning:
```json
{"choices":[{"message":{"content":"391","reasoning":"We need to compute 17 * 23 = 391."}}]}
```
