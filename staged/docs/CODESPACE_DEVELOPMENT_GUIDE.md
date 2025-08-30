# Syn_OS Codespace Development Environment Guide

**Version**: 2025.01  
**Date**: January 28, 2025  
**Status**: PRODUCTION READY

## Overview

This guide provides comprehensive instructions for setting up and using the ideal Syn_OS development environment in GitHub Codespaces. The environment is specifically designed for AI-enhanced cybersecurity operating system development with all necessary tools, dependencies, and workflows pre-configured.

## Quick Start

### 1. Create New Codespace

```bash
# From GitHub repository
# Click "Code" → "Codespaces" → "Create codespace on main"
# Or use GitHub CLI:
gh codespace create --repo TLimoges33/Syn_OS
```

### 2. Initial Setup (Automatic)

The environment will automatically:
- Install all development tools and dependencies
- Configure Rust, Python, Go, C/C++, and Node.js environments
- Set up security tools and containerization
- Initialize development services
- Run health checks

### 3. Verify Installation

```bash
# Run comprehensive health check
healthcheck.sh

# Quick environment test
syn-dev health

# Display welcome information
syn-welcome
```

## Environment Specifications

### System Requirements

- **CPU**: 8+ cores (recommended)
- **Memory**: 32GB RAM (16GB minimum)
- **Storage**: 100GB+ SSD
- **Network**: High-speed internet for package downloads

### Included Development Tools

#### Core Languages
- **Rust 1.75+**: Complete toolchain with kernel development targets
- **Python 3.11+**: Virtual environment with AI/ML libraries
- **Go 1.21+**: Full development environment with security tools
- **C/C++**: Clang 14, GCC, static analysis tools
- **Node.js 20+**: TypeScript, modern web development stack

#### Security Tools
- **Trivy**: Container vulnerability scanning
- **Bandit**: Python security analysis
- **Semgrep**: Multi-language static analysis
- **Nmap**: Network scanning and discovery
- **Wireshark**: Network protocol analysis

#### Performance Tools
- **Valgrind**: Memory debugging and profiling
- **GDB/LLDB**: Multi-language debugging
- **Flamegraph**: Performance visualization
- **Perf**: Linux performance analysis

#### Virtualization
- **QEMU**: System emulation for kernel testing
- **Docker**: Container development and deployment
- **KVM**: Hardware-accelerated virtualization

## Development Workflows

### Rust Kernel Development

```bash
# Set up kernel development environment
cd /workspace
source ~/.cargo/env

# Build kernel for bare metal
cargo build --target x86_64-unknown-none

# Run kernel in QEMU
cargo run --target x86_64-unknown-none

# Watch for changes and rebuild
cargo watch -x "build --target x86_64-unknown-none"

# Run tests
cargo test --workspace
```

### Python AI Development

```bash
# Activate Python virtual environment
source /workspace/.venv/bin/activate

# Install additional dependencies
pip install -r requirements-dev.txt

# Run AI consciousness tests
python -m pytest tests/consciousness/

# Start development server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Security Analysis

```bash
# Comprehensive security scan
syn-dev security-scan

# Container security analysis
trivy image syn-os:latest

# Python security check
bandit -r src/

# Multi-language analysis
semgrep --config=p/security-audit src/
```

### Docker Development

```bash
# Start development services
docker-compose up -d

# View service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Rebuild and restart
docker-compose down && docker-compose up -d --build
```

## Configuration Management

### Environment Variables

The environment uses a configuration file at `/workspace/config/local/.env`:

```bash
# Syn_OS Development Configuration
SYNAPTICOS_ENV=development
RUST_BACKTRACE=1
CARGO_TERM_COLOR=always
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev-token
NATS_URL=nats://localhost:4222
REDIS_URL=redis://localhost:6379
LOG_LEVEL=debug
```

### VS Code Settings

Workspace-specific settings are automatically configured:

```json
{
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.command": "clippy",
    "python.defaultInterpreterPath": "/workspace/.venv/bin/python",
    "python.linting.enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    }
}
```

## Development Commands

### syn-dev Helper Script

The `syn-dev` command provides quick access to common development tasks:

```bash
# Environment health check
syn-dev health

# Build entire workspace
syn-dev build

# Run all tests
syn-dev test

# Run the kernel
syn-dev run

# Clean build artifacts
syn-dev clean

# Update development tools
syn-dev setup
```

### Rust-Specific Aliases

```bash
# Build project
cb          # cargo build
ct          # cargo test
cc          # cargo check
cr          # cargo run
cw          # cargo watch -x check -x test -x run
```

### Python Aliases

```bash
# Python shortcuts
py          # python3
pia         # source .venv/bin/activate
```

### Git Aliases

```bash
# Git shortcuts
gs          # git status
ga          # git add
gc          # git commit
gp          # git push
gl          # git log --oneline
gd          # git diff
```

## Testing Framework

### Unit Testing

```bash
# Rust unit tests
cargo test --workspace

# Python unit tests
python -m pytest tests/unit/

# Go unit tests
go test ./...

# C/C++ tests (if using criterion)
make test
```

### Integration Testing

```bash
# Start test environment
docker-compose -f tests/docker-compose.test.yml up -d

# Run integration tests
python -m pytest tests/integration/

# Rust integration tests
cargo test --test integration

# Clean up test environment
docker-compose -f tests/docker-compose.test.yml down
```

### Security Testing

```bash
# Automated security testing
make security-test

# Manual penetration testing
nmap -sS -O localhost
```

## Debugging and Profiling

### Rust Debugging

```bash
# Debug with GDB
cargo build
gdb target/debug/syn-kernel

# Debug with LLDB
lldb target/debug/syn-kernel

# Memory profiling with Valgrind
valgrind --tool=memcheck target/debug/syn-kernel
```

### Python Debugging

```bash
# Interactive debugging
python -m pdb src/main.py

# Profile performance
python -m cProfile -o profile.out src/main.py
python -c "import pstats; pstats.Stats('profile.out').sort_stats('cumulative').print_stats(10)"
```

### Performance Analysis

```bash
# Generate flamegraph
cargo install flamegraph
cargo flamegraph --root -- --target x86_64-unknown-none

# System-wide profiling
sudo perf record -g ./target/debug/syn-kernel
perf report
```

## Service Management

### Development Services

The environment includes several services for development:

```yaml
# Services started automatically
- redis: Key-value store for caching
- nats: Message bus for inter-service communication
- postgres: Relational database for structured data
- vault: Secret management (development mode)
```

### Service Control

```bash
# Check service status
docker-compose ps

# Start specific service
docker-compose up -d redis

# Stop all services
docker-compose down

# View service logs
docker-compose logs -f nats

# Restart service
docker-compose restart postgres
```

## Troubleshooting

### Common Issues

#### Rust Compilation Errors

```bash
# Clear Rust cache
cargo clean

# Update Rust toolchain
rustup update

# Reinstall targets
rustup target add x86_64-unknown-none --force
```

#### Python Environment Issues

```bash
# Recreate virtual environment
rm -rf /workspace/.venv
python3 -m venv /workspace/.venv
source /workspace/.venv/bin/activate
pip install -r requirements-dev.txt
```

#### Docker Issues

```bash
# Restart Docker daemon
sudo service docker restart

# Clean Docker system
docker system prune -f

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Permission Issues

```bash
# Fix workspace permissions
sudo chown -R $USER:$USER /workspace
chmod -R u+w /workspace/target
```

### Health Check Diagnostics

```bash
# Comprehensive environment check
healthcheck.sh

# Check specific component
healthcheck.sh rust
healthcheck.sh python
healthcheck.sh docker
```

### Log Analysis

```bash
# View session logs
tail -f /workspace/logs/session.log

# Check container logs
docker-compose logs -f --tail=100

# System logs
journalctl -f
```

## Performance Optimization

### Build Optimization

```bash
# Parallel builds
export CARGO_BUILD_JOBS=$(nproc)

# Use faster linker
export RUSTFLAGS="-C link-arg=-fuse-ld=lld"

# Release builds with debug info
cargo build --release --bin syn-kernel
```

### Resource Management

```bash
# Monitor resource usage
htop
iotop
docker stats

# Cleanup build artifacts
syn-dev clean
docker system prune -f
```

## Security Best Practices

### Secret Management

- Never commit secrets to repository
- Use environment variables for configuration
- Rotate development tokens regularly
- Use Vault for production secrets

### Code Security

```bash
# Automated security scanning
syn-dev security-scan

# Dependency vulnerability check
cargo audit
pip-audit
```

### Container Security

```bash
# Scan container images
trivy image syn-os:latest

# Check Dockerfile security
hadolint Dockerfile
```

## Continuous Integration

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### CI/CD Pipeline

The environment integrates with GitHub Actions for:
- Automated testing on pull requests
- Security scanning
- Build verification
- Deployment preparation

## Advanced Features

### Kernel Development

```bash
# Boot kernel in QEMU with debugging
qemu-system-x86_64 -kernel target/x86_64-unknown-none/debug/syn-kernel \
    -nographic -serial mon:stdio -gdb tcp::1234

# Connect GDB to QEMU
gdb target/x86_64-unknown-none/debug/syn-kernel
(gdb) target remote :1234
```

### eBPF Development

```bash
# Compile eBPF programs
cd src/kernel/ebpf
make all

# Load eBPF program
sudo insmod syn-ebpf.ko
```

### AI Model Development

```bash
# Train consciousness model
python src/consciousness/train.py

# Test model inference
python src/consciousness/test_inference.py

# Model optimization
python src/consciousness/optimize.py
```

## Support and Resources

### Documentation

- **Architecture**: `/workspace/docs/SYN_OS_ARCHITECTURE_BLUEPRINT.md`
- **Security**: `/workspace/docs/SECURITY_IMPLEMENTATION_GUIDELINES.md`
- **Contributing**: `/workspace/docs/CONTRIBUTING.md`

### Getting Help

```bash
# Environment help
syn-dev --help

# Health check
healthcheck.sh

# Welcome information
syn-welcome
```

### Community

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join technical discussions in repository discussions
- **Security**: Report security issues through responsible disclosure

---

**Environment Status**: ✅ PRODUCTION READY  
**Last Updated**: January 28, 2025  
**Next Review**: February 28, 2025
