# Fact-Checking Pitfall: Product Claim Drift

## What It Is

Outlines and daily data files often cite specific prices, lifetime licenses, or availability claims that become stale as products pivot their business model. The outline says "$19.99 lifetime license." The live vendor site says "$14.99/year subscription." The live source wins. The outline is stale.

## Why It Matters

Vinny said "information included in your article MUST be true." Propagating an outdated price or licensing claim is false information, even if it appeared in a trusted daily data file. The vendor's site is the primary source for its own pricing.

## How to Handle It

1. **Always check the live vendor site** for any tool that has a pricing/licensing component. Navigate directly to the product's homepage or pricing page.
2. **When the live source contradicts the outline, the live source wins.**
3. **Do not attempt to reconcile conflicting sources by guessing or averaging.** There is no "$17.50 hybrid license." There is only what the vendor currently charges.
4. **Omit the outdated claim rather than propagating it.** If the pricing detail is not central to the argument, drop it. If it is central, describe the model generically ("a paid subscription" or "a one-time license, subject to change") rather than citing a specific outdated number.
5. **Do not mark unverified claims as "reportedly" or "allegedly" to keep them in.** Vinny's instruction is "information MUST be true." "Reportedly $19.99" when the site says $14.99 is still false.

## Example from Session 2026-07-04 (Article 119)

**Outline claim:** "LockIn MCP: $19.99 lifetime license."

**Live vendor site (lockinmcp.com):** "Pro subscription — $14.99/year" with monthly and yearly toggle. No lifetime license mentioned.

**Resolution:** The "$19.99 lifetime license" claim was omitted from the article. LockIn MCP was described as "a shipping product" and "consumer-grade system administration" without citing a specific price.

## Related Pitfalls

- **Vendor blog URL slug mismatch** — especially NVIDIA. See `references/google-trends-fallback.md` for vendor URL verification patterns.
- **GitHub stats are live, not static** — star counts and forks change hourly. Always pull fresh.
- **Verification tool failures** — see `references/fact-checking-pattern.md` in ghostwriter-terminal for the full workflow.
