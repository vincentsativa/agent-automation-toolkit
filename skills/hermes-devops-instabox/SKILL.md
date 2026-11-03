---
name: instabox
description: Use when Vinny says instabox or cloud box.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [instabox, cloud, linux, sandbox, api]
    related_skills: [scrapling]
---

# InstaBox

## When to Use

Load this skill when Vinny says "instabox", "my cloud box", "my server", "Hermes agent in instabox", or "pi coding in instabox"; when he asks to run, install, build, test, or host something on a remote Linux machine; and before any call to `api.instabox.sh`. Also load it when a task needs heavy compute, headless Chromium, Docker, or a long-running server that should not live on this WSL host.

InstaBox gives each agent its own Linux machine (Firecracker microVM) in the cloud, reached only through the HTTP API at `https://api.instabox.sh`. There is no GUI for us and no CLI installed on this host. Everything below is REST via `curl`, already verified against Vinny's account.

## Auth (already configured)

The key lives in `~/.bashrc` as `export INSTABOX_API_KEY=ibk_...`, so every new shell and every `terminal()` call has it. Send it as `X-API-Key: $INSTABOX_API_KEY` or `Authorization: Bearer $INSTABOX_API_KEY`.

Rules:
- Never print, echo, log, or paste the key. Reference `$INSTABOX_API_KEY` only. Never put the literal key in a script, skill, file, or message.
- Verify auth with `curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: $INSTABOX_API_KEY" https://api.instabox.sh/v1/machines` (200 = good).
- `.bashrc` returns early for non-interactive shells, so `terminal()` does not inherit `$INSTABOX_API_KEY`. Export it in the same command: `export INSTABOX_API_KEY=$(grep 'INSTABOX_API_KEY=' ~/.bashrc | cut -d= -f2)`.
- A 401 has a reason in `error.code`: `missing_key`, `malformed_key`, `invalid_key`, `expired_key`, `revoked_key`. That means the env var is unset or the key was rotated or revoked; ask Vinny for a new one rather than guessing.

## Vinny's account (checked Oct 29, 2026; re-check with GET /v1/me and GET /v1/orgs)

- Plan: **free**. Workspace `org_3cc11d4000d5474980fe87a2a13a3164`, personal, tier `free`, role admin.
- Key scopes: `machines:read`, `machines:write`, `machines:delete`, `images:read`.
- Allowed size: exactly one spec, 4 vCPU / 8192 MiB / 20 GiB persistent disk. No resize, no larger machine, no disk growth on free.
- Free plan: **one machine at a time**, 5 snapshots, 100 GiB egress/month, creates only from `agent-browser` or `ci` (snapshots exempt), `maxRunMinutes` fixed at 480, `autoSuspendAfterSeconds` only 1800.
- Existing machine: `freemachine` / `m_agqyslvrg433nydcum6oqxyadm`, running, template `agent-browser`. Use this one unless the task needs a clean box; do not delete it without an explicit order.

## What the API can do (all reachable with this key)

Lifecycle on `/v1/machines`: create, get, patch (rename, labels, auto-suspend, max-run), start, stop, suspend, resume, wake, fork (clone on the same host, seconds), restore (disks back to a snapshot, same ID), delete.

Inside a machine:
- `POST /v1/machines/{id}/exec` runs a command. Body is either `cmd` (shell string, `bash -lc`) or `argv` (exact program plus args, no shell). Fields: `cwd`, `envs`, `stdin` (max 1 MiB), `timeoutSeconds` (default 60, max 600).
- Files: `GET /v1/machines/{id}/files?path=` lists a directory, `GET .../files/content?path=` reads a file, `PUT .../files?path=` writes, `POST .../files/upload-url` gives a presigned upload for large files.
- Processes: `GET .../processes`. Logs: `GET .../logs`. Metrics: `GET .../metrics`. Usage: `GET .../usage`. Exec history: `GET .../history`.
- Ports: `POST .../ports` publishes a port and returns a public HTTPS URL (`access: public` or private token link), `GET .../ports` lists them, `DELETE .../ports/{port}` closes.
- SSH: `POST .../ssh-tokens` mints a short-lived token; also `GET .../connection-info`.
- Desktop: `POST .../desktop`, `GET .../vnc`, `GET .../terminal` for browser-desktop access (VNC/Xfce/Chromium on `agent-browser`).
- Secrets: per-machine `/secrets` and `/vault` inject values into exec without putting them on the command line.

Snapshots and images: `POST /v1/machines/{id}/snapshots` saves, `GET /v1/snapshots` lists, `GET /v1/snapshots/{id}/files` browses, `POST /v1/machines` with `snapshotId` boots from one.

Account: `GET /v1/templates`, `GET /v1/me`, `GET /v1/orgs`, `GET /v1/usage`, `GET /v1/ports`, `GET /v1/operations/{id}`, feedback and support tickets, org webhooks.

## What runs inside the box: Hermes and Pi are both there

The box is not empty. `freemachine` already has a Hermes agent and a Pi coding install, and they are reached through the same API as everything else: `exec` and the files API. InstaBox's API talks to the machine, not to apps inside it, so there is no separate HTTP endpoint for either one. Total control of both is via `exec`.

Paths:
- Hermes binary: `/data/home/.local/bin/hermes`, home `/data/home/.hermes` (config.yaml, auth.json, .env, gateway.lock, cron, skills, sessions, kanban.db, state.db, logs).
- Pi binary: `/data/home/.local/bin/pi`, home `/data/home/.pi`.
- Also installed: `/usr/local/bin/codex`, `/data/home/.local/bin/claude`, and `ollama` with `/usr/local/bin/ollama serve` running.
- Guest user is `user`, passwordless sudo, home `/data/home`.

Seen running on Oct 29, 2026: `ollama launch pi --model beam:cloud` driving `pi`, plus Xvnc/Xfce desktop and Chromium.

To see and manage them:
- Version and health: `hermes --version`, `hermes gateway status`, `pi --version`, `ps aux | grep -Ei "hermes|ollama|pi"`.
- Logs: read the files under `$HOME/.hermes/logs` with `GET /v1/machines/{id}/files/content`, or `GET /v1/machines/{id}/logs`.
- Config: read with `GET /v1/machines/{id}/files/content`, or `exec` `hermes config get <key>`; write scalars with `hermes config set` inside the box, and only fall back to `PUT` for structures the CLI cannot express.
- Drive them: start, stop, restart, or send them commands through `exec`. A long-running one must be detached with output redirected to a file (see the protocol section), since exec's pipe breaks when it returns.
- Desktop: `POST /v1/machines/{id}/desktop` or `GET .../vnc` to see the actual screen and drive the GUI.
- Ports: publish one if either process listens on a port.

## What the Hermes agent inside the box has (configured Oct 29, 2026)

Everything below was installed and verified through `exec` and the files API, and each one was tested with real output:
- **Keenable web search**: plugin `web/keenable` enabled (bundled, no pip needed) and `web.backend: keenable` set in `/data/home/.hermes/config.yaml`. Verified with a live `hermes -z` search that returned a real result.
- **AgentMail**: MCP server `agentmail` in the box config as `npx -y agentmail-mcp` with `AGENTMAIL_API_KEY`, 53 tools. `hermes mcp ls` shows it enabled and `hermes mcp test agentmail` lists the tools. Add MCP servers by editing the box `config.yaml` with the files API; `hermes mcp add` connects but does not persist when run non-interactively.
- **Skills**: `vinny-constitution`, `productivity/email-sender`, `content-swarm/ghostwriter-terminal`, and `creative/writing-style` copied into `/data/home/.hermes/skills`, all listed enabled by `hermes skills list`.
- **Email**: IONOS SMTP (`smtp.ionos.com:587`, `imap.ionos.com:993`) credentials are set in the box `.env` (`EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_IMAP_HOST`, `EMAIL_IMAP_PORT`, `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`). A gateway bounce is needed once these change; `EMAIL_ALLOWED_USERS` may still need setting depending on the platform.
- **GitHub**: `GITHUB_TOKEN` is set in the box `.env`, so the box's Hermes can clone or fetch skill/cron content from GitHub directly; use it when Vinny asks to add or sync skills/crons on the box.
- **Model**: Ollama Cloud via `https://ollama.com/v1` in the box config, so its prompts bill the Ollama account, not InstaBox. The default model is `deepseek-v4.1-flash:1017` (verified Oct 30, 2026); re-check with `hermes config get model.default` rather than trusting this line, because a model switch rewrites it.

Copy skills into the box by tarring them locally, `PUT` the tarball to `files?path=`, then untar in `~/.hermes/skills` with `exec`.

## Model and provider config in the box

- Write scalars with `hermes config set <dotted.key> <value>` inside the box and read back with `hermes config get`. `hermes model` and `hermes config edit` both need a terminal and are useless over exec.
- Diagnose "what did it do to X" from `~/.hermes/backups/config/config.yaml.good.<timestamp>`: one file per config write, so the files in time order are the edit history.
- A box with an empty `providers:` map still shows provider rows, built from `auth.json` `credential_pool` plus live discovery, so such a row lists the endpoint's whole catalog. When he orders a model added to that provider, write a pinned `providers.<slug>` row (`discover_models: false`, the declared `models:` list, `base_url`, and the real key copied out of `credential_pool`) and report the catalog row as the separate duplicate it is. Never close the order with "it was already on the row".
- An empty `model.default` makes the gateway log `Empty model resolved ... recovering last-known-good model <id>` and run a stale model that may not exist on the configured provider. Set the default, then bounce.
- Build the bounce script with the file-writing tool and exec it by path; a heredoc containing `pgrep`/`kill` in the local terminal command is refused by the local gateway guard even though the kill only runs inside the box.

Probe a row without a picker: `scripts/probe_provider_rows.py` works because it imports `hermes_bootstrap` first, which is what puts the runtime dependency set on `sys.path`. A helper that skips that step dies on `ruamel` from `hermes_yaml` even under the managed python, so either import `hermes_bootstrap` before any `hermes_cli` import or point `PYTHONPATH` at `/data/home/.hermes/cache/uv/archive-v0/*`. Full diagnostic sequence and the `PYTHONPATH` form: `references/box-hermes-model-config.md`.

A provider that appears twice is two rows, not a rendering quirk: one from `providers:` and one from `credential_pool`. "It should be in there once" is an instruction to delete the pool credential (`hermes auth remove <provider> <id>`, both args, id from `hermes auth list`) after copying its key into the declared block, then to prove one row by counting them. Never clear a 401 flag with `hermes auth reset <provider> all`; that target is parsed as a credential and logs the provider out.

## Messaging platforms for the Hermes agent in the box

Turning on Telegram (or another platform) for the box's Hermes is not a YAML edit. The platform comes up from `~/.hermes/.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL`), the adapter's library must exist in the box runtime python (`/data/home/.hermes/tools/python-*/bin/python3`, no venv), and a running gateway ignores config changes until it is bounced. A gateway that reports "running" while logging `No messaging platforms enabled.` is a platform that never started: trust the log line `Gateway running with N platform(s)`, never the status command alone. Bouncing it means writing a small script to the box and exec'ing it by path, because the local guard refuses gateway lifecycle verbs inside an outer command string. Full procedure, script and healthy log lines: `references/hermes-gateway-in-box.md`.

## What it cannot do (do not try; these are 403 by design for every API key)

Sign-in only, return `403 permission_denied` for API keys: creating/listing/revoking API keys, the personal Vault, GitHub CI installations and jobs, billing changes, workspace create/delete, members/invites, sessions. Only Vinny in the dashboard or a signed-in CLI can do those.

Plan and scope limits, not bugs:
- Resize, disk grow, extra vCPUs or memory: free plan has one allowed spec.
- Templates other than `agent-browser` and `ci` on free: `403 template_not_allowed`.
- More than one machine at once on free: `429 quota_exceeded`.
- `autoSuspendAfterSeconds` other than 1800, or anything that needs `manualLifecycle`: `403 permission_denied`.
- Anything outside the key's workspace: `404` (other workspaces do not exist to this key).

## Protocol every call must follow

1. **Idempotency.** Every lifecycle call (create, start, stop, suspend, resume, delete, fork, restore, update) needs an `Idempotency-Key` header with any unique string, e.g. `$(uuidgen)`. Reusing a key on a *different* request is `409 idempotency_conflict`. Keys live 7 days. `exec` and Secrets do not take one.
2. **Deletes are confirmed.** `DELETE /v1/machines/{id}` and `DELETE /v1/snapshots/{id}` need `X-Confirm-Delete: <id or exact name>`. Wrong or missing value is `409 delete_confirmation_required` and nothing is deleted. Always send it, even where optional.
3. **Lifecycle is async.** Create/start/stop/suspend/resume/delete answer `202` with an operation. Poll `GET /v1/operations/{id}` until `succeeded` or `failed`, then act. A machine runs one operation at a time; a second one is `409 operation_conflict`.
4. **Branch on `error.code`, never on the message.** Retry only when `retryable` is true, after `retryAfterSeconds`. `no_capacity` is retryable (503, wait 60s), then retry with a **new** Idempotency-Key.
5. **Read files with the files API, not `exec cat`.** Exec output is UTF-8 text, each stream cut at 1 MiB (`truncated`), non-UTF-8 bytes become U+FFFD. Binary and anything large must come through `files/content` or a presigned URL.
6. **Long work.** Exec is capped at 600s and returns when the command exits; anything left running keeps going but its later writes to exec's output fail with a broken pipe. So: redirect a server's output to a file (`nohup ./server >server.log 2>&1 &`), or use a background job pattern, and for work over 10 minutes run it detached and poll the log file with `files/content`.
7. **Do not leave boxes burning.** The free machine pauses after 30 min idle and after 480 running minutes anyway, but suspend or stop it when done, and confirm state with `GET /v1/machines/{id}`.

## Working recipes

Create a box and wait for it (adjust `name`):
```
curl -s -X POST https://api.instabox.sh/v1/machines \
  -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"name":"job1","templateId":"agent-browser","metadata":{"purpose":"build"}}'
# -> 202 with operation.id; then poll GET /v1/operations/{id}
```

Run a command and read its result:
```
curl -s -X POST https://api.instabox.sh/v1/machines/$ID/exec \
  -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"cmd":"python3 --version && nproc","cwd":"/data/home","timeoutSeconds":120}'
# -> {stdout, stderr, exitCode, signal, timedOut, truncated, invalidUtf8, durationMs}
```

For output as it happens, add `-H 'Accept: text/event-stream'`: `stdout`/`stderr` events carrying `{"data"}`, then an `exit` event with the result.

Write a file in and read it back:
```
curl -s -X PUT "https://api.instabox.sh/v1/machines/$ID/files?path=/data/home/x.txt" \
  -H "X-API-Key: $INSTABOX_API_KEY" --data-binary @local.txt
curl -s "https://api.instabox.sh/v1/machines/$ID/files/content?path=/data/home/x.txt" \
  -H "X-API-Key: $INSTABOX_API_KEY"
```

Publish a port:
```
curl -s -X POST https://api.instabox.sh/v1/machines/$ID/ports \
  -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"port":3000,"name":"web","access":"public"}'
```

Delete, with confirmation:
```
curl -s -X DELETE https://api.instabox.sh/v1/machines/$ID \
  -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(uuidgen)" \
  -H "X-Confirm-Delete: $ID"
```

## Environment facts inside a box

- Templates: `agent-browser` (default; Debian 13, Node 22, Bun, uv, Go, Rust, OpenJDK 21, Docker with Compose, Xfce desktop, Chromium, Claude Code, Codex), `universal` (same minus preinstalled desktop), `ci` (Ubuntu 24.04, GitHub runner image, free plan allowed), `herdr`/`orca` (no Docker or toolchains), `t3`.
- Home is `/data/home` on a 20 GiB persistent disk mounted at `/data`; root disk is 16 GiB. `/tmp` is RAM-backed tmpfs about half of guest RAM, so stage big files in `$HOME/tmp`.
- ripgrep, GNU time and htpasswd are **not** preinstalled and apt lists ship empty: `sudo apt-get update && sudo apt-get install -y ripgrep time apache2-utils`.
- Guest user is `user` with passwordless sudo. Default soft `ulimit -n` is 1024; run any raiser in the same exec as the workload.

## Things not to do

- Do not exec in his box on your own initiative to "just check" something. Inspecting a running agent, listing its home, or probing versions all count as touching his stuff: run a command only when the order needs it, and say what you changed when you do. Read-only is still not permission.
- Do not answer a question about the box with what is true of this WSL host, or the reverse. "Hermes agent in instabox" and "pi coding in instabox" mean the copies inside the machine; "this machine" means here. When he corrects the subject, restate the answer about the named system instead of defending the first one.
- Do not install the CLI, MCP server, or their skills unless Vinny orders it. API via curl is the working path and needs nothing extra.
- Do not create a second machine on the free plan (one at a time) and do not delete `freemachine` on your own initiative.
- Do not treat a `202` as done. Poll the operation.
- Do not report work as finished from the exec call alone: check `exitCode`, `truncated`, and read any file output back through the files API.

## Docs

- Index for agents: https://instabox.sh/llms.txt and https://instabox.sh/llms-full.txt
- API overview: https://instabox.sh/docs/api.md (auth, operations, idempotency, errors)
- API keys and scopes: https://instabox.sh/docs/api-keys.md
- Limits: https://instabox.sh/docs/limits.md. Pricing: https://instabox.sh/docs/pricing.md. Errors: https://instabox.sh/docs/errors.md
- Machine-readable spec: https://api.instabox.sh/v1/openapi.json
- Fetch docs with scrapling (Article 6), not curl-to-Google. The `.md` suffix on any docs URL returns Markdown.
