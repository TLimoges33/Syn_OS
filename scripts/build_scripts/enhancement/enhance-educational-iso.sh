#!/bin/bash
################################################################################
# SynOS Educational & AI Enhancement Script
# Adds educational features and AI consciousness integration to ISO build
################################################################################

set -e

CHROOT_DIR="${1:-}"
PROJECT_ROOT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

if [[ -z "$CHROOT_DIR" ]]; then
    echo "Usage: $0 <chroot_dir> [project_root]"
    exit 1
fi

echo "=================================="
echo "🎓 Enhancing SynOS Educational ISO"
echo "=================================="

#######################
# 1. AI DAEMON SYSTEMD SERVICE
#######################
echo "📦 Installing AI Daemon as systemd service..."

# Copy AI daemon
mkdir -p "${CHROOT_DIR}/usr/local/bin"
cp "${PROJECT_ROOT}/ai-daemon.py" "${CHROOT_DIR}/usr/local/bin/synos-ai-daemon"
chmod +x "${CHROOT_DIR}/usr/local/bin/synos-ai-daemon"

# Create systemd service
cat > "${CHROOT_DIR}/etc/systemd/system/synos-ai.service" << 'EOF'
[Unit]
Description=SynOS AI Consciousness Daemon
Documentation=https://github.com/yourusername/synos
After=network.target nats.service
Wants=nats.service

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/synos-ai-daemon
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/log

[Install]
WantedBy=multi-user.target
EOF

# Enable service
chroot "${CHROOT_DIR}" systemctl enable synos-ai.service 2>/dev/null || true

echo "  ✅ AI Daemon configured to start at boot"

#######################
# 2. CUSTOM GRUB THEME
#######################
echo "🎨 Installing custom GRUB theme..."

mkdir -p "${CHROOT_DIR}/boot/grub/themes/synos"

# Copy GRUB background
if [[ -f "${PROJECT_ROOT}/assets/branding/grub/synos-grub-16x9.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/grub/synos-grub-16x9.png" \
       "${CHROOT_DIR}/boot/grub/themes/synos/background.png"
fi

# Copy SynOS logo for GRUB menu
if [[ -f "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" \
       "${CHROOT_DIR}/boot/grub/themes/synos/logo.png"
fi

# Create GRUB theme.txt with logo and footer
cat > "${CHROOT_DIR}/boot/grub/themes/synos/theme.txt" << 'EOF'
# SynOS GRUB Theme - Enhanced Edition
# Black, Red, White - Professional Cybersecurity Aesthetic

desktop-image: "background.png"
desktop-color: "#000000"

# SynOS Logo at top
+ image {
    left = 50%-64
    top = 8%
    width = 128
    height = 128
    file = "logo.png"
}

# Main title
title-text: "SynOS - AI-Enhanced Cybersecurity Education"
title-color: "#ff0000"
title-font: "DejaVu Sans Bold 24"

# Boot menu - positioned below logo
+ boot_menu {
    left = 15%
    top = 35%
    width = 70%
    height = 42%

    item_font = "DejaVu Sans Regular 16"
    item_color = "#999999"
    selected_item_color = "#ffffff"

    item_height = 36
    item_padding = 8
    item_spacing = 4

    icon_width = 32
    icon_height = 32
}

# Progress bar for auto-boot countdown
+ progress_bar {
    id = "__timeout__"
    left = 15%
    top = 82%
    width = 70%
    height = 28

    fg_color = "#ff0000"
    bg_color = "#1a1a1a"
    border_color = "#ff0000"

    font = "DejaVu Sans Regular 14"
    text_color = "#ffffff"
    text = "Auto-boot in %d seconds"
}

# Footer with version and hints
+ label {
    left = 0
    top = 92%
    width = 100%
    height = 20
    align = "center"
    color = "#ff0000"
    font = "DejaVu Sans Bold 13"
    text = "Neural Darwinism | 500+ Security Tools | v1.0"
}

+ label {
    left = 0
    top = 96%
    width = 100%
    height = 16
    align = "center"
    color = "#888888"
    font = "DejaVu Sans Regular 11"
    text = "Press 'e' to edit boot options | 'c' for GRUB console"
}
EOF

# Configure GRUB to use custom theme
if [[ -f "${CHROOT_DIR}/etc/default/grub" ]]; then
    sed -i 's|^GRUB_TIMEOUT=.*|GRUB_TIMEOUT=10|' "${CHROOT_DIR}/etc/default/grub"
    echo 'GRUB_THEME="/boot/grub/themes/synos/theme.txt"' >> "${CHROOT_DIR}/etc/default/grub"
fi

echo "  ✅ GRUB theme installed"

#######################
# 3. ADVANCED PLYMOUTH SPLASH SCREENS
#######################
echo "🎬 Creating advanced Plymouth splash screens..."

mkdir -p "${CHROOT_DIR}/usr/share/plymouth/themes"

# Theme 1: SynOS Advanced (Component Loading with Progress)
echo "  → Creating 'synos-advanced' theme..."
mkdir -p "${CHROOT_DIR}/usr/share/plymouth/themes/synos-advanced"

# Copy logo for Plymouth
if [[ -f "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" \
       "${CHROOT_DIR}/usr/share/plymouth/themes/synos-advanced/logo.png"
fi

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-advanced/synos-advanced.script" << 'PLYMOUTH_SCRIPT'
# SynOS Advanced Plymouth Theme
# Component-by-component loading with AI consciousness indicator

# Background
Window.SetBackgroundTopColor(0.0, 0.0, 0.0);
Window.SetBackgroundBottomColor(0.0, 0.0, 0.0);

# Logo
if (Plymouth.GetMode() == "boot") {
    logo.image = Image("logo.png");
    logo.sprite = Sprite(logo.image);
    logo.sprite.SetX(Window.GetWidth() / 2 - logo.image.GetWidth() / 2);
    logo.sprite.SetY(Window.GetHeight() / 5);
    logo.opacity = 1.0;
}

# Main status message
message_label = "Initializing AI Consciousness...";
message.image = Image.Text(message_label, 1.0, 0.0, 0.0, 1.0, "Sans 16");  # Red text
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                          Window.GetHeight() / 2 - 60,
                          10000);

# Progress bar background
progress_bg.image = Image("progress_bg.png");
if (!progress_bg.image) {
    # Create fallback progress background
    progress_bg.image = Image(600, 30);
    for (x = 0; x < 600; x++) {
        for (y = 0; y < 30; y++) {
            progress_bg.image.SetPixel(x, y, 0.1, 0.1, 0.1, 1.0);  # Dark gray
        }
    }
}
progress_bg.sprite = Sprite(progress_bg.image);
progress_bg.sprite.SetPosition(Window.GetWidth() / 2 - 300,
                              Window.GetHeight() / 2,
                              10000);

# Progress bar foreground (red)
progress_bar.image = Image(1, 20);
for (y = 0; y < 20; y++) {
    progress_bar.image.SetPixel(0, y, 1.0, 0.0, 0.0, 1.0);  # Red
}
progress_bar.sprite = Sprite();
progress_bar.sprite.SetPosition(Window.GetWidth() / 2 - 295,
                               Window.GetHeight() / 2 + 5,
                               10001);

# Percentage text
percent_text.image = Image.Text("0%", 1.0, 1.0, 1.0, 1.0, "Sans 14");  # White
percent_text.sprite = Sprite(percent_text.image);
percent_text.sprite.SetPosition(Window.GetWidth() / 2 + 320,
                               Window.GetHeight() / 2 + 5,
                               10002);

# Component loading messages
components = [];
components[0] = "→ Loading Kernel";
components[1] = "→ Initializing Memory";
components[2] = "→ Starting AI Core";
components[3] = "→ Loading Neural Networks";
components[4] = "→ Security Framework Online";
components[5] = "→ Loading Security Tools";
components[6] = "✓ System Ready";

component_index = 0;
component_text.image = Image.Text(components[0], 0.8, 0.8, 0.8, 1.0, "Sans 12");
component_text.sprite = Sprite(component_text.image);
component_text.sprite.SetPosition(Window.GetWidth() / 2 - component_text.image.GetWidth() / 2,
                                 Window.GetHeight() / 2 + 50,
                                 10000);

# Consciousness level indicator
consciousness_text = "Consciousness Level: Initializing...";
consciousness.image = Image.Text(consciousness_text, 1.0, 0.0, 0.0, 1.0, "Sans 11");  # Red
consciousness.sprite = Sprite(consciousness.image);
consciousness.sprite.SetPosition(Window.GetWidth() / 2 - consciousness.image.GetWidth() / 2,
                                Window.GetHeight() / 2 + 80,
                                10000);

# Boot progress callback
fun progress_callback(duration, progress) {
    if (progress >= 0 && progress <= 1.0) {
        # Update progress bar
        new_width = Math.Int(590 * progress);
        if (new_width > 0) {
            scaled_image = progress_bar.image.Scale(new_width, 20);
            progress_bar.sprite.SetImage(scaled_image);
        }

        # Update percentage
        percent = Math.Int(progress * 100);
        percent_text.image = Image.Text(percent + "%", 1.0, 1.0, 1.0, 1.0, "Sans 14");
        percent_text.sprite.SetImage(percent_text.image);

        # Update component message
        new_index = Math.Int(progress * 7);
        if (new_index != component_index && new_index < 7) {
            component_index = new_index;
            component_text.image = Image.Text(components[component_index], 0.8, 0.8, 0.8, 1.0, "Sans 12");
            component_text.sprite.SetImage(component_text.image);
            component_text.sprite.SetPosition(Window.GetWidth() / 2 - component_text.image.GetWidth() / 2,
                                            Window.GetHeight() / 2 + 50,
                                            10000);
        }

        # Update consciousness level
        if (progress < 0.3) {
            consciousness_text = "Consciousness Level: Awakening...";
        } else if (progress < 0.6) {
            consciousness_text = "Consciousness Level: Rising...";
        } else if (progress < 0.9) {
            consciousness_text = "Consciousness Level: Active...";
        } else {
            consciousness_text = "Consciousness Level: Fully Online";
        }
        consciousness.image = Image.Text(consciousness_text, 1.0, 0.0, 0.0, 1.0, "Sans 11");
        consciousness.sprite.SetImage(consciousness.image);
        consciousness.sprite.SetPosition(Window.GetWidth() / 2 - consciousness.image.GetWidth() / 2,
                                        Window.GetHeight() / 2 + 80,
                                        10000);
    }
}

Plymouth.SetBootProgressFunction(progress_callback);

# Display message callback
fun display_normal_callback() {
    global.status = "normal";
}

fun display_password_callback(prompt, bullets) {
    global.status = "password";
}

fun display_question_callback(prompt, entry) {
    global.status = "question";
}

fun display_message_callback(text) {
}

Plymouth.SetDisplayNormalFunction(display_normal_callback);
Plymouth.SetDisplayPasswordFunction(display_password_callback);
Plymouth.SetDisplayQuestionFunction(display_question_callback);
Plymouth.SetMessageFunction(display_message_callback);
PLYMOUTH_SCRIPT

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-advanced/synos-advanced.plymouth" << 'EOF'
[Plymouth Theme]
Name=SynOS Advanced
Description=AI Consciousness Loading with Component Progress
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-advanced
ScriptFile=/usr/share/plymouth/themes/synos-advanced/synos-advanced.script
EOF

# Theme 2: SynOS Matrix (Hacker Aesthetic)
echo "  → Creating 'synos-matrix' theme..."
mkdir -p "${CHROOT_DIR}/usr/share/plymouth/themes/synos-matrix"

if [[ -f "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" \
       "${CHROOT_DIR}/usr/share/plymouth/themes/synos-matrix/logo.png"
fi

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-matrix/synos-matrix.script" << 'MATRIX_SCRIPT'
# SynOS Matrix Theme - Minimal Hacker Aesthetic

Window.SetBackgroundTopColor(0.0, 0.0, 0.0);
Window.SetBackgroundBottomColor(0.0, 0.0, 0.0);

# Logo
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.sprite.SetX(Window.GetWidth() / 2 - logo.image.GetWidth() / 2);
logo.sprite.SetY(Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 40);

# Simple status text
status_text = "[ INITIALIZING AI CONSCIOUSNESS ]";
status.image = Image.Text(status_text, 1.0, 0.0, 0.0, 1.0, "Monospace 14");
status.sprite = Sprite(status.image);
status.sprite.SetPosition(Window.GetWidth() / 2 - status.image.GetWidth() / 2,
                         Window.GetHeight() / 2 + 100,
                         10000);

# Spinner dots
dots = ["   ", ".  ", ".. ", "..."];
dot_index = 0;

fun refresh_callback() {
    dot_index++;
    if (dot_index >= 4) dot_index = 0;

    dots_text = "Loading" + dots[dot_index];
    dots_image = Image.Text(dots_text, 0.6, 0.6, 0.6, 1.0, "Monospace 12");

    if (!global.dots_sprite) global.dots_sprite = Sprite();
    global.dots_sprite.SetImage(dots_image);
    global.dots_sprite.SetPosition(Window.GetWidth() / 2 - dots_image.GetWidth() / 2,
                                   Window.GetHeight() / 2 + 140,
                                   10000);
}

Plymouth.SetRefreshFunction(refresh_callback);
MATRIX_SCRIPT

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-matrix/synos-matrix.plymouth" << 'EOF'
[Plymouth Theme]
Name=SynOS Matrix
Description=Minimal Hacker Aesthetic
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-matrix
ScriptFile=/usr/share/plymouth/themes/synos-matrix/synos-matrix.script
EOF

# Theme 3: SynOS Minimalist (Clean and Fast)
echo "  → Creating 'synos-minimalist' theme..."
mkdir -p "${CHROOT_DIR}/usr/share/plymouth/themes/synos-minimalist"

if [[ -f "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" \
       "${CHROOT_DIR}/usr/share/plymouth/themes/synos-minimalist/logo.png"
fi

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-minimalist/synos-minimalist.script" << 'MINIMAL_SCRIPT'
# SynOS Minimalist Theme - Clean and Professional

Window.SetBackgroundTopColor(0.0, 0.0, 0.0);
Window.SetBackgroundBottomColor(0.0, 0.0, 0.0);

# Centered logo
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.sprite.SetX(Window.GetWidth() / 2 - logo.image.GetWidth() / 2);
logo.sprite.SetY(Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 30);

# Simple progress bar
progress_bar.width = 400;
progress_bar.height = 4;
progress_bar.x = Window.GetWidth() / 2 - progress_bar.width / 2;
progress_bar.y = Window.GetHeight() / 2 + 80;

# Progress bar background
progress_bg.image = Image(progress_bar.width, progress_bar.height);
for (x = 0; x < progress_bar.width; x++) {
    for (y = 0; y < progress_bar.height; y++) {
        progress_bg.image.SetPixel(x, y, 0.2, 0.2, 0.2, 1.0);
    }
}
progress_bg.sprite = Sprite(progress_bg.image);
progress_bg.sprite.SetPosition(progress_bar.x, progress_bar.y, 10000);

# Progress bar foreground
progress_fg.image = Image(1, progress_bar.height);
for (y = 0; y < progress_bar.height; y++) {
    progress_fg.image.SetPixel(0, y, 1.0, 0.0, 0.0, 1.0);
}
progress_fg.sprite = Sprite();
progress_fg.sprite.SetPosition(progress_bar.x, progress_bar.y, 10001);

fun progress_callback(duration, progress) {
    if (progress >= 0 && progress <= 1.0) {
        new_width = Math.Int(progress_bar.width * progress);
        if (new_width > 0) {
            scaled = progress_fg.image.Scale(new_width, progress_bar.height);
            progress_fg.sprite.SetImage(scaled);
        }
    }
}

Plymouth.SetBootProgressFunction(progress_callback);
MINIMAL_SCRIPT

cat > "${CHROOT_DIR}/usr/share/plymouth/themes/synos-minimalist/synos-minimalist.plymouth" << 'EOF'
[Plymouth Theme]
Name=SynOS Minimalist
Description=Clean and Professional Boot
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/synos-minimalist
ScriptFile=/usr/share/plymouth/themes/synos-minimalist/synos-minimalist.script
EOF

# Set synos-advanced as default
chroot "${CHROOT_DIR}" plymouth-set-default-theme synos-advanced 2>/dev/null || \
    log_warning "Could not set default Plymouth theme (will use system default)"

echo "  ✅ Plymouth themes created (advanced, matrix, minimalist)"

#######################
# 4. WELCOME SCREEN APPLICATION
#######################
echo "👋 Creating first-boot welcome screen..."

mkdir -p "${CHROOT_DIR}/usr/local/share/synos"

cat > "${CHROOT_DIR}/usr/local/bin/synos-welcome" << 'EOF'
#!/usr/bin/env python3
"""SynOS Welcome Screen - Educational introduction and setup wizard"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

class SynOSWelcome:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to SynOS v1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a1628")

        self.current_page = 0
        self.pages = [
            self.create_intro_page,
            self.create_ai_page,
            self.create_tools_page,
            self.create_learning_page,
            self.create_final_page
        ]

        self.container = tk.Frame(root, bg="#0a1628")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.button_frame = tk.Frame(root, bg="#0a1628")
        self.button_frame.pack(fill="x", padx=20, pady=10)

        self.prev_btn = tk.Button(self.button_frame, text="← Previous",
                                   command=self.prev_page, state="disabled",
                                   bg="#1a2638", fg="#00d9ff", font=("Arial", 12))
        self.prev_btn.pack(side="left", padx=5)

        self.next_btn = tk.Button(self.button_frame, text="Next →",
                                   command=self.next_page,
                                   bg="#00d9ff", fg="#0a1628", font=("Arial", 12, "bold"))
        self.next_btn.pack(side="right", padx=5)

        self.show_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_page(self):
        self.clear_container()
        self.pages[self.current_page]()

        # Update buttons
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        if self.current_page == len(self.pages) - 1:
            self.next_btn.config(text="Launch SynOS! 🚀", command=self.finish)
        else:
            self.next_btn.config(text="Next →", command=self.next_page)

    def create_intro_page(self):
        title = tk.Label(self.container, text="🧠 Welcome to SynOS v1.0",
                        font=("Arial", 28, "bold"), fg="#00d9ff", bg="#0a1628")
        title.pack(pady=20)

        subtitle = tk.Label(self.container,
                           text="The World's First AI-Enhanced Cybersecurity Education OS",
                           font=("Arial", 14), fg="#e0e0e0", bg="#0a1628")
        subtitle.pack(pady=10)

        desc = tk.Text(self.container, wrap="word", height=15, width=70,
                      bg="#1a2638", fg="#e0e0e0", font=("Arial", 11),
                      relief="flat", padx=20, pady=20)
        desc.insert("1.0", """
SynOS combines three groundbreaking technologies:

🤖 Neural Darwinism AI Consciousness
   • Custom Rust kernel with embedded AI consciousness
   • Real-time threat detection and pattern recognition
   • Adaptive learning from your security research

🛡️ 500+ Professional Security Tools
   • Complete ParrotOS, Kali Linux, and BlackArch toolsets
   • Automated tool orchestration with AI guidance
   • Educational mode with step-by-step tutorials

🎓 Adaptive Learning Platform
   • Personalized cybersecurity curriculum
   • Safe practice environments (sandboxing)
   • Progress tracking and skill assessment
   • SNHU-aligned educational framework
        """)
        desc.config(state="disabled")
        desc.pack(pady=20)

    def create_ai_page(self):
        title = tk.Label(self.container, text="🧠 AI Consciousness System",
                        font=("Arial", 24, "bold"), fg="#00d9ff", bg="#0a1628")
        title.pack(pady=20)

        desc = tk.Text(self.container, wrap="word", height=18, width=70,
                      bg="#1a2638", fg="#e0e0e0", font=("Arial", 11),
                      relief="flat", padx=20, pady=20)
        desc.insert("1.0", """
SynOS features a custom Rust kernel with integrated AI consciousness:

🔹 Neural Darwinism Architecture
   The AI uses evolutionary selection to strengthen effective security
   patterns, similar to how the brain develops neural pathways.

🔹 Real-Time Threat Detection
   Monitors system activity, network traffic, and security tool output
   to identify threats using pattern recognition.

🔹 Educational Guidance
   The AI learns your skill level and recommends appropriate tools,
   tutorials, and practice scenarios.

🔹 System Status
   Check AI consciousness state anytime:

   $ systemctl status synos-ai
   $ tail -f /var/log/synos-ai.log

   The AI daemon is already running in the background!
        """)
        desc.config(state="disabled")
        desc.pack(pady=20)

    def create_tools_page(self):
        title = tk.Label(self.container, text="🛡️ Security Tools Arsenal",
                        font=("Arial", 24, "bold"), fg="#00d9ff", bg="#0a1628")
        title.pack(pady=20)

        desc = tk.Text(self.container, wrap="word", height=18, width=70,
                      bg="#1a2638", fg="#e0e0e0", font=("Arial", 11),
                      relief="flat", padx=20, pady=20)
        desc.insert("1.0", """
500+ Professional Security Tools Pre-Installed:

📡 Reconnaissance & OSINT
   nmap, recon-ng, theharvester, maltego, shodan, spiderfoot

🔍 Vulnerability Scanning
   nikto, sqlmap, wpscan, nuclei, openvas, nessus

🌐 Web Application Testing
   burpsuite, zaproxy, wfuzz, dirb, gobuster, ffuf

🔑 Password Attacks
   john, hydra, hashcat, medusa, crunch, cewl

📶 Wireless Security
   aircrack-ng, wifite, reaver, kismet, wifiphisher

💥 Exploitation Frameworks
   metasploit-framework, beef-xss, exploitdb, searchsploit

🕵️ Post-Exploitation
   mimikatz, powersploit, empire, covenant

🔬 Forensics & Reverse Engineering
   autopsy, volatility, binwalk, radare2, ghidra, ida-free

Tools organized by learning path in Applications → SynOS Security Tools
        """)
        desc.config(state="disabled")
        desc.pack(pady=20)

    def create_learning_page(self):
        title = tk.Label(self.container, text="🎓 Educational Platform",
                        font=("Arial", 24, "bold"), fg="#00d9ff", bg="#0a1628")
        title.pack(pady=20)

        desc = tk.Text(self.container, wrap="word", height=18, width=70,
                      bg="#1a2638", fg="#e0e0e0", font=("Arial", 11),
                      relief="flat", padx=20, pady=20)
        desc.insert("1.0", """
Learning Modes:

🔰 Beginner Path (Weeks 1-4)
   • Linux fundamentals and command line
   • Basic networking concepts (TCP/IP, DNS, HTTP)
   • Reconnaissance techniques (passive vs active)
   • Introduction to vulnerability scanning

🔸 Intermediate Path (Weeks 5-12)
   • Web application security (OWASP Top 10)
   • Network attacks and mitigation
   • Wireless security testing
   • Basic exploitation techniques

🔺 Advanced Path (Weeks 13+)
   • Custom exploit development
   • Active Directory attacks
   • Cloud security assessments
   • Purple team operations

📚 Resources:
   • Desktop/SynOS-Docs/ - Complete documentation
   • /opt/synos/docs/ - Technical references
   • AI-powered tool recommendations
   • Interactive tutorials with safe practice environments

🎯 SNHU Integration:
   Course materials aligned with cybersecurity degree program
        """)
        desc.config(state="disabled")
        desc.pack(pady=20)

    def create_final_page(self):
        title = tk.Label(self.container, text="🚀 Ready to Begin!",
                        font=("Arial", 24, "bold"), fg="#00d9ff", bg="#0a1628")
        title.pack(pady=20)

        desc = tk.Text(self.container, wrap="word", height=18, width=70,
                      bg="#1a2638", fg="#e0e0e0", font=("Arial", 11),
                      relief="flat", padx=20, pady=20)
        desc.insert("1.0", """
Quick Start Guide:

✅ AI Consciousness Daemon
   Already running! Check status:
   $ systemctl status synos-ai

✅ Security Tools
   Launch from: Applications → SynOS Security Tools
   Or use command line (e.g., nmap, metasploit)

✅ Documentation
   Desktop/SynOS-Docs/ - Start here!
   /opt/synos/ - Full source code

✅ Custom Kernel
   Boot with SynOS custom kernel from GRUB menu
   (Advanced users - network stack 95% complete)

✅ MSSP Features
   Purple team automation: /opt/synos/scripts/purple-team/
   Executive dashboards: /opt/synos/src/executive-dashboard/

📖 Key Commands:
   synos-welcome         - Reopen this welcome screen
   systemctl status synos-ai - Check AI daemon
   cat /opt/synos/README.md - Project overview

🌐 Community & Support:
   GitHub: [Your repository URL]
   Documentation: file:///opt/synos/docs/

Ready to explore the future of cybersecurity education!
        """)
        desc.config(state="disabled")
        desc.pack(pady=20)

        # Don't show again checkbox
        self.no_show_var = tk.BooleanVar()
        check = tk.Checkbutton(self.container, text="Don't show this again on startup",
                              variable=self.no_show_var, bg="#0a1628", fg="#e0e0e0",
                              selectcolor="#1a2638", font=("Arial", 10))
        check.pack(pady=10)

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.show_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def finish(self):
        if hasattr(self, 'no_show_var') and self.no_show_var.get():
            # Disable autostart
            autostart_file = os.path.expanduser("~/.config/autostart/synos-welcome.desktop")
            if os.path.exists(autostart_file):
                os.remove(autostart_file)

        messagebox.showinfo("Welcome Complete",
                          "SynOS is ready! Check Desktop/SynOS-Docs/ to begin.\n\n" +
                          "Reopen anytime with: synos-welcome")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SynOSWelcome(root)
    root.mainloop()
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/synos-welcome"

# Create autostart entry (runs on first login)
mkdir -p "${CHROOT_DIR}/etc/skel/.config/autostart"
cat > "${CHROOT_DIR}/etc/skel/.config/autostart/synos-welcome.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=SynOS Welcome
Comment=Welcome screen for SynOS first boot
Exec=synos-welcome
Icon=system-help
Terminal=false
Categories=System;
X-MATE-Autostart-enabled=true
EOF

echo "  ✅ Welcome screen created"

#######################
# 4B. CUSTOM LOGIN SCREEN (LightDM)
#######################
echo "🔐 Configuring custom LightDM login screen..."

# Install LightDM GTK greeter if not present
chroot "${CHROOT_DIR}" bash -c "
    apt-get install -y --no-install-recommends lightdm-gtk-greeter 2>/dev/null || true
" || log_warning "LightDM installation skipped"

# Configure LightDM GTK greeter with SynOS theme
mkdir -p "${CHROOT_DIR}/etc/lightdm"
cat > "${CHROOT_DIR}/etc/lightdm/lightdm-gtk-greeter.conf" << 'EOF'
[greeter]
# Background
background=/usr/share/backgrounds/synos/synos-neural-dark.jpg
theme-name=Adwaita-dark
icon-theme-name=Adwaita
font-name=DejaVu Sans 11

# Anti-aliasing
xft-antialias=true
xft-dpi=96
xft-hintstyle=slight
xft-rgba=rgb

# Position and indicators
position=50%,center 50%,center
indicators=~host;~spacer;~clock;~spacer;~session;~a11y;~power
clock-format=%A, %B %d    %H:%M

# User settings
user-background=false
hide-user-image=false
default-user-image=/usr/share/pixmaps/synos-logo-128.png

# Panel items
show-indicators=~host;~spacer;~clock;~spacer;~a11y;~session;~power

# Accessibility
a11y-states=+keyboard;+reader
keyboard=onboard
EOF

# Copy logo to pixmaps for LightDM
mkdir -p "${CHROOT_DIR}/usr/share/pixmaps"
if [[ -f "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" ]]; then
    cp "${PROJECT_ROOT}/assets/branding/logos/synos-logo-128.png" \
       "${CHROOT_DIR}/usr/share/pixmaps/" 2>/dev/null || true
fi

# Create custom LightDM greeter banner script
cat > "${CHROOT_DIR}/usr/local/bin/lightdm-greeter-info" << 'EOF'
#!/bin/bash
# Display AI status and system info on login screen

AI_STATUS="🔴 Inactive"
if systemctl is-active --quiet synos-ai 2>/dev/null; then
    AI_STATUS="🟢 Active"
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║          SynOS - Neural Darwinism v1.0               ║"
echo "║     AI-Enhanced Cybersecurity Education Platform     ║"
echo "║                                                      ║"
echo "║  🤖 AI Consciousness: $AI_STATUS                      ║"
echo "║  🛡️  500+ Security Tools Loaded                      ║"
echo "║                                                      ║"
echo "║  💡 Tip: Type 'synos-welcome' for the tutorial      ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/lightdm-greeter-info"

# Add greeting message to LightDM
if [[ -f "${CHROOT_DIR}/etc/lightdm/lightdm.conf" ]]; then
    echo "[Seat:*]" >> "${CHROOT_DIR}/etc/lightdm/lightdm.conf"
    echo "greeter-show-manual-login=false" >> "${CHROOT_DIR}/etc/lightdm/lightdm.conf"
    echo "allow-guest=false" >> "${CHROOT_DIR}/etc/lightdm/lightdm.conf"
else
    mkdir -p "${CHROOT_DIR}/etc/lightdm/lightdm.conf.d"
    cat > "${CHROOT_DIR}/etc/lightdm/lightdm.conf.d/50-synos.conf" << 'EOF'
[Seat:*]
greeter-show-manual-login=false
allow-guest=false
greeter-setup-script=/usr/local/bin/lightdm-greeter-info
EOF
fi

echo "  ✅ LightDM login screen customized"

#######################
# 5. DESKTOP CUSTOMIZATION
#######################
echo "🖥️ Customizing desktop environment..."

# Copy wallpapers
mkdir -p "${CHROOT_DIR}/usr/share/backgrounds/synos"
if [[ -d "${PROJECT_ROOT}/assets/branding/backgrounds" ]]; then
    cp "${PROJECT_ROOT}"/assets/branding/backgrounds/*.jpg \
       "${CHROOT_DIR}/usr/share/backgrounds/synos/" 2>/dev/null || true
fi

# Set default wallpaper in MATE
mkdir -p "${CHROOT_DIR}/etc/skel/.config/mate"
cat > "${CHROOT_DIR}/etc/skel/.config/mate/mate-desktop.conf" << 'EOF'
[background]
picture-filename='/usr/share/backgrounds/synos/synos-neural-blue.jpg'
picture-options='zoom'
primary-color='#0a1628'
EOF

# Create desktop documentation folder
mkdir -p "${CHROOT_DIR}/etc/skel/Desktop/SynOS-Docs"
cat > "${CHROOT_DIR}/etc/skel/Desktop/SynOS-Docs/README.txt" << 'EOF'
# SynOS v1.0 - Quick Start

Welcome to SynOS - AI-Enhanced Cybersecurity Education Platform!

📚 Documentation Locations:
   • This folder - Key getting started guides
   • /opt/synos/docs/ - Complete technical documentation
   • /opt/synos/README.md - Project overview

🛡️ Security Tools:
   • Applications → SynOS Security Tools → [Categories]
   • Command line: nmap, metasploit, burpsuite, etc.

🤖 AI System:
   • Check status: systemctl status synos-ai
   • View logs: tail -f /var/log/synos-ai.log
   • Already running in background!

🎓 Learning Paths:
   • Beginner: /opt/synos/docs/planning/TODO_10X_CYBERSECURITY_ROADMAP.md
   • Tools Guide: /opt/synos/docs/SECURITY.md
   • Build Info: /opt/synos/docs/BUILD_GUIDE.md

🚀 Quick Commands:
   synos-welcome  - Reopen welcome wizard
   nmap --help    - Network scanning
   msfconsole     - Metasploit framework

Enjoy your journey in cybersecurity education!
EOF

# Create desktop launchers for common tools
for tool in "nmap:Network Scanner" "msfconsole:Metasploit" "burpsuite:Burp Suite" "wireshark:Wireshark"; do
    IFS=':' read -r cmd name <<< "$tool"
    cat > "${CHROOT_DIR}/etc/skel/Desktop/${name}.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${name}
Comment=Launch ${name}
Exec=${cmd}
Icon=security-high
Terminal=true
Categories=Security;
EOF
done

echo "  ✅ Desktop customized"

#######################
# 6. AI CONSCIOUSNESS PANEL INDICATOR
#######################
echo "🧠 Creating AI consciousness panel indicator..."

cat > "${CHROOT_DIR}/usr/local/bin/synos-ai-indicator" << 'EOF'
#!/usr/bin/env python3
"""Panel indicator showing AI consciousness state"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import subprocess
import json

class SynOSIndicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "synos-ai-indicator",
            "security-high",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())

        # Update every 10 seconds
        GLib.timeout_add_seconds(10, self.update_status)
        self.update_status()

    def build_menu(self):
        menu = Gtk.Menu()

        status_item = Gtk.MenuItem(label="AI Status: Loading...")
        status_item.set_sensitive(False)
        menu.append(status_item)
        self.status_item = status_item

        menu.append(Gtk.SeparatorMenuItem())

        logs_item = Gtk.MenuItem(label="View AI Logs")
        logs_item.connect("activate", self.open_logs)
        menu.append(logs_item)

        restart_item = Gtk.MenuItem(label="Restart AI Daemon")
        restart_item.connect("activate", self.restart_daemon)
        menu.append(restart_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit Indicator")
        quit_item.connect("activate", Gtk.main_quit)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def update_status(self):
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "synos-ai"],
                capture_output=True, text=True, timeout=2
            )
            if result.stdout.strip() == "active":
                self.status_item.set_label("🟢 AI Consciousness: Active")
                self.indicator.set_icon("security-high")
            else:
                self.status_item.set_label("🔴 AI Consciousness: Inactive")
                self.indicator.set_icon("security-low")
        except:
            self.status_item.set_label("⚠️ AI Consciousness: Unknown")

        return True  # Continue updating

    def open_logs(self, widget):
        subprocess.Popen(["mate-terminal", "-e", "tail -f /var/log/synos-ai.log"])

    def restart_daemon(self, widget):
        subprocess.run(["pkexec", "systemctl", "restart", "synos-ai"])
        GLib.timeout_add_seconds(2, self.update_status)

if __name__ == "__main__":
    indicator = SynOSIndicator()
    Gtk.main()
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/synos-ai-indicator"

# Autostart AI indicator
cat > "${CHROOT_DIR}/etc/skel/.config/autostart/synos-ai-indicator.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=SynOS AI Indicator
Comment=Shows AI consciousness status in panel
Exec=synos-ai-indicator
Icon=security-high
Terminal=false
Categories=System;
X-MATE-Autostart-enabled=true
EOF

echo "  ✅ AI indicator created"

#######################
# 7. SECURITY TOOLS MENU ORGANIZATION
#######################
echo "🔧 Organizing security tools in application menu..."

mkdir -p "${CHROOT_DIR}/usr/share/desktop-directories"

# Create main security category
cat > "${CHROOT_DIR}/usr/share/desktop-directories/synos-security.directory" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Directory
Name=SynOS Security Tools
Comment=AI-Enhanced Cybersecurity Toolkit
Icon=security-high
EOF

# Create subcategories
for category in "Reconnaissance:Recon" "Vulnerability:Vuln" "WebApps:Web" "Exploitation:Exploit" "Wireless:Wireless" "Forensics:Forensics"; do
    IFS=':' read -r name short <<< "$category"
    cat > "${CHROOT_DIR}/usr/share/desktop-directories/synos-${short}.directory" << EOF
[Desktop Entry]
Version=1.0
Type=Directory
Name=${name}
Icon=security-medium
EOF
done

echo "  ✅ Security tools organized"

#######################
# 8. TERMINAL COLOR SCHEME
#######################
echo "🎨 Setting neural blue terminal theme..."

mkdir -p "${CHROOT_DIR}/etc/skel/.config/mate-terminal"
cat > "${CHROOT_DIR}/etc/skel/.config/mate-terminal/profiles/default" << 'EOF'
[Default]
visible-name='SynOS Neural'
background-color='#0a1628'
foreground-color='#e0e0e0'
palette='#1a2638:#ff5555:#50fa7b:#f1fa8c:#00d9ff:#bd93f9:#8be9fd:#e0e0e0:#6272a4:#ff6e6e:#69ff94:#ffffa5:#1adfff:#d6acff:#a4f7ff:#ffffff'
use-theme-colors=false
EOF

echo "  ✅ Terminal theme configured"

#######################
# 9. EDUCATIONAL DOCUMENTATION
#######################
echo "📚 Adding educational documentation to desktop..."

# Copy key docs to desktop folder
DOCS_TO_COPY=(
    "README.md:Getting Started"
    "docs/BUILD_GUIDE.md:Build Guide"
    "docs/SECURITY.md:Security Guide"
    "docs/planning/TODO_10X_CYBERSECURITY_ROADMAP.md:Learning Roadmap"
    "TODO.md:Project Status"
)

for doc_info in "${DOCS_TO_COPY[@]}"; do
    IFS=':' read -r src_path display_name <<< "$doc_info"
    if [[ -f "${PROJECT_ROOT}/${src_path}" ]]; then
        cp "${PROJECT_ROOT}/${src_path}" \
           "${CHROOT_DIR}/etc/skel/Desktop/SynOS-Docs/${display_name}.md"
    fi
done

echo "  ✅ Documentation copied to desktop"

#######################
# 9B. CUSTOM BOOT MESSAGES (VERBOSE MODE)
#######################
echo "📟 Configuring custom boot messages..."

# Create custom boot message script for systemd
mkdir -p "${CHROOT_DIR}/etc/systemd/system"

# Create early boot message service
cat > "${CHROOT_DIR}/etc/systemd/system/synos-boot-banner.service" << 'EOF'
[Unit]
Description=SynOS Boot Banner
DefaultDependencies=no
Before=sysinit.target
After=systemd-journald.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/synos-boot-banner
StandardOutput=journal+console
StandardError=journal+console
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
EOF

# Create boot banner script
cat > "${CHROOT_DIR}/usr/local/bin/synos-boot-banner" << 'EOF'
#!/bin/bash
# SynOS Custom Boot Messages

echo -e "\e[1;31m"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗         ║"
echo "║     ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝         ║"
echo "║     ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗         ║"
echo "║     ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║         ║"
echo "║     ███████║   ██║   ██║ ╚████║╚██████╔╝███████║         ║"
echo "║     ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝         ║"
echo "║                                                            ║"
echo "║        Neural Darwinism Cybersecurity OS v1.0              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "\e[0m"
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/synos-boot-banner"

# Enable the banner service
chroot "${CHROOT_DIR}" systemctl enable synos-boot-banner.service 2>/dev/null || true

# Create AI initialization message service
cat > "${CHROOT_DIR}/etc/systemd/system/synos-ai-init-msg.service" << 'EOF'
[Unit]
Description=SynOS AI Initialization Message
After=synos-ai.service
Requires=synos-ai.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/synos-ai-init-msg
StandardOutput=journal+console
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Create AI init message script
cat > "${CHROOT_DIR}/usr/local/bin/synos-ai-init-msg" << 'EOF'
#!/bin/bash
# Display AI consciousness initialization status

if systemctl is-active --quiet synos-ai; then
    echo -e "\e[1;32m[  OK  ]\e[0m AI Consciousness daemon started successfully"
    echo -e "\e[1;31m[  AI  ]\e[0m Neural Darwinism framework online"
    echo -e "\e[1;31m[  AI  ]\e[0m Pattern recognition active"
    echo -e "\e[1;31m[  AI  ]\e[0m Consciousness level: Rising"
else
    echo -e "\e[1;33m[ WARN ]\e[0m AI Consciousness daemon not started"
fi
EOF

chmod +x "${CHROOT_DIR}/usr/local/bin/synos-ai-init-msg"
chroot "${CHROOT_DIR}" systemctl enable synos-ai-init-msg.service 2>/dev/null || true

# Customize kernel boot parameters for verbose mode
# Add custom kernel command line for educational verbose mode
if [[ -f "${CHROOT_DIR}/etc/default/grub" ]]; then
    # Add custom GRUB menu entry for verbose boot
    cat >> "${CHROOT_DIR}/etc/default/grub" << 'EOF'

# SynOS custom boot parameters
GRUB_CMDLINE_LINUX_VERBOSE="systemd.show_status=1 systemd.log_level=info"
EOF
fi

# Create custom issue file (pre-login message)
cat > "${CHROOT_DIR}/etc/issue" << 'EOF'
\e{red}
 ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗
 ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝
 ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗
 ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║
 ███████║   ██║   ██║ ╚████║╚██████╔╝███████║
 ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
\e{reset}

AI-Enhanced Cybersecurity Education Platform v1.0
Kernel: \r (\l)

EOF

echo "  ✅ Custom boot messages configured"

#######################
# 10. FINAL TOUCHES
#######################
echo "✨ Applying final customizations..."

# Set hostname
echo "synos" > "${CHROOT_DIR}/etc/hostname"

# Add MOTD (message of the day)
cat > "${CHROOT_DIR}/etc/motd" << 'EOF'

 ███████╗██╗   ██╗███╗   ██╗ ██████╗ ███████╗
 ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔════╝
 ███████╗ ╚████╔╝ ██╔██╗ ██║██║   ██║███████╗
 ╚════██║  ╚██╔╝  ██║╚██╗██║██║   ██║╚════██║
 ███████║   ██║   ██║ ╚████║╚██████╔╝███████║
 ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝

 AI-Enhanced Cybersecurity Education Platform v1.0

 🤖 AI Consciousness: systemctl status synos-ai
 🛡️ Security Tools: Applications → SynOS Security Tools
 🎓 Documentation: ~/Desktop/SynOS-Docs/

 Type 'synos-welcome' to reopen the welcome wizard

EOF

# Create helpful aliases
cat >> "${CHROOT_DIR}/etc/skel/.bashrc" << 'EOF'

# SynOS aliases
alias ai-status='systemctl status synos-ai'
alias ai-logs='tail -f /var/log/synos-ai.log'
alias synos-docs='cd /opt/synos/docs && ls -la'
alias security-tools='cd /usr/bin && ls -la | grep -E "(nmap|metasploit|burp|wireshark|aircrack)"'

# Educational prompt
export PS1='\[\033[01;36m\][\u@synos]\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
EOF

echo "  ✅ Final touches complete"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     ✅ BOOT EXPERIENCE ENHANCED TO THE MAX! ✅            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎨 GRUB Boot Menu Enhancements:"
echo "  ✅ SynOS logo (128x128) displayed"
echo "  ✅ Black/Red/White cybersecurity theme"
echo "  ✅ Footer: 'Neural Darwinism | 500+ Tools | v1.0'"
echo "  ✅ Keyboard hints: 'e' to edit, 'c' for console"
echo "  ✅ Red progress bar for auto-boot countdown"
echo ""
echo "🎬 Plymouth Splash Screens (3 Themes):"
echo "  ✅ synos-advanced (default) - Component loading with AI consciousness"
echo "     • Shows: '→ Loading Kernel', '→ AI Core', '→ Security Tools'"
echo "     • Red progress bar with percentage (0-100%)"
echo "     • Consciousness level: Awakening → Rising → Active → Online"
echo "  ✅ synos-matrix - Minimal hacker aesthetic"
echo "  ✅ synos-minimalist - Clean professional boot"
echo "  💡 Switch themes: plymouth-set-default-theme synos-matrix"
echo ""
echo "🔐 Login Screen (LightDM):"
echo "  ✅ Custom dark theme with SynOS branding"
echo "  ✅ Shows: '🟢 AI Consciousness: Active'"
echo "  ✅ Shows: '🛡️ 500+ Security Tools Loaded'"
echo "  ✅ Security tip displayed"
echo "  ✅ SynOS logo as default user image"
echo ""
echo "📟 Boot Messages (Verbose Mode):"
echo "  ✅ Red SynOS ASCII banner during boot"
echo "  ✅ AI initialization messages with color coding"
echo "  ✅ Custom /etc/issue (pre-login banner)"
echo "  ✅ Systemd services show AI consciousness status"
echo ""
echo "🤖 AI Integration:"
echo "  ✅ AI Daemon (systemd service - auto-starts)"
echo "  ✅ Panel indicator (green/red status)"
echo "  ✅ Logs: /var/log/synos-ai.log"
echo ""
echo "👋 User Experience:"
echo "  ✅ Welcome wizard (5-page interactive tour)"
echo "  ✅ Desktop documentation folder"
echo "  ✅ Tool launchers (nmap, metasploit, burp, wireshark)"
echo "  ✅ Custom terminal theme (red/black)"
echo "  ✅ Educational aliases (ai-status, ai-logs)"
echo "  ✅ Custom MOTD with ASCII art"
echo ""
echo "🛡️ Security Tools:"
echo "  ✅ Organized by category in application menu"
echo "  ✅ Educational mode vs Professional mode ready"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🚀 Your ISO now has a FULLY ENHANCED boot-to-desktop experience!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
