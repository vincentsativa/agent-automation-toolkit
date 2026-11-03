# GitHub Authentication, Detailed Reference

## SSH Key Authentication (Full Setup)

Generate a key:
```
ssh-keygen -t ed25519 -C "your@email.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

Add the public key at https://github.com/settings/keys

Test: `ssh -T git@github.com`

Configure git to use SSH:
```
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

## Token Extraction from Git Credentials

```
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```