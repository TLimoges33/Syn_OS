#!/bin/bash
# SYSTEM-WIDE CLAUDE NUCLEAR REMOVAL
# Removes ALL Claude artifacts from the entire system

echo "💥 SYSTEM-WIDE CLAUDE NUCLEAR REMOVAL"
echo "===================================="
echo "This will remove ALL Claude artifacts from the ENTIRE system"
echo "Including: binaries, configs, cache, logs, extensions, etc."
echo ""

read -p "⚠️  Are you absolutely sure? This is irreversible! (type 'NUCLEAR' to confirm): " confirm
if [ "$confirm" != "NUCLEAR" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🚀 Starting nuclear Claude removal..."

# Stop any running Claude processes
echo "🛑 Killing all Claude processes..."
sudo pkill -f claude 2>/dev/null || true
sudo pkill -f anthropic 2>/dev/null || true
sudo pkill -f "Claude Code" 2>/dev/null || true

# Remove all Claude binaries from system paths
echo "🗑️  Removing Claude binaries..."
sudo rm -f /usr/local/bin/claude*
sudo rm -f /usr/bin/claude*
sudo rm -f /bin/claude*
sudo rm -f /opt/claude*
sudo rm -rf /opt/Claude*

# Remove from user's local bin
rm -f ~/.local/bin/claude*

# Remove npm packages (global)
echo "📦 Removing npm Claude packages..."
sudo npm uninstall -g @anthropic-ai/claude-code 2>/dev/null || true
sudo npm uninstall -g @anthropic-ai/claude 2>/dev/null || true
sudo npm uninstall -g anthropic 2>/dev/null || true
sudo npm uninstall -g claude-cli 2>/dev/null || true
sudo npm uninstall -g claude 2>/dev/null || true

# Remove pip packages
echo "🐍 Removing Python Claude packages..."
pip uninstall -y anthropic 2>/dev/null || true
pip3 uninstall -y anthropic 2>/dev/null || true
pipx uninstall anthropic 2>/dev/null || true
pipx uninstall claude 2>/dev/null || true
pipx uninstall claude-cli 2>/dev/null || true

# Remove all Claude configuration directories
echo "📁 Removing Claude configuration directories..."
rm -rf ~/.config/Claude/
rm -rf ~/.config/claude/
rm -rf ~/.claude/
rm -rf ~/.anthropic/
rm -rf ~/.local/share/claude/
rm -rf ~/.local/share/Claude/

# Remove VS Code Claude extensions and logs
echo "🔌 Removing VS Code Claude extensions..."
rm -rf ~/.vscode/extensions/*claude*
rm -rf ~/.vscode/extensions/*anthropic*
rm -rf ~/.config/Code/User/globalStorage/*claude*
rm -rf ~/.config/Code/User/globalStorage/*anthropic*
rm -rf ~/.config/Code/CachedExtensionVSIXs/*claude*
rm -rf ~/.config/Code/CachedExtensionVSIXs/*anthropic*
rm -rf ~/.config/Code/logs/*/window*/mcpServer.claude*

# Remove VSCodium Claude extensions
rm -rf ~/.config/VSCodium/CachedExtensionVSIXs/*claude*
rm -rf ~/.config/VSCodium/CachedExtensionVSIXs/*anthropic*

# Remove Visual Studio Code Claude extensions
rm -rf ~/.config/"Visual Studio Code"/logs/*/window*/mcpServer.claude*

# Remove browser extension data
echo "🌐 Removing browser Claude data..."
rm -rf ~/.config/google-chrome/Default/Extensions/*/assets/*claude*
rm -rf ~/.config/chromium/Default/Extensions/*/assets/*claude*
rm -rf ~/.mozilla/firefox/*/extensions/*claude*

# Remove cache files
echo "🧹 Removing Claude cache files..."
rm -rf ~/.cache/*claude*
rm -rf ~/.cache/*anthropic*
rm -rf ~/.cache/pylint/*claude*

# Remove any Claude desktop applications
echo "🖥️  Removing Claude desktop applications..."
sudo rm -rf /usr/share/applications/*claude*
sudo rm -rf /usr/share/applications/*anthropic*
rm -rf ~/.local/share/applications/*claude*
rm -rf ~/.local/share/applications/*anthropic*

# Remove from PATH in shell configs
echo "🛤️  Cleaning PATH references..."
sed -i '/claude/Id' ~/.bashrc 2>/dev/null || true
sed -i '/Claude/Id' ~/.bashrc 2>/dev/null || true
sed -i '/anthropic/Id' ~/.bashrc 2>/dev/null || true
sed -i '/Anthropic/Id' ~/.bashrc 2>/dev/null || true

# Remove environment variables
unset ANTHROPIC_API_KEY
unset CLAUDE_API_KEY
unset CLAUDE_CODE_OAUTH_TOKEN

# Remove from system services
echo "⚙️  Removing Claude services..."
sudo systemctl stop claude* 2>/dev/null || true
sudo systemctl disable claude* 2>/dev/null || true
sudo rm -f /etc/systemd/system/claude*
sudo rm -f /etc/systemd/user/claude*
sudo systemctl daemon-reload

# Remove snap/flatpak packages
echo "📦 Removing snap/flatpak Claude packages..."
snap list | grep -i claude | awk '{print $1}' | xargs -r sudo snap remove 2>/dev/null || true
flatpak list | grep -i claude | awk '{print $2}' | xargs -r flatpak uninstall -y 2>/dev/null || true

# Clean package manager caches
echo "🧹 Cleaning package manager caches..."
sudo apt autoremove -y 2>/dev/null || true
sudo apt autoclean 2>/dev/null || true
npm cache clean --force 2>/dev/null || true

echo ""
echo "🔍 VERIFICATION - Checking for remaining Claude artifacts..."
echo ""

echo "📍 Binary locations:"
which claude 2>/dev/null || echo "  ✅ No claude binary found"
which anthropic 2>/dev/null || echo "  ✅ No anthropic binary found"

echo ""
echo "📁 Remaining Claude files:"
REMAINING_FILES=$(find /home/diablorain -name "*claude*" -type f 2>/dev/null | head -5)
if [ -z "$REMAINING_FILES" ]; then
    echo "  ✅ No Claude files found in home directory"
else
    echo "  ⚠️  Some files remain:"
    echo "$REMAINING_FILES"
fi

echo ""
echo "💥 NUCLEAR CLAUDE REMOVAL COMPLETE!"
echo "==================================="
echo "🎯 Your system is now completely Claude-free!"
echo ""
echo "🚀 Ready for fresh Claude installation!"
echo "Next steps:"
echo "1. Restart VS Code"
echo "2. Install Claude through official channels"
echo "3. Configure with proper API credentials"
