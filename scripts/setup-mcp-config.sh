#!/bin/bash

# Cross-platform MCP configuration setup script
# This script detects the OS and creates the appropriate symlink/copy

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KILOCODE_DIR="$PROJECT_ROOT/.kilocode"
MCP_CONFIG_PATH="$KILOCODE_DIR/mcp.json"

echo -e "\033[32mSetting up MCP configuration for current OS...\033[0m"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux" ]]; then
    echo -e "\033[36mDetected Linux OS\033[0m"
    SOURCE_CONFIG="$KILOCODE_DIR/mcp-linux.json"
    
    # Remove existing config if it exists
    if [ -f "$MCP_CONFIG_PATH" ] || [ -L "$MCP_CONFIG_PATH" ]; then
        rm -f "$MCP_CONFIG_PATH"
    fi
    
    # Create symlink
    ln -s "$SOURCE_CONFIG" "$MCP_CONFIG_PATH"
    echo -e "\033[32mLinux MCP configuration applied successfully!\033[0m"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "\033[36mDetected macOS\033[0m"
    SOURCE_CONFIG="$KILOCODE_DIR/mcp-linux.json"
    
    # Remove existing config if it exists
    if [ -f "$MCP_CONFIG_PATH" ] || [ -L "$MCP_CONFIG_PATH" ]; then
        rm -f "$MCP_CONFIG_PATH"
    fi
    
    # Create symlink
    ln -s "$SOURCE_CONFIG" "$MCP_CONFIG_PATH"
    echo -e "\033[32mmacOS MCP configuration applied successfully!\033[0m"
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo -e "\033[36mDetected Windows (Git Bash/WSL)\033[0m"
    SOURCE_CONFIG="$KILOCODE_DIR/mcp-windows.json"
    
    # Remove existing config if it exists
    if [ -f "$MCP_CONFIG_PATH" ]; then
        rm -f "$MCP_CONFIG_PATH"
    fi
    
    # Copy file (symlinks don't work well on Windows)
    cp "$SOURCE_CONFIG" "$MCP_CONFIG_PATH"
    echo -e "\033[32mWindows MCP configuration applied successfully!\033[0m"
    
else
    echo -e "\033[33mUnable to detect OS. Please manually copy the appropriate config:\033[0m"
    echo "  - For Windows: copy .kilocode/mcp-windows.json to .kilocode/mcp.json"
    echo "  - For Linux/macOS: copy .kilocode/mcp-linux.json to .kilocode/mcp.json"
fi

echo -e "\n\033[32mConfiguration complete! Restart VS Code to apply changes.\033[0m"

# Make the script executable
chmod +x "$SCRIPT_DIR/setup-mcp-config.sh"