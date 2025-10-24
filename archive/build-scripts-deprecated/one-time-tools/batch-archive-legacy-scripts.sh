#!/bin/bash

################################################################################
# Batch Archive All Legacy Scripts
# Archives all 68 legacy scripts according to LEGACY_SCRIPTS_CATALOG.md
################################################################################

set -euo pipefail

PROJECT_ROOT="/home/diablorain/Syn_OS"
cd "$PROJECT_ROOT"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                               ║"
echo "║                   🗂️  LEGACY SCRIPT BATCH ARCHIVAL 🗂️                        ║"
echo "║                                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will archive 68 legacy scripts with deprecation warnings."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Starting batch archival..."
echo ""

ARCHIVED_COUNT=0
FAILED_COUNT=0

# Function to archive a script
archive_script() {
    local script_path="$1"
    local new_script="$2"
    local category="$3"
    
    if [ ! -f "$script_path" ]; then
        echo "⚠️  Not found: $script_path"
        ((FAILED_COUNT++))
        return
    fi
    
    local script_name=$(basename "$script_path")
    local archive_dir="archive/build-scripts-deprecated/$category"
    local archive_path="$archive_dir/$script_name"
    
    # Create archive directory
    mkdir -p "$archive_dir"
    
    echo "📦 Archiving: $script_name → $category/"
    
    # Read the original script
    local shebang=$(head -n 1 "$script_path")
    local content_after_shebang=$(tail -n +2 "$script_path")
    
    # Create deprecation warning
    local deprecation_warning="
################################################################################
# ⚠️  DEPRECATION WARNING
################################################################################
# This script is DEPRECATED and has been archived as of October 23, 2025.
#
# Please use the new consolidated script instead:
#   → ./scripts/$new_script
#
# Migration Guide: docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md
# Script Help:     ./scripts/$new_script --help
#
# This script remains functional but is no longer maintained.
# It will be removed in a future release.
#
# Original Location: $script_path
# Archived Date:     $(date '+%Y-%m-%d %H:%M:%S')
################################################################################

echo \"\"
echo \"════════════════════════════════════════════════════════════════════\"
echo \"⚠️  WARNING: DEPRECATED SCRIPT\"
echo \"════════════════════════════════════════════════════════════════════\"
echo \"\"
echo \"This script has been replaced by the new Build System v2.0\"
echo \"\"
echo \"  New script: ./scripts/$new_script\"
echo \"  Help:       ./scripts/$new_script --help\"
echo \"  Migration:  docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md\"
echo \"\"
echo \"This script will continue running in 5 seconds...\"
echo \"Press Ctrl+C to cancel and use the new script instead.\"
echo \"\"
sleep 5
echo \"Continuing with deprecated script...\"
echo \"\"
"
    
    # Create new file with deprecation warning
    {
        echo "$shebang"
        echo "$deprecation_warning"
        echo "$content_after_shebang"
    } > "$archive_path"
    
    # Make it executable
    chmod +x "$archive_path"
    
    # Move original to backup, replace with archived version
    mv "$script_path" "${script_path}.orig"
    mv "$archive_path" "$script_path"
    
    echo "   ✓ Archived to: $archive_dir/"
    ((ARCHIVED_COUNT++))
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 1: PRIMARY BUILDERS (13 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Primary builders - all map to build-iso.sh or build-full-linux.sh
archive_script "scripts/unified-iso-builder.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/02-build/core/build-synos-ultimate-iso.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh" "build-full-linux.sh" "primary-builders"
archive_script "scripts/02-build/core/ultimate-final-iso-builder.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/02-build/core/full-synos-build.sh" "build-full-linux.sh" "primary-builders"
archive_script "scripts/02-build/core/stable-checkpoint-ultimate-iso-build.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/02-build/core/smart-iso-builder.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/02-build/core/optimized-iso-builder.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/build-scripts/build-custom-iso.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/build-scripts/full-build-cycle.sh" "build-full-linux.sh" "primary-builders"
archive_script "scripts/06-iso/create-synos-iso.sh" "build-iso.sh" "primary-builders"
archive_script "scripts/06-iso/build-minimal-iso.sh" "build-kernel-only.sh" "primary-builders"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 2: ENHANCEMENT SCRIPTS (12 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Enhancement scripts - mostly map to build-full-linux.sh
for phase in {1..8}; do
    archive_script "scripts/enhance-phase${phase}.sh" "build-full-linux.sh" "enhancement"
done
archive_script "scripts/enhance-all.sh" "build-full-linux.sh" "enhancement"
archive_script "scripts/phase7-build.sh" "build-full-linux.sh" "enhancement"
archive_script "scripts/phase8-finalize.sh" "build-full-linux.sh" "enhancement"
archive_script "scripts/comprehensive-enhance-v1.5-v1.8.sh" "build-full-linux.sh" "enhancement"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 3: INSTALLATION TOOLS (12 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Installation tools - map to build-full-linux.sh (includes tools)
archive_script "scripts/install-gamification-v1.5.sh" "build-full-linux.sh" "tools"
archive_script "scripts/install-cloud-infrastructure-v1.6.sh" "build-full-linux.sh" "tools"
archive_script "scripts/install-ai-educational-tutor-v1.7.sh" "build-full-linux.sh" "tools"
archive_script "scripts/install-mobile-app-v1.8.sh" "build-full-linux.sh" "tools"
archive_script "scripts/add-gamification-v1.5.sh" "build-full-linux.sh" "tools"
archive_script "scripts/add-cloud-infrastructure-v1.6.sh" "build-full-linux.sh" "tools"
archive_script "scripts/add-ai-tutor-v1.7.sh" "build-full-linux.sh" "tools"
archive_script "scripts/add-mobile-app-v1.8.sh" "build-full-linux.sh" "tools"
archive_script "scripts/add-security-services.sh" "build-full-linux.sh" "tools"
archive_script "scripts/setup-ai-tutor.sh" "build-full-linux.sh" "tools"
archive_script "scripts/configure-cloud.sh" "build-full-linux.sh" "tools"
archive_script "scripts/integrate-mobile.sh" "build-full-linux.sh" "tools"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 4: OPTIMIZATION SCRIPTS (11 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Optimization scripts - map to various consolidated scripts
archive_script "scripts/comprehensive-system-optimization.sh" "build-iso.sh" "optimization"
archive_script "scripts/optimize-all-integrations.sh" "build-full-linux.sh" "optimization"
archive_script "scripts/optimize-gamification.sh" "build-full-linux.sh" "optimization"
archive_script "scripts/optimize-cloud-infrastructure.sh" "build-full-linux.sh" "optimization"
archive_script "scripts/optimize-ai-tutor.sh" "build-full-linux.sh" "optimization"
archive_script "scripts/optimize-mobile-app.sh" "build-full-linux.sh" "optimization"
archive_script "scripts/optimize-performance.sh" "build-iso.sh" "optimization"
archive_script "scripts/comprehensive-optimization-audit.sh" "testing/verify-build.sh" "optimization"
archive_script "scripts/audit-full-system.sh" "testing/verify-build.sh" "optimization"
archive_script "scripts/security-audit.sh" "testing/verify-build.sh" "optimization"
archive_script "scripts/performance-audit.sh" "testing/verify-build.sh" "optimization"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 5: MAINTENANCE UTILITIES (8 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Maintenance utilities - map to maintenance scripts
archive_script "scripts/verify-integration.sh" "testing/verify-build.sh" "maintenance"
archive_script "scripts/test-v1.5-v1.8.sh" "testing/test-iso.sh" "maintenance"
archive_script "scripts/validate-enhancements.sh" "testing/verify-build.sh" "maintenance"
archive_script "scripts/cleanup-build.sh" "maintenance/clean-builds.sh" "maintenance"
archive_script "scripts/reset-environment.sh" "maintenance/clean-builds.sh" "maintenance"
archive_script "scripts/backup-build.sh" "maintenance/archive-old-isos.sh" "maintenance"
archive_script "scripts/restore-build.sh" "maintenance/archive-old-isos.sh" "maintenance"
archive_script "scripts/monitor-build-progress.sh" "build-iso.sh" "maintenance"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 6: BUILD VARIANTS (5 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Build variants - map to kernel-only or standard ISO
archive_script "scripts/build-minimal.sh" "build-kernel-only.sh" "variants"
archive_script "scripts/build-lightweight.sh" "build-kernel-only.sh" "variants"
archive_script "scripts/build-development.sh" "build-iso.sh" "variants"
archive_script "scripts/build-production.sh" "build-iso.sh" "variants"
archive_script "scripts/quick-prototype-build.sh" "build-kernel-only.sh" "variants"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Category 7: DEPRECATED/BROKEN (7 scripts)"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Deprecated/broken scripts - map to appropriate replacements
archive_script "scripts/fix-boot-issues.sh" "build-iso.sh" "deprecated"
archive_script "scripts/fix-kernel-compilation.sh" "build-kernel-only.sh" "deprecated"
archive_script "scripts/fix-dependencies.sh" "testing/verify-build.sh" "deprecated"
archive_script "scripts/emergency-rebuild.sh" "build-iso.sh" "deprecated"
archive_script "scripts/rollback-changes.sh" "maintenance/clean-builds.sh" "deprecated"
archive_script "scripts/debug-build.sh" "testing/verify-build.sh" "deprecated"
archive_script "scripts/force-clean-build.sh" "maintenance/clean-builds.sh" "deprecated"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "ARCHIVAL SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Successfully archived: $ARCHIVED_COUNT scripts"
echo "⚠️  Failed/not found:     $FAILED_COUNT scripts"
echo ""
echo "All archived scripts have deprecation warnings that:"
echo "  • Show warning message to users"
echo "  • Direct to new consolidated scripts"
echo "  • Link to migration guide"
echo "  • Give 5-second countdown to cancel"
echo "  • Then run the original functionality"
echo ""
echo "Original scripts backed up with .orig extension"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ BATCH ARCHIVAL COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
