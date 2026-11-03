# Debugging Hermes TUI Slash Commands

## Overview

Hermes slash commands span three layers — Python command registry, tui_gateway JSON-RPC bridge, and the Ink/TypeScript frontend. When a command misbehaves (missing from autocomplete, works in CLI but not TUI, config persists but UI doesn't update), the bug is almost always one layer being out of sync with another.

## Architecture

```
Python backend (hermes_cli/commands.py)     <- canonical COMMAND_REGISTRY
       │
       ▼
TUI gateway (tui_gateway/server.py)         <- slash.exec / command.dispatch
       │
       ▼
TUI frontend (ui-tui/src/app/slash/)        <- local handlers + fallthrough
```

## Investigation Steps

1. Check if command exists in TUI frontend:
   ```bash
   search_files --pattern "/commandname" --file_glob "*.ts" --path ui-tui/
   ```
2. Examine TUI command definition: `read_file ui-tui/src/app/slash/commands/core.ts`
3. Check Python backend: `search_files --pattern "commandname" --path hermes_cli/commands.py --context 3`
4. Examine gateway: `search_files --pattern "slash.exec" --path tui_gateway/`

## Fix: Missing Command Autocomplete

Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`:
```python
CommandDef("commandname", "Description", "Session",
           cli_only=True, aliases=("alias",),
           args_hint="[arg1|arg2|arg3]",
           subcommands=("arg1", "arg2", "arg3")),
```

Key fields: `cli_only`, `gateway_only`, `gateway_config_gate`, `subcommands`, `aliases`

For gateway commands, add handler in `gateway/run.py`. For CLI commands, add to `HermesCLI.process_command()` in `cli.py`.

## Common Issues

1. **Command shows in TUI but not autocomplete** — missing from `COMMAND_REGISTRY`
2. **Command shows in autocomplete but doesn't work** — missing handler in tui_gateway or frontend
3. **CLI vs TUI behavior differs** — different implementations in two places
4. **Config persists but UI doesn't update** — also update nanostore state + render paths
5. **Gateway silently ignores** — check `GATEWAY_KNOWN_COMMANDS` or `gateway_config_gate`

## Verification

1. Rebuild TUI: `npm --prefix ui-tui run build`
2. Test: `hermes --tui`, type `/` and verify autocomplete
3. If gateway-available, test on messaging platform too