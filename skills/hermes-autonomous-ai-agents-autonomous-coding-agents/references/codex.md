# Codex CLI, Reference

[Codex](https://github.com/openai/codex) is OpenAI's autonomous coding agent CLI.

## Prerequisites

```bash
npm install -g @openai/codex
```

### Authentication

- Set `OPENAI_API_KEY` environment variable, OR
- Use Codex CLI OAuth credentials from the Codex CLI login flow
- For Hermes-managed auth: `hermes auth add opencodex` with `model.provider: openai-codex`
- Standalone credentials live under `~/.codex/auth.json`

**Must run inside a git repository**, Codex refuses to run outside one.

## One-Shot Tasks

```bash
# Basic execution
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)

# Scratch work (Codex needs a git repo)
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```bash
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project",
         background=true, pty=true)

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## CLI Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Review

Clone to a temp directory for safe review:

```bash
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW "
                 "&& cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```bash
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'",
         workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'",
         workdir="/tmp/issue-99", background=true, pty=true)

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```bash
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'",
         workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'",
         workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Codex-Specific Rules

1. **Always use `pty=true`**, Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required**, Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots**, `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building**, auto-approves changes within the sandbox
5. **Background for long tasks**, use `background=true` and monitor with `process` tool
6. **Parallel is fine**, run multiple Codex processes at once for batch work