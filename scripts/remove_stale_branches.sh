#!/bin/bash
set -euo pipefail

# Remove stale branches across repositories
echo "=== Stale Branch Cleanup ==="

REPOS=(
    "TLimoges33/Syn_OS-Dev-Team"
    "TLimoges33/Syn_OS"
    "TLimoges33/SynOS" 
    "TLimoges33/SynapticOS"
)

# Branches to preserve (never delete)
PROTECTED_BRANCHES=("main" "master" "dev-team" "develop" "docs/restore-guide")

# Stale branch patterns to clean up
STALE_PATTERNS=(
    "^feature/"
    "^hotfix/"
    "^chore/"
    "^extract/"
    "^dev-[a-z]"
    "^staging$"
    "^test-"
    "^temp-"
)

cleanup_stale_branches() {
    local repo=$1
    echo "🧹 Cleaning stale branches in: $repo"
    
    # Get all branches
    local branches=$(gh api "/repos/$repo/branches" --jq '.[].name' 2>/dev/null || echo "")
    
    if [[ -z "$branches" ]]; then
        echo "❌ Cannot access $repo"
        return
    fi
    
    echo "📋 Found $(echo "$branches" | wc -l) total branches"
    
    # Find stale branches
    local stale_branches=()
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
        
        # Check if branch matches stale patterns
        for pattern in "${STALE_PATTERNS[@]}"; do
            if echo "$branch" | grep -qE "$pattern"; then
                stale_branches+=("$branch")
                break
            fi
        done
    done <<< "$branches"
    
    echo "🗑️ Found ${#stale_branches[@]} stale branches to remove:"
    printf '%s\n' "${stale_branches[@]}" | head -10
    
    if [[ ${#stale_branches[@]} -gt 10 ]]; then
        echo "... and $((${#stale_branches[@]} - 10)) more"
    fi
    
    # Confirm before deletion
    read -p "Delete these stale branches from $repo? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch in "${stale_branches[@]}"; do
            echo "🗑️ Deleting $branch..."
            gh api -X DELETE "/repos/$repo/git/refs/heads/$branch" 2>/dev/null || echo "⚠️ Failed to delete $branch"
        done
        echo "✅ Cleanup completed for $repo"
    else
        echo "⏭️ Skipped cleanup for $repo"
    fi
    
    echo ""
}

# Main execution
echo "Starting stale branch cleanup across repositories..."
echo "This will identify and optionally remove old feature/hotfix/chore branches"
echo ""

for repo in "${REPOS[@]}"; do
    cleanup_stale_branches "$repo"
done

echo "🎯 Stale branch cleanup completed!"
