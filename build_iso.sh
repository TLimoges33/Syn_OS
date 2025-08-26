#!/bin/bash
# Manual ISO build trigger
echo "🏗️ Building Syn_OS ISO"
if [ -f "scripts/build-simple-kernel-iso.sh" ]; then
    chmod +x scripts/build-simple-kernel-iso.sh
    ./scripts/build-simple-kernel-iso.sh
    echo "✅ ISO build complete"
    find build/ -name "*.iso" -exec echo "📀 Generated: {}" \;
else
    echo "❌ ISO build script not found"
fi
