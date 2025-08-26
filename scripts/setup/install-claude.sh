#!/bin/bash

echo "🤖 Installing Claude Desktop for Codespace"
echo "=========================================="

# Check if running in a display environment
if [ -z "$DISPLAY" ]; then
    echo "⚠️  No display detected - setting up for VNC/X11 forwarding"
    export DISPLAY=:1
fi

# Create temporary directory
cd /tmp

# Function to download Claude Desktop
download_claude() {
    echo "📥 Downloading Claude Desktop AppImage..."
    
    # Try multiple download methods
    if command -v wget &> /dev/null; then
        wget -O claude-desktop.AppImage "https://storage.googleapis.com/claude-artifacts-prod/claude-desktop-latest-linux-x86_64.AppImage" 2>/dev/null && return 0
    fi
    
    if command -v curl &> /dev/null; then
        curl -L -o claude-desktop.AppImage "https://storage.googleapis.com/claude-artifacts-prod/claude-desktop-latest-linux-x86_64.AppImage" 2>/dev/null && return 0
    fi
    
    echo "❌ Download failed with both wget and curl"
    return 1
}

# Function to install Claude Desktop
install_claude() {
    if [ -f "claude-desktop.AppImage" ]; then
        echo "📦 Installing Claude Desktop..."
        chmod +x claude-desktop.AppImage
        
        # Install to user bin directory
        mkdir -p ~/.local/bin
        mv claude-desktop.AppImage ~/.local/bin/claude
        
        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            export PATH="$HOME/.local/bin:$PATH"
        fi
        
        echo "✅ Claude Desktop installed successfully!"
        echo "🚀 You can now run: claude"
        return 0
    else
        echo "❌ Claude Desktop AppImage not found"
        return 1
    fi
}

# Function to create desktop entry (for VNC access)
create_desktop_entry() {
    mkdir -p ~/.local/share/applications
    cat > ~/.local/share/applications/claude.desktop << 'EOF'
[Desktop Entry]
Name=Claude Desktop
Comment=AI Assistant by Anthropic
Exec=/home/codespace/.local/bin/claude
Icon=claude
Terminal=false
Type=Application
Categories=Office;Development;
EOF
    echo "📱 Desktop entry created for VNC access"
}

# Function to test Claude installation
test_claude() {
    echo "🧪 Testing Claude installation..."
    if command -v claude &> /dev/null; then
        echo "✅ Claude command found in PATH"
        
        # Test if Claude can start (in background)
        timeout 10s claude --version 2>/dev/null && echo "✅ Claude starts successfully" || echo "⚠️  Claude may need display environment"
        
        return 0
    else
        echo "❌ Claude command not found"
        return 1
    fi
}

# Main installation process
echo "🔍 Checking if Claude is already installed..."
if command -v claude &> /dev/null; then
    echo "✅ Claude Desktop is already installed!"
    claude --version 2>/dev/null || echo "Claude is installed but may need display environment"
    exit 0
fi

echo "📦 Starting Claude Desktop installation..."

# Download Claude
if download_claude; then
    echo "✅ Download successful"
else
    echo "❌ Failed to download Claude Desktop"
    echo "📝 Manual installation instructions:"
    echo "1. Go to: https://claude.ai/download"
    echo "2. Download the Linux AppImage"
    echo "3. Upload to your codespace"
    echo "4. Run: chmod +x claude-*.AppImage && mv claude-*.AppImage ~/.local/bin/claude"
    exit 1
fi

# Install Claude
if install_claude; then
    echo "✅ Installation successful"
else
    echo "❌ Installation failed"
    exit 1
fi

# Create desktop entry for VNC
create_desktop_entry

# Test installation
test_claude

echo ""
echo "🎉 Claude Desktop Setup Complete!"
echo ""
echo "📋 How to use Claude in your Codespace:"
echo ""
echo "🖥️  Via Command Line:"
echo "   claude                 # Launch Claude Desktop"
echo ""
echo "🖱️  Via VNC (if using desktop environment):"
echo "   1. Connect to VNC on port 5901"
echo "   2. Password: vscode"
echo "   3. Look for Claude icon in applications menu"
echo ""
echo "⚠️  Note: Claude Desktop is a GUI application"
echo "   - Works best with VNC/X11 forwarding"
echo "   - May need display environment setup"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If 'claude' command not found: source ~/.bashrc"
echo "   - If display issues: export DISPLAY=:1"
echo "   - If permission issues: chmod +x ~/.local/bin/claude"
