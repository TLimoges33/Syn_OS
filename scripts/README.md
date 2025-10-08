# 🔧 Syn_OS Scripts

This directory contains all automation scripts for building, testing, and maintaining Syn_OS.

## 📁 Directory Structure

```
scripts/
├── build/          Build ISO images
├── setup/          Environment setup
├── testing/        Test scripts
├── maintenance/    Maintenance tools
├── deployment/     Deployment scripts
├── development/    Development tools
├── ai-services/    AI service management
├── migration/      Code migration tools
└── archive/        Old/deprecated scripts
```

## 🚀 Quick Start

### Build the Ultimate ISO
```bash
cd scripts/build
sudo ./build-synos-ultimate-iso.sh
```

### Test ISO in QEMU
```bash
cd scripts/testing
./test-iso-in-qemu.sh
```

### Setup Development Environment
```bash
cd scripts/setup
./setup-development-environment.sh
```

## 📖 Detailed Documentation

### Build Scripts (`build/`)
- **build-synos-ultimate-iso.sh** - Complete ISO with 500+ tools (MAIN)
- **build-synos-minimal-iso.sh** - Minimal ISO without security tools
- **build-synos-kernel-iso.sh** - Kernel-only bootable ISO

### Testing Scripts (`testing/`)
- **test-iso-in-qemu.sh** - Test ISO in QEMU emulator
- **test-ai-services.sh** - Validate AI services
- **test-security-tools.sh** - Verify security tools

### Maintenance Scripts (`maintenance/`)
- **clean-build-artifacts.sh** - Clean build directories
- **clean-memory.sh** - Free up system memory
- **validate-production-readiness.sh** - Production checks

### AI Services (`ai-services/`)
- **package-ai-services.sh** - Package AI services as .deb
- **compress-ai-models.py** - Compress AI models
- **check-ai-daemon-status.sh** - Check service status

## 🔐 Permissions

Most scripts require specific permissions:
- **Build scripts**: Require `sudo` (root access)
- **Testing scripts**: User permissions
- **Maintenance scripts**: Some require `sudo`

## ⚠️ Important Notes

- Always run build scripts with `sudo`
- Review scripts before execution
- Check system requirements first
- Read script documentation

## 📚 More Information

See [docs/building/](../docs/building/) for detailed build documentation.
