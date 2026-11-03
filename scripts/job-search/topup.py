"""Stage 4c: close a short list by widening supply, before anyone ships it.

The count is the deliverable. A run that ends under target because one collection
pass was too narrow is a failure the scripts can fix without a human: re-collect
the direct-apply sources, re-filter, re-resolve, re-verify, and re-select. On
October 22, 2026 the first pass left the in-band pool one short at twelve and the
list went out at nineteen; widening supply produced an eighth in-band role and
the twenty closed. On October 25, 2026 the two old rounds (Alignerr and the
Workable search) both went dead in one morning - Alignerr excluded by Vinny,
Workable search rate-limited for the third straight day - and a run that held
6 picks for a target of 20 hung for 75 minutes until the cron supervisor killed
it. The rounds below are the direct-apply supply that still answers.

Usage:
    python topup.py [--date YYYY-MM-DD] [--target 20] [--max-rounds 3]

Rounds are ordered cheapest first: the Workable search pulls deeper (and falls
back to the employer boards itself while the search endpoint is banned), then
SmartRecruiters pages deeper into its search surface, then the Workable
employer-board fallback runs forced so it happens even on a morning the search
endpoint answers. Nothing here relaxes a cap. If supply genuinely cannot fill
the target it says so and exits 0 so the caller can report the honest arithmetic
instead of padding.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

# Each round widens a direct-apply source. Workable is asked for more pages and
# more rows per term; SmartRecruiters pages deeper into the same search surface
# the baseline collect walked; the forced-board round is the documented
# Workable employer-board fallback (config/workable-boards.json) and runs even
# when the search endpoint answers, because the boards are a different service
# that is not rate-limited.
ROUNDS = [
    {"only": "workable", "params": {"workable_pages": 100, "workable_per_term": 100}},
    {"only": "smartrecruiters", "params": {
        "smartrecruiters_modifiers": ["part time", "contract", "freelance", "remote",
                                       "specialist", "coordinator", "assistant"],
        "smartrecruiters_request_cap": 400}},
    {"only": "workable", "params": {"workable_force_boards": True, "workable_per_board": 100}},
]


def step(script, extra):
    cmd = [sys.executable, os.path.join(HERE, script)] + extra
    print("\n=== topup: %s %s ===" % (script, " ".join(extra)))
    result = subprocess.run(cmd, cwd=HERE)
    if result.returncode != 0:
        print("topup: %s exited %d, continuing" % (script, result.returncode))


def pick_count(out_dir):
    path = os.path.join(out_dir, "selected.json")
    if not os.path.exists(path):
        return 0
    try:
        return len(json.load(open(path, encoding="utf-8")).get("picks") or [])
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--target", type=int)
    ap.add_argument("--max-rounds", type=int, default=len(ROUNDS))
    args = ap.parse_args()

    rules = C.config("rules.json")
    target = args.target or int(rules.get("target_count", 20))
    out_dir = C.run_dir(args.date)
    date_args = ["--date", args.date] if args.date else []

    have = pick_count(out_dir)
    if have >= target:
        print("topup: %d picks for a target of %d, supply is already sufficient" % (have, target))
        return

    print("topup: %d picks for a target of %d, widening supply" % (have, target))
    for index, spec in enumerate(ROUNDS[:args.max_rounds], 1):
        overrides = []
        for key, value in spec["params"].items():
            overrides.extend(["--param", "%s=%s" % (key, json.dumps(value))])
        # Each override applies only to this collection subprocess. A short run
        # must never silently narrow or otherwise alter tomorrow's baseline.
        step("collect.py", date_args + ["--only", spec["only"]] + overrides)
        step("prefilter.py", date_args)
        step("resolve_employer.py", date_args)
        step("verify.py", date_args)
        step("payfix.py", date_args + ["--limit", "100"])
        step("pack.py", date_args)
        step("select.py", date_args + ["--force"])
        have = pick_count(out_dir)
        print("topup: round %d (%s) leaves %d picks" % (index, spec["only"], have))
        if have >= target:
            print("topup: target met at %d picks" % have)
            return

    print("topup: still %d picks for a target of %d after %d rounds. "
          "The shortfall is supply, not selection: report it with the pool "
          "arithmetic (in-band paid + %d above-band + %d unpaid) and do not pad."
          % (have, target, min(args.max_rounds, len(ROUNDS)),
             int(rules.get("max_above_band_picks", 4)),
             int(rules.get("max_unpaid_picks", 3))))


if __name__ == "__main__":
    main()
