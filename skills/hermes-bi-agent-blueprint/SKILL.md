---
name: bi-agent-blueprint
description: Lead Gen Competitive Intelligence System, Playwright stealth automation for competitor registration, ad capture, advertiser resolution, and decision-maker mapping.
---

# BI Agent Blueprint, Lead Gen Competitive Intelligence System

## Context
Vinny's automated competitive intelligence system. Spins up headless browsers to register on competitor lead-gen sites, captures served ads, traces advertisers, maps decision makers.

## Architecture (per blueprint doc_f20b26e93e4c_bi-agent-blueprint.md)

### Phase 1: Core Infrastructure
- **p01_stealth_browser.py**, Playwright + playwright-stealth + fingerprint rotation (working ✓)
- **p02_pii_generator.py**, Faker + SimpleLogin/SMS-Activate integration (planned)
- **p03_flow_navigator.py**, Multi-step form detection + qualifier answering (working ✓)

### Phase 2: Ad Capture System
- **p04_ad_detector.py**, Creative detection + DOM scanning + screenshot
- **p05_text_extractor.py**, DOM text + OCR fallback + DBA footer extraction
- **p06_link_tracer.py**, Redirect chain capture → final landing URL

### Phase 3: Advertiser Resolution
- **p07_landing_analyzer.py**, Privacy Policy/ToS → legal entity extraction
- **p08_dba_resolver.py**, DBA → company mapping database
- **p09_decision_makers.py**, LinkedIn/Apollo.io → contact discovery

### Phase 4: Data Management
- PostgreSQL schema + S3 creative storage
- Daily CSV/JSON export pipeline

### Phase 5: Anti-Detection Hardening
- Residential proxy rotation (Bright Data / Oxylabs)
- Fingerprint randomization per session
- Behavioral mimicry (Bezier mouse curves, scroll modeling)
- Captcha solving (2Captcha / CapSolver)

### Phase 6: Orchestration & Scaling
- Redis job queue + Celery workers
- Monitoring/alerting dashboard
- Manual review queue

## Critical Implementation Notes

### playwright-stealth API
- The module is `playwright_stealth.stealth.Stealth` (class, not function)
- Apply with: `Stealth(...).apply_stealth_sync(page)`, NOT `stealth(page, ...)`
- `playwright_stealth.stealth` is a **module**, `from playwright_stealth import stealth` gives you the module, not a callable

### Python module naming
- Phase files CANNOT start with digits in import paths
- Use `p01_`, `p02_` prefix for phase modules
- Import via `sys.path.insert(0, str(Path(__file__).parent))` then `from p01_stealth_browser import ...`

### Playwright sync API
- `playwright.sync_api.sync_playwright()`, use inside `with` context manager
- `context.pages[0]`, always grab the existing page from persistent context, or `context.new_page()`
- `page.wait_for_load_state("networkidle")`, preferred over fixed sleeps

### Fingerprint rotation
- Rotate: user-agent, viewport, timezone, locale, canvas noise seed
- Maintain consistency within a single session
- Never repeat the same fingerprint across sessions

### Form field detection
- Strategy: match against `name`, `placeholder`, `aria-label`, `id` attributes
- Build field_map dict keyed by attribute patterns → fake value
- Always human_delay(0.5-1.5s) between field fills

### Behavioral mimicry
- Mouse: Bezier curves, not straight lines; acceleration/deceleration
- Scroll: variable speed, pause to "read", occasional scroll-back
- Between-field: 0.5-2s random delay
- Pre-click: hover + 1-3s delay

## Verified Working Components
- ✓ Browser launch with stealth config
- ✓ Fingerprint rotation (4 UA variants, 4 viewports, 4 timezones)
- ✓ Form field detection + fake PII fill (Faker)
- ✓ Multi-step flow detection (radio/checkbox/dropdown counts)
- ✓ Qualifier selection with random answer strategy
- ✓ Screenshot capture per step (pre/filled/post)
- ✓ JSON session data persistence

## Environment
- Python: `/usr/bin/python3` (3.12.3, WSL)
- pip packages installed to: `~/.local/lib/python3.12/site-packages/`
- Key packages: `playwright==1.58.0`, `playwright-stealth==2.0.3`, `faker==40.15.0`
- Playwright browsers: `~/.cache/ms-playwright/chromium-*` (already cached)
- Working dir: `~/bi-agent/phase1/`
