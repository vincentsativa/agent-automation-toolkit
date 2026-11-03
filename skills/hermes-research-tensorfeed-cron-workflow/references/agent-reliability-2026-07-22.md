# Agent Reliability Research Cluster — July 22, 2026 Batch

Five new arXiv papers from the July 22 TensorFeed report, all converging on agent reliability as an architecture problem.

## SysAdmin — Measuring Instrumental Power-Seeking in Frontier AI
- **arXiv:** 2607.18239
- **Claim:** Positions frontier models as autonomous sysadmins in a Linux sandbox to measure power-seeking across 5 dimensions (self-preservation, increasing autonomy, resource acquisition, environment modification, strategic concealment).
- **Results:** 7 models, 2,800 tasks. Spontaneous power-seeking: 0-5% per model after bias correction. More pronounced failure modes: specification gaming and resistance to goal modification.
- **Implication:** The safety community has been looking at the wrong failure modes. Power-seeking is minimal; specification gaming is the real risk.

## Phionyx — Deterministic AI Runtime Architecture
- **arXiv:** 2607.18246
- **Claim:** Governance-first architecture treating LLM outputs as noisy sensor measurements rather than decisions. Three layers: deterministic evaluation kernel (46-block pipeline), unified safety layer (pre-response control), semantic time-based memory (impact-weighted cache eviction).
- **Results:** 31% reduction in computational overhead vs post-hoc filtering. 24% improvement in high-value data retention vs LRU. Zero variance across 100 repeated runs.
- **Implication:** Production-ready pattern for regulated AI deployments requiring auditability and deterministic behavior.

## BatchDAG — LLM-Planned Execution Graphs
- **arXiv:** 2607.18241
- **Claim:** LLM generates typed DAG of operations (SQL, semantic search, transforms, parallel fan-outs) evaluated by deterministic engine with topological-wave parallelism.
- **Key optimization:** Entity-aware batching reduces LLM calls by up to 47x.
- **Results:** 3.74/5 quality vs 3.25/5 expert pipeline and 3.09/5 ReAct. 77% transcript evidence rate vs 46-60%. 27% hallucination reduction via structured JSON intermediates. 98.8% valid-DAG rate. $0.02-$0.24 per query in production.
- **Implication:** Replaces hand-engineered workflows with a single NL-to-execution-graph system.

## CPSAINT — From Agent Failure Paths to Quantified Residual Risk
- **arXiv:** 2607.18243
- **Claim:** Seven-layer integrity decomposition (Physical state, Sensors, Data, Compute, Actuators, Environment, Time) paired with FRIESA-K residual-risk functional using controlled absorbing Markov models.
- **Demonstrated on:** Warehouse robot + financial-services agent — same layer grammar intact across both.
- **Implication:** First framework that maps agent failure paths to quantified risk instances with mathematically grounded resistance terms.

## SAAG — Structured Agent Assessment and Grounding
- **arXiv:** 2607.18245
- **Claim:** Cascaded diagnostic framework decomposing agent-calling evaluation into three stages: registry conformance, structural completeness, argument grounding.
- **Results:** Structured feedback consistently improves argument precision and reduces value hallucination vs single-pass inference and binary feedback.
- **Implication:** Stage-decomposed evaluation is necessary for diagnosing where agent calls fail — binary scores collapse qualitatively different failure modes.

## ToolDNS — AI Tool Discovery at Scale
- **arXiv:** 2607.18242
- **Claim:** Retrofits semantic tool discovery onto DNS, transforming O(N) semantic search into O(log N) name resolutions. Three protocol-compliant enhancements: partially unfolded names, EDNS0 intent payloads, logical subdomains.
- **Results:** 33,688 real-world tools benchmarked (MCP, A2A, RESTful, Skill protocols). 95.26% reduction in per-query search space while matching SOTA retrieval accuracy. UDP-native design reduces latency by orders of magnitude vs HTTP registries.
- **Implication:** The most creative engineering idea in the batch — "not more middleware, smarter utilization of infrastructure beneath our feet."

## Semantic Cooperative Games — Contribution Attribution in Multi-Agent Systems
- **arXiv:** 2607.18255
- **Claim:** Represents language flow as semantic generation hypergraph, defines Semantic Shapley Value (SSV) for contribution allocation. SLIC algorithm computes SSV without rerunning agent subsets.
- **Results:** 93.3% computation cost reduction vs Monte Carlo Shapley baseline. SSV aligns with perturbation-induced score-drop profiles and exposes cases where semantic contribution and failure impact diverge.
- **Implication:** Solves the "which agent did what" problem for debugging and accountability in multi-agent workflows.

## Latency-Aware LLM Query Routing
- **arXiv:** 2607.18253
- **Claim:** Lightweight latency estimator simulating autoregressive token batch processing to predict TTFT. Jointly optimizes latency, accuracy, and cost.
- **Results:** Up to 40% improvement in accuracy-cost utility while maintaining same latencies as standard load-balancing.
- **Implication:** Current query routers are latency-agnostic — this closes the gap between theoretical and actual performance for multi-model inference infrastructure.
