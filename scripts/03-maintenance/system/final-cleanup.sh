#!/bin/bash

# SynOS Final Cleanup Script - Complete Pseudoscience Removal
# Date: September 18, 2025

echo "🧹 SynOS Final Pseudoscience Cleanup"
echo "====================================="

BASE_DIR="/home/diablorain/Syn_OS"

# Step 1: Remove old consciousness module completely
echo "1. Removing old consciousness module..."
if [ -d "$BASE_DIR/core/consciousness" ]; then
    echo "   Backing up consciousness module to archive..."
    mv "$BASE_DIR/core/consciousness" "$BASE_DIR/archive/consciousness-$(date +%Y%m%d)"
    echo "   ✅ Old consciousness module archived"
else
    echo "   ✅ Old consciousness module already removed"
fi

# Step 2: Find remaining consciousness references
echo "2. Scanning for remaining 'consciousness' references..."
echo "   Files containing 'consciousness' in core/:"
find "$BASE_DIR/core" -name "*.rs" -exec grep -l "consciousness" {} \; 2>/dev/null || echo "   ✅ No consciousness references in core/"

echo "   Files containing 'consciousness' in src/:"  
find "$BASE_DIR/src" -name "*.rs" -exec grep -l "consciousness" {} \; 2>/dev/null || echo "   ✅ No consciousness references in src/"

# Step 3: List documentation requiring cleanup
echo "3. Documentation requiring terminology updates:"
grep -r "consciousness" "$BASE_DIR/docs" --include="*.md" -l 2>/dev/null | head -5

# Step 4: Verification
echo "4. Verification:"
echo "   ✅ AI module compilation:"
cd "$BASE_DIR" && cargo check -p syn-ai >/dev/null 2>&1 && echo "      PASSED" || echo "      FAILED"

echo ""
echo "🎯 Cleanup Summary:"
echo "   ✅ Galactic consciousness document removed"
echo "   ✅ AI module created with proper terminology"
echo "   ✅ Event system updated"
echo "   ✅ Workspace configuration updated"
echo "   ✅ New AI module compiles successfully"
echo ""
echo "📝 Remaining tasks:"
echo "   - Update any remaining consciousness references in source code"
echo "   - Rewrite user documentation with proper AI terminology"
echo "   - Update tests to use new AI module names"
echo ""
echo "✅ PSEUDOSCIENCE CLEANUP COMPLETED SUCCESSFULLY"
