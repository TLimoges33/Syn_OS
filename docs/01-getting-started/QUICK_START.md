# 🚀 SynOS v1.0 - Quick Start Guide

**Get up and running with SynOS in 5 minutes**

---

## ⚡ Fastest Path to SynOS

### Option 1: Download Pre-built ISO (Coming Soon)

```bash
# Download latest release
wget https://github.com/yourusername/synos/releases/download/v1.0.0/synos-v1.0.0.iso

# Verify checksum
sha256sum -c synos-v1.0.0.iso.sha256

# Burn to USB
sudo dd if=synos-v1.0.0.iso of=/dev/sdX bs=4M status=progress
```

### Option 2: Build from Source (Available Now)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/synos.git
cd synos

# 2. Install dependencies
sudo apt update
sudo apt install live-build debootstrap squashfs-tools xorriso grub-pc-bin

# 3. Build ISO (30-60 minutes)
sudo ./scripts/02-build/core/build-synos-ultimate-iso.sh

# 4. Find your ISO
ls -lh build/synos-ultimate.iso  # 12-15GB
```

---

## 🖥️ Test in Virtual Machine

**Recommended:** Test in VM before installing on hardware

### Using QEMU (Fast)

```bash
# BIOS mode (most compatible)
qemu-system-x86_64 -cdrom build/synos-ultimate.iso -m 4096 -smp 2

# UEFI mode (modern systems)
qemu-system-x86_64 -bios /usr/share/ovmf/OVMF.fd \
    -cdrom build/synos-ultimate.iso -m 4096 -smp 2 -enable-kvm
```

### Using VirtualBox (User-friendly)

1. Create new VM: Linux, Debian 64-bit
2. Allocate: 4096MB RAM, 2 CPUs
3. Attach ISO to optical drive
4. Start VM

### Using VMware

1. Create new VM from ISO
2. Linux, Debian 12 x64
3. 4GB RAM, 2 CPUs minimum
4. Start and enjoy

---

## 🔐 First Login

### Live Session Credentials

**Username:** `synos`  
**Password:** `synos`

**Root Password:** `toor`

### What You'll See

1. **🔴 Red Phoenix Boot Screen** - Plymouth animation
2. **⚙️ GRUB Menu** - Neural Command theme
3. **🎨 Login Screen** - Red phoenix branding
4. **💻 Desktop** - XFCE with circuit mandala wallpaper

---

## 🎯 Your First 5 Minutes

### 1. Explore the Desktop (1 min)

- **Panel:** Bottom, with custom SynOS layout
- **Wallpaper:** Circuit mandala (red/black)
- **Theme:** Dark red GTK theme (if applied)
- **Icons:** Click phoenix icon for application menu

### 2. Open Terminal (30 sec)

```bash
# Open with: Applications → Terminal
# Or press: Ctrl+Alt+T

# You'll see custom SynOS prompt:
# ┌─[Syn_OS]─[synos@synos]─[~]
# └─▶
```

### 3. Run Your First Scan (2 min)

```bash
# Scan localhost
nmap 127.0.0.1

# Scan network
nmap 192.168.1.0/24

# Advanced scan
nmap -A -T4 scanme.nmap.org
```

### 4. Test AI Features (1 min)

```bash
# Check AI daemon status
systemctl status synos-ai-daemon

# Interact with AI (if available)
ai status
ai help
```

### 5. Explore Security Tools (30 sec)

```bash
# List installed tools
ls /usr/bin | grep -E "(nmap|metasploit|burp|john)"

# Quick tool check
which nmap metasploit-framework burpsuite wireshark
```

---

## 🛠️ Essential Commands

### System Info

```bash
# SynOS version
cat /etc/os-release

# Kernel version
uname -a

# System resources
htop  # or: top

# Disk usage
df -h
```

### Security Tools

```bash
# Network scanning
nmap -h

# Password cracking
john --help

# Web analysis
burpsuite &

# Packet capture
wireshark &

# Metasploit framework
msfconsole
```

### AI Features

```bash
# AI daemon
systemctl status synos-ai-daemon

# Check threats (if configured)
tail -f /var/log/security/threats.log

# Neural status
cat /proc/synos/neural-status  # (if implemented)
```

---

## 📚 Next Steps

### Learn the Tools

1. **Read Tool Guides:** `docs/02-user-guide/tutorials/`
2. **Security Best Practices:** `docs/02-user-guide/security-best-practices.md`
3. **Tool Reference:** `docs/02-user-guide/reference/security-tools.md`

### Customize Your System

1. **Change Wallpaper:** Right-click desktop → Desktop Settings
2. **Adjust Theme:** Applications → Settings → Appearance
3. **Terminal Colors:** Terminal → Edit → Preferences → Colors
4. **Panel Layout:** Right-click panel → Panel → Panel Preferences

### Try Tutorials

- 📖 [Your First Security Scan](../02-user-guide/tutorials/first-security-scan.md)
- 🤖 [Using AI Features](../02-user-guide/tutorials/using-ai-features.md)
- 🎨 [Customizing Desktop](../02-user-guide/tutorials/customizing-desktop.md)

### Join Community

- 💬 Discord: (Coming soon)
- 📧 Email: hello@synos.example.com
- 🐛 Report Issues: GitHub Issues

---

## 🆘 Quick Troubleshooting

### ISO Won't Boot

- Check BIOS/UEFI boot order
- Disable Secure Boot
- Try BIOS mode instead of UEFI
- Verify ISO checksum

### VM Performance Slow

- Allocate more RAM (8GB+)
- Increase CPUs (4+)
- Enable hardware virtualization
- Use KVM acceleration (QEMU)

### Tools Not Working

```bash
# Update package database
sudo apt update

# Reinstall tool
sudo apt install --reinstall <tool-name>

# Check logs
journalctl -xe
```

### Network Issues

```bash
# Check network
ip addr show

# Test connectivity
ping 8.8.8.8

# Restart networking
sudo systemctl restart networking
```

---

## 📖 Additional Resources

- **Main Documentation:** [docs/README.md](../README.md)
- **Build Guide:** [docs/03-build/ultimate-build-guide.md](../03-build/ultimate-build-guide.md)
- **Architecture:** [docs/04-development/ARCHITECTURE.md](../04-development/ARCHITECTURE.md)
- **Project Status:** [docs/06-project-status/PROJECT_STATUS.md](../06-project-status/PROJECT_STATUS.md)

---

## 🎯 Success Checklist

After 5 minutes, you should have:

- [  ] Booted SynOS successfully
- [  ] Logged in to desktop
- [  ] Opened terminal
- [  ] Run first nmap scan
- [  ] Explored applications menu
- [  ] Checked installed security tools

**If you completed these steps: Congratulations! You're ready to explore SynOS! 🎉**

---

**🔴 Welcome to the Red Phoenix era of cybersecurity. 🔴**

*Need help? Check [docs/README.md](../README.md) or ask the community!*
