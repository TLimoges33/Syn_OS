# SynOS Build Scripts Migration Guide

**Version:** 2.0  
**Date:** October 23, 2025  
**Migration Deadline:** November 30, 2025 (30-day grace period)

---

## 🎯 Executive Summary

This guide helps you migrate from the legacy build scripts (62 scripts with 75% duplication) to the new consolidated build system (10 optimized scripts). The new system provides:

-   **87% code reduction** (13,000+ lines → 1,700 lines of unique code)
-   **Consistent interfaces** across all tools
-   **Comprehensive testing** and validation
-   **Professional features** (signing, Docker builds, archiving)
-   **Better maintainability** with shared library

**Timeline:**

-   **Today:** New scripts available, legacy scripts still work
-   **Nov 1-30, 2025:** Grace period with deprecation warnings
-   **Dec 1, 2025:** Legacy scripts archived (still available in archive/)

---

## 📋 Quick Migration Reference

### Most Common Script Migrations

| Old Script                   | New Script                            | Notes                    |
| ---------------------------- | ------------------------------------- | ------------------------ |
| `unified-iso-builder.sh`     | `scripts/build-iso.sh`                | Primary ISO builder      |
| `build-simple-kernel-iso.sh` | `scripts/build-kernel-only.sh`        | Fast kernel-only builds  |
| `build-full-linux-iso.sh`    | `scripts/build-full-linux.sh`         | Full distribution builds |
| Various test scripts         | `scripts/testing/test-iso.sh`         | Unified testing          |
| Various cleanup scripts      | `scripts/maintenance/clean-builds.sh` | Unified cleanup          |
| N/A (new)                    | `scripts/utilities/sign-iso.sh`       | ISO signing              |
| N/A (new)                    | `scripts/docker/build-docker.sh`      | Docker builds            |

### Quick Command Translation

```bash
# OLD: Build ISO with unified builder
./scripts/unified-iso-builder.sh

# NEW: Build ISO with new builder
./scripts/build-iso.sh

# OLD: Build kernel-only ISO
./scripts/build-simple-kernel-iso.sh

# NEW: Build kernel-only ISO
./scripts/build-kernel-only.sh

# OLD: Test ISO manually
qemu-system-x86_64 -cdrom build/SynOS.iso -m 2048

# NEW: Test ISO automatically
./scripts/testing/test-iso.sh build/SynOS.iso

# OLD: Clean builds manually
rm -rf build/workspace-*

# NEW: Clean builds safely
./scripts/maintenance/clean-builds.sh --old --days 7
```

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Before You Start](#before-you-start)
3. [Core Build Scripts](#core-build-scripts)
4. [Testing Scripts](#testing-scripts)
5. [Maintenance Scripts](#maintenance-scripts)
6. [Specialized Scripts](#specialized-scripts)
7. [Makefile Updates](#makefile-updates)
8. [CI/CD Integration](#cicd-integration)
9. [Troubleshooting](#troubleshooting)
10. [Rollback Plan](#rollback-plan)

---

## 1. Overview

### What Changed?

**Old System:**

-   62 separate scripts
-   ~13,000 lines of code (75% duplication)
-   Inconsistent interfaces
-   Limited error handling
-   No testing framework
-   Manual cleanup required

**New System:**

-   10 consolidated scripts + 1 shared library
-   4,609 lines of code (no duplication)
-   Consistent CLI interfaces
-   Comprehensive error handling
-   Built-in testing framework
-   Automated maintenance

### Why Migrate?

1. **Reduced Complexity:** Fewer scripts to learn and maintain
2. **Better Reliability:** Shared library ensures consistency
3. **Enhanced Features:** Testing, signing, Docker support
4. **Improved UX:** Better help, error messages, progress indication
5. **Future-Proof:** Easier to extend and maintain

### Migration Strategy

We're using a **phased migration** approach:

**Phase A (Now - Nov 1):** Evaluation

-   Test new scripts alongside old ones
-   Compare outputs and behavior
-   Report any issues

**Phase B (Nov 1-30):** Transition

-   Use new scripts as primary
-   Old scripts show deprecation warnings
-   Grace period for adjustments

**Phase C (Dec 1+):** Archive

-   Legacy scripts moved to `archive/`
-   Symlinks available for compatibility
-   Focus on new system

---

## 2. Before You Start

### Prerequisites Check

Run the environment verification script:

```bash
./scripts/testing/verify-build.sh --full
```

Expected output:

```
✓ Passed: 15+ checks
ℹ Failed: 0 checks
✓ Build environment ready!
```

### Backup Your Work

Before migrating, backup your current setup:

```bash
# Backup entire build directory
tar -czf ~/synos-build-backup-$(date +%Y%m%d).tar.gz build/

# Backup custom scripts (if any)
tar -czf ~/synos-scripts-backup-$(date +%Y%m%d).tar.gz scripts/
```

### Test New Scripts

Test the new scripts without affecting your workflow:

```bash
# Build a test ISO
./scripts/build-kernel-only.sh --test-qemu

# Verify it works
./scripts/testing/test-iso.sh build/SynOS-*.iso --quick
```

---

## 3. Core Build Scripts

### 3.1 Primary ISO Builder

**Old:** `scripts/unified-iso-builder.sh`  
**New:** `scripts/build-iso.sh`

#### Migration Steps

1. **Compare Options:**

    Old script options:

    ```bash
    ./scripts/unified-iso-builder.sh [options]
    # Limited options, hard-coded paths
    ```

    New script options:

    ```bash
    ./scripts/build-iso.sh --help
    # Options: --quick, --kernel-only, --no-source, --no-checksums, --output
    ```

2. **Basic Migration:**

    ```bash
    # OLD
    ./scripts/unified-iso-builder.sh

    # NEW (equivalent)
    ./scripts/build-iso.sh

    # NEW (faster, no source archive)
    ./scripts/build-iso.sh --quick
    ```

3. **Advanced Usage:**

    ```bash
    # Build without source archive
    ./scripts/build-iso.sh --no-source

    # Build to custom directory
    ./scripts/build-iso.sh --output /path/to/output

    # Quick build (kernel only, no checksums)
    ./scripts/build-iso.sh --quick --kernel-only
    ```

#### Behavior Changes

| Aspect              | Old Behavior    | New Behavior                                  |
| ------------------- | --------------- | --------------------------------------------- |
| Source archive      | Always included | Optional (--no-source to skip)                |
| Checksums           | Optional        | Always generated (use --no-checksums to skip) |
| Output location     | Fixed to build/ | Configurable with --output                    |
| Progress indication | Minimal         | Detailed with time estimates                  |
| Error handling      | Basic           | Comprehensive with cleanup                    |
| Help system         | None            | Full --help documentation                     |

#### Testing Your Migration

```bash
# 1. Build with new script
./scripts/build-iso.sh --output build/test-new

# 2. Compare with old build (if you have one)
ls -lh build/test-new/*.iso
ls -lh build/*.iso

# 3. Verify ISO structure
./scripts/testing/test-iso.sh build/test-new/*.iso

# 4. Boot test
./scripts/testing/test-iso.sh build/test-new/*.iso --full
```

---

### 3.2 Kernel-Only Builder

**Old:** `scripts/build-simple-kernel-iso.sh`  
**New:** `scripts/build-kernel-only.sh`

#### Migration Steps

1. **Basic Usage:**

    ```bash
    # OLD
    ./scripts/build-simple-kernel-iso.sh

    # NEW (equivalent)
    ./scripts/build-kernel-only.sh
    ```

2. **With QEMU Testing:**

    ```bash
    # NEW: Build and test automatically
    ./scripts/build-kernel-only.sh --test-qemu

    # Runs build, then boots in QEMU for verification
    ```

3. **Debug Mode:**

    ```bash
    # NEW: Build in debug mode (not stripped)
    ./scripts/build-kernel-only.sh --debug
    ```

#### Benefits of New Script

-   **Faster:** Optimized build process (2-5 minutes typical)
-   **Smaller ISOs:** ~50MB vs 100MB+
-   **Testing:** Built-in QEMU integration
-   **Targets:** Support for different kernel targets

---

### 3.3 Full Linux Distribution Builder

**Old:** `scripts/build-full-linux-iso.sh`, `scripts/parrot-remaster.sh`  
**New:** `scripts/build-full-linux.sh`

#### Migration Steps

1. **Basic Distribution:**

    ```bash
    # OLD (Parrot-based)
    ./scripts/parrot-remaster.sh

    # NEW (Choose base: debian or ubuntu)
    ./scripts/build-full-linux.sh --base-distro debian
    ```

2. **Variants:**

    ```bash
    # Minimal (core only)
    ./scripts/build-full-linux.sh --variant minimal

    # Standard (common tools)
    ./scripts/build-full-linux.sh --variant standard

    # Full (everything)
    ./scripts/build-full-linux.sh --variant full
    ```

3. **Skip Package Installation:**

    ```bash
    # Build without package installation (faster for testing)
    ./scripts/build-full-linux.sh --skip-packages
    ```

#### Variant Comparison

| Variant  | Size   | Build Time | Use Case          |
| -------- | ------ | ---------- | ----------------- |
| Minimal  | ~800MB | ~15 min    | Testing, embedded |
| Standard | ~1.5GB | ~25 min    | General purpose   |
| Full     | ~2.5GB | ~40 min    | Complete system   |

---

## 4. Testing Scripts

### 4.1 ISO Testing Framework

**Old:** Manual QEMU commands, various test scripts  
**New:** `scripts/testing/test-iso.sh`

#### Migration Steps

1. **Basic Testing:**

    ```bash
    # OLD
    qemu-system-x86_64 -cdrom build/SynOS.iso -m 2048
    # (manual observation required)

    # NEW
    ./scripts/testing/test-iso.sh build/SynOS.iso
    # (automated testing with results)
    ```

2. **Test Levels:**

    ```bash
    # Quick test (30 seconds)
    ./scripts/testing/test-iso.sh build/SynOS.iso --quick

    # Full test (2-3 minutes, comprehensive)
    ./scripts/testing/test-iso.sh build/SynOS.iso --full
    ```

3. **Test Modes:**

    ```bash
    # Headless (no GUI, for CI/CD)
    ./scripts/testing/test-iso.sh build/SynOS.iso --headless

    # With display (watch boot process)
    ./scripts/testing/test-iso.sh build/SynOS.iso --display
    ```

4. **Advanced Options:**

    ```bash
    # Generate JSON report
    ./scripts/testing/test-iso.sh build/SynOS.iso --report results.json

    # Capture screenshots
    ./scripts/testing/test-iso.sh build/SynOS.iso --screenshot screenshots/

    # Custom memory/timeout
    ./scripts/testing/test-iso.sh build/SynOS.iso --memory 4096 --timeout 120
    ```

#### Test Coverage

The new script validates:

-   ✓ ISO 9660 format structure
-   ✓ Kernel presence and location
-   ✓ GRUB bootloader configuration
-   ✓ Boot sequence (QEMU)
-   ✓ GRUB menu parsing
-   ✓ Kernel file integrity

---

### 4.2 Build Environment Verification

**Old:** Manual checks, scattered validation  
**New:** `scripts/testing/verify-build.sh`

#### Migration Steps

1. **Basic Verification:**

    ```bash
    # NEW: Check environment before building
    ./scripts/testing/verify-build.sh

    # Shows: ✓ 15+ checks passed
    ```

2. **Verification Modes:**

    ```bash
    # Minimal checks (essential only)
    ./scripts/testing/verify-build.sh --minimal

    # Full checks (including optional tools)
    ./scripts/testing/verify-build.sh --full
    ```

3. **Auto-Fix Issues:**

    ```bash
    # Attempt to fix issues automatically
    ./scripts/testing/verify-build.sh --fix

    # Will install missing tools, add targets, etc.
    ```

4. **Export Results:**

    ```bash
    # Generate JSON report
    ./scripts/testing/verify-build.sh --json verify-results.json
    ```

#### Checks Performed

-   ✓ User permissions (not root)
-   ✓ Rust toolchain (rustc, cargo)
-   ✓ Kernel target (x86_64-unknown-none)
-   ✓ Build tools (make, git, gcc)
-   ✓ ISO tools (grub-mkrescue, xorriso)
-   ✓ Disk space (5GB minimum)
-   ✓ Memory (2GB minimum)
-   ✓ Kernel source presence
-   ✓ Cargo dependencies
-   ✓ Git repository status
-   ✓ Environment variables

---

## 5. Maintenance Scripts

### 5.1 Build Cleanup

**Old:** Manual `rm -rf` commands, various cleanup scripts  
**New:** `scripts/maintenance/clean-builds.sh`

#### Migration Steps

1. **Safe Cleanup:**

    ```bash
    # OLD (dangerous)
    rm -rf build/workspace-*
    rm -rf build/*.iso

    # NEW (safe with confirmation)
    ./scripts/maintenance/clean-builds.sh --old --days 7
    ```

2. **Cleanup Modes:**

    ```bash
    # Clean old builds (>7 days)
    ./scripts/maintenance/clean-builds.sh --old --days 7

    # Clean large builds (>1GB)
    ./scripts/maintenance/clean-builds.sh --large --size 1000

    # Clean workspace cache
    ./scripts/maintenance/clean-builds.sh --workspace

    # Clean old ISOs (keeps most recent)
    ./scripts/maintenance/clean-builds.sh --isos --days 14

    # Clean logs and temp files
    ./scripts/maintenance/clean-builds.sh --logs --temp
    ```

3. **Dry Run:**

    ```bash
    # See what would be deleted without deleting
    ./scripts/maintenance/clean-builds.sh --dry-run --all
    ```

4. **Interactive Mode:**

    ```bash
    # Confirm each deletion
    ./scripts/maintenance/clean-builds.sh --interactive --old
    ```

#### Safety Features

-   ✓ Always preserves most recent ISO
-   ✓ Never deletes current workspace
-   ✓ Dry-run mode available
-   ✓ Interactive confirmations
-   ✓ Disk usage analysis

---

### 5.2 ISO Archiving

**Old:** Manual tar/gzip commands  
**New:** `scripts/maintenance/archive-old-isos.sh`

#### Migration Steps

1. **Archive Old ISOs:**

    ```bash
    # OLD
    tar -czf archive/SynOS-old.tar.gz build/*.iso
    rm build/*.iso

    # NEW (automatic with verification)
    ./scripts/maintenance/archive-old-isos.sh --archive --age 30
    ```

2. **Compression Options:**

    ```bash
    # Use gzip (fast)
    ./scripts/maintenance/archive-old-isos.sh --archive --compress gzip

    # Use xz (best compression)
    ./scripts/maintenance/archive-old-isos.sh --archive --compress xz --level 9

    # Use zstd (balanced)
    ./scripts/maintenance/archive-old-isos.sh --archive --compress zstd
    ```

3. **Keep Recent ISOs:**

    ```bash
    # Archive old, keep 3 most recent unarchived
    ./scripts/maintenance/archive-old-isos.sh --archive --keep 3
    ```

4. **List Archives:**

    ```bash
    # Show all archived ISOs
    ./scripts/maintenance/archive-old-isos.sh --list

    # With detailed info
    ./scripts/maintenance/archive-old-isos.sh --list --verbose
    ```

5. **Restore Archive:**

    ```bash
    # Restore specific ISO
    ./scripts/maintenance/archive-old-isos.sh --restore SynOS-v1.0.0.iso
    ```

#### Benefits

-   ✓ 30-50% space savings
-   ✓ Preserves checksums
-   ✓ Verification support
-   ✓ Easy restoration
-   ✓ Never deletes without archiving

---

## 6. Specialized Scripts

### 6.1 ISO Signing

**Old:** N/A (manual GPG commands)  
**New:** `scripts/utilities/sign-iso.sh`

#### New Capability - Getting Started

1. **Check for GPG Key:**

    ```bash
    ./scripts/utilities/sign-iso.sh --list-keys
    ```

2. **Create Key if Needed:**

    ```bash
    # Follow prompts to create GPG key
    gpg --gen-key
    ```

3. **Sign ISO:**

    ```bash
    # Sign with default key
    ./scripts/utilities/sign-iso.sh --sign build/SynOS-v1.0.0.iso

    # Creates: build/SynOS-v1.0.0.iso.sig
    ```

4. **Verify Signature:**

    ```bash
    ./scripts/utilities/sign-iso.sh --verify build/SynOS-v1.0.0.iso
    ```

5. **Batch Signing:**

    ```bash
    # Sign all ISOs in build/
    ./scripts/utilities/sign-iso.sh --batch build/*.iso
    ```

#### Use Cases

-   **Release Management:** Sign official releases
-   **Security:** Users can verify ISO authenticity
-   **Distribution:** Include .sig files with ISOs
-   **Compliance:** Meet security requirements

---

### 6.2 Docker Builds

**Old:** N/A (manual Docker setup)  
**New:** `scripts/docker/build-docker.sh`

#### New Capability - Getting Started

1. **Check Docker:**

    ```bash
    # Verify Docker is running
    docker ps
    ```

2. **Build in Docker:**

    ```bash
    # First build (creates image and builds ISO)
    ./scripts/docker/build-docker.sh --build

    # Subsequent builds (uses cached image)
    ./scripts/docker/build-docker.sh --build
    ```

3. **Debug in Container:**

    ```bash
    # Open interactive shell
    ./scripts/docker/build-docker.sh --shell

    # Inside container:
    ./scripts/build-iso.sh --quick
    exit
    ```

4. **Clean Docker Artifacts:**

    ```bash
    # Remove containers and images
    ./scripts/docker/build-docker.sh --clean
    ```

#### Benefits

-   **Reproducibility:** Same environment every time
-   **Isolation:** No system pollution
-   **CI/CD:** Perfect for automated builds
-   **Cross-platform:** Build for different architectures

---

## 7. Makefile Updates

### Current Makefile Integration

The new scripts are designed to work with existing Makefile targets. Update your Makefile:

```makefile
# Example Makefile updates

.PHONY: iso kernel test clean

# Build ISO with new script
iso:
	./scripts/build-iso.sh

# Build kernel-only ISO
kernel:
	./scripts/build-kernel-only.sh

# Test ISO
test: iso
	./scripts/testing/test-iso.sh build/SynOS-*.iso

# Verify environment
verify:
	./scripts/testing/verify-build.sh --full

# Clean builds
clean:
	./scripts/maintenance/clean-builds.sh --old --days 7 --force

# Full clean (interactive)
clean-all:
	./scripts/maintenance/clean-builds.sh --all

# Sign release
sign: iso
	./scripts/utilities/sign-iso.sh --sign build/SynOS-*.iso

# Docker build
docker-build:
	./scripts/docker/build-docker.sh --build
```

---

## 8. CI/CD Integration

### GitHub Actions Example

```yaml
name: Build SynOS ISO

on:
    push:
        branches: [master]
    pull_request:
        branches: [master]

jobs:
    build:
        runs-on: ubuntu-latest

        steps:
            - uses: actions/checkout@v3

            - name: Verify Build Environment
              run: |
                  ./scripts/testing/verify-build.sh --full --fix

            - name: Build ISO
              run: |
                  ./scripts/build-iso.sh --quick

            - name: Test ISO
              run: |
                  ./scripts/testing/test-iso.sh build/SynOS-*.iso --quick --headless

            - name: Sign ISO (if release)
              if: startsWith(github.ref, 'refs/tags/')
              run: |
                  ./scripts/utilities/sign-iso.sh --sign build/SynOS-*.iso

            - name: Upload Artifacts
              uses: actions/upload-artifact@v3
              with:
                  name: synos-iso
                  path: |
                      build/*.iso
                      build/*.sig
```

### GitLab CI Example

```yaml
build-iso:
    stage: build
    script:
        - ./scripts/testing/verify-build.sh --full --fix
        - ./scripts/build-iso.sh
        - ./scripts/testing/test-iso.sh build/SynOS-*.iso --headless
    artifacts:
        paths:
            - build/*.iso
            - build/*.sig
        expire_in: 1 week
```

### Docker-based CI

```yaml
build-iso-docker:
    stage: build
    script:
        - ./scripts/docker/build-docker.sh --build --no-cache
    artifacts:
        paths:
            - build/*.iso
```

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Issue 1: Script Not Found

**Symptom:**

```
bash: ./scripts/build-iso.sh: No such file or directory
```

**Solution:**

```bash
# Ensure you're in the project root
cd /path/to/Syn_OS

# Verify script exists
ls -l scripts/build-iso.sh

# Make executable if needed
chmod +x scripts/build-iso.sh
```

---

#### Issue 2: Permission Denied

**Symptom:**

```
bash: ./scripts/build-iso.sh: Permission denied
```

**Solution:**

```bash
# Make all new scripts executable
chmod +x scripts/*.sh
chmod +x scripts/lib/*.sh
chmod +x scripts/testing/*.sh
chmod +x scripts/maintenance/*.sh
chmod +x scripts/utilities/*.sh
chmod +x scripts/docker/*.sh
```

---

#### Issue 3: Build Common Library Not Found

**Symptom:**

```
./scripts/build-iso.sh: line 45: scripts/lib/build-common.sh: No such file or directory
```

**Solution:**

```bash
# Verify library exists
ls -l scripts/lib/build-common.sh

# If missing, the library wasn't created properly
# Check project documentation for setup steps
```

---

#### Issue 4: Rust Target Missing

**Symptom:**

```
error: Can't find crate for `core`
```

**Solution:**

```bash
# Add required target
rustup target add x86_64-unknown-none

# Or use auto-fix
./scripts/testing/verify-build.sh --fix
```

---

#### Issue 5: GRUB Tools Missing

**Symptom:**

```
✗ grub-mkrescue not found
```

**Solution:**

```bash
# Install GRUB tools
sudo apt install grub-pc-bin grub-efi-amd64-bin xorriso
```

---

#### Issue 6: Build Fails Silently

**Symptom:**

```
Build appears to run but no ISO created
```

**Solution:**

```bash
# Check logs
ls -l build/logs/

# View latest log
tail -100 build/logs/build-*.log

# Run with verbose output
./scripts/build-iso.sh --verbose
```

---

#### Issue 7: ISO Won't Boot in QEMU

**Symptom:**

```
QEMU starts but ISO doesn't boot
```

**Solution:**

```bash
# Verify ISO structure
./scripts/testing/test-iso.sh build/SynOS-*.iso --quick

# Check for common issues:
# - Kernel not found
# - GRUB config missing
# - Incorrect file permissions
```

---

#### Issue 8: Docker Permission Issues

**Symptom:**

```
permission denied while trying to connect to Docker daemon
```

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Or run with sudo (not recommended for regular use)
sudo ./scripts/docker/build-docker.sh --build
```

---

### Getting Help

If you encounter issues not covered here:

1. **Check Documentation:**

    ```bash
    # Script-specific help
    ./scripts/build-iso.sh --help

    # Environment verification
    ./scripts/testing/verify-build.sh --full --verbose
    ```

2. **Review Logs:**

    ```bash
    # Latest build log
    tail -100 build/logs/build-*.log
    ```

3. **Report Issues:**
    - GitHub Issues: `https://github.com/TLimoges33/Syn_OS/issues`
    - Include: script name, error message, environment details

---

## 10. Rollback Plan

If you encounter critical issues with the new scripts, you can temporarily rollback:

### Temporary Rollback (Grace Period Only)

During the grace period (Nov 1-30), legacy scripts remain available:

```bash
# Use legacy builder temporarily
./scripts/unified-iso-builder.sh

# Note: You'll see deprecation warnings
```

### Access Archived Scripts (After Dec 1)

After the migration deadline, legacy scripts are archived but still accessible:

```bash
# Access archived script
./archive/build-scripts-deprecated/unified-iso-builder.sh

# Or use compatibility symlink (if created)
./scripts/legacy-iso-builder.sh  # symlinks to archived version
```

### Full Rollback (Emergency Only)

If you need to completely rollback:

```bash
# 1. Restore from backup
tar -xzf ~/synos-scripts-backup-YYYYMMDD.tar.gz

# 2. Report the issue
# Please report critical issues so we can address them

# 3. Document the problem
echo "Rollback reason: [describe issue]" > rollback-reason.txt
```

**Note:** Full rollback should only be used in emergencies. Please report issues so we can improve the new scripts.

---

## 📊 Migration Checklist

Use this checklist to track your migration progress:

### Phase A: Evaluation (Week 1)

-   [ ] Read migration guide completely
-   [ ] Run environment verification
-   [ ] Backup current build directory
-   [ ] Test new build-iso.sh script
-   [ ] Test new build-kernel-only.sh script
-   [ ] Compare ISO outputs with old builds
-   [ ] Run ISO test suite
-   [ ] Verify all features work as expected

### Phase B: Transition (Weeks 2-4)

-   [ ] Update local scripts to use new builders
-   [ ] Update Makefile targets
-   [ ] Update documentation/README
-   [ ] Train team members (if applicable)
-   [ ] Update CI/CD pipelines
-   [ ] Test new maintenance scripts
-   [ ] Test ISO signing workflow
-   [ ] Test Docker build workflow

### Phase C: Completion (Week 5+)

-   [ ] Verify no references to old scripts
-   [ ] Confirm CI/CD uses new scripts
-   [ ] Remove old script shortcuts/aliases
-   [ ] Update any external documentation
-   [ ] Archive old scripts (automatic on Dec 1)
-   [ ] Celebrate successful migration! 🎉

---

## 🎯 Quick Reference Card

Print or save this quick reference:

```
╔═══════════════════════════════════════════════════════════════╗
║           SynOS Build Scripts Quick Reference                 ║
╠═══════════════════════════════════════════════════════════════╣
║ BUILD                                                         ║
║   ISO:            ./scripts/build-iso.sh                      ║
║   Kernel:         ./scripts/build-kernel-only.sh             ║
║   Full Linux:     ./scripts/build-full-linux.sh              ║
║   Docker:         ./scripts/docker/build-docker.sh --build   ║
╠═══════════════════════════════════════════════════════════════╣
║ TEST                                                          ║
║   Environment:    ./scripts/testing/verify-build.sh          ║
║   ISO:            ./scripts/testing/test-iso.sh <iso>        ║
╠═══════════════════════════════════════════════════════════════╣
║ MAINTAIN                                                      ║
║   Cleanup:        ./scripts/maintenance/clean-builds.sh      ║
║   Archive:        ./scripts/maintenance/archive-old-isos.sh  ║
╠═══════════════════════════════════════════════════════════════╣
║ RELEASE                                                       ║
║   Sign:           ./scripts/utilities/sign-iso.sh --sign     ║
║   Verify:         ./scripts/utilities/sign-iso.sh --verify   ║
╠═══════════════════════════════════════════════════════════════╣
║ HELP                                                          ║
║   Any script:     <script> --help                            ║
║   This guide:     docs/BUILD_SCRIPTS_MIGRATION_GUIDE.md      ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📞 Support

-   **Documentation:** `docs/` directory
-   **Phase Summaries:** `docs/PHASE*_COMPLETION_SUMMARY.md`
-   **Issues:** Report on GitHub
-   **Questions:** See CONTRIBUTING.md for communication channels

---

**Last Updated:** October 23, 2025  
**Version:** 2.0  
**Next Review:** November 30, 2025

---

_This migration guide will be updated based on user feedback during the grace period._
