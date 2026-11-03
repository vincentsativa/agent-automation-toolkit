---
name: hermes-hardware-deployment
description: Hardware options for running Hermes Agent — dedicated appliances (Autonomous AI Intern 2), single-board computers (Raspberry Pi 5/500), mini PCs, and x86 boards. Covers specs, pricing, tradeoffs, and decision criteria for choosing a host machine.
version: 1.0.0
author: Hermes Agent
tags: [hermes, hardware, deployment, raspberry-pi, autonomous-ai-intern, sbc, mini-pc]
---

# Hermes Hardware Deployment

When a user asks about hardware to run Hermes on, the most common options are:

## Autonomous AI Intern 2 ($249)

A dedicated Hermes appliance from autonomous.ai. Preloaded with Hermes (or OpenClaw) out of the box.

- **Board:** Orange Pi 4 Pro in a 4.7" cube
- **CPU:** 8-core: 2× Cortex-A76 + 6× Cortex-A55 @ 2.0 GHz
- **RAM:** 6 GB LPDDR5
- **Storage:** 64 GB eMMC + up to 256 GB expansion
- **Voice:** Dual mic (3m pickup), 5W speaker
- **Connectivity:** Wi-Fi 6, Bluetooth 5.4
- **Power:** USB-C (5V/5A)
- **Dashboard:** Built-in web monitor with logs, analytics, CLI
- **Editions:** OpenClaw, Hermes, Developer (choose at purchase)
- **Warranty:** 30-day return, 1-year warranty

**Best for:** Dedicated Hermes appliance, voice interaction, zero-setup, plug-and-play.

## Raspberry Pi 500 Desktop Kit ($400)

Pi 5 built into a keyboard, sold as a complete desktop kit with official monitor and mouse.

- **CPU:** 4× Cortex-A76 @ 2.4 GHz
- **RAM:** Up to 16 GB LPDDR4X
- **Storage:** microSD (no onboard NVMe — requires hat for PCIe Gen 2 x1)
- **Connectivity:** Wi-Fi 5, Bluetooth 5.0
- **Power:** USB-C (5V/5A, 27W recommended)
- **Includes:** Keyboard-PC, official mouse, official monitor
- **Software:** No preloaded Hermes — manual install required

**Best for:** General-purpose Linux desktop that can also run Hermes.

## Raspberry Pi 5 (board only, $50-120)

The Pi 5 without the keyboard enclosure. Same CPU/RAM as the Pi 500.

- Needs: case, power supply, microSD, cooling (heatsink/fan required under load)
- Max power draw: ~12 W under load
- PCIe Gen 2 x1 for NVMe (requires hat)

## Mini PCs (used, $100-200)

Dell Wyse 5070, Lenovo M720q, HP EliteDesk, Intel NUC.

- **Pros:** x86 (no ARM translation issues), full-speed NVMe, more RAM (8-32 GB), better perf per dollar, Docker-native
- **Cons:** Larger, higher power draw (~15-25 W), no voice hardware, no preloaded Hermes

## Key Decision Factors

| Factor | Intern 2 | Pi 500 | Mini PC |
|--------|----------|--------|---------|
| Price | $249 complete | $400 complete kit | $100-200 (used) |
| Hermes setup | Preloaded | Manual install | Manual install |
| Voice | Dual mic + speaker | None | None |
| RAM | 6 GB | Up to 16 GB | 8-32 GB |
| Storage speed | eMMC | microSD (slow) | NVMe (fast) |
| CPU | 2× A76 + 6× A55 @ 2.0 GHz | 4× A76 @ 2.4 GHz | x86 (varies) |
| x86 compat | No (ARM) | No (ARM) | Yes |
| Power | ~10 W | ~12 W peak | ~15-25 W |

## Running Large Models Locally (DeepSeek V4 Flash class)

When the user asks how to run a big open-weight model (284B-class) locally and how many machines it takes, see `references/deepseek-v4-flash-local-sizing.md`. Key facts: the Mac mini tops out at 64 GB unified memory (can't run a 284B model on one unit), stringing minis works but is slow, and 2x DGX Spark (~$8K) is the reference deployment hitting 55-60 tok/s with 1M context.

## Use Cases

### Free Your Laptop
The most common reason to buy a dedicated Hermes box: run one agent 24/7 at home so your laptop can travel. The Pi 500 or Intern 2 handles crons, dashboard, and always-on connectivity. Your laptop becomes a portable terminal you can take anywhere. If you need a second agent while traveling, fire it up on the laptop. If you need a third permanent agent, buy another Pi 500 for $400.

**Dedicated cron runner setup:** See `references/dedicated-cron-runner.md` for the full flow — cloning a backup to a secondary machine, handling provider drift (issue #44585), configuring Telegram on the clone, and the pitfalls of running a second Hermes instance as a headless cron appliance.

**Email pipeline & domain warmup:** See `references/email-distribution-warmup.md` for how the cron box's daily email sends build sender reputation, the mechanics of ISP trust, how real subscriber engagement compounds over months, and how branded-alias subscribers (like Dann Sommer at dann-sommer.dk) are high-signal watchers who unknowingly help warm your domain.

### Dual-Purpose Cron Box (Backup Workstation)

A dedicated cron machine can also serve as a fallback workstation. This is a natural pairing that earns the hardware its keep in two ways:

- **Primary role:** Headless cron appliance — runs all scheduled jobs 24/7 on native Linux, delivers to Telegram, never sleeps
- **Secondary role:** Emergency workstation — if the main laptop dies, SSH in and use it as a full Hermes session
- **Tertiary role:** Build/experiment sandbox — test new pipelines, OS configurations, and workflows without touching the production machine

**Key design decisions:**
- Run native Linux (not WSL) — fewer translation layers, cleaner execution, better tool compatibility. Hermes performs noticeably better on Linux than on WSL.
- Keep interactive sessions minimal on the cron box to avoid starving cron jobs of context
- The backup capability is insurance — it costs nothing to have and you hope you never need it
- Every bug squashed and config dialed in on the cron box is future coaching content — the process of setting it up across Windows, WSL, and Linux builds repetition at scale

**Multi-agent deployment:** A single Linux box can run multiple Hermes agent instances. The primary agent (interactive, creative, strategic) runs on the laptop. A second agent instance (e.g. "Bill") runs on the cron box with the same skills, memory, and workflows, handling the automated pipeline in parallel. This is force multiplication — same brain, separate iron.

**Cross-OS setup as coaching curriculum:** Every OS you set up on (Windows, WSL, Linux) builds repetition that becomes teachable expertise. The bugs you squash, the configs you dial in, the quirks you learn to dance around — those are hours of future coaching content you can deliver without having to figure it out on camera. The machine is the product, the process is the curriculum.

**See:** `references/dedicated-cron-runner.md` for setup details.

### Cron-Only Appliance
For users who primarily run scheduled jobs (crons) and check the dashboard, 6 GB is sufficient. Cron jobs fire, execute, deliver, and die — they don't accumulate context. The Intern 2 is ideal here: headless, voice-capable, preloaded, tucked in a corner.

### Full Desktop + Agent
For users who want to sit at the machine, open the dashboard in a browser, have the desktop available for other work, and manually manage crons. The Pi 500 kit is the better choice — it's an actual computer with a screen, keyboard, and mouse in the box. 16 GB RAM means you can run the dashboard, a browser, a terminal, and a Hermes session simultaneously.

## Business Model: Selling Pi 500 Setups to Small Businesses

The Pi 500 is a natural product for SMBs. Key selling points:

### Low Risk to Say Yes
$400 is a dinner out for a business. If it doesn't work, they're out $400 and they learned something. If it does work, they're hooked. You're selling a bet they can afford to lose.

### "Not on Your Machine"
The biggest barrier to SMB adoption of AI agents is fear — security concerns, IT approval, slowdowns on their work machine. A dedicated box solves all of that:
- "It's not on your computer, it's a little box that plugs into the wall."
- "If something goes wrong, unplug it and your machine is fine."
- No installs on their work laptop. No IT approval. No "is this going to slow down my QuickBooks?"
- It's a self-contained appliance that lives on the network. They can see it, touch it, unplug it.

### Repairability as a Feature
Small businesses have been burned by proprietary appliance culture. The Pi 500 is the opposite:
- Fan dies: $5
- Power supply goes: $15
- SD card corrupts: $10 and reflash
- Whole computer dies: $100 for a replacement board, back in business in an hour
- No soldering, no proprietary parts, no sending it to a repair shop for a week

### The Full Stack: Pi 500 + Ollama Pro
Pair the Pi 500 with Ollama Pro for a complete local-AI stack:
- $400 hardware, always on, repairable, zero fear factor
- Ollama Pro handles inference — no $2700 Mac Mini or $5000 GPU rig needed
- No cloud API costs per token
- No data leaving the network
- No subscription for the hardware
- Predictable monthly cost for the brain

### Revenue Model
- Hardware margin on the Pi 500 setup (one-time)
- Recurring revenue on Ollama Pro or service fee (monthly)
- You're the guy who makes it all work
- Referral machine: once they rely on it, they tell other business owners

### The Adoption Curve
1. Month 1: Nervous, checking the dashboard daily, not sure what to do with it
2. Month 2: Starting to rely on it
3. Month 3: Can't imagine running their business without it
4. You're the guy who set it up — locked-in relationship

### Pricing Psychology

**The $200/month trap.** The market has trained SMBs to say no. Every SaaS sales rep, AI consultant, and digital transformation pitch has been $200-500/month for something they don't understand. They have an allergic reaction to that number. Walk in with $400 for the box and $20/month for the brain. It is less than their phone bill. It disarms them completely.

**The ROI framing.** $1,040 for the first year ($800 hardware + $240 Ollama Pro). That is an employee that never sleeps, never calls out sick, never asks for a raise, never takes vacation. If that does not return 5x ($5,000+) in a year, the business is not using it right. 5x is the floor, not the ceiling. One good use case — automated lead response, price monitoring, customer sentiment tracking — could return that in a month.

**The college course comparison.** A community college course is $500 for a semester and you might learn something you never use. This is $250/year for a brain that works for you every single day. One semester of night school or a year of having an AI assistant that actually does things.

**The bet they cannot afford not to take.** AI is not a trend, it is a shift. Businesses that figure it out now have a 2-3 year head start. The cost of not trying is higher than the cost of trying and failing. A business that ignores AI for two years will not just be where they are now — they will be behind. Their competitors will be faster, cheaper, more efficient. The gap does not stay static, it widens.

### Sales Approach (B2B In-Person)

See `references/sales-playbook-smb.md` for the full playbook. Key principles:

**Add value before talking numbers.** If you can show the value without talking about it, you can charge whatever. Most prospects ask the price upfront because it is the easiest way to say no without engaging. Sidestep: "Let me show you what it does first, then you tell me what it is worth."

**The reverse close.** "It is expensive, which is why I am not trying to sell you on it." You agree with their objection before they make it. Now they have to convince themselves.

**Lead with their story, not your product.** Walk in empty-handed. No pitch, no materials, no pressure. Ask questions and let them talk. By the time they ask what you are selling, you already know exactly how to frame it.

**The pattern interrupt.** Tell them what they are thinking before they can think it: "The only reason I am here is my boss made me come. This is very expensive and most people throw me out after 5 minutes of my pitch." Now they cannot use that script on you.

**The curiosity object.** Drop the Pi 500 on their counter. Do not mention it. Let them ask what that little machine is. Then: "Oh, this is what I used to find that info." You never pitched. They asked.

**The competitor frame.** "I was preparing for an appointment at your competitor and pulled up the wrong business. Since the work was done, I figured I would share the output." Same message without the accusation.

**Make it a game.** If it is not a game, it is work. Every sale is a level. Every referral is a bonus.

**The unexpected leads to impulse.** Predictable gets tuned out. Unexpected gets a reaction. Make them laugh and they will buy.

## Pitfalls

- **Don't confuse the Intern 2 with a generic SBC.** It's a purpose-built Hermes appliance from autonomous.ai, not a LattePanda or generic Orange Pi. The URL is autonomous.ai/intern.
- **RAM is the bottleneck for Hermes.** Long sessions with heavy tool output can push past 6 GB. If the user runs 50+ turn sessions regularly, recommend 8 GB+.
- **Pi 5 needs active cooling.** It throttles without a heatsink/fan under sustained load. Factor that into the BOM.
- **Pi 5 storage is slow without an NVMe hat.** microSD is noticeably slow for session I/O, skill loading, and log writes. An NVMe hat adds $15-25.
- **ARM compatibility.** Docker images, binaries, and some Python packages may lack ARM builds. If the user needs x86 compatibility, recommend a mini PC instead.
- **The Pi 500 kit at $400 is a complete desktop.** Don't recommend adding a monitor/keyboard/mouse — it's all included.
- **At the same $400, the Pi 500 is the better value for desktop use.** The Intern 2's advantages are voice and preloaded Hermes. The Pi 500 has 2-3x the RAM and a faster CPU. One curl command to install Hermes is not a meaningful difference.
- **Don't guess the future.** When a user is deciding between a $400 Pi and a $2700 Mac Mini for local models, the right answer is: start with the Pi, learn the stack, and buy the big machine when you know exactly what you need it for. The Pi covers what they know they need right now.
