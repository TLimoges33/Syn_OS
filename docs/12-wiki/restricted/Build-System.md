# 🔨 Build System Reference

**Build Tools**: Make, Cargo, Docker  
**Targets**: Kernel, userspace, ISO, containers

---

## Quick Start

```bash
# Build everything
make all

# Build kernel only
make kernel

# Build ISO
make iso

# Clean
make clean

# Run tests
make test
```

---

## Makefile Targets

### Core Targets

| Target | Description |
|--------|-------------|
| `all` | Build everything |
| `kernel` | Build kernel |
| `userspace` | Build userspace tools |
| `iso` | Create bootable ISO |
| `docker` | Build Docker images |
| `test` | Run all tests |
| `clean` | Remove build artifacts |

### Development Targets

| Target | Description |
|--------|-------------|
| `dev` | Development build |
| `release` | Release build (optimized) |
| `debug` | Debug build (symbols) |
| `docs` | Generate documentation |

---

## Cargo Workspaces

### Kernel Workspace

```bash
cd src/kernel
cargo build --target x86_64-unknown-none
cargo test --target x86_64-unknown-linux-gnu
```

### Security Workspace

```bash
cd core/security
cargo build --release
cargo test
```

---

## Build Configuration

### Config Files

- `Cargo.toml` - Rust dependencies
- `Makefile` - Build orchestration
- `rust-toolchain.toml` - Rust version
- `.cargo/config.toml` - Cargo config

### Environment Variables

```bash
# Build type
export BUILD_TYPE=release

# Target architecture
export ARCH=x86_64

# Number of jobs
export MAKE_JOBS=8
```

---

## Custom Builds

### Minimal Kernel

```bash
# Edit config
vim src/kernel/.config

# Disable features
CONFIG_AI_ENGINE=n
CONFIG_SECURITY_ADVANCED=n

# Build
make kernel-minimal
```

### Custom ISO

```bash
# Edit ISO config
vim config/iso-config.yml

# Set packages
packages:
  - base
  - network
  # (exclude ai, security)

# Build
make iso-custom
```

---

## Troubleshooting

### Build Fails

```bash
# Clean and rebuild
make clean && make all

# Check dependencies
./scripts/check-dependencies.sh

# Verbose output
make V=1 all
```

### Slow Builds

```bash
# Parallel builds
make -j$(nproc) all

# Incremental builds
cargo build --incremental

# Cache builds
sccache cargo build
```

---

**For advanced**: See `BUILD.md` in project root
