# Archived Build Scripts

**Date Archived:** October 24, 2025
**Reason:** Replaced by Build System v2.0 and enhanced build-full-distribution.sh

## Replacements

**Primary Builders:**
- `unified-iso-builder.sh` → `scripts/build-iso.sh`
- `comprehensive-prebuild-test.sh` → `scripts/testing/verify-build.sh`

**Ultimate Builds:**
- `ultimate-final-master-developer-v1.0-build.sh` → Enhanced `scripts/build-full-distribution.sh`

**Kernel Fixes:**
- All `fix-phase*.sh` scripts → Issues resolved in source code
- `quick-fix-kernel-modules.sh` → Proper module architecture
- `reorganize-kernel-src.sh` → Proper structure from start

**One-Time Tools:**
- Migration tools → Migration complete, no longer needed

## Migration Guide

See:
- `docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md`
- `docs/LEGACY_SCRIPTS_CATALOG.md`
- `docs/ULTIMATE_BUILDS_ANALYSIS.md`

## Usage

**Do not use these scripts.** Use the new consolidated scripts instead:

```bash
# Standard builds
./scripts/build-iso.sh
./scripts/build-kernel-only.sh
./scripts/build-full-distribution.sh

# Testing
./scripts/testing/verify-build.sh
./scripts/testing/test-iso.sh

# Help
./scripts/build-iso.sh --help
```
