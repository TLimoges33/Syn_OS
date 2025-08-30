#!/bin/bash
set -euo pipefail

# Comprehensive branch cleanup across repositories
echo "=== SynOS Multi-Repository Branch Cleanup ==="

REPOS=(
    "TLimoges33/Syn_OS-Dev-Team"
    "TLimoges33/Syn_OS"
)

# Target branch alignment
TARGET_SHA_MAIN="d43122b38f448ea4c41658c97b0c3fd8d4806f48"
TARGET_SHA_MASTER="97b9be989d5213e5d8306dcb6479e75fd34b802b"
TARGET_SHA_DEV_TEAM="19c6e41138a2b528729f36e59fd8b23e2468a741"

echo "Starting branch alignment..."
echo "Targets: main=$TARGET_SHA_MAIN, master=$TARGET_SHA_MASTER, dev-team=$TARGET_SHA_DEV_TEAM"

for repo in "${REPOS[@]}"; do
    echo ""
    echo "🔧 Processing: $repo"
    
    # Update main branch
    echo "Updating main branch..."
    gh api -X PATCH "/repos/$repo/git/refs/heads/main" -f sha="$TARGET_SHA_MAIN" 2>/dev/null || echo "Failed to update main"
    
    # Update master branch  
    echo "Updating master branch..."
    gh api -X PATCH "/repos/$repo/git/refs/heads/master" -f sha="$TARGET_SHA_MASTER" 2>/dev/null || echo "Failed to update master"
    
    # Update or create dev-team branch
    echo "Updating dev-team branch..."
    gh api -X PATCH "/repos/$repo/git/refs/heads/dev-team" -f sha="$TARGET_SHA_DEV_TEAM" 2>/dev/null || \
    gh api -X POST "/repos/$repo/git/refs" -f ref="refs/heads/dev-team" -f sha="$TARGET_SHA_DEV_TEAM" 2>/dev/null || \
    echo "Failed to update/create dev-team"
    
    echo "✅ $repo completed"
done

echo ""
echo "🎯 Branch alignment completed!"
