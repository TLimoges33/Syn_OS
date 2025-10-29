# Permission Issues with Build Artifacts - Solution Guide

**Problem:** "Operation not permitted" when trying to remove old build artifacts

**Root Cause:** Build artifacts created by processes running as root cannot be deleted by regular users

---

## 🔍 Understanding the Problem

### Why This Happens

1. **Build script runs as root** (via `sudo`)
2. **Creates files/directories as root** in the chroot environment
3. **Next build attempt** tries to clean up
4. **Cleanup fails** if not running as root (permission denied)

### File Ownership Example

```bash
$ ls -la build/full-distribution/
drwxr-xr-x diablorain diablorain  .          # User-owned
drwxr-xr-x root       root         chroot/   # Root-owned! ❌
```

---

## ✅ Solutions

### Solution 1: Always Run Build Script with Sudo (RECOMMENDED)

The build script **must** be run with sudo:

```bash
# ✅ CORRECT
sudo ./scripts/build-full-distribution.sh --clean --fresh

# ❌ WRONG - Will fail to clean up root-owned files
./scripts/build-full-distribution.sh --clean --fresh
```

**Why this works:**

-   Script runs as root
-   Can create AND delete root-owned files
-   Cleanup works properly with `--clean` flag

### Solution 2: Manual Cleanup Script

If you have existing build artifacts causing issues, use the cleanup script:

```bash
# Run the dedicated cleanup script
sudo ./scripts/utilities/clean-build-artifacts.sh
```

**What it does:**

-   Checks for root-owned files
-   Unmounts chroot filesystems
-   Removes entire build directory
-   Provides clear status messages

### Solution 3: Manual Cleanup (Emergency)

If scripts aren't working, manual cleanup:

```bash
# Unmount filesystems
sudo umount -l build/full-distribution/chroot/sys
sudo umount -l build/full-distribution/chroot/proc
sudo umount -l build/full-distribution/chroot/dev

# Remove build directory
sudo rm -rf build/full-distribution/

# Verify cleanup
ls -la build/
```

---

## 🛠️ Script Improvements (v2.4.2)

### Enhanced Cleanup Logic

The build script now includes:

1. **Root-owned file detection:**

    ```bash
    if [ "$(find "$BUILD_DIR" -user root 2>/dev/null | head -1)" ]; then
        echo "Detected root-owned files, using sudo..."
    fi
    ```

2. **Better error handling:**

    ```bash
    sudo rm -rf "$BUILD_DIR" || {
        echo "Failed to remove build directory"
        echo "Try: sudo rm -rf $BUILD_DIR"
        exit 1
    }
    ```

3. **Cleanup order fixed:**
    - Check for clean build flag FIRST
    - Remove directory with sudo BEFORE recreating
    - Create new directories as current user

### Sudo Access Check

Script validates sudo access at startup:

```bash
if [ "$EUID" -ne 0 ]; then
    echo "This build requires sudo access"
    sudo -v || exit 1
    # Keep sudo alive during build
fi
```

---

## 📋 Prevention Checklist

-   [ ] Always use `sudo` when running build script
-   [ ] Don't mix sudo and non-sudo builds
-   [ ] Use `--clean --fresh` for first build after permission errors
-   [ ] Keep cleanup script handy for emergencies

---

## 🚨 Common Error Messages

### "Operation not permitted"

**Cause:** Trying to delete root-owned files as regular user  
**Fix:** Run with sudo

### "Permission denied" during git clone

**Cause:** Script not running as root, can't write to root-owned directories  
**Fix:** Run entire script with sudo

### "Device or resource busy" during cleanup

**Cause:** Chroot filesystems still mounted  
**Fix:** Use cleanup script which unmounts first, or manually unmount

---

## 💡 Best Practices

1. **Always run build script with sudo:**

    ```bash
    sudo ./scripts/build-full-distribution.sh --clean --fresh
    ```

2. **Use cleanup script between builds:**

    ```bash
    sudo ./scripts/utilities/clean-build-artifacts.sh
    sudo ./scripts/build-full-distribution.sh --clean --fresh
    ```

3. **Check disk space before building:**

    ```bash
    df -h  # Need 100GB+ free
    ```

4. **Monitor build progress:**
    ```bash
    # In another terminal
    tail -f build/full-distribution/build-*.log
    ```

---

## 📊 Summary

| Issue                   | Cause                 | Solution            |
| ----------------------- | --------------------- | ------------------- |
| Can't delete chroot/    | Root-owned files      | Run build with sudo |
| Permission denied logs  | Mixed user/root files | Use cleanup script  |
| Operation not permitted | No sudo access        | Always use sudo     |

**Golden Rule:** If it creates files as root, it must clean them as root! ✨

---

**Updated:** October 25, 2025  
**Build Script Version:** v2.4.2
