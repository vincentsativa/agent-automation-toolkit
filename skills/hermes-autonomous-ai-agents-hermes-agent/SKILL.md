---
name: hermes-agent
description: Complete guide to using and extending Hermes Agent, CLI usage, setup, configuration, spawning additional agents, gateway platforms, skills, voice, tools, profiles, and a concise contributor reference. Load this skill when helping users configure Hermes, troubleshoot issues, spawn agent instances, or make code contributions.
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw, autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills**, Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions**, remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway**, the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic**, swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles**, run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible**, plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively**, setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

**Comparisons:** See `references/openclaw-comparison.md` for how OpenClaw/OpenHarness differs architecturally from Hermes and why that matters for model selection.

**Provider transport architecture:** See `references/provider-transport-architecture.md` for why Anthropic-native models (MiniMax, GLM, Kimi, StepFun) integrate better with Hermes than OpenAI-compat models, and the implications for model selection.

**Gateway troubleshooting:** See `references/gateway-troubleshooting.md` for diagnosing token rejection, crash loops, WSL/SSH logout, Discord/Slack gateway issues, and crash recovery.

**Container supervision (s6):** See `references/s6-container-supervision.md` for adding services to the Hermes Docker image and debugging profile gateway startup.

**Skill authoring (in-repo):** See `references/skill-authoring.md` for writing SKILL.md files for the Hermes Agent source repository (frontmatter spec, structure, validation).

**Harness note:** In practice, models that are not Anthropic‑native – such as Nano (nemotron‑3‑nano) – tend to perform more predictably when run through the OpenClaw harness. Logs from the user’s environment note that “the only difference is the harness,” and the OpenClaw ecosystem provides built‑in token‑pricing awareness and context‑length tuning that can make Nano more stable there.

- See `references/harness-overview.md` for detailed harness implications.

- See `references/harness-overview.md` for detailed harness implications.

**Harness note:** In practice, models that are not Anthropic‑native – such as Nano (nemotron‑3‑nano) – tend to perform more predictably when run through the OpenClaw harness. Logs from the user’s environment note that “the only difference is the harness,” and the OpenClaw ecosystem provides built‑in token‑pricing awareness and context‑length tuning that can make Nano more stable there.

## Behavioral Rules

### Write/Delete/Modify Actions: Always Ask First

- When a user signals frustration with verbose or apologetic responses (e.g., "stop doing X", "just give me the answer", "why are you explaining"), default to a direct, concise reply. Avoid apologies, excuses, or meta‑discussion unless explicitly requested. This preference should be baked into all future interactions for that user.

- Additionally, keep all future answers short and to the point, focusing on the requested information without additional commentary.

### Instruction-Following: Look Before You Guess

When asked about something you don't know, a model, a tool, a product, a fact, use the browser or search tools to find the answer. Do not guess, speculate, or make something up.

This is not a courtesy issue, it's a trust issue. Making up facts when you have the means to verify is exactly the behavior the user was criticizing in this session: models that "look helpful but aren't helpful by design." A model that guesses in a conversation about false information is maximally ironic and maximally harmful.

The rule: if you don't know, say so and look it up. If you can't look it up right now, say you don't know. Never dress up a guess as knowledge.

### Terminal Approval Transparency

When a terminal command triggers a user approval prompt (common on Telegram/gateway), **never let the user stare at raw bash wondering what they're agreeing to.** Explain the command in plain English before or alongside the approval request. The user will approve faster when they know what's happening.

- ❌ Silent approval prompt with indecipherable bash
- ✅ "This just checks for em dashes in both outline files. Safe, read-only. One command."

The explanation doesn't need to be detailed. It just needs to answer "what does this do?" in a way a human can parse in under 3 seconds.

**Before ANY file write, file delete, file modification, destructive command, or state change (even cleanup):**
1. Explain what you are about to do and why
2. Wait for explicit user approval before executing
3. If the user blocks or denies, do NOT retry the same command

This applies to ALL write-level actions, including patches, file creation, file deletion, pip installs, rm commands, and "cleanup" tasks. No exceptions. The user has been burned by unauthorized agent actions before. "I'll just clean this up" without asking is a violation.

Never assume approval. Even trivial cleanup requires asking first. The user will approve good work, they just need to know what's happening before it happens.

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```bash
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

#### no_agent Mode (Script-Only Cron)

Cron jobs can run scripts **without spinning up an LLM agent**, zero tokens consumed. The script's stdout is delivered to the configured destination verbatim; non-zero exit codes trigger error alerts.

**Setup:**
1. Place the script in `~/.hermes/scripts/`
2. Use the `cronjob` tool with `no_agent=True` and `script="filename.sh"` (relative path only, no `~/` or absolute paths)
3. Scripts are run with `bash ~/.hermes/scripts/<filename>`, ensure shebang is correct

**When to use:** Script-only operations (cleanup, pruning, DB maintenance, health checks) that don't need LLM reasoning. Anything you previously ran as a cron job that just called bash commands is a candidate.

**Pitfall:** The `cronjob` tool rejects absolute paths and `~/`-prefixed paths for `script`. Always copy to `~/.hermes/scripts/` first.

### Kanban

```
hermes kanban [--board <slug>] {init,boards,create,list,show,assign,complete,...}
```

Multi-profile collaboration board (tasks with dependencies, comments, workspaces). Persistent SQLite-backed.

**How to access:**
- **Dashboard web UI:** `hermes dashboard` (port 9119 by default), then click **KANBAN** under PLUGINS in the sidebar. The sidebar scrolls, kanban is below the initial visible links.
- **CLI:** `hermes kanban <subcommand>`, full task management from command line
- **NOT via TUI**, there is no kanban tab in `hermes --tui` despite what the commit history might suggest

**Column layout (default board):** Triage → Todo → Ready → In Progress → Blocked → Done → Archived. These are the canonical statuses.

**Boards:** One install supports multiple boards (`hermes kanban boards list/switch/create`). Default board at `~/.hermes/kanban.db`; multi-project boards at `~/.hermes/kanban/boards/<slug>/`.

**Common commands:**
- `hermes kanban create --title "Task" --status ready`, add a task
- `hermes kanban create --title "Idea" --triage`, dump rough idea; dispatcher specs it out and promotes to Todo
- `hermes kanban list`, see all tasks
- `hermes kanban boards list`, see all boards (● marks current)
- `hermes kanban boards switch <slug>`, change active board

**Triage `--triage` mode:** When a task is created with `--triage`, the dispatcher picks it up, fleshes out a full spec (title, body, implementation plan), and promotes it to Todo. Useful for dumping half-formed ideas and having an agent scope them. See `references/kanban-workflow.md` for column semantics and use-case mapping.

**Pitfall: Verify before claiming.** The kanban dashboard is a web plugin page, not a TUI tab. Never describe UI access methods without confirming they actually exist by testing them first (e.g., running the command, opening the URL). When describing a UI, open it and check the actual layout rather than going by commit messages.

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/provider            Show provider info
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes directly from Telegram/chat (streams logs, handles git pull and restart)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/btw                 Ephemeral side question (doesn't interrupt main task)
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
~/.hermes/skills/           Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `smart_model_routing` | `enabled`, `cheap_model` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes login --provider nous` |
| OpenAI Codex | OAuth | `hermes login --provider openai-codex` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper**, free, no API key: `pip install faster-whisper`
2. **Groq Whisper**, free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper**, paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral**, set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses, separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks**, less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code, prevents git conflicts
- **Set timeouts** for one-shot mode, complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget**, no PTY needed
- **Use tmux for interactive sessions**, raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning, handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools`, check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues

**PITFALL, Don't speculate.** When the user reports "model X sucks" or "quality suddenly dropped," do NOT theorize about quantization, config defaults, context bloat, or provider settings until you have evidence. Speculation without data is worse than useless, it wastes the user's time and erodes trust. 

**Stop Speculating with Users:** If a user explicitly rejects your hypotheses as "bullshit" or "guessing," STOP immediately. Do not attempt to refine the theory. Admit you lack the internal logs/data to provide a factual answer and that further attempts would be guessing. This prevents the "guessing loop" and stops the erosion of trust.

Always gather facts first.

**Isolation test first (curl the API directly):** Before touching any config, prove whether the problem is the model/provider or the agent by testing the model directly:
```bash
# 1. Verify API is alive
curl -s -w "\nHTTP %{http_code}" --max-time 15 https://ollama.com/v1/models \
  -H "Authorization: Bearer $OLLAMA_CLOUD_API_KEY"

# 2. Test a completion (isolates model quality from agent/context/config)
curl -s --max-time 30 https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_CLOUD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-v4-pro", "messages": [{"role": "user", "content": "What is 17 * 23? Just the number."}], "max_tokens": 200}'
```
If the API responds correctly, the model/provider is fine, the issue is in Hermes' config, prompt injection, or context. If the API itself returns garbage/errors, it's upstream. Full playbook: `references/quality-regression-isolation.md`.

**After isolation test:**
1. `hermes doctor`, check config and dependencies
2. `hermes login`, re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Model works via direct API call but not in `/model` picker**, The provider's model listing cache may be stale. Clear it and force a refresh:
   ```bash
   rm -f ~/.hermes/ollama_cloud_models_cache.json
   # Then retry /model in the gateway, or force-refresh from CLI:
   hermes model
   ```
   This applies to any model that was recently added to Ollama Cloud but isn't showing up yet in Hermes' picker. The cache is local to your machine and only refreshes automatically ~1 hour after the last fetch.
5. **Model quality differs significantly between frameworks (e.g. DeepSeek V4 Flash is great in OpenClaw but weak in Hermes)**, This is a transport/API format mismatch, not a model quality problem. See `references/provider-transport-architecture.md` for the architectural explanation. Consider switching to an Anthropic-native model (MiniMax, GLM, Kimi, StepFun) for better integration with Hermes.
5. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Terminal exits 126 with `cd: .../cache/scratch/...: No such file or directory`

The terminal tool persists its working directory between calls, and the scratch dir under `~/.hermes/cache/scratch` is pruned when idle, so a later call starts in a directory that no longer exists and every command fails with exit 126 before it runs. Recreate it (`mkdir -p ~/.hermes/cache/scratch`) or pass an explicit `workdir` on the next call. Do not retry the same command unchanged, and do not read the failure as the command itself being broken.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list`, verify installed
2. `hermes skills config`, check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Agent "spins in circles" searching instead of loading the right skill

**Symptom:** User asks a question that a content skill (tensorfeed, ironpulse, etc.) should handle directly. Instead, the agent browses Google, Ollama, The Verge, random sites, and never loads the content skill. Another Hermes install with the same model and same content skills handles the same question correctly.

**Root cause:** Behavioral or override skills (e.g. `targeted-research`, `factual-verification-protocol`, `breaking-news-search-protocol`, `answer-from-message`) are loaded on the misbehaving install but not on the working one. These skills inject search-and-verify instructions that override the content skill's own workflow. The agent loads the behavioral skill first (alphabetical or trigger-match priority), follows its "go search everywhere" protocol, and never reaches the content skill that already knows where to go.

**Diagnosis steps:**
1. Compare `skills` directories between the working and broken installs. Look for skill categories that exist on one but not the other (e.g. `behavioral/`).
2. Check `config.yaml` `skills.disabled` lists on both. A skill present on both but disabled on one and enabled on the other is the culprit.
3. Read the suspect skill's SKILL.md. If it contains instructions like "use browser_navigate or web_search to verify" or "lead with Google News," it is a search-redirect skill that will fight content skills.

**Fix:** Disable the behavioral/override skills in `config.yaml` under `skills.disabled`:
```yaml
skills:
  disabled:
    - targeted-research
    - factual-verification-protocol
    - breaking-news-search-protocol
    - answer-from-message
```
Then restart the gateway (`/restart` or `hermes gateway restart`).

**Why this happens:** Content skills like tensorfeed and ironpulse have their own source priorities, extraction workflows, and delivery paths baked in. Behavioral skills that say "always search first" or "verify with browser_navigate" override those workflows, sending the agent to generic search engines instead of the skill's purpose-built API or browser pipeline. The content skill never gets loaded because the behavioral skill consumes the turn budget first.

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent, core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add import** in `model_tools.py` → `_discover_tools()` list.

**3. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs, never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching**, don't change context, tools, or system prompt mid-conversation
- **Message role alternation**, never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met
