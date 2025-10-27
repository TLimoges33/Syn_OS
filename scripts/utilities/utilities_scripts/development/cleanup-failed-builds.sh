#!/bin/bash

# SynOS Development Cleanup Script
# Removes failed build methodologies and organizes for production

echo "🧹 SynOS Development Cleanup - Removing Failed Build Methodologies"
echo "=================================================================="

# Create archive directory for failed attempts
mkdir -p /home/diablorain/Syn_OS/development/archive/failed-builds

echo "📁 Archiving failed build attempts..."

# Archive lightweight build strategy (partial/incomplete)
if [ -d "/home/diablorain/Syn_OS/development/lightweight-build-strategy" ]; then
    echo "  ↳ Archiving lightweight-build-strategy..."
    mv /home/diablorain/Syn_OS/development/lightweight-build-strategy \
       /home/diablorain/Syn_OS/development/archive/failed-builds/
fi

# Archive multi-track development (overcomplicated)
if [ -d "/home/diablorain/Syn_OS/development/multi-track-os-development" ]; then
    echo "  ↳ Archiving multi-track-os-development..."
    mv /home/diablorain/Syn_OS/development/multi-track-os-development \
       /home/diablorain/Syn_OS/development/archive/failed-builds/
fi

# Archive prototypes that didn't work
if [ -d "/home/diablorain/Syn_OS/development/prototypes" ]; then
    echo "  ↳ Archiving incomplete prototypes..."
    mv /home/diablorain/Syn_OS/development/prototypes \
       /home/diablorain/Syn_OS/development/archive/failed-builds/
fi

# Archive research integration attempts
if [ -d "/home/diablorain/Syn_OS/development/research-integration" ]; then
    echo "  ↳ Archiving research-integration attempts..."
    mv /home/diablorain/Syn_OS/development/research-integration \
       /home/diablorain/Syn_OS/development/archive/failed-builds/
fi

# Clean up redundant files
echo "🗑️  Removing redundant configuration files..."
rm -f /home/diablorain/Syn_OS/development/package-lock.json
rm -f /home/diablorain/Syn_OS/development/Makefile.optimized

# Verify complete-docker-strategy is intact
echo "✅ Verifying complete-docker-strategy integrity..."
if [ -f "/home/diablorain/Syn_OS/development/complete-docker-strategy/synos-dev" ]; then
    echo "  ↳ synos-dev orchestrator: ✅ Present"
else
    echo "  ↳ synos-dev orchestrator: ❌ MISSING!"
    exit 1
fi

if [ -f "/home/diablorain/Syn_OS/development/complete-docker-strategy/docker-compose.yml" ]; then
    echo "  ↳ docker-compose.yml: ✅ Present"
else
    echo "  ↳ docker-compose.yml: ❌ MISSING!"
    exit 1
fi

if [ -d "/home/diablorain/Syn_OS/development/complete-docker-strategy/docker" ]; then
    echo "  ↳ Docker configurations: ✅ Present"
else
    echo "  ↳ Docker configurations: ❌ MISSING!"
    exit 1
fi

# Set proper permissions
echo "🔧 Setting proper permissions..."
chmod +x /home/diablorain/Syn_OS/development/complete-docker-strategy/synos-dev
chmod -R 755 /home/diablorain/Syn_OS/development/complete-docker-strategy/docker/

# Create development shortcuts
echo "🔗 Creating development shortcuts..."
cd /home/diablorain/Syn_OS/development

# Create quick access symlink
ln -sf complete-docker-strategy/synos-dev synos-dev

# Update development directory structure
echo "📁 Final development directory structure:"
echo "========================================"
ls -la /home/diablorain/Syn_OS/development/ | grep -E "(complete-docker-strategy|synos-dev|archive)"

echo ""
echo "🎉 Cleanup Complete!"
echo "==================="
echo ""
echo "✅ Working Strategy: complete-docker-strategy/"
echo "📁 Archived Failed Attempts: archive/failed-builds/"
echo "🔗 Quick Access: ./synos-dev (symlink to complete-docker-strategy/synos-dev)"
echo ""
echo "🚀 Ready to proceed with production build:"
echo "   cd /home/diablorain/Syn_OS/development/complete-docker-strategy"
echo "   ./synos-dev start"
echo ""
