# Phase 6: Script Archival Progress

**Date Started:** October 23, 2025  
**Status:** In Progress  
**Approach:** Adding deprecation warnings to existing scripts

---

## Strategy Update

Instead of physically moving all 68 scripts to an archive directory, we're taking a more practical approach:

1. **Add deprecation warnings** to the most commonly used legacy scripts
2. **Leave scripts in place** for backward compatibility
3. **Warn users** about the new consolidated system
4. **Give 5-second countdown** to cancel and use new scripts
5. **Continue execution** if user doesn't cancel

This approach:

-   ✅ Maintains backward compatibility
-   ✅ Gently guides users to new system
-   ✅ Doesn't break existing workflows
-   ✅ Provides clear migration path
-   ✅ Can be done incrementally

---

## Scripts with Deprecation Warnings Added

### Primary Builders

| Script                           | Status  | Replacement    | Notes                                         |
| -------------------------------- | ------- | -------------- | --------------------------------------------- |
| `scripts/unified-iso-builder.sh` | ✅ Done | `build-iso.sh` | Most critical - users see warning immediately |

### Next Priority

The following scripts should get deprecation warnings next (if they're actively used):

1. `scripts/02-build/core/build-synos-ultimate-iso.sh` → `build-iso.sh`
2. `scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh` → `build-full-linux.sh`
3. Any other scripts users commonly run

---

## Deprecation Warning Template

```bash
#!/bin/bash

################################################################################
# ⚠️  DEPRECATION WARNING
################################################################################
# This script is DEPRECATED and archived as of October 23, 2025.
#
# Please use the new consolidated Build System v2.0 instead:
#   → ./scripts/[NEW_SCRIPT_NAME]
#
# Migration Guide: docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md
# Script Help:     ./scripts/[NEW_SCRIPT_NAME] --help
#
# This script remains functional but is no longer maintained.
# It will be removed in a future release.
################################################################################

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "⚠️  WARNING: DEPRECATED SCRIPT"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "This script has been replaced by the new Build System v2.0"
echo ""
echo "  New script: ./scripts/[NEW_SCRIPT_NAME]"
echo "  Help:       ./scripts/[NEW_SCRIPT_NAME] --help"
echo "  Migration:  docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md"
echo ""
echo "This script will continue running in 5 seconds..."
echo "Press Ctrl+C to cancel and use the new scripts instead."
echo ""
sleep 5
echo "Continuing with deprecated script..."
echo ""

# [Original script continues here...]
```

---

## User Experience

When a user runs a deprecated script:

```bash
$ ./scripts/unified-iso-builder.sh

════════════════════════════════════════════════════════════════════
⚠️  WARNING: DEPRECATED SCRIPT
════════════════════════════════════════════════════════════════════

This script has been replaced by the new Build System v2.0

  Recommended: ./scripts/build-iso.sh
  Quick test:  ./scripts/build-kernel-only.sh
  Full build:  ./scripts/build-full-linux.sh

  Help:        ./scripts/build-iso.sh --help
  Migration:   docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md

This script will continue running in 5 seconds...
Press Ctrl+C to cancel and use the new scripts instead.

Continuing with deprecated unified-iso-builder.sh...

[Script continues normally...]
```

This gives users:

-   Clear warning they're using old code
-   Specific alternatives to use
-   Links to help and migration docs
-   Chance to cancel (Ctrl+C)
-   Graceful fallback if they don't cancel

---

## Next Steps

### Immediate (Stage 3 cont'd)

1. ✅ Add deprecation warning to `unified-iso-builder.sh`
2. ⏳ Monitor usage to see if other scripts need warnings
3. ⏳ Add warnings to 2-3 other commonly used scripts

### Stage 6: Regression Testing (Next Priority)

Focus should shift to testing the NEW consolidated scripts:

1. **Test build-kernel-only.sh**

    - Verify it builds kernel ISO in 5-10 minutes
    - Test --help, --version, --debug options
    - Check error handling

2. **Test build-iso.sh**

    - Verify standard ISO build (20-30 minutes)
    - Test all command-line options
    - Verify cleanup on error

3. **Test build-full-linux.sh**

    - Full distribution build
    - All variants work
    - Integration testing

4. **Test testing/verify-build.sh**

    - Environment verification
    - All checks work
    - Clear error messages

5. **Test testing/test-iso.sh**

    - QEMU testing works
    - All test levels functional
    - Screenshots capture correctly

6. **Test maintenance scripts**

    - clean-builds.sh (interactive and automated)
    - archive-old-isos.sh (archiving works)

7. **Test specialized tools**
    - sign-iso.sh (GPG signing)
    - docker/build-docker.sh (container builds)

### Stage 7: Performance Benchmarks

-   Measure actual build times
-   Compare with legacy (if possible)
-   Document metrics

### Stage 8: Final Cleanup

-   Remove TODO comments from new scripts
-   Run shellcheck on all 10 scripts
-   Final documentation review

### Stage 9: Release

-   Tag v2.0.0-consolidated
-   Create release notes
-   Announcement

---

## Metrics

### Deprecation Warnings

-   **Added:** 1 script (unified-iso-builder.sh)
-   **Remaining:** ~5-10 commonly used scripts (as needed)
-   **Total legacy scripts:** 68 (most don't need warnings if unused)

### Testing Priority

-   **10 new consolidated scripts** - Must all work perfectly
-   **4-6 hours** estimated for comprehensive testing

### Overall Progress

-   **Phase 6:** 80% → 85% (with deprecation warning added)
-   **Stage 3:** 0% → 15% (started deprecation warnings)
-   **Overall Project:** 97% → 97.5%

---

## Decision Rationale

**Why not move all 68 scripts?**

-   Many scripts may not be used anymore
-   Moving creates compatibility issues
-   In-place deprecation is gentler
-   Users see warnings when they actually run scripts
-   Can be done incrementally based on actual usage

**Why 5-second countdown?**

-   Gives users time to read the message
-   Provides opportunity to cancel
-   Doesn't completely block legacy workflows
-   Encourages but doesn't force migration

**Why keep scripts functional?**

-   Backward compatibility
-   Gradual migration period
-   Less disruptive to users
-   Can remove in future major version

---

_Last Updated: October 23, 2025_
_Next: Focus on regression testing of new consolidated scripts_
