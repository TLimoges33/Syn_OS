# ✅ Pre-Build Checklist

Before running the comprehensive build, verify:

## System Requirements

-   [ ] **Free Disk Space:** At least 25 GB available

    ```bash
    df -h /home/diablorain/Syn_OS
    # Should show > 25 GB free
    ```

-   [ ] **RAM:** At least 8 GB (16 GB recommended)

    ```bash
    free -h
    # Should show > 8 GB total
    ```

-   [ ] **CPU:** Multi-core processor (more cores = faster build)
    ```bash
    nproc
    # Shows number of CPU cores
    ```

## Software Requirements

-   [ ] **Debian/Ubuntu System:** Running Debian-based distribution

    ```bash
    lsb_release -a
    # Should show Debian or Ubuntu
    ```

-   [ ] **debootstrap:** Installed

    ```bash
    which debootstrap || sudo apt-get install debootstrap
    ```

-   [ ] **live-build:** Installed (will be installed during build if needed)

    ```bash
    which lb || sudo apt-get install live-build
    ```

-   [ ] **Rust/Cargo:** Installed

    ```bash
    cargo --version
    # Should show version 1.70+
    ```

-   [ ] **Build tools:** Essential tools installed
    ```bash
    sudo apt-get install build-essential git curl wget
    ```

## Project Verification

-   [ ] **In correct directory:**

    ```bash
    pwd
    # Should show: /home/diablorain/Syn_OS
    ```

-   [ ] **Build script exists and is executable:**

    ```bash
    ls -lh scripts/BUILD-COMPLETE-SYNOS-DISTRIBUTION.sh
    # Should show -rwxr-xr-x (executable)
    ```

-   [ ] **Kernel can build:**
    ```bash
    cd src/kernel
    cargo check --target=x86_64-unknown-none
    cd ../..
    ```

## Network Requirements

-   [ ] **Internet connection:** Active (for downloading packages)

    ```bash
    ping -c 3 debian.org
    # Should succeed
    ```

-   [ ] **Repository access:** Can reach Debian and ParrotOS repos
    ```bash
    curl -I http://deb.debian.org >/dev/null 2>&1 && echo "✅ Debian OK"
    curl -I http://deb.parrot.sh >/dev/null 2>&1 && echo "✅ ParrotOS OK"
    ```

## Permissions

-   [ ] **Can use sudo:**
    ```bash
    sudo -v
    # Should not ask for password if recently used
    ```

## Ready to Build!

If all checks pass, you're ready to build:

```bash
cd /home/diablorain/Syn_OS
sudo ./scripts/BUILD-COMPLETE-SYNOS-DISTRIBUTION.sh
```

## Build Monitoring

Once started, you can monitor progress:

```bash
# In another terminal
tail -f linux-distribution/SynOS-Linux-Builder/build-complete-*.log
```

## Expected Timeline

```
Phase 1:  Rust Compilation          → 15-20 minutes
Phase 2:  Environment Prep           → 2-3 minutes
Phase 3:  Binary Collection          → 1-2 minutes
Phase 4:  Source Archive             → 3-5 minutes
Phase 5:  Package Repository         → 2-3 minutes
Phase 6-8: Configuration             → 5 minutes
Phase 9-11: Live-Build               → 60-90 minutes
Phase 12: Component Injection        → 5 minutes
Phase 13: Finalization               → 10-15 minutes
Phase 14-15: Verification & Report   → 2-3 minutes
────────────────────────────────────────────────────
TOTAL:                                90-120 minutes
```

## Output Files

After successful build, you'll have:

```
linux-distribution/SynOS-Linux-Builder/
├── SynOS-Complete-v1.0-TIMESTAMP-amd64.iso         # The complete ISO!
├── SynOS-Complete-v1.0-TIMESTAMP-amd64.iso.sha256  # Checksum
├── SynOS-Complete-v1.0-TIMESTAMP-amd64.iso.md5     # MD5
├── BUILD-REPORT-TIMESTAMP.md                       # Detailed report
└── build-complete-TIMESTAMP.log                    # Full build log
```

## After Build

1. **Verify checksums:**

    ```bash
    sha256sum -c SynOS-Complete-*.iso.sha256
    ```

2. **Test in QEMU:**

    ```bash
    qemu-system-x86_64 -cdrom SynOS-Complete-*.iso -m 8G -smp 4 -enable-kvm
    ```

3. **Read build report:**

    ```bash
    cat BUILD-REPORT-*.md
    ```

4. **Verify contents:**
    ```bash
    sudo mount -o loop SynOS-Complete-*.iso /mnt
    ls -R /mnt/usr/src/synos/    # Your source code
    ls -R /mnt/boot/synos/        # Your kernel
    ls /mnt/usr/local/bin/        # Your binaries
    sudo umount /mnt
    ```

---

**All checks passed? Ready to build your complete distribution!** 🚀

```bash
sudo ./scripts/BUILD-COMPLETE-SYNOS-DISTRIBUTION.sh
```
