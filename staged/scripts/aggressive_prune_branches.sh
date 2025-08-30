#!/bin/bash
set -euo pipefail

# Aggressive branch pruning after data extraction
echo "=== Aggressive Branch Pruning Tool ==="

REPOS=(
    "TLimoges33/Syn_OS-Dev-Team"
    "TLimoges33/Syn_OS"
)

# Branches to preserve (never delete)
PROTECTED_BRANCHES=(
    "main" 
    "master" 
    "dev-team"
    "develop"
    "docs/restore-guide"
)

# High priority branches to consolidate (not delete yet)
HIGH_PRIORITY_BRANCHES=(
    "feature/consciousness-kernel"
    "feature/ai-ml-consciousness-core"
    "feature/AI-ML-consciousness-core"
    "feature/cybersecurity-zero-trust"
    "feature/performance-optimization"
    "feature/system-performance-optimization"
)

aggressive_prune_repo() {
    local repo=$1
    echo "🔥 Aggressive pruning: $repo"
    
    # Get all branches
    local branches=$(gh api "/repos/$repo/branches" --jq '.[].name' 2>/dev/null || echo "")
    
    if [[ -z "$branches" ]]; then
        echo "❌ Cannot access $repo"
        return
    fi
    
    echo "📋 Found $(echo "$branches" | wc -l) total branches"
    
    # Find branches to delete
    local branches_to_delete=()
    while IFS= read -r branch; do
        # Skip protected branches
        local is_protected=false
        for protected in "${PROTECTED_BRANCHES[@]}"; do
            if [[ "$branch" == "$protected" ]]; then
                is_protected=true
                break
            fi
        done
        
        if [[ "$is_protected" == "true" ]]; then
            continue
        fi
        
        # Skip high priority branches for now
        local is_high_priority=false
        for priority in "${HIGH_PRIORITY_BRANCHES[@]}"; do
            if [[ "$branch" == "$priority" ]]; then
                is_high_priority=true
                break
            fi
        done
        
        if [[ "$is_high_priority" == "true" ]]; then
            echo "🔄 Preserving high priority: $branch"
            continue
        fi
        
        # Delete everything else
        branches_to_delete+=("$branch")
    done <<< "$branches"
    
    echo "🗑️ AGGRESSIVE DELETION: ${#branches_to_delete[@]} branches"
    printf '%s\n' "${branches_to_delete[@]}" | head -15
    
    if [[ ${#branches_to_delete[@]} -gt 15 ]]; then
        echo "... and $((${#branches_to_delete[@]} - 15)) more"
    fi
    
    # Confirm aggressive deletion
    echo ""
    read -p "🔥 CONFIRM AGGRESSIVE PRUNING of ${#branches_to_delete[@]} branches from $repo? (yes/no): " -r
    if [[ $REPLY == "yes" ]]; then
        local deleted_count=0
        for branch in "${branches_to_delete[@]}"; do
            echo "🗑️ Deleting $branch..."
            if gh api -X DELETE "/repos/$repo/git/refs/heads/$branch" 2>/dev/null; then
                ((deleted_count++))
            else
                echo "⚠️ Failed to delete $branch"
            fi
        done
        echo "✅ Deleted $deleted_count branches from $repo"
    else
        echo "⏭️ Skipped aggressive pruning for $repo"
    fi
    
    echo ""
}

consolidate_duplicate_branches() {
    echo "🔄 Consolidation recommendations for duplicate branches:"
    echo ""
    echo "1. AI/ML Consciousness:"
    echo "   - feature/ai-ml-consciousness-core"
    echo "   - feature/AI-ML-consciousness-core" 
    echo "   → Recommend: Merge into feature/ai-ml-consciousness-core"
    echo ""
    echo "2. Performance Optimization:"
    echo "   - feature/performance-optimization"
    echo "   - feature/system-performance-optimization"
    echo "   → Recommend: Merge into feature/performance-optimization"
    echo ""
    echo "3. Education Platform:"
    echo "   - feature/education-platform"
    echo "   - feature/educational-integration-platform"
    echo "   → Recommend: Merge into feature/education-platform"
    echo ""
    echo "4. Testing Framework:"
    echo "   - feature/quality-assurance-testing"
    echo "   - feature/testing-framework"
    echo "   → Recommend: Merge into feature/testing-framework"
    echo ""
}

# Main execution
echo "Starting aggressive branch pruning..."
echo "⚠️  WARNING: This will delete most feature branches except high priority ones"
echo "💾 All branch data has been extracted to archive/extracted-branch-data/"
echo ""

for repo in "${REPOS[@]}"; do
    aggressive_prune_repo "$repo"
done

consolidate_duplicate_branches

echo ""
echo "🎯 Aggressive pruning completed!"
echo "📋 Next steps:"
echo "1. Review high priority branches for consolidation"
echo "2. Merge duplicate branches manually"
echo "3. Focus development on core features"
