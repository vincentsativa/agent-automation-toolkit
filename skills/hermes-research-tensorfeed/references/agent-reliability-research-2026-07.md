# Agent Reliability Research Cluster, July 2026

A cluster of papers and experiments surfaced across the July 13 and July 16, 2026 TensorFeed reports, all converging on the same thesis: **agent reliability is an architecture problem, not a model capability problem.** This reference captures the key findings so future reports can reference them without re-browsing.

## Core Papers (July 13 Batch)

### CogniConsole, Externalizing Inference-Time Control
- **arXiv:** 2607.08774
- **Claim:** Reliability is significantly influenced by inference-time control (the computational layer governing task framing and context selection), not just model capability.
- **Method:** 489 controllability-oriented probes in a multi-step interactive environment, comparing unstructured to fully scaffolded control.
- **Result:** Increasing structural scaffolding systematically reduces output variance and failure rates under a fixed model architecture.
- **Implication:** Many observed failure modes (context drift, inconsistent constraint adherence) arise from under-specified control, not insufficient capability.

### GATS, Graph-Augmented Tree Search
- **arXiv:** 2607.08894
- **Claim:** Systematic search with learned world models can outperform LLM-guided exploration for agent planning.
- **Architecture:** Three-layer world model, L1 (exact symbolic action matching), L2 (statistics from execution logs), L3 (LLM-based prediction for unknown actions).
- **Results:** 100% success rate vs 92% (LATS) and 64% (ReAct). Zero LLM calls per task during planning vs 37 for LATS. Deterministic plans with zero variance.
- **Implication:** Planning and execution can be decoupled from expensive inference.

### GRACE, Graph-Regularized Agentic Context Evolution
- **arXiv:** 2607.09175
- **Claim:** Persistent agent instructions maintained as a typed semantic graph outperform flat-text accumulation.
- **Method:** Validates proposed updates within local typed neighborhoods of modified nodes; accepted updates reconstructed as incremental edits to textual instruction checkpoint.
- **Results:** Improves strict reliability from 0.091 (Gemini 2.5 Flash zero-shot) to 0.673. Flat-text baseline achieves only 0.191. Exceeds Gemini 3.1 Pro reference of 0.242.
- **Implication:** Two requirements for reliable long-horizon context evolution: (1) structural substrate making verification local, (2) consolidation mechanism keeping accumulated instructions usable.

### KV-PRM, KV-Cache Transfer for Process Reward Modeling
- **arXiv:** 2607.09153
- **Claim:** KV cache contains strictly greater information capacity than text for downstream reward modeling.
- **Method:** Reads KV cache produced during LLM generation instead of re-encoding trajectory text from scratch.
- **Results:** O(L^2) → O(L) scoring cost. Up to 5,000x reduction in scoring FLOPs, 37x reduction in latency, 34x reduction in memory footprint. Matches or exceeds text-PRM performance.
- **Implication:** Dramatically reduces cost of test-time scaling for multi-agent systems.

### ARCANA, Reflective Multi-Agent Program Synthesis
- **arXiv:** 2607.09059
- **Claim:** Collaborative multi-agent framework with structured program search and adaptive multi-turn correction for abstract reasoning.
- **Architecture:** Perceptual grounding agent → latent program policy → symbolic executor → reflective agent. Shared differentiable blackboard, learned meta-controller.
- **Domain:** ARC-AGI-2 abstract transformation tasks under strict time and hardware constraints.
- **Implication:** Structured multi-agent decomposition with reflective feedback loops outperforms monolithic approaches on abstract reasoning.

### Long-Horizon-Terminal-Bench
- **arXiv:** 2607.08964
- **Claim:** Current terminal benchmarks focus on short, well-specified tasks with sparse reward signals.
- **Method:** 46 long-horizon tasks across 9 categories, decomposed into fine-grained graded subtasks with dense intermediate rewards.
- **Results:** Strongest tested model achieves 15.2% pass@1 at 0.95 partial-reward threshold. Agents consume avg 9.9M tokens, 231 episodes, 85.3 minutes per task.
- **Implication:** Vast gap between current agent capabilities and real long-horizon work demands.

## Core Papers (July 16 Batch)

### Self-Improvements in Modern Agentic Systems: A Survey
- **arXiv:** 2607.13104
- **Claim:** Self-improving autonomous agents are moving from research prototypes to deployed systems. The primary goal is controllable evolution from experience with minimal human input.
- **Method:** 97-page survey offering a system-level framework representing a modern agent as a configuration coupling a foundation model with an operational scaffold of prompts, memory, tools, and control logic. Self-improvement formalized as a self-induced update operator that commits updates to model parameters or scaffold components.
- **Results:** Organizes prior work by update target and driving signals; reviews applications and evaluation approaches.
- **Implication:** The scaffold (not the model) is the primary locus of improvement. Self-improvement means updating either parameters or scaffold components, and the scaffold is where most practical gains live.

### Oracle Agent Memory, Enterprise Memory Substrate
- **arXiv:** 2607.13157
- **Claim:** Agent memory is a systems problem for long-horizon agents. Practical deployments require retention of task state across extended conversations, recovery of user-specific facts across sessions, and accumulation of procedural knowledge.
- **Method:** Database-native memory substrate built on Oracle Database with a layered architecture separating active memory core from passive memory-store interface. Scope control across users, agents, and threads.
- **Results:** 93.8% accuracy on LongMemEval, using 10.7x fewer tokens than flat-history baselines.
- **Implication:** Database-native memory is a serious alternative to vector-database-only approaches for enterprise agent deployments. Memory is a lifecycle (ingestion, extraction, consolidation, retrieval, summarization, revision/removal), not a lookup table.

### Harness Handbook, Behavior-Centric Harness Evolution
- **arXiv:** 2607.13285
- **Claim:** The capability of a modern AI agent depends not only on its foundation model but also on its harness (prompts, state, tools, control logic). As models, APIs, and environments evolve, the harness must be continually modified, but finding where to make changes is the bottleneck.
- **Method:** Behavior-centric representation synthesized automatically from harness codebases via static analysis and LLM-assisted structuring. Introduces Behavior-Guided Progressive Disclosure (BGPD) guiding agents from high-level behaviors to relevant implementation details.
- **Results:** On diverse modification requests from two open-source harnesses, Handbook-Assisted planning improved behavior localization and edit-plan quality while using fewer planner tokens. Largest gains on scattered sites, rarely executed paths, and cross-module interactions.
- **Implication:** Evolving complex agentic systems depends not only on generating edits, but on determining where those edits should be made. This is the first formal treatment of harness maintainability as a research problem.

### AI-Native Insurance for Agentic AI
- **arXiv:** 2607.13230
- **Claim:** Agentic AI introduces new insurance challenges because autonomous AI systems can make decisions, invoke tools, modify external environments, and interact with third-party services.
- **Method:** Mathematical framework representing a deployment by a risk state capturing autonomy level, operational authority, permission exposure, governance maturity, and dependency concentration. Maps risk state to event probabilities, loss severities, premiums, deductibles, and policy covenants.
- **Results:** Establishes structural properties of insurability including characterization of an insurability region, monotone deterioration of feasibility with increasing exposure, and governance certification thresholds.
- **Implication:** Insurance is both an operational cost and a regulatory mechanism for AI deployment. The framework could become the basis for enterprise AI risk assessment.

### SPINE, Bridging the Cyber-Physical Gap with Agentic AI
- **arXiv:** 2607.13049
- **Claim:** Deploying foundation model intelligence into physical robot platforms still demands tedious, expert-driven calibration, a "spinal cord" bottleneck to scalable Embodied AI.
- **Method:** Two orchestrated multi-agent workflows: a profile builder creating robot-specific context, and a debugger cycling through diagnosis, repair, and validation until teleoperation works.
- **Results:** Robotics novice using SPINE outperformed human operators using Claude Code (75% → 100% operationalization success, 16:45 → 13:47 mean time). On a distinct bimanual arm, resolved 10/10 bugs vs 9/10 for expert baseline.
- **Implication:** Structured multi-agent workflows can replace expert calibration for robot deployment. The architecture (not the model) is what transfers across platforms.

### Interventional Grounding Audits, Testing CoT Premise Dependency
- **arXiv:** 2607.13069
- **Claim:** LLMs produce chain-of-thought reasoning that appears logically sound yet may not genuinely depend on its stated premises.
- **Method:** Black-box, step-level test: intervene on a single premise by substituting its target predicate with a fresh symbol, re-run the model, and check whether each reasoning step's conclusion changes.
- **Results:** F1=0.806 on detecting proof-tree dependencies (vs 0.343 for self-consistency baseline). 66% of correctly-solved problems contain at least one reasoning step insensitive to a direct dependency, a "right answer, wrong reasoning" signal invisible to passive methods.
- **Implication:** Standard accuracy metrics miss systematic reasoning failures. Production agents need premise-dependency auditing, not just output validation.

### Networked Intelligence / Mycelium, Active Shared Context Graphs
- **arXiv:** 2607.13220
- **Claim:** Challenging scientific problems are rarely solved by one reasoner alone. The open problem is scaling connections between humans and AI systems, not scaling a single reasoning process.
- **Method:** Mycelium, an active shared workspace that automatically captures observations and hypotheses, tracks how they relate to the team's evolving model, and routes them to the person or agent whose next decision they can inform.
- **Results:** In a biological multi-omics campaign, routed shared context turned a local analytical finding into a cross-expert mechanistic constraint and ultimately into an experimental design.
- **Implication:** Networked intelligence as sparse conditional computation over distributed scientific contexts. When independent expertise and non-mergeable contexts exist, the network is irreducible to a scaled standalone agent.

### OriginBlame, Record- and Token-Level Data Provenance
- **arXiv:** 2607.13037
- **Claim:** When a data contributor requests removal, unlearning algorithms require a forget set, yet no tool can locate which training records belong to a given author. Existing provenance systems operate at file or dataset level, forcing catastrophic over-deletion.
- **Method:** Record- and token-level data provenance that propagates author identity through data processing pipelines and resolves revocation requests into precise forget sets via deterministic queries.
- **Results:** Eliminates dataset-level over-deletion (from 101x to 1.3x) on 219,555 Wikipedia pages. Integration adds 1.3-4.0% throughput overhead. On a 1.7B model, provenance-based forget sets improve unlearning by 42% over random baselines.
- **Implication:** Critical infrastructure for the coming regulatory environment where data contributors have the right to request removal from training datasets.

## Production Case Studies (July 16 Batch)

### Ai2 Shippy, Maritime Domain Awareness Agent
- **URL:** huggingface.co/blog/allenai/shippy-tech-blog
- **Architecture:** Three-component model: soul (system prompt defining persona and behavioral boundaries), skills (handlers for specific request types), config (harness, LLM choice, runtime settings), all baked into versioned Docker images.
- **Key design choices:** Deterministic tools for nondeterministic agents. Sandboxed hosting for isolation. Agent evaluated as a system, not a model.
- **Lesson:** "The real work wasn't the model, it was building a system we could trust to be correct, to stay within its limits, and to hold up across diverse tasks."
- **Implication:** Production blueprint for high-stakes agent deployment. The soul/skills/config decomposition is a reusable architectural pattern.

### IBM Research, Model Routing Is Not a Classification Problem
- **URL:** huggingface.co/blog/ibm-research/model-routing-is-simple-until-it-isnt
- **Key finding:** Across 417 tasks, Claude Sonnet 4.6 was cheaper than GPT-4.1 despite higher sticker prices, because Sonnet's lower cache-read pricing benefited disproportionately from agent workloads that reuse large context chunks.
- **Three hidden dimensions:** (1) Cost is more than model pricing, caching effects dominate. (2) Complexity is more than task difficulty, agent trajectories vary unpredictably. (3) Latency is more than model speed, infrastructure matters.
- **Implication:** A router that only looks at pricing sheets is optimizing against the wrong objective. Effective routing requires understanding the interaction between model behavior, workload patterns, and serving infrastructure.

### pgrust, $100k Postgres Rewrite in Rust with AI
- **URL:** malisper.me/how-pgrust-was-built-four-attempts-to-rewrite-postgres-in-rust-with-ai/
- **Key numbers:** $100k spend, 40 concurrent subagents, 1.8M lines of idiomatic Rust, 4 failed attempts before success.
- **Critical lesson:** File-at-a-time beats feature-at-a-time for AI-assisted codebase rewrites. Repeatable skills are essential. Parallel agent swarms need structured coordination.
- **Result:** 5th version of pgrust is faster than Postgres for transactional workloads and as fast as Clickhouse for analytical queries.
- **Implication:** Practical blueprint for large-scale AI-assisted code transformation with concrete failure modes and success patterns.

## Tooling Experiments

### Toolmetry, MCP Description Rewriting
- **URL:** toolmetry-one.vercel.app
- **Method:** Rewrote MCP server tool descriptions with an LLM rewriter (Kimi K2). Agent: gpt-oss-120b. Total API spend: $4.
- **Results:**
  - SQLite server: 34% → 100% strict success (+66%)
  - Memory server: 61.8% → 96.4% (+34.5%)
  - Git server: 75% → 96.7% (+21.7%)
  - Filesystem server: 74.4% → 84.4% (+10%)
- **Three failure archetypes fixed:**
  1. Wrong-tool confusion, fixed by adding explicit cross-references ("use X instead when...")
  2. Ritual extra calls, fixed by one added sentence ("Do not call this merely to check...")
  3. Deprecated parameter patterns, fixed by removing stale parameter descriptions
- **Implication:** Tool description quality is a massive lever for agent reliability that costs almost nothing to improve.

### DiscoMCP, MCP Server Discovery
- **URL:** github.com/ieranama/discomcp
- **Claim:** Automatically discovers and wraps MCP servers into reusable operational skills for AI agents via a "soft-landing" process.
- **Implication:** Addresses the discoverability problem in the growing MCP ecosystem.

### Founders OS, AI Session Checkpoints
- **URL:** github.com/OurThinkTank/founders-os
- **Claim:** Self-hosted MCP server providing CRM, tasks, finances, feeds, and memory with session checkpointing across AI tools.
- **Implication:** Treating agent memory as infrastructure rather than a feature.

## Common Thread

All of these converge on the same insight: **how you structure the agent's control flow, context, and tool interfaces matters more than which model you use.** This is a direct challenge to the scaling-is-all-you-need orthodoxy and supports the PhantomByte thesis that the harness is the real model.

## Usage in Reports

When writing TensorFeed reports, reference this cluster when the theme "Agent Reliability Through Architecture, Not Scale" appears. The key numbers to cite:
- GATS: 100% success, zero LLM calls (vs 37 for LATS)
- GRACE: 0.091 → 0.673 reliability (vs 0.191 flat-text)
- KV-PRM: 5,000x FLOP reduction
- Toolmetry: 34% → 100% for $4
- Oracle Agent Memory: 93.8% accuracy, 10.7x fewer tokens
- Harness Handbook: improved behavior localization with fewer planner tokens
- SPINE: 75% → 100% operationalization success for robotics novice
- pgrust: 1.8M lines, $100k, 40 concurrent subagents
