# Performance-Weighted Topic Allocation

Source: Pinterest Analytics overview export, 2026-08-14 to 2026-11-12 (90 days), PhantomByteAI, organic Pins only. Regenerate any time with `python3 ~/.hermes/scripts/pinterest_performance.py`, which reads the newest export in `.../<user>/Downloads` and rewrites `~/.hermes/state/pinterest_performance.json`.

## Measured rates (rates, not totals)

- AI News / Emerging Tech: 19,871 impressions, 1.85% engagement, 0.39% save, 0.065% outbound. Carries 28.9% of all impressions and the most saves (77) and outbound clicks (13).
- AI for Developers / Programming: 15,577 impressions, 0.73% engagement, 0.06% save, 0.039% outbound. Reach without saves: the weakest save rate of any real board.
- AI Tools / Business Productivity: 14,533 impressions, 0.73% engagement, 0.08% save, 0.069% outbound.
- AI Agents / Automation: 9,463 impressions, 1.03% engagement, 0.11% save, 0.106% outbound. Best outbound-click rate on the account, meaning it is the board that actually sends traffic.
- Robotics / Physical AI: 4,125 impressions, 2.30% engagement, 0.82% save, 0.073% outbound. Highest engagement and highest save rate by a wide margin, at a sixth of the news board's reach.
- Agent Security: 3,927 impressions, 1.07% engagement, 0.10% save, 0.051% outbound.
- Quantum Computing: 1,147 impressions, 1.74% engagement, 0.61% save, 0.000% outbound. Rates look decent, reach is tiny, and it converts nothing.

Weekly impressions fell from 7,260 to 1,467 between mid-August and mid-October, then recovered to 13,674 in the final week. The recovery started the same week the account began publishing again after the September gap, so the trend reads as publishing cadence driving reach, not as a change in per-pin quality.

## What the numbers say to do

1. News stays the largest single allocation. It owns the reach, the saves, and the outbound clicks. Cutting it would trade a proven surface for a hypothesis.
2. Robotics gets a doubled allocation. Its engagement and save rates are the best on the account, and save rate is the strongest distribution signal Pinterest documents. Low impressions next to high rates means under-published, not weak.
3. Developer and tools keep their volume but change their job. Both sit at 0.73% engagement. The fix is not more posts, it is posts built to be saved: a snippet, a command, a checklist, a comparison.
4. Agents keep one slot and get a harder angle. It has the best outbound rate, so the posts must carry architecture comparisons, benchmarks, or real deployment results instead of concept explainers.
5. Quantum loses its standing slot. Zero outbound clicks across 1,147 impressions is a board that indexes interest and sends nobody anywhere. It takes a slot only for a major, dated development.
6. Security holds a contingent slot. Its engagement rate beats developer and tools, so a genuine attack-plus-fix story displaces one news slot for the day.

## The 10-slot daily allocation

- 3 slots, AI News | Machine Learning & Emerging Tech
- 2 slots, Robotics & Physical AI [Humanoid Robots]
- 2 slots, AI for Developers & Programming AI [Tutorials]
- 2 slots, AI Tools for Business & Productivity [2026]
- 1 slot, AI Agents & Automation [Guide]
- 0 slots, Agent Security: Prompt Injection & Sandboxing (contingent 1, swaps out one news slot)
- 0 slots, Quantum Computing [Explained] (contingent 1, swaps out one news slot, major dated development only, maximum once per week)

The total stays at 10. This is a re-weighting, not a volume increase. `pinterest_performance.py` recomputes this allocation from the newest export with the formula below, so it follows the data instead of drifting on opinion: priority = 0.5 x (impressions / max impressions) + 0.3 x (engagement rate / max engagement rate) + 0.2 x (save rate / max save rate), converted to 10 slots proportionally, clamped to each board's band (news 2-4, dev 1-3, tools 1-3, agents 1-2, robotics 1-3, security 0-2, quantum 0-1), quantum held out of the proportional pool.

## Per-board angle rules

These are the content rules that follow from the data, and they apply to headline, graphic, and description together.

- AI News: headline carries the concrete number or the exact change in the first 50 characters. The graphic is a headline card with that number dominant. The description says what changed, who it affects, and why it matters now.
- Robotics / Physical AI: the graphic must show hardware or a deployment scene, never an abstract diagram. Headline names the robot, the factory, or the pilot plus a spec or count. Description carries the spec numbers and the real-world result. This board earns saves, so end with an explicit save reason.
- Developers: the graphic is code, terminal output, or an architecture diagram with a legible snippet. Headline names the tool, model, or technique and the concrete outcome. Description gives the reader something to keep: a command, a config, a comparison, or a measurable before and after. A developer pin that cannot be saved is a wasted slot.
- AI Tools / Business: the graphic shows the product surface or a numbered three-step workflow. Headline names the tool and the job it removes. Description includes a prompt, a checklist, or a pricing or feature comparison, plus the save reason.
- AI Agents: architecture comparison, benchmark table, or a named deployment result. Never "what is an agent" and never a generic capability list. Name the models, the framework, or the numbers.
- Agent Security: one specific attack path and the specific control that stops it. No general security advice.
- Quantum: only a major dated development (a demonstrated advantage, a funding or hardware milestone). No explainers, no "what is quantum computing" posts.

## Repetition rule

Beyond the dedup gate, no story, company, or concept may appear on two consecutive days in the same board, and no more than two posts in one batch may share a company. The dedup script catches exact story repeats; this rule covers the softer repeat where the same company's news is retold with a different angle.

## The feedback loop

The weekly job `PINTEREST PERFORMANCE FEEDBACK LOOP` (Sunday 12:30) does four things in order.

1. Runs `python3 ~/.hermes/scripts/pinterest_performance.py --refresh --enrich 30`, which parses the newest export, recomputes board rates, and enriches the top 30 pins with their board, title, and destination.
2. Compares the new rates against the previous ledger snapshot and names which boards moved and by how much, using rates and never raw totals.
3. Evaluates individual pins: which boards produced the breakout pins, and whether the top pins follow the angle rules above (a robotics pin with a hardware visual, a developer pin that carries a usable snippet, and so on).
4. Adjusts the allocation only when the evidence supports it, by writing `~/.hermes/state/pinterest_allocation.json` with the new slot counts, a written reason, and a timestamp. The script validates the override against the bands and the 10-slot total and rejects anything out of bounds, so drift cannot accumulate silently. If no board moved enough to justify a change, it leaves the computed allocation in place and says so.

A move qualifies only when the board appears in the board table in both exports and its save rate or engagement rate moved more than 25% relative between them. Anything smaller is noise in a 90-day window, and the export does not carry per-pin counts, so no finer test is computable from it.

The loop must report the export date it used. A stale export means the loop has nothing new to say, and it says exactly that instead of re-reporting old numbers as fresh.

## Where the rules are applied

- `pinterest-academy` (governing playbook): allocation, angles, feedback loop
- `pinterest-board-dedup-scrape`: board assignment quotas and the repetition rule
- `pinterest-account-growth`: cadence unchanged, allocation pointer
- `writing-style`: Pinterest headline and description rules that follow from the rates
- Cron `DAILY Pinterest Posts 5:45PM`: reads the brief and enforces the quotas
- Cron `PINTEREST PERFORMANCE FEEDBACK LOOP`: runs the weekly evaluation and may write the override
