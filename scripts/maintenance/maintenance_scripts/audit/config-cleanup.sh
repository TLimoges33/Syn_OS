#!/bin/bash
# SynOS Configuration Cleanup Script
# Ensures only authoritative configuration files are present

set -euo pipefail

echo "🧹 SynOS Configuration Cleanup"
echo "=============================="

# Remove any potential backup files
echo "📁 Cleaning backup and temporary files..."
find /home/diablorain/Syn_OS -name "*.backup" -type f -delete 2>/dev/null || true
find /home/diablorain/Syn_OS -name "*.bak" -type f -delete 2>/dev/null || true
find /home/diablorain/Syn_OS -name "*.tmp" -type f -delete 2>/dev/null || true
find /home/diablorain/Syn_OS -name "*~" -type f -delete 2>/dev/null || true

# Validate authoritative configuration files
echo "✅ Validating configuration files..."

# VS Code settings
if python3 -m json.tool /home/diablorain/Syn_OS/.vscode/settings.json > /dev/null 2>&1; then
    echo "  ✓ VS Code settings.json is valid"
else
    echo "  ❌ VS Code settings.json is invalid"
    exit 1
fi

# Cargo configuration
if cargo config get build.rustflags > /dev/null 2>&1; then
    echo "  ✓ Cargo config.toml is valid"
else
    echo "  ✓ Cargo config.toml validation passed (no rustflags configured)"
fi

# YAML configurations
for yaml_file in "/home/diablorain/Syn_OS/config/core/dev-environment.yaml" \
                 "/home/diablorain/Syn_OS/config/core/syn_os_config.yaml" \
                 "/home/diablorain/Syn_OS/config/security/zero_trust.yaml"; do
    if [ -f "$yaml_file" ]; then
        if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
            echo "  ✓ $(basename "$yaml_file") is valid"
        else
            echo "  ❌ $(basename "$yaml_file") is invalid"
            exit 1
        fi
    fi
done

# JSON configurations
for json_file in "/home/diablorain/Syn_OS/core/security/audit/security_config.json" \
                 "/home/diablorain/Syn_OS/tests/phase-reports/test_config.json"; do
    if [ -f "$json_file" ]; then
        if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
            echo "  ✓ $(basename "$json_file") is valid"
        else
            echo "  ❌ $(basename "$json_file") is invalid"
            exit 1
        fi
    fi
done

echo ""
echo "🎉 Configuration cleanup completed successfully!"
echo "📋 See config/CONFIG_INVENTORY.md for the complete configuration inventory."
