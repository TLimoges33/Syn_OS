# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
pytest tests/ -v
python tests/run_tests.py

# Run security tests
make security-scan
python tests/test_security.py

# Test kernel in QEMU
make qemu-test

# Integration tests
python tests/integration/a_plus_comprehensive_test.py
make test-integration

# Performance testing
python tests/performance_validation/quick_benchmark.py

# Comprehensive test framework
python tests/comprehensive_test_framework.py

# Run optimization tests
./tests/run_optimization_tests.sh
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

# Security audit
make audit
cargo audit
```

### Development Tools
```bash
# Setup development environment
./scripts/setup/setup-dev-environment.sh

# Start development containers
make dev

# Clean build artifacts
make clean

# Build safety framework
./scripts/build-safety-framework.sh
```

### NATS Integration Testing
```bash
# Note: NATS integration test scripts need to be created
# Test functionality is integrated within Python test suites
```

## Architecture

### Core Components

**Kernel Layer** (`src/kernel/`)
- Rust-based kernel with x86_64 target
- Memory management (virtual memory, allocators, guards)
- Boot process and hardware drivers
- AI bridge integration for consciousness interface
- Security-enhanced memory management
- Bootloader integration with custom targets (`x86_64-syn_os.json`)
- Hardware abstraction layer for drivers

**Security Framework** (`core/security/` and `src/security/`)
- Zero-trust architecture implementation
- Cryptographic operations and validation
- Real-time threat detection and monitoring
- Multi-language security modules (Rust + Python)
- Hardware Security Module (HSM) integration
- Quantum-resistant cryptography research
- eBPF-based threat detection
- Advanced audit logging and monitoring

**Consciousness System** (`core/consciousness/` and `src/consciousness_v2/`)
- Neural Darwinism engine implementation
- Event-driven consciousness simulation
- AI-enhanced decision making for security
- NATS message bus integration for distributed consciousness
- Personal context management
- Decision-making framework
- Component-based consciousness simulation
- Pluggable neural processing modules
- State persistence and recovery
- Performance optimization frameworks

**Service Layer** (`core/services/` and `services/orchestrator/`)
- Microservices orchestration
- Message bus integration (NATS)
- System service coordination
- Go-based microservices orchestration
- PostgreSQL and Redis backend storage
- Health monitoring and service discovery
- RESTful API with Gin framework

**AI Integration** (`src/ai_integration/`)
- Multi-model AI orchestration (Claude, Gemini, Perplexity)
- Consciousness-aware AI interfaces
- Educational AI tutoring systems
- Local AI processing (offline-first, LM Studio compatible)
- Adaptive decision making based on system patterns
- Anomaly detection and automated response
- Performance optimization through consciousness engine

### Build Targets

**Primary Target**: `x86_64-unknown-none` for kernel compilation
**Custom Target**: `x86_64-syn_os.json` for kernel-specific builds (located in `.cargo/` and `config/kernel/`)

**Workspace Members**:
- `core/kernel` - Core kernel implementation
- `core/security` - Security framework
- `core/consciousness` - AI consciousness engine
- `core/common` - Shared utilities
- `core/services` - System services
- `src/kernel` - Main kernel binary

## Development Environment

**Prerequisites**:
- Rust with `x86_64-unknown-none` target (latest stable)
- Python 3.8+ with security packages (capstone, keystone-engine, requests, pyyaml)
- QEMU for kernel testing
- Docker for containerized development
- Go 1.19+ for security tooling
- Node.js 18+ for frontend development

**Key Scripts**:
- `scripts/build/` - Build and compilation scripts
- `scripts/audit/` - Security audit tools
- `scripts/core/` - Core system scripts
- `scripts/setup/setup-dev-environment.sh` - Development environment setup
- `scripts/build-safety-framework.sh` - Safety framework builder

**VS Code Workspace**: `synapticOS.code-workspace` with comprehensive tooling
- **Languages**: Rust (primary), C/C++, Go, Python, Assembly, Node.js
- **Debugging**: LLDB, GDB, Valgrind, strace, ltrace
- **Security**: Snyk scanning, cargo audit

## Quality Standards

- Security scans must pass before commits
- Rust code uses `#![no_std]` for kernel components
- All external inputs require validation
- Comprehensive testing with >90% coverage target
- Real-time performance requirements (<38.2ms response times for critical paths, <100ms for general operations)
- Zero high/critical security vulnerabilities
- Complete API documentation coverage

## Important Implementation Notes

**Kernel Development**:
- Uses bare metal Rust compilation (`no_std` environment)
- Memory safety critical for all kernel modules
- Boot process integration with multiboot2 and `bootimage` crate
- Hardware abstraction layer for drivers
- Target architecture: `x86_64-unknown-none`

**Security Focus**:
- Zero-trust architecture throughout with continuous verification
- All network communications use mTLS
- Hardware Security Module (HSM) integration
- eBPF-based threat detection
- Input validation required at all system boundaries
- Cryptographic operations use vetted libraries only
- Comprehensive audit logging for all security events
- Defense-in-depth strategies

**AI Integration**:
- Local AI processing (offline-first)
- Neural Darwinism for adaptive security
- Consciousness-driven command enhancements
- Real-time threat assessment and response
- Event-driven architecture for consciousness simulation
- NATS message bus for distributed consciousness processing
- State persistence for consciousness continuity
- Performance monitoring for real-time consciousness simulation

**Multi-Language Integration**:
- Rust for kernel and core systems (memory safety)
- Python for analysis and tooling scripts
- Go for security utilities and service orchestration
- C/C++ for hardware drivers when needed
- Assembly for critical boot and low-level components

## Key Architecture Patterns

### Message Bus Architecture
- NATS JetStream for reliable messaging
- Event-driven communication between components
- Consciousness events and system-wide coordination
- Schema validation and message persistence

### Modular Design
- Component-based consciousness simulation
- Pluggable neural processing modules
- Microservices orchestration
- Clear separation of concerns between modules

## Development Workflows

### Adding New Security Features
1. Implement in `core/security/` or `src/security/` (Rust or Python)
2. Add tests in `tests/test_security.py` or security integration tests
3. Run security validation: `make security-scan`
4. Verify with comprehensive test framework

### Extending Consciousness Components
1. Add module to `src/consciousness_v2/components/`
2. Implement consciousness interface in `interfaces/consciousness_component.py`
3. Register with event bus in `components/event_bus.py`
4. Test integration with `test_consciousness_orchestrator_integration.py`

### Kernel Development
1. Modify Rust code in `src/kernel/src/`
2. Build with `cargo build --target x86_64-unknown-none --release`
3. Create ISO with `make iso`
4. Validate with QEMU: `make qemu-test`

### Before Committing Changes
```bash
# 1. Run comprehensive tests
make test && cargo test --workspace

# 2. Run security tests
python tests/test_security.py

# 3. Check test coverage
pytest tests/ --cov=src --cov-report=term-missing

# 4. Run comprehensive test framework
python tests/comprehensive_test_framework.py
```

## Configuration Files

### Python Dependencies
- `config/dependencies/requirements-security.txt` - Security framework
- `config/dependencies/requirements-ai-integration.txt` - AI components
- `config/dependencies/requirements-testing.txt` - Testing framework
- `config/dependencies/requirements-nats.txt` - Message bus integration

### Rust Workspace
- Root `Cargo.toml` defines workspace members: `core/security`, `core/consciousness`, `core/common`, `core/services`, `src/kernel`
- Custom target JSON in `.cargo/x86_64-syn_os.json` and `config/kernel/x86_64-syn_os.json`
- Shared dependencies for bootloader, x86_64, security crates
- Multiple build profiles: release, release-small, dev, dev-fast

### Container Orchestration
- `docker/docker-compose.yml` - Development environment
- `deployment/docker-compose.ha.yml` - High availability setup
- Note: Production compose file needs to be created

## Important File Locations
- **Main configuration**: `config/syn_os_config.yaml`
- **Security configurations**: `config/security/`
- **Development scripts**: `scripts/development/`
- **Test results**: `results/` (security_reports, performance_reports, coverage_reports)
- **Documentation**: `docs/` (architecture, guides, research)
- **Container definitions**: `docker/` and `deploy/`

## Testing Strategy

### Test Categories
1. **Unit Tests**: Component-level validation
2. **Integration Tests**: Cross-component communication
3. **Security Tests**: Vulnerability assessment and audit
4. **Performance Tests**: Optimization validation and benchmarking
5. **Consciousness Tests**: AI behavior validation

### Test Execution
- Use `pytest` for Python tests with coverage reporting
- Use `cargo test` for Rust component testing
- Integration tests in `tests/integration/` directory
- Security audits generate reports in `results/security_reports/`

## Key Development Principles

### Security-First Development
- All code must pass security scans before merge
- Input validation required at all system boundaries
- Cryptographic operations use vetted libraries only
- Comprehensive audit logging for all security events

### Consciousness Integration
- Event-driven architecture for consciousness simulation
- NATS message bus for distributed consciousness processing
- State persistence for consciousness continuity
- Performance monitoring for real-time consciousness simulation

### Educational Focus
- Clear documentation for learning operating system concepts
- Security education integration throughout codebase
- AI-assisted learning and tutoring capabilities
- Academic research integration and publication readiness

## Common Development Tasks

### Starting Development Session
```bash
# 1. Setup development environment (if first time)
./scripts/setup/setup-dev-environment.sh

# 2. Start containers
make dev

# 3. Run quick tests
make test

# 4. Build kernel
make kernel
```

## Current Status

The project is production-ready with complete operating system functionality, AI consciousness integration, and comprehensive cybersecurity features. All phases from kernel to userspace applications are implemented and tested.

### Recent Updates
- Complete kernel-to-userspace implementation
- Integrated AI consciousness for threat detection
- Production-ready cybersecurity features
- Comprehensive testing and validation framework
- Multi-language integration (Rust, Python, Go, C/C++, Assembly)
- NATS message bus integration for distributed systems
- Container orchestration for development and deployment