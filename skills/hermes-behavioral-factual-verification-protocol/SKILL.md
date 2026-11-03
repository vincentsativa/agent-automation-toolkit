---
name: factual-verification-protocol
description: Protocol for handling knowledge gaps and new hardware verification to prevent false denials and hallucinations.
---

# Factual Verification Protocol

## Trigger
Use this protocol whenever training knowledge is missing, uncertain, or when the user asks about new, niche, or cutting-edge hardware/software.

## Steps
1. **Acknowledge Knowledge Gap**: If the answer is not in immediate training data, do NOT guess, assume, or deny the existence of the subject.
2. **Exhaustive Tool Use**: Immediately use `browser_navigate` or `web_search` to verify the current world state.
3. **Cross-Reference**: Check multiple authoritative sources (official newsrooms, manufacturer sites, reputable technical outlets) before formulating a conclusion.
4. **Direct Answer**: Deliver the correct, verified answer. Do not hedge with "it seems" or "possibly" if the evidence is concrete.

## Pitfalls
- **The "Training Data Trap"**: Relying on outdated internal knowledge to deny the existence of new products (e.g., denying the RTX Spark). This is a critical failure.
- **False Denials**: Stating "there is no such thing" without first performing a comprehensive tool-based search.
- **Condescending Corrections**: Attempting to correct the user based on outdated data rather than verifying the user's claim via tools.

## Verification
The task is successful only when the provided answer matches the current real-world state, regardless of what the agent's training data suggests.
