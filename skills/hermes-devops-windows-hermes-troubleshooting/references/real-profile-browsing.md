# Real-Profile Browsing (`browser.use_real_profile`)

Hermes' "browse as you" feature: the agent drives a **Hermes-managed snapshot** of
the user's real default-Chromium browser profile so it acts with their logins
(cookies, saved passwords, preferences) without the user handing over credentials
each time. Valuable for login-walled tasks: fetching API keys from a service's
settings page, posting, scraping behind auth.

## Consent toggle

```yaml
# ~/.hermes/config.yaml
browser:
  use_real_profile: true   # OFF by default
```

Set with `hermes config set browser.use_real_profile true`. Takes effect on the
next session restart (gateway `/restart` or new CLI), not mid-conversation.

## How it works (verified from the feature commit 1f4d095)

- On each launch Hermes snapshots the OS-default Chromium-family browser's
  profile into `~/.hermes/browser-profile/<browser>/` — ONLY auth-bearing state:
  cookies, Login Data, Web Data, Preferences, Local State. It strips caches,
  Extensions, Service Workers, IndexedDB, History, Singleton* (turns a
  multi-hundred-MB profile into a few MB).
- It drives that COPY with Hermes' own packaged Chromium on a devtools port.
  The live profile is never opened directly. This sidesteps Chrome 136+'s block
  on remote-debugging the default profile dir and never contends with a running
  browser.
- On each launch it re-syncs the auth files (`_AUTH_REFRESH_FILES`) from the real
  profile, so fresh logins in the user's own browser show up in the agent session.
- Only Chromium-family defaults are supported (Chrome, Edge, Brave, Chromium).
  A non-Chromium default (Firefox) fails **closed** with a clear message.
- Also gates the `local` argument on `browser_exec`, which forces a real-profile
  session even under a cloud backend.

## WSL GOTCHA (the gap on Vinny's machine)

Hermes runs inside WSL, which has **no installed default Chromium-family browser**
(`xdg-settings get default-web-browser` empty, no `$BROWSER`, no chrome/chromium/
edge on the Linux side). The feature needs a *default browser with a logged-in
profile* to snapshot. Consequences:

- It fails closed ("default browser is not a supported Chromium") until a Linux
  Chromium/Chrome is installed and set as default.
- The bundled **Playwright Chromium** (`~/.cache/ms-playwright/chromium-*`) does
  NOT count — it's clean and has no logins, so even promoting it to default gives
  a hollow profile with nothing useful.
- The user's real logins live in **Windows** Chrome (`/mnt/c/Program Files/Google/
  Chrome/Application/chrome.exe`). WSL cannot snapshot a Windows profile directly.
  So the feature only becomes genuinely useful under WSL if the user logs into a
  fresh Linux browser, OR Hermes runs natively on Windows (or the desktop app)
  where it can reach the real Chrome profile.

## Behavior boundaries (set with Vinny)

- Consent is already ON (2026-08-27). It fires ONLY on explicit instruction, never
  on its own.
- Vinny's stated use case: "when I can't figure something out" — API-key hunting
  behind login walls, UI fiddliness. Not daily use.
- Because it's a snapshot, what the agent does is invisible in the user's real
  browser and doesn't disturb an active session.
- Standing blocker: still no Linux Chromium in WSL as of 2026-08-27, so the flag
  is on but not yet usable. Do not claim it works until a default Linux Chromium
  exists.
