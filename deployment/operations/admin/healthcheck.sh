#!/bin/bash
# Syn_OS Development Environment Health Check
# Validates all development tools and dependencies

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
TOTAL_CHECKS=0

# Function to print status
print_status() {
    local status=$1
    local message=$2
    local details=${3:-""}
    
    ((TOTAL_CHECKS++))
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $message"
        [ -n "$details" ] && echo -e "  ${BLUE}→${NC} $details"
        ((CHECKS_PASSED++))
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $message"
        [ -n "$details" ] && echo -e "  ${RED}→${NC} $details"
        ((CHECKS_FAILED++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}!${NC} $message"
        [ -n "$details" ] && echo -e "  ${YELLOW}→${NC} $details"
    else
        echo -e "${BLUE}i${NC} $message"
        [ -n "$details" ] && echo -e "  ${BLUE}→${NC} $details"
    fi
}

# Function to check command existence and version
check_command() {
    local cmd=$1
    local version_flag=${2:-"--version"}
    local expected_pattern=${3:-""}
    
    if command -v "$cmd" &> /dev/null; then
        local version_output
        version_output=$($cmd $version_flag 2>&1 | head -n 1)
        
        if [ -n "$expected_pattern" ] && [[ ! $version_output =~ $expected_pattern ]]; then
            print_status "WARN" "$cmd installed" "Version may not meet requirements: $version_output"
        else
            print_status "PASS" "$cmd installed" "$version_output"
        fi
    else
        print_status "FAIL" "$cmd not found" "Required for Syn_OS development"
    fi
}

# Function to check Rust toolchain
check_rust_toolchain() {
    echo -e "\n${BLUE}🦀 Checking Rust Development Environment${NC}"
    
    check_command "rustc" "--version" "rustc 1\."
    check_command "cargo" "--version" "cargo 1\."
    check_command "rustup" "--version" "rustup"
    
    # Check Rust targets
    if command -v rustup &> /dev/null; then
        local targets=("x86_64-unknown-none" "i686-unknown-none")
        for target in "${targets[@]}"; do
            if rustup target list --installed | grep -q "$target"; then
                print_status "PASS" "Rust target $target" "Installed"
            else
                print_status "FAIL" "Rust target $target" "Missing - required for kernel development"
            fi
        done
        
        # Check Rust components
        local components=("rust-src" "llvm-tools-preview" "clippy" "rustfmt")
        for component in "${components[@]}"; do
            if rustup component list --installed | grep -q "$component"; then
                print_status "PASS" "Rust component $component" "Installed"
            else
                print_status "FAIL" "Rust component $component" "Missing"
            fi
        done
    fi
    
    # Check Cargo tools
    local cargo_tools=("cargo-audit" "cargo-deny" "cargo-watch" "bootimage")
    for tool in "${cargo_tools[@]}"; do
        check_command "$tool" "--version"
    done
}

# Function to check C/C++ toolchain
check_c_toolchain() {
    echo -e "\n${BLUE}🔧 Checking C/C++ Development Environment${NC}"
    
    check_command "gcc" "--version" "gcc"
    check_command "clang" "--version" "clang"
    check_command "make" "--version" "GNU Make"
    check_command "cmake" "--version" "cmake"
    check_command "gdb" "--version" "GNU gdb"
    check_command "valgrind" "--version" "valgrind"
    check_command "objdump" "--version" "GNU objdump"
}

# Function to check Python environment
check_python_environment() {
    echo -e "\n${BLUE}🐍 Checking Python Development Environment${NC}"
    
    check_command "python3" "--version" "Python 3\."
    check_command "pip3" "--version" "pip"
    
    # Check Python packages
    local python_packages=("black" "pylint" "mypy" "bandit" "pytest" "numpy" "fastapi")
    for package in "${python_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            local version=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
            print_status "PASS" "Python package $package" "Version: $version"
        else
            print_status "FAIL" "Python package $package" "Not installed"
        fi
    done
}

# Function to check Go environment
check_go_environment() {
    echo -e "\n${BLUE}🐹 Checking Go Development Environment${NC}"
    
    check_command "go" "version" "go version"
    
    # Check Go tools
    local go_tools=("gopls" "goimports" "golangci-lint" "staticcheck")
    for tool in "${go_tools[@]}"; do
        check_command "$tool" "--version"
    done
}

# Function to check Node.js environment
check_node_environment() {
    echo -e "\n${BLUE}📦 Checking Node.js Development Environment${NC}"
    
    check_command "node" "--version" "v"
    check_command "npm" "--version" ""
    
    # Check global packages
    local npm_packages=("typescript" "eslint" "prettier")
    for package in "${npm_packages[@]}"; do
        if npm list -g "$package" &>/dev/null; then
            local version=$(npm list -g "$package" --depth=0 2>/dev/null | grep "$package" | cut -d'@' -f2)
            print_status "PASS" "NPM package $package" "Version: $version"
        else
            print_status "FAIL" "NPM package $package" "Not installed globally"
        fi
    done
}

# Function to check security tools
check_security_tools() {
    echo -e "\n${BLUE}🔒 Checking Security Tools${NC}"
    
    check_command "trivy" "--version" "Version:"
    check_command "nmap" "--version" "Nmap"
    check_command "tcpdump" "--version" "tcpdump"
    check_command "wireshark" "--version" "Wireshark"
}

# Function to check virtualization
check_virtualization() {
    echo -e "\n${BLUE}🖥️ Checking Virtualization Support${NC}"
    
    check_command "qemu-system-x86_64" "--version" "QEMU"
    
    # Check KVM support
    if [ -e /dev/kvm ]; then
        print_status "PASS" "KVM device available" "/dev/kvm exists"
    else
        print_status "WARN" "KVM device not available" "Performance may be limited"
    fi
    
    # Check for nested virtualization
    if [ -f /sys/module/kvm_intel/parameters/nested ] && [ "$(cat /sys/module/kvm_intel/parameters/nested)" = "Y" ]; then
        print_status "PASS" "Nested virtualization enabled" "Intel KVM"
    elif [ -f /sys/module/kvm_amd/parameters/nested ] && [ "$(cat /sys/module/kvm_amd/parameters/nested)" = "1" ]; then
        print_status "PASS" "Nested virtualization enabled" "AMD KVM"
    else
        print_status "WARN" "Nested virtualization not detected" "May limit some development features"
    fi
}

# Function to check Docker
check_docker_environment() {
    echo -e "\n${BLUE}🐳 Checking Container Environment${NC}"
    
    check_command "docker" "--version" "Docker"
    check_command "docker-compose" "--version" "docker-compose"
    
    # Check Docker daemon
    if docker info &>/dev/null; then
        print_status "PASS" "Docker daemon running" "Ready for containerized development"
    else
        print_status "FAIL" "Docker daemon not running" "Start Docker service"
    fi
}

# Function to check system resources
check_system_resources() {
    echo -e "\n${BLUE}💾 Checking System Resources${NC}"
    
    # Memory check
    local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$memory_gb" -ge 16 ]; then
        print_status "PASS" "Memory: ${memory_gb}GB" "Recommended for AI development"
    elif [ "$memory_gb" -ge 8 ]; then
        print_status "WARN" "Memory: ${memory_gb}GB" "Minimum met, 16GB+ recommended"
    else
        print_status "FAIL" "Memory: ${memory_gb}GB" "Insufficient, minimum 8GB required"
    fi
    
    # Disk space check
    local disk_gb=$(df / | awk 'NR==2{print int($4/1024/1024)}')
    if [ "$disk_gb" -ge 50 ]; then
        print_status "PASS" "Disk space: ${disk_gb}GB available" "Sufficient for development"
    elif [ "$disk_gb" -ge 20 ]; then
        print_status "WARN" "Disk space: ${disk_gb}GB available" "Limited space"
    else
        print_status "FAIL" "Disk space: ${disk_gb}GB available" "Insufficient space"
    fi
    
    # CPU cores check
    local cpu_cores=$(nproc)
    if [ "$cpu_cores" -ge 8 ]; then
        print_status "PASS" "CPU cores: $cpu_cores" "Excellent for parallel builds"
    elif [ "$cpu_cores" -ge 4 ]; then
        print_status "PASS" "CPU cores: $cpu_cores" "Good for development"
    else
        print_status "WARN" "CPU cores: $cpu_cores" "May impact build performance"
    fi
}

# Function to check network connectivity
check_network_connectivity() {
    echo -e "\n${BLUE}🌐 Checking Network Connectivity${NC}"
    
    # Check internet connectivity
    if curl -s --max-time 10 https://google.com > /dev/null; then
        print_status "PASS" "Internet connectivity" "Can reach external services"
    else
        print_status "FAIL" "Internet connectivity" "Cannot reach external services"
    fi
    
    # Check package repository connectivity
    if curl -s --max-time 10 https://crates.io > /dev/null; then
        print_status "PASS" "Rust crates.io access" "Can download Rust packages"
    else
        print_status "WARN" "Rust crates.io access" "May have issues downloading packages"
    fi
    
    if curl -s --max-time 10 https://pypi.org > /dev/null; then
        print_status "PASS" "Python PyPI access" "Can download Python packages"
    else
        print_status "WARN" "Python PyPI access" "May have issues downloading packages"
    fi
}

# Main health check function
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Syn_OS Development Environment Health Check${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    
    check_system_resources
    check_rust_toolchain
    check_c_toolchain
    check_python_environment
    check_go_environment
    check_node_environment
    check_security_tools
    check_virtualization
    check_docker_environment
    check_network_connectivity
    
    # Summary
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Health Check Summary${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "Total checks: $TOTAL_CHECKS"
    echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
    echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
    
    local pass_rate=$((CHECKS_PASSED * 100 / TOTAL_CHECKS))
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All checks passed! Environment is ready for Syn_OS development.${NC}"
        exit 0
    elif [ $pass_rate -ge 80 ]; then
        echo -e "\n${YELLOW}⚠️  Environment mostly ready ($pass_rate% pass rate). Address failed checks for optimal experience.${NC}"
        exit 1
    else
        echo -e "\n${RED}❌ Environment needs attention ($pass_rate% pass rate). Fix critical issues before development.${NC}"
        exit 2
    fi
}

# Run health check
main "$@"
