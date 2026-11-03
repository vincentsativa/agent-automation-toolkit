# Driving a two-tree sync (WSL Frank tree to the Windows tree)

Depth for the "apply the change-brief to both agents" workflow. Read this when a
brief has skill deltas for a skill that exists on both trees, or when the brief
pipeline looks dead.

## Trees

- WSL: `~/.hermes` (skills under `~/.hermes/skills/<category>/<skill>/`).
- Windows: `/mnt/c/Users/<user>/AppData/Local/hermes` (same relative layout).
- Source of truth for what is current: `/tmp/hermes-backup`, a clone of
  `github.com/vincentsativa/linux-hermes-backup` refreshed by the daily/weekly
  backup job.

## Delta, never overwrite

The two trees are NOT mirrors. Each carries skills the other lacks, and each
carries its own version of shared files. So:

- Brief item for a skill the target tree already has: patch the named bullet or
  section in place. Overwriting with the source tree's file silently deletes the
  target's own content.
- Brief item for a skill the target tree lacks: copy the whole directory
  (`shutil.copytree` keeps `references/`), then `diff -r` source against copy.

## Insertion recipe

Extract the inserted text from the source tree so nothing is retyped, convert its
line endings to the target's, and assert the replacement fires exactly once:

```python
src = open(source_path, encoding='utf-8').read()
bullet = [ln for ln in src.split('\n') if ln.lstrip().startswith(marker)][0].rstrip('\r\n')
tgt = open(target_path, encoding='utf-8').read()
eol = '\r\n' if '\r\n' in tgt else '\n'
assert tgt.count(anchor) == 1, 'anchor is not unique, stop'
tgt = tgt.replace(anchor, anchor + eol + bullet.replace('\n', eol), 1)
open(target_path, 'w', encoding='utf-8', newline='').write(tgt)
```

Write with `newline=''` so Python does not translate endings a second time.

## Line endings

The Windows tree is mixed: some files are CRLF, some LF. Sniff the target file
(`'\r\n' in text`) and convert only the block you insert. Forcing one convention
across the tree rewrites every untouched line and buries the real diff.

## Is the brief pipeline alive?

```bash
git -C ~/agent-change-briefs pull && ls ~/agent-change-briefs/briefs/
ls -la ~/.hermes/cron/output/agent-change-brief-*.md
python3 -c "import json;d=json.load(open('~/cron/jobs.json'));j=d if isinstance(d,list) else d.get('jobs',[]);print([{k:x.get(k) for k in ('id','name','schedule','enabled')} for x in j if 'brief' in (x.get('name') or '').lower()])"
diff -q /tmp/hermes-backup/skills/vinny-constitution/SKILL.md ~/.hermes/skills/vinny-constitution/SKILL.md
```

A brief job with `enabled: false` and a backup repo whose newest commit is
weeks newer than the newest brief means unbriefed changes exist. The backup's
git log tells you when the law changed (`git log -- skills/vinny-constitution/`),
which is how you date a gap.

## Items a brief asks for that you must not apply

- Memory edits (section C). Report them, do not write them.
- Anything touching cron jobs, unless Vinny asked for that directly.

## Reporting

State what was already current, what you applied per tree, what you skipped and
why, and any structural finding that explains a gap (a disabled brief job, a
tree whose identity no longer matches its label).
