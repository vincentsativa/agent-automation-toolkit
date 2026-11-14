# Proving a browser build is stale before deleting it

Playwright-family browser builds (Chromium, headless shell, Firefox, ffmpeg) live as revision-suffixed directories in one shared registry at `~/.cache/ms-playwright`, written by every package that uses that registry: Python `playwright` and `patchright` under site-packages, the `playwright-core` copies inside hermes-agent's pnpm tree and the Codex runtime, and any npx-fetched copy. Upgrading a package leaves its old build behind, and nothing marks it stale, so ownership has to be read from the packages.

## Recipe

1. Enumerate every manifest and the revisions it declares:

   ```bash
   find /data/home -name browsers.json -path '*playwright*' -not -path '*/ms-playwright/*' 2>/dev/null
   # then, per file: [(b['name'], b['revision']) for b in json.load(open(f))['browsers']]
   ```

2. Read the registry's owner links: `~/.cache/ms-playwright/.links/*` each contains the absolute path of the driver package that registered it. Owners not on disk anymore registered builds nobody can reinstall from.
3. Build the set of referenced revisions. Delete only registry directories whose revision appears in no manifest and no live owner link; keep everything else, including ffmpeg builds, which a different Playwright version may still want.
4. After deleting, run one real launch (headless Chromium, load a `data:` page) rather than trusting the inventory.

## Pitfalls

- Directory mtime is not ownership: a reinstall can write an older revision set later than the current one, so match revision numbers across manifests, never dates.
- A build referenced by only one of several installed Playwright versions still counts as referenced. The cost of a wrong keep is a few hundred MB; the cost of a wrong delete is a tool that fails at its next launch with an "executable doesn't exist" error and needs a network re-download.
- The Codex runtime ships its own Playwright under `~/.cache/codex-runtimes`, and the bundled tool browsers under `~/.hermes/tools/chromium-*` are separate again; neither is part of the shared registry, so leave both alone during registry cleanup.
