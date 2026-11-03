# Claude Code, Reference

[Claude Code](https://code.claude.com/docs/en/cli-reference) is Anthropic's autonomous coding agent CLI. v2.x can read files, write code, run shell commands, spawn subagents, and manage git workflows autonomously.

## Prerequisites

```bash
# Install
npm install -g @anthropic-ai/claude-code

# Auth
claude                    # browser OAuth for Pro/Max
claude auth login --console  # API key billing
claude auth login --sso      # Enterprise SSO

# Check status
claude auth status
claude auth status --text  # human-readable

# Health check
claude doctor

# Version (must be v2.x+)
claude --version

# Update
claude update
```

## Print Mode (`-p`), Non-Interactive (PREFERRED)

Print mode runs a one-shot task, returns the result, and exits. **No PTY needed. No interactive prompts.**

```bash
terminal(command="claude -p 'Add error handling to all API calls in src/' "
         "--allowedTools 'Read,Edit' --max-turns 10",
         workdir="/path/to/project", timeout=120)
```

**When to use:** one-shot coding, CI/CD, structured extraction, piped input, any task not needing multi-turn conversation.

### Structured JSON Output

```bash
terminal(command="claude -p 'Analyze auth.py for security issues' "
         "--output-format json --max-turns 5", workdir="/project", timeout=120)
```

Returns JSON with fields: `type`, `subtype`, `result`, `session_id`, `num_turns`, `total_cost_usd`, `duration_ms`, `stop_reason`, `usage`, `modelUsage`.

### Streaming Output

```bash
terminal(command="claude -p 'Write a summary' --output-format stream-json "
         "--verbose --include-partial-messages", timeout=60)
```

### Piped Input

```bash
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### JSON Schema for Structured Extraction

```bash
terminal(command="claude -p 'List all functions in src/' --output-format json "
         '--json-schema \'{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}\' '
         "--max-turns 5", workdir="/project", timeout=90)
```

### Session Continuation

```bash
# Start and capture session ID
terminal(command="claude -p 'Start refactoring the database layer' "
         "--output-format json --max-turns 10 > /tmp/session.json",
         workdir="/project", timeout=180)

# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' "
         "--resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') "
         "--max-turns 5", workdir="/project", timeout=120)

# Resume most recent
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1",
         workdir="/project", timeout=30)
```

### Bare Mode for CI/Scripting

```bash
terminal(command="claude --bare -p 'Run all tests and report failures' "
         "--allowedTools 'Read,Bash' --max-turns 10",
         workdir="/project", timeout=180)
```

`--bare` skips hooks, plugins, MCP discovery, and CLAUDE.md loading. Fastest startup. Requires `ANTHROPIC_API_KEY`.

### Fallback Model for Overload

```bash
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```

## Interactive Mode (Multi-Turn via tmux)

**Requires tmux.** Raw `pty=true` alone is insufficient for orchestration.

```bash
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

### Dialog Handling (Critical)

Claude Code presents confirmation dialogs on first launch:

**Dialog 1: Workspace Trust**, default is "Yes, I trust this folder"
```bash
tmux send-keys -t <session> Enter
```

**Dialog 2: Bypass Permissions**, default is "No, exit" (WRONG). Must navigate down first:
```bash
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

**Robust pattern:**
```bash
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")                # Trust dialog
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")  # Permissions
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")        # Check progress
```

After first trust acceptance for a directory, trust dialog won't reappear. Permissions dialog recurs each time with `--dangerously-skip-permissions`.

## CLI Subcommands

| Subcommand | Purpose |
|------------|---------|
| `claude` | Start interactive REPL |
| `claude "query"` | Start REPL with initial prompt |
| `claude -p "query"` | Print mode (non-interactive) |
| `cat file \| claude -p "query"` | Pipe content as stdin context |
| `claude -c` | Continue most recent conversation in this directory |
| `claude -r "id"` | Resume specific session |
| `claude auth login` | Sign in (add `--console` or `--sso`) |
| `claude auth status` | Check login status |
| `claude mcp add <name> -- <cmd>` | Add MCP server |
| `claude mcp list` | List MCP servers |
| `claude mcp remove <name>` | Remove MCP server |
| `claude agents` | List configured agents |
| `claude doctor` | Health checks |
| `claude update` / `claude upgrade` | Update to latest version |
| `claude remote-control` | Start server for claude.ai/mobile control |
| `claude install [target]` | Install native build |
| `claude setup-token` | Set up long-lived auth token |
| `claude plugin` / `claude plugins` | Manage plugins |
| `claude auto-mode` | Inspect auto mode classifier |

## Complete CLI Flags

### Session & Environment
| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode |
| `-c, --continue` | Resume most recent conversation |
| `-r, --resume <id>` | Resume specific session |
| `--fork-session` | Create new session ID on resume |
| `--session-id <uuid>` | Use specific UUID for session |
| `--no-session-persistence` | Don't save session to disk (print mode only) |
| `--add-dir <paths>` | Grant access to additional working directories |
| `-w, --worktree [name]` | Run in isolated git worktree at `.claude/worktrees/<name>` |
| `--tmux` | Create tmux session for worktree (requires `--worktree`) |
| `--ide` | Auto-connect to IDE on startup |
| `--chrome` / `--no-chrome` | Enable/disable Chrome browser integration |
| `--from-pr [number]` | Resume session linked to a GitHub PR |
| `--file <specs>` | File resources to download at startup |

### Model & Performance
| Flag | Effect |
|------|--------|
| `--model <alias>` | Model: `sonnet`, `opus`, `haiku`, or full name |
| `--effort <level>` | Reasoning: `low`, `medium`, `high`, `max`, `auto` |
| `--max-turns <n>` | Limit agentic loops (print mode only) |
| `--max-budget-usd <n>` | Cap spend (print mode only; min ~$0.05) |
| `--fallback-model <model>` | Auto-fallback when overloaded (print mode only) |
| `--betas <betas>` | Beta headers for API requests |

### Permission & Safety
| Flag | Effect |
|------|--------|
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--allow-dangerously-skip-permissions` | Enable bypass as option (not default) |
| `--permission-mode <mode>` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools <tools>` | Whitelist specific tools |
| `--disallowedTools <tools>` | Blacklist specific tools |
| `--tools <tools>` | Override built-in tool set |

### Output & Input Format
| Flag | Effect |
|------|--------|
| `--output-format <fmt>` | `text`, `json`, `stream-json` |
| `--input-format <fmt>` | `text` or `stream-json` |
| `--json-schema <schema>` | Force structured JSON output |
| `--verbose` | Full turn-by-turn output |
| `--include-partial-messages` | Include partial message chunks |
| `--replay-user-messages` | Re-emit user messages on stdout |

### System Prompt & Context
| Flag | Effect |
|------|--------|
| `--append-system-prompt <text>` | Add to default system prompt |
| `--append-system-prompt-file <path>` | Add file contents to default prompt |
| `--system-prompt <text>` | Replace entire system prompt |
| `--system-prompt-file <path>` | Replace prompt with file contents |
| `--bare` | Skip hooks, plugins, MCP, OAuth (fastest) |
| `--agents '<json>'` | Define custom subagents dynamically |
| `--mcp-config <path>` | Load MCP servers from JSON file |
| `--strict-mcp-config` | Only use MCP from `--mcp-config` |
| `--settings <file-or-json>` | Load additional settings |
| `--setting-sources <sources>` | Comma-separated sources: `user`, `project`, `local` |
| `--plugin-dir <paths>` | Load plugins from directories |
| `--disable-slash-commands` | Disable all slash commands |

### Debugging & Agent Teams
| Flag | Effect |
|------|--------|
| `-d, --debug [filter]` | Enable debug logging |
| `--debug-file <path>` | Write debug logs to file |
| `--teammate-mode <mode>` | Agent team display: `auto`, `in-process`, `tmux` |
| `--brief` | Enable agent-to-user communication |

## PR Reviews

```bash
# Quick review (print mode, piped diff)
terminal(command="cd /path/to/repo && git diff main...feature-branch "
         "| claude -p 'Review this diff for bugs, security issues, and style problems' --max-turns 1", timeout=60)

# Deep review with worktree
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
# Handle dialogs, then:
terminal(command="sleep 5 && tmux send-keys -t review Enter")
terminal(command="sleep 2 && tmux send-keys -t review "
         "'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")

# PR review from number
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10",
         workdir="/path/to/repo", timeout=120)

# Built-in worktree + tmux
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```

## Parallel Tasks with tmux

```bash
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && "
         "tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug\" "
         "--allowedTools \"Read,Edit\" --max-turns 10' Enter")
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && "
         "tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests\" "
         "--allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; "
         "tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## Settings & Configuration

### Settings Hierarchy (highest to lowest)
1. CLI flags, override everything
2. Local project: `.claude/settings.local.json` (personal, gitignored)
3. Project: `.claude/settings.json` (shared, git-tracked)
4. User: `~/.claude/settings.json` (global)

### Permissions in Settings
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### Memory Files (CLAUDE.md) Hierarchy
1. Global: `~/.claude/CLAUDE.md`, all projects
2. Project: `./CLAUDE.md`, project-specific (git-tracked)
3. Local: `.claude/CLAUDE.local.md`, personal overrides (gitignored)

Use `#` prefix in interactive mode: `# Always use 2-space indentation`.

## Interactive Slash Commands

| Command | Purpose |
|---------|---------|
| `/help` | Show all commands |
| `/compact [focus]` | Compress context to save tokens |
| `/clear` | Wipe conversation history |
| `/context` | Visualize context usage |
| `/cost` | View token usage with breakdowns |
| `/resume` | Switch to or resume a session |
| `/rewind` | Revert to a previous checkpoint |
| `/btw <question>` | Ask a side question (low cost) |
| `/status` | Show version, connectivity, session info |
| `/todos` | List tracked action items |
| `/exit` or `Ctrl+D` | End session |
| `/review` | Request code review |
| `/security-review` | Perform security analysis |
| `/plan [description]` | Enter Plan mode |
| `/loop [interval]` | Schedule recurring tasks |
| `/batch` | Auto-create worktrees for parallel changes |
| `/model [model]` | Switch models mid-session |
| `/effort [level]` | Set reasoning effort |
| `/init` | Create CLAUDE.md for project memory |
| `/memory` | Open CLAUDE.md for editing |
| `/config` | Open interactive settings |
| `/permissions` | View/update tool permissions |
| `/agents` | Manage subagents |
| `/mcp` | Manage MCP servers |
| `/add-dir` | Add additional working directories |
| `/usage` | Show plan limits and rate limit status |
| `/voice` | Enable push-to-talk voice mode |
| `/release-notes` | Version release notes picker |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Cancel input or generation |
| `Ctrl+D` | Exit session |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+B` | Background a running task |
| `Ctrl+V` | Paste image into conversation |
| `Ctrl+O` | Transcript mode |
| `Esc Esc` | Rewind conversation or code state |
| `Shift+Tab` | Cycle permission modes |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle thinking mode |
| `Alt+O` | Toggle Fast Mode |

**Input prefixes:** `!` = bash directly, `@` = reference files, `#` = add to CLAUDE.md, `/` = slash commands.

**"ultrathink"** keyword triggers maximum reasoning effort on a single turn.

## Hooks, Automation on Events

Configure in `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "dangerous guard cmd"}]
    }]
  }
}
```

### Hook Types
| Hook | When it fires |
|------|--------------|
| `UserPromptSubmit` | Before Claude processes a user prompt |
| `PreToolUse` | Before tool execution (exit 2 = block) |
| `PostToolUse` | After a tool finishes |
| `Notification` | On permission requests or input waits |
| `Stop` | When Claude finishes a response |
| `SubagentStop` | When a subagent completes |
| `PreCompact` | Before context memory is cleared |
| `SessionStart` | When a session begins |

## Custom Subagents

Define in `.claude/agents/` (project), `~/.claude/agents/` (personal), or via `--agents` CLI flag:

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities
- Authentication/authorization flaws
- Secrets in code
```

Invoke via: `@security-reviewer review the auth module`

## MCP Integration

```bash
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres "
         "--connection-string postgresql://localhost/mydb", timeout=30)
```

MCP scopes: `-s user` (global, `~/.claude.json`), `-s local` (project personal, gitignored), `-s project` (team-shared, git-tracked).

## Monitoring

```bash
# Periodic capture
terminal(command="tmux capture-pane -t dev -p -S -10")
```

Indicators: `❯` = waiting for input, `●` = actively using tools, `ctrl+o to expand` = truncated output.

### Context Window Health
- **< 70%**, Normal
- **70-85%**, Precision drops, consider `/compact`
- **> 85%**, Hallucination risk spikes

## Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key auth |
| `CLAUDE_CODE_EFFORT_LEVEL` | Default effort level |
| `MAX_THINKING_TOKENS` | Cap thinking tokens |
| `MAX_MCP_OUTPUT_TOKENS` | Cap MCP output |
| `CLAUDE_CODE_NO_FLICKER=1` | Enable alt-screen rendering |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | Strip credentials from sub-processes |

## Pitfalls

1. **Interactive mode REQUIRES tmux**, raw PTY is insufficient
2. **`--dangerously-skip-permissions` defaults to "No, exit"**, send Down then Enter
3. **`--max-budget-usd` minimum ~$0.05**
4. **`--max-turns` is print-mode only**, ignored in interactive sessions
5. **Trust dialog only once per directory**, then cached
6. **Background tmux sessions persist**, always `tmux kill-session -t <name>` when done
7. **Slash commands only work in interactive mode**
8. **`--bare` skips OAuth**, requires `ANTHROPIC_API_KEY`
9. **Context degradation is real**, proactively `/compact` above 70%