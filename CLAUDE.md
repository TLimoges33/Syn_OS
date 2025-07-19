# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Syn_OS is a security-first operating system integrating AI consciousness with cybersecurity fundamentals. The project is currently in **Foundation Development** phase with established architecture but empty source directories.

## Development Commands

### Environment Setup
```bash
# Initial development environment setup
./scripts/setup-dev-env.sh

# Manual verification steps
source ~/.bashrc
rustc --version
qemu-system-x86_64 --version
```

### Testing and Quality
```bash
# Run all tests (when implemented)
make test

# Security vulnerability scan
make security-scan

# Code quality checks
make lint
```

### Development Prerequisites
- Rust (latest stable) with targets: `x86_64-unknown-none`, `i686-unknown-none`
- Python 3.9+ with packages: capstone, keystone-engine, requests, pyyaml
- Go 1.19+ for security tooling
- Node.js 18+ for frontend development
- QEMU for kernel testing

## Architecture

### Core Module Structure
```
src/
├── kernel/            # Rust - Bare metal kernel (x86_64-unknown-none)
│   ├── boot/          # Boot loader implementation
│   ├── memory/        # Memory management
│   ├── process/       # Process scheduling
│   ├── security/      # Kernel security subsystem
│   └── drivers/       # Hardware drivers
├── consciousness/     # AI decision engine and learning
│   ├── learning/      # ML models (local processing)
│   ├── reasoning/     # Decision algorithms
│   └── adaptation/    # System optimization
├── security/          # Security framework (zero-trust)
│   ├── auth/          # Authentication mechanisms
│   ├── crypto/        # Cryptography (mTLS, HSM)
│   ├── validation/    # Input validation/sanitization
│   └── monitoring/    # eBPF threat detection
└── frontend/          # User interfaces
    ├── cli/           # Command line tools
    ├── gui/           # Graphical interface
    └── api/           # System APIs
```

### Key Architectural Principles

**Security-First Design:**
- Zero-trust architecture with continuous verification
- All external data requires validation and sanitization
- mTLS encryption for network communications
- Hardware Security Module (HSM) integration
- Real-time threat detection with eBPF monitoring

**AI Integration:**
- Local AI processing (offline-first, LM Studio compatible)
- Adaptive decision making based on system patterns
- Anomaly detection and automated response
- Performance optimization through consciousness engine

**Quality Standards:**
- Test coverage >90% for all modules
- Zero high/critical security vulnerabilities
- Response times <100ms
- Complete API documentation coverage

## Development Environment

The project uses VS Code workspace (`synapticOS.code-workspace`) with comprehensive tooling:
- **Languages**: Rust (primary), C/C++, Go, Python, Assembly, Node.js
- **Debugging**: LLDB, GDB, Valgrind, strace, ltrace
- **Security**: Snyk scanning, cargo audit
- **Kernel Development**: QEMU emulation, bare-metal Rust compilation

## Important Implementation Notes

**Rust Kernel Development:**
- Uses `no_std` environment for bare metal compilation
- Target architecture: `x86_64-unknown-none`
- Boot process integration with `bootimage` crate
- Memory safety critical for kernel modules

**Multi-Language Integration:**
- Rust for kernel and core systems (memory safety)
- Python for analysis and tooling scripts
- Go for security utilities and tools
- C/C++ for hardware drivers when needed
- Assembly for critical boot and low-level components

**Testing Strategy:**
- Unit tests for individual modules (>90% coverage required)
- Integration tests for system components
- Security-specific test suites
- QEMU-based kernel testing environment

## Current Project Status

- [x] Repository setup and architecture definition
- [x] Development environment configuration
- [ ] Core security implementation
- [ ] Consciousness engine framework
- [ ] System integration testing

When implementing new features, prioritize security validation, follow zero-trust principles, and ensure all code meets the established quality standards.