# Rotunda Version Mismatch Debug, June 20, 2026

## Symptom
`rotunda fetch` returns "0 versions" from the official repo. The Python API fails with `MissingRelease: No matching release found for Rotunda 0.1.0 on lin x86_64. Please update the Python library.`

## Root Cause
The `is_version_supported()` check in `pkgman.py` (line 212-216) requires an exact string match between the Python library version (from `pyproject.toml`) and the browser release version (from the GitHub release tag):

```python
def is_version_supported(self, version: 'Version') -> bool:
    return version.version == self.python_library_version
```

The `python_library_version` comes from `pyproject.toml`'s `version` field. If `pyproject.toml` says `0.1.0` but all actual releases are `0.3.x`, every release gets filtered out.

## Fix
1. Check the latest release tag: `git tag -l | tail -5` (and `git describe --tags` for HEAD)
2. Bump `pythonlib/pyproject.toml` version to match the tag (e.g. `0.1.0` → `0.5.1`). This local edit is required and is expected to show as a dirty working tree, upstream tags ship `version = "0.1.0"`. Verified live at tag v0.5.1 on 2026-09-25.
3. Resolve the live interpreter (PM-managed environment, not `hermes-agent/venv`):
   ```bash
   python3 -c "import json,glob;print(json.load(open(sorted(glob.glob('~/installs/*/facts.json'))[-1]))['packages']['venv']['environment'])"
   # append /bin/python (WSL) or \Scripts\python.exe (Windows)
   ```
4. Reinstall: `uv pip install -e pythonlib --force-reinstall --python <resolved interpreter>`, then re-pin `playwright==1.62.0` (Rotunda's soft `<=1.59.0` pin drags it down and breaks Scrapling's fetchers extra)
5. The first `NewBrowser()` call auto-downloads the matching browser binary

## Verification
Run the smoke test from the resolved live interpreter, from a neutral cwd such as `/tmp` (a directory named `rotunda` in the cwd shadows the package and fakes an `unknown location` ImportError). The first launch downloads a large zip and extracts it to `~/.cache/rotunda/browsers/official/<version>-<build>/`, e.g. `0.5.1-154.0.1`.

## Why This Happens
The `pyproject.toml` version was never bumped after the initial `0.1.0` release. The Python library and browser binary versions are coupled by design, the library version must match the browser release it was built to work with. When the repo is updated but `pyproject.toml` isn't, the version gate silently blocks everything.
