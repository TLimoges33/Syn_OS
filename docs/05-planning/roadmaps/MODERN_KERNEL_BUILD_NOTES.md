# Modern Kernel Build Process - Notes

**Date:** October 28, 2025
**Topic:** Modern vs. Legacy Kernel Packaging

---

## 🆕 MODERN METHOD (2020+)

### Using `make bindeb-pkg`

**Command:**
```bash
cd /usr/src/linux-source-6.12
sudo make bindeb-pkg -j$(nproc)
```

**What it does:**
- Uses kernel's built-in Debian packaging
- Creates .deb packages directly from Makefile
- No external tools needed (except debhelper)
- Recommended by kernel maintainers

**Output packages:**
```
linux-image-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb
linux-headers-6.12.32-synos-ai-v0.1_6.12.32-1_amd64.deb
linux-libc-dev_6.12.32-1_amd64.deb
linux-image-6.12.32-synos-ai-v0.1-dbg_6.12.32-1_amd64.deb (debug symbols)
```

**Dependencies:**
- `debhelper` - Debian packaging scripts
- `fakeroot` - Fake root for packaging
- Standard build tools (gcc, make, etc.)

---

## ❌ LEGACY METHOD (Pre-2020)

### Using `kernel-package` (DEPRECATED)

**Command:**
```bash
make-kpkg --rootcmd fakeroot --initrd kernel_image kernel_headers
```

**Why deprecated:**
- Unmaintained since ~2018
- Not available in modern Debian/Ubuntu
- Replaced by kernel's native packaging
- Had compatibility issues with modern kernels

**Package name:** `kernel-package` (no longer in Debian repos)

---

## 📊 COMPARISON

| Feature | `make bindeb-pkg` | `kernel-package` |
|---------|-------------------|------------------|
| **Status** | ✅ Active, maintained | ❌ Deprecated |
| **Availability** | ✅ Built into kernel | ❌ Removed from repos |
| **Dependencies** | Minimal (debhelper) | Many (kernel-package) |
| **Speed** | Fast | Slower |
| **Compatibility** | All modern kernels | Issues with 5.x+ |
| **Recommended** | ✅ Yes | ❌ No |

---

## 🔧 MAKE TARGETS

### Available packaging targets:

```bash
make help | grep deb
```

**Output:**
```
  bindeb-pkg          - Build all .deb packages (recommended)
  deb-pkg             - Build only binary .deb package
  intdeb-pkg          - Build all .deb packages (no debug)
```

**Most common:**
- `bindeb-pkg` - Builds all packages including headers (use this)
- `deb-pkg` - Only kernel image (no headers)

---

## 📦 PACKAGE TYPES EXPLAINED

### 1. linux-image-* (Required)
**Size:** 50-100 MB
**Contains:**
- Kernel binary (vmlinuz)
- System.map
- Boot configuration
- initrd generation scripts

**Purpose:** Bootable kernel

### 2. linux-headers-* (Recommended)
**Size:** 10-20 MB
**Contains:**
- Kernel headers for module compilation
- Build scripts
- Kconfig files

**Purpose:** Building external kernel modules (drivers, DKMS)

### 3. linux-libc-dev (Optional)
**Size:** 1-2 MB
**Contains:**
- Kernel headers for userspace programs
- System call definitions

**Purpose:** Compiling programs that use kernel APIs

### 4. linux-image-*-dbg (Optional)
**Size:** 500+ MB
**Contains:**
- Debug symbols
- Unstripped kernel

**Purpose:** Kernel debugging, crash analysis

---

## 🚀 SYNOS AI KERNEL BUILD

### Our approach (Phase 1-6):

**Phase 1 (Current):**
```bash
# Build baseline kernel with bindeb-pkg
cd /usr/src/linux-source-6.12
sudo make bindeb-pkg -j$(nproc)

# Install
sudo dpkg -i linux-image-6.12.32-synos-ai-v0.1_*.deb
sudo dpkg -i linux-headers-6.12.32-synos-ai-v0.1_*.deb
```

**Phase 2-6 (AI modifications):**
Same process, just with modified source:
1. Edit kernel source (add syscalls, eBPF, scheduler changes)
2. Increment version (v0.2, v0.3, etc.)
3. Build with `make bindeb-pkg`
4. Test and deploy

---

## 💡 BEST PRACTICES

### Version Numbering
```bash
# Set in .config
CONFIG_LOCALVERSION="-synos-ai-v0.1"

# Or via command line
make LOCALVERSION=-synos-ai-v0.1 bindeb-pkg
```

**Our scheme:**
- v0.1 - Baseline (Phase 1)
- v0.2 - AI syscalls (Phase 2)
- v0.3 - eBPF telemetry (Phase 3)
- v0.4 - Consciousness scheduler (Phase 4)
- v0.5 - AI runtime integration (Phase 5)
- v1.0 - Production release (Phase 6)

### Parallel Builds
```bash
# Use all cores for speed
make -j$(nproc) bindeb-pkg

# Or specify cores
make -j8 bindeb-pkg
```

### Clean Builds
```bash
# Remove all build artifacts
make mrproper

# Remove only object files (keeps .config)
make clean
```

---

## 🐛 TROUBLESHOOTING

### Error: "No rule to make target 'bindeb-pkg'"
**Cause:** Old kernel source (pre-3.x)
**Solution:** Use modern kernel (we use 6.12.32) ✅

### Error: "debhelper: command not found"
**Cause:** Missing debhelper package
**Solution:**
```bash
sudo apt install debhelper
```

### Error: Package build fails
**Solution:**
```bash
# Check build log
less /usr/src/linux-source-6.12/debian/files

# Try without debug package
make bindeb-pkg KDEB_PKGVERSION=1
```

---

## 📚 REFERENCES

**Official Documentation:**
- Kernel documentation: `Documentation/admin-guide/README.rst`
- Debian packaging: `scripts/package/mkdebian`

**Modern kernel build guides:**
- Debian Wiki: https://wiki.debian.org/BuildADebianKernelPackage
- Kernel.org: https://www.kernel.org/doc/html/latest/admin-guide/README.html

---

## ✅ VERIFICATION

To verify you're using modern method:

```bash
# Should work (modern)
cd /usr/src/linux-source-6.12
make help | grep bindeb-pkg
# Output: bindeb-pkg - Build all .deb packages

# Should NOT work (legacy)
which make-kpkg
# Output: not found ✅
```

---

**Summary:** We're using the modern `make bindeb-pkg` method, which is built into the kernel, actively maintained, and recommended for all Debian-based distributions including ParrotOS.

**Status:** ✅ Correct approach documented and scripted
**Phase 1:** Ready to proceed with modern build method
