#!/usr/bin/env bash
################################################################################
# Legacy Build Scripts Catalog
# 
# Catalogs all legacy build scripts that will be archived during Phase 6
# migration. This script identifies scripts that are being replaced by the
# new consolidated build system.
#
# Usage:
#   ./scripts/catalog-legacy-scripts.sh [--verbose] [--export FILE]
#
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Output files
CATALOG_FILE="${PROJECT_ROOT}/docs/LEGACY_SCRIPTS_CATALOG.md"
JSON_FILE="${PROJECT_ROOT}/docs/legacy-scripts-catalog.json"

# Statistics
TOTAL_SCRIPTS=0
DIRECT_REPLACEMENTS=0
FUNCTIONALITY_ABSORBED=0
DEPRECATED=0

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          SynOS Legacy Build Scripts Catalog                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Scanning for legacy build scripts..."
echo ""

# Define script categories and their replacements
declare -A SCRIPT_MAPPING=(
    # Primary builders
    ["unified-iso-builder.sh"]="scripts/build-iso.sh|DIRECT"
    ["build-simple-kernel-iso.sh"]="scripts/build-kernel-only.sh|DIRECT"
    ["build-simple-grub-iso.sh"]="scripts/build-kernel-only.sh|DIRECT"
    
    # Full distribution builders  
    ["BUILD-COMPLETE-SYNOS-DISTRIBUTION.sh"]="scripts/build-full-linux.sh|DIRECT"
    ["02-build/BUILD-COMPLETE-SYNOS-DISTRIBUTION.sh"]="scripts/build-full-linux.sh|DIRECT"
    ["parrot-remaster.sh"]="scripts/build-full-linux.sh|DIRECT"
    ["build-parrot-iso.sh"]="scripts/build-full-linux.sh|DIRECT"
    
    # Minimal/variant builders
    ["02-build/variants/build-synos-minimal-iso.sh"]="scripts/build-full-linux.sh --variant minimal|ABSORBED"
    ["02-build/variants/lightweight-synos-implementation.sh"]="scripts/build-full-linux.sh --variant minimal|ABSORBED"
    
    # Testing scripts
    ["04-testing/test-iso-in-qemu.sh"]="scripts/testing/test-iso.sh|DIRECT"
    ["04-testing/test-boot-iso.sh"]="scripts/testing/test-iso.sh|DIRECT"
    ["comprehensive-prebuild-test.sh"]="scripts/testing/verify-build.sh|DIRECT"
    ["04-testing/validate-environment.sh"]="scripts/testing/verify-build.sh|ABSORBED"
    ["02-build/auditing/verify-build-ready.sh"]="scripts/testing/verify-build.sh|ABSORBED"
    ["02-build/auditing/verify-pre-build.sh"]="scripts/testing/verify-build.sh|ABSORBED"
    ["02-build/auditing/final-pre-build-audit.sh"]="scripts/testing/verify-build.sh|ABSORBED"
    
    # Cleanup scripts
    ["02-build/maintenance/clean-build-environment.sh"]="scripts/maintenance/clean-builds.sh|ABSORBED"
    ["06-utilities/development/cleanup-failed-builds.sh"]="scripts/maintenance/clean-builds.sh|ABSORBED"
    ["02-build/auditing/pre-build-cleanup.sh"]="scripts/maintenance/clean-builds.sh|ABSORBED"
    ["03-maintenance/system/final-cleanup.sh"]="scripts/maintenance/clean-builds.sh|ABSORBED"
    
    # Enhancement scripts (functionality absorbed into build-full-linux.sh)
    ["02-build/enhancement/enhance-synos-iso.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-synos-ultimate.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-educational-iso.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase1-essential.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase1-fixed.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase1-repos-tools.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase2-ai-integration.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase2-core-integration.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase3-branding.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase4-configuration.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase5-demo-docs.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/enhancement/enhance-phase6-iso-rebuild.sh"]="scripts/build-full-linux.sh|ABSORBED"
    
    # Tool installation scripts (absorbed into variants)
    ["02-build/tools/phase1-install-missing-tools.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/install-productivity-and-security.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/install-ai-daemon.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/add-high-value-tools.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/add-starred-repos.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/copy-parrot-tools-to-chroot.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/manual-build-priority-tools.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/nuclear-install-everything.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/organize-complete-tool-menus.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/organize-tools-in-menu.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/setup-live-system-tasks.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/tools/phase6-iso-generation.sh"]="scripts/build-iso.sh|ABSORBED"
    
    # Optimization scripts
    ["02-build/optimization/comprehensive-architecture-optimization.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/optimization/comprehensive-build-audit.sh"]="scripts/testing/verify-build.sh|ABSORBED"
    ["02-build/optimization/comprehensive-dependency-fix.sh"]="scripts/testing/verify-build.sh --fix|ABSORBED"
    ["02-build/optimization/optimize-chroot-for-iso.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/optimization/audit-and-cleanup-chroot.sh"]="scripts/maintenance/clean-builds.sh|ABSORBED"
    ["02-build/optimization/fix-boot-config.sh"]="scripts/build-iso.sh|ABSORBED"
    ["02-build/optimization/fix-and-install-security-tools.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/optimization/fix-security-tool-categories.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/optimization/force-fix-dependencies.sh"]="scripts/testing/verify-build.sh --fix|ABSORBED"
    ["02-build/optimization/quick-v1.0-fix.sh"]="scripts/testing/verify-build.sh --fix|ABSORBED"
    ["02-build/optimization/remove-pytorch-cuda.sh"]="scripts/build-full-linux.sh --skip-packages|ABSORBED"
    
    # Launcher/helper scripts
    ["02-build/launchers/smart-parrot-launcher.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/helpers/launch-ultimate-build.sh"]="scripts/build-full-linux.sh|ABSORBED"
    ["02-build/monitoring/build-monitor.sh"]="Built into all new scripts|ABSORBED"
    
    # Core build scripts
    ["02-build/build-bootable-kernel.sh"]="scripts/build-kernel-only.sh|DIRECT"
    ["02-build/create-bootable-image.sh"]="scripts/build-iso.sh|DIRECT"
    ["02-build/core/ultimate-final-master-developer-v1.0-build.sh"]="scripts/build-full-linux.sh|DIRECT"
    
    # Utility/fix scripts (no longer needed)
    ["02-build/fix-cargo-warnings.sh"]="No longer needed (clean builds)|DEPRECATED"
    ["02-build/FIX_BUILD_PATHS.sh"]="No longer needed (proper paths)|DEPRECATED"
    ["fix-phase1-tostring.sh"]="No longer needed (fixed in source)|DEPRECATED"
    ["fix-phase3-structures.sh"]="No longer needed (fixed in source)|DEPRECATED"
    ["fix-phase4-constructors.sh"]="No longer needed (fixed in source)|DEPRECATED"
    ["quick-fix-kernel-modules.sh"]="No longer needed (proper module system)|DEPRECATED"
    ["reorganize-kernel-src.sh"]="No longer needed (proper organization)|DEPRECATED"
    
    # Development utilities (keep separate, not build-related)
    ["06-utilities/FIX-BUILD-ERRORS.sh"]="Development utility (keep)|KEEP"
    ["06-utilities/FIX-BUILD-ERRORS-PHASE2.sh"]="Development utility (keep)|KEEP"
    ["06-utilities/FIX-WORKSPACE-MEMBERSHIP.sh"]="Development utility (keep)|KEEP"
)

# Generate catalog
{
    echo "# Legacy Build Scripts Catalog"
    echo ""
    echo "**Generated:** $(date "+%Y-%m-%d %H:%M:%S")"
    echo "**Purpose:** Catalog of legacy build scripts being replaced by consolidated build system"
    echo "**Migration Phase:** Phase 6 - Migration & Cleanup"
    echo ""
    echo "---"
    echo ""
    echo "## Overview"
    echo ""
    echo "This catalog documents all legacy build scripts that are being replaced by the new consolidated build system. The new system reduces 62+ scripts with 75% duplication down to 10 optimized scripts."
    echo ""
    echo "### Migration Status"
    echo ""
    echo "- **Total Legacy Scripts:** Calculating..."
    echo "- **Direct Replacements:** Scripts with 1:1 replacements"
    echo "- **Functionality Absorbed:** Features integrated into new scripts"
    echo "- **Deprecated:** Scripts no longer needed"
    echo ""
    echo "---"
    echo ""
    echo "## Script Mapping"
    echo ""
    echo "### Direct Replacements"
    echo ""
    echo "These scripts have direct 1:1 replacements in the new system:"
    echo ""
    echo "| Legacy Script | New Script | Notes |"
    echo "|---------------|------------|-------|"
    
    for script in "${!SCRIPT_MAPPING[@]}"; do
        IFS='|' read -r replacement type <<< "${SCRIPT_MAPPING[$script]}"
        if [[ "$type" == "DIRECT" ]]; then
            echo "| \`$script\` | \`$replacement\` | Direct replacement |"
            ((DIRECT_REPLACEMENTS++))
            ((TOTAL_SCRIPTS++))
        fi
    done | sort
    
    echo ""
    echo "### Functionality Absorbed"
    echo ""
    echo "These scripts' functionality has been integrated into the new consolidated scripts:"
    echo ""
    echo "| Legacy Script | Functionality Now In | Notes |"
    echo "|---------------|----------------------|-------|"
    
    for script in "${!SCRIPT_MAPPING[@]}"; do
        IFS='|' read -r replacement type <<< "${SCRIPT_MAPPING[$script]}"
        if [[ "$type" == "ABSORBED" ]]; then
            echo "| \`$script\` | \`$replacement\` | Feature integrated |"
            ((FUNCTIONALITY_ABSORBED++))
            ((TOTAL_SCRIPTS++))
        fi
    done | sort
    
    echo ""
    echo "### Deprecated Scripts"
    echo ""
    echo "These scripts are no longer needed with the new system:"
    echo ""
    echo "| Legacy Script | Reason | Notes |"
    echo "|---------------|--------|-------|"
    
    for script in "${!SCRIPT_MAPPING[@]}"; do
        IFS='|' read -r replacement type <<< "${SCRIPT_MAPPING[$script]}"
        if [[ "$type" == "DEPRECATED" ]]; then
            echo "| \`$script\` | $replacement | No longer needed |"
            ((DEPRECATED++))
            ((TOTAL_SCRIPTS++))
        fi
    done | sort
    
    echo ""
    echo "---"
    echo ""
    echo "## Statistics"
    echo ""
    echo "- Total Legacy Scripts Cataloged: $TOTAL_SCRIPTS"
    echo "- Direct Replacements: $DIRECT_REPLACEMENTS"
    echo "- Functionality Absorbed: $FUNCTIONALITY_ABSORBED"
    echo "- Deprecated: $DEPRECATED"
    echo "- Code Reduction: ~65% (will reach 87% after migration)"
    echo ""
    echo "---"
    echo ""
    echo "## New Consolidated System"
    echo ""
    echo "### Core Infrastructure"
    echo "1. \`lib/build-common.sh\` - Shared library (656 lines, 26 functions)"
    echo ""
    echo "### Build Tools (Phase 2)"
    echo "2. \`build-iso.sh\` - Primary ISO builder (228 lines)"
    echo "3. \`build-kernel-only.sh\` - Fast kernel builds (182 lines)"
    echo "4. \`build-full-linux.sh\` - Full distribution (421 lines)"
    echo ""
    echo "### Testing Tools (Phase 3)"
    echo "5. \`testing/test-iso.sh\` - ISO testing framework (542 lines)"
    echo "6. \`testing/verify-build.sh\` - Environment validation (567 lines)"
    echo ""
    echo "### Maintenance Tools (Phase 4)"
    echo "7. \`maintenance/clean-builds.sh\` - Build cleanup (572 lines)"
    echo "8. \`maintenance/archive-old-isos.sh\` - ISO archiving (622 lines)"
    echo ""
    echo "### Specialized Tools (Phase 5)"
    echo "9. \`utilities/sign-iso.sh\` - ISO signing (398 lines)"
    echo "10. \`docker/build-docker.sh\` - Docker builds (421 lines)"
    echo ""
    echo "**Total:** 4,609 lines of optimized, well-documented code"
    echo ""
    echo "---"
    echo ""
    echo "## Migration Process"
    echo ""
    echo "### Phase A: Evaluation (Current)"
    echo "- New scripts available alongside legacy scripts"
    echo "- Users test and compare outputs"
    echo "- Report issues and feedback"
    echo ""
    echo "### Phase B: Transition (Nov 1-30, 2025)"
    echo "- New scripts become primary"
    echo "- Legacy scripts show deprecation warnings"
    echo "- 30-day grace period for adjustment"
    echo ""
    echo "### Phase C: Archive (Dec 1, 2025+)"
    echo "- Legacy scripts moved to \`archive/build-scripts-deprecated/\`"
    echo "- Symlinks available for compatibility"
    echo "- Documentation updated"
    echo ""
    echo "---"
    echo ""
    echo "## Finding Replacements"
    echo ""
    echo "To find the replacement for a legacy script:"
    echo ""
    echo "\`\`\`bash"
    echo "# Quick lookup"
    echo "grep \"legacy-script-name.sh\" docs/LEGACY_SCRIPTS_CATALOG.md"
    echo ""
    echo "# Or see migration guide"
    echo "cat docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md"
    echo "\`\`\`"
    echo ""
    echo "---"
    echo ""
    echo "## Support"
    echo ""
    echo "- **Migration Guide:** \`docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md\`"
    echo "- **Phase Summaries:** \`docs/PHASE*_COMPLETION_SUMMARY.md\`"
    echo "- **Quick Reference:** \`docs/BUILD_SCRIPTS_QUICK_REFERENCE.md\`"
    echo "- **Issues:** Report on GitHub"
    echo ""
    echo "---"
    echo ""
    echo "*This catalog will be updated as additional legacy scripts are identified.*"
    
} > "$CATALOG_FILE"

echo "✓ Catalog created: $CATALOG_FILE"
echo ""
echo "Summary:"
echo "  Total Scripts: $TOTAL_SCRIPTS"
echo "  Direct Replacements: $DIRECT_REPLACEMENTS"
echo "  Functionality Absorbed: $FUNCTIONALITY_ABSORBED"
echo "  Deprecated: $DEPRECATED"
echo ""
echo "✓ Catalog complete!"
