#!/usr/bin/env python3
"""
sync-ollama-models.py, keep ~/.pi/agent/models.json honest about what Ollama
actually serves, so pi never under- or over-estimates a model again.

Why this exists
---------------
pi assumes `contextWindow: 128000` when a model omits the field (docs/models.md).
For Ollama models the real value comes from the server, e.g. the deepseek/glm
cloud models expose 1048576. A missing or stale number makes pi compact the
conversation far too early, or overrun the real window.

Same story for vision: pi decides whether to invoke the vision-proxy (or send
images straight to the model) from each model's `input` array. Ollama already
knows the answer, `GET /api/show` returns it in `capabilities`.

What it syncs (per model under providers.ollama.models)
  contextWindow  <- model_info.*.context_length
  input          <- ["text","image"] when capabilities include "vision", else ["text"]

With --prune it also removes models the server has retired (HTTP 410). Only an
explicit "retired" 410 counts; a 404 or a connection error never deletes a model.

Everything else in the file is left untouched. A .bak copy is written before any
change. Key order follows the file's alphabetical house style, and bytes are
written LF-only so diffs stay surgical.

Usage
  python sync-ollama-models.py                  # dry run, prints the diff
  python sync-ollama-models.py --write          # apply (backs up first)
  python sync-ollama-models.py --write --prune  # also drop retired models
  python sync-ollama-models.py --url http://127.0.0.1:11434

Exit codes: 0 = in sync (or applied), 1 = error (unreadable config, no server).
Drift or prunable models on a dry run still exit 0, callers should read stdout.
"""

import argparse
import json
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

MODELS_JSON = Path.home() / ".pi" / "agent" / "models.json"
BACKUPS_TO_KEEP = 5

OK, MISSING, RETIRED, ERROR = "ok", "missing", "retired", "error"


def derive_base_url(models: dict) -> str:
    """Use the ollama provider's own baseUrl, minus /v1, 0.0.0.0 -> 127.0.0.1."""
    provider = (models.get("providers") or {}).get("ollama") or {}
    raw = provider.get("baseUrl") or "http://127.0.0.1:11434/v1"
    raw = raw.rstrip("/")
    if raw.endswith("/v1"):
        raw = raw[: -len("/v1")]
    return raw.replace("//0.0.0.0", "//127.0.0.1")


def show(base_url: str, model_id: str, timeout: int = 30) -> tuple[str, dict | None, str | None]:
    """Return (status, info, detail) for one model. Never raises."""
    body = json.dumps({"model": model_id}).encode()
    req = urllib.request.Request(
        f"{base_url}/api/show", data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return OK, json.load(r), None
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")[:200]
        if e.code == 404:
            return MISSING, None, "not on this server"
        # Only treat an explicit retirement as removable. A bare 410 is not enough.
        if e.code == 410 and "retire" in text.lower():
            try:
                detail = json.loads(text).get("error", text)
            except Exception:
                detail = text
            return RETIRED, None, detail
        return ERROR, None, f"HTTP {e.code} {text}"
    except Exception as e:
        return ERROR, None, f"{type(e).__name__}: {e}"


def truth_from(info: dict) -> tuple[int | None, list[str] | None]:
    """Extract (context_length, input_modes) from an /api/show response."""
    ctx = None
    for key, value in (info.get("model_info") or {}).items():
        if key.endswith(".context_length") and isinstance(value, int) and value > 0:
            ctx = value
            break  # first match wins; one architecture per model

    modes = None
    caps = info.get("capabilities")
    if isinstance(caps, list):
        modes = ["text", "image"] if "vision" in caps else ["text"]
    return ctx, modes


def prune_backups(keep: int = BACKUPS_TO_KEEP) -> None:
    """Keep the newest N backups. Auto-sync runs often enough that unbounded
    timestamped copies would slowly litter the agent directory."""
    backups = sorted(
        MODELS_JSON.parent.glob(MODELS_JSON.name + ".bak-*"),
        key=lambda p: p.name,
    )
    for old in backups[:-keep] if keep > 0 else backups:
        try:
            old.unlink()
        except OSError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply changes (default: dry run)")
    ap.add_argument("--prune", action="store_true", help="remove models the server retired (410)")
    ap.add_argument("--url", help="ollama base url, e.g. http://127.0.0.1:11434")
    args = ap.parse_args()

    if not MODELS_JSON.exists():
        print(f"error: {MODELS_JSON} not found", file=sys.stderr)
        return 1

    raw = MODELS_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    base_url = (args.url or derive_base_url(data)).rstrip("/")

    provider = ((data.get("providers") or {}).get("ollama")) or {}
    models = provider.get("models") or []
    if not models:
        print("no ollama models configured; nothing to do")
        return 0

    print(f"ollama: {base_url}")
    print(f"file:   {MODELS_JSON}")
    print(f"models: {len(models)}\n")

    changes: list[tuple[str, list[str]]] = []
    unknown: list[tuple[str, str]] = []
    retired: list[tuple[str, str]] = []
    healthy = 0
    unreachable = 0

    for m in models:
        mid = m.get("id")
        if not mid:
            continue
        status, info, detail = show(base_url, mid)

        if status in (MISSING, ERROR):
            unknown.append((mid, detail or status))
            if status == ERROR:
                unreachable += 1
            continue
        if status == RETIRED:
            retired.append((mid, detail or "retired"))
            continue

        ctx, modes = truth_from(info or {})
        did = []
        if ctx is not None and m.get("contextWindow") != ctx:
            was = m.get("contextWindow")
            shown = was if was is not None else "(unset -> pi assumes 128000)"
            did.append(f"contextWindow {shown} -> {ctx}")
            m["contextWindow"] = ctx
        if modes is not None and m.get("input") != modes:
            did.append(f"input {m.get('input')} -> {modes}")
            m["input"] = modes

        if did:
            changes.append((mid, did))
        else:
            healthy += 1

    # Fail loudly if the server never answered at all, silently "succeeding"
    # would let a dead ollama look like a clean bill of health.
    if unreachable == len(models):
        print(f"error: could not reach ollama at {base_url}", file=sys.stderr)
        return 1

    for mid, did in changes:
        print(f"CHANGE {mid}")
        for d in did:
            print(f"       {d}")
    for mid, why in retired:
        verb = "PRUNE " if args.prune else "RETIRED"
        print(f"{verb} {mid}  ({why})")
    for mid, why in unknown:
        print(f"SKIP   {mid}  ({why}, left as-is)")

    to_remove = len(retired) if args.prune else 0
    print(
        f"\n{len(changes)} to change, {len(retired)} retired"
        f"{f' ({to_remove} to prune)' if to_remove else ''}, "
        f"{healthy} already correct, {len(unknown)} skipped"
    )

    if not changes and not to_remove:
        print("nothing to write.")
        return 0

    if not args.write:
        print("\ndry run, re-run with --write to apply.")
        return 0

    if to_remove:
        retired_ids = {mid for mid, _ in retired}
        provider["models"] = [m for m in models if m.get("id") not in retired_ids]

    backup = MODELS_JSON.with_suffix(MODELS_JSON.suffix + f".bak-{datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(MODELS_JSON, backup)
    # sort_keys keeps the alphabetical house style; write_bytes avoids Windows
    # text-mode turning LF into CRLF (which would churn every line).
    newline = "\n" if raw.endswith("\n") else ""
    MODELS_JSON.write_bytes((json.dumps(data, indent=2, sort_keys=True) + newline).encode("utf-8"))
    print(f"\nwrote {MODELS_JSON}\nbackup {backup.name}")
    prune_backups(keep=BACKUPS_TO_KEEP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
