#!/usr/bin/env python3
"""Print the provider rows the Hermes picker builds, with model counts and membership checks.

Works on a normal install and on an InstaBox box (no venv). Pass model IDs as arguments to
check whether each row carries them, e.g.

    probe_provider_rows.py deepseek-v4.1-flash:1017 mistralai/mistral-large-4-1t-a52b

Run on a box with the managed runtime python:

    PY=$(ls -d /data/home/.hermes/tools/python-*/bin/python3 | head -1)
    $PY -I /data/home/probe_provider_rows.py <ids...>

On a normal install run it with the project venv interpreter, because the config loader needs
ruamel.yaml and the bare python3 on PATH does not have it. A ModuleNotFoundError for ruamel
means the wrong interpreter, not a missing package.
"""
import json
import os
import sys

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
os.environ.setdefault("HERMES_HOME", HERMES_HOME)
sys.path.insert(0, os.path.join(HERMES_HOME, "hermes-agent"))

try:
    from hermes_cli.config import load_config
except ModuleNotFoundError:
    import hermes_bootstrap  # noqa: F401  installs the managed dependency set on sys.path
    from hermes_cli.config import load_config

from hermes_cli.model_switch import list_authenticated_providers

wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
cfg = load_config()
model = cfg.get("model") or {}
print("MODEL:", json.dumps(model))
print("PROVIDERS:", json.dumps(cfg.get("providers")))
print("CUSTOM:", json.dumps(cfg.get("custom_providers")))

rows = list_authenticated_providers(
    current_provider=model.get("provider", ""),
    current_base_url=model.get("base_url", ""),
    current_model=model.get("default", ""),
    user_providers=cfg.get("providers"),
    custom_providers=cfg.get("custom_providers"),
)
for r in rows:
    models = r.get("models") or []
    hits = " ".join("%s=%s" % (w, w in models) for w in wanted)
    print("ROW %-14s | %-16s | %3d models%s" % (r.get("slug"), r.get("name"), len(models), (" | " + hits) if hits else ""))

# Fail loudly when the configured default is not on its own provider's row: that pairing
# answers every call with a 404 while the config still looks fine.
prov = model.get("provider")
default = model.get("default")
if prov and default:
    ok = any(r.get("slug") == prov and default in (r.get("models") or []) for r in rows)
    print("DEFAULT_ON_ROW:", ok, "(%s / %s)" % (prov, default))
