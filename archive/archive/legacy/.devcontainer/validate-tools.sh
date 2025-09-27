#!/bin/bash
# Comprehensive tool validation for Syn_OS development environment
# This script validates all tools and extensions are working correctly

set -euo pipefail

echo "🔍 Validating Syn_OS Development Environment..."
echo "=================================================="

VALIDATION_PASSED=0
VALIDATION_FAILED=0

# Function to check if command exists and log result
check_tool() {
    local tool="$1"
    local description="$2"
    local version_flag="${3:---version}"
    
    if command -v "$tool" &> /dev/null; then
        echo "✅ $description: $(command -v "$tool")"
        if [[ "$version_flag" != "skip" ]]; then
            echo "   Version: $($tool $version_flag 2>/dev/null || echo 'N/A')"
        fi
        ((VALIDATION_PASSED++))
    else
        echo "❌ $description: Not found"
        ((VALIDATION_FAILED++))
    fi
}

# Function to check if VS Code extension would be available
check_extension() {
    local ext_id="$1"
    local description="$2"
    
    # In a real codespace, this would check if extension is installed
    # For now, we'll assume it's available if in the devcontainer.json
    if grep -q "$ext_id" .devcontainer/devcontainer.json 2>/dev/null; then
        echo "✅ Extension: $description ($ext_id)"
        ((VALIDATION_PASSED++))
    else
        echo "❌ Extension: $description ($ext_id) - Not configured"
        ((VALIDATION_FAILED++))
    fi
}

echo ""
echo "🔧 Core Development Tools"
echo "------------------------"
check_tool "rustc" "Rust Compiler"
check_tool "cargo" "Cargo Package Manager"
check_tool "python3" "Python"
check_tool "pip" "Python Package Manager" "skip"
check_tool "go" "Go Compiler" "version"
check_tool "node" "Node.js"
check_tool "npm" "NPM Package Manager"
check_tool "gcc" "GCC Compiler"
check_tool "clang" "Clang Compiler"
check_tool "cmake" "CMake Build System"
check_tool "make" "Make Build Tool" "-version"

echo ""
echo "🛡️ Security Tools"
echo "-----------------"
check_tool "cargo-audit" "Rust Security Audit" "--version"
check_tool "cargo-deny" "Rust Dependency Checker" "--version"
check_tool "bandit" "Python Security Linter"
check_tool "safety" "Python Safety Checker"
check_tool "semgrep" "Static Analysis" "--version"
check_tool "trivy" "Container Security Scanner"
check_tool "hadolint" "Dockerfile Linter" "--version"

echo ""
echo "🔍 Analysis and Debugging Tools"
echo "--------------------------------"
check_tool "gdb" "GNU Debugger"
check_tool "lldb" "LLVM Debugger" "--version"
check_tool "valgrind" "Memory Analyzer"
check_tool "strace" "System Call Tracer" "-V"
check_tool "perf" "Performance Analyzer" "--version"
check_tool "cppcheck" "C++ Static Analyzer" "--version"

echo ""
echo "📊 Performance and Profiling"
echo "-----------------------------"
check_tool "flamegraph" "Flame Graph Generator" "skip"
check_tool "cargo-tarpaulin" "Rust Code Coverage" "--version"
check_tool "hyperfine" "Benchmarking Tool" "--version"

echo ""
echo "🌐 Network and Protocol Tools"
echo "------------------------------"
check_tool "tcpdump" "Packet Capture" "--version"
check_tool "tshark" "Wireshark CLI" "--version"
check_tool "nmap" "Network Mapper" "--version"
check_tool "curl" "HTTP Client"
check_tool "wget" "Web Downloader"

echo ""
echo "🗄️ Database and Data Tools"
echo "---------------------------"
check_tool "sqlite3" "SQLite Database" ".version"
check_tool "psql" "PostgreSQL Client" "--version"
check_tool "jq" "JSON Processor"

echo ""
echo "📝 Documentation Tools"
echo "-----------------------"
check_tool "pandoc" "Document Converter"
check_tool "graphviz" "Graph Visualization" "skip"
check_tool "mdbook" "Rust Documentation" "--version"

echo ""
echo "🔄 Container and Cloud Tools"
echo "-----------------------------"
check_tool "docker" "Docker Container Platform"
check_tool "qemu-system-x86_64" "QEMU Emulator" "--version"

echo ""
echo "📋 VS Code Extensions (configured)"
echo "-----------------------------------"
check_extension "rust-lang.rust-analyzer" "Rust Language Server"
check_extension "ms-vscode.cpptools" "C/C++ Tools"
check_extension "ms-python.python" "Python Extension"
check_extension "golang.go" "Go Extension"
check_extension "vadimcn.vscode-lldb" "LLDB Debugger"
check_extension "ms-vscode.hexeditor" "Hex Editor"
check_extension "github.copilot" "GitHub Copilot"
check_extension "continue.continue" "Continue AI"
check_extension "snyk-security.snyk-vulnerability-scanner" "Snyk Security"
check_extension "ms-azuretools.vscode-docker" "Docker Extension"
check_extension "eamodio.gitlens" "GitLens"
check_extension "yzhang.markdown-all-in-one" "Markdown Support"

echo ""
echo "🧪 Development Environment Tests"
echo "--------------------------------"

# Test Rust compilation
if command -v rustc &> /dev/null; then
    echo -n "🦀 Testing Rust compilation... "
    cat > /tmp/test.rs << 'EOF'
fn main() {
    println!("Hello, Syn_OS!");
}
EOF
    if rustc /tmp/test.rs -o /tmp/test_rust 2>/dev/null && /tmp/test_rust &>/dev/null; then
        echo "✅ Working"
        ((VALIDATION_PASSED++))
    else
        echo "❌ Failed"
        ((VALIDATION_FAILED++))
    fi
    rm -f /tmp/test.rs /tmp/test_rust
fi

# Test Python execution
if command -v python3 &> /dev/null; then
    echo -n "🐍 Testing Python execution... "
    if python3 -c "print('Hello, Syn_OS!')" &>/dev/null; then
        echo "✅ Working"
        ((VALIDATION_PASSED++))
    else
        echo "❌ Failed"
        ((VALIDATION_FAILED++))
    fi
fi

# Test Go compilation
if command -v go &> /dev/null; then
    echo -n "🔷 Testing Go compilation... "
    cat > /tmp/test.go << 'EOF'
package main
import "fmt"
func main() {
    fmt.Println("Hello, Syn_OS!")
}
EOF
    if go run /tmp/test.go &>/dev/null; then
        echo "✅ Working"
        ((VALIDATION_PASSED++))
    else
        echo "❌ Failed"
        ((VALIDATION_FAILED++))
    fi
    rm -f /tmp/test.go
fi

# Test C compilation
if command -v gcc &> /dev/null; then
    echo -n "⚙️ Testing C compilation... "
    cat > /tmp/test.c << 'EOF'
#include <stdio.h>
int main() {
    printf("Hello, Syn_OS!\n");
    return 0;
}
EOF
    if gcc /tmp/test.c -o /tmp/test_c 2>/dev/null && /tmp/test_c &>/dev/null; then
        echo "✅ Working"
        ((VALIDATION_PASSED++))
    else
        echo "❌ Failed"
        ((VALIDATION_FAILED++))
    fi
    rm -f /tmp/test.c /tmp/test_c
fi

echo ""
echo "📊 Validation Summary"
echo "===================="
echo "✅ Passed: $VALIDATION_PASSED"
echo "❌ Failed: $VALIDATION_FAILED"

TOTAL=$((VALIDATION_PASSED + VALIDATION_FAILED))
if [[ $TOTAL -gt 0 ]]; then
    SUCCESS_RATE=$((VALIDATION_PASSED * 100 / TOTAL))
    echo "📈 Success Rate: $SUCCESS_RATE%"
    
    if [[ $SUCCESS_RATE -ge 90 ]]; then
        echo "🎉 EXCELLENT: Development environment is ready!"
    elif [[ $SUCCESS_RATE -ge 75 ]]; then
        echo "👍 GOOD: Development environment is mostly ready"
    elif [[ $SUCCESS_RATE -ge 50 ]]; then
        echo "⚠️ WARNING: Some tools are missing"
    else
        echo "❌ CRITICAL: Many tools are missing or broken"
    fi
fi

echo ""
echo "🚀 Development Environment Status: $(if [[ $SUCCESS_RATE -ge 90 ]]; then echo "READY"; else echo "NEEDS SETUP"; fi)"
echo ""