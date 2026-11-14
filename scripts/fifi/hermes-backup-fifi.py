#!/usr/bin/env python3
"""Hermes Windows backup script for the "Fifi The Dog" profile only.

Backs up the fifi profile (profiles/fifi), NOT the default Hermes home.
Repo: <private-backup-repo> (private).

Adapted from the working hermes-backup.py (2026-07-19 robustness pass):
  - Token read from a local 0600 file (scripts/.backup-token), never from the git
    credential manager: GCM pops a GUI sign-in window on Windows when a credential is
    rejected, which a scheduled run must never do.
  - GIT_TERMINAL_PROMPT=0 and credential.helper disabled on every git call: fail fast
    instead of hanging or prompting.
  - Hard timeout on every git call.
  - Unique timestamped staging dir per run (no stale .git lock poisoning).
  - Fresh clone each run (history preserved, no rebase conflict branch).
  - Stale staging dirs older than 24h cleaned up after a successful run.

Safety: refuses to run unless the resolved directory is the fifi profile, so a
HERMES_HOME pointing at the default agent can never be backed up here.
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime

PROFILE_NAME = "fifi"
DEFAULT_PROFILE_DIR = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "hermes", "profiles", PROFILE_NAME
)
REPO_URL = "<private-backup-repo>"
GIT_TIMEOUT = 180  # seconds per git call
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".backup-token")

# Directories to create in staging if the repo is empty.
SUBDIRS = ["config", "skills", "cron/output", "memories"]

# Profile-root files copied into config/
CONFIG_FILES = ["config.yaml", ".env", "profile.yaml", "SOUL.md"]


def _resolve_profile_dir():
    """The fifi profile dir.

    HERMES_HOME is used only when it actually names the fifi profile; otherwise the
    known profile path is used. This job must never back up the default agent.
    """
    env_home = os.path.normpath(os.environ.get("HERMES_HOME", "").strip() or "")
    default = os.path.normpath(DEFAULT_PROFILE_DIR)
    if env_home and os.path.basename(env_home).lower() == PROFILE_NAME:
        return env_home, env_home
    if os.path.isdir(default):
        return default, default
    return None, env_home or default


def _remove_readonly(func, path, excinfo):
    """Clear read-only bit and retry deletion (needed for .git/objects on Windows)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _git_env():
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    # Blank askpass so a helper can never take over the terminal.
    env["GIT_ASKPASS"] = ""
    env["SSH_ASKPASS"] = ""
    return env


def _run_git(args, cwd=None, timeout=GIT_TIMEOUT):
    # credential.helper= (empty) disables git-credential-manager for this call, so a
    # rejected credential fails instead of opening the GCM sign-in window.
    return subprocess.run(
        ["git", "-c", "credential.helper=", "-c", "credential.interactive=false"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=_git_env(),
        timeout=timeout,
    )


def _get_pat():
    """Token for the backup repo, from disk only.

    scripts/.backup-token is the account credential that can actually push to this repo
    (the fine-grained GITHUB_TOKEN that `gh auth token` returns is not scoped to it and
    fails with 403). Nothing here consults the git credential manager, so no GUI prompt.
    """
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as fh:
            token = fh.read().strip()
        if token:
            return token
    except OSError:
        pass

    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=30
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"No token at {TOKEN_FILE} and gh CLI not found; cannot obtain GitHub token"
        )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            f"gh auth token failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _authenticated_repo_url(pat):
    return REPO_URL.replace("https://github.com/", f"https://{pat}@github.com/")


def _cleanup_old_staging(max_age_seconds=86400):
    tmp = tempfile.gettempdir()
    now = time.time()
    for entry in os.listdir(tmp):
        if not entry.startswith("fifi-backup-"):
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
    hermes_dir, rejected = _resolve_profile_dir()
    if hermes_dir is None:
        print(
            f"ERROR: refusing to back up {rejected!r}: it is not the "
            f"{PROFILE_NAME!r} profile",
            file=sys.stderr,
        )
        return 1
    if not os.path.isfile(os.path.join(hermes_dir, "config.yaml")):
        print(f"ERROR: {hermes_dir} has no config.yaml, not a Hermes home", file=sys.stderr)
        return 1

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(tempfile.gettempdir(), f"fifi-backup-{stamp}")

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

    try:
        _run_git(["remote", "set-url", "origin", authed_url], cwd=backup_dir)
    except Exception:
        pass

    try:
        _run_git(
            ["config", "url.insteadOf", "https://github.com/", f"https://{pat}@github.com/"],
            cwd=backup_dir,
        )
    except Exception:
        pass

    for d in SUBDIRS:
        os.makedirs(os.path.join(backup_dir, d), exist_ok=True)

    # Config-ish files at the profile root.
    for fname in CONFIG_FILES:
        src = os.path.join(hermes_dir, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(backup_dir, "config"))

    # Skills tree (skip .git).
    skills_dir = os.path.join(hermes_dir, "skills")
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

    # Cron jobs definition.
    cron_jobs = os.path.join(hermes_dir, "cron", "jobs.json")
    if os.path.isfile(cron_jobs):
        shutil.copy2(cron_jobs, os.path.join(backup_dir, "cron"))

    # Cron run output.
    cron_output = os.path.join(hermes_dir, "cron", "output")
    if os.path.isdir(cron_output):
        for item in os.listdir(cron_output):
            src = os.path.join(cron_output, item)
            dst = os.path.join(backup_dir, "cron", "output", item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    # Memories.
    for fname in ["MEMORY.md", "USER.md"]:
        src = os.path.join(hermes_dir, "memories", fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(backup_dir, "memories"))

    try:
        _run_git(["add", "-A"], cwd=backup_dir)

        diff = _run_git(["diff", "--cached", "--quiet"], cwd=backup_dir)
        if diff.returncode == 0:
            print(f"Fifi profile backup: no changes at {datetime.now():%Y-%m-%d %H:%M}")
            return 0

        date_str = datetime.now().strftime("%Y-%m-%d")
        _run_git(
            [
                "-c", "user.name=Hermes Backup",
                "-c", "user.email=hermes@local",
                "commit", "-qm", f"Fifi profile backup {date_str}",
            ],
            cwd=backup_dir,
        )

        push = _run_git(["push", "--quiet", "origin", "HEAD:main"], cwd=backup_dir)
        if push.returncode != 0:
            print("Push failed, retrying with --force-with-lease...", file=sys.stderr)
            _run_git(["fetch", "--quiet", "origin", "main"], cwd=backup_dir)
            push2 = _run_git(
                ["push", "--quiet", "--force-with-lease", "origin", "HEAD:main"],
                cwd=backup_dir,
            )
            if push2.returncode != 0:
                print(f"ERROR: push failed. stderr: {push2.stderr}", file=sys.stderr)
                return 1

        sha = _run_git(["rev-parse", "--short", "HEAD"], cwd=backup_dir).stdout.strip()
        print(f"Fifi profile backup complete: {datetime.now():%Y-%m-%d %H:%M} - {sha}")
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
