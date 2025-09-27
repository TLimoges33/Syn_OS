#!/bin/bash

# Integration Status Monitor
# Tracks progress of repository integrations

echo "📊 SynOS GitHub Integration Status Report"
echo "========================================"
echo ""

WORKSPACE_DIR="$HOME/SynOS-Workspace"

if [[ ! -d "$WORKSPACE_DIR" ]]; then
    echo "❌ Workspace not found. Run setup-local-repos.sh first."
    exit 1
fi

# Count repositories by tier
tier1_count=$(find "$WORKSPACE_DIR/tier1" -maxdepth 1 -type d | wc -l)
tier2_count=$(find "$WORKSPACE_DIR/tier2" -maxdepth 1 -type d | wc -l)
tier3_count=$(find "$WORKSPACE_DIR/tier3" -maxdepth 1 -type d | wc -l)

echo "📁 Repository Status:"
echo "   Tier 1 (Critical): $((tier1_count - 1)) repositories"
echo "   Tier 2 (Pentesting): $((tier2_count - 1)) repositories"
echo "   Tier 3 (Bug Bounty): $((tier3_count - 1)) repositories"
echo ""

# Check integration progress
echo "🔧 Integration Progress:"

check_integration() {
    local tier_dir=$1
    local tier_name=$2

    if [[ -d "$tier_dir" ]]; then
        for repo_dir in "$tier_dir"/*; do
            if [[ -d "$repo_dir" && -f "$repo_dir/SYNOS_INTEGRATION.md" ]]; then
                local repo_name=$(basename "$repo_dir")
                local branch_count=$(cd "$repo_dir" && git branch | wc -l)
                local commit_count=$(cd "$repo_dir" && git log --oneline synos-integration 2>/dev/null | wc -l || echo "0")

                if [[ $commit_count -gt 0 ]]; then
                    echo "   ✅ $repo_name ($tier_name): $commit_count commits"
                else
                    echo "   ⚠️ $repo_name ($tier_name): Not started"
                fi
            fi
        done
    fi
}

check_integration "$WORKSPACE_DIR/tier1" "T1"
check_integration "$WORKSPACE_DIR/tier2" "T2"
check_integration "$WORKSPACE_DIR/tier3" "T3"

echo ""
echo "📈 Next Actions:"
echo "1. Focus on Tier 1 critical integrations"
echo "2. Implement AI consciousness interfaces"
echo "3. Create security enhancements"
echo "4. Build unified SynOS distribution"
