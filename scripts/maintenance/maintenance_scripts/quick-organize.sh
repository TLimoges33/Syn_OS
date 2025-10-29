#!/bin/bash
################################################################################
# Quick Scripts Organization
# Organizes scripts directory - simpler version
################################################################################

set -uo pipefail  # Don't exit on errors, but catch undefined variables

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="/home/diablorain/Syn_OS"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
ARCHIVE_DIR="$PROJECT_ROOT/archive/build-scripts-deprecated"

echo ""
echo -e "${CYAN}🏗️  Quick Scripts Organization${NC}"
echo ""

# Create archive directories
mkdir -p "$ARCHIVE_DIR/primary-builders"
mkdir -p "$ARCHIVE_DIR/kernel-fixes"
mkdir -p "$ARCHIVE_DIR/one-time-tools"
mkdir -p "$ARCHIVE_DIR/ultimate-builds"
mkdir -p "$SCRIPTS_DIR/fixes"
mkdir -p "$SCRIPTS_DIR/setup"

echo -e "${CYAN}Step 1: Archiving deprecated scripts...${NC}"
echo ""

# Function to safely archive
safe_archive() {
    local src="$1"
    local dest_dir="$2"
    local name=$(basename "$src")

    if [ -f "$src" ]; then
        echo -e "  ${YELLOW}→${NC} Archiving: $name"
        mv "$src" "$dest_dir/" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Archived"
        return 0
    else
        echo -e "  ${YELLOW}⊘${NC} Skip: $name (not found)"
        return 1
    fi
}

# Archive deprecated build scripts
echo "Legacy builders:"
safe_archive "$SCRIPTS_DIR/unified-iso-builder.sh" "$ARCHIVE_DIR/primary-builders"
safe_archive "$SCRIPTS_DIR/comprehensive-prebuild-test.sh" "$ARCHIVE_DIR/primary-builders"

echo ""
echo "Kernel fix scripts:"
safe_archive "$SCRIPTS_DIR/fix-phase1-tostring.sh" "$ARCHIVE_DIR/kernel-fixes"
safe_archive "$SCRIPTS_DIR/fix-phase3-structures.sh" "$ARCHIVE_DIR/kernel-fixes"
safe_archive "$SCRIPTS_DIR/fix-phase4-constructors.sh" "$ARCHIVE_DIR/kernel-fixes"
safe_archive "$SCRIPTS_DIR/quick-fix-kernel-modules.sh" "$ARCHIVE_DIR/kernel-fixes"
safe_archive "$SCRIPTS_DIR/reorganize-kernel-src.sh" "$ARCHIVE_DIR/kernel-fixes"

echo ""
echo "One-time migration tools:"
safe_archive "$SCRIPTS_DIR/batch-archive-legacy-scripts.sh" "$ARCHIVE_DIR/one-time-tools"
safe_archive "$SCRIPTS_DIR/catalog-legacy-scripts.sh" "$ARCHIVE_DIR/one-time-tools"

echo ""
echo "Ultimate builds:"
safe_archive "$SCRIPTS_DIR/02-build/core/ultimate-final-master-developer-v1.0-build.sh" "$ARCHIVE_DIR/ultimate-builds"

echo ""
echo -e "${CYAN}Step 2: Organizing active scripts...${NC}"
echo ""

# Function to safely move
safe_move() {
    local src="$1"
    local dest_dir="$2"
    local name=$(basename "$src")

    if [ -f "$src" ]; then
        if [ "$(dirname "$src")" != "$dest_dir" ]; then
            echo -e "  ${YELLOW}→${NC} Moving: $name"
            mv "$src" "$dest_dir/" 2>/dev/null || true
            echo -e "  ${GREEN}✓${NC} Moved to $(basename "$dest_dir")/"
            return 0
        else
            echo -e "  ${GREEN}✓${NC} Already in place: $name"
            return 0
        fi
    else
        echo -e "  ${YELLOW}⊘${NC} Skip: $name (not found)"
        return 1
    fi
}

echo "Emergency fixes → fixes/:"
safe_move "$SCRIPTS_DIR/ONE-LINE-FIX.sh" "$SCRIPTS_DIR/fixes"
safe_move "$SCRIPTS_DIR/quick-terminal-fix.sh" "$SCRIPTS_DIR/fixes"
safe_move "$SCRIPTS_DIR/fix-terminal-environment.sh" "$SCRIPTS_DIR/fixes"
safe_move "$SCRIPTS_DIR/fix-dev-null.sh" "$SCRIPTS_DIR/fixes"

echo ""
echo "Setup scripts → setup/:"
safe_move "$SCRIPTS_DIR/install-ai-libraries.sh" "$SCRIPTS_DIR/setup"
safe_move "$SCRIPTS_DIR/install-ai-libraries-auto.sh" "$SCRIPTS_DIR/setup"
safe_move "$SCRIPTS_DIR/setup-wiki-security.sh" "$SCRIPTS_DIR/setup"
safe_move "$SCRIPTS_DIR/wiki-backup.sh" "$SCRIPTS_DIR/setup"
safe_move "$SCRIPTS_DIR/apply-permanent-limits.sh" "$SCRIPTS_DIR/setup"

echo ""
echo "Utilities → utilities/:"
safe_move "$SCRIPTS_DIR/monitor-build.sh" "$SCRIPTS_DIR/utilities"
safe_move "$SCRIPTS_DIR/check-dev-health.sh" "$SCRIPTS_DIR/utilities"
safe_move "$SCRIPTS_DIR/quick-status.sh" "$SCRIPTS_DIR/utilities"

echo ""
echo "Testing → testing/:"
safe_move "$SCRIPTS_DIR/test-iso.sh" "$SCRIPTS_DIR/testing"
safe_move "$SCRIPTS_DIR/verify-tools.sh" "$SCRIPTS_DIR/testing"
safe_move "$SCRIPTS_DIR/quick-validate-v2.sh" "$SCRIPTS_DIR/testing"
safe_move "$SCRIPTS_DIR/test-build-system-v2.sh" "$SCRIPTS_DIR/testing"

echo ""
echo -e "${CYAN}Step 3: Creating archive documentation...${NC}"

# Create archive README
cat > "$ARCHIVE_DIR/README.md" << 'EOF'
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
EOF

echo -e "  ${GREEN}✓${NC} Created archive/build-scripts-deprecated/README.md"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            ✅  Organization Complete!                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Archived to archive/build-scripts-deprecated/:"
echo "  • Legacy builders"
echo "  • Kernel fix scripts"
echo "  • One-time migration tools"
echo "  • Ultimate builds"
echo ""

echo "Organized into subdirectories:"
echo "  • scripts/fixes/ - Emergency fixes"
echo "  • scripts/setup/ - Setup & installation"
echo "  • scripts/utilities/ - Monitoring & health"
echo "  • scripts/testing/ - Testing & validation"
echo ""

echo "Active build scripts (in root):"
ls -1 "$SCRIPTS_DIR"/*.sh 2>/dev/null | head -10 || echo "  (none)"
echo ""

echo -e "${CYAN}Next: Enhance build-full-distribution.sh with ultimate features${NC}"
echo ""
