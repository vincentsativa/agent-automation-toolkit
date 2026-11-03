# Session Notes: Hardware Comparison (2026-07-11)

## Context
User asked about running Hermes on dedicated hardware. Initially asked about Pi 4 vs Pi 5, then revealed they were comparing the Autonomous AI Intern 2 ($249) against the Raspberry Pi 500 Desktop Kit ($400).

## Key Discovery
The Autonomous AI Intern 2 is a purpose-built Hermes appliance from autonomous.ai. It's an Orange Pi 4 Pro in a 4.7" cube with dual mics, a 5W speaker, and Hermes preloaded. The user had to provide the URL (https://www.autonomous.ai/intern) because I initially confused it with a generic LattePanda/Intel N100 board.

## Specs Confirmed from Product Page
- **Price:** $249 (bulk discounts: 3-4 @ $241, 5-9 @ $236, 10-29 @ $233, 30+ @ $230)
- **Board:** Orange Pi 4 Pro
- **CPU:** 8-core: 2x Cortex-A76 + 6x Cortex-A55, up to 2.0 GHz
- **RAM:** 6 GB LPDDR5
- **Storage:** 64 GB + up to 256 GB expansion
- **Voice:** Dual mic (up to 3m), 5W speaker
- **Dashboard:** Web monitor with logs, analytics, CLI
- **Power:** USB-C (5V/5A)
- **Connectivity:** Wi-Fi 6 + Bluetooth 5.4
- **Editions:** OpenClaw, Hermes, Developer
- **Returns:** 30-day free return, 1-year warranty
- **4th of July sale:** 30% off through July 12th (at time of conversation)

## Pi 500 Kit Specs (from product page)
- **Price:** $400 (complete with keyboard-PC, mouse, monitor)
- **CPU:** 4x Cortex-A76 @ 2.4 GHz
- **RAM:** Up to 16 GB LPDDR4X
- **Storage:** microSD (no onboard NVMe)
- **Connectivity:** Wi-Fi 5, Bluetooth 5.0
- **No voice hardware**

## User's Use Case
Running Hermes with the dashboard, plus "other stuff", general desktop use alongside the agent.

## Key Insights from Conversation

### The "Free Your Laptop" Argument
The user's real problem: their laptop is a server they can't take anywhere. One Pi 500 frees it completely. One agent runs 24/7 at home on the Pi 500, crons, dashboard, always on. The laptop goes in the bag for travel. If they need a second agent while out, fire it up on the laptop. $400 to unchain a laptop is a bargain.

### At the Same $400, Pi 500 Wins
Both options cost ~$400 when you factor in peripherals for the Intern 2. The Pi 500 has 2-3x the RAM (8-16 GB vs 6 GB) and a faster CPU (2.4 GHz vs 2.0 GHz). The Intern 2's only advantages are voice hardware and preloaded Hermes. One curl command to install Hermes is not a meaningful difference.

### The Business Model Angle
The user realized they could sell Pi 500 setups to small businesses. Key selling points:
- Low risk ($400, disposable)
- "Not on your machine", no security fear, no IT approval
- Repairable with $10-15 parts
- Pair with Ollama Pro for a complete local-AI stack
- Hardware margin + recurring service revenue

### The "Don't Guess the Future" Principle
When deciding between a $400 Pi and a $2700 Mac Mini for local models, the right answer is: start with the Pi, learn the stack, and buy the big machine when you know exactly what you need it for. The Pi covers what you know you need right now.
