---
name: hermes-provider-configuration
description: Fix a provider's model list in Hermes config.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, config, providers, models, picker]
    related_skills: [hermes-config-editing, model-tuning-optimization, hermes-agent]
---

# Hermes Provider Configuration

Governs the `providers:` / `custom_providers:` sections of `config.yaml`: which
models a provider row shows, why a configured list grows or shrinks on its own,
and how to prove a change actually took effect.

Editing the file itself has its own guard and supported write paths; see the
user-owned `hermes-config-editing` skill for the writer. This skill is the
provider semantics.

## When to Use

Load this skill when any of these is true:

- A provider's model list is not what the user configured, too many models, or
  the list changes between opens.
- The user asks for only the models they declared, or a subset of an endpoint's
  catalog.
- A provider row is missing from the picker entirely.
- You are about to edit `providers:` or `custom_providers:` in `config.yaml`.
- You need to prove a provider config change took effect.

## Discovery policy: the one rule that explains the surprises

A provider entry that declares `models:` AND carries a credential gets that list
**replaced** by the endpoint's live `/v1/models` response. The picker paints the
declared list first, then balloons to the endpoint's whole catalog once the probe
lands. A user who configured eleven models and now sees eighty-one is hitting
exactly this, not a bug.

The full decision table:

- **Credential present → live `/v1/models` is the source of truth** and replaces
the declared list.
- **No credential + a list or string `models:` → the declared list is an
allowlist** and the probe is skipped. This is a network-cost guard for keyless
endpoints.
- **A dict-shaped `models:` is per-model metadata, not an allowlist.** Dict shape
is what the wizard writes for context lengths, so those entries still probe.
- **`discover_models: false` overrides all of the above** and pins the row to the
declared list.

So the answer to "I only want the models I configured" is always
`discover_models: false` added to that provider block:

```yaml
providers:
  some-endpoint:
    base_url: https://.../v1
    api_key: ...
    discover_models: false   # keep only the models: below
    models:
      - vendor/model-a
      - vendor/model-b
```

Do not invent a narrower `models:` list by hand-picking a tier you assume is the
intended one, and do not remove the credential to stop the probe. Pinning is the
supported switch and it is one line.

## Resolve the row before editing

The same endpoint can be several independent rows, and `discover_models` on one
does not affect the others:

- `providers.<name>: {base_url, api_key, models}` is a user-provider row.
- A `custom_providers:` entry is its own endpoint row.
- A bare `model.provider: custom` plus `model.base_url` is a third row.
- **A provider with no `providers:` entry at all is still a row** when a pooled
  credential exists under `credential_pool.<slug>` in `auth.json`. That row's
  models come entirely from live discovery, so it paints the endpoint's WHOLE
  catalog, and every model the endpoint serves is already on it. This is the
  mechanism behind the common complaint, never a reason to declare the job done:
  see "Adding one model to a row that already has everything" below.

Confirm which slug the picker is actually emitting, then edit the entry behind
that row. Editing the wrong one produces a change that does nothing.

## Adding one model to a row that already has everything

"Add this model" means THE ROW MUST END UP SHOWING WHAT THEY NAMED. A row that
shows the model among eighty-seven others is not the thing that was asked for,
and answering the order with "it is already there" is a refusal dressed up as a
report. The user cannot act on it and has to order the same job twice.

The shape that satisfies the order is a pinned declared row:

```yaml
providers:
  <slug>:
    base_url: https://<endpoint>/v1
    api_key: <literal key>
    discover_models: false
    models:
      - <exactly the ids they named>
```

One judgement call, made and stated, never left as a question: what else goes in
the list. If they named one model, the minimum is that one. Do not bulk-fill from
the catalog.

The pooled-credential row for the same endpoint still exists and still shows
its full catalog, so the same provider now appears TWICE. Naming it as a separate
row is a first-pass report, not the finished job: when the user says the provider
should appear ONCE ("NVIDIA NIM should be in there once"), the duplicate row is
part of the order and you remove it. Do it after the key is copied into the
declared block, never before, or the declared row loses its credential too.

```bash
hermes auth list                       # provider slug + credential id/label
hermes auth remove <provider> <id>     # BOTH args required, e.g. nvidia 3d2c73
hermes auth reset custom:<slug> <label>  # clears a stale 'auth failed (401)' flag
```

`hermes auth reset <provider> all` is not "every credential of that provider": it
logs the provider out. Pass the id or label from `hermes auth list`.

Verify with a row count, not just the model list: count rows whose slug or name
matches the endpoint and assert it is 1. A declared row keeps working after the
pool credential is deleted only because its key was copied in; confirm with one
live `-m` call afterwards.

## A declared row needs a literal key, not a guessed variable

`api_key: ${SOME_VAR}` only resolves when that variable really exists in the
process environment or `.env` of the install you are editing. An unset variable
produces a keyless block that fails every call with
`HTTP 401 ... Invalid JWT serialization`, which reads like a bad model ID and is
not one.

So: copy the key the endpoint's pooled credential already uses
(`auth.json` -> `credential_pool.<slug>[0]`), write it into the block, and prove
the route with a live call. Verify the write landed by length and prefix through
the config API, not by eye, because display output masks secrets.

## Turn catalog page names into real API model IDs

When the user hands you a list of models from a vendor's browse page (build
portals, model zoos, docs index pages), those are DISPLAY names, not the IDs the
API accepts. Writing them in verbatim produces a list that renders fine and
fails on every call. Resolve each one against the endpoint's live catalog before
writing the block:

```bash
curl -s https://<endpoint>/v1/models -H "Authorization: Bearer <key>" \
  | python3 -c "import sys,json;print('\n'.join(sorted(m['id'] for m in json.load(sys.stdin)['data'])))" \
  > /tmp/ids.txt
```

Then match each requested name to an ID by substring. Report any that matched
nothing, and report any matched ID that is NOT on that endpoint at all, a
vendor catalog routinely lists microservices (image, video, translation,
detection, embedding) that have no chat-completions route. Those belong in the
list only if the user asked for them by name; flag explicitly that selecting them
in the picker will 404 on a chat call, because the picker cannot express "this
model uses its own REST endpoint". Silence there is a lie the user finds out at
use time.

Ask for the page only if you cannot derive the list yourself; do not block on
confirming names you can resolve unambiguously.

## Stale caches survive the fix

Discovered catalogs are cached on disk under `$HERMES_HOME`
(`provider_models_cache.json`, keyed by credential fingerprint plus endpoint, and
provider-specific caches such as `nvidia_models_cache.json`). The picker serves
these without a network round-trip, so a row can keep painting the wide list
after the pin is in place.

They expire on a TTL and refresh in the background. Clearing one is a workaround
for stale display, never the fix. The fix is the config key.

## Verify through the picker, not by re-reading config

Re-loading `config.yaml` only proves the file parsed. Drive the same row builder
the picker uses, at the same scope:

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python3 - <<'PY'
import sys; sys.path.insert(0, "~/hermes-agent")
from hermes_cli.config import load_config
from hermes_cli.model_switch import list_authenticated_providers
cfg = load_config()
rows = list_authenticated_providers(
    current_provider=cfg["model"]["provider"],
    current_base_url=cfg["model"].get("base_url", ""),
    current_model=cfg["model"].get("default", ""),
    user_providers=cfg.get("providers"),
    custom_providers=cfg.get("custom_providers"),
)
for r in rows:
    print(r.get("slug"), r.get("name"), len(r.get("models") or []))
PY
```

Two things this probe must get right:

- **Run it with the project venv interpreter**, not the bare `python3` on PATH.
The config loader imports `ruamel.yaml` through `hermes_yaml`, which only the
project venv has. A ModuleNotFoundError for `ruamel` means the wrong interpreter,
not a missing package. On an install with no venv (a container or remote box),
the equivalent is the managed runtime `python-*/bin/python3` run with `-I` after
`import hermes_bootstrap`; see the `instabox` skill's
`scripts/probe_provider_rows.py`.
- **Prove usability with a call, not a count.** `hermes -m <model-id> --provider
  <slug> -z "Reply with exactly the single word: OK"` returning `OK` is the only
  evidence that a model on a discovered row actually routes.
- **Pass `user_providers` and `custom_providers` explicitly.** Calling the
function with no arguments reports only the built-in rows (openrouter, nous,
Copilot) and a user-defined provider looks missing when it is perfectly fine.

Print the count AND the model IDs. A count of eleven proves the pin. "The row
exists" proves nothing.

## After the edit

The running gateway caches config in memory. The change takes effect for the user
only after `/restart` in chat or a gateway restart. Tell them; do not report the
fix as live without it.

## Reporting the fix

List the exact IDs you wrote, in full, every one, so the user can verify before
checking anything else. State the mechanism in one line (credential present means the live catalog wins),
the one-line change, and the verified count with the model IDs listed. Then name
any separate defect found along the way as an offer, with the exact command to
fix it, and leave it alone until asked.
