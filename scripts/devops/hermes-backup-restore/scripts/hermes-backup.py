#!/usr/bin/env python3
"""Hermes Windows backup script - pure Python, no bash dependency.

Canonical robust version. Implements all fixes from the 2026-07-19 incident:
  - PAT embedded in remote URL (fetched via `gh auth token`)
  - GIT_TERMINAL_PROMPT=0 + GCM_INTERACTIVE=never (fail fast, never prompt)
  - Hard timeout on every git subprocess call (180s)
  - Unique timestamped staging dir per run (no WinError 32 from prior orphans)
  - git clone instead of init+pull+rebase (preserves history, no conflict branch)
  - Stale staging-dir cleanup at end of run (best-effort)

Deploy: copy this file to ~/AppData/Local/hermes/scripts/hermes-backup.py
        and reference it from the cron job by bare filename "hermes-backup.py".
        Requires `gh` CLI authenticated with a token that has push access to
        REPO_URL (verify with `git ls-remote https://<pat>@<repo>` HEAD).
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime

HERMES_DIR = os.path.expanduser("~/AppData/Local/hermes")
REPO_URL = "https://github.com/vincentsativa/windows-hermes-backup.git"
GIT_TIMEOUT = 180  # seconds per git call

SUBDIRS = ["config", "skills", "cron/output", "memories", "kanban"]


def _remove_readonly(func, path, excinfo):
    """Clear read-only bit and retry deletion (needed for .git/objects on Windows)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _git_env():
    """Environment for git calls: never prompt, fail fast instead."""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    return env


def _run_git(args, cwd=None, timeout=GIT_TIMEOUT):
    """Run a git command with a hard timeout. Raises TimeoutExpired if exceeded."""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=_git_env(),
        timeout=timeout,
    )


def _get_pat():
    """Fetch the GitHub PAT from `gh auth token`."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=30
        )
    except FileNotFoundError:
        raise RuntimeError("gh CLI not found; cannot obtain GitHub PAT for backup")
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            f"gh auth token failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _authenticated_repo_url(pat):
    return REPO_URL.replace("https://github.com/", f"https://{pat}@github.com/")


def _cleanup_old_staging(max_age_seconds=86400):
    """Remove hermes-backup-* staging dirs older than max_age_seconds."""
    tmp = tempfile.gettempdir()
    now = time.time()
    for entry in os.listdir(tmp):
        if not entry.startswith("hermes-backup"):
            continue
        path = os.path.join(tmp, entry)
        if not os.path.isdir(path):
            continue
        try:
            if now - os.path.getmtime(path) > max_age_seconds:
                shutil.rmtree(path, onerror=_remove_readonly)
        except OSError:
            pass


def main():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(tempfile.gettempdir(), f"hermes-backup-{stamp}")

    pat = _get_pat()
    authed_url = _authenticated_repo_url(pat)

    try:
        _run_git(["clone", "--quiet", authed_url, backup_dir], timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"ERROR: git clone timed out after {GIT_TIMEOUT}s", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git clone failed: {e.stderr}", file=sys.stderr)
        return 1

    for d in SUBDIRS:
        os.makedirs(os.path.join(backup_dir, d), exist_ok=True)

    config_src = os.path.join(HERMES_DIR, "config.yaml")
    if os.path.isfile(config_src):
        shutil.copy2(config_src, os.path.join(backup_dir, "config"))

    env_src = os.path.join(HERMES_DIR, ".env")
    if os.path.isfile(env_src):
        shutil.copy2(env_src, os.path.join(backup_dir, "config"))

    skills_dir = os.path.join(HERMES_DIR, "skills")
    if os.path.isdir(skills_dir):
        for entry in os.listdir(skills_dir):
            if entry == ".git":
                continue
            src = os.path.join(skills_dir, entry)
            dst = os.path.join(backup_dir, "skills", entry)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    cron_jobs = os.path.join(HERMES_DIR, "cron", "jobs.json")
    if os.path.isfile(cron_jobs):
        shutil.copy2(cron_jobs, os.path.join(backup_dir, "cron"))

    cron_output = os.path.join(HERMES_DIR, "cron", "output")
    if os.path.isdir(cron_output):
        for item in os.listdir(cron_output):
            src = os.path.join(cron_output, item)
            dst = os.path.join(backup_dir, "cron", "output", item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    for fname in ["MEMORY.md", "USER.md"]:
        src = os.path.join(HERMES_DIR, "memories", fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(backup_dir, "memories"))

    kanban_ws = os.path.join(HERMES_DIR, "kanban", "workspaces")
    if os.path.isdir(kanban_ws):
        shutil.copytree(
            kanban_ws,
            os.path.join(backup_dir, "kanban", "workspaces"),
            dirs_exist_ok=True,
        )

    try:
        _run_git(["add", "-A"], cwd=backup_dir)

        diff = _run_git(["diff", "--cached", "--quiet"], cwd=backup_dir)
        if diff.returncode == 0:
            print(f"No changes to backup at {datetime.now():%Y-%m-%d %H:%M}")
            return 0

        date_str = datetime.now().strftime("%Y-%m-%d")
        _run_git(
            ["-c", "user.name=Hermes Backup", "-c", "user.email=hermes@local",
             "commit", "-qm", f"Weekly backup {date_str}"],
            cwd=backup_dir,
        )

        push = _run_git(["push", "--quiet", "origin", "main"], cwd=backup_dir)
        if push.returncode != 0:
            print("Push failed, retrying with --force-with-lease...", file=sys.stderr)
            _run_git(["fetch", "--quiet", "origin", "main"], cwd=backup_dir)
            push2 = _run_git(
                ["push", "--quiet", "--force-with-lease", "origin", "main"],
                cwd=backup_dir,
            )
            if push2.returncode != 0:
                print(f"ERROR: push failed. stderr: {push2.stderr}", file=sys.stderr)
                return 1

        sha = _run_git(["rev-parse", "--short", "HEAD"], cwd=backup_dir).stdout.strip()
        print(f"Backup complete: {datetime.now():%Y-%m-%d %H:%M} - {sha}")
    except subprocess.TimeoutExpired as e:
        print(f"ERROR: git command timed out: {e}", file=sys.stderr)
        return 1
    finally:
        try:
            shutil.rmtree(backup_dir, onerror=_remove_readonly)
        except OSError:
            pass
        _cleanup_old_staging()

    return 0


if __name__ == "__main__":
    sys.exit(main())