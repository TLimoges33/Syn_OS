# 🎨 Code Formatting Configuration

## 📁 Formatting Standards for SynOS

This directory contains code formatting configurations for consistent code style across the SynOS project.

### **Formatting Files**

- **`clang-format`** - C/C++ code formatting configuration
  - Based on Linux kernel style with SynOS customizations
  - Configured for kernel development and eBPF programs
  - Includes special handling for consciousness system code
- **`rustfmt.toml`** - Rust code formatting configuration
  - Edition 2021 compatible
  - Optimized for consciousness system patterns
  - 305 Rust files formatted with these rules

## 🎯 Formatting Standards

### **Common Rules**

- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Comments**: Auto-reflowed and properly aligned

### **Language-Specific**

- **Rust**: Consistent with edition 2021, special handling for neural darwinism patterns
- **C/C++**: Linux kernel style, eBPF macro support, consciousness-specific includes

## 🔧 Usage

These files are automatically used by:

- VS Code extensions (rust-analyzer, clangd)
- CI/CD formatting checks
- Pre-commit hooks
- Developer toolchains
