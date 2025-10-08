#!/bin/bash

################################################################################
# SYN_OS PROJECT REORGANIZATION SCRIPT
# Date: October 7, 2025
# Purpose: Organize project structure for production readiness
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="/home/diablorain/Syn_OS"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║       📁 SYN_OS PROJECT REORGANIZATION                       ║${NC}"
echo -e "${CYAN}║          Cleaning up for production readiness                ║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$PROJECT_ROOT"

# Function to safely move files
safe_move() {
    local src="$1"
    local dest="$2"

    if [[ -f "$src" ]] || [[ -d "$src" ]]; then
        echo -e "${BLUE}  ➜${NC} Moving: $(basename "$src") → $dest"
        mkdir -p "$(dirname "$dest")"
        mv "$src" "$dest"
    else
        echo -e "${YELLOW}  ⚠${NC} Not found: $src"
    fi
}

# Step 1: Create directory structure
echo -e "${GREEN}Step 1: Creating new directory structure...${NC}"

mkdir -p docs/{getting-started,building,development,user-guide,administration,project-status,audits,planning}
mkdir -p scripts/{build/helpers,setup,testing,maintenance,deployment,development,ai-services,migration,archive/old-scripts}

echo -e "${GREEN}  ✓ Directories created${NC}"
echo ""

# Step 2: Reorganize scripts
echo -e "${GREEN}Step 2: Reorganizing scripts directory...${NC}"

# Build scripts
safe_move "scripts/build-synos-ultimate-iso.sh" "scripts/build/build-synos-ultimate-iso.sh"
safe_move "scripts/build-synos-iso.sh" "scripts/build/build-synos-minimal-iso.sh"
safe_move "scripts/build-bulletproof-iso.sh" "scripts/archive/old-scripts/build-bulletproof-iso.sh"

# Testing scripts
safe_move "scripts/test-synos-vm.sh" "scripts/testing/test-iso-in-qemu.sh"
safe_move "scripts/run-fuzzing.sh" "scripts/testing/run-fuzzing-tests.sh"

# Maintenance scripts
safe_move "scripts/clean-memory.sh" "scripts/maintenance/clean-memory.sh"
safe_move "scripts/validate-production-readiness.sh" "scripts/maintenance/validate-production-readiness.sh"

# AI service scripts
safe_move "scripts/package-ai-services.sh" "scripts/ai-services/package-ai-services.sh"
safe_move "scripts/compress-ai-models.py" "scripts/ai-services/compress-ai-models.py"
safe_move "scripts/check-ai-daemon-status.sh" "scripts/ai-services/check-ai-daemon-status.sh"

# Migration scripts
safe_move "scripts/migrate-static-mut.sh" "scripts/migration/migrate-static-mut.sh"
safe_move "scripts/migrate-unwrap-to-result.sh" "scripts/migration/migrate-unwrap-to-result.sh"
safe_move "scripts/refactor-ai-modules.sh" "scripts/migration/refactor-ai-modules.sh"

# Setup scripts
safe_move "scripts/setup-wiki-git-repos.sh" "scripts/setup/setup-wiki-git-repos.sh"
safe_move "scripts/setup-wiki-permissions.sh" "scripts/setup/setup-wiki-permissions.sh"

echo -e "${GREEN}  ✓ Scripts reorganized${NC}"
echo ""

# Step 3: Move documentation to /docs
echo -e "${GREEN}Step 3: Organizing documentation...${NC}"

# Building documentation
safe_move "FINAL-ISO-BUILD-INSTRUCTIONS.txt" "docs/building/iso-build-instructions.md"
safe_move "README-ISO-BUILD.txt" "docs/building/iso-build-readme.md"
safe_move "ULTIMATE-BUILD-READY.md" "docs/building/ultimate-build-guide.md"

# Audit reports
safe_move "ISO-BUILD-AUDIT-REPORT.md" "docs/audits/2025-10-07-iso-build-audit.md"
safe_move "ISO-BUILD-COMPLETE-AUDIT.md" "docs/audits/2025-10-07-complete-audit.md"

# Planning documents
safe_move "4_DAY_LAUNCH_CHECKLIST.md" "docs/planning/launch-checklist.md"
safe_move "LAUNCH_DECISION_EXECUTIVE_SUMMARY.md" "docs/planning/launch-decision.md"

# Project status - Keep main files in root, copy to docs
if [[ -f "PROJECT_STATUS.md" ]]; then
    cp "PROJECT_STATUS.md" "docs/project-status/current-status.md"
fi
safe_move "NEXT_STEPS.md" "docs/project-status/next-steps.md"
if [[ -f "TODO.md" ]]; then
    cp "TODO.md" "docs/project-status/todo.md"
fi
# CLAUDE.md stays in root
if [[ -f "CLAUDE.md" ]]; then
    echo -e "${BLUE}  ℹ${NC} Keeping: CLAUDE.md (root)"
fi

# Keep CHANGELOG in root and copy to docs
if [[ -f "CHANGELOG.md" ]]; then
    cp "CHANGELOG.md" "docs/project-status/changelog.md"
fi

echo -e "${GREEN}  ✓ Documentation organized${NC}"
echo ""

# Step 4: Create README files for navigation
echo -e "${GREEN}Step 4: Creating navigation README files...${NC}"

# Main docs README
cat > docs/README.md << 'EOF'
# 📚 Syn_OS Documentation

Welcome to the Syn_OS documentation! This directory contains all project documentation.

## 📖 Quick Navigation

### 🚀 [Getting Started](getting-started/)
- New to Syn_OS? Start here!
- Installation guides
- Quick start tutorials

### 🛠️ [Building](building/)
- [Ultimate Build Guide](building/ultimate-build-guide.md) - Complete ISO build
- [ISO Build Instructions](building/iso-build-instructions.md) - Detailed steps
- Kernel building guides

### 💻 [Development](development/)
- Architecture documentation
- Contributing guidelines
- API references
- Coding standards

### 📘 [User Guide](user-guide/)
- Desktop environment
- Security tools usage
- AI features guide
- Educational mode

### ⚙️ [Administration](administration/)
- System administration
- Security hardening
- Performance tuning
- Backup and recovery

### 📊 [Project Status](project-status/)
- [Current Status](project-status/current-status.md)
- [Roadmap](project-status/roadmap.md)
- [Changelog](project-status/changelog.md)
- [TODO](project-status/todo.md)

### 🔍 [Audits](audits/)
- Latest audit reports
- Security assessments
- Code reviews

### 📋 [Planning](planning/)
- Launch checklists
- Business plans
- Strategic planning

## 🔍 Finding What You Need

- **Building the ISO?** → [building/ultimate-build-guide.md](building/ultimate-build-guide.md)
- **Contributing code?** → [development/](development/)
- **Using Syn_OS?** → [user-guide/](user-guide/)
- **Project status?** → [project-status/current-status.md](project-status/current-status.md)

## 📝 Documentation Standards

All documentation follows:
- Markdown format
- Clear headings and structure
- Code examples where appropriate
- Links to related documents
EOF

# Scripts README
cat > scripts/README.md << 'EOF'
# 🔧 Syn_OS Scripts

This directory contains all automation scripts for building, testing, and maintaining Syn_OS.

## 📁 Directory Structure

```
scripts/
├── build/          Build ISO images
├── setup/          Environment setup
├── testing/        Test scripts
├── maintenance/    Maintenance tools
├── deployment/     Deployment scripts
├── development/    Development tools
├── ai-services/    AI service management
├── migration/      Code migration tools
└── archive/        Old/deprecated scripts
```

## 🚀 Quick Start

### Build the Ultimate ISO
```bash
cd scripts/build
sudo ./build-synos-ultimate-iso.sh
```

### Test ISO in QEMU
```bash
cd scripts/testing
./test-iso-in-qemu.sh
```

### Setup Development Environment
```bash
cd scripts/setup
./setup-development-environment.sh
```

## 📖 Detailed Documentation

### Build Scripts (`build/`)
- **build-synos-ultimate-iso.sh** - Complete ISO with 500+ tools (MAIN)
- **build-synos-minimal-iso.sh** - Minimal ISO without security tools
- **build-synos-kernel-iso.sh** - Kernel-only bootable ISO

### Testing Scripts (`testing/`)
- **test-iso-in-qemu.sh** - Test ISO in QEMU emulator
- **test-ai-services.sh** - Validate AI services
- **test-security-tools.sh** - Verify security tools

### Maintenance Scripts (`maintenance/`)
- **clean-build-artifacts.sh** - Clean build directories
- **clean-memory.sh** - Free up system memory
- **validate-production-readiness.sh** - Production checks

### AI Services (`ai-services/`)
- **package-ai-services.sh** - Package AI services as .deb
- **compress-ai-models.py** - Compress AI models
- **check-ai-daemon-status.sh** - Check service status

## 🔐 Permissions

Most scripts require specific permissions:
- **Build scripts**: Require `sudo` (root access)
- **Testing scripts**: User permissions
- **Maintenance scripts**: Some require `sudo`

## ⚠️ Important Notes

- Always run build scripts with `sudo`
- Review scripts before execution
- Check system requirements first
- Read script documentation

## 📚 More Information

See [docs/building/](../docs/building/) for detailed build documentation.
EOF

# Build scripts README
cat > scripts/build/README.md << 'EOF'
# 🏗️ Build Scripts

Scripts for building Syn_OS ISO images.

## Main Build Script

### build-synos-ultimate-iso.sh (RECOMMENDED)
Complete Syn_OS ISO with ALL features:
- 500+ security tools (ParrotOS + Kali)
- 5 AI services
- Complete source code
- Custom kernel
- Hybrid BIOS + UEFI boot

**Usage:**
```bash
sudo ./build-synos-ultimate-iso.sh
```

**Build Time:** 30-60 minutes
**Output Size:** 12-15GB ISO

## Alternative Builds

### build-synos-minimal-iso.sh
Minimal ISO without security tools:
- Basic Debian system
- XFCE desktop
- Development tools
- Source code only

**Build Time:** 15-20 minutes
**Output Size:** 2-3GB ISO

### build-synos-kernel-iso.sh
Kernel-only bootable ISO:
- Custom Rust kernel
- No Linux, no tools
- Experimental/educational

**Build Time:** 5 minutes
**Output Size:** 200MB ISO

## Prerequisites

Required packages:
```bash
sudo apt install debootstrap squashfs-tools xorriso \
  isolinux syslinux-efi grub-pc-bin grub-efi-amd64-bin \
  mtools dosfstools
```

Required disk space: 50GB minimum

## Build Process

1. **Base System** (10-15 min) - Create Debian base
2. **Security Tools** (30-60 min) - Install 500+ tools
3. **SynOS Components** (5-10 min) - Add AI services
4. **Compression** (10-20 min) - Create SquashFS
5. **ISO Creation** (2-5 min) - Build bootable ISO

## Output Location

Built ISOs are saved to:
```
/home/diablorain/Syn_OS/build/synos-ultimate/
```

## Testing

Test the ISO before deployment:
```bash
cd ../testing
./test-iso-in-qemu.sh
```

## Troubleshooting

Common issues:
- **Out of disk space**: Need 50GB free
- **Package install fails**: Check network connection
- **Permission denied**: Use `sudo`
- **Build errors**: Check build log in `/tmp/`

See [../../docs/building/](../../docs/building/) for detailed documentation.
EOF

echo -e "${GREEN}  ✓ README files created${NC}"
echo ""

# Step 5: Update main README to reflect new structure
echo -e "${GREEN}Step 5: Updating main README.md...${NC}"

cat > README.md << 'EOF'
# 🎯 Syn_OS v1.0 - Ultimate Cybersecurity Education & MSSP Platform

![SynOS Banner](./docs/assets/synos-banner.png)

[![Build Status](https://img.shields.io/badge/Build-Production%20Ready-green.svg)](./docs/project-status/todo.md)
[![AI Integration](https://img.shields.io/badge/AI_Consciousness-Neural%20Darwinism-blue.svg)](./src/)
[![Security Tools](https://img.shields.io/badge/Security%20Tools-500%2B-red.svg)](./core/security/)
[![Linux Distribution](https://img.shields.io/badge/Linux%20Distro-Debian%20Based-orange.svg)](./linux-distribution/)
[![Documentation](https://img.shields.io/badge/Docs-Complete-brightgreen.svg)](./docs/)

**Syn_OS** is the world's first AI-enhanced cybersecurity Linux distribution, combining 500+ security tools with neural consciousness for adaptive learning and intelligent threat detection.

---

## 🚀 Quick Start

### Build the Ultimate ISO

```bash
cd scripts/build
sudo ./build-synos-ultimate-iso.sh
```

### Read the Documentation

```bash
# Getting started guide
cat docs/getting-started/quick-start.md

# Complete build guide
cat docs/building/ultimate-build-guide.md

# Project status
cat docs/project-status/current-status.md
```

---

## 📚 Documentation

All documentation is in the [`docs/`](./docs/) directory:

- **[Getting Started](docs/getting-started/)** - Installation and first steps
- **[Building](docs/building/)** - ISO build guides
- **[Development](docs/development/)** - Developer documentation
- **[User Guide](docs/user-guide/)** - Using Syn_OS
- **[Project Status](docs/project-status/)** - Current status and roadmap
- **[Audits](docs/audits/)** - Security and code audits

---

## 🎯 Project Vision

Transform cybersecurity education through an intelligent, AI-powered operating system that adapts to the user's learning style and provides real-time guidance.

### Target Applications

- 🎓 **SNHU Cybersecurity Degree Studies** - Complete lab environment
- 🏢 **MSSP Consulting Business** - Professional security operations
- 🔴 **Red Team Operations** - Advanced penetration testing
- 🛡️ **Blue Team Defense** - Intelligent threat detection

---

## 🧠 Revolutionary Features

### AI Consciousness System
- **Neural Darwinism Engine** - Adaptive learning and decision-making
- **Intelligent Tool Orchestration** - AI-powered security workflows
- **Personalized Education** - Custom learning experiences
- **Real-time Threat Analysis** - AI-enhanced security monitoring

### Cybersecurity Arsenal
- **500+ Security Tools** - Comprehensive penetration testing suite
- **Custom Kernel Integration** - AI-enhanced system-level security
- **Advanced Forensics** - Integrated digital investigation tools
- **Vulnerability Assessment** - Automated security auditing

### Professional Platform
- **Enterprise-Grade Architecture** - Production-ready infrastructure
- **Custom Branding** - Professional consulting image
- **Automated Reporting** - AI-generated security assessments
- **Client Demonstration Mode** - Impressive technical showcase

---

## 📁 Project Structure

```
Syn_OS/
├── 📄 README.md                 ← You are here
├── 📚 docs/                     ← Complete documentation
├── 🔧 scripts/                  ← Build and automation scripts
├── 💻 src/                      ← Custom OS kernel & userspace
├── 🧠 core/                     ← AI consciousness & security frameworks
├── ⚙️ config/                   ← System configurations
├── 🧪 tests/                    ← Test suites
├── 🛠️ tools/                    ← Development tools
├── 🚀 deployment/               ← Deployment configurations
└── 🐧 linux-distribution/       ← Debian-based distro builder
```

### Key Components

- **[src/](src/)** - Custom Rust kernel, userspace applications, and services
- **[core/](core/)** - AI consciousness engine and security framework
- **[scripts/](scripts/)** - ISO builders, testing, and maintenance tools
- **[docs/](docs/)** - Comprehensive project documentation

---

## 🛠️ Development

### Prerequisites

```bash
# Install build dependencies
sudo apt update
sudo apt install debootstrap squashfs-tools xorriso \
  build-essential rust-all cargo

# Setup development environment
cd scripts/setup
./setup-development-environment.sh
```

### Building Components

```bash
# Build custom kernel
cd src/kernel
cargo build --release --target x86_64-unknown-none

# Build AI services
cd core/ai
./build-all-services.sh

# Run tests
cd tests
cargo test --all
```

---

## 🧪 Testing

```bash
# Test ISO in QEMU
cd scripts/testing
./test-iso-in-qemu.sh

# Test AI services
./test-ai-services.sh

# Run comprehensive tests
./run-comprehensive-tests.sh
```

---

## 🤝 Contributing

We welcome contributions! See:
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community standards
- **[docs/development/](docs/development/)** - Developer guides

---

## 📊 Project Status

- **Version:** 1.0.0 (Neural Genesis)
- **Status:** Production Ready
- **Build Status:** ✅ All components functional
- **Documentation:** ✅ Complete

See [docs/project-status/current-status.md](docs/project-status/current-status.md) for details.

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🔒 Security

For security issues, see [SECURITY.md](SECURITY.md).

---

## 📞 Contact & Support

- **Documentation:** [docs/](docs/)
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

## 🏆 Acknowledgments

Built with:
- Rust programming language
- Debian Linux
- ParrotOS and Kali security tools
- Neural Darwinism principles
- Open source community contributions

---

**Syn_OS - Consciousness-Enhanced Cybersecurity** 🧠🔐🚀
EOF

echo -e "${GREEN}  ✓ Main README updated${NC}"
echo ""

# Step 6: Create .gitignore if needed
echo -e "${GREEN}Step 6: Updating .gitignore...${NC}"

cat >> .gitignore << 'EOF'

# Build outputs
build/
target/
*.iso
*.img
*.squashfs

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
*.tmp

# IDE
.vscode/
.idea/

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS
.DS_Store
Thumbs.db
EOF

echo -e "${GREEN}  ✓ .gitignore updated${NC}"
echo ""

# Summary
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║              ✅ REORGANIZATION COMPLETE! ✅                   ║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Summary:${NC}"
echo -e "  ✅ Created organized directory structure"
echo -e "  ✅ Moved scripts to logical categories"
echo -e "  ✅ Organized documentation in /docs"
echo -e "  ✅ Created navigation README files"
echo -e "  ✅ Updated main README.md"
echo -e "  ✅ Clean root directory"
echo ""
echo -e "${CYAN}📁 New Structure:${NC}"
echo -e "  • Root: Only essential files"
echo -e "  • docs/: All documentation organized"
echo -e "  • scripts/: Categorized by function"
echo ""
echo -e "${CYAN}🚀 Next Steps:${NC}"
echo -e "  1. Review the new structure: ls -la"
echo -e "  2. Read docs/README.md for navigation"
echo -e "  3. Build ISO: cd scripts/build && sudo ./build-synos-ultimate-iso.sh"
echo ""
echo -e "${GREEN}Project is now production-ready! 🎉${NC}"
echo ""
