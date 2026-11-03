---
name: hermes-github-backup
description: Back up Hermes Agent configuration and data to a private GitHub repo, plus a pattern for backing up arbitrary data folders and the change-briefs pipeline. Use when backing up configs, data folders, or distributing change briefs to other agents.
---

# Hermes GitHub Backup

Two distinct jobs live here: (1) backing up arbitrary data folders to a
dedicated private repo, and (2) the Change Briefs pipeline that distributes
dated briefs to other agents.

## Part 1: Backing up Arbitrary Data Folders

Daily backups of any folder to a dedicated private repo, via a
create-or-clone script pattern.

### create-or-clone script pattern

The script tries `git clone` first. If the repo is missing, it:

1. Creates the repo on GitHub via the API: `POST /user/repos`
2. Initializes a local repo (`git init`)
3. Pushes to `master`

### Credential & remote rules

- Use a **CLEAN remote URL** with a **credential store** — never embed a token
  in the remote URL.
- The default branch is **`master`**, not `main`.

### Sync mechanics

- Use `rsync` with `--delete` so removed local files are also removed from the
  backup (mirror semantics), e.g.:

  ```bash
  rsync -a --delete /path/to/source/ /path/to/repo/
  ```

### Output

- Keep output minimal. The script prints only what matters (which files
  changed / the commit result) — not a full noisy file listing.

## Part 2: Change Briefs Pipeline

A collector + curator + distributor flow that sends dated change briefs to
other agents so they can apply updates in order.

1. **Collector:** a script diffs `linux-hermes-backup` over the last 7 days to
   identify what changed.
2. **Curate:** an agent cron curates the diff into a dated brief (e.g.
   `2026-08-02`).
3. **Publish:** the brief is pushed to the `agent-change-briefs` repo.
4. **Apply:** other agents clone the repo and apply the briefs in order
   (oldest first), so no update is skipped or applied out of sequence.

## Pitfalls

- `master` vs `main` — match what the remote actually uses; this pattern
  standardizes on `master`.
- Embedding a token in the remote URL leaks credentials into `.git/config`
  and shell history — always use the credential store.
- Without `--delete`, rsync accumulates stale files and the backup drifts
  from the source.
- Verify the backup by cloning fresh or reading the repo listing back before
  declaring success.
