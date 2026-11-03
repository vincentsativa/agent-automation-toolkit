# Sweeping notes and scripts after a scraping-dependency upgrade

An upgrade to scrapling, Rotunda, or Playwright is only half done when the packages install. The other half is finding every note and script that names the old CLI surface and correcting it, because a stale command fails at fetch time and looks like a block or an empty page rather than a bad note.

## 1. Read the live surface first

```bash
scrapling --version
scrapling extract --help
for c in get post put delete fetch; do echo "== $c"; scrapling extract $c --help; done
python3 -c "import scrapling.fetchers as f; print([n for n in dir(f) if not n.startswith('_')])"
```

The `dir()` line matters as much as the CLI help: subcommands and classes move independently. A version that renamed a subcommand has usually also dropped or renamed Python classes, so check both before deciding what the new surface is.

Run that block against **every** installation on the machine, not only the one the shell resolves: `which -a scrapling` on WSL, `where.exe scrapling` on Windows, and each venv's own `Scripts/scrapling.exe`. Two installs routinely sit on different versions, and a rename shows up only in the one you actually probe. When they disagree, the venv copy is what the agent imports and the global copy is what a bare command calls, so upgrade them as separate steps and verify each.

## 2. Find every occurrence, separating live from historical

```bash
grep -rln "<old-token>" ~/.hermes/skills ~/.hermes/plugins ~/.hermes/cron/jobs.json
```

Widen only when that comes back clean:

```bash
grep -rln "<old-token>" ~ --include="*.md" --include="*.py" --include="*.sh" --include="*.txt" --include="*.yaml" --include="*.yml" --include="*.json" 2>/dev/null \
  | grep -v -E "/\.hermes/cache/|/\.hermes/cron/output/|/\.git/"
```

Exclusions and why:
- `~/.hermes/cron/output/` and `~/.hermes/cache/` are past run transcripts and fetched pages. They record what was true then, they are never executed, and they bury the real hits under hundreds of kilobytes of log.
- A tree named `*backup*` is a copy, not a source. Leave it alone.
- The Hermes product checkout (`~/.hermes/hermes-agent/`, including `optional-skills/` and `website/docs/`) is upstream vendor content. Editing it dirties the product repo and is wiped on upgrade. Report it as untouched instead of patching it.

Sweep every Hermes home that actually loads skills, and prove each home is the real one before trusting a clean grep. On Windows the home is `%LOCALAPPDATA%\hermes`, which from WSL is `/mnt/c/Users/<user>/AppData/Local/hermes`. `C:\Users\<user>\.hermes` also exists on these boxes but holds only `workspace/`, `creds/`, and browser-debug dirs, with no `skills/`, no `config.yaml` and no `cron/jobs.json`, so a sweep there returns empty and proves nothing:

```bash
H=/mnt/c/Users/<user>/AppData/Local/hermes
find "$H/skills" -name SKILL.md | wc -l     # zero means this is not the home you meant
ls "$H/cron/jobs.json" "$H/config.yaml"
```

Sweep the other agent trees on that machine too when they exist (`~/.claude/skills`, `~/.codex/skills`, `~/.pi/agent/skills`, `clawd/skills`, `.openclaw/workspace/skills`), plus any script directories. Then report the homes enumerated and how many skill files each held, because 'checked the other agent' is only true when the path held skills to check.

## 3. An unrestricted grep over the Windows mount times out

A plain `grep -r` across `/mnt/c/Users/<user>/workspace` can exceed two minutes. Target named directories with narrow includes and a hard cap:

```bash
timeout 120 grep -rln "<old-token>" /mnt/c/Users/<user>/workspace/scripts /mnt/c/Users/<user>/Desktop \
  --include="*.py" --include="*.sh" --include="*.ps1" --include="*.md" --include="*.txt" 2>/dev/null
```

## 4. Rewrite so the dead token cannot be copied

- Replace the command in every code block. A note whose dead line is annotated "this is GONE" still gets copied; delete the dead line from the block and put the warning in prose underneath it.
- Keep one sentence naming the removed token so a search for the old name lands on the correction. Everywhere else uses the new name only.
- When a version changed a flag rather than a name, state the unit or the accepted values explicitly, for example `--timeout` in milliseconds on the browser fetch and seconds on the plain one, and list which flags each subcommand rejects.

## 5. Prove the new form runs

Do not report the sweep off the diff. Execute each documented form once:

```bash
SCRATCH=$(mktemp -d ~/cache/scratch/smoke-XXXXXX)
scrapling extract fetch "https://example.com" "$SCRATCH/out.txt"
scrapling extract fetch "https://example.com" "$SCRATCH/out.html" --network-idle --wait 3000
scrapling extract get "https://example.com" "$SCRATCH/g.txt"
scrapling extract <removed-subcommand> "https://example.com" "$SCRATCH/x.txt"   # must exit 'No such command'
rm -rf "$SCRATCH"
```

A 200 plus a non-trivial byte count on each live form is the proof. Running the removed form is worth it too: it confirms the removal instead of trusting the changelog.

## 6. Close the loop

Refresh the rule in the owning skill so the next bump does not repeat the discovery from scratch. Report to the user with the files changed, the second break found while sweeping (there usually is one, because a CLI rename and a class removal ship in the same release), the commands run and their results, and any tree left alone with the reason.