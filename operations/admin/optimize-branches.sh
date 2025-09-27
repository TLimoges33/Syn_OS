#!/bin/bash

# 🌿 SynOS Branch Optimization Script
# Safely restructures branches to: master, main, dev-team-codespace, archive
# Date: September 10, 2025

set -e  # Exit on any error

echo "🌿 Starting SynOS Branch Optimization..."
echo "📋 Target: master, main, dev-team-codespace, archive branches only"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backup current state
echo -e "${BLUE}📦 Creating safety backup...${NC}"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
git tag "backup-before-optimization-${BACKUP_DATE}" 2>/dev/null || echo "Tag already exists"

# Function to safely archive a branch
archive_branch() {
    local branch_name=$1
    echo -e "${YELLOW}📁 Archiving branch: ${branch_name}${NC}"
    
    if git show-ref --verify --quiet refs/heads/"${branch_name}"; then
        git checkout archive 2>/dev/null || {
            echo -e "${BLUE}Creating archive branch...${NC}"
            git checkout -b archive
        }
        
        # Create archive commit for this branch
        git merge --no-ff "${branch_name}" -m "Archive: ${branch_name} ($(date))" || {
            echo -e "${YELLOW}Branch ${branch_name} already in archive or conflict${NC}"
            git merge --abort 2>/dev/null || true
        }
    else
        echo -e "${YELLOW}Branch ${branch_name} not found locally${NC}"
    fi
}

# Function to safely archive remote branch
archive_remote_branch() {
    local remote=$1
    local branch_name=$2
    echo -e "${YELLOW}📁 Archiving remote branch: ${remote}/${branch_name}${NC}"
    
    if git show-ref --verify --quiet refs/remotes/"${remote}"/"${branch_name}"; then
        git checkout archive 2>/dev/null || {
            echo -e "${BLUE}Creating archive branch...${NC}"
            git checkout -b archive
        }
        
        # Create archive commit for this remote branch
        git merge --no-ff "${remote}/${branch_name}" -m "Archive: ${remote}/${branch_name} ($(date))" || {
            echo -e "${YELLOW}Remote branch ${remote}/${branch_name} already in archive or conflict${NC}"
            git merge --abort 2>/dev/null || true
        }
    else
        echo -e "${YELLOW}Remote branch ${remote}/${branch_name} not found${NC}"
    fi
}

echo ""
echo -e "${GREEN}🔍 PHASE 1: ARCHIVING HISTORICAL BRANCHES${NC}"
echo "=============================================="

# Ensure we're on main before starting
git checkout main

# Archive important local branches before deletion
echo -e "${BLUE}Archiving local branches...${NC}"
archive_branch "develop"
archive_branch "ebpf-100-percent-achievement-backup"
archive_branch "ebpf-achievement-clean"
archive_branch "ebpf-achievement-merge-safe"

# Archive important remote feature branches
echo -e "${BLUE}Archiving remote feature branches...${NC}"
archive_remote_branch "production" "feature/ai-ml-consciousness-core"
archive_remote_branch "production" "feature/consciousness-kernel"
archive_remote_branch "production" "feature/cybersecurity-zero-trust"
archive_remote_branch "production" "feature/devops-operations-infrastructure"
archive_remote_branch "production" "feature/performance-optimization"
archive_remote_branch "production" "feature/quantum-computing"
archive_remote_branch "production" "develop"

echo ""
echo -e "${GREEN}🔧 PHASE 2: BRANCH RESTRUCTURING${NC}"
echo "=================================="

# Rename dev-team to dev-team-codespace
if git show-ref --verify --quiet refs/heads/dev-team; then
    echo -e "${BLUE}Renaming dev-team → dev-team-codespace...${NC}"
    git branch -m dev-team dev-team-codespace
else
    echo -e "${YELLOW}Creating dev-team-codespace branch...${NC}"
    git checkout -b dev-team-codespace
    git checkout main
fi

echo ""
echo -e "${GREEN}🗑️ PHASE 3: CLEANING LOCAL BRANCHES${NC}"
echo "===================================="

# Safely remove archived local branches
for branch in "develop" "ebpf-100-percent-achievement-backup" "ebpf-achievement-clean" "ebpf-achievement-merge-safe"; do
    if git show-ref --verify --quiet refs/heads/"${branch}"; then
        echo -e "${RED}Removing local branch: ${branch}${NC}"
        git branch -D "${branch}" 2>/dev/null || echo "Could not delete ${branch}"
    fi
done

echo ""
echo -e "${GREEN}☁️ PHASE 4: UPDATING REMOTES${NC}"
echo "============================="

# Push archive branch to both remotes
echo -e "${BLUE}Pushing archive to remotes...${NC}"
git checkout archive
git push archive archive -f 2>/dev/null || echo "Could not push to archive remote"
git push production archive -f 2>/dev/null || echo "Could not push archive to production"

# Update main branches
echo -e "${BLUE}Updating main branches...${NC}"
git checkout main
git push production main 2>/dev/null || echo "Could not push main to production"
git push archive main 2>/dev/null || echo "Could not push main to archive"

git checkout master
git push production master 2>/dev/null || echo "Could not push master to production"
git push archive master 2>/dev/null || echo "Could not push master to archive"

# Push renamed dev-team-codespace
echo -e "${BLUE}Pushing dev-team-codespace...${NC}"
git checkout dev-team-codespace
git push production dev-team-codespace 2>/dev/null || echo "Could not push dev-team-codespace"

echo ""
echo -e "${GREEN}🧹 PHASE 5: REMOTE CLEANUP${NC}"
echo "=========================="

# Remove old remote branches (be careful here)
echo -e "${YELLOW}Note: Remote branch cleanup should be done manually for safety${NC}"
echo -e "${YELLOW}Suggested commands (run manually if desired):${NC}"
echo "git push production --delete develop"
echo "git push production --delete dev-team"
echo "git push production --delete ebpf-achievement-clean"
echo "git push production --delete feature/ai-ml-consciousness-core"
echo "git push production --delete feature/consciousness-kernel"
echo "git push production --delete feature/cybersecurity-zero-trust"
echo "git push production --delete feature/devops-operations-infrastructure" 
echo "git push production --delete feature/performance-optimization"
echo "git push production --delete feature/quantum-computing"

echo ""
echo -e "${GREEN}✅ PHASE 6: VERIFICATION${NC}"
echo "======================="

# Return to main
git checkout main

echo -e "${BLUE}Current local branches:${NC}"
git branch

echo ""
echo -e "${BLUE}Current remote branches:${NC}"
git branch -r

echo ""
echo -e "${GREEN}🎉 BRANCH OPTIMIZATION COMPLETE!${NC}"
echo "================================="
echo ""
echo -e "${BLUE}📋 FINAL STRUCTURE:${NC}"
echo "• master          - Production releases"
echo "• main            - Lead developer workspace (you)"  
echo "• dev-team-codespace - Team collaboration"
echo "• archive         - Historical preservation"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Verify branches look correct above"
echo "2. Test that main branch works as expected"
echo "3. Manually clean remote branches if desired (commands shown above)"
echo "4. Set up branch protection rules for master/main"
echo ""
echo -e "${GREEN}🛡️ Safety: Backup tag created: backup-before-optimization-${BACKUP_DATE}${NC}"
echo ""
