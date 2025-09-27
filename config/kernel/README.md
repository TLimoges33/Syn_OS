# ⚙️ Kernel Configuration

## 📁 Kernel Target Configuration

This directory contains kernel-specific configuration files for SynOS.

### **Target Configuration**

- **`x86_64-syn_os.json`** - Rust kernel target configuration for x86_64 architecture with SynOS-specific settings

## 🔗 Integration

Kernel configuration integrates with:

- [`../core/rust-project.json`](../core/rust-project.json) - Rust IDE configuration
- [`../formatting/rustfmt.toml`](../formatting/rustfmt.toml) - Rust code formatting
- `/src/kernel/` - Kernel source code
- `/.cargo/config.toml` - Cargo build configuration

## 🚀 Usage

```bash
# Build kernel with target configuration
cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-syn_os

# Reference in Cargo.toml
# target = "config/kernel/x86_64-syn_os.json"
```
