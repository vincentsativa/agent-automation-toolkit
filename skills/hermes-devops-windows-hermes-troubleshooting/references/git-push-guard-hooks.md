# Global Git Push Guards (`core.hooksPath`)

A global `core.hooksPath` in `~/.gitconfig` redirects ALL of git's hooks to a shared directory. On a machine where agent scripts push to GitHub unattended, a pre-push guard installed there is a global kill switch: any repo it rejects fails every scheduled push, forever, with a message that points at the repo instead of the hook.

## Finding it

```bash
grep -n -i hooks /mnt/c/Users/<user>/.gitconfig
ls -la /mnt/c/Users/<user>/.githooks/
```

`core.hooksPath` is a global setting, so it also applies inside throwaway staging clones created by backup scripts. A clone in `/tmp` inherits it; nothing in the repo's own `.git/hooks` is involved.

## The recurring bug: `curl ... || printf '000'`

The single most common defect in a hand-written HTTP probe in a shell hook:

```bash
# WRONG
code="$(curl -s -o /dev/null -w '%{http_code}' -m 15 "$api" 2>/dev/null || printf '000')"
```

When curl writes its `%{http_code}` output and THEN exits non-zero (timeout during the transfer, connection reset after headers), the `||` branch runs too and its output is APPENDED, not substituted. The variable holds `200000`. Any guard comparing that value against `200` / `404` matches nothing and falls through to its "cannot verify, refuse" branch. Symptom: a plausible-but-impossible HTTP code in the error text, and every push blocked with a connectivity-sounding message while the network is fine.

Correct form, capture to a file, then validate the shape:

```bash
out="$(mktemp)"
curl -s -o /dev/null -w '%{http_code}' -m 15 "$api" >"$out" 2>/dev/null
code="$(tr -d ' \r\n' <"$out")"
rm -f "$out"
case "$code" in
  [0-9][0-9][0-9]) printf '%s' "$code" ;;
  *) printf '000' ;;
esac
```

## Second defect in the same class: a literal placeholder header

A fallback probe that sends `-H "Authorization: Bearer ***"` (the token redacted in a log or a docstring) can never authenticate. The failure is silent: the probe returns 401/404, the guard treats it as unverified, and the real token is never used. Never hand-redact a token into a code path that actually needs it, read it at call time.

## Verifying a guard change

Two separate checks, both required:

1. **The fix works**, run the real failing script end to end with the Windows toolchain (see the Windows-cron section in SKILL.md) and confirm the effect server-side.
2. **The protection still works**, invoke the hook directly with a known-public slug and assert exit 1:

   ```bash
   bash /mnt/c/Users/<user>/.githooks/pre-push origin https://github.com/<public-owner>/<repo>; echo "EXIT=$?"
   ```

Do NOT try to test the guard by pushing to a repo you cannot write to. GitHub returns 403 during connection setup, before the pre-push hook executes, so the guard never runs and a broken guard looks like it passed.

## Fixing a job that a guard blocks

The guard is a safety mechanism, not the bug. Never "fix" the failing job with `git push --no-verify`, and never widen the guard's allowlist to unblock one repo. Fix the probe.
