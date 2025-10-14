# 🚀 Getting Started with SynOS

Welcome to SynOS! This guide will help you get up and running quickly.

## Prerequisites

### System Requirements

**Minimum**:

-   CPU: 2 cores, x86_64
-   RAM: 4 GB

-   Storage: 20 GB free space

-   Internet connection for package downloads

**Recommended**:

-   CPU: 4+ cores, x86_64 with AVX2
-   RAM: 8+ GB
-   Storage: 50+ GB SSD
-   GPU: NVIDIA/AMD for AI acceleration (optional)

### Software Requirements

-   **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, Arch, etc.)
-   **Rust**: 1.91.0-nightly or later
-   **Docker**: Latest stable version
-   **Git**: For source code management

## Quick Start

### Option 1: Using Pre-built ISO (Fastest)

```bash
# Download the latest SynOS ISO
wget https://releases.synos.dev/latest/synos-v1.0.iso

# Verify checksum
sha256sum synos-v1.0.iso
cat synos-v1.0.iso.sha256

# Create bootable USB (Linux)
sudo dd if=synos-v1.0.iso of=/dev/sdX bs=4M status=progress
sudo sync

# Boot from USB and follow installation wizard
```

### Option 2: Building from Source (Developer)

```bash
# Clone the repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default nightly
rustup target add x86_64-unknown-none

# Install system dependencies
sudo apt update
sudo apt install -y build-essential git curl wget \
    libssl-dev pkg-config clang llvm nasm qemu-system-x86

# Build the kernel
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Build the security framework
cargo build --manifest-path=core/security/Cargo.toml

# Run tests
make test

# Build ISO image
./scripts/build-simple-kernel-iso.sh
```

### Option 3: Docker Development Environment (Quickest Setup)

```bash
# Clone repository
git clone https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# Start development containers
docker-compose -f docker/docker-compose.yml up -d

# Access development shell
docker exec -it synos-dev bash

# Build inside container
make build
```

## First Steps

### 1. Verify Installation

```bash
# Check SynOS version
synos --version

# Verify AI consciousness is running
synos consciousness status

# Check security tools
synos tools list
```

### 2. Run Your First Command

```bash
# Start AI consciousness engine
synos consciousness start

# Check consciousness level
synos consciousness level

# Run a security scan
synos scan --quick
```

### 3. Explore the System

```bash
# List all syscalls
synos syscalls list

# Show system information
synos info

# Display security status
synos security status
```

## Understanding SynOS

### Key Concepts

1. **AI Consciousness**: The adaptive intelligence system that learns from your usage
2. **Quantum Memory**: AI-optimized memory allocation for better performance
3. **Threat Detection**: Real-time security monitoring and response
4. **Educational Mode**: Guided learning for cybersecurity students

### System Components

-   **Kernel**: Custom Rust-based kernel with AI integration
-   **AI Engine**: Neural Darwinism consciousness system
-   **Security Framework**: 500+ integrated security tools
-   **Distribution**: Debian-based Linux with custom enhancements

## Basic Usage

### For Students

```bash
# Enable educational mode
synos mode educational

# Start guided tutorial
synos tutorial start

# Access learning resources
synos learn --topic "penetration-testing"

# Track progress
synos progress show
```

### For Security Professionals

```bash
# Enable professional mode
synos mode professional

# Start security assessment
synos assess --target 192.168.1.0/24

# Generate report
synos report --format pdf --output assessment.pdf

# Launch specific tool
synos tool launch --name metasploit
```

### For Developers

```bash
# Enable development mode
synos mode development

# Build custom kernel module
synos dev build-module --source my_module.rs

# Run integration tests
synos test integration

# Monitor system performance
synos monitor --metrics all
```

## Configuration

### Basic Configuration

Edit `/etc/synos/config.toml`:

```toml
[consciousness]
enabled = true
learning_rate = 0.001
model_path = "/var/lib/synos/models"

[security]
threat_detection = true
auto_response = false
audit_logging = true

[education]
mode = "student"
guided_learning = true
progress_tracking = true
```

### AI Configuration

Edit `/etc/synos/ai.toml`:

```toml
[neural_darwinism]
enabled = true
hardware_acceleration = "auto"  # auto, cpu, gpu, tpu
max_memory_mb = 2048

[models]
inference_engine = "tensorflow-lite"

quantization = "int8"
```

## Troubleshooting

### Common Issues

**Issue**: Build fails with "cannot find crate"

```bash


# Solution: Update dependencies
cargo update
rustup update nightly


```

**Issue**: AI consciousness won't start

```bash
# Solution: Check model files
ls -la /var/lib/synos/models/

synos consciousness reset
```

**Issue**: Security tools not found

```bash
# Solution: Reinstall tools
sudo synos tools install --all
```

### Getting Help

```bash
# View detailed help
synos --help
synos <command> --help

# Check logs
synos logs show
tail -f /var/log/synos/system.log

# Run diagnostics
synos diagnose --full
```

## Next Steps

### Learning Paths

1. **Beginner**: [Beginner Path](Beginner-Path.md)

    - Basic system navigation
    - Simple security scans
    - Educational tutorials

2. **Intermediate**: [Intermediate Path](Intermediate-Path.md)

    - Custom syscall usage
    - AI integration
    - Advanced security tools

3. **Advanced**: [Advanced Path](Advanced-Path.md)

    - Kernel module development
    - Security framework customization
    - Performance optimization

4. **Expert**: [Expert Path](Expert-Path.md)
    - Contributing to core
    - Research and development
    - Teaching and mentoring

### Recommended Reading

-   [Architecture Overview](Architecture-Overview.md) - System design
-   [Syscall Reference](Syscall-Reference.md) - API documentation
-   [Security Framework](Security-Framework.md) - Security capabilities
-   [Development Guide](Development-Guide.md) - Contributing code

### Tutorials

-   [Your First Syscall](Tutorial-First-Syscall.md)
-   [AI Integration](Tutorial-AI-Integration.md)
-   [Security Hardening](Tutorial-Security-Hardening.md)
-   [Custom Kernel Module](Tutorial-Kernel-Module.md)

## Community & Support

-   **GitHub**: [TLimoges33/Syn_OS](https://github.com/TLimoges33/Syn_OS)
-   **Issues**: [Report bugs](https://github.com/TLimoges33/Syn_OS/issues)
-   **Discussions**: [Community forum](https://github.com/TLimoges33/Syn_OS/discussions)
-   **Security**: [Report vulnerabilities](../../SECURITY.md)

## Quick Reference

### Essential Commands

```bash
synos --version              # Show version
synos consciousness status   # Check AI status
synos security scan          # Run security scan
synos tools list             # List security tools
synos info                   # System information
synos help                   # Show help
```

### Essential Paths

```
/etc/synos/              # Configuration files
/var/lib/synos/          # Data and models
/var/log/synos/          # Log files
/usr/lib/synos/          # Library files
/opt/synos/tools/        # Security tools
```

### Essential Documentation

-   `/docs/README.md` - Documentation index
-   `/docs/api/SYSCALL_REFERENCE.md` - Complete API reference
-   `/PHASE_3B_COMPLETE.md` - Latest development status
-   `/TODO.md` - Current development tasks

---

**Welcome to the SynOS community!** 🎉

Ready to revolutionize cybersecurity education and operations? Let's get started!

---

## 🎤 Voice Assistant (ALFRED)

### Using ALFRED

SynOS v1.0 includes ALFRED, your AI voice assistant:

```bash
# Launch ALFRED (automatically starts on boot)
alfred

# Wake word: "alfred"
# Example commands:
"alfred, open nmap"
"alfred, open metasploit"
"alfred, open terminal"
"alfred, health check"
"alfred, what time is it?"
```

### ALFRED Features (v1.0)
- ✅ Wake word detection
- ✅ British accent voice
- ✅ Security tool launching
- ✅ System operations
- ✅ Conversational responses
- 🔄 System-wide transcription (coming in v1.4)
- 🔄 "Read to Me" feature (coming in v1.4)

---

_Last Updated: October 13, 2025 - v1.0 "Red Phoenix"_
