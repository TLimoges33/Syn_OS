# 🔧 SynOS Scripts Directory

**Automated scripts for building, deploying, and maintaining SynOS.**

All scripts are organized by function into numbered categories for easy navigation.

---

## 📂 Scripts Organization

### [01-deployment/](01-deployment/)

**Deployment scripts** - Deploy SynOS to production environments

- `deploy-synos-v1.0.sh` - Full deployment script (requires sudo)
- `deploy-synos-v1.0-nosudo.sh` - Deployment without sudo (limited features)

### [02-build/](02-build/)

**Build scripts** - ISO creation, enhancement, and build automation

#### Core Builders ([core/](02-build/core/))

- `build-synos-v1.0-complete.sh` - Complete v1.0 build
- `ultimate-iso-builder.sh` - Ultimate edition ISO builder
- `parrot-inspired-builder.sh` - ParrotOS-inspired builder
- `smart-iso-builder.sh` - Smart build with optimization
- `rebuild-iso-only.sh` - Rebuild ISO from existing chroot
- `build-synos-ultimate-iso.sh` - Ultimate build script
- `FINAL_BUILD_COMMANDS.sh` - Final build command sequences

#### Variants ([variants/](02-build/variants/))

- `build-synos-minimal-iso.sh` - Minimal ISO (lightweight)
- `lightweight-synos-implementation.sh` - Lightweight variant

#### Enhancement ([enhancement/](02-build/enhancement/))

- `enhance-synos-iso.sh` - Main enhancement script
- `enhance-synos-ultimate.sh` - Ultimate enhancements
- `enhance-phase1-*.sh` - Phase 1 enhancements (repos, tools)
- `enhance-phase2-*.sh` - Phase 2 (core integration)
- `enhance-phase3-*.sh` - Phase 3 (branding)
- `enhance-phase4-*.sh` - Phase 4 (configuration)
- `enhance-phase5-*.sh` - Phase 5 (demo, docs)
- `enhance-phase6-*.sh` - Phase 6 (ISO rebuild)
- `enhancement-utils.sh` - Shared enhancement utilities

#### Tools ([tools/](02-build/tools/))

- `add-starred-repos.sh` - Add starred GitHub repositories
- `add-high-value-tools.sh` - Install high-value security tools
- `organize-tools-in-menu.sh` - Organize menu structure
- `install-ai-daemon.sh` - Install AI consciousness daemon
- Various other tool installation scripts

#### Optimization ([optimization/](02-build/optimization/))

- `optimize-chroot-for-iso.sh` - Optimize chroot for ISO
- `remove-pytorch-cuda.sh` - Remove heavy CUDA dependencies
- `audit-and-cleanup-chroot.sh` - Audit and clean chroot
- `quick-v1.0-fix.sh` - Quick v1.0 fixes
- Comprehensive fix and audit scripts

#### Monitoring ([monitoring/](02-build/monitoring/))

- `build-monitor.sh` - Monitor build progress (shell)
- `build-monitor.py` - Monitor build progress (Python)

#### Auditing ([auditing/](02-build/auditing/))

- `final-pre-build-audit.sh` - Pre-build audit
- `pre-build-cleanup.sh` - Pre-build cleanup
- `verify-pre-build.sh` - Verify pre-build state

#### Launchers ([launchers/](02-build/launchers/))

- `launch-ultimate-build.sh` - Launch ultimate build
- `smart-parrot-launcher.sh` - Smart ParrotOS launcher

#### Helpers ([helpers/](02-build/helpers/))

- Utility functions and helper scripts

### [03-maintenance/](03-maintenance/)

**Maintenance scripts** - Project organization and maintenance

- `reorganize-project.sh` - Project reorganization script
- `REORGANIZATION_SUMMARY.md` - Previous reorganization summary

### [04-testing/](04-testing/)

**Testing scripts** - Automated testing and validation

- (Future testing scripts will go here)

### [05-automation/](05-automation/)

**Automation scripts** - Workflow automation and orchestration

- `index.sh` - Script index and automation

### [06-utilities/](06-utilities/)

**Utility scripts** - Miscellaneous utilities

- (Utility scripts will go here)

---

## 🚀 Quick Start

### Build a Complete ISO

```bash
# Recommended: Ultimate ISO with all features
./02-build/core/ultimate-iso-builder.sh

# Alternative: Complete v1.0 build
./02-build/core/build-synos-v1.0-complete.sh
```

### Build a Minimal ISO

```bash
./02-build/variants/build-synos-minimal-iso.sh
```

### Enhance Existing ISO

```bash
# Phase-by-phase enhancement
./02-build/enhancement/enhance-phase1-repos-tools.sh
./02-build/enhancement/enhance-phase2-core-integration.sh
./02-build/enhancement/enhance-phase3-branding.sh
# ... continue through phases

# Or all at once
./02-build/enhancement/enhance-synos-ultimate.sh
```

### Deploy SynOS

```bash
# With sudo (full features)
sudo ./01-deployment/deploy-synos-v1.0.sh

# Without sudo (limited)
./01-deployment/deploy-synos-v1.0-nosudo.sh
```

---

## 📋 Build Script Categories

### Core Builders

- **Purpose:** Complete ISO builds from scratch
- **Input:** Source code, dependencies
- **Output:** Bootable ISO files
- **Time:** 30-90 minutes

### Variants

- **Purpose:** Specialized ISO builds (minimal, lightweight)
- **Input:** Base system
- **Output:** Variant-specific ISOs
- **Time:** 20-45 minutes

### Enhancement

- **Purpose:** Add features, tools, branding to existing build
- **Input:** Existing chroot or ISO
- **Output:** Enhanced chroot/ISO
- **Time:** Variable (5-60 minutes per phase)

### Tools

- **Purpose:** Install specific tool sets or configurations
- **Input:** Chroot environment
- **Output:** Configured chroot
- **Time:** 5-30 minutes

### Optimization

- **Purpose:** Fix issues, optimize size, audit quality
- **Input:** Build artifacts
- **Output:** Optimized/fixed artifacts
- **Time:** 5-20 minutes

---

## 🔍 Script Naming Convention

- `build-*.sh` - Full build scripts (create ISO from scratch)
- `enhance-*.sh` - Enhancement scripts (add to existing build)
- `install-*.sh` - Installation scripts (add components)
- `fix-*.sh` - Fix/repair scripts (resolve issues)
- `optimize-*.sh` - Optimization scripts (improve performance/size)
- `audit-*.sh` - Audit scripts (verify quality)
- `deploy-*.sh` - Deployment scripts (production deployment)

---

## ⚠️ Important Notes

### Build Requirements

- **Disk Space:** 30-50GB free space
- **RAM:** 8GB minimum, 16GB recommended
- **Time:** 30-90 minutes for full build
- **Network:** Fast internet for package downloads

### Permissions

- Most build scripts require sudo/root
- Deployment scripts vary (check individual scripts)
- Test in VM before production deployment

### Build Artifacts

- Chroot: `build/synos-ultimate/chroot/`
- ISO output: `build/` directory
- Logs: Check each script's output directory

---

## 📊 Statistics

- **Total Scripts:** 50+ organized scripts
- **Categories:** 6 main categories
- **Build Variants:** 3 (Ultimate, Minimal, Lightweight)
- **Enhancement Phases:** 6 phases
- **Last Reorganization:** October 12, 2025

---

## 🔗 Related Documentation

- [Build Guide](/docs/03-build/ultimate-build-guide.md)
- [ISO Build Instructions](/docs/03-build/iso-build-instructions.md)
- [Project Status](/docs/project-status/PROJECT_STATUS.md)

---

**Last Updated:** October 12, 2025
**Maintainer:** SynOS Development Team
