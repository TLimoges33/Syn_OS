#!/bin/bash
# Script to setup live system auto-configuration for SynOS
# This creates a first-boot script that runs on initial system startup

set -e

CHROOT=/home/diablorain/Syn_OS/build/synos-v1.0/work/chroot

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🔧 CONFIGURING LIVE SYSTEM AUTO-SETUP                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create scripts directory
echo "[1/5] Creating scripts directory..."
mkdir -p $CHROOT/opt/synos/scripts

# Create the first-boot setup script
echo "[2/5] Creating first-boot-setup.sh..."
cat > $CHROOT/opt/synos/scripts/first-boot-setup.sh << 'ENDSCRIPT'
#!/bin/bash
# SynOS First Boot Setup Script
# Runs once on first system boot to configure live system elements

SETUP_MARKER="/var/lib/synos-first-boot-complete"

# Check if already run
if [ -f "$SETUP_MARKER" ]; then
    echo "First boot setup already completed."
    exit 0
fi

echo "🔧 SynOS First Boot Configuration Starting..."

# Function to create desktop shortcut
create_desktop_shortcut() {
    local name="$1"
    local exec="$2"
    local icon="$3"
    local terminal="$4"
    local file="$HOME/Desktop/${name}.desktop"

    cat > "$file" << DESKTOPEOF
[Desktop Entry]
Type=Application
Name=${name}
Exec=${exec}
Icon=${icon}
Terminal=${terminal}
Categories=System;Utility;
DESKTOPEOF

    chmod +x "$file"
    chown $USER:$USER "$file"
    gio set "$file" "metadata::trusted" true 2>/dev/null || true
}

# [1] Create Desktop Shortcuts
echo "[1/4] Creating desktop shortcuts..."
if [ -d "$HOME/Desktop" ]; then
    create_desktop_shortcut "Install SynOS" "calamares" "system-software-install" "false"
    create_desktop_shortcut "Terminal" "qterminal" "utilities-terminal" "false"
    create_desktop_shortcut "Firefox ESR" "firefox-esr" "firefox-esr" "false"
    create_desktop_shortcut "SynOS Welcome" "python3 /opt/synos/scripts/welcome.py" "help-about" "false"
    echo "✅ Desktop shortcuts created"
else
    echo "⚠️  Desktop directory not found, skipping shortcuts"
fi

# [2] Organize Application Menu
echo "[2/4] Organizing application menu..."

# Update security tools categories
for desktop_file in /usr/share/applications/{burpsuite,metasploit,wireshark,nmap,zaproxy}.desktop; do
    if [ -f "$desktop_file" ]; then
        sudo sed -i 's/Categories=.*/Categories=SynOS-Security;Network;/' "$desktop_file" 2>/dev/null || true
    fi
done

# Update AI tools categories
for desktop_file in /usr/share/applications/{jupyter-lab,spyder}.desktop; do
    if [ -f "$desktop_file" ]; then
        sudo sed -i 's/Categories=.*/Categories=SynOS-AI;Development;Science;/' "$desktop_file" 2>/dev/null || true
    fi
done

echo "✅ Application menu organized"

# [3] Configure Desktop Environment
echo "[3/4] Configuring desktop environment..."

# Set theme preferences for current user
if [ -d "$HOME/.config" ]; then
    mkdir -p $HOME/.config/qt5ct
    mkdir -p $HOME/.config/gtk-3.0

    # GTK theme
    cat > $HOME/.config/gtk-3.0/settings.ini << GTKEOF
[Settings]
gtk-theme-name=ARK-Dark
gtk-icon-theme-name=ara
gtk-font-name=Noto Sans 10
GTKEOF

    echo "✅ Desktop environment configured"
else
    echo "⚠️  .config directory not found"
fi

# [4] Show welcome message on first login
echo "[4/4] Setting up welcome screen..."
if command -v zenity >/dev/null 2>&1; then
    (sleep 5 && zenity --info --width=500 --title="Welcome to SynOS v1.0" --text="<big><b>Welcome to SynOS v1.0</b></big>\n\n<b>Security &amp; AI Operating System</b>\n\n<b>Quick Start:</b>\n• 500+ Security Tools installed\n• AI Integration: Claude, Gemini, GPT, Ollama\n• Tutorials in: ~/SynOS-Tutorials/\n• Documentation: /opt/synos/docs/\n\n<b>Credentials:</b>\nroot / superroot\nuser / user\n\n<b>Install:</b> Double-click 'Install SynOS' on desktop\n\nEnjoy your secure environment! 🛡️") &
fi

# Mark setup as complete
sudo touch "$SETUP_MARKER"
echo "✅ First boot setup completed successfully!"
echo "🎉 SynOS is ready to use!"
ENDSCRIPT

chmod +x $CHROOT/opt/synos/scripts/first-boot-setup.sh
echo "✅ First-boot script created"

# Create systemd service
echo "[3/5] Creating systemd service..."
cat > $CHROOT/etc/systemd/system/synos-first-boot.service << 'ENDSERVICE'
[Unit]
Description=SynOS First Boot Configuration
After=graphical.target
ConditionPathExists=!/var/lib/synos-first-boot-complete

[Service]
Type=oneshot
ExecStart=/opt/synos/scripts/first-boot-setup.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
ENDSERVICE

echo "✅ Systemd service created"

# Enable the service
echo "[4/5] Enabling first-boot service..."
chroot $CHROOT systemctl enable synos-first-boot.service 2>&1 | grep -v "Created symlink" | grep -v "systemd is not running" || true
echo "✅ Service enabled"

# Create a simple welcome script
echo "[5/5] Creating welcome script..."
cat > $CHROOT/opt/synos/scripts/welcome.py << 'ENDWELCOME'
#!/usr/bin/env python3
"""
SynOS Welcome Script
Displays system information and quick start guide
"""

import subprocess
import sys

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
except ImportError:
    print("Error: tkinter not available")
    sys.exit(1)

def get_system_info():
    """Get basic system information"""
    info = {}
    try:
        info['kernel'] = subprocess.check_output(['uname', '-r']).decode().strip()
    except:
        info['kernel'] = 'Unknown'

    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemTotal' in line:
                    mem_kb = int(line.split()[1])
                    info['memory'] = f"{mem_kb // 1024} MB"
                    break
    except:
        info['memory'] = 'Unknown'

    return info

class WelcomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SynOS v1.0 - Welcome")
        self.root.geometry("700x600")

        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title = ttk.Label(main_frame, text="🛡️ Welcome to SynOS v1.0",
                         font=('Sans', 16, 'bold'))
        title.grid(row=0, column=0, pady=10)

        subtitle = ttk.Label(main_frame,
                           text="Security & AI Operating System",
                           font=('Sans', 12))
        subtitle.grid(row=1, column=0, pady=5)

        # Info text
        info_text = scrolledtext.ScrolledText(main_frame, width=80, height=30,
                                              wrap=tk.WORD)
        info_text.grid(row=2, column=0, pady=10)

        # Get system info
        sys_info = get_system_info()

        content = f"""
SYSTEM INFORMATION
==================
Kernel: {sys_info['kernel']}
Memory: {sys_info['memory']}

FEATURES
========
✅ 500+ Security Tools
   • Metasploit Framework
   • Burp Suite, OWASP ZAP
   • Wireshark, Nmap, Aircrack-ng
   • All Kali + ParrotOS tools

✅ AI Integration
   • Claude, Gemini, GPT, Ollama CLIs
   • PyTorch 2.8.0, TensorFlow 2.20.0
   • Jupyter Lab 4.4.9
   • 58 Python AI packages

✅ ParrotOS Theme
   • ARK-Dark + ara icon theme
   • Custom GRUB & Plymouth
   • Professional appearance

QUICK START
===========
📚 Tutorials:
   ~/SynOS-Tutorials/
   • 01-Getting-Started.ipynb
   • 02-AI-Security-Analysis.ipynb

📖 Documentation:
   /opt/synos/docs/
   • TOOLS.md - Complete tool catalog
   • CONFIGURATION.md - System setup
   • ~/Desktop/QUICK-START.txt

🛠️  Sample Projects:
   /opt/synos/demos/
   • pentest/ - Web app scanning
   • ai-security/ - Log analysis

CREDENTIALS
===========
root / superroot
user / user

INSTALLATION
============
To install SynOS permanently:
1. Double-click "Install SynOS" on desktop
2. Follow Calamares installer
3. Reboot and enjoy!

SUPPORT
=======
Documentation: /opt/synos/docs/
GitHub: https://github.com/yourusername/SynOS

Enjoy your secure environment! 🔐
        """

        info_text.insert(1.0, content)
        info_text.config(state=tk.DISABLED)

        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=root.destroy)
        close_btn.grid(row=3, column=0, pady=10)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = WelcomeWindow(root)
    root.mainloop()
ENDWELCOME

chmod +x $CHROOT/opt/synos/scripts/welcome.py
echo "✅ Welcome script created"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         ✅ LIVE SYSTEM AUTO-SETUP CONFIGURED                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Summary:"
echo "   • First-boot script: /opt/synos/scripts/first-boot-setup.sh"
echo "   • Systemd service: synos-first-boot.service (enabled)"
echo "   • Welcome script: /opt/synos/scripts/welcome.py"
echo ""
echo "On first boot, the system will automatically:"
echo "   ✓ Create desktop shortcuts (Install, Terminal, Firefox, Welcome)"
echo "   ✓ Organize application menu categories"
echo "   ✓ Configure desktop environment theme"
echo "   ✓ Display welcome message"
echo ""
echo "✅ Live system tasks configuration complete!"
