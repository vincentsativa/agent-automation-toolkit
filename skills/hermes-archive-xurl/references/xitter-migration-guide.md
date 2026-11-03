# Xitter → xurl Migration Guide

## Context

The `xitter` skill (wrapping `x-cli` from Infatoshi) has been deprecated and replaced by `xurl` (the official X developer platform CLI). This reference documents the unique content from the deprecated xitter skill that is not yet covered by xurl's SKILL.md.

## Credential Setup (x-cli alternative path)

If for any reason the user must use `x-cli` instead of `xurl`:

Five X API credentials are needed:
- `X_API_KEY` (consumer key)
- `X_API_SECRET` (consumer secret)
- `X_BEARER_TOKEN`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

Install: `uv tool install git+https://github.com/Infatoshi/x-cli.git`

The CLI looks for credentials in `~/.config/x-cli/.env`:
```bash
mkdir -p ~/.config/x-cli
ln -sf ~/.hermes/.env ~/.config/x-cli/.env
```

Common `x-cli` commands (use `xurl` instead wherever possible):
- `x-cli tweet post "text"` → `xurl post "text"`
- `x-cli tweet get <id>` → `xurl read <id>`
- `x-cli tweet search "query" --max N` → `xurl search "query" -n N`
- `x-cli user get <handle>` → `xurl user <handle>`

## Why xurl won

1. **Official maintainer**, xurl is maintained by the X developer platform team
2. **OAuth 2.0 PKCE**, auto-refreshing tokens, no manual token rotation
3. **Larger API surface**, DMs, media upload, raw v2 endpoint access, streaming
4. **Single-command auth**, `xurl auth oauth2` vs 5 env vars for x-cli