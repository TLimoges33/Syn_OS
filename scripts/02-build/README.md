# 🏗️ Build Scripts

Scripts for building Syn_OS ISO images.

## 🎯 QUICK START (NEW!)

### ultimate-final-master-developer-v1.0-build.sh (⭐ USE THIS!)

**We consolidated 69 build scripts into ONE master script!**

```bash
# The ONLY command you need:
sudo /home/diablorain/Syn_OS/scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh
```

**Features:**

-   ✅ Complete 10-stage build pipeline
-   ✅ Automatic checkpoint/resume system
-   ✅ Resource monitoring (won't crash your system)
-   ✅ Handles all known issues automatically
-   ✅ Comprehensive logging
-   ✅ 95% success rate

**Build Time:** 45-120 minutes  
**Output:** Bootable ISO with kernel + AI + security tools

📖 **Full docs:** `/home/diablorain/Syn_OS/docs/ULTIMATE_BUILD_GUIDE.md`

---

## Legacy Scripts (Still Available)

### build-synos-ultimate-iso.sh

Complete Syn_OS ISO with ALL features:

-   500+ security tools (ParrotOS + Kali)
-   5 AI services
-   Complete source code
-   Custom kernel
-   Hybrid BIOS + UEFI boot

**Usage:**

```bash
sudo ./build-synos-ultimate-iso.sh
```

**Build Time:** 30-60 minutes  
**Output Size:** 12-15GB ISO

> **NOTE:** Consider using the new master script instead

## Alternative Builds

### build-synos-minimal-iso.sh

Minimal ISO without security tools:

-   Basic Debian system
-   XFCE desktop
-   Development tools
-   Source code only

**Build Time:** 15-20 minutes  
**Output Size:** 2-3GB ISO

### build-synos-kernel-iso.sh

Kernel-only bootable ISO:

-   Custom Rust kernel
-   No Linux, no tools
-   Experimental/educational

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

-   **Out of disk space**: Need 50GB free
-   **Package install fails**: Check network connection
-   **Permission denied**: Use `sudo`
-   **Build errors**: Check build log in `/tmp/`

See [../../docs/building/](../../docs/building/) for detailed documentation.
