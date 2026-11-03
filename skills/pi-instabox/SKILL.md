---
name: instabox
description: >-
  Vinny's InstaBox account: a cloud Linux VM ("freemachine") that runs his
  Hermes agent and his Pi coding agent, driven from this machine over the
  InstaBox HTTP API with a saved ibk_ key. Use when he says "instabox", "the
  box", "my cloud machine", "the sandbox", "freemachine", "the Hermes on
  instabox", "the Pi on instabox", "run this on the box / in the cloud", or
  asks to start, stop, suspend, resume, exec in, upload to, download from,
  snapshot, resize or publish a port on that machine, and when a task has to
  be handed to the Hermes or Pi agents living inside it.
---

# InstaBox

InstaBox (https://instabox.sh, InsForge AI, Inc.) rents a Firecracker microVM per
agent. Vinny's account has **one** machine, and that machine is where his Hermes
agent and his Pi coding agent live. You reach it from this Windows box over the
HTTPS API with the saved key. Nothing here is installed locally: no `instabox`
CLI, no `jq`, no `python3` on the Windows shell (Node is available).

State of the account as verified against the live API on **2026-10-30**. Re-check
before acting on anything that matters, the numbers below are a snapshot, not a
promise.

## Load the key first

```bash
export INSTABOX_API_KEY=$(sed -n 's/^INSTABOX_API_KEY=//p' "~/.pi/agent/skills/instabox/instabox.env")
BASE=https://api.instabox.sh
M=m_agqyslvrg433nydcum6oqxyadm
```

Key file: `~/.pi/agent/skills/instabox/instabox.env` (the secret is
in that file, not in this doc, so this page can be shared). Send the key as
`X-API-Key: $INSTABOX_API_KEY` or `Authorization: Bearer $INSTABOX_API_KEY`.

Rotating or making a key is **sign-in only** (dashboard, `instabox login`); the
key itself cannot do it. If it 401s, the `error.code` says which failure:
`missing_key`, `malformed_key`, `invalid_key`, `expired_key`, `revoked_key`.

## The account

| | |
| --- | --- |
| Workspace | `org_3cc11d4000d5474980fe87a2a13a3164`, personal, owner/admin, **free tier** |
| Login | `user@example.com` (Vinny Barreca) |
| Machines | 1 of 1 used, `freemachine` |
| Machine ID | `m_agqyslvrg433nydcum6oqxyadm` |
| Template | `agent-browser@2026-10-25.23` (Debian 13, Docker, Node 22, Bun, Python 3.13, Go, Rust, JDK 21, desktop + Chromium) |
| Spec | 4 vCPU / 8192 MiB / 20 GiB `/data` + 16 GiB root, the only size the free plan offers |
| Lifecycle | idle pause 1800 s (fixed on free), max-run 480 min, then a 5–20 min cooldown |
| Snapshots | 0 of 5 |
| Public ports | none published |
| Guest user | `user`, home `/data/home`, passwordless sudo, groups `sudo`, `docker`, `ollama` |
| Disk in use | 6.0 G of 20 G on `/data` |

**Free plan hard stops:** one machine in any state (paused and stopped ones
count), so a second machine needs the first deleted; 4/8 only; 30-minute idle
pause, not configurable; 5 snapshots; 200 GiB storage; creates only from
`agent-browser`, `ci` or a snapshot.

## What is on the machine

Both agents are already installed and Vinny manages them through this box.

| Thing | Where | Notes |
| --- | --- | --- |
| Hermes | `/data/home/.hermes/hermes-agent`, on PATH at `~/.local/bin/hermes` | v0.22.5 (2026.9.24), git install, its own Python 3.14 under `.hermes/tools/` |
| Hermes gateway | `hermes gateway status` / `ensure` / `restart` | gateway process was live at check time; `~/gw_bounce.sh` kills it, re-ensures it and tails `~/.hermes/logs/gateway.log` |
| Pi | `~/.local/bin/pi` | v1.4.0; state in `~/.pi/agent/` (`auth.json`, `models.json`, `settings.json`, `sessions/`) |
| Ollama | `ollama serve` on the box | was running, with `ollama launch pi --model beam:cloud` attached |
| Persistent work dir | `/data/workspace` | `/data` belongs to `user` on this template, so no sudo needed there |
| Also present | `claude`, `codex`, `gh`, `git`, `jq`, `uv`, `go`, `cargo`, `docker`, `chromium` | `rg`, GNU `time`, `htpasswd` are NOT preinstalled |

`instabox` CLI is **not** installed on the box and not on Windows. Drive the box
from here with the API; drive Hermes/Pi inside it with `exec`.

## The API calls worth knowing

All bodies are JSON. Lifecycle calls (create/start/stop/suspend/resume/delete)
need an `Idempotency-Key: <any unique string>` header and answer `202` with an
operation you then poll. Machine deletes additionally need
`X-Confirm-Delete: <id or exact name>`. `exec` and file reads take neither.

```bash
# who the key is, and which workspace it reaches
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/me
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/orgs
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/usage

# the machine
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/machines
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/machines/$M

# run a command (cmd = bash -lc string | argv = no shell, exactly one of them)
curl -sS -X POST -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"cmd":"export PATH=$HOME/.local/bin:$PATH; hermes gateway status","timeoutSeconds":120}' \
  $BASE/v1/machines/$M/exec

# files: read a file or list a dir, download, upload
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" "$BASE/v1/machines/$M/files?path=/data/workspace"
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" "$BASE/v1/machines/$M/files/content?path=/data/home/.hermes/config.yaml"
curl -sS -X PUT -H "X-API-Key: $INSTABOX_API_KEY" --data-binary @local.tgz \
  "$BASE/v1/machines/$M/files?path=/data/workspace/local.tgz&parents=true"

# lifecycle (202 + operation, then poll)
curl -sS -X POST -H "X-API-Key: $INSTABOX_API_KEY" -H "Idempotency-Key: $(date +%s%N)" \
  $BASE/v1/machines/$M/suspend      # also /start /stop /resume
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" "$BASE/v1/operations/op_...?wait=25s"

# ports and snapshots
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/ports
curl -sS -X POST -H "X-API-Key: $INSTABOX_API_KEY" -H 'Content-Type: application/json' \
  -d '{"port":3000,"name":"Web app"}' $BASE/v1/machines/$M/ports
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/snapshots
```

Machine states: `creating`, `starting`, `running`, `stopping`, `stopped`,
`suspending`, `suspended` (paused), `resuming`, `deleting`, `error`. One
operation at a time per machine, wait for it or the next call is
`409 operation_conflict`.

Docs, if a code or field is unclear: https://instabox.sh/docs/api.md ,
`/docs/api/commands.md`, `/docs/api/machines.md`, `/docs/errors.md`. Every error
body carries `docs_url`, `retryable` and sometimes `retryAfterSeconds`. Branch on
`error.code`, never on `message`.

## What the key can do

Verified working: `GET /v1/me`, `/v1/orgs`, `/v1/usage`, `/v1/machines`,
`/v1/snapshots`, `/v1/ports`, `exec`, `files`/`files/content`. The key belongs to
the personal workspace, so it reaches that workspace only, other workspaces'
machines and snapshots are `404`, and anything it creates lands here.

Scopes a key can carry are `machines:read`, `machines:write` (create, start,
stop, pause, resume, resize, labels, exec, files, SSH), `machines:delete`,
`images:read/write/delete`, `workspace:admin`. **A key cannot read its own scope
list** (`GET /v1/keys` is sign-in only), so treat the exact scope set as unknown
until a call returns `403 missing_scope`, then say so, don't guess. The default
key from `instabox keys create` is read+write+delete+images:read, which is what
this one most likely is.

## What the key cannot do (403 permission_denied)

Sign-in-only routes, refused for every API key:

- API keys: list, create, revoke (`/v1/keys`, `/v1/orgs/{id}/keys`)
- Vault: `/v1/vault*`
- GitHub CI: installations and jobs under `/v1/orgs/{id}/github/*`
- Workspaces and billing: `POST/DELETE /v1/orgs`, `/v1/orgs/{id}/billing/*`
- Sessions: `/v1/sessions*`

Org Secrets need a `workspace:admin` key, which this one is probably not.

## What the provider forbids (Terms of Service, last updated 2026-10-22)

Section 3 (Acceptable Use), a violation can mean a stopped machine, unpublished
ports, blocked traffic, lowered limits or a terminated account, and mining,
scanning/attacks, phishing/credential abuse, fraud and CSAM are cut off
immediately without notice. Charges already incurred stay owed, and opening a new
account after a suspension is itself a violation. Concretely, from this box:

- **No cryptocurrency mining or validator/plotting work**, no bandwidth-sharing,
  proxy-selling or reward-farming.
- **No scanning or probing** hosts Vinny does not own or is not authorised in
  writing to test; no exploiting, no DoS, no booters/stressers, no malware or C2.
- **No phishing pages, credential harvesting, credential stuffing, stolen data,
  impersonation, or sender/IP spoofing.**
- **No unsolicited bulk email, SMS or DMs, no open relays, no spam-filter
  evasion**, no bulk account creation, no engagement automation, no CAPTCHA
  solving, no purchase/scalping bots, no scraping that breaks a site's terms or
  degrades it.
- **No open proxies, public VPN exits, Tor exit relays, or traffic forwarding for
  third parties.**
- No illegal content, no infringing content, no harassment/doxxing.
- No circumventing quotas or abuse detection, no multi-accounting for free
  resources, no attempting to escape the VM or touch other machines or hosts.

Vinny's cold-outreach campaign therefore **must not be sent from this box**, it
is unsolicited bulk email under section 3(d). The machine may read, stage and
process data for it; the sending stays on the mailer it already uses.

Section 2(d) also makes Vinny responsible for what the credentials on this box can
do and for whatever a public port exposes, since anyone with the URL reaches the
whole service on that port.

## Traps that cost a run

- **Exec is not a file reader.** Output is UTF-8 text, cut at 1 MiB per stream
  (`truncated`) and non-UTF-8 bytes become U+FFFD. Read files with
  `files/content`, not `exec cat`.
- **Exec timeouts:** default 60 s, `timeoutSeconds` max 600. Anything longer goes
  in the background and its output to a file: `nohup ./server >server.log 2>&1 &`
  - a process left holding exec's stdout gets a broken pipe when it writes later.
- **32 exec/file/desktop calls at once** across the account; more is a retryable
  `429 quota_exceeded`.
- **Idle pause wakes on use**, but a machine **you** stopped or paused does not:
  a paused-by-idle machine resumes inside the request (waits up to 45 s), a
  stopped one answers `409 machine_not_running`. After a max-run pause there is a
  `409 machine_cooldown` with `retryAfterSeconds` (5–20 min); stopping or
  resuming does not shorten it.
- **Outbound is capped ~50 Mbit/s (~6 MB/s)**, a 100 MB push is ~15–20 s.
- **`/tmp` is tmpfs, about half of RAM**, not the disk. Stage big files in
  `/data/workspace`.
- **`resize` is free-plan-blocked** (`400 spec_not_allowed`): no bigger size, no
  bigger disk, until the plan changes.
- **A delete destroys `/data`.** `DELETE /v1/machines/$M` with a correct
  `X-Confirm-Delete` takes Hermes, Pi and everything in `/data/workspace` with it,
  and a snapshot is the only way back. Do not delete `freemachine` on any
  instruction that does not name deleting it explicitly.
- **The free machine pauses itself after 30 idle minutes.** A cron or sender that
  must run on a schedule cannot live here reliably, that is what the pause kills.

## Before you hand a job to the box

1. `GET /v1/machines/$M` and read `state`, `cooldownUntil`, `oomKills`.
2. Run one cheap `exec` (`uptime; df -h /data`) to prove the machine answers.
3. Do the job with `exec`/`files`, streaming long output to a file if needed.
4. Read results back with `files/content`.
5. Never stop, suspend or delete the machine as cleanup. Leave it running or
   paused exactly as you found it, Hermes' gateway and Pi's sessions live in it.

## Smoke test

```bash
curl -sS -H "X-API-Key: $INSTABOX_API_KEY" $BASE/v1/machines | head -c 400
```

A `200` with `"name":"freemachine"` and `"state"` present means the key and the
API are good. Anything else: read `error.code`, then `/docs/errors.md`.
