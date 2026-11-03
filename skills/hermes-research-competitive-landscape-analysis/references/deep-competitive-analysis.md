# Deep Competitive Analysis, Operating Prompt (v2)

> **Source:** Archived skill `deep-competitive-analysis` (formerly at `research/deep-competitive-analysis/SKILL.md`)
> **Purpose:** PhantomByte-specific business intelligence sweeps, business models, growth engines, unfair advantages, trajectory signals, and vulnerability detection
> **Runs:** Monday, Wednesday, Thursday at 10:45 AM EDT
> **Original Author:** Vinny Barreca (Frank persona)

---

This reference contains the full "Why them?" competitive intelligence framework originally defined in `deep-competitive-analysis`. Use it when you need to conduct a deep business-intelligence-level sweep of specific competitive targets, not just landscape mapping, but structured interrogation of how each target makes money, grows, and where they're vulnerable.

---

## The "Why Them?" Framework, Every Target, Every Run

Answer each question. If you can't find the answer, say "unknown", don't guess.

### 1. Business Model, How do they make money?
```
primary_revenue_stream: [ads | subscriptions | products | services | consulting | affiliate | courses | sponsorships | donations | unknown]
secondary_streams: [...]
estimated_annual_revenue: educated guess based on public signals (subscriber counts, pricing, ad rates)
revenue_concentration: [single_stream | diversified], one stream or multiple?
pricing_model: if subscription/product, what do they charge?
growth_stage: [early | growth | maturity | decline], based on hiring, product launches, content frequency
monetization_notes: one sentence summary
```

### 2. Growth Engine, How did they get big?
```
primary_acquisition_channel: [SEO | social | referral | paid_ads | partnerships | PR | newsletter | product_led | unknown]
estimated_traffic: rough traffic level (small <10k/mo | medium <100k | large <1M | massive 1M+)
known_growth_tactics: specific things they did/do to grow
initial_traction: how they got their first users/customers (if known)
distribution_advantage: what distribution moat do they have?
growth_notes: one sentence
```

### 3. Unfair Advantage, Why can't everyone do this?
```
moat_type: [brand | network_effects | proprietary_data | distribution_lock | technical_secret | audience_trust | first_mover | cost_advantage | none_visible]
moat_strength: [weak | moderate | strong | unassailable]
copyable_components: what parts COULD PhantomByte replicate?
uncopyable_components: what CAN'T be copied?
advantage_notes: one sentence
```

### 4. Operations, How do they run?
```
team_size: [solo | small (<5) | medium (5-20) | large (20+) | unknown]
founder_public_profile: [high | medium | low | unknown], are they personally the brand?
tech_stack_signals: any clues about tools/platforms they use
publishing_operation: [manual | semi-automated | fully-automated | unknown]
outsourcing_signals: do they use freelancers, agencies, syndication?
ops_notes: one sentence
```

### 5. Trajectory, Are they winning or fading?
```
trajectory: [accelerating | steady | plateauing | declining | unclear]
trajectory_evidence: specific signals that support this assessment
recent_changes: any pivots, launches, price changes, staff changes in last 90 days
innovation_pace: [fast | moderate | slow | stopped], new features/products/courses?
trajectory_notes: one sentence
```

### 6. Vulnerabilities, Where can they be beaten?
```
biggest_risk: single biggest existential or competitive threat to them
single_point_of_failure: one thing that, if it broke, kills the business
audience_fatigue_signals: declining engagement, repeat complaints, churn risk
revenue_vulnerability: what happens if their primary stream dries up?
copyable_by_phantombyte: [yes | no], can PhantomByte do what they do, but better?
attack_vector: one sentence on how PhantomByte could take share from them
```

### 7. What They DON'T Do (The Missed Opportunities)
```
conspicuous_absences: obvious things they should be doing but aren't
audience_needs_not_met: what their audience clearly wants that they ignore
format_pioneering: formats/mediums they haven't touched
monetization_gaps: obvious revenue streams they've left on the table
phantombyte_opening: one sentence, what's the specific opening for PhantomByte here?
```

---

## Targets

### Tier 1, Every Run
| Target | URL |
|--------|-----|
| Simon Willison | simonwillison.net |
| Pieter Levels | levels.io |
| Brett / DesignJoy | designjoy.co |
| VentureBeat | venturebeat.com |
| The Rundown AI | therundown.ai |

### Tier 2, Every Run (lighter scan)
| Target | URL |
|--------|-----|
| Lilian Weng | lilianweng.github.io |
| Dan Luu | danluu.com |
| Marc Lou | marclou.com |
| Lenny Rachitsky | lennysnewsletter.com |
| Swyx / Latent Space | swyx.io |
| MarkTechPost | marktechpost.com |
| Towards AI | towardsai.net |
| Towards Data Science | towardsdatascience.com |
| Ben's Bites | bensbites.com |

### Supplementary
Ollama Blog (ollama.com/blog), PerformCB (performcb.com, login)

---

## Report Output Format

### Raw Data
Save JSON to: `~/data/scrapling/deep/YYYY-MM-DD-raw.json`

### Intelligence Brief
Save to: `/mnt/c/Users/<user>/workspace/data/scrapling/reports/competitive-deep-dive-YYYY-MM-DD.md`

Format:
```
# Competitive Business Intelligence, [Day, Month DD, YYYY]

## TOP 3 INTEL SIGNALS (what Vinny needs to know NOW)
1. [Target], [one-line intel]
2. [Target], [one-line intel]
3. [Target], [one-line intel]

## TIER 1, FULL PROFILES
### [Target Name]
**Business Model:** ...
**Growth Engine:** ...
**Unfair Advantage:** ...
**Trajectory:** ...
**Vulnerability:** ...
**The Miss:** What they're not doing that they should be
**PhantomByte Move:** (copy | avoid | attack | ignore), one sentence

### [Next Target]
...

## TIER 2, QUICK HITS
### [Target]: [Business Model] | [Growth Engine] | [Vulnerability] | PhantomByte Move: ...

## ATTACK VECTOR SUMMARY
Ranked by potential payout:
1. [HIGH] Target + vulnerability + PhantomByte play
2. [MEDIUM] ...
3. [LOW] ...

## MISSED OPPORTUNITIES COMPENDIUM
Things our competitors are NOT doing that we absolutely should.
```

---

## Data Collection Methodology

### Primary: Scrapling
```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch(url, headless=True, network_idle=True)
```

### What to look for on each page:
- **About page**, founder story, team size, origin story (hints at initial traction)
- **Pricing page**, revenue model, tiers, positioning
- **Homepage**, value proposition, what they lead with, CTA (growth engine hint)
- **Blog/Content**, frequency tells you if they're active or coasting
- **Jobs/Careers**, hiring = growth, no hiring = plateau or solo
- **Footer**, ad networks, affiliate disclosures, sponsors
- **Social links**, follower counts, engagement levels (trajectory signal)
- **Testimonials/case studies**, target market, proof points

### Check third-party signals:
- Crunchbase / AngelList for funding, team size, founding date
- Similarweb for traffic estimates (if accessible)
- Wayback Machine for historical changes
- Twitter/LinkedIn for founder activity and audience engagement

---

## Anti-False-Completion Check

- [ ] Raw JSON file exists and is non-empty
- [ ] All Tier 1 targets profiled
- [ ] Every target has ALL 7 framework sections answered (even if "unknown")
- [ ] Report has: Top 3 Signals, Tier 1 Full Profiles, Tier 2 Quick Hits, Attack Vector Summary, Missed Opportunities
- [ ] PhantomByte Move is assigned per target (copy | avoid | attack | ignore)

---

## Edge Cases

- **Paywalled:** Collect what's public. Note "gated."
- **No pricing page:** That itself is a signal (likely ads or consulting)
- **Single founder, no team:** High vulnerability, they ARE the business
- **No visible monetization:** Either they're VC-funded, pre-revenue, or making money invisibly (consulting, backchannel deals)
- **Site down:** Log it. Skip. Max 2 retries.
- **Same as last run:** Log "no change detected", that's useful data (stagnation signal)

---

## Scrapling Pipeline (Operational Counterpart)

### Frank's Scrapling Pipeline, Operational Competitor Monitoring

A Scrapling-based competitor intelligence pipeline for PhantomByte.

**Tool: Scrapling** (installed in WSL venv, `scrapling[fetchers] v0.4.10`)
```python
from scrapling.fetchers import StealthyFetcher
sf = StealthyFetcher()
page = sf.fetch(url, headless=True, network_idle=True)
```

**Data to collect per target:** new_content, structural_changes, seo_patterns, monetization_signals, competitive_intel

**Frequency:** Daily (Simon Willison + Ollama Blog, Mon-Fri), Weekly (all targets, Monday 1 PM EDT)

**Output paths:**
- Daily raw: `~/data/scrapling/raw/daily-YYYY-MM-DD.json`
- Weekly raw: `~/data/scrapling/raw/weekly-YYYY-MM-DD.json`
- Weekly brief: `/mnt/c/Users/<user>/workspace/data/scrapling/weekly-brief-YYYY-MM-DD.md`

### BI Agent Blueprint, Lead Gen Intelligence Automation

Playwright-based stealth automation for competitor registration, ad capture, and decision-maker mapping. Architecture:

**Phase 1 (Core):** `p01_stealth_browser.py` (Playwright + stealth + fingerprint rotation), `p02_pii_generator.py`, `p03_flow_navigator.py`
**Phase 2 (Ad Capture):** `p04_ad_detector.py`, `p05_text_extractor.py`, `p06_link_tracer.py`
**Phase 3 (Resolution):** `p07_landing_analyzer.py`, `p08_dba_resolver.py`, `p09_decision_makers.py`

**Critical Playwright-stealth API note:**
- Module is `playwright_stealth.stealth.Stealth` (class, not function)
- Apply with: `Stealth(...).apply_stealth_sync(page)`, NOT `stealth(page, ...)`
- `playwright_stealth.stealth` is a **module**, not a callable

**Python phase file naming:** Phase files cannot start with digits in import paths, use `p01_`, `p02_` prefix and import via `sys.path.insert(0, str(Path(__file__).parent))`

**Environment:** `/usr/bin/python3` (3.12.3), packages at `~/.local/lib/python3.12/site-packages/`, working dir `~/bi-agent/phase1/`

### Scrapling vs. Playwright Decision

Use **Scrapling** for: competitor content monitoring, news feeds, static pages, Cloudflare/Turnstile-protected sites (its specialty)
Use **Playwright (bi-agent)** for: multi-step form registration flows, ad capture behind login walls, advertiser resolution requiring interaction