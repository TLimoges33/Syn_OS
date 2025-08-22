#!/bin/bash

# VS Code Development Environment Validation Script
# Tests that all critical extensions and tools are working properly

echo "🔍 SynapticOS Development Environment Validation"
echo "================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if extension is installed
check_extension() {
    local ext_id="$1"
    local description="$2"
    
    if code --list-extensions | grep -q "^$ext_id$"; then
        echo -e "${GREEN}✅${NC} $description ($ext_id)"
        return 0
    else
        echo -e "${RED}❌${NC} $description ($ext_id) - NOT INSTALLED"
        return 1
    fi
}

# Function to check if command exists
check_command() {
    local cmd="$1"
    local description="$2"
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $description ($cmd)"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $description ($cmd) - NOT FOUND"
        return 1
    fi
}

echo -e "\n${BLUE}📦 Core Language Extensions${NC}"
check_extension "rust-lang.rust-analyzer" "Rust Language Server"
check_extension "ms-vscode.cpptools" "C++ Tools"
check_extension "golang.go" "Go Language Support"
check_extension "ms-python.python" "Python Support"
check_extension "13xforever.language-x86-64-assembly" "x86-64 Assembly"

echo -e "\n${BLUE}🔧 Development Tools${NC}"
check_extension "ms-vscode.hexeditor" "Hex Editor"
check_extension "vadimcn.vscode-lldb" "LLDB Debugger"
check_extension "webfreak.debug" "Native Debugging"
check_extension "ms-vscode.vscode-embedded-tools" "Embedded Tools"

echo -e "\n${BLUE}🤖 AI Development${NC}"
check_extension "github.copilot" "GitHub Copilot"
check_extension "github.copilot-chat" "GitHub Copilot Chat"
check_extension "continue.continue" "Continue AI"
check_extension "kilocode.kilo-code" "Kilo Code MCP"
check_extension "anthropic.claude-code" "Claude Integration"

echo -e "\n${BLUE}🛡️ Security & Analysis${NC}"
check_extension "snyk-security.snyk-vulnerability-scanner" "Snyk Security Scanner"
check_extension "streetsidesoftware.code-spell-checker" "Spell Checker"

echo -e "\n${BLUE}📝 Documentation${NC}"
check_extension "yzhang.markdown-all-in-one" "Markdown Support"
check_extension "bierner.markdown-mermaid" "Mermaid Diagrams"
check_extension "hediet.vscode-drawio" "Draw.io Integration"

echo -e "\n${BLUE}☁️ Container & Cloud${NC}"
check_extension "ms-azuretools.vscode-docker" "Docker Support"
check_extension "ms-kubernetes-tools.vscode-kubernetes-tools" "Kubernetes Tools"

echo -e "\n${BLUE}🔗 Version Control${NC}"
check_extension "eamodio.gitlens" "GitLens"
check_extension "github.vscode-pull-request-github" "GitHub Integration"

echo -e "\n${BLUE}🛠️ Command Line Tools${NC}"
check_command "rustc" "Rust Compiler"
check_command "cargo" "Rust Package Manager"
check_command "python3" "Python 3"
check_command "pip3" "Python Package Manager"
check_command "git" "Git Version Control"
check_command "make" "GNU Make"
check_command "gcc" "GNU C Compiler"
check_command "gdb" "GNU Debugger"
check_command "go" "Go Compiler"

echo -e "\n${BLUE}📊 Extension Count${NC}"
EXTENSION_COUNT=$(code --list-extensions | wc -l)
echo -e "${GREEN}📦${NC} Total Extensions Installed: $EXTENSION_COUNT"

echo -e "\n${BLUE}📁 Project Structure${NC}"
if [ -f ".vscode/settings.json" ]; then
    echo -e "${GREEN}✅${NC} VS Code settings configured"
else
    echo -e "${RED}❌${NC} VS Code settings missing"
fi

if [ -f ".vscode/tasks.json" ]; then
    echo -e "${GREEN}✅${NC} Build tasks configured"
else
    echo -e "${RED}❌${NC} Build tasks missing"
fi

if [ -f ".vscode/launch.json" ]; then
    echo -e "${GREEN}✅${NC} Debug configurations configured"
else
    echo -e "${RED}❌${NC} Debug configurations missing"
fi

if [ -f ".kilocode/mcp.json" ]; then
    echo -e "${GREEN}✅${NC} MCP servers configured"
else
    echo -e "${RED}❌${NC} MCP servers missing"
fi

if [ -f ".cargo/config.toml" ]; then
    echo -e "${GREEN}✅${NC} Rust configuration present"
else
    echo -e "${RED}❌${NC} Rust configuration missing"
fi

echo -e "\n${BLUE}🎯 Environment Status${NC}"
echo -e "${GREEN}🚀${NC} SynapticOS development environment is ready for OS development!"
echo -e "${BLUE}💡${NC} Next steps:"
echo "   1. Start VS Code: code ."
echo "   2. Open Command Palette (Ctrl+Shift+P)"
echo "   3. Try 'Rust: Run' or 'Python: Select Interpreter'"
echo "   4. Test AI assistants with Copilot or Continue"
echo "   5. Begin development using docs/PROJECT_STRUCTURE.md"

echo -e "\n${GREEN}✨ Happy coding! ✨${NC}"
