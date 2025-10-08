# CLAUDE.md


## Project Overview

SynOS is a neural darwinism-enhanced cybersecurity operating system built in Rust. It features integrated AI consciousness for threat detection, a complete kernel-to-userspace implementation, and advanced security capabilities.

## Development Commands

### Build Commands
```bash
# Build kernel
make kernel
cargo build --target x86_64-unknown-none --release

# Build all workspace components
cargo build --workspace

# Create bootable ISO
make iso

# Development setup
make dev-setup
```

### Testing Commands
```bash
# Run all tests
make test
cargo test --workspace

# Run security tests
make security-scan
python scripts/a_plus_security_audit.py

# Test kernel in QEMU
make qemu-test

# Integration tests
python tests/integration/a_plus_comprehensive_test.py
```

### Code Quality
```bash
# Format code
make format
cargo fmt --all

# Check code quality
make check
cargo clippy --workspace -- -D warnings

# Full validation pipeline
make validate
```

### Development Tools
```bash
# Environment validation
./scripts/validate-environment.sh

# Security audit
make audit
cargo audit

# Clean build artifacts
make clean
```

## Architecture

### Core Components

**Kernel Layer** (`src/kernel/`)
- Rust-based kernel with x86_64 target
- Memory management (virtual memory, allocators, guards)
- Boot process and hardware drivers
- AI bridge integration for consciousness interface

**Security Framework** (`core/security/`)
- Zero-trust architecture implementation
- Cryptographic operations and validation
- Real-time threat detection and monitoring

**Consciousness System** (`core/consciousness/`)
- Neural Darwinism engine implementation
- Event-driven consciousness simulation
- AI-enhanced decision making for security

**Service Layer** (`core/services/`)
- Microservices orchestration
- Message bus integration (NATS)
- System service coordination

### Build Targets

**Primary Target**: `x86_64-unknown-none` for kernel compilation
**Workspace Members**:
- `core/kernel` - Core kernel implementation  
- `core/security` - Security framework
- `core/consciousness` - AI consciousness engine
- `core/common` - Shared utilities
- `core/services` - System services
- `src/kernel` - Main kernel binary

## Development Environment

**Prerequisites**:
- Rust with `x86_64-unknown-none` target
- Python 3.8+ with security packages
- QEMU for kernel testing
- Docker for containerized development

**Key Scripts**:
- `scripts/security-automation/` - Security validation tools
- `scripts/validate-environment.sh` - Environment setup verification
- `scripts/build-simple-kernel-iso.sh` - ISO creation

## Quality Standards

- Security scans must pass before commits
- Rust code uses `#![no_std]` for kernel components
- All external inputs require validation
- Comprehensive testing with >90% coverage target
- Real-time performance requirements (<38.2ms response times)

## Important Implementation Notes

**Kernel Development**:
- Uses bare metal Rust compilation
- Memory safety critical for all kernel modules
- Boot process integration with multiboot2
- Hardware abstraction layer for drivers

**Security Focus**:
- Zero-trust architecture throughout
- All network communications use mTLS
- Hardware Security Module (HSM) integration
- eBPF-based threat detection

**AI Integration**:
- Local AI processing (offline-first)
- Neural Darwinism for adaptive security
- Consciousness-driven command enhancements
- Real-time threat assessment and response

## Current Status

The project is production-ready with complete operating system functionality, AI consciousness integration, and comprehensive cybersecurity features. All phases from kernel to userspace applications are implemented and tested.