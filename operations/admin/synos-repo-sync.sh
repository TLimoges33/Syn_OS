#!/bin/bash

# 🚀 SynOS Repository Sync and Branch Management Script
# Automates the lead developer workflow: main -> dev-team -> master -> production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}============================================${NC}"
    echo -e "${PURPLE}🚀 SynOS Repository Management${NC}"
    echo -e "${PURPLE}============================================${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [[ ! -f "SynOS-Focused.code-workspace" ]]; then
    print_error "Please run this script from the SynOS root directory"
    exit 1
fi

print_header

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_step "Current branch: $CURRENT_BRANCH"

# Function to commit current changes
commit_current_changes() {
    print_step "Committing current changes on $CURRENT_BRANCH"
    
    # Add all changes
    git add .
    
    # Create commit message with timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    COMMIT_MSG="✨ SynOS v1.0 Development Update - $TIMESTAMP

🎯 Major Updates:
- Enhanced VS Code workspace configuration
- Comprehensive architecture audit completed
- ParrotOS dependencies analysis and removal
- Documentation cleanup and reorganization
- Development environment optimization
- Added development setup scripts

🔧 Technical Changes:
- Optimized .vscode settings for SynOS development
- Added debugging configurations for consciousness engine
- Enhanced build tasks and automation
- Improved Python/Rust integration settings
- Added security audit automation

📁 Structure Improvements:
- Removed redundant ParrotOS integration workspace
- Cleaned up legacy documentation
- Optimized folder structure
- Enhanced development tooling

🚀 Ready for: Production deployment and team collaboration"

    git commit -m "$COMMIT_MSG"
    print_success "Changes committed to $CURRENT_BRANCH"
}

# Function to sync with remote
sync_branch() {
    local branch=$1
    print_step "Syncing $branch with remote"
    
    git checkout "$branch" 2>/dev/null || {
        print_warning "Branch $branch doesn't exist locally, creating..."
        git checkout -b "$branch"
    }
    
    # Try to pull from origin first, create if doesn't exist
    if git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        git pull origin "$branch" || print_warning "Could not pull from origin/$branch"
    else
        print_warning "Branch $branch doesn't exist on origin, will be created on push"
    fi
    
    git push -u origin "$branch"
    print_success "Branch $branch synced with origin"
}

# Function to merge changes between branches
merge_to_branch() {
    local from_branch=$1
    local to_branch=$2
    
    print_step "Merging $from_branch -> $to_branch"
    
    # Checkout target branch
    git checkout "$to_branch" 2>/dev/null || {
        print_warning "Branch $to_branch doesn't exist, creating..."
        git checkout -b "$to_branch"
    }
    
    # Merge from source branch
    git merge "$from_branch" --no-ff -m "🔄 Merge $from_branch into $to_branch

Automated merge from lead developer workflow
- All latest SynOS v1.0 developments
- Architecture optimizations
- Development environment enhancements
- Ready for production deployment"
    
    print_success "Merged $from_branch into $to_branch"
}

# Main workflow
case "${1:-full}" in
    "commit")
        print_step "Committing current changes only"
        commit_current_changes
        ;;
    
    "sync")
        print_step "Syncing current branch only"
        sync_branch "$CURRENT_BRANCH"
        ;;
    
    "dev-team")
        print_step "Creating/updating dev-team branch"
        if [[ "$CURRENT_BRANCH" != "main" ]]; then
            print_warning "Switching to main branch first"
            git checkout main
        fi
        commit_current_changes
        sync_branch "main"
        merge_to_branch "main" "dev-team"
        sync_branch "dev-team"
        git checkout main
        print_success "dev-team branch ready for team collaboration"
        ;;
    
    "master")
        print_step "Deploying to master branch"
        if [[ "$CURRENT_BRANCH" != "main" ]]; then
            git checkout main
        fi
        commit_current_changes
        sync_branch "main"
        merge_to_branch "main" "master"
        sync_branch "master"
        git checkout main
        print_success "master branch updated for production"
        ;;
    
    "production")
        print_step "Full production deployment"
        if [[ "$CURRENT_BRANCH" != "main" ]]; then
            git checkout main
        fi
        commit_current_changes
        sync_branch "main"
        merge_to_branch "main" "dev-team"
        sync_branch "dev-team"
        merge_to_branch "main" "master"
        sync_branch "master"
        
        # Push to production remote if it exists
        if git remote | grep -q "production"; then
            print_step "Pushing to production remote"
            git push production master
            git push production main
            git push production dev-team
            print_success "Pushed to production remote"
        else
            print_warning "No production remote configured"
        fi
        
        git checkout main
        print_success "Full production deployment complete"
        ;;
    
    "full"|*)
        print_step "Full workflow: commit -> main -> dev-team -> master"
        
        # Ensure we're on main
        if [[ "$CURRENT_BRANCH" != "main" ]]; then
            print_warning "Switching to main branch"
            git checkout main
        fi
        
        # Commit current changes
        commit_current_changes
        
        # Sync main
        sync_branch "main"
        
        # Create/update dev-team branch
        merge_to_branch "main" "dev-team"
        sync_branch "dev-team"
        
        # Update master
        merge_to_branch "main" "master"
        sync_branch "master"
        
        # Return to main
        git checkout main
        
        print_success "🎉 Full workflow complete!"
        echo ""
        echo "📋 Branch Status:"
        echo "  main     ✅ Latest development (lead developer workspace)"
        echo "  dev-team ✅ Ready for team collaboration"
        echo "  master   ✅ Production ready"
        echo ""
        echo "🔄 Next Steps:"
        echo "  - Team members can create PRs from dev-team to main"
        echo "  - Production deployments use master branch"
        echo "  - Continue development on main branch"
        ;;
esac

print_success "Repository sync complete! 🚀"
