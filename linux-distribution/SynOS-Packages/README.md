# SynOS Custom Packages

This directory contains the source and build configurations for SynOS-specific packages:

## Core AI Components

- **synos-ai-daemon**: Background service for AI consciousness processing
- **synos-neural-darwinism**: Neural Darwinism consciousness framework implementation
- **synos-security-orchestrator**: AI-powered security tool orchestration system
- **synos-mate-desktop**: Customized MATE desktop with SynOS branding and AI integration

## Package Structure

Each package follows standard Debian packaging conventions:
- `debian/` - Debian packaging control files
- `src/` - Source code
- `data/` - Configuration files, themes, assets
- `docs/` - Package documentation

## Building Packages

```bash
# Build individual package
cd synos-ai-daemon
debuild -us -uc

# Build all packages
./build-all-packages.sh
```

## Repository Management

Packages are automatically added to the SynOS repository in `/SynOS-Repository/` after building.