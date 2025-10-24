# Critical Terminal Environment Fix

**Problem**: VS Code terminals failing with `forkpty(3) failed` error
**Root Cause**: System resource exhaustion or corrupted PTY devices
**Date**: October 23, 2025

## IMMEDIATE ACTION REQUIRED

The IDE environment is critically broken. You must execute these fixes from an **external terminal** (not VS Code).

---

## Step 1: Open External Terminal

Press `Ctrl+Alt+T` or use your system's terminal application (NOT VS Code terminal).

---

## Step 2: Run Diagnostic

```bash
cd /home/diablorain/Syn_OS

# Run the diagnostic script
sudo bash scripts/fix-terminal-environment.sh
```

Password: `superadmin33`

This will:

-   Check PTY device status
-   Verify resource limits
-   Identify process/file descriptor exhaustion
-   Show mount point status
-   Check for zombie processes

---

## Step 3: Quick Fix (Run in External Terminal)

```bash
# Fix critical devices
sudo rm -f /dev/null && sudo mknod -m 666 /dev/null c 1 3
sudo rm -f /dev/ptmx && sudo mknod -m 666 /dev/ptmx c 5 2
sudo chmod 666 /dev/null /dev/zero /dev/ptmx /dev/random /dev/urandom

# Ensure /dev/pts is mounted
sudo mount -t devpts devpts /dev/pts -o rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000

# Clear system caches
sync
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# Check status
ls -la /dev/null /dev/ptmx
mount | grep pts
ulimit -a
```

---

## Step 4: Increase System Limits

Edit `/etc/security/limits.conf` (requires sudo):

```bash
sudo nano /etc/security/limits.conf
```

Add these lines:

```
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
diablorain soft nofile 65536
diablorain hard nofile 65536
diablorain soft nproc 32768
diablorain hard nproc 32768
```

---

## Step 5: Fix Systemd Login Limits

Edit `/etc/systemd/logind.conf`:

```bash
sudo nano /etc/systemd/logind.conf
```

Uncomment or add:

```
[Login]
UserTasksMax=32768
```

Restart logind:

```bash
sudo systemctl restart systemd-logind
# WARNING: This may disconnect your session
```

---

## Step 6: Fix Systemd User Limits

```bash
sudo mkdir -p /etc/systemd/system/user@.service.d
sudo nano /etc/systemd/system/user@.service.d/limits.conf
```

Add:

```
[Service]
LimitNOFILE=65536
LimitNPROC=32768
TasksMax=32768
```

Reload:

```bash
sudo systemctl daemon-reload
```

---

## Step 7: Close VS Code Completely

```bash
# Kill all VS Code processes
pkill -9 code
pkill -9 electron
ps aux | grep -i code | grep -v grep | awk '{print $2}' | xargs -r kill -9

# Wait a few seconds
sleep 5

# Verify all killed
ps aux | grep -i code | grep -v grep
```

---

## Step 8: Clean Up System Resources

```bash
# Clean zombie processes
ps aux | awk '$8=="Z"' | awk '{print $2}' | xargs -r kill -9

# Clean stale file locks
sudo rm -rf /tmp/.X*-lock 2>/dev/null || true
sudo rm -rf /tmp/vscode-* 2>/dev/null || true
sudo rm -rf /tmp/code-* 2>/dev/null || true

# Clean user temp files
rm -rf ~/.config/Code/logs/* 2>/dev/null || true
rm -rf ~/.config/Code/CachedData/* 2>/dev/null || true
```

---

## Step 9: Reboot (if needed)

If the above fixes don't resolve it:

```bash
sudo reboot
```

After reboot, verify:

```bash
ulimit -n  # Should show 65536
ulimit -u  # Should show 32768
ls -la /dev/null /dev/ptmx  # Should be character devices with 666 permissions
mount | grep pts  # Should show /dev/pts mounted
```

---

## Step 10: Restart VS Code

```bash
# Start VS Code from terminal to see any errors
cd /home/diablorain/Syn_OS
code .
```

---

## Step 11: Test Terminal in VS Code

Once VS Code opens:

1. Press `` Ctrl+` `` to open terminal
2. Test: `echo "test" > /dev/null`
3. Test: `ls -la`
4. Test: `cargo --version`

---

## Root Cause Analysis

The `forkpty(3) failed` error typically occurs due to:

1. **File Descriptor Exhaustion**: VS Code + Rust builds can open thousands of files

    - Default limit: 1024
    - Fixed by: Increasing to 65536

2. **Process Limit Exhaustion**: systemd user slice has default TasksMax

    - Default: Often 10000-20000
    - Fixed by: Increasing to 32768

3. **Corrupted PTY Devices**: /dev/pts or /dev/ptmx damaged or unmounted

    - Fixed by: Recreating devices and remounting /dev/pts

4. **Zombie Processes**: Accumulation of dead VS Code/Electron processes

    - Fixed by: Killing all VS Code processes and restarting

5. **Memory Pressure**: System running out of memory
    - Fixed by: Clearing caches and closing applications

---

## Prevention

To prevent recurrence:

1. **Restart VS Code daily** when doing heavy builds
2. **Monitor resources**: `htop`, `watch -n 1 'ps aux | wc -l'`
3. **Clean builds**: `cargo clean` periodically
4. **Use release builds** instead of debug (smaller)
5. **Close unused terminals/editors** in VS Code
6. **Disable unnecessary extensions** in VS Code

---

## Verification Script

After fixes, run this to verify:

```bash
#!/bin/bash
echo "=== Verification ==="
echo "File descriptors: $(ulimit -n)"
echo "Process limit: $(ulimit -u)"
echo "Open FDs: $(lsof -u $(whoami) 2>/dev/null | wc -l)"
echo "Running processes: $(ps -u $(whoami) --no-headers | wc -l)"
echo "/dev/null: $(ls -la /dev/null)"
echo "/dev/ptmx: $(ls -la /dev/ptmx)"
echo "/dev/pts mount: $(mount | grep pts)"
echo "Test write: $(echo test >/dev/null 2>&1 && echo OK || echo FAILED)"
echo "Test PTY: $(python3 -c 'import pty; pty.openpty()' 2>&1 && echo OK || echo FAILED)"
```

---

## Emergency Contact

If all else fails:

1. Save your work (git commit)
2. Full system reboot
3. Check system logs: `journalctl -xe | grep -i 'pty\|tty\|fork'`
4. Check dmesg: `dmesg | grep -i 'pty\|tty\|resource'`

---

## Files Created

-   `/home/diablorain/Syn_OS/scripts/fix-terminal-environment.sh` - Full diagnostic
-   `/home/diablorain/Syn_OS/scripts/quick-terminal-fix.sh` - Quick fix
-   This document

Run from external terminal, NOT VS Code.
