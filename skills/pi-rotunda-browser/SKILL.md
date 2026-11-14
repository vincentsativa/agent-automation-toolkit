---
name: rotunda-browser
description: "Rotunda, fingerprinted Firefox fork driven through Playwright's Juggler, plus Scrapling. Covers where it runs (InstaBox box, WSL), where it cannot run (native Windows), the four local fixes that make it launch, and the verification commands."
trigger: >
  Load this skill automatically when any task needs web browsing, browser automation, web
  research, bot-detection evasion, Playwright, Juggler, or local browser navigation, and on
  any rotunda or scrapling error. Core infra skill, err on the side of loading.
---

# Rotunda browser stack, all hosts

Rotunda is a patched, fingerprinted Firefox build (uBlock Origin bundled) driven through Playwright's Firefox/Juggler API. Scrapling is the HTTP fetcher for plain page reads. Separate tools: Scrapling for ordinary fetches, Rotunda when a site blocks, needs JS, or needs a real fingerprint.

Everything below was run and verified on 2026-11-13. Nothing here is a guess.

## Where it works, right now

| Host | rotunda | scrapling | Notes |
|---|---|---|---|
| InstaBox `freemachine` (Linux, `/data/home`, python3.13) | WORKS, build `0.5.1-154.0.1` | 0.5.1 | CLI and Python API, playwright 1.64.1, browserforge data 0.16.0, all fixes applied |
| WSL Ubuntu (user `vincent`, python3.12) | WORKS, build `0.5.1-154.0.1` | 0.5.1 | CLI and Python API, playwright 1.63.0, browserforge data 0.15.0, all fixes applied |
| Native Windows | CANNOT RUN. Package imports, no browser build exists. | 0.5.1, works | Release assets are Linux x86_64/arm64 + macOS arm64 only. `rotunda sync` finds 0 versions, `rotunda active` says `(not fetched)`, `NewBrowser` raises `MissingRelease: No matching release found for Rotunda 0.5.1 on win x86_64`. Use WSL. |

Do not try to make rotunda launch natively on Windows. A copied Linux ELF in `C:\Users\<user>\.cache\rotunda\...` fails with `spawn ... ENOENT`, and there is no Windows asset to fetch. On Windows, run it through WSL; use stock Playwright Firefox (`python -m playwright install firefox`) only if you need a browser without rotunda.

## Smoke test, per host

InstaBox box:

```bash
export PATH=$HOME/.local/bin:$PATH
rotunda active                       # official/stable/0.5.1-154.0.1
python3 -c "from scrapling.fetchers import Fetcher; print('scrapling', Fetcher.get('https://example.com',timeout=20).status)"
```

WSL:

```bash
wsl -u vincent -- bash .../<user>/workspace/rotunda/run-rotunda.sh active
```

Full browser proof, on any host that has a build:

```bash
rotunda agent new-profile --name chk --headless     # prints prof_xxxx
rotunda agent new-context prof_xxxx                 # prints ctx_xxxx and page_xxxx
rotunda agent navigate page_xxxx https://example.com
rotunda agent extract page_xxxx --format text
rotunda agent describe page_xxxx
rotunda agent stop prof_xxxx
```

References are strings, not indexes: `new-page` takes a `ctx_` id, `navigate`/`extract`/`describe` take a `page_` id. Passing `0` returns `Unknown context reference: 0`.

Windows Scrapling proof (interpreter matters, see below):

```bash
"/c/Users/<user>/AppData/Local/Programs/Python/Python311/python.exe" -c "from scrapling.fetchers import Fetcher; print(Fetcher.get('https://example.com',timeout=20).status)"
```

## The four fixes that make it launch

The shipped pairing rotunda 0.5.1 + browser build 154.0.1 does not work out of the box with any current Playwright. If a host starts failing, work down this list.

### 1. Browserforge fingerprint data 0.16.0

Symptom: `No headers based on this input can be generated. Please relax or change some of the requirements you specified.` from `browserforge/headers/generator.py`.

Cause: `apify_fingerprint_datapoints` 0.15.0 lacks fingerprint rows for this build.

```bash
python3 -m pip install --user --break-system-packages -U apify_fingerprint_datapoints
python3 -c "import importlib.metadata as m; print(m.version('apify_fingerprint_datapoints'))"
```

InstaBox is on 0.16.0. WSL still runs 0.15.0 and its launches work, so this one is host-dependent; upgrade it if you see the header error.

### 2. The build's viewport schema must accept `isMobile`

Symptom: `Protocol error (Browser.setDefaultViewport): ERROR: failed to call method 'Browser.setDefaultViewport' ... Found property "<root>.viewport.isMobile" - false which is not described in this scheme`.

Cause: Playwright 1.61+ sends `isMobile`; the build's juggler schema in `Protocol.js` never declares it, so validation rejects the call. This is the error the old notes blamed on "the API cannot launch", and why `no_viewport=True` was needed.

Fix: add the field to `pageTypes.Viewport` inside the build's `omni.ja`. Back up first; the backup names are `omni.ja.bak-isMobile`.

```python
import zipfile, pathlib, shutil
p = pathlib.Path("/data/home/.cache/rotunda/browsers/official/0.5.1-154.0.1/omni.ja")   # WSL: ~/.cache/...
bak = p.with_suffix(".ja.bak-isMobile")
if not bak.exists(): shutil.copy2(p, bak)
src = zipfile.ZipFile(bak); target = "chrome/juggler/content/protocol/Protocol.js"
d = src.read(target).decode()
old = """pageTypes.Viewport = {
  viewportSize: pageTypes.Size,
  deviceScaleFactor: t.Optional(t.Number),
};"""
new = """pageTypes.Viewport = {
  viewportSize: pageTypes.Size,
  deviceScaleFactor: t.Optional(t.Number),
  isMobile: t.Optional(t.Boolean),
};"""
assert d.count(old) == 1
d = d.replace(old, new)
tmp = p.with_suffix(".ja.new")
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
    for it in src.infolist():
        buf = src.read(it.filename)
        if it.filename == target: buf = d.encode()
        out.writestr(it, buf)
tmp.replace(p)
```

With this in place `browser.new_context()` works normally, no `no_viewport` needed. Without it, the fallback is `no_viewport=True` on the context (that fallback still works).

### 3. Drop `--window-size` from persistent-context args or the launch hangs

Symptom: no error at all. `BrowserType.launch_persistent_context` sits until timeout. Bisect result: the full option set launches in 1.2s; the same set with `args: ["--window-size","1932,1014"]` never returns. This is what made `rotunda agent new-context` fail while the library looked healthy.

Fix in `rotunda.utils.persistent_context_options()`, just before `return result`:

```python
    # Local fix: the shipped 154.0.1 browser never completes a persistent-context
    # launch while "--window-size" is in args. viewport above already sizes it.
    if isinstance(result.get("args"), list) and "--window-size" in result["args"]:
        out = []
        skip = False
        for x in result["args"]:
            if x == "--window-size":
                skip = True
                continue
            if skip:
                skip = False
                continue
            out.append(x)
        result["args"] = out
    return result
```

Patched files, backups `utils.py.bak-args`:
- Source tree (Windows + WSL both import this): `C:\Users\<user>\workspace\rotunda\pythonlib\rotunda\utils.py`
- InstaBox site-packages copy: `/data/home/.local/lib/python3.13/site-packages/rotunda/utils.py`

### 4. Playwright must be 1.61 through 1.64

rotunda's metadata pins `playwright<=1.59.0,>=1.51.0`. That pin is wrong for this build:

- 1.51 to 1.60: browser starts, logs `Juggler listening to the pipe`, then the launch never completes. Tested 1.56, 1.57, 1.58, 1.59, 1.60, all hang.
- 1.61 to 1.64: handshake works. Only usable window.
- 1.65+: `import rotunda` fails with `ModuleNotFoundError: playwright._impl._js_handle`.

InstaBox runs 1.64.1, WSL runs 1.63.0. Any pip resolve of rotunda's dependencies silently downgrades Playwright to 1.59 and re-breaks the launch. After such an install, put it back with the interpreter that runs the agent (see install rules below), e.g.:

```bash
python3 -m pip install --user --break-system-packages "playwright==1.64.1"
```

## Repo, install and the version bump

Rotunda is installed editable from the shared checkout:

```
C:\Users\<user>\workspace\rotunda\pythonlib\rotunda\      git clone of MonkeySee-AI/rotunda, tag v0.5.1
```

Windows Python and WSL python both import it from there, so a library edit serves both hosts. Browser builds are per host, under `~/.cache/rotunda/browsers/official/<build>/`.

`pythonlib/pyproject.toml` carries a deliberate local bump to `version = "0.5.1"` while upstream tags carry `0.1.0`. Rotunda builds its download asset name from the installed library version, so without the bump the release gate finds nothing and the browser download fails with `MissingRelease`. The dirty `pyproject.toml` in the working tree is expected. Do not revert it.

Install into the interpreter the agent actually runs, not the system one:

```bash
python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('~/.hermes/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])"
```

That path + `/bin/python` (WSL) or `\Scripts\python.exe` (Windows) is the live runtime. `pip install --break-system-packages` writes to system site-packages, which no Hermes environment reads. Prefer `uv pip install -e <repo>/pythonlib --python "<resolved python>"`.

## Using rotunda from Windows or from the fifi profile

There is no Windows browser build, so Windows agents shell into WSL through the wrapper:

```bash
wsl -u vincent -- bash .../<user>/workspace/rotunda/run-rotunda.sh active
wsl -u vincent -- bash .../<user>/workspace/rotunda/run-rotunda.sh agent new-context prof_xxxx
```

Put commands in a script file instead of passing inline `bash -lc "..."`. The Windows PATH WSL inherits contains `Program Files (x86)`, and the parentheses break the quoting through `wsl.exe` (`bash: -c: line 1: syntax error near unexpected token '('`) before anything runs.

`rotunda test` launches the browser and builds a fingerprinted context fine on a patched host, then dies at `Opening Playwright inspector...` with `EPIPE` because the inspector needs a terminal. That last failure is normal outside an interactive shell and does not mean the browser is broken.

## Python API

With fix 2 applied, the plain shape works: no `no_viewport` workaround, no manual `executable_path`.

```python
from playwright.sync_api import sync_playwright
import rotunda                                  # import first: installs driver hooks
from rotunda import NewBrowser

with sync_playwright() as pw:
    browser = NewBrowser(pw, headless=True)      # uses the active rotunda build
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto("https://example.com", wait_until="domcontentloaded")
    print(page.title())
    browser.close()
```

Async shape:

```python
from rotunda import AsyncRotunda, AsyncNewContext

async with AsyncRotunda(headless=True) as browser:
    ctx = await AsyncNewContext(browser)
    page = await ctx.new_page()
    await page.goto("https://example.com")
```

`NewContext(browser)` / `AsyncNewContext(browser)` wrap a context with rotunda's fingerprint settings. If a host has not had fix 2 applied and you cannot patch it, `ctx = browser.new_context(no_viewport=True)` is the older workaround.

## Agent CLI

```bash
rotunda version      # package, browser, storage
rotunda active       # active version spec
rotunda list all     # local and remote versions
rotunda fetch [SPEC] # install active, or a pinned spec
rotunda set official/stable
rotunda agent ...    # profiles, contexts, pages, refs
```

`rotunda agent` subcommands: `new-profile`, `new-context`, `new-page`, `navigate`, `describe`, `extract`, `click`, `fill`, `press`, `check`, `hover`, `drag`, `dialog`, `downloads`, `screenshot`, `info`, `back`, `forward`, `close-page`, `stop`. Refs from `describe` look like `[ocsmuu6f] - link "Learn more" <a>` and are passed back to `click`/`fill`.

## Scrapling, and the interpreter rule on Windows

Scrapling is installed in the system Python on Windows, not in Hermes's bundled interpreter. Find the one that has it before blaming the install:

```bash
for p in /c/Users/<user>/AppData/Local/Programs/Python/Python3*/python.exe; do "$p" -c "import scrapling" 2>/dev/null && echo "HAS SCRAPLING: $p"; done
```

Verified: `Python311` has scrapling 0.5.1 and rotunda 0.5.1 (library only); `Python312` has neither. On Linux hosts plain `python3` has it.

```python
from scrapling.fetchers import Fetcher
page = Fetcher.get("https://example.com", timeout=20)
print(page.status, len(page.get_all_text() or ""))
```

`get_all_text()` for visible text, `html_content` for markup. `page.text` can be empty on a 200, so print a length. The `deprecated ... use Fetcher.configure()` warning on every call is noise.

Tiered stack: Scrapling `StealthyFetcher` first for a protected target, escalate to rotunda when it returns 403/429/CAPTCHA, and feed rotunda's HTML back into Scrapling's parser.

## Pitfalls

1. **cwd shadowing**: a directory named `rotunda` in the working directory becomes a namespace package and breaks the import with `cannot import name 'NewBrowser' ... (unknown location)`. Check with `cd /tmp && python3 -c "import rotunda; print(rotunda.__file__)"`. On Windows and WSL it must print the `workspace/rotunda/pythonlib/rotunda` path.
2. **Wrong interpreter**: after a pull, install into the resolved live interpreter, never the legacy `~/.hermes/hermes-agent/venv` and never system site-packages via `pip install --break-system-packages`.
3. **Version gate**: `pyproject.toml` must stay at the tag version (0.5.1) or the browser download fails `MissingRelease`.
4. **Playwright drift**: any rotunda dependency resolve pulls Playwright to 1.59 and breaks launching. Keep 1.61–1.64.
5. **WSL has no X server**: use `headless=True`, or `xvfb-run` for headed work.
6. **Profile growth**: `~/.rotunda/agent/profiles/` accumulates; remove test profiles after use.
7. **Google Trends 429**: even rotunda gets 429'd there; use pytrends instead.
8. **Never claim it works without the smoke test on that host.** On native Windows it does not work, by design of the releases.

## Updating rotunda

```bash
cd .../<user>/workspace/rotunda
git fetch origin && git log --oneline HEAD..origin/main | wc -l    # 0 = nothing new, stop
git pull origin main
# keep pyproject.toml version equal to the new tag
# install editable into each live interpreter with uv pip install -e ... --python "<resolved>"
# restore Playwright afterwards to 1.61-1.64, because the pin will have downgraded it
# new browser build ⇒ re-apply fix 2 to its omni.ja, and re-check fix 3 still applies
```

Then re-run the smoke test on that host before telling anyone it is done.

## What undoes the patches

- `rotunda remove` or `rotunda fetch` re-extracts the browser and wipes fix 2.
- Reinstalling rotunda writes a fresh `utils.py` and wipes fix 3.
- A pip resolve of rotunda's deps downgrades Playwright and wipes fix 4.

Backups to restore from: `omni.ja.bak-isMobile` in each build dir, `utils.py.bak-args` next to each patched `utils.py`.
