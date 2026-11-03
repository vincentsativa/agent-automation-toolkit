---
name: sovereign-ai-blueprint-revision
description: Revise the Sovereign AI Stack Blueprint into an expanded, platform-comprehensive edition covering all hardware paths from $0 reuse to DGX, with email delivery.
trigger: "Vinny asks to revise the Sovereign AI Stack Blueprint, expand the blueprint, or make a 'banger' first-impression tutorial document"
---

# Sovereign AI Stack Blueprint Revision Workflow

## When to use
- Vinny asks to revise/expand the Sovereign AI Stack Blueprint
- Vinny asks to make a "banger" or "10/10" first-impression tutorial document
- Any request to create a comprehensive hardware options guide covering NVIDIA, Apple, DGX, and Windows RTX AI PCs

## Source Material
- Original PDF: `https://vincentsativa.com/assets/The-Sovereign-AI-Stack-Blueprint.pdf`
- Extract text with: `pdftotext /tmp/sovereign-ai-stack.pdf -` or `curl -L -o /tmp/sovereign-ai-stack.pdf <url>`

## Required Skills
- `email-sender` — for emailing the finished document

## Revision Structure (7 Hardware Tiers)

The expanded blueprint must cover ALL of these paths:

1. **Tier 0: $0 Reuse What You Own** — any existing computer, CPU inference
2. **Tier 1: Budget Sovereignty (~$900–$1,200)** — RTX 4060 Ti 16GB, Ryzen 5
3. **Tier 2: Enthusiast (~$2,500–$3,500)** — RTX 4090 or dual 3090, 70B models
4. **Tier 3: F*ck the Cloud Workstation (~$6,000–$10,000)** — Threadripper, 4x GPU
5. **Tier 4: Windows RTX AI PC / RTX Spark (Pre-Built, ~$1,500–$4,000)** — MSI, ASUS, Alienware, HP Z, Dell Precision, NVIDIA RTX Spark SFF
6. **Tier 5: Apple Silicon (~$2,000–$8,000)** — MacBook Pro M3/M4, Mac Studio M2/M3 Ultra, Mac Pro, unified memory advantages, MLX
7. **Tier 6: NVIDIA DGX ($40,000–$200,000+)** — DGX Station, DGX A100/H100, DGX B200 Blackwell
8. **Tier 7: Cloud GPU Rental (Hybrid, $0.50–$5.00/hr)** — Lambda, RunPod, Vast.ai, CoreWeave

## Document Sections (in order)

1. **Part 0: Why Sovereign AI Matters** — opening hook about data privacy, no rate limits, no censorship
2. **Part 1: Hardware — The Complete Options Matrix** — all 7+ tiers with specs, pricing, what you can run
3. **Part 2: The Software Stack** — OS, NVIDIA drivers/CUDA, Ollama, Open WebUI, OpenClaw, Hermes Agent, optional tools (n8n, Continue.dev, AnythingLLM, pgvector, Docker Compose)
4. **Part 3: Configuration Checklist** — 5 phases with checkboxes
5. **Post-Setup: Model Expansion Plan** — Week 1/2/3 model pulls
6. **Part 4: Real Numbers — Cloud vs. Local** — cost comparison table
7. **Part 5: Troubleshooting Quick Reference** — common problems and fixes
8. **Part 6: The "Next Level" — What to Build After Setup** — project ideas
9. **Part 7: Platform-Specific Notes** — Windows RTX, Apple Silicon, DGX, Linux

## Key Principles for a "Banger" First Impression

- **Every tier must answer:** "What can I actually run on this?" with specific model names and tokens/sec
- **Every tier must have:** total cost, pros/cons, "best for" audience
- **Platform-specific notes** at the end for Windows, macOS, DGX, and Linux
- **Cost comparison** (cloud vs. local) with real monthly numbers
- **Troubleshooting section** with exact commands
- **Tone:** Direct, confident, no fluff. PhantomByte voice — "Code from the Shadows"
- **Format:** Plain text with clear section separators (`=====`), bullet lists, code blocks

## Email Delivery

Use the `email-sender` skill. Write the document to a `.txt` file first, then write the Python email script to a file (never inline), and run it.

- **To:** hello@phantom-byte.com
- **Subject:** "Revised Sovereign AI Stack Blueprint — Expanded Edition"
- **Body:** Brief note about what's new
- **Attachment:** The `.txt` file

## Pitfalls

- Do NOT skip any hardware tier — Vinny wants comprehensive coverage
- Do NOT fabricate specs or pricing — use real market data
- Do NOT send the document content in Telegram — email it as an attachment
- Always verify the TO address before sending (hello@phantom-byte.com)
- Always grep for email addresses in the script before running
- The inline `python3 -c` approach fails with IONOS SMTP — always use a file
