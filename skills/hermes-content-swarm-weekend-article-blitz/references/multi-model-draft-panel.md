# Multi-Model Draft Panel

Vinny evaluates article drafts by running them through a panel of ~8 different LLMs. Each model votes on which draft is best. Vinny publishes the consensus winner — he does not cast his own vote to avoid biasing the result.

## Panel Composition

The panel runs ~8 models drawn from: Grok 4.3, Gemini, GPT-5.5, Kimi K2.6, DeepSeek V4 Pro, DeepSeek Flash, and others. All models see the same drafts and vote independently. Every major architecture family is represented, making consensus a cross-architecture signal rather than a single-model echo.

**Important:** Same model can vote differently depending on harness. Observed in this session: DeepSeek Pro in Hermes voted for Pro draft; DeepSeek Pro in its own chatbot voted for Flash. The wrapper (system prompt, context window, personality) changes the vote. This is why cross-harness consensus matters — it filters out harness bias.

**Gemini carries implicit SEO weight** — it's trained on the same infrastructure that ranks content (Google Search, Discover). Its vote is not just another model preference; it's a signal from a model that grew up in the same house as the search referee.

## Known Pattern: Flash Dominance

Flash typically wins panel votes because it synthesizes the best qualities of the other drafts:

- **Pro** brings heat — sharp voice, memorable metaphors, aggressive tone
- **Kimi** brings restraint — clean structure, data density, measured delivery
- **Flash** blends both — Pro's punch without the rough edges, Kimi's polish without the mildness

Flash is the safe bet for most article drafts, but it's not a foregone conclusion — depends on the material. Pro often comes in strong second and is considered a quality draft.

## Decision Rule

- Vinny follows the panel consensus. He does not overrule.
- If all 8 models align on one draft, that's a strong signal.
- If votes split, the *reasons* for the split are as valuable as the vote itself.
- Vinny's byline goes on whatever the panel selects — total editorial delegation.

## Operational Notes

- This panel process applies to all PhantomByte article drafts, not just weekend blitz pieces.
- When Hermes votes, it should report its pick clearly with brief reasoning. No hedging.
- Models that wrote the drafts get a vote too — only Vinny abstains.
