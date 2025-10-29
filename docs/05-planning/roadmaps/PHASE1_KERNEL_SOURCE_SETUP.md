# Phase 1: Linux Kernel Source Setup

**Start Date:** October 28, 2025
**Duration:** Weeks 1-2 (Target: November 8, 2025)
**Status:** 🔄 IN PROGRESS
**Effort:** 40-60 hours

---

## 🎯 PHASE 1 OBJECTIVES

**Goal:** Set up Linux kernel development environment and build first custom kernel .deb package (unmodified, to establish baseline).

**Success Criteria:**
- [ ] Kernel source downloaded and extracted
- [ ] Build dependencies installed
- [ ] Kernel configured with ParrotOS defaults
- [ ] Successful kernel compilation
- [ ] Custom .deb package created
- [ ] Kernel boots successfully in test VM
- [ ] Build process fully documented

---

## 📊 CURRENT ENVIRONMENT

**Host System:**
- **OS:** ParrotOS 6.4 (lorikeet) - Debian-based
- **Current Kernel:** 6.12.32-amd64 (linux-image-6.12.32-amd64)
- **Architecture:** x86_64 (amd64)
- **Available Sources:** linux-source-6.12 (Debian patches included)

**Existing Kernel Headers:**
- `/usr/src/linux-headers-6.12.32-amd64/` ✅
- `/usr/src/linux-headers-6.12.32-common/` ✅

---

## 📋 PHASE 1 TASKS

### Task 1: Install Kernel Build Dependencies (Day 1)

**Required Packages:**
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    bc \
    bison \
    flex \
    libssl-dev \
    libelf-dev \
    libncurses-dev \
    dwarves \
    rsync \
    git \
    fakeroot \
    debhelper \
    linux-source-6.12
```

**Purpose of Each:**
- `build-essential` - GCC, make, and essential build tools
- `bc` - Basic calculator for kernel build scripts
- `bison` - Parser generator
- `flex` - Lexical analyzer
- `libssl-dev` - SSL library (for kernel crypto)
- `libelf-dev` - ELF library (for BPF and kernel modules)
- `libncurses-dev` - Terminal UI library (for menuconfig)
- `dwarves` - DWARF utilities (for BTF generation)
- `rsync` - File synchronization
- `git` - Version control
- `fakeroot` - Fake root privileges for packaging
- `debhelper` - Debian packaging tools (for bindeb-pkg)
- `linux-source-6.12` - Actual kernel source code

**Verification:**
```bash
dpkg -l | grep -E "build-essential|bc|libssl-dev|libelf-dev"
```

**Estimated Time:** 30-60 minutes (depending on download speed)

---

### Task 2: Extract Kernel Source (Day 1)

**Download Location:**
```bash
# linux-source package installs to:
ls /usr/src/linux-source-6.12.tar.xz
```

**Extract:**
```bash
cd /usr/src
sudo tar -xf linux-source-6.12.tar.xz
cd linux-source-6.12
```

**Verify Extraction:**
```bash
ls -la /usr/src/linux-source-6.12/
# Should show: arch/, drivers/, kernel/, Makefile, etc.
```

**Size:** ~1.2 GB extracted

**Estimated Time:** 10-15 minutes

---

### Task 3: Configure Kernel Build (Day 2)

**Copy Current Kernel Config:**
```bash
cd /usr/src/linux-source-6.12
sudo cp /boot/config-6.12.32-amd64 .config
```

**Why:** Start with working ParrotOS configuration to ensure compatibility.

**Adjust Config for Custom Build:**
```bash
# Set custom kernel version string
sudo make menuconfig
# Navigate to: General setup -> Local version
# Set to: "-synos-ai-v0.1"
# Save and exit
```

**Alternative (Non-Interactive):**
```bash
# Use oldconfig to accept defaults
sudo make oldconfig
```

**Set Custom Version:**
```bash
# Edit .config file
sudo sed -i 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-synos-ai-v0.1"/' .config
```

**Verify Configuration:**
```bash
grep "CONFIG_LOCALVERSION" .config
# Should show: CONFIG_LOCALVERSION="-synos-ai-v0.1"
```

**Estimated Time:** 30-60 minutes

---

### Task 4: Compile Kernel (Day 3-4)

**Set Build Parameters:**
```bash
# Use all CPU cores for faster build
export MAKEFLAGS="-j$(nproc)"

# Optional: Set architecture explicitly
export ARCH=x86_64
```

**Build Kernel:**
```bash
cd /usr/src/linux-source-6.12

# Clean any previous builds
sudo make mrproper

# Restore config
sudo cp /boot/config-6.12.32-amd64 .config
sudo make oldconfig

# Build kernel image, modules, and device tree blobs
sudo make -j$(nproc) bzImage modules
```

**Build Time Estimate:**
- **With 8 cores:** 30-60 minutes
- **With 4 cores:** 60-120 minutes
- **With 2 cores:** 2-4 hours

**Monitor Progress:**
```bash
# In another terminal:
watch -n 5 'tail -20 /proc/cpuinfo | grep MHz'
```

**Expected Output:**
```
  CC      init/main.o
  CC      init/version.o
  LD      init/built-in.o
  ...
  Kernel: arch/x86/boot/bzImage is ready  (#1)
```

**Verify Build:**
```bash
ls -lh arch/x86/boot/bzImage
# Should be ~8-12 MB

ls -lh vmlinux
# Should be ~500-800 MB (uncompressed)
```

**Estimated Time:** 1-4 hours (depending on CPU)

---

### Task 5: Install Kernel Modules (Day 4)

**Install Modules:**
```bash
cd /usr/src/linux-source-6.12
sudo make modules_install
```

**What This Does:**
- Installs modules to `/lib/modules/6.12.32-synos-ai-v0.1/`
- Creates `modules.dep` and other module metadata

**Verify Installation:**
```bash
ls -la /lib/modules/6.12.32-synos-ai-v0.1/
# Should show: kernel/, modules.*, build -> /usr/src/...
```

**Estimated Time:** 10-20 minutes

---

### Task 6: Create Debian Package (Day 5)

**Build .deb Packages:**
```bash
cd /usr/src/linux-source-6.12

# Create debian packages (image, headers, libc-dev)
sudo make bindeb-pkg -j$(nproc)
```

**What Gets Created:**
```
/usr/src/
├── linux-image-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb       (~50-100 MB)
├── linux-headers-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb     (~10-20 MB)
├── linux-libc-dev_6.12.32-1_amd64.deb                          (~1-2 MB)
└── linux-image-6.12.32-synos-ai-v0.1-dbg_6.12.32-1_amd64.deb   (~500+ MB, debug symbols)
```

**Verify Packages:**
```bash
ls -lh /usr/src/*.deb
```

**Estimated Time:** 20-40 minutes

---

### Task 7: Test Kernel in VM (Day 6)

**Install Kernel in Test VM:**
```bash
# Copy .deb to test VM
scp /usr/src/linux-image-*.deb testvm:~/

# On test VM:
sudo dpkg -i ~/linux-image-6.12.32-synos-ai-v0.1_*.deb
sudo update-grub
sudo reboot
```

**Verify Boot:**
```bash
# After reboot:
uname -r
# Should show: 6.12.32-synos-ai-v0.1
```

**Test Basic Functionality:**
```bash
# Check kernel loaded correctly
dmesg | head -50

# Check modules
lsmod | head -10

# Check networking
ip addr
ping -c 3 8.8.8.8

# Check filesystems
df -h
```

**Rollback Plan:**
If kernel doesn't boot:
1. Boot into GRUB menu
2. Select "Advanced options"
3. Choose previous working kernel (6.12.32-amd64)
4. Debug build issues

**Estimated Time:** 1-2 hours (setup VM + testing)

---

### Task 8: Document Build Process (Day 7)

**Create Documentation:**

1. **Build Log:**
```bash
# Save complete build output
cd /usr/src/linux-source-6.12
script -c "sudo make -j$(nproc) bzImage modules" ~/synos-kernel-build.log
```

2. **Configuration File:**
```bash
# Archive the working .config
cp .config ~/synos-kernel-6.12.32-base.config
```

3. **Build Script:**
Create reusable build script at `/home/diablorain/Syn_OS/scripts/kernel/build-synos-kernel.sh`

4. **Documentation:**
Create `/home/diablorain/Syn_OS/docs/04-development/KERNEL_BUILD_GUIDE.md`

**Estimated Time:** 2-4 hours

---

## 📊 PHASE 1 TIMELINE

| Day | Task | Duration | Cumulative |
|-----|------|----------|------------|
| 1 | Install dependencies + Extract source | 2-3 hours | 2-3 hours |
| 2 | Configure kernel | 1-2 hours | 3-5 hours |
| 3-4 | Compile kernel + modules | 2-6 hours | 5-11 hours |
| 5 | Create .deb packages | 1-2 hours | 6-13 hours |
| 6 | Test in VM | 2-3 hours | 8-16 hours |
| 7 | Documentation | 3-4 hours | 11-20 hours |

**Total Phase 1 Effort:** 11-20 hours (can extend to 40-60 hours with thorough testing)

---

## ✅ SUCCESS CRITERIA

### Must Have (Blockers for Phase 2)
- [x] Build dependencies installed
- [ ] Kernel source extracted and ready
- [ ] Kernel compiles without errors
- [ ] .deb package created successfully
- [ ] Kernel boots in test VM
- [ ] Basic functionality verified (network, filesystem, modules)

### Nice to Have (Can defer)
- [ ] Automated build script created
- [ ] Build time optimized
- [ ] Debug symbols package tested
- [ ] Multiple kernel configs tested

---

## 🚧 POTENTIAL ISSUES & SOLUTIONS

### Issue 1: Build Fails with Missing Dependencies
**Solution:**
```bash
# Install all possible dependencies
sudo apt build-dep linux
```

### Issue 2: Out of Disk Space
**Symptoms:** Build fails with "No space left on device"
**Solution:**
```bash
# Check disk space
df -h /usr/src

# Clean up if needed
sudo apt clean
sudo rm -rf /usr/src/linux-source-6.12/debian/tmp
```

**Requirement:** 20-30 GB free space for kernel build

### Issue 3: Compilation Errors
**Common Causes:**
- Missing headers
- Wrong compiler version
- Corrupted source

**Solution:**
```bash
# Clean and retry
cd /usr/src/linux-source-6.12
sudo make mrproper
sudo cp /boot/config-6.12.32-amd64 .config
sudo make oldconfig
sudo make -j$(nproc) bzImage modules
```

### Issue 4: Kernel Doesn't Boot
**Symptoms:** VM hangs or kernel panic
**Solution:**
1. Boot into old kernel from GRUB
2. Check build logs for errors
3. Verify .config matches working kernel
4. Try building with `make olddefconfig` instead

---

## 📁 FILES & DIRECTORIES

### Source Locations
- **Kernel Source:** `/usr/src/linux-source-6.12/`
- **Build Output:** `/usr/src/linux-source-6.12/arch/x86/boot/bzImage`
- **Modules:** `/lib/modules/6.12.32-synos-ai-v0.1/`
- **Packages:** `/usr/src/*.deb`

### Configuration Files
- **Current Kernel Config:** `/boot/config-6.12.32-amd64`
- **Custom Config:** `/usr/src/linux-source-6.12/.config`
- **Backup Config:** `~/synos-kernel-6.12.32-base.config`

### Documentation
- **This File:** `/docs/05-planning/roadmaps/PHASE1_KERNEL_SOURCE_SETUP.md`
- **Build Guide:** `/docs/04-development/KERNEL_BUILD_GUIDE.md` (to be created)
- **Build Log:** `~/synos-kernel-build.log`

---

## 🔄 NEXT PHASE

After Phase 1 completion, proceed to:
**Phase 2: AI-Aware System Calls (Weeks 3-6)**
- Design 5 new syscalls for AI integration
- Implement syscall handlers
- Create userspace test programs
- Document syscall API

**Prerequisites from Phase 1:**
- Working kernel build environment ✅
- Ability to modify kernel source ✅
- Testing/verification process ✅
- Documentation workflow ✅

---

## 📝 NOTES

### Version Naming Convention
- **Base Version:** 6.12.32 (matches ParrotOS)
- **Custom Suffix:** -synos-ai-v0.1
- **Full Version:** 6.12.32-synos-ai-v0.1

**Future Versions:**
- v0.1 - Base kernel (no modifications)
- v0.2 - AI syscalls added (Phase 2)
- v0.3 - eBPF telemetry (Phase 3)
- v0.4 - Consciousness scheduler (Phase 4)
- v1.0 - Full AI integration (Phase 6)

### Build Environment
- **Recommended:** Dedicated build machine with 8+ GB RAM, 4+ cores
- **Minimum:** 4 GB RAM, 2 cores (slower but works)
- **Storage:** 30+ GB free space

### Parallel Builds
```bash
# Check CPU cores
nproc
# Use: make -j$(nproc) for maximum speed
```

---

**Phase 1 Start:** October 28, 2025
**Phase 1 Target Completion:** November 8, 2025 (2 weeks)
**Status:** Ready to begin
**First Task:** Install kernel build dependencies

---

**Let's build the foundation for SynOS AI kernel!** 🚀
