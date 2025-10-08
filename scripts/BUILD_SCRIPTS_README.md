# Syn_OS Build Scripts Documentation

## 🎯 Primary Build Script

### `build-synos-iso.sh` - **Production Linux Distribution Builder**

**Purpose:** Creates the complete Syn_OS Linux distribution ISO  
**Type:** Debian-based Linux distribution with XFCE desktop  
**Output:** ~9-10 GB bootable ISO with BIOS + UEFI support

**What's Included:**

-   ✅ Complete XFCE4 desktop environment
-   ✅ All Syn_OS AI modules (core/ai/)
-   ✅ Security framework (core/security/)
-   ✅ Complete source code (src/, core/, docs/, scripts/, tests/, tools/)
-   ✅ Development tools (gcc, g++, Rust, Python, git, vim, nano, htop)
-   ✅ Firefox ESR browser
-   ✅ Network Manager, File Roller
-   ✅ Custom Rust kernel (73KB, educational component)

**Usage:**

```bash
sudo ./scripts/build-synos-iso.sh
```

**Login Credentials:**

-   User: `synos` / Password: `synos`
-   Root: `root` / Password: `toor`

**Build Time:** ~20-30 minutes  
**Requirements:** 20GB free space, internet connection

---

## 📁 Directory Structure

```
scripts/
├── build-synos-iso.sh           # ⭐ MAIN PRODUCTION BUILDER
├── archive/
│   ├── experimental-builds/
│   │   └── build-true-synos-iso.sh    # Bare-metal Rust kernel (experimental)
│   └── old-build-scripts/             # Historical build attempts
├── build/                        # Utility scripts for monitoring/management
├── build-system/                 # Alternative builders (legacy)
└── BUILD_SCRIPTS_README.md       # This file
```

---

## 🗄️ Archived Scripts

### `archive/experimental-builds/build-true-synos-iso.sh`

**Purpose:** Boots the custom Rust kernel directly (bare-metal OS)  
**Status:** Experimental - Not production ready  
**Type:** Bare-metal operating system (NOT Linux-based)

**Why Archived:**

-   This was created during a misunderstanding about the project scope
-   Syn_OS is a **Linux distribution** (like Kali/ParrotOS), not a bare-metal OS
-   The custom Rust kernel is for **education/research**, not replacement of Linux
-   Kept for future experimentation and learning purposes

### `archive/old-build-scripts/`

Historical build attempts from early development. Kept for reference.

---

## 🔧 Build System Scripts (`build-system/`)

Legacy scripts that may be consolidated in future:

-   `build-synos-linux.sh` - Alternative Debian builder
-   `build-production-iso.sh` - Earlier production attempt
-   `setup-iso-build-env.sh` - Environment setup

**Status:** Under review for consolidation or archival

---

## 🚀 Quick Start

1. **Build the ISO:**

    ```bash
    cd /home/diablorain/Syn_OS
    sudo ./scripts/build-synos-iso.sh
    ```

2. **Test in QEMU:**

    ```bash
    qemu-system-x86_64 -cdrom build/SynOS-Complete-v1.0-*.iso -m 4096 -smp 2 -enable-kvm
    ```

3. **Write to USB (with Ventoy):**

    - Copy ISO to Ventoy USB drive
    - Boot from USB
    - Select ISO from Ventoy menu

4. **Write to USB (direct):**
    ```bash
    sudo dd if=build/SynOS-Complete-v1.0-*.iso of=/dev/sdX bs=4M status=progress oflag=sync
    ```

---

## 📊 Script Comparison

| Feature      | build-synos-iso.sh          | build-true-synos-iso.sh |
| ------------ | --------------------------- | ----------------------- |
| **Type**     | Linux Distribution          | Bare-metal OS           |
| **Base**     | Debian 12                   | None (custom kernel)    |
| **Desktop**  | XFCE4                       | None                    |
| **Size**     | ~9-10 GB                    | ~100-200 MB             |
| **Boot**     | BIOS + UEFI                 | BIOS only               |
| **Status**   | ✅ Production               | ⚠️ Experimental         |
| **Use Case** | Daily use, security testing | Research, learning      |

---

## 🎯 Recommended Usage

**For Production/Daily Use:**

-   Use `build-synos-iso.sh`
-   Creates complete Linux distribution
-   All tools and applications included
-   Fully functional desktop environment

**For Experimentation:**

-   Use `archive/experimental-builds/build-true-synos-iso.sh`
-   Tests bare-metal Rust kernel
-   Educational purposes only
-   Limited functionality

---

## 📝 Notes

-   **Primary Goal:** Syn_OS is a Linux distribution (like Kali Linux, Parrot Security)
-   **Custom Kernel:** The Rust kernel is an educational component that runs ON Linux
-   **Build Scripts:** Consolidated to one main script for production use
-   **Archives:** Old scripts kept for reference and learning

---

## 🔄 Future Improvements

1. Add option for different desktop environments (KDE, GNOME)
2. Integrate with linux-distribution/ folder builds
3. Add automated testing suite
4. Create minimal/standard/full build options
5. Add custom package selection menu

---

## 📞 Build Support

If the build fails:

1. Check `/tmp/synos-distro-build.log`
2. Verify 20GB free space: `df -h`
3. Ensure internet connection
4. Try cleaning build directory: `sudo rm -rf build/synos-iso/`

---

**Last Updated:** October 7, 2025  
**Maintainer:** Syn_OS Development Team
