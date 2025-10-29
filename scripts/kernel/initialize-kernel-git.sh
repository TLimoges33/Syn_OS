#!/bin/bash
# Initialize Git Repository for SynOS Kernel Development
# Creates git repo, commits Phase 1 baseline, and prepares for Phase 2 branch

set -e  # Exit on error

KERNEL_DIR="/usr/src/linux-source-6.12"

echo "=========================================="
echo "SynOS Kernel Git Repository Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (sudo)"
    echo "   Reason: /usr/src/ requires root permissions"
    exit 1
fi

# Check if kernel source exists
if [ ! -d "$KERNEL_DIR" ]; then
    echo "❌ Error: Kernel source not found at $KERNEL_DIR"
    exit 1
fi

cd "$KERNEL_DIR"
echo "Working directory: $KERNEL_DIR"
echo ""

# Initialize git repository
if [ -d .git ]; then
    echo "✅ Git repository already initialized"
else
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
fi
echo ""

# Configure git (if not already configured)
if ! git config user.name >/dev/null 2>&1; then
    echo "Configuring git user..."
    git config user.name "SynOS Development Team"
    git config user.email "synos@localhost"
    echo "✅ Git user configured"
fi
echo ""

# Create .gitignore for kernel-specific files
echo "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Kernel build artifacts
*.o
*.o.d
*.cmd
*.ko
*.mod
*.mod.c
*.symvers
*.order
.tmp_versions/
Module.markers
Module.symvers
modules.builtin
*.dwo

# Compiled files
*.a
*.s
*.i
*.lst

# Build directories
build/
debian/

# Editor files
*.swp
*.swo
*~
.*.sw?

# IDE files
.vscode/
.idea/

# Patches
*.patch
*.diff
*.orig
*.rej

# Cscope/ctags
cscope.*
tags
TAGS

# Backup files
*.bak
*.old
EOF
echo "✅ .gitignore created"
echo ""

# Check if we already have commits
if git rev-parse HEAD >/dev/null 2>&1; then
    echo "✅ Repository already has commits"
    COMMITS=$(git log --oneline | wc -l)
    echo "   Current commits: $COMMITS"
    echo ""
    echo "Repository status:"
    git log --oneline -5
else
    # Initial commit
    echo "Creating initial commit (Phase 1 baseline)..."
    echo "This may take a few minutes - adding ~70,000 files..."

    git add .

    git commit -m "Phase 1 Complete: Baseline SynOS Kernel 6.12.32-synos-ai-v0.1

This is the working baseline kernel that successfully:
- Compiles without errors (20,817 object files)
- Installs 4,221 kernel modules
- Creates 4 Debian packages (113 MB)
- Boots successfully in QEMU VM
- Verified with: uname -r shows 6.12.32-synos-ai-v0.1

Build Statistics:
- Compilation time: 3.5 hours
- Source size: 1.2 GB extracted, 22 GB after build
- Compiler: GCC 12.2.0 (Debian 12.2.0-14+deb12u1)
- Architecture: x86_64
- Base: ParrotOS 6.4 / Debian 12 Bookworm

Phase 1 Deliverables:
✅ Kernel build environment established
✅ Custom version string applied (-synos-ai-v0.1)
✅ Debian packages created and installable
✅ VM boot testing successful
✅ Foundation ready for Phase 2 AI syscalls

Next Phase: Phase 2 - AI-Aware System Calls
Branch: phase2-ai-syscalls (to be created)

Documentation:
- docs/05-planning/roadmaps/PHASE1_COMPLETION_REPORT.md
- docs/05-planning/roadmaps/PHASE1_KERNEL_SOURCE_SETUP.md
- docs/05-planning/roadmaps/PHASE1_QUICK_START.md
"

    echo "✅ Initial commit created"
fi
echo ""

# Create Phase 1 tag
echo "Creating Phase 1 tag..."
if git tag | grep -q "^phase1-complete$"; then
    echo "⚠️  Tag 'phase1-complete' already exists"
    echo "   Existing tag points to:"
    git show phase1-complete --no-patch --format="%h %s"
else
    git tag -a phase1-complete -m "Phase 1 Complete: Working baseline kernel 6.12.32-synos-ai-v0.1

This tag marks the successful completion of Phase 1:
- Working baseline kernel compiled and tested
- No AI features yet (stock Linux 6.12.32)
- Ready for Phase 2 AI syscall integration

To return to this state:
  git checkout phase1-complete

Artifacts:
- /boot/vmlinuz-6.12.32-synos-ai-v0.1 (12 MB)
- /lib/modules/6.12.32-synos-ai-v0.1/ (4,221 modules)
- /usr/src/*.deb packages (4 packages)
"
    echo "✅ Tag 'phase1-complete' created"
fi
echo ""

# Show current status
echo "=========================================="
echo "Git Repository Status"
echo "=========================================="
git log --oneline -5
echo ""
echo "Tags:"
git tag -l
echo ""
echo "Current branch:"
git branch --show-current
echo ""

echo "=========================================="
echo "✅ Git Repository Setup Complete!"
echo "=========================================="
echo ""
echo "Repository location: $KERNEL_DIR"
echo "Current branch: master"
echo "Baseline: phase1-complete tag"
echo ""
echo "Next steps:"
echo "1. Create Phase 2 branch: cd $KERNEL_DIR && git checkout -b phase2-ai-syscalls"
echo "2. Make Phase 2 changes (add syscalls, /proc interface)"
echo "3. Test in VM until working"
echo "4. Merge to master: git checkout master && git merge phase2-ai-syscalls"
echo "5. Tag Phase 2: git tag -a phase2-complete -m 'Phase 2 complete'"
echo ""
echo "Safety: You can always return to Phase 1 with:"
echo "  git checkout phase1-complete"
echo ""
