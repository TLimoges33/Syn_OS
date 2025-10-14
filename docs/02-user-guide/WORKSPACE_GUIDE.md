# SynOS Ultimate Developer Workspace Guide

## Quick Start

### Opening the Workspace

```bash
# From command line
code SynOS-Ultimate-Developer.code-workspace

# Or from VS Code
File > Open Workspace from File > SynOS-Ultimate-Developer.code-workspace
```

### First Time Setup

1. **Install Recommended Extensions** (prompt will appear automatically)

    - Rust Analyzer (essential for kernel development)
    - Python + Pylint (for AI engine scripting)
    - Docker (for containerized builds)
    - GitLens (enhanced git integration)
    - Markdown All in One (documentation)

2. **Verify Rust Toolchain**

    ```bash
    rustup show  # Should show x86_64-unknown-none target
    ```

3. **Test Build System**
    - Press `Ctrl+Shift+B` to see available build tasks
    - Try: "🔨 Build Complete Workspace"

## Workspace Structure

The workspace is organized into **focused folder views** for efficient navigation:

```
Workspace Folders:
├── 🧠 SynOS Linux Distribution (Root)    # Full project view
├── 🤖 AI Engine & Consciousness System   # src/ai-engine/
├── 🔧 Kernel Core & System               # src/kernel/
├── 🛡️ Security Framework & Tools         # core/security/
├── 🐧 Linux Distribution Builder         # linux-distribution/
├── 🚀 Build & Deployment Scripts         # scripts/
├── 🧪 Testing & Validation Suite         # tests/
├── 📚 Documentation & Architecture       # docs/
├── ⚙️ Configuration (Unified)            # config/
├── 🔧 Core Libraries & Frameworks        # core/
├── 🚀 Deployment & Operations            # deployment/
└── 🛠️ Development Tools                  # development/
```

## Built-in Tasks

Access via `Ctrl+Shift+B` or `Terminal > Run Task`:

### Build Tasks

-   **🔨 Build Complete Workspace** - Full workspace build (default)
-   **🤖 Build AI Engine** - Consciousness system compilation
-   **🔧 Build Kernel** - Bare-metal kernel (x86_64-unknown-none)
-   **🛡️ Build Security Framework** - Security tools compilation
-   **🐧 Build SynOS Linux Distribution** - Complete Linux distro
-   **🚀 Build Production ISO** - Bootable ISO image

### Test Tasks

-   **🧪 Run Complete Test Suite** - All tests (default)
-   **📊 Run Comprehensive Security Audit** - Security validation
-   **🔍 Vulnerability Scan** - Master security suite
-   **🎯 Cybersec Tools Test** - Tools validation

### Utility Tasks

-   **🧹 Clean All Build Artifacts** - Clean workspace
-   **📦 Package Distribution** - Create release package
-   **🔄 Update Documentation** - Regenerate docs

## Debug Configurations

Press `F5` to launch debugger with these configurations:

-   **🔧 Debug Kernel** - LLDB for bare-metal kernel
-   **🤖 Debug AI Engine** - LLDB for AI/consciousness system
-   **🛡️ Debug Security Framework** - Security tools debugging
-   **🐍 Debug Python Scripts** - Python debugger (current file)

## Terminal Profiles

Custom terminal profiles optimized for SynOS development:

1. **SynOS Development Shell** (default)

    - Pre-configured environment variables
    - Cargo optimization settings
    - Python bytecode disabled
    - Custom PATH with scripts/

2. **Security Testing Shell**
    - Full Rust backtraces
    - Security mode enabled
    - Security tools in PATH

Access via terminal dropdown or `Ctrl+Shift+\``

## Performance Optimizations

The workspace includes several performance optimizations:

### File Indexing

-   **~70% reduction** in indexed files through intelligent exclusions
-   Excludes: `target/`, `build/`, `logs/`, `archive/`, large build artifacts
-   Linux distribution build cache excluded (25GB)

### Rust Analyzer

-   Configured for bare-metal kernel target (`x86_64-unknown-none`)
-   Custom feature flags for consciousness/security systems
-   Linked projects for multi-crate workspace
-   Optimized cargo check (clippy + limited targets)

### Editor

-   Smart case search
-   5000 result limit (balance between completeness and speed)
-   8 editor limit (memory management)
-   Large file support (1GB max)

## Key Keyboard Shortcuts

| Shortcut          | Action                   |
| ----------------- | ------------------------ |
| `Ctrl+Shift+B`    | Show build tasks         |
| `F5`              | Start debugging          |
| `Ctrl+Shift+P`    | Command palette          |
| `Ctrl+P`          | Quick file open          |
| `Ctrl+Shift+F`    | Search in files          |
| ` Ctrl+`` `       | Toggle terminal          |
| ` Ctrl+Shift+`` ` | New terminal             |
| `Ctrl+K Ctrl+O`   | Open folder in workspace |

## File Associations

Special file types configured for Linux distribution development:

-   `*.service`, `*.socket`, `*.timer` → Systemd unit files
-   `*.deb`, `*.iso`, `*.squashfs` → Binary packages
-   `sources.list*`, `*.list` → Debian package sources
-   `*.rules` → Udev rules
-   `*.desktop` → Desktop entries
-   `Dockerfile*` → Docker configurations

## Common Workflows

### Building the Kernel

```bash
# Via task (recommended)
Ctrl+Shift+B → "🔧 Build Kernel"

# Or manual
cargo build --manifest-path src/kernel/Cargo.toml --target x86_64-unknown-none
```

### Building Complete ISO

```bash
# Via task
Ctrl+Shift+B → "🚀 Build Production ISO"

# Result
build/syn_os.iso
```

### Running Security Audit

```bash
# Via task
Ctrl+Shift+P → Run Task → "📊 Run Comprehensive Security Audit"

# Or terminal
python3 deployment/operations/admin/comprehensive-architecture-audit.py
```

### Testing AI Engine

```bash
# Build first
Ctrl+Shift+B → "🤖 Build AI Engine"

# Then debug
F5 → Select "🤖 Debug AI Engine"
```

## Troubleshooting

### Rust Analyzer Not Working

1. Check rust-toolchain.toml exists
2. Verify target installed: `rustup target list --installed`
3. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Performance Issues

1. Check file exclusions are working
2. Close unnecessary editor tabs (8 max recommended)
3. Disable minimap if needed: `View > Toggle Minimap`

### Build Failures

1. Clean build artifacts: Run "🧹 Clean All Build Artifacts" task
2. Update dependencies: `cargo update`
3. Check Cargo.lock isn't corrupted

### Python Import Errors

1. Verify virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Check PYTHONPATH in terminal profile

## Extension Recommendations

### Essential

-   `rust-lang.rust-analyzer` - Rust language support
-   `ms-python.python` - Python support
-   `ms-vscode.cpptools` - C/C++ support (for kernel interfacing)

### Highly Recommended

-   `eamodio.gitlens` - Git superchargers
-   `ms-azuretools.vscode-docker` - Docker support
-   `yzhang.markdown-all-in-one` - Documentation

### Security

-   `snyk-security.snyk-vulnerability-scanner` - Vulnerability scanning

### Optional

-   `hediet.vscode-drawio` - Architecture diagrams
-   `ms-vscode.hexeditor` - Binary file editing
-   `13xforever.language-x86-64-assembly` - Assembly syntax

## Environment Variables

The workspace sets these environment variables automatically:

```bash
RUST_BACKTRACE=1              # Full Rust error traces
SYNOS_DEV_MODE=1              # Development mode flag
CARGO_TARGET_DIR=./target     # Consistent cargo output
CARGO_BUILD_JOBS=2            # Limit parallel builds (memory)
PYTHONDONTWRITEBYTECODE=1     # No .pyc files
SYNOS_PROJECT_ROOT=.          # Project root reference
CYBERSEC_TOOLS_PATH=./core/security/tools  # Security tools
```

## Configuration Files

The workspace respects these configuration files:

-   `Cargo.toml` - Workspace dependencies
-   `rust-toolchain.toml` - Rust version/target
-   `.editorconfig` - Editor settings
-   `.gitignore` - Git exclusions
-   `Makefile` - Build system
-   `config/` - Runtime configurations

## Getting Help

1. **Documentation**: Check `docs/` directory
2. **Architecture**: See `docs/project-status/ARCHITECTURAL_REORGANIZATION_COMPLETE.md`
3. **Security**: Review `docs/security/SECURITY_AUDIT_COMPLETE.md`
4. **Planning**: See `docs/planning/` for roadmaps

## Updates & Maintenance

To keep the workspace current:

1. **Update Extensions**: `Ctrl+Shift+P` → "Extensions: Update All Extensions"
2. **Update Rust**: `rustup update`
3. **Update Workspace**: Pull latest from git, workspace config auto-updates

---

**Last Updated:** October 2, 2025  
**Workspace Version:** 2.0 (Post-Architectural Reorganization)  
**Maintainer:** SynOS Development Team
