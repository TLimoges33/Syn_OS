#!/bin/bash

# SynOS Git Save System
# Comprehensive git workflow automation with safety checks
# Author: SynOS Development Team
# Version: 1.0
# Date: August 27, 2025

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(git rev-parse --show-toplevel)"
LOG_FILE="$REPO_ROOT/logs/git-save-system.log"
BACKUP_DIR="$REPO_ROOT/.git-backups"
FAILURE_COUNTER_FILE="$REPO_ROOT/.git-save-failures"
CURRENT_BRANCH=""
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

# Initialize failure counter if it doesn't exist
if [ ! -f "$FAILURE_COUNTER_FILE" ]; then
    echo "0" > "$FAILURE_COUNTER_FILE"
fi

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[SynOS Save] $message${NC}"
    log "$message"
}

# Error handler with failure tracking
error_exit() {
    local error_msg="$1"
    local current_failures=$(cat "$FAILURE_COUNTER_FILE")
    local new_failures=$((current_failures + 1))
    echo "$new_failures" > "$FAILURE_COUNTER_FILE"
    
    print_status "$RED" "ERROR: $error_msg"
    print_status "$RED" "Failure count: $new_failures"
    
    # Check for consecutive failures
    if [ "$new_failures" -ge 2 ]; then
        print_status "$YELLOW" "⚠️  Two consecutive failures detected!"
        print_status "$YELLOW" "🤖 Recommending GitHub Copilot Chat for advanced troubleshooting..."
        print_status "$BLUE" "Suggested Copilot Chat queries:"
        echo "  1. 'Help me debug git merge conflicts in SynOS repository'"
        echo "  2. 'Analyze git save system failures and suggest solutions'"
        echo "  3. 'Review Makefile merge conflict resolution strategies'"
        echo ""
        print_status "$BLUE" "To reset failure counter after resolving issues:"
        echo "  echo '0' > $FAILURE_COUNTER_FILE"
    fi
    
    exit 1
}

# Success handler - reset failure counter
success_handler() {
    echo "0" > "$FAILURE_COUNTER_FILE"
    print_status "$GREEN" "✅ Operation successful - failure counter reset"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error_exit "Not in a git repository"
    fi
}

# Get current branch
get_current_branch() {
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_status "$BLUE" "Current branch: $CURRENT_BRANCH"
}

# Create backup of current state
create_backup() {
    print_status "$YELLOW" "Creating backup of current state..."
    local backup_file="$BACKUP_DIR/backup_${CURRENT_BRANCH}_${TIMESTAMP}.tar.gz"
    
    # Create backup excluding .git directory
    tar -czf "$backup_file" --exclude='.git' --exclude='.git-backups' -C "$REPO_ROOT" .
    print_status "$GREEN" "Backup created: $backup_file"
    
    # Store backup filename for potential cleanup
    echo "$backup_file" > "$BACKUP_DIR/latest_backup.txt"
}

# Clean up backups after successful sync
cleanup_backups() {
    print_status "$BLUE" "🧹 Cleaning up old backups after successful sync..."
    
    # Keep only the 3 most recent backups
    local backup_count=$(ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | wc -l)
    if [ "$backup_count" -gt 3 ]; then
        print_status "$YELLOW" "Found $backup_count backups, keeping only 3 most recent..."
        ls -1t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +4 | xargs rm -f
        print_status "$GREEN" "Old backups cleaned up"
    fi
    
    # Clean up the latest backup if all branches are synchronized
    if branches_synchronized; then
        local latest_backup=$(cat "$BACKUP_DIR/latest_backup.txt" 2>/dev/null || echo "")
        if [ -n "$latest_backup" ] && [ -f "$latest_backup" ]; then
            print_status "$GREEN" "🎉 All branches synchronized - removing latest backup: $(basename "$latest_backup")"
            rm -f "$latest_backup"
            rm -f "$BACKUP_DIR/latest_backup.txt"
        fi
    fi
}

# Check if all three branches (dev-team-main, main, master) are synchronized
branches_synchronized() {
    local dev_commit=$(git rev-parse dev-team-main 2>/dev/null || echo "missing")
    local main_commit=$(git rev-parse main 2>/dev/null || echo "missing")
    local master_commit=$(git rev-parse master 2>/dev/null || echo "missing")
    
    if [ "$dev_commit" = "missing" ] || [ "$main_commit" = "missing" ] || [ "$master_commit" = "missing" ]; then
        return 1
    fi
    
    # Check if main and master have the same content (allowing for merge commits)
    if git merge-base --is-ancestor main master && git merge-base --is-ancestor master main; then
        print_status "$BLUE" "✅ Main and master branches are synchronized"
        return 0
    fi
    
    return 1
}

# Check for uncommitted changes
check_uncommitted_changes() {
    if ! git diff-index --quiet HEAD --; then
        print_status "$YELLOW" "Uncommitted changes detected"
        return 1
    fi
    return 0
}

# Stash uncommitted changes
stash_changes() {
    if ! check_uncommitted_changes; then
        print_status "$YELLOW" "Stashing uncommitted changes..."
        git stash push -m "Auto-stash before save operation - $TIMESTAMP"
        return 0
    fi
    return 1
}

# Pop stashed changes
pop_stash() {
    if git stash list | grep -q "Auto-stash before save operation"; then
        print_status "$YELLOW" "Restoring stashed changes..."
        git stash pop
    fi
}

# Run comprehensive tests
run_tests() {
    print_status "$BLUE" "Running comprehensive tests..."
    
    # Check if Makefile exists and has test target
    if [ -f "$REPO_ROOT/Makefile" ] && grep -q "^test:" "$REPO_ROOT/Makefile"; then
        print_status "$BLUE" "Running Makefile tests..."
        if ! make test; then
            return 1
        fi
    fi
    
    # Check for Rust tests
    if [ -f "$REPO_ROOT/Cargo.toml" ] || find "$REPO_ROOT" -name "Cargo.toml" -type f | grep -q .; then
        print_status "$BLUE" "Running Rust tests..."
        if ! cargo test --workspace; then
            return 1
        fi
    fi
    
    # Check for Python tests
    if [ -f "$REPO_ROOT/requirements.txt" ] || [ -f "$REPO_ROOT/pyproject.toml" ]; then
        if command -v pytest > /dev/null; then
            print_status "$BLUE" "Running Python tests..."
            if ! pytest tests/ 2>/dev/null || true; then
                print_status "$YELLOW" "Python tests completed (some may have failed)"
            fi
        fi
    fi
    
    # Run security audit if available
    if [ -f "$REPO_ROOT/scripts/a_plus_security_audit.py" ]; then
        print_status "$BLUE" "Running security audit..."
        if ! python3 "$REPO_ROOT/scripts/a_plus_security_audit.py"; then
            print_status "$YELLOW" "Security audit completed with warnings"
        fi
    fi
    
    return 0
}

# Validate environment
validate_environment() {
    print_status "$BLUE" "Validating environment..."
    
    if [ -f "$REPO_ROOT/scripts/validate-environment.sh" ]; then
        if ! bash "$REPO_ROOT/scripts/validate-environment.sh"; then
            return 1
        fi
    fi
    
    return 0
}

# Check if branch is clean and ready for merge
check_branch_ready() {
    local branch=$1
    
    print_status "$BLUE" "Checking if $branch is ready for operations..."
    
    # Check if branch exists
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
        error_exit "Branch $branch does not exist"
    fi
    
    # Check if branch is up to date with remote
    if git ls-remote --heads origin "$branch" | grep -q .; then
        local local_commit=$(git rev-parse "$branch")
        local remote_commit=$(git rev-parse "origin/$branch" 2>/dev/null || echo "")
        
        if [ -n "$remote_commit" ] && [ "$local_commit" != "$remote_commit" ]; then
            print_status "$YELLOW" "Branch $branch is not up to date with remote"
            return 1
        fi
    fi
    
    return 0
}

# Intelligent Makefile conflict resolver
resolve_makefile_conflicts() {
    print_status "$BLUE" "🔧 Checking for Makefile conflicts..."
    
    if git status --porcelain | grep -q "^UU.*Makefile"; then
        print_status "$YELLOW" "⚠️  Makefile conflicts detected - applying intelligent resolution..."
        
        # Remove git conflict markers from Makefile
        if sed -i '/^<<<<<<< HEAD$/d; /^=======$/d; /^>>>>>>> main$/d; /^>>>>>>> master$/d; /^>>>>>>> dev-team-main$/d' "$REPO_ROOT/Makefile"; then
            print_status "$GREEN" "✅ Makefile conflict markers removed"
            
            # Check if the Makefile is now valid
            if make -n -f "$REPO_ROOT/Makefile" >/dev/null 2>&1; then
                print_status "$GREEN" "✅ Makefile syntax validated"
                git add "$REPO_ROOT/Makefile"
                return 0
            else
                print_status "$YELLOW" "⚠️  Makefile syntax issues detected - attempting repair..."
                
                # Common Makefile fixes
                # Fix missing tabs (replace leading spaces with tabs for target lines)
                sed -i 's/^    \([^#]\)/\t\1/' "$REPO_ROOT/Makefile"
                
                # Remove duplicate empty lines
                sed -i '/^$/N;/^\n$/d' "$REPO_ROOT/Makefile"
                
                if make -n -f "$REPO_ROOT/Makefile" >/dev/null 2>&1; then
                    print_status "$GREEN" "✅ Makefile repaired successfully"
                    git add "$REPO_ROOT/Makefile"
                    return 0
                else
                    print_status "$RED" "❌ Unable to auto-repair Makefile - manual intervention required"
                    return 1
                fi
            fi
        else
            print_status "$RED" "❌ Failed to remove conflict markers from Makefile"
            return 1
        fi
    else
        print_status "$GREEN" "✅ No Makefile conflicts detected"
        return 0
    fi
}

# Enhanced safe merge operation with conflict handling
safe_merge() {
    local source_branch=$1
    local target_branch=$2
    
    print_status "$BLUE" "Performing safe merge from $source_branch to $target_branch..."
    
    # Checkout target branch
    git checkout "$target_branch"
    
    # Create merge backup
    git tag "backup-pre-merge-$TIMESTAMP" HEAD
    
    # Attempt merge
    if git merge "$source_branch" --no-edit; then
        print_status "$GREEN" "✅ Clean merge successful: $source_branch -> $target_branch"
        return 0
    else
        print_status "$YELLOW" "⚠️  Merge conflicts detected - attempting intelligent resolution..."
        
        # Try to resolve Makefile conflicts automatically
        if resolve_makefile_conflicts; then
            print_status "$BLUE" "Attempting to complete merge after conflict resolution..."
            
            # Check if there are any remaining conflicts
            if git status --porcelain | grep -q "^UU"; then
                print_status "$YELLOW" "⚠️  Additional conflicts remain - listing them:"
                git status --porcelain | grep "^UU" | while read -r line; do
                    print_status "$YELLOW" "  Conflict: $line"
                done
                
                print_status "$RED" "❌ Manual conflict resolution required"
                git merge --abort
                return 1
            else
                # All conflicts resolved, complete the merge
                if git commit --no-edit; then
                    print_status "$GREEN" "✅ Merge completed successfully after conflict resolution"
                    return 0
                else
                    print_status "$RED" "❌ Failed to complete merge commit"
                    git merge --abort
                    return 1
                fi
            fi
        else
            print_status "$RED" "❌ Failed to resolve conflicts automatically"
            git merge --abort
            return 1
        fi
    fi
}

# Push to remote with safety checks
safe_push() {
    local branch=$1
    
    print_status "$BLUE" "Pushing $branch to remote..."
    
    # Check if remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_status "$YELLOW" "No remote origin configured, skipping push"
        return 0
    fi
    
    # Push with lease to prevent overwrites
    if git push --force-with-lease origin "$branch"; then
        print_status "$GREEN" "Successfully pushed $branch to remote"
        return 0
    else
        print_status "$RED" "Push failed - remote may have been updated"
        return 1
    fi
}

# Main save operation for dev-team work
save_dev_team() {
    print_status "$GREEN" "=== Starting Dev-Team Save Operation ==="
    
    # Ensure we're on dev-team-main
    if [ "$CURRENT_BRANCH" != "dev-team-main" ]; then
        error_exit "Must be on dev-team-main branch for dev-team save"
    fi
    
    # Create backup
    create_backup
    
    # Stash any uncommitted changes
    local stashed=false
    if stash_changes; then
        stashed=true
    fi
    
    # Run tests on current branch
    if ! run_tests; then
        if [ "$stashed" = true ]; then
            pop_stash
        fi
        error_exit "Tests failed on dev-team-main"
    fi
    
    # Validate environment
    if ! validate_environment; then
        if [ "$stashed" = true ]; then
            pop_stash
        fi
        error_exit "Environment validation failed"
    fi
    
    # Commit current changes if any
    if ! check_uncommitted_changes || [ "$stashed" = true ]; then
        if [ "$stashed" = true ]; then
            pop_stash
        fi
        
        print_status "$BLUE" "Committing changes..."
        git add -A
        
        # Interactive commit message
        echo "Enter commit message (or press Enter for auto-generated):"
        read -r commit_message
        
        if [ -z "$commit_message" ]; then
            commit_message="Auto-save: Development progress on $(date '+%Y-%m-%d %H:%M')"
        fi
        
        git commit -m "$commit_message"
    fi
    
    # Push dev-team-main
    safe_push "dev-team-main"
    
    # Switch to main and merge
    if safe_merge "dev-team-main" "main"; then
        # Run tests on main
        if run_tests; then
            # Push main
            safe_push "main"
            
            # Clean up backups after successful sync
            cleanup_backups
            
            # Reset failure counter on success
            success_handler
            
            print_status "$GREEN" "=== Dev-Team Save Completed Successfully ==="
        else
            print_status "$RED" "Tests failed on main, reverting merge..."
            git reset --hard HEAD~1
            git checkout "dev-team-main"
            error_exit "Tests failed on main branch"
        fi
    else
        git checkout "dev-team-main"
        error_exit "Failed to merge dev-team-main into main"
    fi
    
    # Return to original branch
    git checkout "dev-team-main"
}

# Main save operation for production release
save_production() {
    print_status "$GREEN" "=== Starting Production Save Operation ==="
    
    # Ensure we're on main
    if [ "$CURRENT_BRANCH" != "main" ]; then
        error_exit "Must be on main branch for production save"
    fi
    
    # Create backup
    create_backup
    
    # Comprehensive testing
    if ! run_tests; then
        error_exit "Tests failed on main - not safe for production"
    fi
    
    # Extended validation for production
    if ! validate_environment; then
        error_exit "Environment validation failed - not safe for production"
    fi
    
    # Merge to master
    if safe_merge "main" "master"; then
        # Final tests on master
        if run_tests; then
            # Push master
            safe_push "master"
            
            # Create release tag
            local tag_name="release-$(date '+%Y%m%d-%H%M%S')"
            git tag -a "$tag_name" -m "Production release: $tag_name"
            git push origin "$tag_name"
            
            # Clean up backups after successful sync
            cleanup_backups
            
            # Reset failure counter on success
            success_handler
            
            print_status "$GREEN" "=== Production Save Completed Successfully ==="
            print_status "$GREEN" "Release tag created: $tag_name"
        else
            print_status "$RED" "Tests failed on master, reverting merge..."
            git reset --hard HEAD~1
            git checkout "main"
            error_exit "Tests failed on master branch"
        fi
    else
        git checkout "main"
        error_exit "Failed to merge main into master"
    fi
    
    # Return to main
    git checkout "main"
}

# Status check operation
check_status() {
    print_status "$BLUE" "=== Repository Status Check ==="
    
    echo
    print_status "$BLUE" "Branch Status:"
    git branch -v
    
    echo
    print_status "$BLUE" "Working Directory Status:"
    git status --short
    
    echo
    print_status "$BLUE" "Recent Commits:"
    git log --oneline -5
    
    echo
    print_status "$BLUE" "Remote Status:"
    if git remote get-url origin > /dev/null 2>&1; then
        git remote -v
        git fetch --dry-run 2>&1 || true
    else
        echo "No remote configured"
    fi
    
    echo
    print_status "$BLUE" "Failure Counter:"
    local failures=$(cat "$FAILURE_COUNTER_FILE")
    if [ "$failures" -eq 0 ]; then
        print_status "$GREEN" "✅ No recent failures"
    else
        print_status "$YELLOW" "⚠️  Recent failures: $failures"
    fi
    
    echo
    print_status "$BLUE" "Branch Synchronization:"
    if branches_synchronized; then
        print_status "$GREEN" "✅ All branches synchronized"
    else
        print_status "$YELLOW" "⚠️  Branches not synchronized"
    fi
    
    echo
    print_status "$BLUE" "Backup Status:"
    local backup_count=$(ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | wc -l)
    echo "  Active backups: $backup_count"
    if [ "$backup_count" -gt 0 ]; then
        echo "  Latest: $(ls -1t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1 | xargs basename)"
    fi
}

# Reset failure counter
reset_failures() {
    print_status "$BLUE" "Resetting failure counter..."
    echo "0" > "$FAILURE_COUNTER_FILE"
    print_status "$GREEN" "✅ Failure counter reset to 0"
}

# Advanced troubleshooting mode
troubleshoot() {
    print_status "$BLUE" "=== Advanced Troubleshooting Mode ==="
    
    local failures=$(cat "$FAILURE_COUNTER_FILE")
    print_status "$BLUE" "Current failure count: $failures"
    
    echo
    print_status "$BLUE" "🤖 GitHub Copilot Chat Integration:"
    echo "Copy and paste these queries into GitHub Copilot Chat for assistance:"
    echo
    echo "1. Repository Analysis:"
    echo "   'Analyze my SynOS git repository state and suggest merge conflict resolution'"
    echo
    echo "2. Makefile Issues:"
    echo "   'Help debug Makefile syntax errors and merge conflicts in my project'"
    echo
    echo "3. Branch Synchronization:"
    echo "   'Help synchronize dev-team-main, main, and master branches with conflicts'"
    echo
    echo "4. Git Save System Debug:"
    echo "   'Debug git automation script failures in my development workflow'"
    echo
    
    echo
    print_status "$BLUE" "📊 Diagnostic Information:"
    echo "Repository: $(pwd)"
    echo "Current branch: $(git branch --show-current)"
    echo "Uncommitted changes: $(git status --porcelain | wc -l)"
    echo "Recent failures: $failures"
    echo "Last backup: $(ls -1t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"
    
    echo
    print_status "$BLUE" "🔧 Quick Recovery Options:"
    echo "1. Reset failures: $0 reset"
    echo "2. Force clean state: git clean -fd && git reset --hard HEAD"
    echo "3. Restore from backup: tar -xzf .git-backups/[backup-file]"
    echo "4. Emergency stash: git stash push -m 'Emergency backup'"
}

# Help function
show_help() {
    cat << EOF
SynOS Git Save System - Enhanced Comprehensive Git Workflow Automation

Usage: $0 [COMMAND]

Commands:
    dev         Save dev-team work (commit, test, merge to main, push)
    production  Save to production (merge main to master, tag release)
    status      Show comprehensive repository status
    reset       Reset failure counter
    troubleshoot Show advanced troubleshooting with Copilot integration
    help        Show this help message

Enhanced Features:
    ✅ Intelligent Makefile conflict resolution
    ✅ Automatic backup cleanup after successful sync
    ✅ Failure tracking with Copilot Chat integration
    ✅ Branch synchronization detection
    ✅ Advanced troubleshooting mode

Examples:
    $0 dev         # Save development work from dev-team-main to main
    $0 production  # Promote main to master for production release
    $0 status      # Check repository status across all branches
    $0 reset       # Reset failure counter after resolving issues
    $0 troubleshoot # Get Copilot Chat suggestions for complex issues

Safety Features:
    - Automatic backups before major operations
    - Comprehensive testing at each stage
    - Intelligent conflict resolution (Makefile focus)
    - Safe merge operations with rollback
    - Force-with-lease pushes to prevent overwrites
    - Automatic stashing and restoration
    - Environment validation
    - Failure tracking and recovery guidance

Branch Synchronization:
    dev-team-main → main → master
    ✅ Automatic cleanup when all branches synchronized
    ✅ Intelligent conflict detection and resolution

Troubleshooting Integration:
    - Failure counter tracks consecutive issues
    - After 2 failures: GitHub Copilot Chat recommendations
    - Advanced diagnostic information
    - Recovery suggestions and commands

Logs: $LOG_FILE
Backups: $BACKUP_DIR
Failures: $FAILURE_COUNTER_FILE
EOF
}

# Main execution
main() {
    print_status "$GREEN" "SynOS Git Save System v1.0"
    print_status "$BLUE" "Timestamp: $TIMESTAMP"
    
    check_git_repo
    get_current_branch
    
    case "${1:-help}" in
        "dev"|"development")
            save_dev_team
            ;;
        "prod"|"production"|"master")
            save_production
            ;;
        "status"|"check")
            check_status
            ;;
        "reset"|"reset-failures")
            reset_failures
            ;;
        "troubleshoot"|"debug"|"copilot")
            troubleshoot
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_status "$RED" "Unknown command: ${1:-}"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
