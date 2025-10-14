# 💿 Complete Installation Guide

Comprehensive installation instructions for SynOS on all platforms.

## Table of Contents

-   [System Requirements](#system-requirements)
-   [Linux Installation](#linux-installation)
-   [macOS Installation](#macos-installation)
-   [Windows (WSL) Installation](#windows-wsl-installation)
-   [Docker Installation](#docker-installation)
-   [From Source](#from-source)
-   [ISO Installation](#iso-installation)
-   [Post-Installation](#post-installation)
-   [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

| Component   | Specification          |
| ----------- | ---------------------- |
| **CPU**     | 2 cores, x86_64        |
| **RAM**     | 4 GB                   |
| **Storage** | 20 GB free space       |
| **OS**      | Linux kernel 5.4+      |
| **Network** | Internet for downloads |

### Recommended Requirements

| Component   | Specification                  |
| ----------- | ------------------------------ |
| **CPU**     | 4+ cores, x86_64 with AVX2     |
| **RAM**     | 8 GB or more                   |
| **Storage** | 50 GB SSD                      |
| **GPU**     | NVIDIA/AMD for AI acceleration |
| **OS**      | Ubuntu 22.04 LTS, Debian 12    |

### Optional Components

-   **TPU/NPU**: For enhanced AI performance
-   **Hardware Security Module**: For enhanced cryptography
-   **Multiple Network Interfaces**: For security testing

---

## Linux Installation

### Ubuntu/Debian Installation

#### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    libssl-dev \
    pkg-config \
    clang \
    llvm \
    nasm \
    qemu-system-x86 \
    docker.io \
    docker-compose
```

#### Step 2: Install Rust Toolchain

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Source environment
source $HOME/.cargo/env

# Install nightly toolchain
rustup default nightly

# Add x86_64-unknown-none target
rustup target add x86_64-unknown-none

# Verify installation
rustc --version
cargo --version
```

#### Step 3: Clone Repository

```bash
# Clone SynOS
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Verify repository
git status
ls -la
```

#### Step 4: Build SynOS

```bash
# Build kernel
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Build security framework
cargo build --manifest-path=core/security/Cargo.toml

# Run tests
make test

# Build ISO (optional)
./scripts/build-simple-kernel-iso.sh
```

#### Step 5: Verify Installation

```bash
# Check build output
ls -lh target/x86_64-unknown-none/debug/

# Run diagnostics
synos diagnose --full

# Check kernel module
lsmod | grep synos
```

### Arch Linux Installation

```bash
# Install dependencies
sudo pacman -S base-devel git rust cargo clang llvm nasm qemu docker

# Enable Docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Clone and build
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

### Fedora/RHEL Installation

```bash
# Install dependencies
sudo dnf install -y \
    gcc \
    git \
    rust \
    cargo \
    clang \
    llvm \
    nasm \
    qemu-system-x86 \
    docker

# Start Docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Clone and build
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

---

## macOS Installation

### Prerequisites

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Xcode Command Line Tools
xcode-select --install
```

### Installation Steps

```bash
# Install dependencies
brew install git rust llvm nasm qemu docker

# Start Docker Desktop
open /Applications/Docker.app

# Install x86_64 target
rustup target add x86_64-unknown-none

# Clone repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Build (cross-compilation for x86_64)
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

### macOS Limitations

-   Native kernel module loading not supported
-   Development and testing only
-   Use Docker for full functionality
-   QEMU for kernel testing

---

## Windows (WSL) Installation

### Step 1: Install WSL 2

```powershell
# Run in PowerShell as Administrator
wsl --install

# Restart computer
# Install Ubuntu from Microsoft Store
```

### Step 2: Configure WSL

```bash
# Inside WSL Ubuntu terminal
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    build-essential \
    git \
    curl \
    libssl-dev \
    pkg-config \
    clang \
    llvm \
    nasm
```

### Step 3: Install Docker Desktop

1. Download Docker Desktop for Windows
2. Enable WSL 2 backend
3. Configure Docker to use WSL 2

### Step 4: Build SynOS

```bash
# Follow Linux installation steps
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup default nightly
rustup target add x86_64-unknown-none

git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

---

## Docker Installation

### Quick Docker Setup

```bash
# Clone repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Verify containers
docker ps

# Access development shell
docker exec -it synos-dev bash

# Inside container
synos --version
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

### Custom Docker Configuration

```yaml
# docker-compose.override.yml
version: "3.8"
services:
    synos-dev:
        volumes:
            - ./custom-config:/etc/synos/
        environment:
            - SYNOS_MODE=development
            - AI_ACCELERATION=gpu
        ports:
            - "8080:8080"
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f synos-dev

# Rebuild images
docker-compose build --no-cache

# Clean up
docker-compose down -v
docker system prune -a
```

---

## From Source

### Advanced Build Options

#### Debug Build

```bash
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

#### Release Build

```bash
cargo build --release --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
```

#### Custom Features

```bash
# Build with AI acceleration
cargo build --features ai-acceleration

# Build with full security suite
cargo build --features full-security

# Build minimal kernel
cargo build --no-default-features
```

### Build Configuration

Edit `Cargo.toml` for custom configurations:

```toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"

[profile.dev]
opt-level = 0
debug = true
```

---

## ISO Installation

### Building the ISO

```bash
cd Syn_OS

# Build bootable ISO
./scripts/build-simple-kernel-iso.sh

# Verify ISO
ls -lh build/syn_os.iso
sha256sum build/syn_os.iso > build/syn_os.iso.sha256
```

### Creating Bootable USB

#### Linux

```bash
# Find USB device
lsblk

# Create bootable USB (CAREFUL: This will erase the USB!)
sudo dd if=build/syn_os.iso of=/dev/sdX bs=4M status=progress conv=fsync
sync

# Verify
sudo fdisk -l /dev/sdX
```

#### macOS

```bash
# Find USB device
diskutil list

# Unmount USB
diskutil unmountDisk /dev/diskN

# Write ISO
sudo dd if=build/syn_os.iso of=/dev/rdiskN bs=4m
sync

# Eject
diskutil eject /dev/diskN
```

#### Windows

Use one of these tools:

-   **Rufus**: https://rufus.ie/
-   **Etcher**: https://www.balena.io/etcher/
-   **Ventoy**: https://www.ventoy.net/

### Installing from ISO

1. Boot from USB/ISO
2. Select "Install SynOS"
3. Choose installation location
4. Configure network
5. Set up user account
6. Install bootloader (GRUB)
7. Reboot

---

## Post-Installation

### Initial Configuration

```bash
# Edit main configuration
sudo nano /etc/synos/config.toml

# Configure AI system
sudo nano /etc/synos/ai.toml

# Set up security policies
sudo nano /etc/synos/security/policies.toml
```

### Enable Services

```bash
# Enable SynOS services
sudo systemctl enable synos-consciousness
sudo systemctl enable synos-security
sudo systemctl enable synos-network

# Start services
sudo systemctl start synos-consciousness
sudo systemctl start synos-security

# Check status
sudo systemctl status synos-*
```

### Security Hardening

```bash
# Run security audit
sudo synos security audit

# Apply recommended hardening
sudo synos security harden --apply

# Configure firewall
sudo synos network firewall --enable

# Set up audit logging
sudo synos audit enable --level full
```

### Install Security Tools

```bash
# Install all security tools
sudo synos tools install --all

# Or install specific categories
sudo synos tools install --category network
sudo synos tools install --category web
sudo synos tools install --category forensics

# Verify installation
synos tools list
```

### User Setup

```bash
# Create user
sudo synos user create --name student --role student

# Set permissions
sudo synos user permissions --name student --grant network-scan

# Configure educational mode
synos mode educational --enable
```

---

## Troubleshooting

### Build Errors

#### Cannot find crate

```bash
# Solution: Update Rust and dependencies
rustup update nightly
cargo update
cargo clean
```

#### Linker errors

```bash
# Solution: Install linker
sudo apt install lld  # Debian/Ubuntu
brew install llvm     # macOS
```

#### Out of memory

```bash
# Solution: Limit parallel jobs
cargo build -j 1
# Or increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Runtime Errors

#### AI consciousness won't start

```bash
# Check model files
ls -la /var/lib/synos/models/

# Download models
sudo synos ai download-models

# Reset consciousness
sudo synos consciousness reset
```

#### Security tools not found

```bash
# Reinstall tools
sudo synos tools install --all --force

# Check paths
echo $PATH
export PATH=$PATH:/opt/synos/tools/bin
```

#### Permission denied errors

```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.synos
sudo chmod -R 755 /opt/synos

# Add user to synos group
sudo usermod -aG synos $USER
# Log out and back in
```

### Network Issues

```bash
# Check network configuration
synos network status

# Reset network stack
sudo synos network reset

# Check firewall
sudo ufw status
sudo synos network firewall --status
```

### Getting Help

1. **Check Logs**:

    ```bash
    tail -f /var/log/synos/system.log
    journalctl -u synos-* -f
    ```

2. **Run Diagnostics**:

    ```bash
    synos diagnose --full --output report.txt
    ```

3. **Community Support**:
    - GitHub Issues: https://github.com/TLimoges33/Syn_OS/issues
    - Discussions: https://github.com/TLimoges33/Syn_OS/discussions
    - DeepWiki: https://deepwiki.com/TLimoges33/Syn_OS

---

## Verification Checklist

After installation, verify:

-   [ ] Kernel builds successfully
-   [ ] AI consciousness starts
-   [ ] Security framework active
-   [ ] Network stack operational
-   [ ] Security tools accessible
-   [ ] System commands work
-   [ ] Logs are being written
-   [ ] Configuration files present

---

## Next Steps

After successful installation:

1. [Quick Start Guide](Quick-Start.md) - Try essential commands
2. [Getting Started](Getting-Started.md) - Learn the system
3. [Architecture Overview](Architecture-Overview.md) - Understand design
4. [Tutorials](Tutorial-First-Syscall.md) - Hands-on learning

---

**Installation Time**: 10-30 minutes  
**Difficulty**: Intermediate  
**Support**: [GitHub Discussions](https://github.com/TLimoges33/Syn_OS/discussions)

---

_Last Updated: October 4, 2025_
