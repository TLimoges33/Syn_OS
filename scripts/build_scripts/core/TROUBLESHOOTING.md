# Build Script Troubleshooting Guide

Common issues and solutions for the SynOS build system.

---

## Issue: "Missing: Rust toolchain (cargo)"

### Symptoms

```bash
[ERROR] ✗ Missing: Rust toolchain (cargo)
[ERROR] ✗ Missing dependencies: cargo
```

Even though running `cargo --version` works normally.

### Cause

Rust is installed in your user directory (`~/.cargo/bin/`), but when running the build script with `sudo`, it can't find cargo because sudo uses a different PATH.

### Solution

**The script automatically fixes this!** (As of October 13, 2025)

The build script now:

1. Searches common Rust installation locations
2. Automatically adds the found location to PATH
3. Continues with the build

### Manual Verification

```bash
# Check if cargo exists in your user directory
ls -la ~/.cargo/bin/cargo

# Check if sudo can find it (will fail before fix)
sudo which cargo

# After fix, the script will find and use it automatically
sudo ./ultimate-final-master-developer-v1.0-build.sh
```

### If Still Not Working

If cargo is in a non-standard location, you can:

**Option 1: Set CARGO_HOME**

```bash
export CARGO_HOME=/path/to/your/cargo
sudo -E ./ultimate-final-master-developer-v1.0-build.sh
```

**Option 2: Install system-wide** (not recommended)

```bash
sudo apt install cargo rustc
```

**Option 3: Add to sudo secure_path**

```bash
sudo visudo
# Add: Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/YOUR_USER/.cargo/bin"
```

### More Info

See: `docs/FIX_CARGO_DETECTION.md`

---

## Issue: Log file not created / "No such file or directory"

### Symptoms

```bash
./ultimate-final-master-developer-v1.0-build.sh: line 116: /home/user/Syn_OS/build/logs/build-xxx.log: No such file or directory
```

### Cause

Early logging functions tried to write to log files before the `build/logs/` directory was created.

### Solution

**Already fixed!** (As of October 13, 2025)

Logging functions now check if the log directory exists before writing:

-   Console output always works
-   File logging happens only after directory is created
-   No errors during banner display

### Verification

The script should now display the banner and logs without errors:

```bash
╔════════════════════════════════════════════════════════════════════════════╗
║              🧠 SynOS Ultimate Master Developer Build v1.0.0              ║
╚════════════════════════════════════════════════════════════════════════════╝

[INFO] SynOS Ultimate Master Build v1.0.0-final
[INFO] Build ID: 20251013-XXXXXX-XXXXXXX
[INFO] Logging initialized: /home/user/Syn_OS/build/logs/build-xxx.log
```

---

## Issue: Permission denied errors

### Symptoms

```bash
mkdir: cannot create directory '/home/user/Syn_OS/build/iso': Permission denied
mount: only root can use "--bind" option
```

### Cause

The build script needs root privileges to:

-   Create bind mounts for chroot
-   Use debootstrap
-   Create ISO images with proper permissions

### Solution

Run with sudo:

```bash
sudo ./scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh
```

**Note:** The script automatically handles the cargo PATH issue when running with sudo (see "Missing cargo" section above).

---

## Issue: Rust target not installed

### Symptoms

```bash
[ERROR] ✗ Rust target x86_64-unknown-none not installed
```

### Cause

The bare-metal target needed for kernel compilation isn't installed.

### Solution

**The script automatically installs it!**

If you want to install manually:

```bash
rustup target add x86_64-unknown-none --toolchain nightly
```

---

## Issue: Build fails with "No space left on device"

### Symptoms

```bash
[ERROR] ✗ Insufficient disk space
[ERROR] ✗ Stage failed: stage_check_resources
```

### Cause

Building the ISO requires significant disk space:

-   At least 10 GB free recommended
-   20+ GB for full development build

### Solution

**Option 1: Clean previous builds**

```bash
sudo ./scripts/03-maintenance/cleanup/clean-build-artifacts.sh
```

**Option 2: Check disk space**

```bash
df -h /home/diablorain/Syn_OS
```

**Option 3: Clean Docker**

```bash
docker system prune -a
```

**Option 4: Expand disk/partition**

---

## Issue: debootstrap fails

### Symptoms

```bash
[ERROR] ✗ Failed to create Debian chroot
E: Failed getting release file...
```

### Cause

-   Network issues
-   Invalid Debian mirror
-   Outdated debootstrap

### Solution

**Option 1: Update debootstrap**

```bash
sudo apt update && sudo apt install --reinstall debootstrap
```

**Option 2: Use different mirror**
Edit the script and change:

```bash
DEBIAN_MIRROR="http://deb.debian.org/debian"
# to
DEBIAN_MIRROR="http://ftp.us.debian.org/debian"
```

**Option 3: Check network**

```bash
ping -c 3 deb.debian.org
curl -I http://deb.debian.org/debian/dists/bookworm/Release
```

---

## Issue: Build stalls / hangs

### Symptoms

Script appears frozen with no output for extended period.

### Cause

-   Waiting for package downloads
-   Compiling large Rust projects
-   Docker container startup

### Solution

**Check if actually working:**

```bash
# In another terminal
sudo tail -f build/logs/build-*.log

# Check resource usage
top
htop
```

**Common "stall points" (actually working):**

1. Rust target installation (2-5 minutes)
2. Kernel compilation (10-30 minutes)
3. debootstrap package installation (5-15 minutes)
4. SquashFS creation (2-10 minutes)

**If truly hung:**

```bash
# Kill gracefully
sudo pkill -SIGTERM -f ultimate-final-master

# Force kill if needed
sudo pkill -SIGKILL -f ultimate-final-master

# Clean up mounts
sudo umount /home/diablorain/Syn_OS/build/chroot/dev
sudo umount /home/diablorain/Syn_OS/build/chroot/proc
sudo umount /home/diablorain/Syn_OS/build/chroot/sys
```

---

## Issue: Chroot errors

### Symptoms

```bash
chroot: failed to run command '/bin/bash': No such file or directory
```

### Cause

Incomplete debootstrap or missing bind mounts.

### Solution

**Option 1: Verify mounts**

```bash
mount | grep chroot
```

Should show:

```
/home/diablorain/Syn_OS/build/chroot/dev
/home/diablorain/Syn_OS/build/chroot/proc
/home/diablorain/Syn_OS/build/chroot/sys
```

**Option 2: Remount**

```bash
sudo ./scripts/02-build/core/ensure-chroot-mounts.sh
```

**Option 3: Rebuild chroot**

```bash
sudo rm -rf build/chroot
# Re-run build script
```

---

## Issue: ISO doesn't boot

### Symptoms

ISO created successfully but won't boot in QEMU or on real hardware.

### Cause

-   Missing GRUB configuration
-   Incorrect kernel path
-   Missing boot files

### Solution

**Test the ISO:**

```bash
# Quick test
qemu-system-x86_64 -cdrom build/iso/synos-v1.0.0-final.iso -m 2G

# With more debugging
qemu-system-x86_64 \
  -cdrom build/iso/synos-v1.0.0-final.iso \
  -m 2G \
  -enable-kvm \
  -serial stdio \
  -display gtk
```

**Verify ISO contents:**

```bash
# Mount and inspect
mkdir -p /tmp/iso-check
sudo mount -o loop build/iso/synos-v1.0.0-final.iso /tmp/iso-check
ls -R /tmp/iso-check/
sudo umount /tmp/iso-check
```

**Check for required files:**

-   `/boot/grub/grub.cfg`
-   `/boot/kernel/synos-kernel.elf` or similar
-   `/boot/initrd.img`

---

## Issue: Python dependency errors

### Symptoms

```bash
ModuleNotFoundError: No module named 'XXX'
```

### Cause

Missing Python packages needed by AI daemon or build scripts.

### Solution

**Install development requirements:**

```bash
pip3 install -r development/requirements.txt

# Or system-wide
sudo pip3 install -r development/requirements.txt
```

**Common missing packages:**

```bash
pip3 install pyyaml requests psutil
```

---

## Issue: Docker containers not starting

### Symptoms

```bash
[ERROR] ✗ Failed to start NATS container
```

### Cause

-   Docker not running
-   Port conflicts
-   Previous containers still running

### Solution

**Check Docker status:**

```bash
sudo systemctl status docker
sudo systemctl start docker
```

**Clean up old containers:**

```bash
docker ps -a
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
```

**Start fresh:**

```bash
cd /home/diablorain/Syn_OS
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d nats postgres redis
```

---

## Getting More Help

### Enable debug logging

```bash
# Set environment variable
export DEBUG=1
sudo -E ./scripts/02-build/core/ultimate-final-master-developer-v1.0-build.sh
```

### Check recent logs

```bash
# View latest build log
ls -lt build/logs/build-*.log | head -1 | awk '{print $NF}' | xargs less

# View all recent logs
tail -100 build/logs/build-*.log
```

### Report an issue

When reporting issues, include:

1. Output of `uname -a`
2. Output of `cargo --version` and `rustc --version`
3. Relevant sections from `build/logs/build-*.log`
4. Output of `df -h` (disk space)
5. Output of `free -h` (memory)

---

## Quick Diagnosis Commands

```bash
# Check all dependencies
command -v cargo debootstrap xorriso mksquashfs grub-mkrescue python3 git

# Check Rust setup
rustup show
rustup target list | grep installed

# Check disk space
df -h /home/diablorain/Syn_OS

# Check memory
free -h

# Check running processes
ps aux | grep -E 'build|cargo|rustc'

# Check mounts
mount | grep chroot

# Check Docker
docker ps
docker-compose -f docker/docker-compose.yml ps

# Verify build environment
./scripts/02-build/validation/validate-build-env.sh
```

---

## Known Working Configuration

The build script has been tested and confirmed working with:

-   **OS:** Ubuntu 22.04 LTS / Debian 12
-   **Rust:** rustc 1.75+ (nightly)
-   **Cargo:** 1.75+
-   **Python:** 3.10+
-   **Docker:** 24.0+
-   **Disk Space:** 20+ GB free
-   **Memory:** 8+ GB RAM
-   **Architecture:** x86_64

---

**Last Updated:** October 13, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
