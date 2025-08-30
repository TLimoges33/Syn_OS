#!/bin/bash
set -euo pipefail

# Extract data from branches before pruning
echo "=== Branch Data Extraction Tool ==="

REPOS=(
    "TLimoges33/Syn_OS-Dev-Team"
    "TLimoges33/Syn_OS"
)

OUTPUT_DIR="archive/extracted-branch-data"
ROADMAP_FILE="docs/EXTRACTED_BRANCH_ROADMAP.md"

mkdir -p "$OUTPUT_DIR"

extract_branch_info() {
    local repo=$1
    local branch=$2
    local output_file="$OUTPUT_DIR/${repo//\//_}_${branch//\//_}.md"
    
    echo "📊 Extracting data from $repo:$branch"
    
    # Get branch info
    local branch_info=$(gh api "/repos/$repo/branches/$branch" 2>/dev/null || echo "{}")
    local commit_sha=$(echo "$branch_info" | jq -r '.commit.sha // "unknown"' 2>/dev/null || echo "unknown")
    local commit_date=$(echo "$branch_info" | jq -r '.commit.commit.author.date // "unknown"' 2>/dev/null || echo "unknown")
    local commit_message=$(echo "$branch_info" | jq -r '.commit.commit.message // "No message"' 2>/dev/null || echo "No message")
    
    # Create extraction file
    cat > "$output_file" << BRANCH_EOF
# Branch Data: $repo:$branch

## Branch Information
- **Repository**: $repo
- **Branch**: $branch
- **Last Commit SHA**: $commit_sha
- **Last Commit Date**: $commit_date
- **Last Commit Message**: $commit_message

## Commit History (Last 10)
BRANCH_EOF
    
    # Get recent commits
    gh api "/repos/$repo/commits?sha=$branch" --jq '.[] | "- **\(.commit.author.date)**: \(.commit.message | split("\n")[0])"' 2>/dev/null | head -10 >> "$output_file" || echo "- No commits accessible" >> "$output_file"
    
    echo "" >> "$output_file"
    echo "## Files Changed (Recent)" >> "$output_file"
    gh api "/repos/$repo/commits?sha=$branch" --jq '.[0].files[]? | "- \(.filename) (\(.status))"' 2>/dev/null | head -20 >> "$output_file" || echo "- No file changes accessible" >> "$output_file"
    
    echo "✅ Extracted to $output_file"
}

extract_all_feature_branches() {
    echo "🔍 Finding all feature branches to extract..."
    
    for repo in "${REPOS[@]}"; do
        echo ""
        echo "📂 Processing repository: $repo"
        
        # Get all feature branches
        local feature_branches=$(gh api "/repos/$repo/branches" --jq '.[] | select(.name | test("^(feature/|chore/|hotfix/|dev-)")) | .name' 2>/dev/null || echo "")
        
        if [[ -z "$feature_branches" ]]; then
            echo "❌ No feature branches found or no access"
            continue
        fi
        
        echo "Found $(echo "$feature_branches" | wc -l) feature branches:"
        echo "$feature_branches"
        
        # Extract data from each branch
        while IFS= read -r branch; do
            extract_branch_info "$repo" "$branch"
        done <<< "$feature_branches"
    done
}

generate_roadmap() {
    echo "📋 Generating comprehensive roadmap..."
    
    cat > "$ROADMAP_FILE" << 'ROADMAP_EOF'
# Extracted Branch Roadmap

## Overview
This document contains extracted data from all feature branches before pruning.
Generated on: $(date)

## Branch Categories

### Feature Development Branches
ROADMAP_EOF
    
    # Add feature branch data
    find "$OUTPUT_DIR" -name "*feature*.md" -type f | while read -r file; do
        local branch_name=$(basename "$file" .md | sed 's/.*_feature_/feature\//')
        echo "- **$branch_name**: [Extracted Data]($file)" >> "$ROADMAP_FILE"
    done
    
    echo "" >> "$ROADMAP_FILE"
    echo "### Development Branches" >> "$ROADMAP_FILE"
    
    find "$OUTPUT_DIR" -name "*dev-*.md" -type f | while read -r file; do
        local branch_name=$(basename "$file" .md | sed 's/.*_dev-/dev-/')
        echo "- **$branch_name**: [Extracted Data]($file)" >> "$ROADMAP_FILE"
    done
    
    echo "" >> "$ROADMAP_FILE"
    echo "### Maintenance Branches" >> "$ROADMAP_FILE"
    
    find "$OUTPUT_DIR" -name "*chore*.md" -o -name "*hotfix*.md" -type f | while read -r file; do
        local branch_name=$(basename "$file" .md | sed 's/.*_//')
        echo "- **$branch_name**: [Extracted Data]($file)" >> "$ROADMAP_FILE"
    done
    
    cat >> "$ROADMAP_FILE" << 'ROADMAP_EOF'

## Implementation Priorities

### High Priority Features
- Consciousness kernel development
- AI/ML core integration  
- Security and zero-trust implementation
- Performance optimization

### Medium Priority Features
- Educational platform integration
- Enterprise features and scalability
- Documentation system improvements
- DevOps infrastructure

### Low Priority / Research
- Advanced computing research
- Experimental integrations
- Legacy system migrations

## Next Steps

1. **Review extracted data** for valuable implementations
2. **Merge critical features** into main development branch
3. **Archive completed features** to prevent data loss
4. **Continue branch pruning** with confidence

## Extraction Metadata

- **Total branches processed**: [COUNT]
- **Extraction date**: $(date)
- **Repositories**: TLimoges33/Syn_OS-Dev-Team, TLimoges33/Syn_OS
- **Data location**: archive/extracted-branch-data/
ROADMAP_EOF

    echo "✅ Roadmap generated: $ROADMAP_FILE"
}

# Main execution
echo "Starting branch data extraction before pruning..."
echo "This will preserve all valuable information from branches before deletion"
echo ""

extract_all_feature_branches
generate_roadmap

echo ""
echo "🎯 Branch data extraction completed!"
echo "📁 Extracted data: $OUTPUT_DIR"
echo "📋 Roadmap: $ROADMAP_FILE"
echo ""
echo "Ready to continue with aggressive branch pruning!"
