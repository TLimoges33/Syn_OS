# 🚀 SynOS Build Scripts - Quick Reference

## Phase 2 Complete - Three Ways to Build

**Status:** ✅ Production Ready  
**Date:** October 23, 2025  
**Progress:** 40% Complete (4 of 10 scripts)

---

## 📋 Which Script Should I Use?

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DECISION TREE                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Need full ISO with all features?                                  │
│  └─ YES → ./scripts/build-iso.sh                                   │
│                                                                     │
│  Just testing kernel changes quickly?                              │
│  └─ YES → ./scripts/build-kernel-only.sh                           │
│                                                                     │
│  Want complete Linux distribution?                                 │
│  └─ YES → ./scripts/build-full-linux.sh                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ build-iso.sh - Primary ISO Builder

**Use when:** You want a standard SynOS bootable ISO

**Features:**

-   ✅ Kernel + workspace binaries
-   ✅ Documentation included
-   ✅ Optional source archive
-   ✅ Checksums (MD5, SHA256)
-   ✅ Multiple boot modes (GRUB)

**Quick Commands:**

```bash
# Standard build (everything)
./scripts/build-iso.sh

# Quick build (skip workspace)
./scripts/build-iso.sh --quick

# Minimal kernel-only
./scripts/build-iso.sh --kernel-only

# No source code archive
./scripts/build-iso.sh --no-source

# Custom output directory
./scripts/build-iso.sh --output /path/to/output

# Get help
./scripts/build-iso.sh --help
```

**Build Time:** 10-15 minutes  
**ISO Size:** 1-2 GB  
**Output:** `build/SynOS-v1.0.0-Complete-TIMESTAMP.iso`

---

## 2️⃣ build-kernel-only.sh - Fast Test Builder

**Use when:** Rapid kernel development/testing

**Features:**

-   ⚡ Fastest builds (2-5 minutes)
-   🔬 Kernel testing focused
-   🎯 Minimal ISO (~50 MB)
-   🧪 QEMU integration
-   🐛 Debug mode available

**Quick Commands:**

```bash
# Quick kernel test
./scripts/build-kernel-only.sh

# Build and auto-test in QEMU
./scripts/build-kernel-only.sh --test-qemu

# Debug build
./scripts/build-kernel-only.sh --debug

# Different target architecture
./scripts/build-kernel-only.sh --target aarch64-unknown-none

# Get help
./scripts/build-kernel-only.sh --help
```

**Build Time:** 2-5 minutes  
**ISO Size:** ~50 MB  
**Output:** `build/SynOS-v1.0.0-KernelTest-TIMESTAMP.iso`

**Perfect for:**

-   Kernel boot testing
-   GRUB configuration testing
-   Quick iteration cycles
-   CI/CD pipelines

---

## 3️⃣ build-full-linux.sh - Complete Distribution

**Use when:** Building full Linux distribution with SynOS

**Features:**

-   🐧 Debian or Ubuntu base
-   📦 Three variants (minimal/standard/full)
-   👤 User accounts configured
-   🌐 Network ready
-   💿 Live system + installer
-   🎨 Desktop environment (full variant)

**Quick Commands:**

```bash
# Standard Debian distribution
./scripts/build-full-linux.sh

# Ubuntu base with full packages
./scripts/build-full-linux.sh --base-distro ubuntu --variant full

# Minimal Debian (smallest)
./scripts/build-full-linux.sh --variant minimal

# Skip package install (reuse chroot)
./scripts/build-full-linux.sh --skip-packages

# Custom hostname
SYNOS_HOSTNAME=mysynos ./scripts/build-full-linux.sh

# Get help
./scripts/build-full-linux.sh --help
```

**Build Time:** 20-40 minutes (first build)  
**ISO Size:** 2-4 GB  
**Output:** `build/SynOS-v1.0.0-Debian-Standard-TIMESTAMP.iso`

**Variants:**

-   `minimal`: Base system + essentials (systemd, sudo)
-   `standard`: + network tools, vim, curl, wget (default)
-   `full`: + dev tools, python, nodejs, git

**Login Credentials:**

-   User: `synos` / Password: `synos`
-   Root: `root` / Password: `root`

---

## 🎯 Common Use Cases

### Daily Development

```bash
# 1. Make kernel changes
vim src/kernel/...

# 2. Quick test
./scripts/build-kernel-only.sh --test-qemu

# 3. Iterate until working
# ... repeat ...

# 4. Final test with full build
./scripts/build-iso.sh
```

### Release Build

```bash
# Complete release ISO with everything
./scripts/build-iso.sh

# Generate full Linux distribution
./scripts/build-full-linux.sh --variant full
```

### CI/CD Pipeline

```bash
# Fast validation
./scripts/build-kernel-only.sh

# If passes, full build
./scripts/build-iso.sh --no-source
```

---

## 🛠️ Environment Variables

All scripts support:

```bash
# Version override
SYNOS_VERSION=2.0.0 ./scripts/build-iso.sh

# Build type
BUILD_TYPE=debug ./scripts/build-kernel-only.sh

# Kernel target
KERNEL_TARGET=aarch64-unknown-none ./scripts/build-kernel-only.sh

# Full Linux specific
SYNOS_HOSTNAME=custom ./scripts/build-full-linux.sh
DEBIAN_MIRROR=http://mirror.local/debian ./scripts/build-full-linux.sh
```

---

## 📦 Output Files

### Standard ISO (build-iso.sh)

```
build/
├── SynOS-v1.0.0-Complete-20251023-123456.iso
├── SynOS-v1.0.0-Complete-20251023-123456.iso.md5
└── SynOS-v1.0.0-Complete-20251023-123456.iso.sha256
```

### Kernel-Only ISO (build-kernel-only.sh)

```
build/
└── SynOS-v1.0.0-KernelTest-20251023-123456.iso
```

### Full Linux ISO (build-full-linux.sh)

```
build/
├── SynOS-v1.0.0-Debian-Standard-20251023-123456.iso
├── SynOS-v1.0.0-Debian-Standard-20251023-123456.iso.md5
├── SynOS-v1.0.0-Debian-Standard-20251023-123456.iso.sha256
└── chroot-debian/  (reusable base system)
```

---

## 🧪 Testing Your ISO

### QEMU (Recommended)

```bash
# Basic test (2GB RAM)
qemu-system-x86_64 -cdrom build/SynOS-*.iso -m 2G

# With KVM acceleration
qemu-system-x86_64 -cdrom build/SynOS-*.iso -m 2G -enable-kvm

# Full Linux needs more RAM
qemu-system-x86_64 -cdrom build/SynOS-*-Debian-*.iso -m 4G -enable-kvm
```

### VirtualBox

```bash
# Create VM
VBoxManage createvm --name "SynOS Test" --register
VBoxManage modifyvm "SynOS Test" --memory 2048 --cpus 2
VBoxManage storagectl "SynOS Test" --name "IDE" --add ide
VBoxManage storageattach "SynOS Test" --storagectl "IDE" \
  --port 0 --device 0 --type dvddrive --medium build/SynOS-*.iso
VBoxManage startvm "SynOS Test"
```

### Physical Hardware

```bash
# Write to USB (⚠️ DANGER: Verify /dev/sdX is correct!)
sudo dd if=build/SynOS-*.iso of=/dev/sdX bs=4M status=progress
sudo sync

# Verify checksum
md5sum -c build/SynOS-*.iso.md5
```

---

## ❌ Troubleshooting

### Build Fails - Missing Dependencies

```bash
# Install required tools
sudo apt install cargo rustc grub-mkrescue xorriso git

# For full Linux builder, also need:
sudo apt install debootstrap squashfs-tools genisoimage
```

### Build Fails - Disk Space

```bash
# Check available space
df -h build/

# Minimum requirements:
# - build-kernel-only.sh: 500 MB
# - build-iso.sh:        5 GB
# - build-full-linux.sh: 10 GB

# Clean old builds
rm -rf build/workspace-*
rm -f build/*.iso.old
```

### Build Fails - Rust Target Missing

```bash
# Install kernel target
rustup target add x86_64-unknown-none

# Verify installed
rustup target list --installed
```

### ISO Won't Boot

```bash
# Verify ISO integrity
verify_iso() {
    iso="$1"
    echo "Checking ISO structure..."
    isoinfo -d -i "$iso"
    echo "Checking for kernel..."
    isoinfo -l -i "$iso" | grep kernel
    echo "Checking for GRUB..."
    isoinfo -l -i "$iso" | grep grub
}

verify_iso build/SynOS-*.iso
```

---

## 📚 More Information

-   **Full Documentation:** `docs/PHASE2_COMPLETION_SUMMARY.md`
-   **Consolidation Plan:** `docs/BUILD_SCRIPT_CONSOLIDATION_PLAN.md`
-   **Progress Tracking:** `docs/SCRIPT_CONSOLIDATION_PROGRESS.md`
-   **Build Audit:** `docs/ISO_BUILD_READINESS_AUDIT_2025-10-23.md`

---

## 🎉 Quick Status

```
✅ Phase 1: Shared library (build-common.sh) - COMPLETE
✅ Phase 2: Core builders (3 scripts) - COMPLETE
📋 Phase 3: Testing tools - NEXT
📋 Phase 4: Maintenance tools - PLANNED
📋 Phase 5: Specialized tools - PLANNED
📋 Phase 6: Migration & cleanup - PLANNED

Overall Progress: 40% (4 of 10 scripts)
```

---

**Last Updated:** October 23, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
