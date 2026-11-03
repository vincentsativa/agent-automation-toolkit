# WSL Hermes as Windows Desktop Agent

## Two Patterns

There are two distinct ways to access your WSL Hermes agent from the Windows desktop. Do not conflate them.

### Pattern 1: File Access via /mnt/c/

Run Hermes inside WSL and access the Windows desktop filesystem directly via `/mnt/c/Users/<username>/Desktop/` (or OneDrive/Desktop). This gives you:

- Full Linux environment (bash, proper tools, path semantics)
- All accumulated Hermes memory, skills, and session history
- Direct access to Windows desktop files without bouncing between environments

### Pattern 2: Remote Backend via `hermes serve` (Desktop App Connection)

The Hermes Desktop app (native Windows GUI) can connect to a Hermes backend running in WSL. This is a **documented, supported feature** — not a hack or workaround.

The Desktop App is a front-end that drives the same agent runtime whether that runtime is local, in WSL, or on a remote VPS. The connection uses `hermes serve` as the backend process and the Desktop App's "Remote Gateway" settings.

#### Setup

**On the WSL side (the backend):**

```bash
# 1. Set auth credentials in ~/.hermes/.env
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=<your-username>
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<your-password>
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. Find your WSL IP
hostname -I

# 3. Start the backend bound to all interfaces
hermes serve --host 0.0.0.0 --port 9119
```

Keep `hermes serve` running (tmux, systemd, or process manager). If it stops, the Desktop App loses connection.

**On the Windows side (the Desktop App):**

Settings → Gateway → Remote Gateway, enter `http://<WSL-IP>:9119` plus the credentials, and connect.

#### Auth Options

| Provider | When to use | Setup |
|----------|------------|-------|
| Username/password | Local / trusted network (Tailscale, LAN) | Set `HERMES_DASHBOARD_BASIC_AUTH_*` in `.env` |
| OAuth (Nous Portal) | Public internet / VPS | `hermes dashboard register` then "Sign in with Nous Research" |

#### Important

- The `hermes serve` backend is a separate process from the gateway. The gateway (Telegram/Discord/etc.) runs independently.
- Binding to `0.0.0.0` automatically engages the auth gate. Without auth, the backend refuses non-loopback connections.
- The `HERMES_DASHBOARD_BASIC_AUTH_SECRET` keeps sessions alive across restarts. Without it, a random key is generated per boot and you're logged out every time.
- On Windows 11 22H2+ with mirrored networking mode (`networkingMode=mirrored` in `.wslconfig`), `localhost` works in both directions — you can use `http://localhost:9119` instead of the WSL IP.

## Why This Works Better Than Windows Native

| Factor | WSL Hermes | Windows Native Hermes |
|--------|-----------|----------------------|
| Terminal backend | bash (full Linux toolchain) | cmd.exe (no ls/grep/sed/awk) |
| Work history | All accumulated sessions, memory, skills | Starts from zero per install |
| Path semantics | Linux-native (`/mnt/c/...`) | Windows paths, UNC issues |
| Tool availability | Everything | Missing pyright, browser deps, etc. |

## Path Mapping

| Windows Path | WSL Path |
|-------------|----------|
| `C:\Users\<username>\Desktop\` | `/mnt/c/Users/<username>/Desktop/` |
| `C:\Users\<username>\OneDrive\Desktop\` | `/mnt/c/Users/<username>/OneDrive/Desktop/` |
| `C:\Users\<username>\Documents\` | `/mnt/c/Users/<username>/Documents/` |
| `C:\Users\<username>\Downloads\` | `/mnt/c/Users/<username>/Downloads/` |

## Portability

The entire `~/.hermes/` directory is portable to a new machine:

```bash
# Backup
tar czf hermes-backup.tar.gz ~/.hermes/

# Restore on new machine
tar xzf hermes-backup.tar.gz -C ~/
```

This carries over:
- config.yaml (all settings)
- .env (API keys — optional, include at your discretion)
- skills/ (all learned procedures)
- memories/ (persistent facts)
- sessions/ (conversation history)
- profiles/ (if using multiple profiles)
- auth.json (OAuth tokens)

Only system-level dependencies need re-setup on the new machine (Python, pip, hermes package, system deps).

## Hybrid Strategy

- **Cloud-first**: Ollama Cloud for daily inference (cheap, always available)
- **Local fallback**: M4 Pro/Max Mac runs local models (DeepSeek Flash, Gemma 4) when cloud is down
- **Portable agent**: Same `~/.hermes/` moves between machines — agent is the same regardless of host
- **Resilience**: Cloud failure → local. Hardware failure → new machine + backup. Neither scenario stops work.
