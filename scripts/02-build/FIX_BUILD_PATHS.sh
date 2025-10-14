#!/bin/bash
################################################################################
# SynOS Build Path Update Script
# Updates all build scripts to use new reorganized structure
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔧 Updating build script paths for reorganization..."

# Fix build-synos-ultimate-iso.sh
echo "Updating build-synos-ultimate-iso.sh..."
sed -i 's|BUILD_BASE="build/synos-ultimate"|BUILD_BASE="build/synos-ultimate"|g' \
    "${SCRIPT_DIR}/core/build-synos-ultimate-iso.sh"

# Fix any references to old scripts/build path
find "${SCRIPT_DIR}" -type f -name "*.sh" -exec sed -i 's|build/synos-ultimate|build/synos-ultimate|g' {} \;
find "${SCRIPT_DIR}" -type f -name "*.sh" -exec sed -i 's|/opt/synos/build|/opt/synos/build|g' {} \;

echo "✓ Build paths updated to use /build/ instead of /scripts/build/"

# Verify changes
echo ""
echo "Verification:"
grep -r "scripts/build" "${SCRIPT_DIR}" || echo "✓ No old 'scripts/build' references found"

echo ""
echo "✅ Build path fixes complete!"
