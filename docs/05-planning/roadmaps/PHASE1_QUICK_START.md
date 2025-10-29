# Phase 1 Quick Start Guide

**Start Date:** October 28, 2025
**Your Mission:** Build your first custom SynOS AI kernel (unmodified baseline)

---

## 🚀 QUICK START - Day 1

### Step 1: Install Dependencies (5 minutes + 20 minutes download)

```bash
cd /home/diablorain/Syn_OS
sudo ./scripts/kernel/install-kernel-dependencies.sh
```

**What this does:**
- Installs GCC, make, and kernel build tools
- Downloads 1.2 GB kernel source
- Verifies all dependencies installed correctly

---

### Step 2: Extract Kernel Source (10 minutes)

```bash
cd /usr/src
sudo tar -xf linux-source-6.12.tar.xz
cd linux-source-6.12
ls -la
```

**You should see:**
```
arch/          - Architecture-specific code
drivers/       - Device drivers
kernel/        - Core kernel
Makefile       - Build instructions
README         - Kernel documentation
```

---

### Step 3: Copy Working Configuration (1 minute)

```bash
cd /usr/src/linux-source-6.12
sudo cp /boot/config-6.12.32-amd64 .config
```

**Why:** Start with ParrotOS's proven configuration

---

### Step 4: Set Custom Version String (2 minutes)

```bash
# Add custom version suffix
sudo sed -i 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-synos-ai-v0.1"/' .config

# Verify
grep CONFIG_LOCALVERSION .config
```

**Expected output:**
```
CONFIG_LOCALVERSION="-synos-ai-v0.1"
```

---

## 🔨 BUILD - Day 2-3

### Step 5: Compile Kernel (30-120 minutes depending on CPU)

```bash
cd /usr/src/linux-source-6.12

# Clean any previous builds
sudo make mrproper

# Restore config
sudo cp /boot/config-6.12.32-amd64 .config
sudo sed -i 's/CONFIG_LOCALVERSION=""/CONFIG_LOCALVERSION="-synos-ai-v0.1"/' .config

# Build with all CPU cores
sudo make -j$(nproc) bzImage modules

# Install modules
sudo make modules_install
```

**Monitor progress in another terminal:**
```bash
watch -n 5 'ps aux | grep make | head -3'
```

**Expected end result:**
```
Kernel: arch/x86/boot/bzImage is ready  (#1)
```

---

### Step 6: Create Debian Package (20-40 minutes)

```bash
cd /usr/src/linux-source-6.12
sudo make bindeb-pkg -j$(nproc)
```

**Output packages (in /usr/src/):**
```
linux-image-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb       (~50-100 MB)
linux-headers-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb     (~10-20 MB)
linux-libc-dev_6.12.32-1_amd64.deb                          (~1-2 MB)
```

**Verify:**
```bash
ls -lh /usr/src/*.deb | grep synos-ai
```

---

## ✅ VERIFICATION - Day 3

### Step 7: Test Kernel (Optional but Recommended)

**Option A: Test in QEMU (Quick)**
```bash
# Install kernel locally (will appear in GRUB menu)
sudo dpkg -i /usr/src/linux-image-6.12.32-synos-ai-v0.1_*.deb
sudo update-grub

# Reboot and select new kernel from GRUB menu
sudo reboot
```

**After reboot, verify:**
```bash
uname -r
# Should show: 6.12.32-synos-ai-v0.1
```

**Test basic functionality:**
```bash
# Check kernel booted correctly
dmesg | head -20

# Check modules loaded
lsmod | head -10

# Check network works
ping -c 3 8.8.8.8

# Check filesystem works
df -h
```

**Success criteria:**
- [x] uname shows 6.12.32-synos-ai-v0.1
- [x] No kernel panics in dmesg
- [x] Network functional
- [x] Filesystem accessible

---

## 🎉 SUCCESS!

You now have:
- ✅ Custom SynOS AI kernel compiled
- ✅ Bootable .deb package created
- ✅ Kernel tested and verified

**Your kernel:**
- **Version:** 6.12.32-synos-ai-v0.1
- **Size:** ~50-100 MB (.deb package)
- **Location:** /usr/src/linux-image-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb
- **Source:** /usr/src/linux-source-6.12/
- **Modules:** /lib/modules/6.12.32-synos-ai-v0.1/

---

## 🚧 TROUBLESHOOTING

### Build fails with "missing dependencies"
```bash
sudo apt build-dep linux
sudo apt install -y libssl-dev libelf-dev
```

### Out of disk space
```bash
# Check space
df -h /usr/src

# Clean if needed
sudo apt clean
rm -rf ~/.cache/*
```

**Need:** 20-30 GB free space

### Compilation errors
```bash
# Check build log
cd /usr/src/linux-source-6.12
# Look for first ERROR: line

# Try clean rebuild
sudo make mrproper
sudo cp /boot/config-6.12.32-amd64 .config
sudo make oldconfig
sudo make -j$(nproc) bzImage modules
```

### Kernel doesn't boot
1. Reboot into GRUB menu
2. Select "Advanced options"
3. Choose previous kernel (6.12.32-amd64)
4. Check build logs for errors
5. Retry build

---

## 📊 TIME ESTIMATE

| Task | Duration | Cumulative |
|------|----------|------------|
| Install deps | 25 min | 25 min |
| Extract source | 10 min | 35 min |
| Configure | 3 min | 38 min |
| Compile | 30-120 min | 68-158 min |
| Create .deb | 20-40 min | 88-198 min |
| Test | 30 min | 118-228 min |

**Total:** 2-4 hours for Phase 1

---

## 🔄 NEXT PHASE

**Phase 2: AI-Aware System Calls** (Weeks 3-6)

After completing Phase 1, you'll:
1. Add 5 new syscalls for AI integration
2. Modify kernel source code
3. Test AI communication with kernel
4. Document syscall API

**Phase 1 establishes:**
- ✅ Kernel build environment
- ✅ Ability to modify and rebuild kernel
- ✅ Testing/verification workflow
- ✅ Packaging process

---

## 📚 DOCUMENTATION

**Full Details:** `/docs/05-planning/roadmaps/PHASE1_KERNEL_SOURCE_SETUP.md`

**Build Guide:** Coming in Phase 1 Task 8

**AI Kernel Roadmap:** `/docs/05-planning/roadmaps/AI_LINUX_KERNEL_IMPLEMENTATION_ROADMAP.md`

---

**Phase 1 Status:** Ready to begin!
**First Command:** `sudo ./scripts/kernel/install-kernel-dependencies.sh`
**Duration:** 2-4 hours total
**Let's build the foundation!** 🚀
