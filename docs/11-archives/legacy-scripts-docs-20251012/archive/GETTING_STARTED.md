# SynOS Development Guide

## 🚀 Getting Started

This guide helps you set up and contribute to SynOS development.

### Prerequisites

- **Rust**: Nightly toolchain (configured via rust-toolchain.toml)
- **Python**: 3.9+ with pip
- **Docker**: For containerized services
- **Git**: For version control

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/TLimoges33/Syn_OS-Dev-Team.git
cd Syn_OS

# 2. Install Rust nightly (if not already installed)
rustup toolchain install nightly
rustup target add x86_64-unknown-none --toolchain nightly

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Verify kernel builds
cargo +nightly build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# 5. Run security audit
python3 scripts/a_plus_security_audit.py
```

## 🏗️ Project Structure

```
Syn_OS/
├── src/                    # Core Rust components
│   ├── kernel/            # SynOS kernel implementation
│   ├── security/          # Security modules (PQC, etc.)
│   ├── consciousness/     # Consciousness integration
│   └── common/           # Shared utilities
├── services/              # Python microservices
│   ├── consciousness/     # Consciousness services
│   ├── monitoring/       # System monitoring
│   └── education/        # Educational platform
├── scripts/              # Development and automation scripts
├── Final_SynOS-1.0_ISO/  # Production ISO build
├── docs/                 # Documentation (this directory)
└── archive/              # Legacy code (consolidated)
```

## 🔧 Development Workflow

### 1. **Kernel Development**

```bash
# Build kernel
cargo +nightly build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Run tests
cargo +nightly test --manifest-path=src/kernel/Cargo.toml

# Format code
cargo fmt --manifest-path=src/kernel/Cargo.toml

# Lint code
cargo clippy --manifest-path=src/kernel/Cargo.toml
```

### 2. **Service Development**

```bash
# Install development dependencies
pip install -r requirements.txt

# Run consciousness service
cd services/consciousness/core
python3 unified_consciousness_service.py

# Run tests
python3 -m pytest tests/

# Format code
black services/
isort services/
```

### 3. **Documentation**

```bash
# Build documentation
sphinx-build -b html docs/ docs/_build/

# Serve documentation locally
python3 -m http.server 8000 --directory docs/_build/
```

## 🧪 Testing

### Unit Tests

```bash
# Rust tests
cargo +nightly test --all

# Python tests
python3 -m pytest services/ scripts/ -v
```

### Integration Tests

```bash
# Run comprehensive test suite
make test

# Run security audit
python3 scripts/a_plus_security_audit.py
```

### ISO Testing

```bash
# Build ISO image
cd Final_SynOS-1.0_ISO
sudo ./build_synos_iso.sh

# Test in VM
qemu-system-x86_64 -cdrom synos-v1.0.iso -m 4096
```

## 🎨 Code Style

### Rust Code Style

- Use `cargo fmt` for formatting
- Follow `cargo clippy` recommendations
- Document all public APIs
- Use meaningful variable names

```rust
/// Process consciousness data with proper error handling
pub fn process_consciousness_data(
    data: &ConsciousnessData,
    context: &SecurityContext,
) -> Result<ProcessedData, ConsciousnessError> {
    // Implementation
}
```

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Format with `black`
- Sort imports with `isort`

```python
async def process_neural_data(
    data: Dict[str, Any],
    context: Optional[ProcessingContext] = None,
) -> ProcessingResult:
    """Process neural network data with consciousness integration."""
    # Implementation
```

## 🔒 Security Guidelines

1. **Never commit secrets** - Use environment variables
2. **Run security scans** - Use bandit and safety tools
3. **Follow secure coding** - Validate all inputs
4. **Use PQC encryption** - For sensitive data

## 🐛 Debugging

### Kernel Debugging

```bash
# Build with debug symbols
cargo +nightly build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Use QEMU for debugging
qemu-system-x86_64 -s -S -cdrom synos.iso
```

### Service Debugging

```bash
# Enable debug logging
export SYNOS_LOG_LEVEL=DEBUG

# Run with pdb
python3 -m pdb services/consciousness/core/unified_consciousness_service.py
```

## 📊 Performance Monitoring

### Consciousness Metrics

```bash
# Monitor consciousness performance
python3 scripts/consciousness-monitor.py

# View dashboard
python3 scripts/dashboard.py
```

### System Metrics

```bash
# Monitor system resources
python3 scripts/memory_pressure_manager.py

# Security monitoring
python3 scripts/security-dashboard.py
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style guidelines**
4. **Add tests for new functionality**
5. **Run security audit**: `python3 scripts/a_plus_security_audit.py`
6. **Submit pull request**

### Commit Message Format

```
type(scope): brief description

Detailed description of changes made.

- List specific changes
- Include any breaking changes
- Reference issue numbers if applicable
```

Example:
```
feat(consciousness): add quantum processing support

Implement quantum consciousness processing with post-quantum cryptography.

- Add KYBER/DILITHIUM encryption
- Integrate with kernel memory management
- Add comprehensive test coverage

Fixes #123
```

## 🆘 Getting Help

- **Documentation**: Check docs/ directory
- **Issues**: Open GitHub issue
- **Discussions**: GitHub Discussions
- **Security**: Email security@syn-os.ai (planned)

---

*This development guide follows Phase 2 optimization standards for improved developer experience.*
