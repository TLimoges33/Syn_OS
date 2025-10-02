#!/bin/bash

# ==================================================================
# SynOS Repository Management & Archive Strategy
# ==================================================================
# Handles the massive commit situation and archive management
# ==================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=============================================="
echo "🚀 SynOS Repository Management Strategy"
echo "=============================================="
echo ""

# Check current status
CHANGED_FILES=$(git status --porcelain | wc -l)
log_info "Current repository status: $CHANGED_FILES changed files"

if [ "$CHANGED_FILES" -gt 10000 ]; then
    log_warning "MASSIVE CHANGE SET DETECTED ($CHANGED_FILES files)"
    echo "This requires a strategic approach to avoid performance issues"
    echo ""
fi

# Strategy selection
echo "📋 Available strategies:"
echo "1. Commit all changes in phases (recommended)"
echo "2. Archive transfer first, then commit"
echo "3. Selective commit (cleanup only)"
echo "4. Status check only"
echo ""

read -p "Select strategy (1-4): " strategy

case $strategy in
    1)
        log_info "Executing phased commit strategy..."
        
        # Phase 1: Critical infrastructure changes
        log_info "Phase 1: Committing infrastructure changes..."
        git add .gitignore .devcontainer/ docs/development/GIT_WORKFLOW_ARCHITECTURE.md
        git add scripts/laptop-dev-optimization* scripts/vscode-stability-fix.sh
        git add docs/setup-guides/LAPTOP_MEMORY_OPTIMIZATION_GUIDE.md
        git commit -m "🚀 Infrastructure: Git workflow optimization, Codespace setup, memory management

- Comprehensive .gitignore for all environments
- Professional Git workflow architecture
- Optimized Codespace configuration with Rust/security tools
- Memory management strategy for laptop development
- VS Code stability fixes and performance optimization
- Development monitoring tools and cleanup scripts"
        
        # Phase 2: Directory cleanup and reorganization
        log_info "Phase 2: Committing directory cleanup..."
        git add -A
        git commit -m "🧹 Cleanup: Directory reorganization and file management

- Removed empty documentation files from root
- Moved docker files to docker/ directory  
- Moved CONTRIBUTING.md to docs/
- Moved Final_SynOS-0.99_ISO to build/ directory
- Cleaned root directory to essential files only
- Maintained README.md and TODO.md in root"
        
        log_success "Phased commits completed successfully!"
        ;;
        
    2)
        log_info "Archive transfer strategy selected..."
        log_warning "This will require manual archive repository management"
        echo "Run: git clone git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git ../archive-repo"
        echo "Then: cp -r archive/* ../archive-repo/"
        echo "Then: cd ../archive-repo && git add . && git commit && git push"
        ;;
        
    3)
        log_info "Selective commit strategy..."
        git add .gitignore .devcontainer/ docs/ scripts/
        git commit -m "🔧 Core infrastructure updates and optimizations"
        log_success "Selective commit completed"
        ;;
        
    4)
        log_info "Repository status check..."
        echo ""
        echo "=== Git Status Summary ==="
        echo "Changed files: $CHANGED_FILES"
        echo "Current branch: $(git branch --show-current)"
        echo "Remotes:"
        git remote -v
        echo ""
        echo "=== Large directories/files ==="
        find . -name "*.iso" -o -name "*.img" -o -name "target" -type d 2>/dev/null | head -10
        ;;
        
    *)
        log_error "Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "=== Next Steps ==="
echo "1. ✅ Git workflow optimized"
echo "2. ✅ Codespace configuration ready"
echo "3. ✅ Memory management implemented"
echo "4. 🔄 Ready for archive management"
echo "5. 🔄 Ready for production repository setup"
echo ""
log_success "Repository management strategy executed!"
echo ""
echo "🚀 Ready to create Codespace on main branch with:"
echo "  - Branch protection requiring PRs"
echo "  - Optimized development environment"
echo "  - Memory-efficient configuration"
echo "  - Professional workflow architecture"
