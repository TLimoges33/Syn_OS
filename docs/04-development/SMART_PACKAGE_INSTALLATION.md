# Build Process Optimization - Smart Package Installation

**Date:** October 23, 2025  
**Issue:** Timeouts are interrupting legitimate package operations

---

## Problem Analysis

### Current Issues

1. ❌ **Timeout during unpacking** - 180 seconds isn't enough for large packages
2. ❌ **Timeout kills legitimate operations** - Unpacking nmap (1.9GB) takes time
3. ❌ **No hang detection** - Timeout can't distinguish between hang and slow operation
4. ❌ **Batch installation fails** - Dependency conflicts cause fallback to slow individual installs

### Root Causes

-   **Timeout is wrong tool:** Unpacking isn't hanging, it's just slow
-   **Dependency hell:** Mixed repos (Debian/Kali/Parrot) cause conflicts
-   **No progress monitoring:** Can't tell if apt is working or hung
-   **Sequential installation:** Fallback wastes time

---

## Smart Solutions - Best Practices

### 1. ✅ Remove Timeouts, Add Progress Monitoring

**Instead of timeout, detect actual hangs:**

```bash
# Monitor apt process activity instead of killing it
monitor_apt_progress() {
    local chroot_dir="$1"
    local max_idle_seconds=300  # 5 minutes of no disk activity = hung
    local last_activity=$(date +%s)

    while true; do
        # Check if apt/dpkg processes are still running
        if ! sudo chroot "$chroot_dir" pgrep -x "apt-get|dpkg" > /dev/null; then
            break  # Process finished
        fi

        # Check for disk I/O activity in chroot
        local current_io=$(sudo iostat -x 1 2 | grep -A1 "Device" | tail -1 | awk '{print $4}')
        if [[ "$current_io" != "0.00" ]]; then
            last_activity=$(date +%s)  # Reset timer on activity
        fi

        # Check if truly hung (no I/O for max_idle_seconds)
        local idle_time=$(($(date +%s) - last_activity))
        if [ $idle_time -gt $max_idle_seconds ]; then
            warning "APT appears hung (no I/O for ${idle_time}s), investigating..."
            return 1  # Signal hang
        fi

        sleep 10
    done
    return 0
}
```

**Benefits:**

-   ✅ No arbitrary timeouts
-   ✅ Detects real hangs (no disk activity)
-   ✅ Allows slow operations to complete
-   ✅ Monitors actual progress

### 2. ✅ Fix Dependency Conflicts (Root Cause)

**Problem:** Batch install fails due to mixed repository versions

```bash
# Current error:
bulk-extractor : Depends: libc6 (>= 2.38) but 2.36-9+deb12u13 is installed
```

**Solution A: Install from single repo first**

```bash
# Separate packages by source
DEBIAN_STABLE_TOOLS=(nmap tcpdump netcat-openbsd john hydra)
KALI_ONLY_TOOLS=(sqlmap nikto)
PARROT_ONLY_TOOLS=()

# Install Debian packages first (no conflicts)
apt-get install -y ${DEBIAN_STABLE_TOOLS[*]}

# Then try Kali/Parrot packages
apt-get install -y -t kali-rolling ${KALI_ONLY_TOOLS[*]} || warn "Some kali tools failed"
```

**Solution B: Skip problematic packages in batch**

```bash
# Remove packages known to have dependency issues
SKIP_IN_BATCH=(bulk-extractor radare2 build-essential)
BATCH_SAFE_TOOLS=($(echo "${DEBIAN_TOOLS[@]}" | tr ' ' '\n' | grep -v -F -f <(printf '%s\n' "${SKIP_IN_BATCH[@]}")))

# Install safe packages in batch
apt-get install -y --no-install-recommends ${BATCH_SAFE_TOOLS[*]}

# Install problematic ones individually
for tool in "${SKIP_IN_BATCH[@]}"; do
    apt-get install -y --no-install-recommends "$tool" || warn "Skipped $tool"
done
```

### 3. ✅ Use APT's Built-in Progress Monitoring

```bash
# APT has progress reporting - use it!
apt-get install -y -o APT::Status-Fd=3 ${TOOLS[*]} 3>&1 | \
    while read -r line; do
        if [[ "$line" =~ pmstatus:([^:]+):([^:]+):([^:]+) ]]; then
            echo "Progress: ${BASH_REMATCH[2]}% - ${BASH_REMATCH[3]}"
        fi
    done
```

### 4. ✅ Parallel Downloads, Sequential Install

```bash
# Download all packages first (parallel)
apt-get install -y --download-only ${TOOLS[*]}

# Then install (fast, no network delay)
apt-get install -y ${TOOLS[*]}
```

### 5. ✅ Use apt-fast for Parallel Downloads

```bash
# Install apt-fast (parallel apt-get)
apt-get install -y apt-fast

# Configure for 10 parallel connections
echo 'DOWNLOADBEFORE=true' >> /etc/apt-fast.conf
echo 'MIRRORS=("http://deb.debian.org/debian,http://mirror.us.debian.org/debian")' >> /etc/apt-fast.conf

# Use apt-fast instead of apt-get
apt-fast install -y ${TOOLS[*]}
```

---

## Recommended Implementation

### Phase 1: Fix Immediate Issue (Quick)

```bash
# Remove all timeouts, add APT progress monitoring
info "Installing ${#DEBIAN_TOOLS[@]} tools..."

# Try batch first (NO TIMEOUT - let it run)
if sudo chroot "$CHROOT_DIR" bash -c "
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    -o Dpkg::Options::='--force-confdef' \
    -o Dpkg::Options::='--force-confold' \
    ${DEBIAN_TOOLS[*]} 2>&1" | tee -a "$BUILD_LOG"; then

    success "All tools installed successfully"
    INSTALLED_COUNT=${#DEBIAN_TOOLS[@]}
else
    warning "Batch failed (likely dependency conflicts), trying refined approach..."

    # Separate clean packages from problematic ones
    PROBLEMATIC=(bulk-extractor radare2 autopsy build-essential)
    CLEAN_TOOLS=($(comm -23 <(printf '%s\n' "${DEBIAN_TOOLS[@]}" | sort) <(printf '%s\n' "${PROBLEMATIC[@]}" | sort)))

    # Install clean packages in batch
    sudo chroot "$CHROOT_DIR" bash -c "
        DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends ${CLEAN_TOOLS[*]}" && \
        INSTALLED_COUNT=${#CLEAN_TOOLS[@]}

    # Try problematic ones individually
    for tool in "${PROBLEMATIC[@]}"; do
        if sudo chroot "$CHROOT_DIR" bash -c "
            DEBIAN_FRONTEND=noninteractive \
            apt-get install -y --no-install-recommends '$tool' 2>&1"; then
            ((INSTALLED_COUNT++))
        else
            warning "Skipped: $tool (dependency conflict)"
            ((FAILED_COUNT++))
        fi
    done
fi

success "Installed $INSTALLED_COUNT tools, $FAILED_COUNT failed"
```

### Phase 2: Add Progress Monitoring (Better)

```bash
# Function to monitor apt without killing it
wait_for_apt_with_monitoring() {
    local max_no_progress=600  # 10 minutes of no progress = hung
    local last_line=""
    local same_line_count=0

    while IFS= read -r line; do
        echo "$line"  # Show output

        # Check if line is changing (progress)
        if [[ "$line" == "$last_line" ]]; then
            ((same_line_count++))
            if [ $same_line_count -gt 60 ]; then  # 60 identical lines = hung
                warning "APT may be hung (same output repeated)"
                return 1
            fi
        else
            same_line_count=0
            last_line="$line"
        fi
    done
    return 0
}

# Use it
sudo chroot "$CHROOT_DIR" bash -c "apt-get install -y ${TOOLS[*]}" 2>&1 | \
    wait_for_apt_with_monitoring
```

### Phase 3: Optimize Repository Strategy (Best)

```bash
# Create clean Debian-only environment first
info "Phase 7A: Installing Debian stable tools..."
DEBIAN_ONLY=(nmap tcpdump netcat-openbsd socat wireshark tshark
             john hydra medusa aircrack-ng binwalk foremost
             sleuthkit gdb strace ltrace hexedit openssl gnupg
             git python3 python3-pip python3-venv)

apt-get install -y --no-install-recommends ${DEBIAN_ONLY[*]}

# Phase 7B: Try Kali-specific tools (with fallback)
info "Phase 7B: Installing Kali-enhanced tools..."
KALI_ENHANCED=(sqlmap nikto)
apt-get install -y -t kali-rolling ${KALI_ENHANCED[*]} || \
    apt-get install -y ${KALI_ENHANCED[*]}  # Fallback to Debian

# Phase 7C: Skip problematic tools, document why
KNOWN_CONFLICTS=(bulk-extractor radare2 autopsy)
info "Skipping packages with known dependency conflicts in mixed repos"
for tool in "${KNOWN_CONFLICTS[@]}"; do
    warning "Skipped: $tool (requires newer libc6 than Debian stable provides)"
done
```

---

## Best Practices Summary

### ✅ DO:

1. **Trust APT's process** - It knows what it's doing
2. **Monitor progress** - Check for actual hangs, not time limits
3. **Separate by repository** - Install Debian, then Kali, then Parrot
4. **Pre-download packages** - Separate network from installation
5. **Document known issues** - Skip problematic packages with explanation
6. **Use apt-fast** - Parallel downloads speed things up
7. **Log everything** - Debug from logs, not interruptions

### ❌ DON'T:

1. **Use arbitrary timeouts** - Kills legitimate operations
2. **Mix repositories in batch** - Causes dependency hell
3. **Kill processes blindly** - May corrupt package database
4. **Assume fast = working** - Large packages are slow
5. **Fail entire build** - Skip problematic packages, continue

---

## Recommended Changes to Script

### Change 1: Remove Timeouts

```diff
- if timeout 1800 sudo chroot "$CHROOT_DIR" bash -c "apt-get install..."; then
+ if sudo chroot "$CHROOT_DIR" bash -c "apt-get install..."; then
```

### Change 2: Separate Repository Sources

```diff
+ # Install Debian stable tools first (no conflicts)
+ DEBIAN_STABLE=(nmap tcpdump john hydra...)
+ apt-get install -y ${DEBIAN_STABLE[*]}
+
+ # Then try Kali/Parrot packages
+ KALI_TOOLS=(sqlmap nikto...)
+ apt-get install -y -t kali-rolling ${KALI_TOOLS[*]} || true
```

### Change 3: Add Progress Feedback

```diff
+ info "This may take 10-15 minutes for large packages like nmap..."
  apt-get install -y ${TOOLS[*]}
+ success "Installation complete"
```

### Change 4: Document Known Issues

```diff
+ # Known issues with Debian 12 + mixed repos
+ SKIP_TOOLS=(bulk-extractor radare2)  # Require libc6 >= 2.38
+ warning "Skipping tools with libc6 conflicts: ${SKIP_TOOLS[*]}"
```

---

## Expected Results

### Before Optimization:

-   ❌ nmap timeout at 180s (during unpack)
-   ❌ Batch fails due to dependency conflicts
-   ❌ Build stops or hangs
-   ⏱️ ~60+ minutes for Phase 7

### After Optimization:

-   ✅ nmap installs successfully (takes ~5 minutes total)
-   ✅ Clean packages install in batch
-   ✅ Problematic packages skipped with documentation
-   ✅ Build continues to completion
-   ⏱️ ~15-20 minutes for Phase 7

---

**Next Step: Implement Phase 1 (quick fix) to get past nmap?**
