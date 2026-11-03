#!/usr/bin/env python3
"""Prove a custom provider entry and one of its models are live, the way the picker and
runtime read them. Run it with the Hermes interpreter that imports ruamel (see the
skill's Pitfalls for resolving that path).

Usage:
  python verify_provider_model.py <provider-name> <model-id> [config.yaml-path]

config.yaml-path defaults to $HERMES_HOME/config.yaml. Runtime resolution always reads
the root config, so pass a profile path only to check that profile's allowlist.
Prints nothing secret; never echo the API key.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(local) / "hermes"


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    provider, model = sys.argv[1], sys.argv[2]
    home = hermes_home()
    cfg_path = Path(sys.argv[3]) if len(sys.argv) > 3 else home / "config.yaml"
    sys.path.insert(0, str(home / "hermes-agent"))
    os.environ.setdefault("HERMES_HOME", str(home))

    try:
        import yaml
    except ImportError:
        print("FAIL: this interpreter has no yaml/ruamel; use the Hermes runtime interpreter")
        return 1

    raw = cfg_path.read_text(encoding="utf-8")
    parsed = yaml.safe_load(raw)
    print("config:", cfg_path)
    print("raw 'custom_providers:' lines:", raw.count("\ncustom_providers:"))
    print("raw lines containing the model id:", raw.count(model))

    entries = [p for p in (parsed.get("custom_providers") or []) if p.get("name") == provider]
    if len(entries) != 1:
        print("FAIL: expected exactly one entry named", provider, "found", len(entries))
        return 1
    entry = entries[0]
    models = entry.get("models")
    is_list = isinstance(models, list)
    print("allowlist is a LIST (pin):", is_list, "| discover_models:", entry.get("discover_models"))
    print("allowlist size:", len(models) if is_list else "n/a", "| target present:", bool(is_list and model in models))
    print("base_url:", entry.get("base_url"), "| api_mode:", entry.get("api_mode"), "| key_env:", entry.get("key_env"))

    try:
        from hermes_cli.config import (get_compatible_custom_providers, load_config,
                                       validate_config_structure)
        cfg = load_config()
        for e in get_compatible_custom_providers(cfg):
            name = e.get("name") if isinstance(e, dict) else getattr(e, "name", None)
            if name == provider:
                m = e.get("models") if isinstance(e, dict) else getattr(e, "models", None)
                print("PICKER", provider, "models:", len(m or []), "| target present:", model in (m or []))
        issues = validate_config_structure(cfg)
        print("VALIDATOR issues:", len(issues), [str(i)[:120] for i in issues][:5])
    except Exception as exc:  # noqa: BLE001 - report, do not hide
        print("picker/validator check failed:", type(exc).__name__, exc)

    try:
        from hermes_cli.runtime_provider import resolve_runtime_provider
        rt = resolve_runtime_provider(requested=provider, target_model=model)
        for k in ("provider", "base_url", "api_mode", "model"):
            print("  runtime", k, "=", rt.get(k))
        print("  runtime api_key set:", bool(rt.get("api_key")))
    except Exception as exc:  # noqa: BLE001
        print("runtime resolution failed:", type(exc).__name__, exc)

    # Live entitlement probe: 1 token against the endpoint with the key from the env file.
    key_env = entry.get("key_env") or ""
    base_url = (entry.get("base_url") or "").rstrip("/")
    key = ""
    env_file = home / ".env"
    if env_file.exists() and key_env:
        m = re.search(rf"^{re.escape(key_env)}=(.*)$", env_file.read_text(encoding="utf-8"), re.M)
        key = (m.group(1).strip().strip('"') if m else "")
    if key and base_url:
        body = json.dumps({"model": model, "messages": [{"role": "user", "content": "hi"}],
                           "max_tokens": 5}).encode()
        req = urllib.request.Request(base_url + "/chat/completions", data=body,
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode())
                print("LIVE call HTTP", resp.status, "| usage:", payload.get("usage"))
        except urllib.error.HTTPError as exc:
            print("LIVE call HTTP", exc.code, "-", exc.read().decode()[:200], "(drop the id if 402/403)")
        except Exception as exc:  # noqa: BLE001
            print("LIVE call failed:", type(exc).__name__, exc)
    else:
        print("LIVE call skipped: key_env value not found in", env_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
