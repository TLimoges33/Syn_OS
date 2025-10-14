# 🔴 SynOS Automated System Health Check

**Comprehensive post-boot validation in 5-10 minutes**

---

## 📋 Overview

The **SynOS System Health Check** is an automated diagnostic tool that validates all components of your SynOS installation. It runs 40+ tests across 10 categories and generates both terminal output and an HTML report.

**Perfect for:**
- ✅ Verifying ISO integrity after build
- ✅ Troubleshooting system issues
- ✅ Quick validation before demos
- ✅ CI/CD testing pipelines
- ✅ User support diagnostics

---

## 🚀 Quick Start

### Method 1: Desktop Launcher (GUI)

1. **Open Application Menu**
2. **Navigate to:** System → SynOS System Check
3. **Click to run** (will prompt for sudo password)
4. **Wait 5-10 minutes** for tests to complete
5. **View results** in terminal and HTML report

### Method 2: Command Line

```bash
# Run system health check
sudo synos-system-check

# Results will display in terminal
# HTML report saved to: ~/.synos/system-checks/
```

---

## 📊 What It Tests

### 1. System Boot & Kernel (5 tests)
- ✅ Kernel version (Linux 6.5+)
- ✅ System architecture (x86_64)
- ✅ Boot mode (BIOS/UEFI)
- ✅ Systemd status
- ✅ System uptime

### 2. Network Connectivity (4 tests)
- ✅ Network interfaces detected
- ✅ IP address assigned
- ✅ Internet connectivity
- ✅ DNS resolution

### 3. Security Tools Sample (10 tests)
**Tests critical tools from 500+ available:**
- nmap - Network scanner
- metasploit-framework - Exploitation framework
- wireshark - Network analyzer
- john - Password cracker
- aircrack-ng - Wireless security
- sqlmap - SQL injection
- burpsuite - Web security
- hydra - Password attack
- nikto - Web scanner
- masscan - Port scanner

### 4. AI Services (3 tests)
- ✅ AI daemon service file exists
- ✅ Service status (active or installed)
- ✅ NATS message bus available

### 5. Desktop Environment (4 tests)
- ✅ Display server running (X11)
- ✅ Desktop environment (XFCE/MATE)
- ✅ Window manager active
- ✅ Terminal emulator available

### 6. Red Phoenix Branding (5 tests)
- ✅ Phoenix logos present
- ✅ Red Phoenix wallpapers
- ✅ Plymouth boot theme
- ✅ GRUB theme
- ✅ GTK theme (SynOS Dark Red)

### 7. Package Management (2 tests)
- ✅ APT package manager working
- ✅ Repositories configured (Debian, ParrotOS, Kali)

### 8. Performance & Resources (3 tests)
- ✅ Memory usage (< 80% used)
- ✅ CPU load average
- ✅ Disk space (< 90% used)

### 9. Documentation (2 tests)
- ✅ Local documentation available
- ✅ Man pages present

### 10. Known Limitations (4 tests)
- ⚠️ Desktop AI stubs (expected, non-critical)
- ⚠️ AI Runtime FFI bindings (expected, v1.2)
- ⚠️ Network stack completion (expected, v1.1)
- ⚠️ Custom Rust kernel (expected, v2.0)

**Total:** 40+ automated tests

---

## 📈 Understanding Results

### Test Status Indicators

**✅ PASS (Green)**
- Test passed successfully
- Component functioning correctly
- No action needed

**⚠️ WARN (Yellow)**
- Test passed with warnings
- Component may have minor issues
- Usually non-critical
- Check details for context

**❌ FAIL (Red)**
- Test failed
- Component not functioning
- Requires investigation
- May need troubleshooting

### Success Criteria

**PASS:**
- 0 failed tests
- 80%+ success rate
- System fully operational

**CONDITIONAL PASS:**
- 0 failed tests
- Some warnings present
- System functional with minor issues

**FAIL:**
- 1+ failed tests
- Critical components broken
- Requires troubleshooting

---

## 📄 HTML Report

### Report Location
```bash
~/.synos/system-checks/system-check-YYYYMMDD-HHMMSS.html
```

### Report Contents
- ✅ All test results (color-coded)
- ✅ Detailed information per test
- ✅ Summary statistics
- ✅ Timestamp and system info
- ✅ Professional red/black theme

### Opening Report
```bash
# Automatically opens in Firefox (if available)
firefox ~/.synos/system-checks/system-check-*.html

# Or navigate to the file manually
```

---

## 🔧 Troubleshooting

### Common Issues

**Problem:** "Command not found: synos-system-check"

**Solution:**
```bash
# Check if installed
ls -la /usr/bin/synos-system-check

# Re-install if missing
sudo cp /usr/share/synos/tools/synos-system-check /usr/bin/
sudo chmod +x /usr/bin/synos-system-check
```

---

**Problem:** Multiple failed tests

**Solution:**
1. Review HTML report for details
2. Check system logs: `journalctl -b`
3. Verify internet connectivity
4. Re-run test after fixes
5. Report persistent failures

---

**Problem:** Cannot open HTML report

**Solution:**
```bash
# Install Firefox if missing
sudo apt install firefox-esr

# Or use alternative browser
chromium ~/.synos/system-checks/system-check-*.html
```

---

**Problem:** Tests take too long (> 15 minutes)

**Solution:**
- Check network speed (tool downloads may timeout)
- Verify system resources (low RAM can slow tests)
- Ensure system is not under heavy load

---

## 💡 Advanced Usage

### Running Specific Test Categories

The script runs all tests by default, but you can modify it for specific categories:

```bash
# Edit the script
sudo nano /usr/share/synos/tools/synos-system-check

# Comment out test sections you don't need
# Example: Comment out "Security Tools" section to speed up tests
```

### Automated Testing (CI/CD)

```bash
# Run in non-interactive mode
sudo synos-system-check > /tmp/health-check.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "Health check PASSED"
else
    echo "Health check FAILED"
    exit 1
fi
```

### Parsing Results Programmatically

```bash
# Extract passed tests count
grep "✅ PASS" ~/.synos/system-checks/system-check-*.html | wc -l

# Extract failed tests
grep "❌ FAIL" ~/.synos/system-checks/system-check-*.html

# Check overall status
if grep -q "SYSTEM CHECK PASSED" /tmp/health-check.log; then
    echo "All good!"
fi
```

---

## 🎯 Use Cases

### 1. Post-Installation Validation
```bash
# After installing SynOS to disk
sudo synos-system-check

# Verify all components functional
# Confirm 80%+ pass rate
```

### 2. Pre-Demo Checklist
```bash
# Before client demo or presentation
sudo synos-system-check

# Ensure no critical failures
# Review any warnings
```

### 3. Troubleshooting User Issues
```bash
# User reports problems
# Ask them to run health check
sudo synos-system-check

# Send HTML report for analysis
# Identify specific failed components
```

### 4. Development Testing
```bash
# After making system changes
sudo synos-system-check

# Compare before/after results
# Verify no regressions introduced
```

---

## 📊 Performance Benchmarks

**Typical Run Times:**
- Fast system (SSD, 16GB RAM): 5-7 minutes
- Standard system (HDD, 8GB RAM): 8-10 minutes
- Slow system (old hardware): 12-15 minutes

**Resource Usage:**
- CPU: 5-20% (spikes during tool checks)
- Memory: +200-300MB (temporarily)
- Disk: Minimal (report file < 1MB)

---

## 🔄 Interpreting Known Limitations

The health check tests for **known v1.0 limitations**:

### Desktop AI Stubs (Expected ⚠️)
- **Status:** 63 stub functions present
- **Impact:** None (desktop fully functional)
- **Action:** No action needed
- **Fix:** v1.1 (November 2025)

### AI Runtime FFI (Expected ⚠️)
- **Status:** TensorFlow Lite bindings incomplete
- **Impact:** Limited (AI framework operational)
- **Action:** Use Python-based AI tools
- **Fix:** v1.2 (December 2025)

### Network Stack (Expected ⚠️)
- **Status:** TCP state machine 85% complete
- **Impact:** Minimal (basic networking works)
- **Action:** None needed for standard use
- **Fix:** v1.1 (November 2025)

### Custom Rust Kernel (Expected ⚠️)
- **Status:** Not default boot option
- **Impact:** None (Linux 6.5 fully functional)
- **Action:** Use Debian kernel (default)
- **Fix:** v2.0 (Q1 2026)

**These warnings are normal and documented in v1.0 release notes.**

---

## 🙋 FAQ

**Q: How often should I run the health check?**
A: After installation, before demos, when troubleshooting, or monthly for maintenance.

**Q: Can I run it without sudo?**
A: Some tests require root access. Run with sudo for complete results.

**Q: Does it modify my system?**
A: No, it only reads system state and generates reports.

**Q: Can I automate it with cron?**
A: Yes! Add to crontab for weekly checks:
```bash
0 2 * * 0 /usr/bin/synos-system-check > /tmp/weekly-health.log 2>&1
```

**Q: What if I get 100% pass rate?**
A: Excellent! Your SynOS installation is fully functional. The 4 "known limitations" warnings are expected and documented.

**Q: Can I share the HTML report?**
A: Yes! It contains no sensitive information, only system configuration details.

---

## 🔗 Related Documentation

- [Installation Guide](../01-getting-started/INSTALLATION.md)
- [Troubleshooting Guide](../02-user-guide/TROUBLESHOOTING.md)
- [Release Notes v1.0](../06-project-status/RELEASE_NOTES_v1.0.md)
- [Known Limitations](../06-project-status/RELEASE_NOTES_v1.0.md#known-limitations-v10)

---

## 🤝 Contributing

Found a bug in the health check? Want to add more tests?

**See:** [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

<div align="center">

# 🔴 Red Phoenix v1.0 - System Health Check 🔴

**Automated · Comprehensive · Fast · Reliable**

*5-10 minutes to full system validation*

</div>

---

**Last Updated:** October 12, 2025  
**Version:** 1.0.0  
**Maintainer:** SynOS Team
