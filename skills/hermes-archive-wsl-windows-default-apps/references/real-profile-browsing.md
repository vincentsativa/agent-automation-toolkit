# Real-Profile Browsing Requires a Chromium Default

## The trap: `use_real_profile: true` set ≠ feature works

Setting `browser.use_real_profile: true` in `~/.hermes/config.yaml` only flips
the consent flag. The real-profile path **fails closed**, returns an error,
launches nothing, copies nothing, whenever the default browser is not a
supported Chromium (Chrome/Edge/Brave/Chromium).

On this machine the default is **Comet** (non-Chromium), so the feature is
enabled but can never run. Do NOT conclude "feature is broken" or "agent lied";
the mechanism is a default-browser compatibility gate, not consent.

## Decisive diagnostics (run, don't argue)

1. Flag is on? `grep use_real_profile ~/.hermes/config.yaml`
2. Snapshot ever ran? `ls ~/.hermes/browser-profile/`
   Empty/missing dir ⇒ snapshot never succeeded ⇒ consent is not the blocker.
3. Default-browser gate (the decisive check):
   ```
   cd ~/.hermes/hermes-agent && python3 -c \
     "from hermes_cli.browser_connect import detect_default_chromium; \
      print(repr(detect_default_chromium()))"
   ```
   - returns a key (`chrome`/`edge`/...) ⇒ supported, feature should work
   - returns `None` ⇒ default browser is non-Chromium ⇒ fails closed

## Fix path

Set default to a supported Chromium. BUT on this box the UCPD driver blocks
scripted default-browser writes (see parent skill), so the change likely needs
the OS-sanctioned settings UI (`explorer.exe "ms-settings:defaultapps"`) rather
than a registry write.

## Other fail-closed causes

- `browser.engine` must be `auto`/`chrome`. **Lightpanda cannot load a Chromium
  profile** and fails closed with an explicit message.
- Pre-release Chromium channel (Beta/Dev/Canary) as default is unsupported
  (won't guess the channel's profile dir, wrong-principal safety).

## Source

`tools/browser_tool.py` → `_real_profile_cdp()` (the fail-closed gate).
`hermes_cli/browser_connect.py` → `detect_default_chromium()`,
`snapshot_real_profile()`, `real_profile_copy_dir()`.
Snapshot copies only auth state (cookies, Login Data, Preferences) to
`~/.hermes/browser-profile/<browser>/`.
