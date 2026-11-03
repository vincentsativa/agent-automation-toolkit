# Ollama Local vs Ollama Pro Cloud — Critical Distinction

## The Two Products

| | **Local Ollama** | **Ollama Pro / Cloud** |
|---|---|---|
| What it is | Self-hosted LLM server running on YOUR machine | Cloud API service (api.ollama.com) |
| Endpoint | `http://localhost:11434` | `https://api.ollama.com` |
| Models | `qwen2.5:0.5b`, `llama3.1:8b`, etc. | `:cloud` variants — `qwen3.5:cloud`, `glm-5.1:cloud`, etc. |
| Auth | None (local) | Requires API key |
| Status page | None | None (no public status page) |

## Vinny's Setup

Vinny uses **Ollama Pro cloud** — NOT local Ollama.

- He calls `https://api.ollama.com` directly from his code
- He does NOT run a local Ollama server for production work
- Local Ollama may be installed but is not the primary inference layer

## The Failure Pattern (May 24, 2026)

**What happened:** When Vinny asked if Ollama was having issues, I checked `localhost:11434` (local Ollama) — which was fine. He wanted Ollama Pro cloud status. I wasted his time and enraged him by checking the wrong thing.

**Why it happened:** I assumed "Ollama" meant the local install because that was the context I was in (hermes-agent runs on a machine with local Ollama). I did not ask or verify.

**The rule:** When Vinny says "Ollama" with no qualifier, he means the **cloud service**. Local Ollama status is irrelevant to his workflow.

## How to Check Ollama Pro Cloud Status

Ollama Pro has **no public status page**. The only signals are:

1. **GitHub issues** — search `site:github.com/ollama/ollama` for "cloud" or "503" issues
   - Current known issues (May 2026):
     - #15453 — "Ollama Cloud Pro: 95% failure rate across all cloud models" (Open since Apr 9, 2026)
     - #15419 — "Frequent 503 errors making cloud models unreliable" (7+ confirmations, Open since Apr 8, 2026)
2. **Test the API directly:**
   ```bash
   curl -s --max-time 10 "https://api.ollama.com/api/chat" \
     -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_KEY" \
     -d '{"model":"qwen3.5:cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
   ```
   - 401 = endpoint alive (needs auth)
   - 503 = service error
   - timeout/empty = degraded
3. **Reddit/r/ollama** — search for "Ollama Cloud" posts about failures

## Model Naming Convention

Cloud models have the `:cloud` suffix. When Vinny mentions a model without `:cloud` and it's not in your local tags list, assume it's a cloud model he uses via Ollama Pro.

## Version Independence — CRITICAL (June 2026)

**Ollama OSS (open-source GitHub project) and Ollama Cloud have completely independent versioning.** A version number from one has no relation to the other.

| | **OSS Ollama (GitHub)** | **Ollama Cloud** |
|---|---|---|
| Latest prerelease | Check `api.github.com/repos/ollama/ollama/releases?per_page=100` | **No public endpoint** — version is internal/private |
| Latest stable | Same GitHub API | `api.ollama.com/api/version` returns placeholder `"0.0.0"` |
| What to query | GitHub API v3, paginate by `?page=N` | Direct API probes (see Ollama Cloud Status doc) |

**The failure (June 2, 2026):** Vinny asked "what's the latest Ollama pre-release version." I called the GitHub API with default pagination, got `v0.20.1` as the first prerelease hit, and claimed that was the answer. Vinny had `v0.30.0-rc31` running on Ollama Cloud — an internal version that never appears in the OSS repo at all. Two lessons:

1. **Ollama Cloud versions are private** — you cannot look them up. If Vinny reports a cloud version, that IS the answer; there's nothing to verify against.
2. **When querying any paginated API, one request is not enough.** GitHub returns 30 items per page by default. The `v0.20.1` was on page 1 but it wasn't the complete picture. Always paginate or use `?per_page=100` to get a representative window.

## Quick Discrimination Test

- **Local Ollama question:** "is my local server running?" → check `localhost:11434/api/tags`
- **Ollama Pro question:** "is the cloud service down?" → check GitHub issues + api.ollama.com probe
- **Version question (OSS):** GitHub API with pagination, multiple pages
- **Version question (Cloud):** **Don't look it up — there's no public source.** Vinny's installed version IS the truth.
- **When in doubt:** Ask "do you mean local or cloud?" — one question prevents a massive waste of time.