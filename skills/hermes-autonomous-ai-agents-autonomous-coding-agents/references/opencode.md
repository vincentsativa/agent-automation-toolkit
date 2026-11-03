# OpenCode, Reference

[OpenCode](https://opencode.ai) is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## Prerequisites

```bash
# Install
npm i -g opencode-ai@latest
# OR
brew install anomalyco/tap/opencode

# Auth
opencode auth login          # Interactive login
opencode auth list           # Verify configured providers
```

**Auth:** Configure at least one provider (OpenRouter, Anthropic, OpenAI) via `opencode auth login` or set env vars like `OPENROUTER_API_KEY`.

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. Verify:

```bash
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

If needed, pin an explicit binary path:

```bash
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

## One-Shot Tasks (`opencode run`)

Use `opencode run` for bounded, non-interactive tasks. **No PTY needed.**

```bash
# Basic
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")

# With context files
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example",
         workdir="~/project")

# Show model thinking
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")

# Force specific model
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4",
         workdir="~/project")
```

## Interactive Sessions (TUI)

For iterative work requiring multiple exchanges, start the TUI in background:

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly, Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit`, it is not a valid OpenCode command and opens an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")`.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

```bash
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)       # Continue last
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue last session |
| `--session <id>` / `-s` | Continue specific session |
| `--agent <name>` | Choose agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output |
| `--file <path>` / `-f` | Attach file(s) to message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to running opencode server |

## PR Review

```bash
# Built-in PR command
terminal(command="opencode pr 42", workdir="~/project", pty=true)

# Or review in temp clone for isolation
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW "
         "&& cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, "
         "test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\\n' ' ')",
         pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```bash
terminal(command="opencode run 'Fix issue #101 and commit'",
         workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'",
         workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Session & Cost Management

```bash
# List past sessions
terminal(command="opencode session list")

# Check stats
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## Procedure for Hermes Agents

1. Verify tool readiness: `opencode --version`, `opencode auth list`
2. For bounded tasks, use `opencode run '...'` (no pty needed)
3. For iterative tasks, start `opencode` with `background=true, pty=true`
4. Monitor long tasks with `process(action="poll"|"log")`
5. If OpenCode asks for input, respond via `process(action="submit", ...)`
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`
7. Summarize file changes, test results, and next steps back to user

## Verification

```bash
terminal(command="opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'")
```

Success: output includes `OPENCODE_SMOKE_OK`, exits without errors.

## OpenCode-Specific Pitfalls

- Interactive TUI requires `pty=true`. `opencode run` does NOT need pty.
- `/exit` is NOT valid, use Ctrl+C
- PATH mismatch can select wrong binary
- Enter may need to be pressed twice in TUI
- Avoid sharing workdir across parallel sessions