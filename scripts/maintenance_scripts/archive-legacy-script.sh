#!/bin/bash

################################################################################
# Script Archival Helper
# Adds deprecation warning and moves script to archive
################################################################################

set -euo pipefail

# Usage check
if [ $# -lt 3 ]; then
    echo "Usage: $0 <script-path> <new-script-name> <category>"
    echo ""
    echo "Example:"
    echo "  $0 scripts/unified-iso-builder.sh build-iso.sh primary-builders"
    echo ""
    echo "Categories:"
    echo "  - primary-builders"
    echo "  - enhancement"
    echo "  - tools"
    echo "  - optimization"
    echo "  - maintenance"
    echo "  - variants"
    echo "  - deprecated"
    exit 1
fi

SCRIPT_PATH="$1"
NEW_SCRIPT_NAME="$2"
CATEGORY="$3"

# Validate inputs
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found: $SCRIPT_PATH"
    exit 1
fi

SCRIPT_NAME=$(basename "$SCRIPT_PATH")
ARCHIVE_DIR="archive/build-scripts-deprecated/$CATEGORY"
ARCHIVE_PATH="$ARCHIVE_DIR/$SCRIPT_NAME"

echo "════════════════════════════════════════════════════════════════════"
echo "Archiving Legacy Script"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Script:      $SCRIPT_NAME"
echo "Replacement: $NEW_SCRIPT_NAME"
echo "Category:    $CATEGORY"
echo "Archive to:  $ARCHIVE_PATH"
echo ""

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Read the original script
ORIGINAL_CONTENT=$(cat "$SCRIPT_PATH")

# Get the shebang line
SHEBANG=$(head -n 1 "$SCRIPT_PATH")

# Get content after shebang
CONTENT_AFTER_SHEBANG=$(tail -n +2 "$SCRIPT_PATH")

# Create deprecation warning
DEPRECATION_WARNING="
################################################################################
# ⚠️  DEPRECATION WARNING
################################################################################
# This script is DEPRECATED and has been archived as of October 23, 2025.
#
# Please use the new consolidated script instead:
#   → ./scripts/$NEW_SCRIPT_NAME
#
# Migration Guide: docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md
# Script Help:     ./scripts/$NEW_SCRIPT_NAME --help
#
# This script remains functional but is no longer maintained.
# It will be removed in a future release.
#
# Original Location: $SCRIPT_PATH
# Archived Date:     $(date '+%Y-%m-%d %H:%M:%S')
################################################################################

echo \"\"
echo \"════════════════════════════════════════════════════════════════════\"
echo \"⚠️  WARNING: DEPRECATED SCRIPT\"
echo \"════════════════════════════════════════════════════════════════════\"
echo \"\"
echo \"This script has been replaced by the new Build System v2.0\"
echo \"\"
echo \"  New script: ./scripts/$NEW_SCRIPT_NAME\"
echo \"  Help:       ./scripts/$NEW_SCRIPT_NAME --help\"
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
    echo "$SHEBANG"
    echo "$DEPRECATION_WARNING"
    echo "$CONTENT_AFTER_SHEBANG"
} > "$ARCHIVE_PATH"

# Make it executable
chmod +x "$ARCHIVE_PATH"

echo "✓ Script archived with deprecation warning"
echo "✓ Location: $ARCHIVE_PATH"
echo ""

# Ask about symlink
read -p "Create symlink at original location? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Calculate relative path from original location to archive
    ORIGINAL_DIR=$(dirname "$SCRIPT_PATH")
    RELATIVE_PATH=$(realpath --relative-to="$ORIGINAL_DIR" "$ARCHIVE_PATH")
    
    # Remove original file
    rm "$SCRIPT_PATH"
    
    # Create symlink
    ln -s "$RELATIVE_PATH" "$SCRIPT_PATH"
    
    echo "✓ Symlink created: $SCRIPT_PATH -> $RELATIVE_PATH"
else
    # Just move the file
    mv "$SCRIPT_PATH" "$ARCHIVE_PATH.backup"
    mv "$ARCHIVE_PATH" "$SCRIPT_PATH"
    echo "✓ Original script replaced with deprecated version"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "✅ Archival Complete!"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Log the archival
LOG_FILE="archive/build-scripts-deprecated/ARCHIVAL_LOG.md"
{
    if [ ! -f "$LOG_FILE" ]; then
        echo "# Script Archival Log"
        echo ""
        echo "Tracking all legacy scripts moved to archive."
        echo ""
        echo "| Date | Script | Replacement | Category | Status |"
        echo "|------|--------|-------------|----------|--------|"
    fi
    echo "| $(date '+%Y-%m-%d') | \`$SCRIPT_NAME\` | \`$NEW_SCRIPT_NAME\` | $CATEGORY | ✅ Archived |"
} >> "$LOG_FILE"

echo "📝 Logged to: $LOG_FILE"
echo ""
