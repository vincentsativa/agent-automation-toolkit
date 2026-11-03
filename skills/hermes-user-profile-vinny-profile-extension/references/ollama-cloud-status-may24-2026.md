# Ollama Cloud / Pro, Known Issues (as of May 24, 2026)

## Active GitHub Issues

### #15453, Ollama Cloud Pro: 95% failure rate (OPEN, since Apr 9, 2026)
**URL:** https://github.com/ollama/ollama/issues/15453  
**Reporter:** KUANKEI21 ($20/mo Pro subscriber, macOS)  
**Models tested:** glm-5.1:cloud, kimi-k2.5:cloud, qwen3.5:cloud, deepseek-v3.2:cloud  
**Result:** 1/20 requests succeeded (5%), both `/api/chat` and `/api/generate` return empty responses or timeouts  
**Status:** Still Open, no resolution after ~6 weeks

### #15419, Ollama Cloud: Frequent 503 errors (OPEN, since Apr 8, 2026)
**URL:** https://github.com/ollama/ollama/issues/15419  
**Status:** 7+ confirmations, still open

## Today's New Issues (May 24, 2026), LOCAL only, NOT cloud

| # | Title | Type | Platform |
|---|-------|------|----------|
| 16280 | 500 Internal Server Error loading MoE models | Local GPU | Ubuntu/Docker |
| 16279 | Tool calling not streaming on macOS MLX | Local MLX | macOS |
| 16278 | `ollama pull` "file does not exist" | Local manifest | macOS M4 |

**None of today's new issues are Ollama Cloud / Pro API problems.**

## No Fresh Cloud Outage Today

As of May 24, 2026, no community reports of a widespread Ollama Pro/Cloud outage today. The service appears functionally stable, though the underlying reliability issues from April (#15453, #15419) remain unresolved.

## Key Distinction

- **Local Ollama** (localhost:11434) = runs models on YOUR hardware, check with `curl -s http://localhost:11434/api/tags`
- **Ollama Cloud / Pro** (api.ollama.com) = hosted models, check via GitHub issues, community reports, status.ollama.com does not exist