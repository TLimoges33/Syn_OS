#!/bin/bash
set -euo pipefail

# Final cleanup of remaining non-essential branches
echo "=== Final Branch Cleanup Strategy ==="

REPO="TLimoges33/Syn_OS"

# Branches to potentially remove in final cleanup
CLEANUP_CANDIDATES=(
    "feature/documentation-system"
    "feature/technical-writing-documentation"  
    "feature/education-platform"
    "feature/enterprise-features-scalability"
    "feature/testing-framework"
    "feature/security-framework"
    "orchestrator-binary-only"
)

# Core branches to absolutely preserve
CORE_BRANCHES=(
    "main"
    "master" 
    "dev-team"
    "feature/consciousness-kernel"
    "feature/ai-ml-consciousness-core"
    "feature/cybersecurity-zero-trust"
    "feature/performance-optimization"
    "feature/devops-operations-infrastructure"
    "feature/quantum-computing"
)

echo "🎯 FINAL CLEANUP STRATEGY"
echo ""
echo "✅ CORE BRANCHES TO PRESERVE (${#CORE_BRANCHES[@]} branches):"
printf '  - %s\n' "${CORE_BRANCHES[@]}"
echo ""
echo "🗑️ CLEANUP CANDIDATES (${#CLEANUP_CANDIDATES[@]} branches):"
printf '  - %s\n' "${CLEANUP_CANDIDATES[@]}"
echo ""

read -p "Proceed with final cleanup of non-essential branches? (yes/no): " -r
if [[ $REPLY == "yes" ]]; then
    echo "🔥 Executing final cleanup..."
    
    deleted_count=0
    for branch in "${CLEANUP_CANDIDATES[@]}"; do
        echo "🗑️ Deleting $branch..."
        if gh api -X DELETE "/repos/$REPO/git/refs/heads/$branch" 2>/dev/null; then
            echo "✅ Deleted $branch"
            ((deleted_count++))
        else
            echo "⚠️ Failed to delete $branch or already deleted"
        fi
    done
    
    echo ""
    echo "🎯 Final cleanup completed!"
    echo "📊 Deleted $deleted_count branches"
    echo "✅ Repository streamlined to core development branches"
else
    echo "⏭️ Skipped final cleanup"
fi

echo ""
echo "📋 Final repository status:"
gh api "/repos/$REPO/branches" --jq '.[].name' | sort | wc -l | xargs echo "Total branches:"
echo ""
echo "🎯 Recommended next steps:"
echo "1. Focus development on consciousness-kernel"
echo "2. Advance AI/ML core integration"
echo "3. Implement zero-trust security"
echo "4. Optimize performance framework"
echo "5. Set up branch protection rules"
