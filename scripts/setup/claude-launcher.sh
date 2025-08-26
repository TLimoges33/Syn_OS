#!/bin/bash

echo "🤖 Claude Desktop Launcher"
echo "=========================="

# Check if Claude is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Desktop not found!"
    echo "📦 Installing Claude Desktop..."
    bash /tmp/install-claude.sh
    exit $?
fi

# Check if we're in a desktop environment
if [ -z "$DISPLAY" ]; then
    echo "⚠️  No display environment detected"
    echo ""
    echo "🖥️  To use Claude Desktop in Codespace:"
    echo ""
    echo "Option 1: VNC Access (Recommended)"
    echo "1. Open port 6080 in your browser (should auto-open)"
    echo "2. Password: vscode"
    echo "3. Click Claude icon or run from terminal"
    echo ""
    echo "Option 2: Set up display forwarding"
    echo "export DISPLAY=:1"
    echo "claude &"
    echo ""
    echo "Option 3: Use Claude via web"
    echo "Open: https://claude.ai in your browser"
    echo ""
    read -p "Press Enter to try launching Claude anyway, or Ctrl+C to exit..."
fi

# Try to launch Claude
echo "🚀 Launching Claude Desktop..."
claude &

# Give it a moment to start
sleep 2

# Check if process started
if pgrep -f claude > /dev/null; then
    echo "✅ Claude Desktop is running!"
    echo "🖱️  Switch to VNC viewer or check port 6080 to see the interface"
else
    echo "⚠️  Claude Desktop may not have started properly"
    echo "🔧 Troubleshooting:"
    echo "   - Check VNC connection on port 6080"
    echo "   - Try: export DISPLAY=:1 && claude"
    echo "   - Or use web version at: https://claude.ai"
fi
