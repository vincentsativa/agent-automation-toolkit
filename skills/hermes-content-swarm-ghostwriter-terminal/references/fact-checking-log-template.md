# Fact-Checking Log Template

Use this as a running record when Vinny requests fact-checking on an outline. Copy this template, fill it per session, and append to the file.

---

## Session: YYYY-MM-DD -- Article Title

### Claims Verified
| Claim | Source | URL | Status |
|-------|--------|-----|--------|
| Iran struck 3 AWS data centers (UAE/Bahrain) | West Point MWI | https://mwi.westpoint.edu/data-center-warfare-defending-the-key-terrain-of-ai-infrastructure/ | VERIFIED |
| Oracle Dubai data center damaged | West Point MWI | Same | VERIFIED |
| Iran declared 18 tech companies military targets | West Point MWI | Same | VERIFIED |
| Gigawatt power per AI training run | West Point MWI | Same | VERIFIED |
| Digital megacampus concept | West Point MWI | Same | VERIFIED |
| 5M gallons water/day per large DC | West Point MWI | Same | VERIFIED |
| APNIC Blog -- vulnerability mgmt in AI/CI/CD | APNIC Blog search | https://blog.apnic.net/ | LOCATED (exact article not retrievable via direct URL) |

### Claims Unverifiable / Omitted
| Claim | Intended Source | Reason | Adjustment Made |
|-------|---------------|--------|-----------------|
| MIT TR: Amazon engineers terminated for data center concerns | MIT Technology Review | URL 404, search blocked by CAPTCHA, daily data files had no corroboration | Reframed Section 4 around general incentive problem without specific incident |

### Tool Behavior Notes
- Google search: CAPTCHA encountered (IP flagged)
- DuckDuckGo search: Standard HTML version also serves checkbox challenge
- Direct URL access to known publications: Most reliable
- Daily data files (ironpulse/tensorfeed/blogwatcher): Checked but contained no corroboration for unverified claim
- West Point MWI: Fully accessible, all claims confirmed

### Adjustments to Article
- Section 4 reframed from "Amazon specifically threatened engineers" to "the companies whose facilities were struck continue building while internally rewarding growth over risk warnings"
- Specific incident replaced with general pattern description
- Argument preserved, no fabricated data introduced
