# Dedicated Cron Runner Architecture

A secondary Hermes instance on a separate machine that runs only scheduled jobs, freeing the primary agent (and its laptop) from cron noise.

## When To Use

- Your primary Hermes runs on a laptop you want to carry around
- You have 5+ cron jobs that fire daily — they wake the primary agent, burn context, and drain battery
- You want a machine that stays on 24/7 in a corner, never interrupted
- You want clean separation: primary = interactive work, secondary = scheduled output

## Architecture

```
Primary Agent (laptop)          Secondary Agent (cron box)
  - Interactive sessions          - No interactive sessions
  - Manual queries                - Cron jobs only
  - Development work              - Delivers to Telegram
  - Goes to coffee shop           - Stays plugged in
```

## Setup Flow

### 1. Clone the Backup

The secondary machine needs a GitHub PAT with **`Contents: Read`** (fine-grained) or **`repo`** scope (classic) to clone the backup repo:

```bash
git clone https://github.com/vincentsativa/wsl-hermes-backup.git ~/.hermes-restore
cp -r ~/.hermes-restore/skills/* ~/.hermes/skills/
cp ~/.hermes-restore/cron/jobs.json ~/.hermes/cron/
cp -r ~/.hermes-restore/cron/output/* ~/.hermes/cron/output/
cp ~/.hermes-restore/memories/MEMORY.md ~/.hermes/memories/
cp ~/.hermes-restore/memories/USER.md ~/.hermes/memories/
cp -r ~/.hermes-restore/kanban/* ~/.hermes/kanban/
cp ~/.hermes-restore/config/config.yaml ~/.hermes/   # structure only, needs API keys
```

### 2. Configure Telegram

The clone needs its own Telegram bot token. Without it, every job with `deliver: "telegram"` logs: `delivery: platform 'telegram' not configured/enabled`. This is harmless but noisy.

Set the bot token in `~/.hermes/.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Handle Provider Drift

Jobs created on the original machine may reference a different provider (e.g. `custom`). The secondary machine's global provider is different (e.g. `ollama-cloud`). Hermes has a safety feature (issue #44585) that **skips unpinned jobs** — jobs without an explicit `provider`/`model` pinned at creation — rather than silently running them on a different provider and potentially burning money.

**Jobs that will run fine:** Those with explicit provider+model pins (e.g. `provider=ollama-com model=glm-5.2`).

**Jobs that will skip:** Unpinned jobs (provider and model are both `null`). These log:
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created
```

**Fix:** Pin the unpinned jobs to the secondary machine's provider:
```bash
cronjob action=update job_id=<id> provider=ollama-cloud model=<model>
```

Or set the secondary machine's global provider to match the original. Pinning is cleaner — each job declares what it needs.

### 4. Unpause Jobs

If the original machine had jobs paused, they stay paused on the clone. Resume selectively:
```bash
cronjob action=resume job_id=<id>
```

### 5. Verify

Check that jobs are running and delivering:
```bash
cronjob action=list
```

Look for `last_status: "ok"` and no `last_delivery_error`.

## Multi-Agent Deployment

A single Linux cron box can run multiple Hermes agent instances. The primary agent (interactive, creative, strategic) runs on the laptop. A second agent instance (e.g. "Bill") runs on the cron box with the same skills, memory, and workflows, handling the automated pipeline in parallel.

**Benefits:**
- Force multiplication — same brain, separate iron, parallel execution
- One handles creative/strategic work, the other runs the automated pipeline
- The cron box agent never sleeps, never gets interrupted, just cranks through jobs
- Both agents share the same skill library and memory (synced via backup)

**Setup:**
- Install a second Hermes instance on the cron box (same install method as primary)
- Clone skills and memory from the primary (see Setup Flow above)
- Configure a separate Telegram bot token for the cron box agent
- The cron box agent runs headless — no interactive sessions, no dashboard browsing

## Cross-OS Setup as Coaching Curriculum

Every OS you set up Hermes on (Windows, WSL, Linux) builds repetition that compounds into teachable expertise:

- **Windows:** Native install, WSL quirks, path translation, tool compatibility issues
- **WSL:** Translation layer overhead, filesystem bridging, network quirks
- **Linux:** Clean execution, no translation layer, best performance

The bugs you squash, the configs you dial in, the OS quirks you learn to dance around — those become hours of future coaching content you can deliver without having to figure it out on camera. By the time you're ready to coach, you've done the dance so many times you could teach it in your sleep.

The machine is the product. The process is the curriculum. You get paid twice — once in infrastructure, once in expertise.

- **Don't run interactive sessions on the cron box.** It's a headless appliance. Every interactive session is context that could have gone to a cron job. If you need to debug something, SSH in, fix it, and leave.
- **Provider drift is a feature, not a bug.** The safety check (#44585) prevents the clone from silently burning money on a different provider. Pin jobs explicitly rather than fighting the safety.
- **Telegram token is per-instance.** The clone needs its own bot. You can't share a bot token between two Hermes instances — they'll fight over updates.
- **Backup the cron box too.** Once it's running, add it to the weekly backup rotation. Its cron output and any job modifications are valuable state.
- **The clone's config.yaml has placeholder API keys.** The backup skill strips live keys. You must inject fresh keys after cloning. The config structure (model names, provider settings, tool configs) is preserved.
