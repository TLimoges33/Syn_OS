# IMMEDIATE ACTION REQUIRED

## Your VS Code environment is critically broken

**Symptom**: `forkpty(3) failed` - cannot create terminals
**Cause**: PTY device corruption + resource exhaustion

---

## QUICK FIX (5 minutes)

### 1. Open External Terminal

Press `Ctrl+Alt+T` (NOT in VS Code)

### 2. Run This One Command

```bash
sudo rm -f /dev/null && sudo mknod -m 666 /dev/null c 1 3 && sudo rm -f /dev/ptmx && sudo mknod -m 666 /dev/ptmx c 5 2 && sudo chmod 666 /dev/null /dev/zero /dev/ptmx && sudo mount -t devpts devpts /dev/pts -o rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 2>/dev/null || true && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && pkill -9 code && sleep 5
```

Password: `superadmin33`

### 3. Restart VS Code

Close this window, wait 10 seconds, then reopen VS Code.

---

## If Still Broken

Run permanent fix:

```bash
cd /home/diablorain/Syn_OS
sudo bash scripts/fix-terminal-environment.sh
```

Then add to `/etc/security/limits.conf`:

```
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
```

Then **reboot**:

```bash
sudo reboot
```

---

## Full Documentation

See: `/home/diablorain/Syn_OS/docs/CRITICAL_TERMINAL_FIX.md`

---

**DO THIS NOW - Your IDE cannot function until fixed**
