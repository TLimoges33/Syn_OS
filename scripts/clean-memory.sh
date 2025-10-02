#!/bin/bash
# SynOS Memory Optimization Cleanup Script
# Removes duplicate build artifacts and large temporary files

set -e

echo "🧹 SynOS Memory Cleanup"
echo "======================="
echo ""

# Function to calculate size
get_size() {
    du -sh "$1" 2>/dev/null | cut -f1 || echo "0"
}

total_freed=0

# 1. Remove nested target directories (use workspace target instead)
echo "📦 Removing nested target directories..."
if [ -d "src/kernel/target" ]; then
    size=$(get_size "src/kernel/target")
    echo "  - Removing src/kernel/target ($size)"
    rm -rf src/kernel/target
fi

if [ -d "src/userspace/synpkg/target" ]; then
    size=$(get_size "src/userspace/synpkg/target")
    echo "  - Removing src/userspace/synpkg/target ($size)"
    rm -rf src/userspace/synpkg/target
fi

# 2. Clean fuzz artifacts (keep corpus for testing)
if [ -d "fuzz/artifacts" ]; then
    size=$(get_size "fuzz/artifacts")
    echo "  - Removing fuzz/artifacts ($size)"
    rm -rf fuzz/artifacts/*
fi

# 3. Remove large audit reports
if [ -f "workspace-audit-report.json" ]; then
    size=$(get_size "workspace-audit-report.json")
    echo "  - Removing workspace-audit-report.json ($size)"
    rm -f workspace-audit-report.json
fi

# 4. Optional: Clean main target (asks user)
if [ -d "target" ]; then
    size=$(get_size "target")
    echo ""
    read -p "Clean main target directory ($size)? This will require rebuild. [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cargo clean
        echo "  - Cleaned main target directory"
    fi
fi

echo ""
echo "✅ Memory cleanup complete!"
echo ""
echo "💡 Tip: Run 'cargo build' from workspace root to rebuild using shared target"
