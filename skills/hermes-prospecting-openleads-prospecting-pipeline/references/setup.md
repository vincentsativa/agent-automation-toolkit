# OpenLeads install and repair runbook

Both agents are already installed and verified. Use this when something breaks,
when a fresh machine needs it, or when the repo needs updating.

## Safety check before installing anything

Run these on any copy of the repo before you install or run it.

```bash
cd <repo>
# 1. what it talks to
grep -rhoE 'https?://[a-zA-Z0-9._-]+' --include='*.py' . | sed 's|https\?://||' | sort -u
# 2. no dynamic execution
grep -rnE '\b(eval|exec|os\.system|pickle\.loads|marshal)\(' --include='*.py' .
# 3. no telemetry or phone-home
grep -rniE 'telemetry|analytics|posthog|sentry|mixpanel' --include='*.py' .
# 4. dependency surface
cat requirements.txt pyproject.toml
```

The copy reviewed on 2026-09-16 passed all four. Outbound hosts are GitHub, PyPI,
Wikidata, Google DNS-over-HTTPS, Cloudflare DNS, Gravatar, OpenStreetMap/Overpass,
Nominatim, Hacker News (Algolia), OpenAlex, NPI registry, SEC EDGAR, YC's public
dataset, ProductHunt RSS, and OpenRouter (only if you set an API key). Dependencies
are zero for the engine itself; `requests` and `python-dotenv` are pulled only by
the optional campaign extras. There is no telemetry and no hosted backend. The only
`exec`-family hit in the tree is `importlib` loading your own `*.py` source plugins
from `~/.openleads/sources`, which is by design.

The optional `openleads web` dashboard binds `127.0.0.1` only. If you ever run it,
do not expose that port.

## WSL install (already done)

```bash
git clone --depth 1 https://github.com/Samyrrrrrr990/openleads.git ~/tools/openleads
python3 -m venv ~/.venvs/openleads
~/.venvs/openleads/bin/python3 -m pip install -U pip
cd ~/tools/openleads && ~/.venvs/openleads/bin/python3 -m pip install .[all]
ln -sf ~/.venvs/openleads/bin/openleads ~/.local/bin/openleads
```

Then the launcher at `~/tools/openleads/ol.sh`:

```bash
export PYTHONIOENCODING=utf-8
exec ~/.venvs/openleads/bin/python3 -m openleads "$@"
```

Verify:

```bash
~/tools/openleads/ol.sh --version     # openleads 4.0.1
~/tools/openleads/ol.sh doctor
~/.venvs/openleads/bin/python3 -m pytest ~/tools/openleads/tests -q   # 302 passed
```

`pip install --user` and `pip install` into the system Python both fail under
PEP 668 on this box. Use the venv, do not use `--break-system-packages`.

## Windows install (already done)

From the WSL agent, driving `cmd.exe` (always `cd` into a `C:` path first, because
`cmd.exe` cannot use a UNC working directory):

```bash
cp -r ~/tools/openleads /mnt/c/Users/<user>/workspace/openleads
rm -rf /mnt/c/Users/<user>/workspace/openleads/.git
cd /mnt/c/Users/<user>/workspace/openleads
/mnt/c/Windows/System32/cmd.exe /c "C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe -m venv C:\Users\<user>\.venvs\openleads"
/mnt/c/Windows/System32/cmd.exe /c "C:\Users\<user>\.venvs\openleads\Scripts\python.exe -m pip install -U pip"
/mnt/c/Windows/System32/cmd.exe /c "C:\Users\<user>\.venvs\openleads\Scripts\python.exe -m pip install .[all]"
```

Notes learned the hard way:

- Quote the local path alone, with no extras inside the quotes:
  `pip install .[all]` run from inside the folder. Passing
  `"C:\path[all]"` fails with `Invalid requirement`.
- PowerShell one-liners launched from bash need `\$` for their variables.

Then the launcher at `C:\Users\<user>\workspace\openleads\ol.cmd`:

```bat
@echo off
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
"C:\Users\<user>\.venvs\openleads\Scripts\python.exe" -m openleads %*
```

`PYTHONIOENCODING=utf-8` is also set as a User environment variable, so any Windows
shell gets it. Verify:

```
C:\Users\<user>\.venvs\openleads\Scripts\openleads.exe --version   -> openleads 4.0.1
ol.cmd doctor                                                     -> port 25 reachable
```

The venv `Scripts` folder is on the User PATH, so `openleads` works in a freshly
opened Windows shell. A shell that was already open when the PATH was set will not
see it until it is reopened.

Test suite on Windows: `301 passed, 1 failed`. The single failure is the `0600`
mode assertion in `tests/test_settings_cli.py`. Windows cannot express POSIX `0600`
and the code path is fine. Leave it.

## Updating

WSL:

```bash
cd ~/tools/openleads && git pull
~/.venvs/openleads/bin/python3 -m pip install --force-reinstall .[all]
```

Windows: pull into `~/tools/openleads`, then re-copy to
`C:\Users\<user>\workspace\openleads` (minus `.git`) and re-run the `pip install`.

`openleads config` (interactive), `openleads config set <key> <value>` for
settings, and `openleads doctor` for health. Secrets are written to
`secrets.json` inside the state dir, separate from `settings.json`.
