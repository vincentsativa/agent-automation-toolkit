# Verifying a Hermes install-tree patch without reloading it

Goal: turn "I edited the line" into "I drove the real code and it now returns the right value", while the running gateway still holds the old module. Then hand over the reload separately.

## 1. Compile check and diff scope

```bash
cd ~/.hermes/hermes-agent
python -m py_compile <file> [<file> ...] && echo COMPILE_OK
git diff --stat -- <paths>
```

`git status --short` on this tree also lists edits you did not make (scheduler, desktop scratch files). Judge your work from the per-path diff, never from the whole-tree status.

## 2. Drive the real function from a scratch dir

Use a fresh scratch dir per run, never a fixed filename:

```bash
SCRATCH=$(mktemp -d /tmp/hermes-verify-XXXXXX)
cat > "$SCRATCH/t.py" <<'EOF'
import sys
sys.path.insert(0, '~/hermes-agent')
...
EOF
cd ~/hermes-agent && python "$SCRATCH/t.py"; echo "exit=$?"
rm -rf "$SCRATCH"
```

Import the module by absolute path insertion so the same interpreter that runs the gateway resolves the same tree. Confirming the module imports is itself a check, since a broken edit fails here first.

## 3. Bind what the method needs instead of reimplementing it

A patched method that reads `self` can still be called unbound against a stub, as long as the stub supplies its siblings:

```python
class Stub:
    _merge_caption = staticmethod(BasePlatformAdapter._merge_caption)

TelegramAdapter._merge_into_pending(Stub(), pending, "key", event)
```

A `staticmethod` wrap of the REAL sibling keeps the test running production logic. Rewriting the helper inside the test is how a test passes on a shape production no longer has.

## 4. Assert the fixed case AND the control

Three assertions, all required:

1. The fixed input now passes the production gate (call the real validator, not a lookalike).
2. A second shape the fix must also handle (mixed flags, single item, empty list) passes.
3. The pre-fix input shape STILL returns the old failure, proving the check is live.

```python
assert validator(fixed) is None
assert validator(control) == "<the old failure>"
```

If a validator checks several clauses in order, a control can trip an earlier clause and mask the one you care about. Set the unrelated fields to a consistent shape so the intended clause is the one that fires, and read the returned clause instead of assuming.

## 5. Report, then hand over the reload

The verified facts are: compiles, diff is only the fix, real function returns the right value, control still fails. The unverified part is the live process. Say that, and give the reload command in one line. `/restart` from chat, `hermes gateway restart` from a shell outside the gateway. Then ask for the original message to be retried.
