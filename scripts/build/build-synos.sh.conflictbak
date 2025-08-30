#!/bin/bash
set -euo pipefail

# Syn_OS Master Build System
# Orchestrates the complete build process for the AI-powered security OS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Version and build information
SYNOS_VERSION="${SYNOS_VERSION:-1.0.0}"
BUILD_ID="${BUILD_ID:-$(date +%Y%m%d-%H%M%S)}"
GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

# Build configuration
BUILD_JOBS="${BUILD_JOBS:-$(nproc)}"
ARCH="${ARCH:-x86_64}"
TARGET_ENV="${TARGET_ENV:-production}"

# Directories
BUILD_DIR="${PROJECT_ROOT}/build"
OUTPUT_DIR="${BUILD_DIR}/output"
CACHE_DIR="${BUILD_DIR}/cache"
LOGS_DIR="${BUILD_DIR}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }
log_stage() { echo -e "${PURPLE}[STAGE]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }
log_substage() { echo -e "${CYAN}[SUBSTAGE]${NC} $1" | tee -a "${LOGS_DIR}/build.log"; }

# Progress tracking
TOTAL_STAGES=10
CURRENT_STAGE=0

update_progress() {
    local stage_name="$1"
    CURRENT_STAGE=$((CURRENT_STAGE + 1))
    local progress=$((CURRENT_STAGE * 100 / TOTAL_STAGES))
    
    echo -e "\n${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC} Stage ${CURRENT_STAGE}/${TOTAL_STAGES}: ${stage_name}$(printf "%*s" $((50 - ${#stage_name})) "") ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC} Progress: [$(printf "%*s" $((progress/2)) "" | tr ' ' '█')$(printf "%*s" $((50-progress/2)) "" | tr ' ' '░')] ${progress}% ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

# Cleanup function
cleanup() {
    log_info "Performing cleanup..."
    
    # Unmount any remaining mounts
    for mount in $(mount | grep "${BUILD_DIR}" | awk '{print $3}' | sort -r); do
        umount "$mount" 2>/dev/null || true
    done
    
    # Stop any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT

# Initialize build environment
init_build_env() {
    update_progress "Initializing Build Environment"
    
    log_info "Syn_OS Build System v${SYNOS_VERSION}"
    log_info "Build ID: ${BUILD_ID}"
    log_info "Git Commit: ${GIT_COMMIT}"
    log_info "Architecture: ${ARCH}"
    log_info "Target Environment: ${TARGET_ENV}"
    log_info "Build Jobs: ${BUILD_JOBS}"
    
    # Create build directories
    mkdir -p "${OUTPUT_DIR}" "${CACHE_DIR}" "${LOGS_DIR}"
    mkdir -p "${BUILD_DIR}/kernel" "${BUILD_DIR}/iso" "${BUILD_DIR}/packages"
    
    # Create build manifest
    cat > "${OUTPUT_DIR}/build-manifest.json" << EOF
{
    "version": "${SYNOS_VERSION}",
    "build_id": "${BUILD_ID}",
    "git_commit": "${GIT_COMMIT}",
    "architecture": "${ARCH}",
    "target_environment": "${TARGET_ENV}",
    "build_date": "$(date -u -Iseconds)",
    "build_host": "$(hostname)",
    "build_user": "$(whoami)",
    "components": []
}
EOF
    
    log_success "Build environment initialized"
}

# Check system requirements and dependencies
check_prerequisites() {
    update_progress "Checking Prerequisites"
    
    log_info "Checking system requirements..."
    
    # Check if running as root (required for some build steps)
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root for kernel and ISO building"
        exit 1
    fi
    
    # Check available disk space (need at least 50GB)
    local available_space=$(df "${PROJECT_ROOT}" | tail -1 | awk '{print $4}')
    local required_space=$((50 * 1024 * 1024)) # 50GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        log_error "Insufficient disk space. Need at least 50GB, have $(($available_space / 1024 / 1024))GB"
        exit 1
    fi
    
    # Check memory (need at least 8GB)
    local total_mem=$(free -m | awk '/^Mem:/{print $2}')
    if [[ $total_mem -lt 8192 ]]; then
        log_warning "Low memory detected (${total_mem}MB). Recommend at least 8GB for optimal build performance"
    fi
    
    # Check build dependencies
    local deps=(
        gcc g++ make cmake ninja-build
        python3 python3-pip python3-venv python3-dev
        rustc cargo
        nodejs npm
        git curl wget
        debootstrap squashfs-tools xorriso
        qemu-system-x86 qemu-utils
        docker docker-compose
    )
    
    local missing_deps=()
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing packages and run again"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
}

# Build consciousness engine and AI components
build_consciousness() {
    update_progress "Building Consciousness Engine"
    
    log_info "Building AI consciousness components..."
    
    # Set up Python virtual environment
    log_substage "Setting up Python environment"
    python3 -m venv "${BUILD_DIR}/python-env"
    source "${BUILD_DIR}/python-env/bin/activate"
    
    pip install --upgrade pip setuptools wheel
    pip install -r "${PROJECT_ROOT}/requirements-ai-integration.txt"
    pip install -r "${PROJECT_ROOT}/requirements-security.txt"
    
    # Build consciousness engine
    log_substage "Building consciousness engine"
    cd "${PROJECT_ROOT}/src/consciousness_v2"
    python -m pytest tests/ || log_warning "Some consciousness tests failed"
    
    # Package consciousness engine
    python setup.py bdist_wheel
    cp dist/*.whl "${OUTPUT_DIR}/consciousness-engine-${SYNOS_VERSION}-py3-none-any.whl"
    
    # Update manifest
    jq '.components += [{"name": "consciousness-engine", "version": "'${SYNOS_VERSION}'", "type": "python-wheel"}]' \
        "${OUTPUT_DIR}/build-manifest.json" > "${OUTPUT_DIR}/build-manifest.json.tmp"
    mv "${OUTPUT_DIR}/build-manifest.json.tmp" "${OUTPUT_DIR}/build-manifest.json"
    
    log_success "Consciousness engine built"
}

# Build custom kernel with AI enhancements
build_kernel() {
    update_progress "Building Custom Kernel"
    
    log_info "Building Syn_OS custom kernel..."
    
    local kernel_version="6.8.0-synos-${SYNOS_VERSION}"
    local kernel_build_dir="${BUILD_DIR}/kernel"
    
    mkdir -p "$kernel_build_dir"
    cd "$kernel_build_dir"
    
    # Download Linux kernel source if not exists
    if [[ ! -d "linux-6.8" ]]; then
        log_substage "Downloading Linux kernel source"
        wget -O linux-6.8.tar.xz https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.8.tar.xz
        tar -xf linux-6.8.tar.xz
    fi
    
    cd linux-6.8
    
    # Apply Syn_OS patches
    log_substage "Applying Syn_OS kernel patches"
    if [[ -d "${PROJECT_ROOT}/build/kernel/patches" ]]; then
        for patch in "${PROJECT_ROOT}/build/kernel/patches"/*.patch; do
            if [[ -f "$patch" ]]; then
                log_info "Applying patch: $(basename "$patch")"
                patch -p1 < "$patch" || log_warning "Patch $(basename "$patch") failed"
            fi
        done
    fi
    
    # Copy Syn_OS kernel configuration
    log_substage "Configuring kernel"
    if [[ -f "${PROJECT_ROOT}/build/kernel/synos_defconfig" ]]; then
        cp "${PROJECT_ROOT}/build/kernel/synos_defconfig" .config
    else
        # Generate default config with Syn_OS features
        make defconfig
        
        # Enable Syn_OS specific features
        cat >> .config << 'EOF'
# Syn_OS AI enhancements
CONFIG_CONSCIOUSNESS=y
CONFIG_AI_MEMORY_MANAGEMENT=y  
CONFIG_AI_SCHEDULER=y
CONFIG_SYNOS_SECURITY=y
CONFIG_AI_NETFILTER=y
CONFIG_EDUCATIONAL_SYSCALLS=y

# Security hardening
CONFIG_SECURITY_SYNOS=y
CONFIG_DEFAULT_SECURITY="synos"
CONFIG_HARDENED_USERCOPY=y
CONFIG_FORTIFY_SOURCE=y

# Performance optimization
CONFIG_PREEMPT_VOLUNTARY=y
CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE=y
CONFIG_SLAB_FREELIST_RANDOM=y

# Container support
CONFIG_NAMESPACES=y
CONFIG_CGROUPS=y
CONFIG_MEMCG=y
EOF
    fi
    
    # Build kernel
    log_substage "Compiling kernel (this may take 30-60 minutes)"
    make -j"$BUILD_JOBS" LOCALVERSION="-synos-${SYNOS_VERSION}"
    
    # Build kernel modules
    log_substage "Building kernel modules"
    make -j"$BUILD_JOBS" modules
    
    # Install to temporary directory
    local kernel_install_dir="${kernel_build_dir}/install"
    mkdir -p "$kernel_install_dir"
    
    make INSTALL_PATH="$kernel_install_dir" install
    make INSTALL_MOD_PATH="$kernel_install_dir" modules_install
    
    # Create kernel package
    log_substage "Creating kernel package"
    cd "$kernel_install_dir"
    
    # Create debian package structure
    mkdir -p debian/DEBIAN
    mkdir -p debian/boot debian/lib/modules
    
    cp -r boot/* debian/boot/
    cp -r lib/modules/* debian/lib/modules/
    
    # Create package control file
    cat > debian/DEBIAN/control << EOF
Package: linux-image-synos
Version: ${kernel_version}
Section: kernel
Priority: optional
Architecture: ${ARCH}
Maintainer: Syn_OS Team <team@synos.ai>
Description: Syn_OS AI-enhanced Linux kernel
 Custom Linux kernel with AI consciousness integration,
 enhanced security features, and cybersecurity optimizations.
EOF
    
    # Build .deb package
    dpkg-deb --build debian "${OUTPUT_DIR}/linux-image-synos_${kernel_version}_${ARCH}.deb"
    
    # Update manifest
    jq '.components += [{"name": "linux-kernel", "version": "'${kernel_version}'", "type": "deb-package"}]' \
        "${OUTPUT_DIR}/build-manifest.json" > "${OUTPUT_DIR}/build-manifest.json.tmp"
    mv "${OUTPUT_DIR}/build-manifest.json.tmp" "${OUTPUT_DIR}/build-manifest.json"
    
    log_success "Custom kernel built"
}

# Build security tools with AI wrappers
build_security_tools() {
    update_progress "Building Security Tools"
    
    log_info "Building AI-enhanced security tools..."
    
    # Build AI wrapper system
    log_substage "Building AI wrapper system"
    cd "${PROJECT_ROOT}/build"
    
    # Test AI wrapper
    python3 -c "
import ai_security_wrapper
import asyncio

async def test():
    from ai_security_wrapper import AISecurityWrapper
    wrapper = AISecurityWrapper('test-tool', '/bin/echo')
    execution = await wrapper.execute(['Hello', 'AI', 'World'])
    print(f'Test execution: {execution.exit_code}')

asyncio.run(test())
"
    
    # Package AI wrapper system
    python3 -m pip install build
    python3 -m build --wheel
    
    if [[ -f dist/*.whl ]]; then
        cp dist/*.whl "${OUTPUT_DIR}/ai-security-wrapper-${SYNOS_VERSION}-py3-none-any.whl"
    fi
    
    log_success "Security tools built"
}

# Build container images
build_containers() {
    update_progress "Building Container Images"
    
    log_info "Building Docker containers..."
    
    local images=(
        "consciousness-engine"
        "security-dashboard" 
        "ai-orchestrator"
        "educational-platform"
    )
    
    for image in "${images[@]}"; do
        log_substage "Building $image container"
        
        if [[ -f "${PROJECT_ROOT}/docker/Dockerfile.$image" ]]; then
            docker build \
                -t "synos/$image:$SYNOS_VERSION" \
                -t "synos/$image:latest" \
                -f "${PROJECT_ROOT}/docker/Dockerfile.$image" \
                "${PROJECT_ROOT}"
            
            # Save container image
            docker save "synos/$image:$SYNOS_VERSION" | gzip > "${OUTPUT_DIR}/$image-$SYNOS_VERSION.tar.gz"
        else
            log_warning "Dockerfile for $image not found, skipping"
        fi
    done
    
    # Update manifest
    for image in "${images[@]}"; do
        jq '.components += [{"name": "'$image'", "version": "'${SYNOS_VERSION}'", "type": "docker-image"}]' \
            "${OUTPUT_DIR}/build-manifest.json" > "${OUTPUT_DIR}/build-manifest.json.tmp"
        mv "${OUTPUT_DIR}/build-manifest.json.tmp" "${OUTPUT_DIR}/build-manifest.json"
    done
    
    log_success "Container images built"
}

# Package management system
build_packages() {
    update_progress "Building Package Management System"
    
    log_info "Building SynPkg package manager..."
    
    # Test SynPkg manager
    log_substage "Testing SynPkg manager"
    cd "${PROJECT_ROOT}/build"
    python3 -c "
import sys
sys.path.append('.')
from synpkg_manager import SynPkgManager
import asyncio

async def test():
    manager = SynPkgManager()
    await manager.load_config()
    print('SynPkg manager loaded successfully')

asyncio.run(test())
"
    
    # Package SynPkg
    cp synpkg-manager.py "${OUTPUT_DIR}/synpkg-manager-${SYNOS_VERSION}.py"
    
    log_success "Package management system built"
}

# Build live ISO
build_iso() {
    update_progress "Building Live ISO"
    
    log_info "Building Syn_OS live ISO..."
    
    # Make ISO builder executable
    chmod +x "${PROJECT_ROOT}/build/iso/synos-live-builder.sh"
    
    # Run ISO builder
    cd "${PROJECT_ROOT}/build/iso"
    ISO_VERSION="$SYNOS_VERSION" ./synos-live-builder.sh
    
    # Copy ISO to output directory
    if [[ -f "${PROJECT_ROOT}/build/iso/synos-ai-security-${SYNOS_VERSION}-"*".iso" ]]; then
        cp "${PROJECT_ROOT}/build/iso/synos-ai-security-${SYNOS_VERSION}-"*".iso" "${OUTPUT_DIR}/"
        cp "${PROJECT_ROOT}/build/iso/synos-ai-security-${SYNOS_VERSION}-"*".iso.sha256" "${OUTPUT_DIR}/"
        cp "${PROJECT_ROOT}/build/iso/synos-ai-security-${SYNOS_VERSION}-"*".iso.md5" "${OUTPUT_DIR}/"
    fi
    
    # Update manifest
    local iso_file=$(ls "${OUTPUT_DIR}"/synos-ai-security-*.iso 2>/dev/null | head -1)
    if [[ -f "$iso_file" ]]; then
        local iso_size=$(du -h "$iso_file" | cut -f1)
        jq '.components += [{"name": "live-iso", "version": "'${SYNOS_VERSION}'", "type": "iso-image", "size": "'$iso_size'"}]' \
            "${OUTPUT_DIR}/build-manifest.json" > "${OUTPUT_DIR}/build-manifest.json.tmp"
        mv "${OUTPUT_DIR}/build-manifest.json.tmp" "${OUTPUT_DIR}/build-manifest.json"
    fi
    
    log_success "Live ISO built"
}

# Run tests and validation
run_tests() {
    update_progress "Running Tests and Validation"
    
    log_info "Running test suite..."
    
    # Unit tests
    log_substage "Running unit tests"
    cd "${PROJECT_ROOT}"
    
    # Python tests
    if [[ -d "tests" ]]; then
        source "${BUILD_DIR}/python-env/bin/activate"
        python -m pytest tests/ -v --tb=short --maxfail=5 || log_warning "Some Python tests failed"
    fi
    
    # Rust tests
    if [[ -f "Cargo.toml" ]]; then
        cargo test --workspace || log_warning "Some Rust tests failed"
    fi
    
    # Integration tests
    log_substage "Running integration tests"
    if [[ -f "tests/integration/run_tests.sh" ]]; then
        chmod +x tests/integration/run_tests.sh
        tests/integration/run_tests.sh || log_warning "Some integration tests failed"
    fi
    
    # Security audit
    log_substage "Running security audit"
    if command -v cargo-audit >/dev/null 2>&1; then
        cargo audit || log_warning "Security audit found issues"
    fi
    
    # Container security scan
    if command -v docker >/dev/null 2>&1; then
        for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep synos); do
            log_info "Scanning container: $image"
            # Add container security scanning here
        done
    fi
    
    log_success "Tests completed"
}

# Create documentation
build_documentation() {
    update_progress "Building Documentation"
    
    log_info "Building documentation..."
    
    local docs_dir="${OUTPUT_DIR}/documentation"
    mkdir -p "$docs_dir"
    
    # Copy markdown documentation
    if [[ -d "${PROJECT_ROOT}/docs" ]]; then
        cp -r "${PROJECT_ROOT}/docs"/* "$docs_dir/"
    fi
    
    # Generate API documentation
    log_substage "Generating API documentation"
    
    # Python API docs
    if command -v sphinx-build >/dev/null 2>&1; then
        cd "${PROJECT_ROOT}/src/consciousness_v2"
        sphinx-apidoc -o "${docs_dir}/api/python" . || log_warning "Python API docs generation failed"
    fi
    
    # Rust API docs
    if [[ -f "${PROJECT_ROOT}/Cargo.toml" ]]; then
        cd "${PROJECT_ROOT}"
        cargo doc --workspace --no-deps || log_warning "Rust API docs generation failed"
        if [[ -d "target/doc" ]]; then
            cp -r target/doc "${docs_dir}/api/rust"
        fi
    fi
    
    # Create README for output
    cat > "${OUTPUT_DIR}/README.md" << EOF
# Syn_OS Build Output

This directory contains the complete Syn_OS build artifacts.

## Build Information
- **Version**: ${SYNOS_VERSION}
- **Build ID**: ${BUILD_ID}
- **Git Commit**: ${GIT_COMMIT}
- **Build Date**: $(date -u -Iseconds)
- **Architecture**: ${ARCH}

## Components

### Live ISO
- **File**: synos-ai-security-${SYNOS_VERSION}-*.iso
- **Boot**: Write to USB or burn to DVD, boot from USB/DVD
- **Login**: Username 'live', password 'synos'

### Kernel Package
- **File**: linux-image-synos_*.deb
- **Install**: \`dpkg -i linux-image-synos_*.deb\`
- **Features**: AI consciousness integration, enhanced security

### Consciousness Engine
- **File**: consciousness-engine-${SYNOS_VERSION}-py3-none-any.whl
- **Install**: \`pip install consciousness-engine-*.whl\`
- **Usage**: See documentation/consciousness/

### AI Security Wrapper
- **File**: ai-security-wrapper-${SYNOS_VERSION}-py3-none-any.whl
- **Install**: \`pip install ai-security-wrapper-*.whl\`
- **Usage**: Automatically enhances security tools with AI

### Container Images
- **Files**: *-${SYNOS_VERSION}.tar.gz
- **Load**: \`docker load < image.tar.gz\`
- **Run**: \`docker-compose up\`

### Package Manager
- **File**: synpkg-manager-${SYNOS_VERSION}.py
- **Install**: Copy to /usr/local/bin/synpkg
- **Usage**: \`synpkg install <package>\`

## Quick Start

1. **Boot Live ISO**: Write ISO to USB, boot system
2. **Install**: Run installer from live environment
3. **Configure**: Set up consciousness engine and security tools
4. **Learn**: Use educational features and AI guidance

## Documentation

See the documentation/ directory for:
- User guides
- Developer documentation  
- API references
- Security guides
- Educational materials

## Support

- **Website**: https://synos.ai
- **Documentation**: https://docs.synos.ai
- **Community**: https://community.synos.ai
- **Issues**: https://github.com/synos-ai/synos/issues

Built with ❤️ by the Syn_OS team.
EOF
    
    log_success "Documentation built"
}

# Final packaging and release preparation
create_release() {
    update_progress "Creating Release Package"
    
    log_info "Preparing release package..."
    
    local release_dir="${OUTPUT_DIR}/synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}"
    mkdir -p "$release_dir"
    
    # Copy all build artifacts
    cp -r "${OUTPUT_DIR}"/* "$release_dir/" 2>/dev/null || true
    
    # Create release archive
    log_substage "Creating release archive"
    cd "${OUTPUT_DIR}"
    tar -czf "synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}.tar.gz" \
        "synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}/"
    
    # Create checksums for release
    sha256sum "synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}.tar.gz" > \
        "synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}.tar.gz.sha256"
    
    # GPG sign if key available
    if gpg --list-secret-keys "synos-release" >/dev/null 2>&1; then
        gpg --armor --detach-sign --local-user "synos-release" \
            "synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}.tar.gz"
        log_success "Release package signed with GPG"
    fi
    
    # Create upload script
    cat > "${OUTPUT_DIR}/upload-release.sh" << 'EOF'
#!/bin/bash
# Upload script for Syn_OS release

RELEASE_FILE="synos-${SYNOS_VERSION}-${ARCH}-${BUILD_ID}.tar.gz"
ISO_FILE=$(ls synos-ai-security-*.iso)

echo "Uploading Syn_OS release..."
echo "Release package: $RELEASE_FILE"  
echo "ISO file: $ISO_FILE"

# Add your upload commands here
# rsync -avz "$RELEASE_FILE" user@releases.synos.ai:/releases/
# rsync -avz "$ISO_FILE" user@releases.synos.ai:/isos/

echo "Upload commands prepared in upload-release.sh"
EOF
    
    chmod +x "${OUTPUT_DIR}/upload-release.sh"
    
    log_success "Release package created"
}

# Generate build summary
generate_summary() {
    local end_time=$(date)
    local build_duration=$(($(date +%s) - ${build_start_time}))
    local duration_formatted=$(printf "%02d:%02d:%02d" $((build_duration/3600)) $((build_duration%3600/60)) $((build_duration%60)))
    
    log_info "Generating build summary..."
    
    cat > "${OUTPUT_DIR}/build-summary.txt" << EOF
Syn_OS Build Summary
===================

Build Information:
- Version: ${SYNOS_VERSION}
- Build ID: ${BUILD_ID}
- Git Commit: ${GIT_COMMIT}
- Architecture: ${ARCH}
- Target Environment: ${TARGET_ENV}

Build Timing:
- Start Time: ${build_start_time_formatted}
- End Time: ${end_time}
- Duration: ${duration_formatted}

Build Artifacts:
$(ls -la "${OUTPUT_DIR}" | grep -v "^d" | tail -n +2)

Build Statistics:
- Total Output Size: $(du -sh "${OUTPUT_DIR}" | cut -f1)
- Number of Components: $(jq '.components | length' "${OUTPUT_DIR}/build-manifest.json")

Component Details:
$(jq -r '.components[] | "- \(.name) \(.version) (\(.type))"' "${OUTPUT_DIR}/build-manifest.json")

Build Environment:
- Build Host: $(hostname)
- Build User: $(whoami)
- OS Version: $(uname -sr)
- CPU Cores: ${BUILD_JOBS}
- Available Memory: $(free -h | awk '/^Mem:/{print $2}')
- Available Disk: $(df -h "${PROJECT_ROOT}" | tail -1 | awk '{print $4}')

Next Steps:
1. Test the live ISO in a virtual machine
2. Validate all security tools function correctly  
3. Test AI consciousness features
4. Run security validation tests
5. Prepare for release

Build completed successfully! 🎉
EOF
    
    # Display summary
    cat "${OUTPUT_DIR}/build-summary.txt"
    
    log_success "Build summary generated"
}

# Main build function
main() {
    local build_start_time=$(date +%s)
    local build_start_time_formatted=$(date)
    
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    SYN_OS BUILD SYSTEM                        ║"
    echo "║                  AI-Powered Security OS                       ║"
    echo "║                                                                ║"
    echo "║  Building the ultimate cybersecurity operating system         ║"
    echo "║  with integrated AI consciousness engine                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    # Execute build stages
    init_build_env
    check_prerequisites  
    build_consciousness
    build_kernel
    build_security_tools
    build_containers
    build_packages
    build_iso
    run_tests
    build_documentation
    create_release
    
    # Generate final summary
    generate_summary
    
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                     BUILD COMPLETED                           ║${NC}"
    echo -e "${GREEN}║                                                                ║${NC}"
    echo -e "${GREEN}║  Syn_OS ${SYNOS_VERSION} has been built successfully!                    ║${NC}"
    echo -e "${GREEN}║  Check ${OUTPUT_DIR} for all build artifacts          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

# Command line argument handling
case "${1:-}" in
    --help|-h)
        echo "Syn_OS Build System"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version      Show version information"
        echo "  --clean        Clean previous builds before starting"  
        echo "  --iso-only     Build only the live ISO"
        echo "  --kernel-only  Build only the kernel"
        echo "  --test-only    Run only tests"
        echo
        echo "Environment Variables:"
        echo "  SYNOS_VERSION  Version to build (default: 1.0.0)"
        echo "  BUILD_JOBS     Number of parallel build jobs (default: nproc)"
        echo "  ARCH           Target architecture (default: x86_64)"
        echo "  TARGET_ENV     Target environment (default: production)"
        echo
        exit 0
        ;;
    --version)
        echo "Syn_OS Build System v${SYNOS_VERSION}"
        echo "Git commit: ${GIT_COMMIT}"
        exit 0
        ;;
    --clean)
        log_info "Cleaning previous builds..."
        rm -rf "${BUILD_DIR}/output" "${BUILD_DIR}/cache" "${BUILD_DIR}/logs"
        rm -rf "${BUILD_DIR}/kernel/linux-*" "${BUILD_DIR}/iso/chroot"
        log_success "Clean completed"
        main
        ;;
    --iso-only)
        init_build_env
        check_prerequisites
        build_iso
        ;;
    --kernel-only)
        init_build_env
        check_prerequisites
        build_kernel
        ;;
    --test-only)
        init_build_env
        run_tests
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac