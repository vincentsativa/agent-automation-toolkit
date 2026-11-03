# Dedicated Agent Hardware, Intern 2 / SBC Clone

## The Concept

Vinny is interested in a dedicated always-on Hermes appliance, a standalone Linux box (Orange Pi or similar SBC) that runs a full copy of Hermes with all skills, memories, and config cloned from the WSL instance.

## Why It Matters

- **Frees the laptop**, currently the laptop must stay plugged in 24/7 because it hosts Hermes. A dedicated box means the laptop can be closed, bagged, and taken anywhere.
- **Always-on cron**, scheduled jobs (IronPulse, PhantomByte publishing, money-making cron) run independently of whether the laptop is awake, asleep, or in another city.
- **Voice interface**, the Intern 2 ships with mic + speaker for voice interaction.
- **Telegram + CLI + desktop dashboard**, all four interfaces on one device.
- **Clone, not twin**, after cloning, the two instances diverge independently. No live sync unless rsync is set up.

## The Build vs Buy Trade-Off

| | Buy (Intern 2) | Build |
|---|---|---|
| Cost | $249 | ~$150 |
| Time | None | A weekend |
| SBC | Orange Pi 4 Pro (2018 ARM) | Pick your own (RPi 5, OPi 5, etc.) |
| Enclosure | Professional | Janky or custom |
| Support | Warranty, returns | You're on your own |
| Fun factor | Zero | High |

Vinny would likely buy it and then immediately take it apart anyway.

## The Real Value

The Intern 2 at $249 is the key that unlocks the laptop. It takes over the "always-on agent" job so the laptop becomes a free machine again, close the lid, throw it in a bag, take it to a coffee shop. When you need to code, open it. When you're done, close it. The agent keeps running on the cube.

## Future Vision

- **Intern 2**, always-on Hermes (voice, Telegram, dashboard)
- **Laptop**, mobile dev machine
- **Mac Mini** (future), whatever it needs to be

## Cloning Process

Everything lives in `~/.hermes/` on WSL:
- `~/.hermes/skills/`, all workflows
- `~/.hermes/memories/`, persistent facts
- `~/.hermes/config.yaml`, provider setup, Ollama Pro endpoint
- `~/.hermes/sessions/`, conversation history

Copy the whole directory to the new box's Hermes installation, change the provider endpoint if needed, and boot.
