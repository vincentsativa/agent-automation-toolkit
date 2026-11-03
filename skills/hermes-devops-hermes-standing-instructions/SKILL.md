---
name: hermes-standing-instructions
description: Use when a rule must hold every turn, not per skill.
trigger: "A user asks for a behavior to be fixed for good, a rule that must apply to every session, or a model that turns plain questions into long tool chains."
---

# Standing Instructions and Turn Over-Run

Two halves of one problem: where an always-on rule actually lives, and why a model keeps working when it should have answered.

## 1. Where a standing rule belongs (and where it does not)

When the request is "make this stop happening every session," the instrument matters more than the wording.

| Instrument | Applies when | Cap | Survives `hermes update` |
|---|---|---|---|
| `agent.system_prompt` (config.yaml) | every turn, every session, every platform | none | yes |
| Skill (SKILL.md / auto_load) | only when loaded or triggered | none | yes |
| Memory entry | every turn | small char budget | yes, but capped |
| Source patch | everywhere | n/a | **no, wiped by update** |

- A rule about HOW to do a class of task (news workflow, publishing, prospecting) belongs in that skill.
- A rule that must bind regardless of task (answer questions in the same turn; never touch a given system) belongs in `agent.system_prompt`.
- Memory is for state and durable facts, NOT for locking in a behavior. Writing memory in response to an order reads as modifying the user's system without permission, and it does not change how the runtime steers the model.
- Never present a memory write as "the fix" for a behavioral complaint.

**Do not restate the environment's own guidance.** Hermes already injects tool-use enforcement and execution discipline; a standing instruction carries the user's rule only.

## 2. Install the rule (procedure)

1. Confirm nothing already shadows the slot: `display.personality` empty, `HERMES_EPHEMERAL_SYSTEM_PROMPT` unset, no `channel_overrides` entry for that chat with its own `system_prompt`.
2. Write the text into `agent.system_prompt` with a targeted YAML update that preserves the rest of the file:

```python
import sys, os
sys.path.insert(0, r"~\AppData\Local\hermes\hermes-agent")
os.environ.setdefault("HERMES_HOME", r"~\AppData\Local\hermes")
from utils import atomic_roundtrip_yaml_update
atomic_roundtrip_yaml_update(
    r"~\AppData\Local\hermes\config.yaml",
    "agent.system_prompt", TEXT,
)
```

Use the Hermes venv python (`$LOCALAPPDATA/hermes/hermes-agent/venv/Scripts/python`). That interpreter is a native Windows binary: give it forward-slash `C:/...` paths, never an MSYS `/tmp` path, and put the helper script in the scratch dir rather than the system temp dir.
3. Write the rule in the user's own terms: what counts as a question, what counts as a task, what the exceptions are (a broken thing still gets diagnosed; assigned work still gets finished). Keep it short and unambiguous; do not paraphrase the user's words into new rules.
4. If a skill governs the same class of task, mirror the rule there too, so it binds even when the config value is missing.

## 3. Verify it, do not eyeball it

Reading the YAML back is not proof, and neither is a diff. Call the function the runtime calls:

```python
from gateway.run import _load_gateway_config
from hermes_cli.config import resolve_ephemeral_system_prompt_from_config
cfg = _load_gateway_config()
print(len(resolve_ephemeral_system_prompt_from_config(cfg)))
```

**Resolution order** (`hermes_cli/personality.py`, `resolve_ephemeral_system_prompt`): `HERMES_EPHEMERAL_SYSTEM_PROMPT` env wins, then `display.personality` when the name is a known personality, then `agent.system_prompt`. A per-channel `channel_overrides` `system_prompt` beats the global value for that chat. If the resolver returns empty, check those sources before editing anything else.

**Propagation:** the gateway resolves the prompt per turn (`gateway/run_config_loaders.py` → `_load_ephemeral_system_prompt`, handed to `AIAgent` as `ephemeral_system_prompt` by `gateway/run_turn_runner.py`), so an edit lands on the next turn. A CLI session needs a new session. State which case applies instead of claiming an effect the resolver did not show.

## 4. Why the model will not stop (turn over-run)

When the symptom is "I asked a question and it went away doing things," the cause is usually injected guidance, not the model's temperament:

- `agent.tool_use_enforcement` (default `"auto"`) matches model names containing `gpt`, `codex`, `gemini`, `gemma`, `grok`, `glm`, `qwen`, `deepseek`, `muse` and instructs the model to make tool calls immediately, keep working until the task is complete, and never end a turn with a promise of future action.
- `agent.execution_guidance` (default `"auto"`) adds a tool-persistence block: keep calling tools until the work is complete AND verified, retrying partial or narrow results.
- `agent.task_completion_guidance` and `agent.parallel_tool_call_guidance` add more of the same.
- `display.interim_assistant_messages: true` is what surfaces each mid-turn tool call in chat, which is why the user sees a wall of activity instead of one answer.

Both auto-matches fire on `deepseek` model names. On an assigned task this guidance is correct; on a read-only question it is exactly the failure. The fix is a standing instruction that draws the line between question and task, not disabling the guidance globally, because the assigned-work half still needs it.

## 5. Pitfalls

- **Diagnosis is not a fix.** Naming the cause and then asking "want me to apply it?" is the same failure being complained about. A direct "fix it" order is the authorization for the write; do not ask permission for what was just ordered.
- **Do not answer a behavioral complaint with a memory write.** Unauthorized, capped, and inert.
- **Do not claim the gateway picked it up** without running the resolver, and name the one restart command if a restart is genuinely needed.
- **Keep the rule in one place per surface.** Duplicating the same text across config, a skill, and memory guarantees they drift.
