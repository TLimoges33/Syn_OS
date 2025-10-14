# ⚡ 5-Minute Quick Start Guide

Get SynOS up and running in just 5 minutes!

## Prerequisites

-   Linux system (Ubuntu 20.04+, Debian 11+, or similar)
-   4GB RAM minimum
-   20GB free disk space
-   Internet connection

## Quick Start Options

### Option 1: Docker (Fastest - 2 minutes)

```bash
# Clone the repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Start development environment
docker-compose -f docker/docker-compose.yml up -d

# Access the environment
docker exec -it synos-dev bash

# Verify installation
synos --version
```

### Option 2: Build from Source (5 minutes)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup default nightly

# Clone repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Quick build
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Verify build
ls -lh target/x86_64-unknown-none/debug/
```

### Option 3: Pre-built ISO (Boot in 1 minute)

```bash
# Download latest ISO
wget https://releases.synos.dev/latest/synos-v1.0.iso

# Verify checksum
sha256sum -c synos-v1.0.iso.sha256

# Create bootable USB (replace sdX with your USB device)
sudo dd if=synos-v1.0.iso of=/dev/sdX bs=4M status=progress
sync

# Boot from USB
```

## First Commands

Once SynOS is running:

```bash
# Check system status
synos info

# Start AI consciousness
synos consciousness start

# Check consciousness level
synos consciousness level

# Run a quick security scan
synos scan --quick

# List available security tools
synos tools list | head -20

# Show syscalls
synos syscalls list
```

## Quick Test

Verify everything works:

```bash
# Test AI functionality
synos consciousness status

# Test security framework
synos security status

# Test build system
cargo test --manifest-path=src/kernel/Cargo.toml

# Run quick diagnostics
synos diagnose --quick
```

## What's Next?

Now that you have SynOS running:

1. **Learn the System**: [Getting Started Guide](Getting-Started.md)
2. **Understand Architecture**: [Architecture Overview](Architecture-Overview.md)
3. **Try Tutorials**: [Tutorial: First Syscall](Tutorial-First-Syscall.md)
4. **Configure System**: Edit `/etc/synos/config.toml`
5. **Join Community**: [GitHub Discussions](https://github.com/TLimoges33/Syn_OS/discussions)

## Common Issues

### Issue: Rust not found

```bash
# Solution: Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### Issue: Docker not running

```bash
# Solution: Start Docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and back in
```

### Issue: Build fails

```bash
# Solution: Update dependencies
rustup update nightly
cargo clean
cargo update
```

## Resource Links

-   📖 [Full Getting Started Guide](Getting-Started.md)
-   🏗️ [Architecture Overview](Architecture-Overview.md)
-   📚 [Documentation Hub](../DOCUMENTATION_HUB.md)
-   🌐 [DeepWiki](https://deepwiki.com/TLimoges33/Syn_OS)
-   💬 [Community Support](https://github.com/TLimoges33/Syn_OS/discussions)

## Quick Reference

**Essential Paths**:

-   Config: `/etc/synos/config.toml`
-   Data: `/var/lib/synos/`
-   Logs: `/var/log/synos/`
-   Tools: `/opt/synos/tools/`

**Essential Commands**:

```bash
synos --help              # Show all commands
synos info                # System information
synos status              # Current status
synos consciousness start # Start AI
synos security scan       # Security scan
synos tools launch nmap   # Launch tool
```

**Build Commands**:

```bash
cargo build              # Build kernel
make test                # Run tests
make build               # Full build
./scripts/build-simple-kernel-iso.sh  # Build ISO
```

---

**Time to Complete**: 2-5 minutes  
**Difficulty**: Beginner  
**Next Step**: [Getting Started Guide](Getting-Started.md)

---

_Last Updated: October 4, 2025_
