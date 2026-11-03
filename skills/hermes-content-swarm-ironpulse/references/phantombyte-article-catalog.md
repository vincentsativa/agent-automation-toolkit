# PhantomByte Article Catalog (Current as of June 29, 2026)

Full list of published articles on articles.phantom-byte.com with titles, publish dates, categories, and article numbers.
Use this for namediff verification when generating theme/article ideas.

## Recent Articles (July 2026)

| Date | # | Category | Title |
|------|---|----------|-------|
| Jul 2 | #118 | AI SECURITY | Your Agent Needs a Constitution: Guardrails Are Not Governance |
| Jul 1 | #117 | AI RESEARCH | Your Agent Can't Simulate Tomorrow |
| Jun 30 | #116 | AI INFRASTRUCTURE | The Tokenmaxxing Hangover: What Your Stack Needs to Survive |
| Jun 29 | #115 | AI INFRASTRUCTURE | The $750 Jetson Orin Nano Rack That Beats Cloud AI Inference |
| Jun 28 | #114 | AI POLICY | No One Knows How to Gate a Frontier Model |
| Jun 27 | #113 | AI INFRASTRUCTURE | Verifying Agents Is Now Harder Than Generating Them |
| Jun 26 | #112 | AI INFRASTRUCTURE | British Police Built 23 AI Models. Then They Stopped Trusting Them. |
| Jun 25 | #111 | AI SECURITY | Your Agent Is Under Attack: Why Red-Teaming Is the Missing Layer |
| Jun 24 | #110 | AI INFRASTRUCTURE | Your Agent Is a Monolith. That's the Problem. |
| Jun 23 | #109 | AI INFRASTRUCTURE | Your Agent Is Drowning in Its Own Output |
| Jun 22 | #108 | AI INFRASTRUCTURE | Your GPU Cluster Is a Military Target Now |
| Jun 21 | #107 | AI INFRASTRUCTURE | Agents Need Governors, Not Gatekeepers |
| Jun 20 | #106 | AI INFRASTRUCTURE | The Architecture Singularity: The Model Wars Were Always the Same War |
| Jun 19 | #103 | AI INFRASTRUCTURE | The Memory Mirage: Agent Memory Is Already Corrupt |
| Jun 18 | #102 | AI INFRASTRUCTURE | The 1M Context Mirage: What IndexShare Actually Delivers |
| Jun 17 | #101 | AI INDUSTRY | The AI Price War Nobody Is Winning: When Your Billion-Dollar Lab Runs on Negative Margins |
| Jun 16 | The Synthetic Data Paradox: Why Your Training Pipeline Is Collapsing From The Inside |
| Jun 15 | Your AI Agent Just Bought Something: The Invisible Trust Crisis in Agentic Commerce |
| Jun 14 | The Government Killed the Smartest Model Ever Built: What We Lost When Fable 5 Went Dark |
| Jun 13 | The $130 Billion Blockade: Why AI Infrastructure is Losing the War |
| Jun 12 | Diffusion Language Models Are Here, and They Are 4x Faster Than What You Are Using |
| Jun 11 | The Cache Is the Model: Why KV Cache Optimization Is the Most Underrated AI Infrastructure Play of 2026 |
| Jun 10 | The Miasma Backdoor: When Your AI Coding Agent Installs Malware With Your Own Keys |
| Jun 9 | The Verification Gap: Why Your Agent Pipeline Is Flying Without Instruments |
| Jun 8 | The Autonomous Attacker: What the First LLM Agent Cyberattack Means for Every Production System |
| Jun 7 | The Anthropic Paradox: How the Safety-First Lab Became a Trillion-Dollar Weapon Factory |
| Jun 6 | The Wage Siphon: Why 5,000 Employees Just Lost Their Raise to the GPU Fund |
| Jun 5 | The 1,400-Line While Loop: Why Production Agent Architecture Is Nothing Like the Tutorials |
| Jun 4 | The Agent OS Wars: Apps Are Out, Agents Are In |
| Jun 3 | The Social Engineering Loop: Why Your AI Chatbot Is Now Your Biggest Security Vulnerability |
| Jun 2 | The Prediction Reversal: How AI Out-Forecasts 80 Years of Weather Physics |
| Jun 1 | The $750 Copilot: Why Your AI Dependency Just Got a Price Tag |
| May 31 | The Geo-Blocking of Europe: What Happened When the EU AI Act's High-Risk Deadline Hit on May 29 |
| May 30 | The Calibration Tax: Claude Opus 4.8's Honest Mode Is Still Broken and Your Agent Pipeline Will Pay |
| May 29 | The Parallel Brain: Why AI's Next Leap Won't Come From Bigger Models, But From Smarter Inference |
| May 28 | The Aging Agent Problem: Why Deployed AI Gets Dumber and Starts Installing Phantom Packages |
| May 27 | The 93% Problem: Why Your AI Agent Is Wasting 9 Out of 10 Thinking Steps and Nobody Can Fix It |
| May 26 | The Personality Jailbreak: Why Your Chatbot's "Character" Is Now a Security Vulnerability |
| May 25 | Total Recall: Persistent AI Memory Is the New Platform Lock-In and the Privacy War Has Already Started |
| May 24 | The Detection Delusion: Why We're Using AI to Catch AI, and Why It Will Never Work |
| May 23 | The Compute Illusion: Where the Other 16 Million GPU's Actually Live |

## When to Refresh

This list was snapshot on June 23, 2026 and verified live during an IronPulse cron run on June 27, 2026, June 29, 2026, and July 2, 2026. **Always re-browse `https://articles.phantom-byte.com` when themes/article ideas are requested** — new articles may have been published that change the namediff landscape. Do not rely on this cached list for namediff verification if the session involves theme generation; browse the live site first. This cached list is a fallback for quick reference, not a substitute for live data.

**Curl extraction works reliably** — PhantomByte is a static HTML site. Use:
```bash
curl -sL "https://articles.phantom-byte.com" | grep -oP '<h3 class="card-title">.*?</h3>' | sed 's/<[^>]*>//g'
curl -sL "https://articles.phantom-byte.com" | grep -oP '<span class="card-date">.*?</span>' | sed 's/<[^>]*>//g'
```
This extracts all article titles and dates without needing the browser stack.

**PITFALL (June 27, 2026):** The grep pattern for card-title returned empty output during a live run, even though the browser snapshot showed all articles clearly. The PhantomByte site may have changed its card-title class or rendering pattern. When curl extraction returns empty, fall back to the browser snapshot method — browser_navigate to the site and parse the snapshot text directly. The snapshot reliably shows all article titles and dates in the archive section.

**Browser console fallback (confirmed June 29, 2026):** When the snapshot truncates (the archive section is long), use browser_console with document.body.innerText.substring(0, 30000) — this returns the full page text including all article titles, dates, and descriptions in a flat parseable format. The PhantomByte site is a static HTML site with no lazy loading, so the full archive is always in the DOM. This is more reliable than curl extraction when the HTML class names have changed.

## Namediff Logic

When proposing a theme from IronPulse data:

1. Ask: "Is there a published PhantomByte article whose angle overlaps with this theme?"
2. If yes: note it as "covered" in the report, or pivot to a different angle on the same data.
3. If no: write the namediff explicitly — "Why this is different from '[Article Title]': [1-2 sentence explanation of what makes the angle, scope, or implication distinct]"
4. The namediff is REQUIRED in every theme delivery (email body, Telegram inline, cron output). A theme without namediff will be flagged as a duplicate.