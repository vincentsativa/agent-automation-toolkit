#!/usr/bin/env python3
"""Bulk-retag cron job models through the jobs store (never by hand-editing jobs.json).

Dry-run by default; writes only with --apply. Backs the store up before writing and
reads every job back afterwards.

Run it with the install venv, which is the interpreter that owns the cron package:
  ~/.hermes/hermes-agent/venv/bin/python retag_cron_models.py \
      --match deepseek --target deepseek-v4.1-flash:1017-cloud --provider ollama-com --skip glm
  ... same call plus --apply

Rules this encodes:
  * paused/disabled jobs are reported, not rewritten, unless --include-paused is passed;
  * jobs already on the target are skipped, so the run is idempotent;
  * a job with no model at all (script-only) is listed separately, never counted as pinned.
"""
import argparse
import datetime
import os
import shutil
import sys


def _bootstrap():
    home = os.environ.get("HERMES_HOME") or os.path.expanduser("~/.hermes")
    src = os.path.join(home, "hermes-agent")
    if os.path.isdir(src) and src not in sys.path:
        sys.path.insert(0, src)
    return home


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", required=True, help="substring of the current model, e.g. deepseek")
    ap.add_argument("--target", required=True, help="model string to write")
    ap.add_argument("--provider", default=None, help="provider slug to write alongside the model")
    ap.add_argument("--skip", action="append", default=[], help="model prefix to leave alone (repeatable), e.g. --skip glm")
    ap.add_argument("--include-paused", action="store_true", help="also rewrite paused/disabled jobs")
    ap.add_argument("--apply", action="store_true", help="write the change (default is dry-run)")
    a = ap.parse_args()

    home = _bootstrap()
    from cron.jobs import list_jobs, update_job

    jobs = list_jobs(include_disabled=True)
    match, target = a.match.lower(), a.target.lower()
    skips = [s.lower() for s in a.skip]

    todo, untouched, paused, nomodel = [], [], [], []
    for j in jobs:
        model = str(j.get("model") or "").strip()
        if not model:
            nomodel.append(j)
            continue
        ml = model.lower()
        if any(ml.startswith(s) for s in skips) or ml == target or match not in ml:
            untouched.append((j, model))
            continue
        enabled = bool(j.get("enabled", True)) and j.get("state") != "paused"
        if not enabled and not a.include_paused:
            paused.append((j, model))
            continue
        todo.append((j, model))

    print(f"jobs total: {len(jobs)}   to retag: {len(todo)}   untouched: {len(untouched)}   paused/held back: {len(paused)}   no model: {len(nomodel)}")
    for j, model in todo:
        print(f"  CHANGE  {j['id']}  {model} -> {a.target}  | {j.get('name')}")
    for j, model in paused:
        print(f"  PAUSED  {j['id']}  {model}  | {j.get('name')}  (state={j.get('state')}) - not rewritten")
    for j in nomodel:
        print(f"  NOMODEL {j['id']}  | {j.get('name')}")

    if not a.apply:
        print("\ndry run: nothing written. Re-run with --apply to commit.")
        return 0
    if not todo:
        print("\nnothing to change.")
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    src = os.path.join(home, "cron", "jobs.json")
    bak = f"{src}.bak.{stamp}_bulkretag"
    shutil.copy(src, bak)
    print(f"\nbackup: {bak}")

    updates = {"model": a.target}
    if a.provider:
        updates["provider"] = a.provider
    for j, _ in todo:
        update_job(j["id"], dict(updates))

    # Read back from the store, never from the in-memory list that drove the writes.
    after = {j["id"]: j for j in list_jobs(include_disabled=True)}
    bad = [j["id"] for j, _ in todo if str(after[j["id"]].get("model") or "").strip().lower() != target]
    on_target = sum(1 for j in after.values() if str(j.get("model") or "").strip().lower() == target)
    print(f"wrote {len(todo)} job(s); jobs now on {a.target}: {on_target}")
    if bad:
        print("FAILED to land on: " + ", ".join(bad))
        return 1
    print("read-back verified: every intended job carries the target model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
