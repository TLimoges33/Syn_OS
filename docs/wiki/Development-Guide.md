# 🛠️ SynOS Development Guide

**Audience**: Developers  
**Difficulty**: Intermediate to Advanced  
**Time**: 2-3 hours to complete setup

This comprehensive guide will help you set up a complete development environment for SynOS, understand the codebase architecture, and start contributing effectively.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Building from Source](#building-from-source)
4. [IDE Configuration](#ide-configuration)
5. [Project Structure](#project-structure)
6. [Development Workflow](#development-workflow)
7. [Debugging Techniques](#debugging-techniques)
8. [Testing Your Changes](#testing-your-changes)
9. [Code Quality Standards](#code-quality-standards)
10. [Submitting Changes](#submitting-changes)
11. [Advanced Topics](#advanced-topics)

---

## 1. Prerequisites

### Required Knowledge

Before diving into SynOS development, you should be familiar with:

-   **Rust Programming**: Core language (async, lifetimes, traits, macros)
-   **Systems Programming**: Memory management, OS concepts
-   **Version Control**: Git and GitHub workflows
-   **Command Line**: Linux/Unix shell proficiency

### Recommended Knowledge

These will help but aren't strictly required:

-   **Kernel Development**: Understanding of OS kernels
-   **AI/ML**: TensorFlow, ONNX, neural networks
-   **Security**: Penetration testing, cryptography
-   **Networking**: TCP/IP, protocols, sockets

### System Requirements

**Minimum**:

-   CPU: 4 cores (x86_64)
-   RAM: 8 GB
-   Storage: 30 GB free space
-   OS: Linux (Ubuntu 20.04+, Arch, Fedora)

**Recommended**:

-   CPU: 8+ cores (with AVX2 support)
-   RAM: 16 GB
-   Storage: 50 GB SSD
-   OS: Linux (latest stable)
-   GPU: NVIDIA (for AI acceleration, optional)

### Required Software

We'll install these in the next section:

-   Rust (nightly)
-   LLVM/Clang
-   GDB
-   Git
-   Docker (optional)
-   QEMU (for testing)

---

## 2. Development Environment Setup

### 2.1 Install Rust Toolchain

SynOS requires Rust nightly with specific components:

```bash
# Install rustup if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install nightly toolchain
rustup toolchain install nightly-2024-09-01
rustup default nightly-2024-09-01

# Add required components
rustup component add rust-src
rustup component add rust-analyzer
rustup component add clippy
rustup component add rustfmt

# Add cross-compilation targets
rustup target add x86_64-unknown-none
rustup target add x86_64-unknown-linux-gnu

# Verify installation
rustc --version
cargo --version
```

Expected output:

```
rustc 1.91.0-nightly (xxx 2024-09-01)
cargo 1.91.0-nightly (xxx 2024-09-01)
```

### 2.2 Install System Dependencies

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    git \
    curl \
    pkg-config \
    libssl-dev \
    clang \
    llvm \
    lld \
    qemu-system-x86 \
    gdb \
    nasm \
    grub-pc-bin \
    xorriso \
    mtools
```

#### Arch Linux

```bash
sudo pacman -S --needed \
    base-devel \
    cmake \
    git \
    curl \
    openssl \
    clang \
    llvm \
    lld \
    qemu \
    gdb \
    nasm \
    grub \
    xorriso \
    mtools
```

#### Fedora/RHEL

```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install -y \
    cmake \
    git \
    curl \
    openssl-devel \
    clang \
    llvm \
    lld \
    qemu-system-x86 \
    gdb \
    nasm \
    grub2-tools \
    xorriso \
    mtools
```

### 2.3 Clone Repository

```bash
# Clone with submodules
git clone --recursive https://github.com/TLimoges33/Syn_OS.git
cd Syn_OS

# If you already cloned without --recursive:
git submodule update --init --recursive
```

### 2.4 Install Python Development Tools

```bash
# Install Python 3.10+
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r development/requirements.txt
```

### 2.5 Install Optional Tools

```bash
# Docker (for containerized development)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Cargo tools
cargo install cargo-watch      # Auto-rebuild on file changes
cargo install cargo-edit        # Manage dependencies
cargo install cargo-tree        # Visualize dependency tree
cargo install cargo-audit       # Security audit
cargo install cargo-bloat       # Binary size profiler
cargo install cargo-flamegraph  # Performance profiling

# Development utilities
cargo install tokei             # Count lines of code
cargo install ripgrep           # Fast search
cargo install fd-find           # Fast file finder
```

---

## 3. Building from Source

### 3.1 Quick Build

```bash
# Build everything
make

# Or use cargo directly
cargo build --workspace

# Build in release mode (optimized)
cargo build --workspace --release
```

### 3.2 Component Builds

Build individual components:

```bash
# Build kernel only
make kernel
# Or: cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none

# Build security framework
make security
# Or: cargo build --manifest-path=core/security/Cargo.toml

# Build AI consciousness engine
cargo build --manifest-path=core/ai/consciousness/Cargo.toml

# Build services
cargo build --manifest-path=core/services/Cargo.toml
```

### 3.3 Build Configurations

#### Debug Build (Default)

```bash
cargo build --workspace
```

Features:

-   Debug symbols included
-   Assertions enabled
-   No optimizations
-   Fast compile times
-   Large binary size

#### Release Build

```bash
cargo build --workspace --release
```

Features:

-   Optimizations enabled (opt-level=3)
-   Debug symbols stripped
-   Assertions disabled (unless debug_assertions)
-   Slower compile times
-   Smaller binary size

#### Custom Build Features

```bash
# Enable all features
cargo build --workspace --all-features

# Disable default features
cargo build --workspace --no-default-features

# Enable specific features
cargo build --workspace --features "ai-acceleration,full-security"

# Available features:
# - ai-acceleration: GPU/TPU acceleration for AI
# - full-security: All 500+ security tools
# - minimal: Minimal feature set
# - development: Extra development tools
```

### 3.4 Build the ISO

```bash
# Build bootable ISO image
./scripts/build-simple-kernel-iso.sh

# Output: build/syn_os.iso
```

### 3.5 Build Troubleshooting

**Problem**: Linker errors

```bash
# Install LLD linker
sudo apt install lld

# Or use default linker
export RUSTFLAGS="-C linker=clang"
```

**Problem**: Out of memory during build

```bash
# Limit parallel jobs
cargo build --workspace -j 2

# Or increase swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Problem**: Rust version mismatch

```bash
# Update toolchain
rustup update nightly-2024-09-01
rustup default nightly-2024-09-01
```

---

## 4. IDE Configuration

### 4.1 Visual Studio Code (Recommended)

#### Install Extensions

```bash
code --install-extension rust-lang.rust-analyzer
code --install-extension vadimcn.vscode-lldb
code --install-extension tamasfe.even-better-toml
code --install-extension serayuzgur.crates
code --install-extension usernamehw.errorlens
```

#### Workspace Settings

Create `.vscode/settings.json`:

```json
{
    "rust-analyzer.checkOnSave.command": "clippy",
    "rust-analyzer.checkOnSave.allTargets": false,
    "rust-analyzer.cargo.features": ["development"],
    "rust-analyzer.cargo.target": "x86_64-unknown-linux-gnu",
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "[rust]": {
        "editor.defaultFormatter": "rust-lang.rust-analyzer"
    }
}
```

#### Launch Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "lldb",
            "request": "launch",
            "name": "Debug SynOS Kernel",
            "cargo": {
                "args": ["build", "--manifest-path=src/kernel/Cargo.toml", "--target=x86_64-unknown-none"]
            },
            "args": [],
            "cwd": "${workspaceFolder}"
        },
        {
            "type": "lldb",
            "request": "launch",
            "name": "Debug Security Framework",
            "cargo": {
                "args": ["build", "--manifest-path=core/security/Cargo.toml"]
            },
            "args": [],
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

#### Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "cargo build",
            "type": "shell",
            "command": "cargo",
            "args": ["build", "--workspace"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "cargo test",
            "type": "shell",
            "command": "cargo",
            "args": ["test", "--workspace"],
            "group": {
                "kind": "test",
                "isDefault": true
            }
        },
        {
            "label": "cargo clippy",
            "type": "shell",
            "command": "cargo",
            "args": ["clippy", "--workspace", "--", "-D", "warnings"]
        }
    ]
}
```

### 4.2 CLion / IntelliJ IDEA

1. Install **Rust plugin**
2. Open project: `File > Open > Select Syn_OS directory`
3. Configure Rust toolchain: `Settings > Languages & Frameworks > Rust`
4. Set toolchain to: `~/.cargo/bin`
5. Enable external linter: `Settings > Rust > External Linters > Clippy`

### 4.3 Vim/Neovim

Install **rust.vim** and **coc-rust-analyzer**:

```vim
" In ~/.vimrc or ~/.config/nvim/init.vim
Plug 'rust-lang/rust.vim'
Plug 'neoclide/coc.nvim', {'branch': 'release'}

" Install coc-rust-analyzer
:CocInstall coc-rust-analyzer

" Configure rust.vim
let g:rustfmt_autosave = 1
let g:rust_clip_command = 'xclip -selection clipboard'
```

---

## 5. Project Structure

### 5.1 Directory Layout

```
Syn_OS/
├── src/                    # Userspace source code
│   └── kernel/            # Custom kernel
│       ├── src/
│       │   ├── arch/      # Architecture-specific code (x86_64)
│       │   ├── memory/    # Memory management
│       │   ├── process/   # Process management
│       │   ├── hal/       # Hardware Abstraction Layer
│       │   ├── security/  # Kernel security
│       │   └── syscalls/  # System call handlers
│       └── Cargo.toml
├── core/                   # Core systems
│   ├── ai/
│   │   └── consciousness/ # AI consciousness engine
│   │       ├── src/
│   │       │   ├── engine.rs        # Main engine
│   │       │   ├── neural_darwin.rs # Neural Darwinism
│   │       │   ├── learning.rs      # Learning algorithms
│   │       │   └── inference.rs     # Inference engine
│   │       └── Cargo.toml
│   ├── security/          # Security framework
│   │   ├── src/
│   │   │   ├── framework.rs  # Security framework
│   │   │   ├── mac.rs        # Mandatory Access Control
│   │   │   ├── rbac.rs       # Role-Based Access Control
│   │   │   ├── threat.rs     # Threat detection
│   │   │   └── audit.rs      # Audit system
│   │   └── Cargo.toml
│   ├── services/          # System services
│   ├── libraries/         # Shared libraries
│   └── common/            # Common utilities
├── deployment/            # Deployment configs
├── development/           # Development tools
│   ├── cli/              # Development CLI
│   └── tools/            # Helper scripts
├── scripts/              # Build and utility scripts
├── config/               # Configuration files
├── docs/                 # Documentation
│   └── api/             # API documentation
├── tests/               # Integration tests
├── wiki/                # Wiki documentation
└── Cargo.toml           # Workspace manifest
```

### 5.2 Key Files

| File                  | Purpose                                  |
| --------------------- | ---------------------------------------- |
| `Cargo.toml`          | Workspace manifest, defines all packages |
| `rust-toolchain.toml` | Rust toolchain specification             |
| `Makefile`            | Build system shortcuts                   |
| `.github/`            | CI/CD workflows                          |
| `LICENSE`             | MIT License                              |
| `README.md`           | Project overview                         |

### 5.3 Code Organization Principles

**Separation of Concerns**:

-   Kernel code: `src/kernel/`
-   Userspace services: `core/services/`
-   Libraries: `core/libraries/`
-   AI systems: `core/ai/`
-   Security: `core/security/`

**Module Hierarchy**:

-   Each major component is a separate crate
-   Shared code goes in `core/common/`
-   Platform-specific code in `arch/` directories

---

## 6. Development Workflow

### 6.1 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Check status
git status

# Add changes
git add .

# Commit with conventional commit message
git commit -m "feat(kernel): add new scheduling algorithm"

# Push to your fork
git push origin feature/my-feature

# Create pull request on GitHub
```

### 6.2 Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:

-   `feat`: New feature
-   `fix`: Bug fix
-   `docs`: Documentation changes
-   `style`: Code style changes (formatting)
-   `refactor`: Code refactoring
-   `perf`: Performance improvements
-   `test`: Adding/updating tests
-   `build`: Build system changes
-   `ci`: CI/CD changes
-   `chore`: Other changes (dependencies, etc.)

**Examples**:

```
feat(consciousness): implement neural Darwinism learning algorithm
fix(kernel): resolve memory leak in process scheduler
docs(wiki): add development guide
refactor(security): simplify MAC implementation
perf(ai): optimize TensorFlow Lite inference
test(kernel): add integration tests for syscalls
```

### 6.3 Development Cycle

```bash
# 1. Update your branch
git pull origin master

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes with auto-rebuild
cargo watch -x "build --workspace"

# 4. Run tests continuously
cargo watch -x "test --workspace"

# 5. Check code quality
cargo clippy --workspace -- -D warnings
cargo fmt --all -- --check

# 6. Run full test suite
make test

# 7. Build release
cargo build --workspace --release

# 8. Commit and push
git add .
git commit -m "feat(scope): description"
git push origin feature/my-feature

# 9. Create PR on GitHub
```

### 6.4 Code Review Checklist

Before submitting:

-   [ ] Code compiles without warnings
-   [ ] All tests pass
-   [ ] New tests added for new features
-   [ ] Documentation updated
-   [ ] Code formatted with `cargo fmt`
-   [ ] Clippy passes with no warnings
-   [ ] Commit messages follow convention
-   [ ] No debug prints or commented code
-   [ ] Performance impact considered
-   [ ] Security implications reviewed

---

## 7. Debugging Techniques

### 7.1 Debugging Kernel Code

#### Using QEMU with GDB

```bash
# Terminal 1: Start QEMU with GDB server
qemu-system-x86_64 \
    -cdrom build/syn_os.iso \
    -m 2G \
    -s -S \
    -serial stdio

# Terminal 2: Connect GDB
gdb src/kernel/target/x86_64-unknown-none/debug/synos_kernel
(gdb) target remote localhost:1234
(gdb) break main
(gdb) continue
```

#### Common GDB Commands

```gdb
# Set breakpoint
break src/main.rs:42
break function_name

# Step through code
step      # Step into
next      # Step over
finish    # Step out
continue  # Continue execution

# Inspect variables
print variable_name
print *pointer
info locals
info args

# Backtrace
backtrace
frame 3
up
down

# Memory inspection
x/16x 0x1000  # Examine 16 bytes at 0x1000
x/s 0x1000    # Examine as string
```

### 7.2 Debugging Userspace Code

#### Using rust-lldb

```bash
# Build with debug symbols
cargo build --workspace

# Debug with lldb
rust-lldb target/debug/synos-service

# Set breakpoints
(lldb) breakpoint set --file main.rs --line 42
(lldb) breakpoint set --name function_name
(lldb) run

# Inspect
(lldb) print variable
(lldb) frame variable
(lldb) bt  # backtrace
```

### 7.3 Logging and Tracing

#### Add Logging

```rust
use tracing::{debug, info, warn, error};

pub fn my_function() {
    info!("Starting my_function");
    debug!(value = 42, "Processing value");
    warn!("This might be a problem");
    error!("Something went wrong!");
}
```

#### Configure Log Levels

```bash
# Set log level
export RUST_LOG=debug

# Module-specific levels
export RUST_LOG=synos_kernel=debug,synos_security=info

# Run with logging
cargo run
```

### 7.4 Performance Profiling

#### Using Flamegraph

```bash
# Install flamegraph
cargo install flamegraph

# Profile your code
cargo flamegraph --bin synos-service

# Open flamegraph.svg in browser
firefox flamegraph.svg
```

#### Using perf

```bash
# Record performance data
cargo build --release
perf record --call-graph dwarf ./target/release/synos-service

# View report
perf report
```

---

## 8. Testing Your Changes

### 8.1 Unit Tests

Write unit tests in the same file:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_my_function() {
        assert_eq!(my_function(2, 3), 5);
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_division_by_zero() {
        divide(10, 0);
    }
}
```

Run tests:

```bash
# Run all tests
cargo test --workspace

# Run specific test
cargo test test_my_function

# Run tests in specific package
cargo test --package synos-kernel

# Run with output
cargo test -- --nocapture
```

### 8.2 Integration Tests

Create files in `tests/` directory:

```rust
// tests/kernel_syscalls.rs
use synos_kernel::syscalls;

#[test]
fn test_syscall_read() {
    // Test implementation
}
```

### 8.3 Benchmark Tests

```rust
#![feature(test)]
extern crate test;

#[cfg(test)]
mod benchmarks {
    use super::*;
    use test::Bencher;

    #[bench]
    fn bench_my_function(b: &mut Bencher) {
        b.iter(|| {
            my_function(100)
        });
    }
}
```

Run benchmarks:

```bash
cargo bench --workspace
```

### 8.4 Test Coverage

```bash
# Install tarpaulin
cargo install cargo-tarpaulin

# Generate coverage report
cargo tarpaulin --workspace --out Html

# Open report
firefox tarpaulin-report.html
```

---

## 9. Code Quality Standards

### 9.1 Formatting

Always format code before committing:

```bash
# Format all code
cargo fmt --all

# Check formatting
cargo fmt --all -- --check
```

### 9.2 Linting

Run Clippy to catch common mistakes:

```bash
# Run clippy
cargo clippy --workspace

# Fail on warnings
cargo clippy --workspace -- -D warnings

# Fix automatically (when possible)
cargo clippy --workspace --fix
```

### 9.3 Documentation

Document all public APIs:

````rust
/// Calculates the sum of two numbers.
///
/// # Arguments
///
/// * `a` - The first number
/// * `b` - The second number
///
/// # Returns
///
/// The sum of `a` and `b`
///
/// # Examples
///
/// ```
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
````

Generate documentation:

```bash
# Build documentation
cargo doc --workspace --no-deps

# Open in browser
cargo doc --workspace --no-deps --open
```

### 9.4 Security Audit

```bash
# Install cargo-audit
cargo install cargo-audit

# Run security audit
cargo audit

# Check for outdated dependencies
cargo outdated
```

---

## 10. Submitting Changes

See **[Contributing Guide](Contributing.md)** for complete details.

### Quick Checklist

-   [ ] Feature branch created
-   [ ] Code compiles without warnings
-   [ ] All tests pass
-   [ ] New tests added
-   [ ] Code formatted (`cargo fmt`)
-   [ ] Clippy passes (`cargo clippy`)
-   [ ] Documentation updated
-   [ ] Conventional commit messages
-   [ ] PR description complete

---

## 11. Advanced Topics

### 11.1 Custom Targets

Build for different architectures:

```bash
# Add target
rustup target add aarch64-unknown-none

# Build for ARM64
cargo build --target aarch64-unknown-none
```

### 11.2 Cross-Compilation

```bash
# Install cross
cargo install cross

# Build with cross
cross build --target x86_64-unknown-linux-musl
```

### 11.3 Optimizing Build Times

```toml
# Add to Cargo.toml
[profile.dev]
opt-level = 0
debug = true
split-debuginfo = "unpacked"

[profile.dev.package."*"]
opt-level = 2  # Optimize dependencies

# Use mold linker (faster than lld)
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
```

### 11.4 Working with Submodules

```bash
# Update all submodules
git submodule update --remote

# Add new submodule
git submodule add https://github.com/user/repo.git path/to/submodule

# Initialize after clone
git submodule update --init --recursive
```

---

## 🎓 Learning Resources

### Internal Documentation

-   [Architecture Overview](Architecture-Overview.md)
-   [API Reference](API-Reference.md) (Coming Soon)
-   [Contributing Guide](Contributing.md)

### External Resources

**Rust**:

-   [The Rust Book](https://doc.rust-lang.org/book/)
-   [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
-   [The Rustonomicon](https://doc.rust-lang.org/nomicon/) (Unsafe Rust)

**OS Development**:

-   [OSDev.org](https://wiki.osdev.org/)
-   [Writing an OS in Rust](https://os.phil-opp.com/)

**AI/ML**:

-   [TensorFlow Documentation](https://www.tensorflow.org/)
-   [ONNX Runtime Documentation](https://onnxruntime.ai/)

---

## 🐛 Getting Help

-   **GitHub Issues**: Report bugs
-   **GitHub Discussions**: Ask questions
-   **DeepWiki**: AI-powered help at https://deepwiki.com/TLimoges33/Syn_OS
-   **Discord**: (Coming Soon)

---

**Last Updated**: October 4, 2025  
**Maintainer**: SynOS Development Team  
**License**: MIT

Happy coding! 🚀
