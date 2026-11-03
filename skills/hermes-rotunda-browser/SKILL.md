---
name: rotunda-browser
description: "Rotunda — agent-first Firefox fork with stealth browsing, humanized input, and captcha evasion. Installed and ready."
trigger: >
  Load this skill automatically when any task requires: web browsing, browser automation, web
  research, bot-detection evasion, captcha bypass, Playwright, Juggler protocol, or local
  browser navigation. Also load on any prompt that involves searching the web, scraping,
  visiting URLs, or interacting with sites that may give captchas. This is a core infra
  skill — err on the side of loading.
---

# Rotunda Browser Skill

Rotunda (`github.com/MonkeySee-AI/rotunda`) is an agent-first browser forked from
Firefox. It uses the Juggler protocol (not CDP), runs locally on the host machine,
humanizes inputs, and avoids fingerprint detection without lying about its identity.

## Architecture & Key Concepts

- **Forked from Firefox**, not Chromium. Uses Playwright's Firefox Juggler pipeline.
- **Juggler protocol** — browser automation hooks live OUTSIDE the JS context, so
  fingerprinters cannot detect them by patching `navigator.webdriver` or checking
  native-function implementations.
- **No stealth-plugin lies** — Rotunda is honest about its fingerprint (real GPU, real OS,
  real IP from your home network). It only avoids automation signatures.
- **Humanized input** — keystroke cadence with errors/stutters, mouse path prediction
  with overshoot, natural typing speed instead of instant `fill()`.
- **Local-first** — designed to run on your laptop over your home network. NOT for
  cloud crawling (use Browserbase/Browser Use for that).
- **Profile-based agent CLI** — `rotunda agent` commands manage profiles, contexts,
  pages, element refs.

## WSL Setup (current environment)

Rotunda is installed editable from the shared repo into the live PM-managed environment, and its browser binary is cached. Verified live 2026-09-25:

- Python package: `/mnt/c/Users/<user>/workspace/rotunda/pythonlib/` (editable install; on Windows the same repo at `C:\Users\<user>\workspace\rotunda\pythonlib`)
- Git tag: `v0.5.1`, HEAD `e90a7cc`, 0 commits behind origin/main. Newest tag upstream is also v0.5.1 (published 2026-08-31).
- pyproject.toml version: `0.5.1`. Upstream never bumps this field; the tags carry `version = "0.1.0"`. The local 0.1.0 → 0.5.1 edit is required and is expected to show as a dirty working tree — Rotunda builds its download asset name from the installed library version (`pattern: "{name}-{build}-{version}-{os}.{arch}.zip"` in `assets/repos.yml`, read via `installed_library_version()` in `pkgman.py`), so without the bump the version gate silently finds no release. Do not revert it and do not commit it away.
- Browser binary (WSL): `~/.cache/rotunda/browsers/official/0.5.1-154.0.1/rotunda` (Firefox 154.0.1)
- Profiles: `~/.rotunda/agent/profiles/`
- **v0.4.3 (2026-08-14):** One commit over v0.4.2 — restores ink overflow bounds for element snapshots (fixes a regression from #63 where the selector-video crop also contracted still snapshots, dropping shadows). The snapshot path now keeps ink overflow while the video path keeps the border-box crop. Patch-only change to `browserbuild/patches/native-element-snapshot.patch`; no Python API surface change.
- **v0.4.2 (2026-08-14):** New commits added session-history restore (back/forward), native video streaming via WebRTC, Playwright hooks propagated to the remote Juggler bridge, and a grouped-component refactor. The `NewBrowser`/`NewContext` symbols became importable from `rotunda` (the 'unknown location' ImportError was a cwd shadow, not a missing API — see pitfall #8). The API still cannot LAUNCH under Playwright 1.62.0; use the direct-binary method.

**WSL headless requirement:** There is no X server in WSL. Headless mode works
directly (`headless=True`). For headed mode, use `xvfb-run` (already installed).

**Hermes environment path (current):** the agent runs from a PM-managed environment, not a venv under `hermes-agent/`. Resolve it live:

```bash
python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('~/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])"
# append /bin/python  (WSL) or \Scripts\python.exe  (Windows)
```

`hermes doctor` prints the same path ("Runtime venv staged (...) (active in this process)"). The old `~/.hermes/hermes-agent/venv/` still exists but is a legacy leftover and is NOT what the running agent imports.

## Usage — Python API (recommended for Hermes tools)

```python
from playwright.sync_api import sync_playwright
from rotunda import NewBrowser, NewContext

with sync_playwright() as playwright:
    # headless=True works in WSL with no X server
    browser = NewBrowser(playwright, headless=True)
    context = NewContext(browser)
    page = context.new_page()

    page.goto("https://example.com", wait_until="domcontentloaded")
    text = page.locator("h1").first.inner_text()
    print(text)

    browser.close()
```

The API is a drop-in for Playwright's standard `chromium.launch()` / `chromium.launch_persistent_context()`
via `NewBrowser` / `NewContext` wrappers. All Playwright methods (`locator`, `click`, `fill`,
`inner_text`, `goto`, `screenshot`, `wait_for_selector`, etc.) work normally.

## Usage — Agent CLI (manual control)

```bash
# Create a profile (one-time)
uvx rotunda agent new-profile --name my-profile

# Create browser context (launches Rotunda browser)
uvx rotunda agent new-context my-profile

# Navigate to a page (page index from new-context output)
uvx rotunda agent navigate 2 https://example.com

# Describe the page (gets element refs like @e1, @e5)
uvx rotunda agent describe 2

# Interact via refs
uvx rotunda agent click @e7
uvx rotunda agent fill @e12 "search query"
uvx rotunda agent press @e12 Enter

# Screenshot
uvx rotunda agent screenshot 2 --full-page

# Close when done
uvx rotunda agent stop 2
```

Note: The agent CLI requires a running X server or `xvfb-run` on WSL for headed
mode. Prefer the Python API with `headless=True` from within Hermes.

## Pitfalls

1. **X Server / DISPLAY**: In WSL without an X server, always use `headless=True`
   in the Python API. Rotunda's agent CLI (`rotunda agent new-context`) currently
   only supports headed mode — use the Python API instead.
2. **Profile directory growth**: Rotunda profiles persist browser data in
   `~/.rotunda/agent/profiles/`. Periodic cleanup may be needed.
3. **Not for cloud crawling**: README explicitly recommends Browserbase or
   ScrapingBee for cloud/crawling workloads. Rotunda is for local agent browsing.
4. **Port conflicts**: Juggler uses random ports. No manual port config needed.
5. **Python API vs CLI**: The Python API (`NewBrowser`/`NewContext`) is a
   Playwright wrapper and supports all Playwright options. The CLI exposes
   Rotunda-specific features (element refs, page diff tracking) but needs
   `xvfb-run` on WSL.
6. **Install to the wrong environment**: After a git pull, reinstall into the
   RESOLVED live interpreter (see "Hermes environment path" above), not into
   `~/.hermes/hermes-agent/venv` — that legacy venv still exists on WSL but is
   not what the running agent imports, and on Windows it does not exist at all.
   Using `pip install --break-system-packages` installs to the system
   site-packages, invisible to every Hermes environment.
7. **Always verify with a smoke test**: After updating, run the verification
   script. Do NOT report success without actually exercising the browser. The
   first launch auto-downloads the matching browser binary — if the version
   gate is wrong, it will fail with `MissingRelease`.
8. **`NewBrowser`/`NewContext` import fails with 'unknown location'**: The
   `from rotunda import NewBrowser, NewContext` pattern raises
   `ImportError: cannot import name 'NewBrowser' from 'rotunda' (unknown
   location)`. **Root cause (confirmed 2026-09-25): a directory named `rotunda`
   in the current working directory.** An empty `~/rotunda` existed on WSL and
   became a namespace package that shadowed the real one whenever Python
   started from `~`; `import rotunda` then reported
   `__path__ = ['~/rotunda']` and `__file__ = None`. The empty
   directory has been removed. Check for this shadow before blaming the
   package:
   ```bash
   cd /tmp && python3 -c "import rotunda; print(rotunda.__file__)"
   # expect: /mnt/c/Users/<user>/workspace/rotunda/pythonlib/rotunda/__init__.py
   ```
   If the import is clean from `/tmp` but fails from your cwd, the cwd is the
   problem, not the install. The direct-binary method below still remains the
   reliable path for actually LAUNCHING the browser (see pitfall #9).
   **UPDATE (verified 2026-09-25):** the import now works on both WSL and
   Windows, but under Playwright 1.62.0 the API launch fails at
   `NewContext()` with
   `Protocol error (Browser.setDefaultViewport): Found property
   "<root>.viewport.isMobile" - false which is not described in this scheme`.
   `no_viewport=True` is worse (`"deviceScaleFactor" option is not supported
   with null "viewport"`). The direct-binary method with
   `no_viewport=True` on `new_context()` remains the only working path.
9. **`no_viewport=True` required with Rotunda binary**: When launching Rotunda's
   Firefox via `executable_path`, calling `browser.new_context()` without
   `no_viewport=True` fails with:
   `Protocol error (Browser.setDefaultViewport): Found property "<root>.viewport.isMobile" - false which is not described in this scheme`
   This is a Juggler protocol quirk — Rotunda's Firefox doesn't support the
   `isMobile` viewport property that Playwright's stock Firefox expects. Always
   pass `no_viewport=True` to `new_context()` when using the Rotunda binary.
   **Caveat:** Even Rotunda's Firefox gets 429'd by Google Trends — use
   pytrends for Trends data (see keyword-research-seo skill).
10. **No Windows browser binary — confirmed by direct test 2026-09-25**:
    Rotunda's GitHub releases only ship Linux (x86_64 + arm64) and macOS (arm64).
    There is no Windows build. The v0.5.1 release assets are exactly
    `rotunda-154.0.1-0.5.1-lin.arm64.zip`,
    `rotunda-154.0.1-0.5.1-lin.x86_64.zip`, and
    `rotunda-154.0.1-0.5.1-mac.arm64.zip`. The `NewBrowser` API on Windows
    fails with `MissingRelease: No matching release found for Rotunda 0.5.1
    on win x86_64`.
    **The copied-WSL-ELF workaround does NOT work.** `C:\Users\<user>\.cache\rotunda\browsers\official\0.5.1-154.0.1\` does contain the Linux
    binary (verified: `ELF 64-bit LSB pie executable, x86-64`), but launching it
    through Playwright on Windows fails outright:
    `Error BrowserType.launch: Failed to launch: Error: spawn ...\rotunda ENOENT`.
    **Workaround**: use stock Playwright Firefox on Windows
    (`python -m playwright install firefox`), verified loading
    `https://example.com` on 2026-09-25. Do not claim Rotunda works on Windows.
11. **Version check against origin**: To confirm the local repo is up to date
    without pulling, use:
    ```bash
    cd /path/to/rotunda && git fetch origin && git log --oneline HEAD..origin/main | wc -l
    ```
    Output `0` means no new commits. Then check the tag with `git describe --tags`.

## Complementary Skill: Scrapling

Scrapling and Rotunda form a **tiered scraping stack** — always consider using them together when a target site has anti-bot protection:

1. **Try Scrapling's StealthyFetcher first** — handles 90%+ of Cloudflare/Turnstile targets with a single HTTP call. Fast, lightweight, no browser overhead.
2. **Escalate to Rotunda** — when Scrapling gets 403/429/CAPTCHA, launch Rotunda. Its Firefox-Juggler pipeline evades automation detection that Playwright-based `StealthyFetcher` can't.
3. **Combine both** — use Rotunda for the browser session (fingerprint-evading navigation, humanized input, CAPTCHA resolution) and feed the resulting HTML back into Scrapling's `Adaptor` parser for adaptive CSS extraction and crawling.

Scrapling also has a full Spider framework (`CrawlSpider`, `SitemapSpider`, `LinkExtractor`) that works well for multi-page crawling tasks done through Rotunda pages.

## Updating Rotunda

When a new Rotunda version is released:

```bash
# 0. First, check if there are actually new commits (avoid unnecessary pulls)
cd /mnt/c/Users/<user>/workspace/rotunda
git fetch origin
git log --oneline HEAD..origin/main | wc -l
# If output is 0, you're already up to date — skip the rest.

# 1. Git pull the repo
cd /mnt/c/Users/<user>/workspace/rotunda && git pull origin main

# 2. Re-apply the version bump in pythonlib/pyproject.toml to match the new tag.
#    Upstream tags carry version = "0.1.0"; the asset-name pattern and the
#    release gate both read the INSTALLED library version, so a stale value
#    makes the browser download fail with MissingRelease. Keep the git tag,
#    pyproject version, and installed dist-info version equal.

# 3. Resolve both live interpreters, then install into each
WSL_PY=$(python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('~/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])")/bin/python
WIN_PY=$(python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('/mnt/c/Users/<user>/AppData/Local/hermes/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])")/Scripts/python.exe

uv pip install -e /mnt/c/Users/<user>/workspace/rotunda/pythonlib --force-reinstall --python "$WSL_PY"
"$WIN_PY" -m pip install -e C:\\Users\\<user>\\workspace\\rotunda\\pythonlib --force-reinstall

# 4. Rotunda's playwright<=1.59.0 pin pulls Playwright DOWN and breaks
#    Scrapling's fetchers extra. The pin is soft — restore the environment's
#    own Playwright (1.62.0) after installing Rotunda:
uv pip install "playwright==1.62.0" --python "$WSL_PY"
"$WIN_PY" -m pip install "playwright==1.62.0"

# 5. On Windows, reinstall the Playwright Firefox browser if the version changed
"$WIN_PY" -m playwright install firefox
```

**CRITICAL:** Use `uv pip install` targeting the RESOLVED live interpreter, NOT `pip install --break-system-packages`. The latter installs to the system site-packages where no Hermes environment can see it. The editable install from the repo picks up any new/changed Python modules.

### What to verify after update
- `git log --oneline -5` — confirm the new commits are pulled
- `git tag -l | tail -5` — confirm the version tag exists
- `git describe --tags` — confirm HEAD sits exactly on the newest tag (live 2026-09-25: `v0.5.1`)
- The installed dist-info version matches the tag: expected `rotunda-<tag>.dist-info` in the environment's site-packages
- The pip reinstall may pull Playwright down to 1.59.0 (Rotunda's soft pin) — restore 1.62.0 afterward, it is the environment's locked version
- The browser cache directory name is `<library version>-<firefox build>`, e.g. `0.5.1-154.0.1`

### Version tagging
Rotunda uses semver tags (v0.3.2, v0.5.1, etc.), and the newest upstream tag as of 2026-09-25 is `v0.5.1`. The tag is what the browser release is built from, but the ASSET NAME and the release gate read the INSTALLED library version, so `pyproject.toml` must carry the same number (upstream tags ship `version = "0.1.0"` — the local bump is deliberate and must be kept). Check what you are on with:
```bash
git describe --tags
git tag -l | tail -5
```
Then confirm the installed distribution matches: look for `rotunda-<version>.dist-info` in the environment's site-packages.

The version gate itself lives in `pkgman.py` (`is_version_supported()` compares the GitHub release version against `installed_library_version()`), and the asset name pattern is `"{name}-{build}-{version}-{os}.{arch}.zip"` in `pythonlib/rotunda/assets/repos.yml`. See `references/version-mismatch-debug.md` for the failure mode when the two disagree.

## Verification

Run a smoke test from the resolved live interpreter — do NOT report success without running this.

**Run it from a neutral cwd such as `/tmp`.** A directory named `rotunda` in the current working directory becomes a namespace package that shadows the real one and produces a false `ImportError: cannot import name 'NewBrowser' from 'rotunda' (unknown location)`. That is a cwd artifact, not a broken install.

### Preferred: Direct Playwright + Rotunda binary (the only path that works under Playwright 1.62.0)

```bash
cd /tmp
python3 -c "
import os
from playwright.sync_api import sync_playwright
ROTUNDA_BIN = os.path.expanduser(
    '~/.cache/rotunda/browsers/official/0.5.1-154.0.1/rotunda'
)
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True, executable_path=ROTUNDA_BIN)
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto('https://example.com')
    print('Rotunda OK:', page.title(), browser.version)
    browser.close()
"
```

Expected output: `Rotunda OK: Example Domain 154.0.1-0.5.1`

### Fallback: NewBrowser/NewContext API (imports fine, but the launch fails under Playwright 1.62.0)

```bash
cd /tmp
python3 -c "
from playwright.sync_api import sync_playwright
from rotunda import NewBrowser, NewContext
with sync_playwright() as p:
    b = NewBrowser(p, headless=True)
    c = NewContext(b)
    page = c.new_page()
    page.goto('https://example.com')
    print('Rotunda OK:', page.title())
    b.close()
"
```

Verified live on 2026-09-25: the import succeeds, but `NewContext(b)` raises `Protocol error (Browser.setDefaultViewport): Found property "<root>.viewport.isMobile" - false which is not described in this scheme`. Passing an explicit `viewport=` does not help, and `no_viewport=True` fails earlier with `"deviceScaleFactor" option is not supported with null "viewport"`. Until Rotunda's Juggler bridge supports the viewport properties Playwright 1.62.0 sends, use the preferred direct-binary method. Do not substitute a fabricated result.

### Windows smoke test

On Windows, the Rotunda browser binary is not available (no Windows build; the
copied Linux ELF does not launch — see pitfall #10). Use stock Playwright Firefox
instead. The Rotunda Python API (`NewBrowser`/`NewContext`) fails with
`MissingRelease` on Windows — use direct Playwright Firefox launch:

```powershell
python -m playwright install firefox
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    context = browser.new_context(no_viewport=True)
    page = context.new_page()
    page.goto('https://example.com')
    print('Stock Firefox OK:', page.title())
    browser.close()
"
```
