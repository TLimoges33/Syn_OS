# Syn_OS Restore Guide

This guide explains how to restore both the active repository state and the historical archive from tags and offline bundles.

## Active repo (current main)

- The active, cleaned history is tracked on `main` in `TLimoges33/Syn_OS-Dev-Team`.
- Historical pointers:
  - `archive/cleaned-history-20250828`
  - `archive/pre-rewrite-main`

To check out the archived snapshot locally:

```bash
# Clone if needed
git clone git@github.com:TLimoges33/Syn_OS-Dev-Team.git
cd Syn_OS-Dev-Team

# Fetch tags and check out archived commit
git fetch --tags
ARCH_SHA=$(git rev-list -n1 archive/cleaned-history-20250828^{})
git switch --detach "$ARCH_SHA"
```

## Vault repository (full historical backup)

- Remote: `git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git`
- Contains full pre-rewrite history and offline artifacts (bundles + checksums if a Release is published).

### Restore from Git bundle

If you have the bundle file locally (or from the Vault release assets):

```bash
# Verify bundle integrity (must match .sha256)
sha256sum -c archive/bundles/wip-*.bundle.sha256

# Create a new repo from the bundle
git clone --mirror archive/bundles/wip-*.bundle synos-archive.mirror
cd synos-archive.mirror

# Optionally add the Vault remote and push all refs
git remote add origin git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git
# Dry-run first
git push --mirror --dry-run origin
# Then push
git push --mirror origin
```

### Restore into a working tree

```bash
# From the mirror above or after fetching from Vault
git clone git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git synos-archive
cd synos-archive
# List historic branches/tags
git show-ref --heads | head
git show-ref --tags | head
# Check out a specific historic branch or tag
git checkout <branch-or-tag>
```

## Notes

- The archive tags `archive/*` point to the commit that matched `origin/main` at cleanup time for traceability.
- Prefer Releases in the Vault to distribute bundle files instead of storing them in the active repo.
- After cloning from a bundle, you can repack/gc:

```bash
git repack -a -d --write-bitmap-index
git gc --prune=now --aggressive
```

If you need help restoring a specific point-in-time snapshot, open an issue with the desired date/branch/tag.