---
name: firebase-storage-setup
description: Use for Firebase Cloud Storage file hosting and delivery.
trigger: "Setting up Firebase storage, uploading/downloading files from Firebase, or hosting files for delivery."
category: devops
---

# Firebase Storage Setup

Firebase Cloud Storage setup. Save service-account JSON to `~/.hermes/secrets/firebase-service-account.json` (chmod 600).

## Install

```
pip install google-cloud-storage firebase-admin
```

## Bucket

Bucket format is `<project-id>.firebasestorage.app` (NOT .appspot.com).

- Project: `gen-lang-client-0237860564`
- Bucket: `gen-lang-client-0237860564.firebasestorage.app`

## Helper Script

`~/.hermes/scripts/firebase-storage.py` with subcommands: `list`, `upload local [remote]`, `download remote [local]`, `cat`, `delete`.

## Pitfalls

- Ensure Storage is enabled in the Firebase Console before API calls (the API can't create it).
- Service-account key is a secret, chmod 600.
