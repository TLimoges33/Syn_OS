#!/bin/bash
################################################################################
# Archive Cleanup Script for SynOS
# Compresses old logs, tarballs, and removes redundant build artifacts
# Expected savings: 3-4GB
#
# Usage:
#   ./archive-cleanup.sh          # Actually perform cleanup
#   ./archive-cleanup.sh --dry-run  # Show what would be done
################################################################################

set -euo pipefail

# Parse arguments
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]] || [[ "${1:-}" == "-n" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

ARCHIVE_BASE="archives/2025-10"
BUILD_DIR="build"

echo "🗂️  SynOS Archive Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create archive structure
echo "📁 Creating archive directories..."
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_BASE"/{logs,tarballs,old-isos,experiments}
else
    echo "  [DRY-RUN] Would create: $ARCHIVE_BASE/{logs,tarballs,old-isos,experiments}"
fi

# Archive old build logs
echo ""
echo "📦 Archiving old build logs..."
if [ -d "$BUILD_DIR/logs/archived" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$ARCHIVE_BASE/logs"
        mv "$BUILD_DIR/logs/archived" "$ARCHIVE_BASE/logs/" 2>/dev/null || true
        echo "  ✓ Moved build/logs/archived"
    else
        SIZE=$(du -sh "$BUILD_DIR/logs/archived" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  [DRY-RUN] Would move build/logs/archived ($SIZE)"
    fi
else
    echo "  • No build/logs/archived directory"
fi

if [ -d "$BUILD_DIR/logs/iso-build" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$ARCHIVE_BASE/logs"
        mv "$BUILD_DIR/logs/iso-build" "$ARCHIVE_BASE/logs/" 2>/dev/null || true
        echo "  ✓ Moved build/logs/iso-build"
    else
        SIZE=$(du -sh "$BUILD_DIR/logs/iso-build" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  [DRY-RUN] Would move build/logs/iso-build ($SIZE)"
    fi
else
    echo "  • No build/logs/iso-build directory"
fi

# Compress tarballs
echo ""
echo "🗜️  Compressing tarballs (tar.gz → tar.xz)..."
COUNT=0
if [ -d "$BUILD_DIR/archives" ]; then
    for tar in "$BUILD_DIR/archives"/*.tar.gz; do
        # Check if glob matched any files
        [ -f "$tar" ] || continue

        BASENAME=$(basename "$tar")
        SIZE=$(du -h "$tar" 2>/dev/null | cut -f1 || echo "unknown")

        if [ "$DRY_RUN" = false ]; then
            echo "  Compressing: $BASENAME ($SIZE)"
            xz -9 "$tar" && COUNT=$((COUNT+1)) || true
        else
            echo "  [DRY-RUN] Would compress: $BASENAME ($SIZE)"
            COUNT=$((COUNT+1))
        fi
    done
fi

if [ $COUNT -eq 0 ]; then
    echo "  • No .tar.gz files found (may already be .tar.xz)"
else
    echo "  ✓ Processed $COUNT tarballs"
fi

# Archive kernel test ISO
echo ""
echo "🧪 Archiving kernel test ISO..."
if [ -d "$BUILD_DIR/isoroot" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$ARCHIVE_BASE/experiments"
        mv "$BUILD_DIR/isoroot" "$ARCHIVE_BASE/experiments/kernel-test-iso" 2>/dev/null || true
        echo "  ✓ Moved build/isoroot"
    else
        SIZE=$(du -sh "$BUILD_DIR/isoroot" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  [DRY-RUN] Would move build/isoroot ($SIZE)"
    fi
else
    echo "  • No kernel test ISO found"
fi

# Remove Parrot ISO
echo ""
echo "🗑️  Removing Parrot remaster ISO..."
if [ -f "$BUILD_DIR/parrot-remaster/Parrot-security-6.4_amd64.iso" ]; then
    if [ "$DRY_RUN" = false ]; then
        rm "$BUILD_DIR/parrot-remaster/Parrot-security-6.4_amd64.iso" 2>/dev/null || true
        echo "  ✓ Removed Parrot ISO"
    else
        SIZE=$(du -sh "$BUILD_DIR/parrot-remaster/Parrot-security-6.4_amd64.iso" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  [DRY-RUN] Would remove Parrot ISO ($SIZE)"
    fi
else
    echo "  • No Parrot remaster ISO found"
fi

# Clean old chroot
echo ""
echo "🧹 Cleaning old chroot artifacts..."
if [ -d "$BUILD_DIR/full-distribution/chroot.old" ]; then
    if [ "$DRY_RUN" = false ]; then
        rm -rf "$BUILD_DIR/full-distribution/chroot.old" 2>/dev/null || true
        echo "  ✓ Removed chroot.old"
    else
        SIZE=$(du -sh "$BUILD_DIR/full-distribution/chroot.old" 2>/dev/null | cut -f1 || echo "unknown")
        echo "  [DRY-RUN] Would remove chroot.old ($SIZE)"
    fi
else
    echo "  • No old chroot artifacts found"
fi

# Create README
echo ""
echo "📋 Creating archive index..."
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_BASE"
    cat > "$ARCHIVE_BASE/README.md" << 'ENDMARKER'
# SynOS Build Archives (October 2025)

**Date:** Auto-generated
**Purpose:** Historical build logs, compressed artifacts, superseded ISOs

## Contents

- `logs/` - Old build logs (archived, iso-build attempts)
- `tarballs/` - Compressed build artifacts (tar.xz format)
- `old-isos/` - Superseded ISO builds
- `experiments/` - Experimental builds (kernel-test-iso, etc)

## Retention Policy

- **Logs:** Keep 6 months, then delete
- **Tarballs:** Keep 1 year
- **ISOs:** Keep latest 3 in build/, rest here for 3-12 months
- **Experiments:** Keep 1 year unless referenced

## Disk Savings

Expected: ~3-4GB freed from build/

## Restoring Files

```bash
# Restore a log
cp archives/2025-10/logs/some-log.txt build/logs/

# Extract a tarball
xz -d archives/2025-10/tarballs/archive.tar.xz
tar -xf archives/2025-10/tarballs/archive.tar
```

---
Created by: scripts/utilities/archive-cleanup.sh
ENDMARKER
    echo "  ✓ Created $ARCHIVE_BASE/README.md"
else
    echo "  [DRY-RUN] Would create: $ARCHIVE_BASE/README.md"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cleanup complete!"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo "📊 Disk Usage:"
    if [ -d "$ARCHIVE_BASE" ]; then
        du -sh "$ARCHIVE_BASE" 2>/dev/null || echo "  archives/: (calculating...)"
    fi
    if [ -d "$BUILD_DIR" ]; then
        du -sh "$BUILD_DIR" 2>/dev/null || echo "  build/: (calculating...)"
    fi
else
    echo "🔍 This was a DRY RUN - no changes were made"
    echo "   Run without --dry-run to actually perform cleanup"
fi

echo ""
