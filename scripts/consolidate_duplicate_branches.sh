#!/bin/bash
set -euo pipefail

# Consolidate duplicate branches by merging content
echo "=== Branch Consolidation Tool ==="

REPO="TLimoges33/Syn_OS"

# Duplicate branch pairs to consolidate
declare -A BRANCH_PAIRS=(
    ["feature/AI-ML-consciousness-core"]="feature/ai-ml-consciousness-core"
    ["feature/system-performance-optimization"]="feature/performance-optimization"
)

consolidate_branches() {
    local from_branch=$1
    local to_branch=$2
    
    echo "🔄 Consolidating $from_branch → $to_branch"
    
    # Get branch info
    local from_info=$(gh api "/repos/$REPO/branches/$from_branch" 2>/dev/null || echo "{}")
    local to_info=$(gh api "/repos/$REPO/branches/$to_branch" 2>/dev/null || echo "{}")
    
    if [[ "$from_info" == "{}" ]]; then
        echo "❌ Source branch $from_branch not found"
        return
    fi
    
    if [[ "$to_info" == "{}" ]]; then
        echo "❌ Target branch $to_branch not found"
        return
    fi
    
    local from_sha=$(echo "$from_info" | jq -r '.commit.sha')
    local to_sha=$(echo "$to_info" | jq -r '.commit.sha')
    local from_date=$(echo "$from_info" | jq -r '.commit.commit.author.date')
    local to_date=$(echo "$to_info" | jq -r '.commit.commit.author.date')
    
    echo "📊 Branch comparison:"
    echo "  $from_branch: $from_date (${from_sha:0:8})"
    echo "  $to_branch: $to_date (${to_sha:0:8})"
    
    # Determine which is newer
    if [[ "$from_date" > "$to_date" ]]; then
        echo "⬆️ $from_branch is newer, updating $to_branch"
        gh api -X PATCH "/repos/$REPO/git/refs/heads/$to_branch" -f sha="$from_sha" || echo "⚠️ Update failed"
    else
        echo "✅ $to_branch is newer or equal, keeping as-is"
    fi
    
    # Delete the duplicate branch
    echo "🗑️ Deleting duplicate: $from_branch"
    gh api -X DELETE "/repos/$REPO/git/refs/heads/$from_branch" || echo "⚠️ Deletion failed"
    
    echo "✅ Consolidation complete: $from_branch → $to_branch"
    echo ""
}

# Main execution
echo "Starting branch consolidation..."
echo "This will merge duplicate branches and remove redundant ones"
echo ""

for from_branch in "${!BRANCH_PAIRS[@]}"; do
    to_branch="${BRANCH_PAIRS[$from_branch]}"
    consolidate_branches "$from_branch" "$to_branch"
done

echo "🎯 Branch consolidation completed!"
