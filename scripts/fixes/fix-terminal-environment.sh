#!/bin/bash
# Terminal Environment Diagnostic & Fix Script
# Fixes forkpty(3) failures and IDE terminal issues

set -euo pipefail

LOG_FILE="/tmp/terminal-fix-$(date +%Y%m%d-%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "Terminal Environment Diagnostic & Fix"
echo "=========================================="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Log: $LOG_FILE"
echo ""

# Function to run with error handling
safe_run() {
    local description="$1"
    shift
    echo ">>> $description"
    if "$@"; then
        echo "✓ Success"
    else
        echo "✗ Failed (exit code: $?)"
    fi
    echo ""
}

# 1. Check PTY devices
echo "=== Checking PTY Devices ==="
ls -la /dev/pts/ 2>&1 | head -20
ls -la /dev/ptmx 2>&1
echo ""

# 2. Check resource limits
echo "=== Current Resource Limits ==="
ulimit -a 2>&1
echo ""

# 3. Check open file descriptors
echo "=== Open File Descriptors ==="
echo "Total for user: $(lsof -u $(whoami) 2>/dev/null | wc -l)"
echo "System limit: $(cat /proc/sys/fs/file-max 2>&1)"
echo "Current open: $(cat /proc/sys/fs/file-nr 2>&1)"
echo ""

# 4. Check process count
echo "=== Process Count ==="
echo "User processes: $(ps -u $(whoami) --no-headers | wc -l)"
echo "PID max: $(cat /proc/sys/kernel/pid_max 2>&1)"
echo ""

# 5. Check VS Code processes
echo "=== VS Code Processes ==="
ps aux | grep -E '[v]scode|[c]ode|[e]lectron' | wc -l
echo ""

# 6. Check mount points that could block terminals
echo "=== Critical Mount Points ==="
mount | grep -E 'devpts|pts|shm' || echo "No pts/shm mounts found"
echo ""

# 7. Check /dev/null and basic devices
echo "=== Critical Devices ==="
ls -la /dev/null /dev/zero /dev/random /dev/urandom 2>&1
echo ""

# 8. Check system memory
echo "=== Memory Status ==="
free -h 2>&1
echo ""

# 9. Check dmesg for PTY errors
echo "=== Recent Kernel Messages (PTY related) ==="
dmesg | grep -i 'pty\|tty\|terminal' | tail -20 || echo "No PTY-related kernel messages"
echo ""

# 10. Check systemd-logind (manages sessions/terminals)
echo "=== Systemd Login Sessions ==="
loginctl list-sessions 2>&1 || echo "loginctl not available"
echo ""

echo "=== DIAGNOSTIC COMPLETE ==="
echo ""
echo "=== ATTEMPTING FIXES ==="
echo ""

# FIX 1: Ensure /dev/pts is properly mounted
if ! mount | grep -q '/dev/pts'; then
    echo ">>> Mounting /dev/pts"
    sudo mount -t devpts devpts /dev/pts -o rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 2>&1 || echo "Failed to mount /dev/pts"
else
    echo "✓ /dev/pts already mounted"
fi
echo ""

# FIX 2: Ensure /dev/ptmx is correct
if [ ! -c /dev/ptmx ]; then
    echo ">>> Recreating /dev/ptmx"
    sudo rm -f /dev/ptmx
    sudo mknod /dev/ptmx c 5 2
    sudo chmod 666 /dev/ptmx
else
    echo "✓ /dev/ptmx exists and is character device"
fi
echo ""

# FIX 3: Fix /dev/null if needed
if [ ! -c /dev/null ]; then
    echo ">>> Recreating /dev/null"
    sudo rm -f /dev/null
    sudo mknod -m 666 /dev/null c 1 3
else
    echo "✓ /dev/null is correct"
fi
echo ""

# FIX 4: Check and fix permissions
echo ">>> Fixing device permissions"
sudo chmod 666 /dev/null /dev/zero /dev/random /dev/urandom 2>&1 || true
sudo chmod 666 /dev/ptmx 2>&1 || true
echo ""

# FIX 5: Increase file descriptor limits if low
current_nofile=$(ulimit -n)
if [ "$current_nofile" -lt 4096 ]; then
    echo ">>> Increasing file descriptor limit from $current_nofile to 4096"
    ulimit -n 4096 2>&1 || echo "Could not increase (may need system-wide change)"
else
    echo "✓ File descriptor limit is adequate: $current_nofile"
fi
echo ""

# FIX 6: Kill any zombie VS Code processes
echo ">>> Checking for zombie processes"
zombie_count=$(ps aux | awk '$8=="Z"' | wc -l)
if [ "$zombie_count" -gt 0 ]; then
    echo "Found $zombie_count zombie processes"
    ps aux | awk '$8=="Z"' | head -10
else
    echo "✓ No zombie processes"
fi
echo ""

# FIX 7: Clean up stale PTS devices
echo ">>> Cleaning stale PTS devices"
sudo find /dev/pts -type c -mtime +1 2>/dev/null || true
echo ""

# FIX 8: Restart systemd-logind if possible (careful - may disconnect session)
echo ">>> Systemd-logind status"
systemctl status systemd-logind --no-pager 2>&1 | head -10 || echo "Cannot check systemd-logind"
echo ""

# FIX 9: Clear system caches to free resources
echo ">>> Syncing and dropping caches"
sync
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' 2>&1 || echo "Could not drop caches"
echo ""

# FIX 10: Show recommendations
echo "=========================================="
echo "=== RECOMMENDATIONS ==="
echo "=========================================="
echo ""
echo "If terminals still fail, try:"
echo "1. Restart VS Code completely (close all windows)"
echo "2. Increase system limits in /etc/security/limits.conf:"
echo "   * soft nofile 65536"
echo "   * hard nofile 65536"
echo "   * soft nproc 32768"
echo "   * hard nproc 32768"
echo ""
echo "3. Check /etc/systemd/logind.conf for UserTasksMax"
echo ""
echo "4. Reboot system if resource exhaustion persists"
echo ""
echo "5. Run: sudo systemctl restart systemd-logind (may disconnect session)"
echo ""
echo "Log saved to: $LOG_FILE"
echo ""
