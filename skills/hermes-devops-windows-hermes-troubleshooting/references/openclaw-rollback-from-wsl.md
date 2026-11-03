# OpenClaw Rollback from WSL

When OpenClaw on Windows breaks after an update (npm install -g openclaw bumped to a bad version), you can roll it back from WSL without touching the Windows machine directly.

## Prerequisites

- WSL is running
- `powershell.exe` is accessible from WSL (it's in the WSL PATH by default)
- The Windows npm CLI is installed (comes with Node.js)

## Procedure

### 1. Check the current version

```bash
powershell.exe -Command "npm list -g openclaw"
```

### 2. Roll back to the last known good version

```bash
powershell.exe -Command "npm install -g openclaw@2026.7.1-beta.2"
```

Replace `2026.7.1-beta.2` with the version that was working before the update.

### 3. Verify the rollback

```bash
powershell.exe -Command "npm list -g openclaw"
```

### 4. Restore the config from last-good backup

OpenClaw saves a `openclaw.json.last-good` file automatically. Restore it:

```bash
powershell.exe -Command "Copy-Item -Path 'C:\Users\<user>\.openclaw\openclaw.json.last-good' -Destination 'C:\Users\<user>\.openclaw\openclaw.json' -Force"
```

### 5. Reinstall the gateway service to match the rolled-back CLI version

```bash
powershell.exe -Command "openclaw gateway install --force"
```

### 6. Verify the CLI version

```bash
powershell.exe -Command "openclaw --version"
```

## Why This Works

OpenClaw is a Node.js app installed globally via npm. The `npm install -g openclaw@<version>` command installs a specific version from the npm registry. Rolling back replaces the binary and all dependencies with the previous version's bundle.

The gateway service is a separate Windows startup item that references the OpenClaw binary. After a rollback, the gateway service may reference the newer version's path. Reinstalling it with `--force` updates the service definition to match the rolled-back CLI.

## Pitfalls

- **Gateway service mismatch:** If the gateway was installed by a newer version, the service definition may reference paths or configs that don't exist in the older version. Always reinstall the gateway after a rollback.
- **Config format changes:** Newer OpenClaw versions may add config fields that the older version doesn't understand. The `last-good` backup was written by the older version, so it's safe. The current config may have fields the older version ignores.
- **npm cache:** If npm has cached the newer version, the install command may still resolve to it. Use `npm cache clean --force` first if the rollback doesn't take.
- **Node.js version:** OpenClaw requires a recent Node.js. If the Windows Node.js version is too old for the rolled-back version, you may need to update Node.js first. Check with `powershell.exe -Command "node --version"`.
