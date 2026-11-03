---
name: autonomous-coding-agents
description: "Consolidated guide to all external autonomous coding CLI agents, Codex, Claude Code, OpenCode, with decision table, shared patterns, and labeled subsections."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, Claude-Code, OpenCode, Code-Review, Refactoring, PTY, Automation]
    related_skills: [hermes-agent, autonomous-ai-agents]
---

# Autonomous Coding Agents

Delegate coding tasks to external autonomous coding agent CLIs via the Hermes terminal. Three supported agents are documented here.

## Decision Table, Which Agent for Which Task

| Task | Recommended Agent | Why |
|------|-------------------|-----|
| **One-shot feature/bug fix** | Codex (with `--yolo` or `--full-auto`) or Claude Code (`-p`) | Fastest execution. Codex is sandboxed by default; Claude Code has structured JSON output. |
| **PR review (quick diff)** | Claude Code (`-p` mode) or Codex (`exec`) | Both handle `git diff` piped reviews well. |
| **PR review (deep, multi-file)** | Claude Code (worktree + interactive) or Codex (temp clone) | Worktree isolation + full repo context for thorough review. |
| **Multi-turn iterative work** | Claude Code (interactive via tmux) or OpenCode (TUI) | Both support natural back-and-forth with slash commands. |
| **CI/CD / scripting** | Claude Code (`--bare -p`) or Codex (`exec`) | Fast startup, no interactive prompts. Claude Code has `--output-format json` for machine parsing. |
| **Batch parallel fixes** | Codex (lightweight) or Claude Code (print mode) | Multiple independent `exec`/`-p` calls in separate worktrees. Codex is slightly lighter per instance. |
| **Provider-agnostic / open-source** | OpenCode | Supports multiple providers (OpenRouter, Anthropic, OpenAI). Fully open-source. |
| **Cost tracking / session resume** | Claude Code or OpenCode | Both have built-in stats and session management. |
| **What's cheapest?** | Codex with `--yolo` or OpenCode (BYO API key) | OpenCode with OpenRouter's cheapest model; Codex `--yolo` skips sandbox overhead. |
| **What's most capable?** | Claude Code | Most feature-rich: worktrees, MCP, hooks, subagents, plugin system. |
| **Local inference setup** | Claude Code + Ollama | Run Claude Code's agent loop with local GGUF models via Ollama backend. No API costs, full offline capability. |

### Quick Selection Guide

- **Claude Code** for most tasks, richest feature set, structured output, mature ecosystem
- **Codex** when you want OpenAI-native or minimal overhead one-shots
- **OpenCode** when you need provider flexibility or an open-source toolchain

## Shared Patterns

These patterns apply to all three agents. Agent-specific commands and flags are documented in the reference files.

### PTY Requirement

All three agents are interactive terminal apps. **Always use `pty=true`** when starting a session that requires user input.

| Agent | Interactive mode needs pty | One-shot mode needs pty |
|-------|--------------------------|------------------------|
| Codex | `codex exec` `--full-auto`, pty=true | `codex exec`, also needs pty=true |
| Claude Code | Interactive, needs tmux orchestration | `-p` / `--print`, NO pty needed |
| OpenCode | TUI session, pty=true | `opencode run`, NO pty needed |

For Claude Code's interactive mode, you must use **tmux** (not raw PTY) because it provides `capture-pane` for monitoring and `send-keys` for input. See the claude-code reference for detailed tmux orchestration.

### Background Process Management

All three agents can run as Hermes-managed background processes:

```yaml
# Common pattern, agent-specific command differs
terminal(command="<agent-start-cmd>", workdir="~/project",
         background=true, pty=<bool>)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input to interactive session
process(action="submit", session_id="<id>", data="continue, yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

### Session Monitoring

| Check | How |
|-------|-----|
| **List running sessions** | `process(action="list")` |
| **Check status** | `process(action="poll", session_id="<id>")` |
| **View output** | `process(action="log", session_id="<id>")` |
| **Wait for completion** | `process(action="wait", session_id="<id>", timeout=300)` |
| **Send input** | `process(action="submit", session_id="<id>", data="...")` |
| **Send Ctrl+C** | `process(action="write", session_id="<id>", data="\x03")` |
| **Kill process** | `process(action="kill", session_id="<id>")` |

### Git Worktree Isolation for Parallel Tasks

For running multiple agent tasks in parallel without file conflicts, use **git worktrees**:

```bash
# Create isolated worktrees from base branch
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main")

# Launch agent in each worktree
terminal(command="<agent> <task>", workdir="/tmp/issue-78",
         background=true, pty=<bool>)
terminal(command="<agent> <task>", workdir="/tmp/issue-99",
         background=true, pty=<bool>)

# Monitor all
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78")
```

### PR Review Approaches

| Approach | When to Use |
|----------|-------------|
| **Piped diff review** | Quick review of a diff, fastest, least context |
| **Temp clone review** | Full repo context without affecting working copy |
| **Worktree review** | Full repo context, no clone needed, safe isolation |
| **Built-in PR command** | Some agents (OpenCode, Claude Code) have native PR review commands |

Common patterns across agents:

```bash
# Piped diff (all agents support this)
terminal(command="git diff origin/main...feature | <agent> 'Review this diff for bugs'")

# Temp clone review
terminal(command="REVIEW=$(mktemp -d) && git clone <repo> $REVIEW && cd $REVIEW && "
                "<agent> 'Review this PR vs main'")

# Worktree review (Claude Code has built-in -w flag)
terminal(command="git worktree add /tmp/pr-review <branch> && "
        "cd /tmp/pr-review && <agent> 'Review changes vs main'")
```

## Agent Reference Files

Each agent has a dedicated reference file with full CLI flags, auth setup, session management, and agent-specific patterns:

- [Codex CLI](references/codex.md), OpenAI Codex CLI: install, auth, one-shot, background, flags, PR review, parallel work
- [Claude Code CLI](references/claude-code.md), Anthropic Claude Code: install, auth, print mode, interactive tmux, flags, settings, hooks, MCP, subagents, worktrees
- [OpenCode CLI](references/opencode.md), Provider-agnostic open-source coding agent: install, auth, one-shot, TUI sessions, flags, PR review, session management

## Rules (All Agents)

1. **Always use `pty=true` for interactive sessions**, all three agents hang without a PTY
2. **`opencode run` and `claude -p` do NOT need pty**, use plain terminal for these
3. **Claude Code interactive mode REQUIRES tmux**, raw PTY is insufficient for multi-turn orchestration
4. **Git repo required for Codex**, Codex refuses to run outside a git directory. Use `mktemp -d && git init` for scratch work
5. **Background for long tasks**, use `background=true` and monitor with `process` tool
6. **Don't interfere**, monitor with `poll`/`log`, be patient with long-running tasks
7. **Isolate parallel agents**, use separate workdirs/worktrees to prevent file conflicts
8. **Clean up**, kill background processes and remove worktrees/tmux sessions when done
9. **Report concrete outcomes**, summarize files changed, test results, and remaining risks
10. **Use `--max-turns` or equivalent**, prevent runaway loops and unbounded costs