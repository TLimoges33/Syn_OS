# SynOS v1.0 - ParrotOS Remaster Build Guide

## 🎯 Overview

This build method takes **ParrotOS Security Edition** as the base and transforms it into **SynOS** by:

✅ **Replacing the kernel** with our custom Rust kernel  
✅ **Injecting all SynOS proprietary components** (ALFRED, Consciousness Framework, AI Daemon)  
✅ **Complete rebranding** - boot screen, wallpapers, themes, names  
✅ **Keeping all ParrotOS security tools** (600+ tools)  
✅ **Adding our custom DEBs**

**Result:** A pure SynOS experience built on a proven security foundation.

---

## 📋 Prerequisites

### System Requirements

-   **OS:** Debian/Ubuntu/ParrotOS
-   **RAM:** 8GB minimum (16GB recommended)
-   **Disk Space:** 30GB free
-   **Root Access:** Required

### Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    squashfs-tools \
    xorriso \
    genisoimage \
    rsync \
    isolinux \
    syslinux-utils
```

---

## 📥 Step 1: Download ParrotOS Base ISO

### Option A: Official ParrotOS (Recommended)

```bash
# Create working directory
mkdir -p ~/Syn_OS/build/parrot-remaster
cd ~/Syn_OS/build/parrot-remaster

# Download ParrotOS Security Edition (5.3GB)
wget https://download.parrot.sh/parrot/iso/5.3/Parrot-security-5.3_amd64.iso

# Verify checksum
wget https://download.parrot.sh/parrot/iso/5.3/Parrot-security-5.3_amd64.iso.sha256
sha256sum -c Parrot-security-5.3_amd64.iso.sha256
```

### Option B: Torrent Download (Faster)

```bash
# Download via torrent
transmission-cli https://download.parrot.sh/parrot/iso/5.3/Parrot-security-5.3_amd64.iso.torrent
```

---

## 🔧 Step 2: Verify SynOS Components

Ensure all our custom work is compiled and ready:

```bash
cd ~/Syn_OS

# Check Rust kernel
ls -lh core/kernel/target/x86_64-unknown-none/release/synos_kernel

# Check ALFRED
ls -lh core/ai/alfred/target/release/alfred

# Check DEBs
ls -lh linux-distribution/SynOS-Packages/*.deb

# Check Consciousness Framework
ls -lh src/consciousness-framework/

# Check AI Daemon
ls -lh src/ai-engine/ai-daemon.py
```

If anything is missing, build it first:

```bash
# Build Rust kernel
cd core/kernel
cargo build --release --target x86_64-unknown-none

# Build ALFRED
cd ../ai/alfred
cargo build --release

# Build DEBs (if needed)
cd ../../linux-distribution/SynOS-Packages
./build-all-packages.sh
```

---

## 🚀 Step 3: Run the Remaster Script

```bash
cd ~/Syn_OS
sudo ./scripts/02-build/build-synos-from-parrot.sh
```

### What This Does:

**Step 0:** Pre-flight checks (dependencies, components)  
**Step 1:** Create working directories  
**Step 2:** Extract ParrotOS ISO  
**Step 3:** Replace kernel with SynOS custom Rust kernel  
**Step 4:** Inject all SynOS proprietary components  
**Step 5:** Complete SynOS rebranding (boot, desktop, themes)  
**Step 6:** Configure SynOS services (ALFRED, AI daemon, consciousness)  
**Step 7:** Clean up ParrotOS residuals  
**Step 8:** Repackage as SynOS ISO  
**Step 9:** Generate checksums

### Expected Output:

```
╔═══════════════════════════════════════════════════════════════╗
║                 BUILD SUCCESSFUL!                             ║
╚═══════════════════════════════════════════════════════════════╝

ISO Location: ~/Syn_OS/build/iso/SynOS-v1.0-20251015.iso
ISO Size: 6.2G

Your custom SynOS with:
  ✓ Custom Rust kernel
  ✓ ALFRED voice assistant
  ✓ Consciousness framework
  ✓ AI daemon
  ✓ Full ParrotOS security tools
  ✓ Complete SynOS branding
```

---

## 🧪 Step 4: Test the ISO

### Test in QEMU/KVM

```bash
qemu-system-x86_64 \
    -cdrom ~/Syn_OS/build/iso/SynOS-v1.0-*.iso \
    -m 4096 \
    -smp 2 \
    -enable-kvm \
    -boot d
```

### Test in VirtualBox

1. Create new VM (Linux, Debian 64-bit)
2. Allocate 4GB RAM, 2 CPUs
3. Mount SynOS ISO as optical drive
4. Boot from ISO

### Test in VMware

1. Create new VM (Linux, Debian 11 64-bit)
2. Configure 4GB RAM, 2 cores
3. Mount SynOS ISO
4. Boot

---

## 💾 Step 5: Create Bootable USB

### Linux

```bash
# Find your USB device
lsblk

# Create bootable USB (replace sdX with your device)
sudo dd if=~/Syn_OS/build/iso/SynOS-v1.0-*.iso \
        of=/dev/sdX \
        bs=4M \
        status=progress \
        oflag=sync

# Verify
sync
```

### Windows

Use **Rufus** or **Etcher**:

-   Select SynOS ISO
-   Select USB drive
-   Write in DD mode

### macOS

```bash
# Find USB device
diskutil list

# Unmount
diskutil unmountDisk /dev/diskN

# Write ISO
sudo dd if=~/Syn_OS/build/iso/SynOS-v1.0-*.iso \
        of=/dev/rdiskN \
        bs=4m \
        status=progress
```

---

## 🎨 Customization Options

### Replace Boot Splash

```bash
# Add your custom splash image
cp your-splash.png ~/Syn_OS/assets/branding/boot-splash.png

# Rebuild
sudo ./scripts/02-build/build-synos-from-parrot.sh
```

### Add Custom Wallpapers

```bash
# Add wallpapers to
cp your-wallpaper.jpg ~/Syn_OS/assets/desktop/wallpapers/

# Rebuild
sudo ./scripts/02-build/build-synos-from-parrot.sh
```

### Add Custom Themes

```bash
# Add GTK/Icon themes to
cp -r your-theme ~/Syn_OS/assets/themes/

# Rebuild
sudo ./scripts/02-build/build-synos-from-parrot.sh
```

---

## 🔍 Verification Checklist

After booting SynOS, verify:

-   [ ] **Boot Screen:** Shows "SynOS" not "ParrotOS"
-   [ ] **Kernel:** `uname -r` shows "synos-1.0.0"
-   [ ] **OS Info:** `cat /etc/os-release` shows SynOS
-   [ ] **ALFRED:** Run `alfred` command
-   [ ] **AI Daemon:** Check `systemctl status synos-ai-daemon`
-   [ ] **Consciousness:** Check `systemctl status synos-consciousness`
-   [ ] **Wallpaper:** Shows SynOS branding
-   [ ] **Security Tools:** Verify `nmap`, `metasploit`, `wireshark`, etc.
-   [ ] **Custom DEBs:** Run `dpkg -l | grep synos`

---

## 🐛 Troubleshooting

### Build Fails at Kernel Step

**Problem:** Can't find SynOS kernel  
**Solution:** Build the kernel first:

```bash
cd ~/Syn_OS/core/kernel
cargo build --release --target x86_64-unknown-none
```

### Build Fails at DEB Installation

**Problem:** Missing custom DEBs  
**Solution:** Build the packages:

```bash
cd ~/Syn_OS/linux-distribution/SynOS-Packages
./build-all-packages.sh
```

### ISO Won't Boot

**Problem:** GRUB configuration issue  
**Solution:** Check if `isolinux.bin` exists in extracted ISO

### Services Don't Start

**Problem:** Systemd service files missing  
**Solution:** Ensure systemd units are in DEBs

---

## 📊 Build Time Estimates

| Stage              | Time          | Notes                 |
| ------------------ | ------------- | --------------------- |
| Download ParrotOS  | 10-30 min     | Depends on connection |
| Extract ISO        | 5 min         | ~5GB extraction       |
| Install Components | 10 min        | Copy files            |
| Repackage ISO      | 15-20 min     | SquashFS compression  |
| **Total**          | **40-65 min** | First build           |

Subsequent builds: ~25-30 min (ISO already downloaded)

---

## 🎯 What You Get

### SynOS v1.0 Features:

✅ **Custom Rust Kernel** - Our proprietary kernel  
✅ **ALFRED Voice Assistant** - "Hey ALFRED" activation  
✅ **AI Consciousness Framework** - Neural Darwinism implementation  
✅ **AI Daemon** - Background AI processing  
✅ **600+ Security Tools** - From ParrotOS base  
✅ **Complete SynOS Branding** - Logo, themes, wallpapers  
✅ **Educational Platform** - 4-phase curriculum integration  
✅ **Hardware Acceleration** - GPU/TPU support  
✅ **Live Boot Capable** - Test without installation

---

## 🚀 Next Steps

After successful build:

1. **Test thoroughly** in VMs
2. **Document any issues** in `TODO.md`
3. **Share with beta testers**
4. **Iterate on branding**
5. **Add missing tools** as separate DEBs
6. **Create tutorial videos**
7. **Publish to GitHub Releases**

---

## 📝 Build Log Location

All build output is logged to:

```
~/Syn_OS/logs/parrot-remaster-$(date +%Y%m%d-%H%M%S).log
```

---

## 🤝 Contributing

Found an issue? Want to improve the build process?

1. Open an issue: https://github.com/synos/synos/issues
2. Submit a PR with improvements
3. Join our Discord: https://discord.gg/synos

---

## 📜 License

SynOS is built on ParrotOS (GPLv3). Our custom components are:

-   **Kernel:** MIT License
-   **ALFRED:** MIT License
-   **Consciousness Framework:** MIT License
-   **Overall Distribution:** GPLv3 (due to ParrotOS base)

---

**Built with 💙 by the SynOS Team**

_Making AI-enhanced security accessible to everyone._
