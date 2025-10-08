# SynOS v1.0 - VM Testing Guide
## Day 2 Final Validation

**ISO:** `synos-linux-1.0.0-YYYYMMDD-amd64.iso`
**Estimated Testing Time:** 2 hours
**VMs Required:** VirtualBox or VMware

---

## 🎯 Testing Objectives

1. ✅ Verify all Day 2 features work in live environment
2. ✅ Capture 8-10 professional screenshots
3. ✅ Document any bugs or issues
4. ✅ Validate keyboard shortcuts functionality
5. ✅ Test AI services integration

---

## 🖥️ VM Setup

### VirtualBox Configuration

```
Name: SynOS-v1.0-Test
Type: Linux
Version: Debian (64-bit)
Memory: 4096 MB (minimum 2048 MB)
CPU: 2 cores
Storage: 40 GB (dynamic)
Graphics: VMSVGA, 128 MB VRAM
Network: NAT (for internet access)
```

### Boot ISO

1. Mount `synos-linux-1.0.0-*.iso` as optical drive
2. Boot VM
3. Select "Live system (amd64)" from GRUB menu
4. Wait for desktop to load (1-2 minutes)

---

## ✅ Testing Checklist

### 1. Boot & Desktop (5 minutes)

**Test:**
- [ ] ISO boots successfully
- [ ] MATE desktop loads
- [ ] Plymouth boot splash shows (neural network animation)
- [ ] SynOS branding visible (wallpaper, theme)
- [ ] No critical errors on boot

**Screenshot:**
- [x] `01-desktop-first-boot.png` - Clean desktop after boot

**Notes:**
```
Boot time: _____ seconds
RAM usage: _____ MB
Visual issues: _____
```

---

### 2. Keyboard Shortcuts (15 minutes)

**Test Panel Toggles:**
- [ ] **F9** - Toggle all panels (distraction-free mode)
- [ ] **F10** - Toggle file tree (left panel)
- [ ] **F11** - Toggle AI chat (right panel)
- [ ] **F12** - Toggle terminal (dropdown or new window)

**Test System Shortcuts:**
- [ ] **Ctrl+Alt+Delete** - System Monitor launches
- [ ] **Ctrl+K** - Emergency kill dialog appears
- [ ] **Ctrl+Alt+Escape** - xkill cursor appears (click to kill window)

**Screenshot:**
- [x] `02-panel-toggles.png` - All three panels visible (F10, F11, F12 pressed)
- [x] `03-system-monitor.png` - MATE System Monitor (Ctrl+Alt+Delete)

**Notes:**
```
F9 working: Yes/No
F10 working: Yes/No
F11 working: Yes/No
F12 working: Yes/No
Ctrl+Alt+Delete: Yes/No
Ctrl+K: Yes/No
```

---

### 3. Jarvis CLI (20 minutes)

**Open Terminal** (F12 or Applications > Terminal)

**Test Commands:**

```bash
# 1. Status check
synos-jarvis status

# Expected: Shows 5 AI services status
# Screenshot: 04-jarvis-status.png
```

**Check:**
- [ ] `synos-jarvis` command found
- [ ] Colored output displays correctly
- [ ] Services listed: ai-daemon, consciousness-daemon, llm-engine, security-orchestrator, hardware-accel
- [ ] Status shows active/inactive for each

```bash
# 2. Query command
synos-jarvis query "What is SQL injection?"

# Expected: Connects to LLM engine, returns response
# Screenshot: 05-jarvis-query.png
```

**Check:**
- [ ] LLM engine connection attempts
- [ ] Error message if LLM offline (expected in live boot)
- [ ] Clear instructions for starting service

```bash
# 3. Context switching
synos-jarvis switch-client test_client

# Expected: Creates context file, shows confirmation
# Screenshot: 06-jarvis-context.png
```

**Check:**
- [ ] Prompts to create new context
- [ ] Context file created in `~/.synos/contexts/`
- [ ] Confirmation message displayed

```bash
# 4. Workflow management
synos-jarvis workflow save test_workflow

# Expected: Saves workflow state
```

**Check:**
- [ ] Workflow saved to `~/.synos/workflows/`
- [ ] Success message displayed

```bash
# 5. Learning insights
synos-jarvis learn

# Expected: Shows "No insights yet" or displays insights
```

**Check:**
- [ ] Command executes without error
- [ ] Appropriate message displayed

```bash
# 6. Help command
synos-jarvis help

# Expected: Shows help message with all commands
# Screenshot: 07-jarvis-help.png
```

**Check:**
- [ ] Help message displays
- [ ] All commands documented
- [ ] Examples included

**Notes:**
```
Commands working: ___/6
Errors encountered: _____
UI/UX issues: _____
```

---

### 4. AI Chat Panel (15 minutes)

**Launch AI Chat:**
- Press **F11** or run `/usr/local/bin/synos-ai-chat-panel`

**Test:**
- [ ] Window appears with "Jarvis AI Assistant" title
- [ ] Header shows 🤖 JARVIS branding
- [ ] Status indicator present (likely red/offline in live boot)
- [ ] Input field has placeholder text
- [ ] Send button visible
- [ ] Clear and Settings buttons visible

**Screenshot:**
- [x] `08-ai-chat-panel.png` - Chat window with UI elements

**Test Functionality:**
- [ ] Type message in input field
- [ ] Press Enter or click Send
- [ ] Error message if LLM engine offline (expected)
- [ ] Message appears in chat history
- [ ] Ctrl+Enter shortcut works
- [ ] Escape key hides panel

**Test Window Behavior:**
- [ ] F11 toggles visibility
- [ ] Window can be moved
- [ ] Window can be resized
- [ ] Clear button prompts confirmation

**Notes:**
```
UI rendering: Good/Issues
Keyboard shortcuts: Working/Broken
Error handling: Clear/Confusing
```

---

### 5. Emergency Kill System (10 minutes)

**Test Dry Run:**

```bash
# Terminal command
synos-emergency-kill --dry-run

# Expected: Shows what would be killed
# Screenshot: 09-emergency-kill-dryrun.png
```

**Check:**
- [ ] Command executes
- [ ] Lists processes that would be killed
- [ ] Shows protected processes
- [ ] Memory analysis displayed

**Test Keyboard Shortcut:**
- Press **Ctrl+K**

**Check:**
- [ ] Zenity dialog appears
- [ ] Warning message clear
- [ ] Protected processes listed
- [ ] Can cancel safely

**Screenshot:**
- [x] `10-emergency-kill-dialog.png` - Confirmation dialog

**Note:** DO NOT actually kill processes unless necessary!

**Notes:**
```
Dry run working: Yes/No
Dialog appearance: Good/Issues
Protected list accurate: Yes/No
```

---

### 6. MATE Panel Configuration (10 minutes)

**Test:**
- [ ] Top panel exists (menu bar)
- [ ] GSettings schema compiled (no errors in logs)
- [ ] Panels have SynOS theme colors
- [ ] Workspace switcher shows 4 workspaces: Main, Recon, Exploit, Report

**Check Files:**

```bash
# Verify GSettings
ls -la /usr/share/glib-2.0/schemas/90_synos-mate-panels.gschema.override
ls -la /usr/share/glib-2.0/schemas/gschemas.compiled

# Check scripts
ls -la /usr/local/bin/synos-toggle-*
ls -la /usr/local/bin/synos-emergency-kill
```

**Screenshot:**
- [x] `11-mate-desktop-config.png` - Desktop showing MATE customizations

**Notes:**
```
Schema compiled: Yes/No
Toggle scripts present: Yes/No
Theme applied: Yes/No
```

---

### 7. AI Services (15 minutes)

**Check Services:**

```bash
# List AI service packages
dpkg -l | grep synos

# Expected output:
# synos-ai-daemon
# synos-consciousness-daemon
# synos-hardware-accel
# synos-llm-engine
# synos-security-orchestrator
```

**Check:**
- [ ] All 5 .deb packages installed
- [ ] Systemd services present

```bash
# Check systemd services
systemctl list-units | grep synos

# Try starting LLM engine
sudo systemctl start synos-llm-engine
sudo systemctl status synos-llm-engine
```

**Check:**
- [ ] Services can be started
- [ ] No immediate crashes
- [ ] Logs accessible

**Screenshot:**
- [x] `12-ai-services-status.png` - Service status output

**Notes:**
```
Packages installed: ___/5
Services starting: Yes/No/Partial
Errors in logs: _____
```

---

### 8. File System & Tools (10 minutes)

**Check SynOS Files:**

```bash
# Verify Day 2 files
ls -la /usr/local/bin/synos-*
ls -la /usr/share/glib-2.0/schemas/*synos*
ls -la /etc/xdg/autostart/*synos*
```

**Check:**
- [ ] Jarvis CLI present and executable
- [ ] AI chat panel present and executable
- [ ] Emergency kill present and executable
- [ ] Toggle scripts present
- [ ] GSettings schema present
- [ ] Autostart entries present

**Check Security Tools:**

```bash
# Sample 10 security tools
which nmap
which burpsuite
which metasploit
which wireshark
which sqlmap
which john
which hashcat
which aircrack-ng
which gobuster
which nikto
```

**Check:**
- [ ] Security tools accessible
- [ ] PATH configured correctly

**Notes:**
```
SynOS files: All present/Some missing
Security tools: Working/Issues
```

---

### 9. Performance & Resources (5 minutes)

**Monitor Resources:**

```bash
# Open system monitor
mate-system-monitor &

# Or use CLI
free -h
top -bn1 | head -20
df -h
```

**Check:**
- [ ] RAM usage reasonable (<2GB for live boot)
- [ ] CPU idle when not active
- [ ] Disk space sufficient
- [ ] No swap thrashing

**Screenshot:**
- [x] `13-system-resources.png` - System monitor showing resource usage

**Notes:**
```
RAM usage: _____ MB
CPU idle: _____ %
Boot time: _____ seconds
Responsiveness: Excellent/Good/Slow
```

---

### 10. Documentation & Help (5 minutes)

**Check:**

```bash
# Find documentation
ls -la /usr/share/doc/synos*/
cat /usr/share/doc/synos/KEYBOARD_SHORTCUTS.md | head -50
```

**Check:**
- [ ] Documentation installed
- [ ] Keyboard shortcuts reference accessible
- [ ] README present

**Test:**

```bash
synos-jarvis help
man synos 2>/dev/null || echo "Man page not installed (OK for v1.0)"
```

**Screenshot:**
- [x] `14-documentation.png` - Help/documentation displayed

---

## 📸 Screenshot Checklist

Capture these screenshots for Day 3 demo materials:

1. ✅ **01-desktop-first-boot.png** - Clean desktop after boot
2. ✅ **02-panel-toggles.png** - All three panels visible
3. ✅ **03-system-monitor.png** - MATE System Monitor
4. ✅ **04-jarvis-status.png** - `synos-jarvis status` output
5. ✅ **05-jarvis-query.png** - `synos-jarvis query` example
6. ✅ **06-jarvis-context.png** - Client context switching
7. ✅ **07-jarvis-help.png** - Help message
8. ✅ **08-ai-chat-panel.png** - Chat window UI
9. ✅ **09-emergency-kill-dryrun.png** - Dry run output
10. ✅ **10-emergency-kill-dialog.png** - Confirmation dialog
11. ✅ **11-mate-desktop-config.png** - MATE customizations
12. ✅ **12-ai-services-status.png** - Service status
13. ✅ **13-system-resources.png** - Resource usage
14. ✅ **14-documentation.png** - Help/docs

**Save screenshots to:** `~/Pictures/synos-v1-testing/`

---

## 🐛 Bug Documentation

### Issue Template

For each bug found, document:

```
**Bug #**: ___
**Severity**: Critical/High/Medium/Low
**Component**: Jarvis CLI/AI Chat/Panels/Other
**Description**: _____
**Steps to Reproduce**:
1. _____
2. _____
3. _____

**Expected**: _____
**Actual**: _____
**Screenshots**: _____
**Workaround**: _____
**Fix Priority**: v1.0/v1.1/v1.2
```

### Common Expected Issues

**Expected (Not Bugs):**
- LLM engine offline in live boot (no persistent storage)
- AI services inactive (need manual start in live boot)
- Conversation history empty (live session)
- Context files temporary (live session)

**These are normal for live boot and will work in installed system.**

---

## ✅ Test Results Summary

### Overall Status

- **Boot**: Pass/Fail
- **Keyboard Shortcuts**: ___/7 working
- **Jarvis CLI**: ___/6 commands working
- **AI Chat Panel**: Pass/Fail
- **Emergency Kill**: Pass/Fail
- **MATE Panels**: Pass/Fail
- **AI Services**: ___/5 installed
- **Performance**: Excellent/Good/Poor

### Critical Issues Found

1. _____
2. _____
3. _____

### Non-Critical Issues Found

1. _____
2. _____
3. _____

### Recommendations

- [ ] **SHIP v1.0**: All critical features work, minor issues acceptable
- [ ] **FIX CRITICAL BUGS**: 1-2 day delay to fix showstoppers
- [ ] **DEFER TO v1.1**: Issues are minor, ship and iterate

---

## 📋 Next Steps (Post-Testing)

### If Testing Passes (Recommended)

1. **Organize Screenshots** (15 min)
   - Move to `docs/screenshots/`
   - Rename with descriptive names
   - Create index file

2. **Update Documentation** (15 min)
   - Add screenshots to README
   - Update any inaccurate documentation
   - Note any workarounds

3. **Create Issues** (15 min)
   - GitHub issues for non-critical bugs
   - Label as v1.1 enhancements
   - Close Day 2 milestone

4. **Mark Day 2 Complete** ✅
   - Update TODO.md
   - Create Day 2 final report
   - Proceed to Day 3

### If Critical Issues Found

1. **Document Issues**
   - Detailed bug reports
   - Reproduction steps
   - Proposed fixes

2. **Assess Impact**
   - Can users work around it?
   - Does it block core functionality?
   - Risk of shipping with issue?

3. **Decision Point**
   - Fix immediately (1-2 days)
   - Ship with known issue (document workaround)
   - Defer to v1.1 (if non-critical)

---

## 🎯 Success Criteria

**Minimum for v1.0 Ship:**
- ✅ ISO boots successfully
- ✅ Desktop loads without errors
- ✅ 5+ keyboard shortcuts work
- ✅ Jarvis CLI executes (3+ commands)
- ✅ AI Chat Panel launches
- ✅ Emergency kill safe mode works
- ✅ No data loss or security issues
- ✅ Performance acceptable (boot <2 min, RAM <2GB)

**If all criteria met: SHIP v1.0** 🚀

---

**Testing Start Time:** _____
**Testing End Time:** _____
**Total Duration:** _____
**Tester:** _____
**ISO Version:** _____
**Result:** PASS / FAIL / CONDITIONAL

---

**Next:** Day 3 - Demo Video & Documentation Polish
