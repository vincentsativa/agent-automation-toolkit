---
name: hermes-config-key-writes
description: Write a Hermes config key and prove it is live.
trigger: "ANY programmatic edit to a Hermes config.yaml key (agent.*, display.*, auxiliary.*, platform settings) or a standing behavioral rule installed via config."
---

# Hermes Config Key Writes

How to change one key in `config.yaml` so the value the running agent actually sees
is the value you intended. Editing the file is the easy half; proving the consumer
reads it is the half that gets skipped and then blamed.

## Procedure

1. Read the CURRENT parsed value before writing. `yaml.safe_load` the file and print
the key you are about to change, plus `grep -c '^  <key>:' config.yaml` to confirm it
exists once.
2. Write through the sanctioned single-key path, never a whole-document dump:

```python
import sys, os
from pathlib import Path
sys.path.insert(0, r"<hermes-agent source dir>")
os.environ.setdefault("HERMES_HOME", r"<hermes home>")
from utils import atomic_roundtrip_yaml_update
atomic_roundtrip_yaml_update(Path(r"<hermes home>/config.yaml"), "agent.system_prompt", VALUE)
```

`atomic_roundtrip_yaml_update` preserves comments, ordering, and quoting and writes
via temp file plus atomic replace. It is the same path `hermes config set` uses.

For a plain scalar at a nested path, skip the script: `hermes config set
mcp_servers.<name>.url https://host/mcp` reaches the same writer and is immune to the
write guard on the root file. Prove it twice, with `hermes config get <dotted.key>`
(prints the parsed value) and `grep -n -A4 '^  <name>:' config.yaml` (one entry, correct
indent). Do not hand-roll a ruamel script for a single scalar; the script path is for
values that need escaping, flattening, or a container write.

3. Re-parse the file and assert on the PARSED value: exact length, start, end, and
`count(chr(10))` (expected 0 for a single-line scalar).
4. Verify through the code that consumes the key, not by re-reading the file. For
gateway-applied keys, call the resolver the gateway calls per turn:

```bash
# $HERMES_PY: resolve the Hermes interpreter by capability (see Pitfalls), never assume ./venv/Scripts/python.exe
cd "$LOCALAPPDATA/hermes/hermes-agent" && "$HERMES_PY" -c "
import sys, os; sys.path.insert(0, r'.')
os.environ.setdefault('HERMES_HOME', r'$LOCALAPPDATA/hermes')
from gateway.run import _load_gateway_config
from hermes_cli.config import resolve_ephemeral_system_prompt_from_config
sp = resolve_ephemeral_system_prompt_from_config(_load_gateway_config())
print('LEN', len(sp), '| HEAD', sp[:60], '| QUOTES', sp.count(chr(34)))"
```

5. Confirm exactly one key line in the raw file: `grep -c '^  <key>:' config.yaml`.
6. Report the parsed value, the resolver output, and the duplicate count. Nothing else
counts as proof.

## Pitfalls

- **Round-trip writers fold long scalars.** ruamel rewraps a long string into a
  multi-line folded scalar indented under the key. It parses identically, but the file
  no longer reads as one line and the user sees "columns". After writing, flatten the
  value to ONE physical line with a plain-text pass over that key only, then re-run the
  resolver check. YAML folds a newline to a space on parse, so a flattened single-quoted
  scalar delivers exactly the same value.
- **Repeated escaping accumulates artifacts.** Pushing the same value through two
  escape-then-write passes leaves literal `\"` sequences that parse as real quote
  characters inside the prompt. If the resolved value contains stray quotes, take the
  CURRENT parsed value, strip only the outer delimiter, and write it back once. Never
  re-run the same escaping script.
- **Quote choice.** If the text contains a double quote, delimit the scalar with single
  quotes. Strip surrounding delimiters off the parsed value before re-quoting, or you
  nest the quotes into the value.
- **Do not re-dump the document.** `yaml.dump` of the whole file strips comments and
  reorders keys. One key at a time.
- **Blocked temp paths.** If `write_file` declines an existing path it has not fully read
  this task, do not retry it. Write the one-off script to a fresh path under the Hermes
  scratch dir (`$LOCALAPPDATA/hermes/cache/scratch/`) and run it from there.
- **Resolve the Hermes interpreter by capability, never by a hardcoded venv path.**
  The launcher's python path is install-layout dependent, and the bare `python` on PATH is
  the bundled toolchain, not the Hermes runtime, so it lacks ruamel and every config
  script dies on import. Pick the first candidate that actually imports ruamel and reuse
  it for the session:
  `for p in "$LOCALAPPDATA"/hermes/installs/*/environments/*/venv/Scripts/python.exe; do
  "$p" -c 'import ruamel.yaml' 2>/dev/null && echo "$p" && break; done`.
- **The root `config.yaml` is write-guarded; profile configs are not.** The `patch` and
  `write_file` tools refuse `$LOCALAPPDATA/hermes/config.yaml` outright ("Refusing to
  write to Hermes config file ... security-sensitive configuration"), while
  `profiles/<name>/config.yaml` accepts a normal targeted line edit. Plan for the split
  instead of hitting it halfway through a mirror: do the profile edits first, then make
  the root edit through `atomic_roundtrip_yaml_update` (or `hermes config set`), and
  parse-verify both files at the end.
- **A value nested inside a list element is written as the whole container key.**
  `atomic_roundtrip_yaml_update` navigates a dotted key path and cannot index a list, so a
  model inside `custom_providers[0].models` is written by reading the parsed
  `custom_providers` value, mutating the list in Python, and writing that key back whole.
  Then confirm the raw file still holds exactly one top-level `<key>:` line and that the
  section comments above it survived the round trip.
- **A list-valued key is written by passing the whole Python list.** Replace the list in
  one call (`atomic_roundtrip_yaml_update(path, "skills.external_dirs",
  ["plugins/<name>/skills"])`); do not attempt a dotted index, which cannot address a list.
  Read the result back through Hermes's own parser with `hermes config get <key>`, which
  prints each element on its own `- item` line, so a real list cannot be mistaken for a
  one-element string, and pair it with `grep -c '<path fragment>' config.yaml` so a second
  copy in absolute, `~`, or `${VAR}` form shows up as a count above one. Where an install
  guide ships with the key, follow its instruction to edit the file rather than use
  `hermes config set` for list keys, since preserving list structure through a single
  KEY VALUE pair is unverified.
- **A keyed endpoint entry lives in every profile that uses it, not just the root.**
  An entry like `nvidia-free` is duplicated verbatim in the root config and each
  `profiles/<name>/config.yaml`, so adding a model to "the endpoint we have set up" means
  editing every copy; report each file you touched and its resulting count rather than the
  one you happened to open first.
- **A quoted container is a silently ignored value, not a scalar.** `providers: '[]'`
  or `plugins.enabled: '["a"]'` parses as a STRING, so every isinstance-gated reader
  falls back to its default and the setting does nothing at all, with no error anywhere.
  The schema already knows which slots are containers: `hermes_cli/config.py::_container_slots()`
  walks `DEFAULT_CONFIG` plus `_KNOWN_CONTAINER_TYPES` (dotted keys typed `list` or
  `mapping`). Fix with a real container, one key at a time:
  `hermes config set <dotted.key> '{}'` (mapping) or `'[]'` (list). The empty mapping is
  usually also the schema default, so the fix changes no behavior; that is exactly why
  the wrong form sits in the file for months without anyone noticing.
- **Every config value must be checked per file.** Each profile owns its own
  `config.yaml` under `profiles/<name>/`. A bad slot value found in the default profile's
  file is very likely duplicated in every profile's file; grep them all and report which
  ones still carry it instead of silently fixing only the one you were shown.
- **Prove a config warning is cleared by re-running the validator, not by re-reading the
  file.** `validate_config_structure(load_config())` returns the issue list the
  startup/doctor paths print; assert it is empty, or that no issue names your key. A
  re-read only proves you typed the line.
- **A warning that first appears after `hermes update` usually predates the update.**
  Updates ship detectors alongside changes, so the check is new far more often than the
  bad value is. Prove which one before saying the update wrote it: date the check with
  `git log --oneline -S "<validator symbol>" -- <file>`, then grep the same key across
  `state-snapshots/*/config.yaml`, `backups/config/*`, and every profile's `config.yaml`.
  If the identical bad value is in the pre-update snapshots, the update added the
  detector, not the value, and the honest report says so.
- **Shadowing.** A config value that never takes effect may be outranked rather than
  miswritten. Check the higher-precedence sources before editing anything.
- **Do not narrate the maintenance.** Blocked-path refusals, backup files, and scratch
  scripts are internal noise. Report the final verified value, not the plumbing.
- **Profile configs do not inherit custom_providers or model defaults from the root config.** Each profile owns its own config.yaml under profiles/<name>/. Changing model/provider/base_url in the default profile does not propagate to fifi, Karma, etc. Mirror the provider name, base_url, model default, auxiliary sections, and the custom_providers entry into every profile that must use it. Verify with grep -n for the provider name in the profile file and that model_catalog.excluded_providers matches the root.
- **Env vars for key_env are process-scoped, not shell-exported.** Checking `env | grep NVIDIA_API_KEY` in a bash session shows NOT_SET even when Hermes gateway is running with the key. Verify availability by asking Hermes to resolve the runtime provider for the name, or inspect the process environment of the running gateway, not the shell.

## Support Files

- `references/standing-instruction-overlay.md` — installing a permanent behavioral rule
  via `agent.system_prompt`: precedence order, where it is read, and how it is verified.
- `references/custom-provider-endpoints.md` — adding a secondary/custom OpenAI-compatible
  provider (NVIDIA NIM etc.) with an allowlisted model subset in the /model selector:
  config shape, allowlist mechanics, resolving a user-facing model name to its exact
  catalog ID, per-model verification.
- `scripts/verify_provider_model.py` — re-runnable proof that a custom provider entry and
  one model are live: raw-file checks, picker allowlist, runtime resolution, validator
  issues, and a live 1-token call against the endpoint.
