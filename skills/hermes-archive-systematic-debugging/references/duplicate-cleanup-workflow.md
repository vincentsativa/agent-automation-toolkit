# Duplicate Cleanup Workflow

When asked to delete a duplicate file, directory, or tree, follow this process to avoid data loss.

## The Problem

"Just delete it" without investigation is the same class of error as "just fix it" without root cause. Duplicates often contain unique data, newer versions, orphaned support files, or content that was never migrated to the canonical location.

## The Workflow

### Phase 1: Discovery

Find all copies of the thing in question:

```bash
# Find by exact name
find /path -type d -name "target-name" 2>/dev/null

# Find by pattern
find /path -type d -name "target*" 2>/dev/null
```

### Phase 2: Inventory

For each copy, check:
- **Size and timestamp**, which is newer? Which is larger?
- **SKILL.md content**, diff the main files
- **Supporting files**, does one have references/, scripts/, templates/ that the other doesn't?
- **Hidden files**, .git/, .archive/, .curator_backups/

```bash
# Compare sizes and timestamps
stat -c '%Y %y %n' copy1/SKILL.md
stat -c '%Y %y %n' copy2/SKILL.md

# List all files in each copy
find copy1 -type f | sort
find copy2 -type f | sort

# Diff the main content
diff copy1/SKILL.md copy2/SKILL.md
```

### Phase 3: Rescue

Before deleting anything:

1. **Copy unique skills** from the duplicate to the primary (if the duplicate has skills the primary doesn't)
2. **Copy newer versions**, if the duplicate's SKILL.md is newer, copy it over the primary
3. **Copy orphaned support files**, references/, scripts/, templates/ that exist only in the duplicate
4. **Check for archived/backup content**, .archive/, .curator_backups/ may hold files that were removed from the primary

```bash
# Copy a missing skill
cp -r skills/duplicate/skill-name skills/primary/skill-name

# Copy a newer SKILL.md
cp skills/duplicate/skill-name/SKILL.md skills/primary/skill-name/SKILL.md

# Copy orphaned support files
cp skills/duplicate/skill-name/references/foo.md skills/primary/skill-name/references/
```

### Phase 4: Verify

After rescue, confirm the primary tree is complete:

```bash
# Re-run the diff to confirm no remaining differences
diff -rq skills/primary/skill-name skills/duplicate/skill-name 2>/dev/null

# Check the primary has all expected files
find skills/primary/skill-name -type f | sort
```

### Phase 5: Delete

Only now is it safe to remove the duplicate.

## Common Pitfalls

- **Assuming timestamps tell the whole story**, a file with an older timestamp may have content the newer one doesn't. Always diff.
- **Missing support files**, SKILL.md is the main file, but references/, scripts/, templates/ directories may hold unique content. Always check.
- **Nested duplicates**, a `skills/skills/` directory means the entire tree was duplicated. Check every subdirectory, not just the top level.
- **The "it's just a copy" assumption**, duplicates often diverge over time as one copy gets updated and the other doesn't. Never assume they're identical.
