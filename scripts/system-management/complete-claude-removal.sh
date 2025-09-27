#!/bin/bash
# Complete Claude Removal from SynOS Codebase
# Removes ALL Claude-related files including archives

echo "🗑️  COMPLETE CLAUDE REMOVAL FROM SYNOS CODEBASE"
echo "================================================"
echo "This will remove ALL Claude files including archives"
echo ""

read -p "Are you sure you want to delete ALL Claude files? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🔍 Finding all Claude-related files..."

# Find all Claude files
CLAUDE_FILES=$(find /home/diablorain/Syn_OS -name "*claude*" -type f 2>/dev/null)

if [ -z "$CLAUDE_FILES" ]; then
    echo "✅ No Claude files found"
    exit 0
fi

echo "📊 Found $(echo "$CLAUDE_FILES" | wc -l) Claude-related files"
echo ""

# Show what will be deleted
echo "📋 Files to be deleted:"
echo "$CLAUDE_FILES" | head -20
if [ $(echo "$CLAUDE_FILES" | wc -l) -gt 20 ]; then
    echo "... and $(( $(echo "$CLAUDE_FILES" | wc -l) - 20 )) more files"
fi
echo ""

read -p "Proceed with deletion? (yes/no): " final_confirm
if [ "$final_confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🗑️  Deleting Claude files..."

# Delete all Claude files
echo "$CLAUDE_FILES" | while read -r file; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✅ Deleted: $file"
    fi
done

echo ""
echo "🔍 Checking for any remaining Claude references in file contents..."

# Search for Claude references in remaining files (excluding binary files)
CLAUDE_REFS=$(grep -r -l "claude\|Claude\|CLAUDE" /home/diablorain/Syn_OS \
    --exclude-dir=.git \
    --exclude="*.bin" \
    --exclude="*.so" \
    --exclude="*.iso" \
    --exclude="*.img" \
    2>/dev/null | head -10)

if [ ! -z "$CLAUDE_REFS" ]; then
    echo "⚠️  Found files with Claude references in content:"
    echo "$CLAUDE_REFS"
    echo ""
    read -p "Remove Claude references from these files? (yes/no): " clean_refs
    if [ "$clean_refs" = "yes" ]; then
        echo "$CLAUDE_REFS" | while read -r file; do
            if [ -f "$file" ]; then
                # Create backup
                cp "$file" "$file.backup"
                # Remove lines containing Claude references
                sed -i '/[Cc]laude/d' "$file"
                echo "  ✅ Cleaned: $file"
            fi
        done
    fi
fi

echo ""
echo "🧹 Removing empty directories..."
find /home/diablorain/Syn_OS -type d -empty -delete 2>/dev/null

echo ""
echo "✅ CLAUDE REMOVAL COMPLETE!"
echo "=========================="
echo ""

# Final verification
REMAINING=$(find /home/diablorain/Syn_OS -name "*claude*" -type f 2>/dev/null)
if [ -z "$REMAINING" ]; then
    echo "✅ No Claude files remain in the codebase"
else
    echo "⚠️  Some Claude files still exist:"
    echo "$REMAINING"
fi

echo ""
echo "📊 Cleanup Summary:"
echo "  - Deleted all Claude-named files"
echo "  - Cleaned Claude references from content (if requested)"
echo "  - Removed empty directories" 
echo "  - SynOS codebase is now Claude-free"
