#!/bin/bash

# SynOS First Boot Setup Script
# Configures the complete security environment on first boot

SYNOS_DIR="/opt/synos"
USER_HOME="/home/user"

configure_user_environment() {
    echo "[SynOS] Configuring user environment..."

    # Create security tools menu structure
    mkdir -p "$USER_HOME/.local/share/applications/Security"

    # Setup custom aliases for security tools
    cat >> "$USER_HOME/.bashrc" << 'EOF'

# SynOS Security Aliases
alias nmap-scan='nmap -sS -sV -O'
alias nmap-vuln='nmap --script vuln'
alias metasploit='msfconsole'
alias burp='java -jar /opt/burpsuite/burpsuite_community.jar'
alias zaproxy='/opt/zaproxy/zap.sh'
alias ghidra='/opt/ghidra/ghidraRun'
alias volatility='python3 /usr/share/volatility3/vol.py'
alias sqlmap='python3 /usr/share/sqlmap/sqlmap.py'
alias wfuzz='wfuzz'
alias gobuster='gobuster'
alias nikto='nikto'
alias hydra='hydra'
alias john='john'
alias hashcat='hashcat'
alias aircrack='aircrack-ng'
alias wireshark='wireshark'
alias tcpdump='tcpdump'

# Kali-style prompt
export PS1='\[\033[01;31m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# Add custom tools to PATH
export PATH="$PATH:/opt/burpsuite:/opt/zaproxy:/opt/ghidra"
EOF

    # Setup desktop environment
    cat > "$USER_HOME/.config/autostart/synos-welcome.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SynOS Welcome
Exec=/opt/synos/synos-welcome.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
}

create_security_menu() {
    echo "[SynOS] Creating security tools menu..."

    # Network Analysis submenu
    mkdir -p "$USER_HOME/.local/share/applications/Security/Network"

    cat > "$USER_HOME/.local/share/applications/Security/Network/Wireshark.desktop" << EOF
[Desktop Entry]
Name=Wireshark
Comment=Network Protocol Analyzer
Exec=wireshark
Icon=wireshark
Terminal=false
Type=Application
Categories=Security;Network;
EOF

    cat > "$USER_HOME/.local/share/applications/Security/Network/Nmap.desktop" << EOF
[Desktop Entry]
Name=Nmap (Zenmap)
Comment=Network Discovery and Security Auditing
Exec=zenmap
Icon=zenmap
Terminal=false
Type=Application
Categories=Security;Network;
EOF

    # Web Application Testing
    mkdir -p "$USER_HOME/.local/share/applications/Security/Web"

    cat > "$USER_HOME/.local/share/applications/Security/Web/Burp-Suite.desktop" << EOF
[Desktop Entry]
Name=Burp Suite
Comment=Web Application Security Testing
Exec=java -jar /opt/burpsuite/burpsuite_community.jar
Icon=burpsuite
Terminal=false
Type=Application
Categories=Security;Web;
EOF

    cat > "$USER_HOME/.local/share/applications/Security/Web/OWASP-ZAP.desktop" << EOF
[Desktop Entry]
Name=OWASP ZAP
Comment=Web Application Security Scanner
Exec=/opt/zaproxy/zap.sh
Icon=zaproxy
Terminal=false
Type=Application
Categories=Security;Web;
EOF

    # Reverse Engineering
    mkdir -p "$USER_HOME/.local/share/applications/Security/Reverse"

    cat > "$USER_HOME/.local/share/applications/Security/Reverse/Ghidra.desktop" << EOF
[Desktop Entry]
Name=Ghidra
Comment=Software Reverse Engineering Framework
Exec=/opt/ghidra/ghidraRun
Icon=ghidra
Terminal=false
Type=Application
Categories=Security;Reverse;
EOF

    cat > "$USER_HOME/.local/share/applications/Security/Reverse/Radare2.desktop" << EOF
[Desktop Entry]
Name=Radare2
Comment=Reverse Engineering Framework
Exec=mate-terminal -e "r2 -"
Icon=radare2
Terminal=false
Type=Application
Categories=Security;Reverse;
EOF

    # Set proper permissions
    chmod +x "$USER_HOME"/.local/share/applications/Security/**/*.desktop
    chown -R user:user "$USER_HOME/.local/share/applications"
}

setup_wordlists() {
    echo "[SynOS] Setting up wordlists and dictionaries..."

    # Create wordlists directory
    mkdir -p /usr/share/wordlists

    # Download common wordlists
    cd /usr/share/wordlists

    # SecLists
    git clone https://github.com/danielmiessler/SecLists.git seclists

    # Download rockyou.txt if not present
    if [ ! -f rockyou.txt ]; then
        wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
    fi

    # Create symlinks for easy access
    ln -sf /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt ./dirlist-medium.txt
    ln -sf /usr/share/wordlists/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt ./top1m-passwords.txt

    # Set proper permissions
    chmod -R 644 /usr/share/wordlists/*
}

configure_services() {
    echo "[SynOS] Configuring security services..."

    # Enable SSH for remote access
    systemctl enable ssh
    systemctl start ssh

    # Configure PostgreSQL for Metasploit
    systemctl enable postgresql
    systemctl start postgresql
    sudo -u postgres createuser msf -P -S -R -D
    sudo -u postgres createdb -O msf msf

    # Initialize Metasploit database
    msfdb init

    # Enable Docker for container security testing
    systemctl enable docker
    systemctl start docker
    usermod -aG docker user

    # Configure ClamAV
    freshclam
    systemctl enable clamav-daemon
    systemctl start clamav-daemon

    # Setup fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
}

create_welcome_script() {
    echo "[SynOS] Creating welcome script..."

    cat > "/opt/synos/synos-welcome.sh" << 'EOF'
#!/bin/bash

# SynOS Welcome and Information Script

show_welcome() {
    zenity --info --width=600 --height=400 --title="Welcome to SynOS" --text="
<b>Welcome to SynOS - Advanced Security Distribution</b>

SynOS includes:
• 500+ Security Tools (BlackArch and Kali equivalent)
• Kali Linux VM (Auto-configured)
• BlackArch VM (Auto-configured)
• AI-Enhanced Security Testing
• Complete Penetration Testing Suite

<b>Quick Start:</b>
• VMs: Applications → System Tools → Virtual Machine Manager
• Security Tools: Applications → Security
• Terminal: Ctrl+Alt+T
• Web Tools: Burp Suite, OWASP ZAP available in Security menu

<b>VM Status:</b>
$(virsh list --all | grep -E '(kali|blackarch)' || echo 'VMs are being configured in background...')

<b>Documentation:</b>
• Local: /opt/synos/docs/
• Online: https://synos-security.org/docs

Happy Hacking!
"

    # Don't show again checkbox
    if zenity --question --text="Show this welcome message on startup?"; then
        # Keep autostart enabled
        echo "Welcome will show on next boot"
    else
        # Disable autostart
        rm -f /home/user/.config/autostart/synos-welcome.desktop
    fi
}

show_welcome
EOF

    chmod +x "/opt/synos/synos-welcome.sh"
}

main() {
    echo "[SynOS] Starting first boot configuration..."

    # Create SynOS directory
    mkdir -p "$SYNOS_DIR"

    configure_user_environment
    create_security_menu
    setup_wordlists
    configure_services
    create_welcome_script

    # Start VM setup in background
    nohup /opt/synos/vm-autosetup.sh > /var/log/synos-vm-setup.log 2>&1 &

    echo "[SynOS] First boot configuration completed!"

    # Reboot notification
    sudo -u user DISPLAY=:0 notify-send "SynOS Ready" "Security environment configured. VMs are being prepared in background." --icon=security-high
}

# Run main function
main "$@"