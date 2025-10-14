# Live System Configuration Guide

## Tasks That Require Live System

These tasks cannot be completed in chroot and must be done after booting the ISO:

### 1. Application Menu Organization

**Location:** User's desktop environment menu (MATE/XFCE)

**Current State:**
- All tools are installed
- Desktop entry files exist
- Tools are scattered in default locations

**Required Actions:**

1. **Create SynOS Tools Main Menu:**
   ```bash
   sudo mkdir -p /usr/share/desktop-directories
   sudo cat > /usr/share/desktop-directories/synos-tools.directory << 'EOF'
   [Desktop Entry]
   Name=SynOS Tools
   Icon=applications-system
   Type=Directory
   EOF
   ```

2. **Organize into Categories:**
   - Information Gathering
   - Vulnerability Analysis
   - Web Applications
   - Password Attacks
   - Wireless Attacks
   - Exploitation
   - Post Exploitation
   - Forensics
   - Reverse Engineering
   - Sniffing & Spoofing
   - Reporting Tools

3. **Update Menu Cache:**
   ```bash
   sudo update-desktop-database
   sudo update-menus
   ```

**Why This Requires Live System:**
- Menu systems need active session bus
- Desktop environment must be running
- User settings need to be applied
- Icon cache needs active X11/Wayland

### 2. Desktop Shortcuts

**Current State:**
- Quick start guide on Desktop
- No executable shortcuts yet

**Required Shortcuts:**

1. **Terminal Shortcut:**
   ```bash
   cp /usr/share/applications/mate-terminal.desktop ~/Desktop/
   chmod +x ~/Desktop/mate-terminal.desktop
   ```

2. **Firefox Shortcut:**
   ```bash
   cp /usr/share/applications/firefox-esr.desktop ~/Desktop/
   chmod +x ~/Desktop/firefox-esr.desktop
   ```

3. **SynOS Tools Launcher:**
   ```bash
   cat > ~/Desktop/synos-tools.desktop << 'EOF'
   [Desktop Entry]
   Name=SynOS Tools
   Comment=Launch Security Tools Browser
   Exec=python3 /opt/synos/tools/launcher.py
   Icon=applications-system
   Terminal=false
   Type=Application
   Categories=Security;
   EOF
   chmod +x ~/Desktop/synos-tools.desktop
   ```

4. **Install SynOS (Calamares):**
   ```bash
   cp /usr/share/applications/calamares.desktop ~/Desktop/
   chmod +x ~/Desktop/calamares.desktop
   ```

**Why This Requires Live System:**
- Desktop folder needs active user session
- Permissions must be set for logged-in user
- Desktop environment must render shortcuts
- Executable flag requires user context

### 3. First Boot Automation

**Recommended Approach:**

Create first-boot script that runs once on initial login:

```bash
sudo cat > /etc/profile.d/synos-first-boot.sh << 'EOF'
#!/bin/bash
# SynOS First Boot Configuration

if [ ! -f ~/.synos-configured ]; then
    echo "=== Welcome to SynOS! ==="
    echo "Running first-boot configuration..."
    
    # Create desktop shortcuts
    if [ -d ~/Desktop ]; then
        cp /usr/share/applications/mate-terminal.desktop ~/Desktop/ 2>/dev/null
        cp /usr/share/applications/firefox-esr.desktop ~/Desktop/ 2>/dev/null
        chmod +x ~/Desktop/*.desktop 2>/dev/null
    fi
    
    # Update desktop database
    update-desktop-database ~/.local/share/applications 2>/dev/null
    
    # Mark as configured
    touch ~/.synos-configured
    
    echo "First-boot configuration complete!"
fi
EOF

sudo chmod +x /etc/profile.d/synos-first-boot.sh
```

### 4. Theme Verification

**Already Complete in Chroot:**
- ✅ ARK-Dark theme copied
- ✅ ara icons copied
- ✅ mate cursor configured
- ✅ GTK settings in /etc/skel/

**Verification on Live System:**
```bash
# Check theme is applied
gsettings get org.gnome.desktop.interface gtk-theme
gsettings get org.gnome.desktop.interface icon-theme
gsettings get org.gnome.desktop.interface cursor-theme
```

**Should return:**
- gtk-theme: 'ARK-Dark'
- icon-theme: 'ara'
- cursor-theme: 'mate'

### 5. Testing Checklist

After booting live system, verify:

- [ ] Desktop shortcuts appear and are executable
- [ ] Application menu shows organized categories
- [ ] Terminal opens with custom prompt (cyan "SynOS")
- [ ] AI commands work (ask-claude, ask-gemini, etc.)
- [ ] Theme is correct (ARK-Dark + ara)
- [ ] Firewall is active (ufw status)
- [ ] Auditing is running (systemctl status auditd)
- [ ] Jupyter Lab launches (jupyter lab)
- [ ] Demo scripts are executable
- [ ] Tutorial notebooks open

### 6. Post-Installation Tasks

**User Must Do:**
1. Change default passwords
2. Set up AI API keys (if using cloud AI)
3. Configure personal preferences
4. Update system (`sudo apt update && sudo apt upgrade`)

### 7. Known Limitations

**Cannot Be Done in Chroot:**
- Application menu organization (requires session bus)
- Desktop shortcut creation (requires user session)
- Theme preview (requires display server)
- Service status checks (requires systemd running)

**Already Handled:**
- ✅ Tool installation
- ✅ Theme copying
- ✅ Configuration files
- ✅ User accounts
- ✅ Firewall rules
- ✅ Audit rules
- ✅ Documentation

## Summary

**Completed in Chroot (Phases 1-5):**
- All tools installed
- All AI frameworks installed
- Theme files copied
- Configuration applied
- Documentation created
- Users configured
- Security hardened

**Requires Live System:**
- Application menu organization
- Desktop shortcuts setup
- First-boot automation
- Live testing

**Recommendation:**
Add first-boot script to handle desktop shortcuts automatically on first login. Application menu organization can be handled by desktop environment's natural categorization of .desktop files.

---

*This guide documents the distinction between chroot-buildable items (complete) and live-system-only items (pending).*
