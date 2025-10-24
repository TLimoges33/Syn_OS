#!/bin/bash
# ONE-LINE EMERGENCY FIX
# Copy and paste this entire command into an EXTERNAL terminal (Ctrl+Alt+T)

echo "=== EMERGENCY TERMINAL FIX ===" && \
sudo rm -f /dev/null && sudo mknod -m 666 /dev/null c 1 3 && \
sudo rm -f /dev/ptmx && sudo mknod -m 666 /dev/ptmx c 5 2 && \
sudo chmod 666 /dev/null /dev/zero /dev/ptmx /dev/random /dev/urandom && \
sudo mount -t devpts devpts /dev/pts -o rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 2>/dev/null || true && \
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && \
pkill -9 code && pkill -9 electron && sleep 3 && \
echo "✓ Devices fixed" && ls -la /dev/null /dev/ptmx && \
echo "✓ Caches cleared" && free -h && \
echo "✓ VS Code killed" && \
echo "" && \
echo "NOW: 1) Wait 5 seconds  2) Restart VS Code  3) Test terminal" && \
echo "If still broken, run: sudo reboot"
