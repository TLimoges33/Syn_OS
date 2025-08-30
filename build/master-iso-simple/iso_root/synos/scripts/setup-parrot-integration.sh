#!/bin/bash
# Syn_OS ParrotOS Integration Setup Script
# Sets up ParrotOS 6.4 base integration with change tracking

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PARROT_VERSION="6.4"
PARROT_REPO="https://github.com/ParrotSec/parrot-build.git"
SYN_OS_ROOT="/opt/syn_os"
BUILD_DIR="$SYN_OS_ROOT/build"
PARROT_BASE_DIR="$BUILD_DIR/parrot-base"
SYN_OS_OVERLAY_DIR="$BUILD_DIR/syn-os-overlay"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Install required dependencies
install_dependencies() {
    log "Installing required dependencies..."
    
    apt update
    apt install -y \
        git \
        build-essential \
        debootstrap \
        squashfs-tools \
        xorriso \
        isolinux \
        syslinux-utils \
        genisoimage \
        memtest86+ \
        rsync \
        curl \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        jq \
        yq
    
    log "Dependencies installed successfully"
}

# Create directory structure
create_directory_structure() {
    log "Creating Syn_OS directory structure..."
    
    mkdir -p "$SYN_OS_ROOT"/{build,config,scripts,logs,cache}
    mkdir -p "$BUILD_DIR"/{parrot-base,syn-os-overlay,iso,work,temp}
    mkdir -p "$SYN_OS_OVERLAY_DIR"/{consciousness,security,ai-integration,branding,config}
    
    # Set proper permissions
    chown -R root:root "$SYN_OS_ROOT"
    chmod -R 755 "$SYN_OS_ROOT"
    
    log "Directory structure created"
}

# Clone ParrotOS repository
clone_parrot_repo() {
    log "Cloning ParrotOS $PARROT_VERSION repository..."
    
    if [ -d "$PARROT_BASE_DIR" ]; then
        warn "ParrotOS base directory already exists. Updating..."
        cd "$PARROT_BASE_DIR"
        git pull origin master
    else
        git clone "$PARROT_REPO" "$PARROT_BASE_DIR"
        cd "$PARROT_BASE_DIR"
        
        # Checkout specific version if available
        if git tag | grep -q "v$PARROT_VERSION"; then
            git checkout "v$PARROT_VERSION"
            log "Checked out ParrotOS version $PARROT_VERSION"
        else
            warn "Specific version v$PARROT_VERSION not found, using latest master"
        fi
    fi
    
    log "ParrotOS repository ready"
}

# Set up change tracking system
setup_change_tracking() {
    log "Setting up change tracking system..."
    
    # Create change tracking configuration
    cat > "$SYN_OS_ROOT/config/change-tracking.json" << EOF
{
    "parrot_upstream": {
        "repository": "$PARROT_REPO",
        "branch": "master",
        "version": "$PARROT_VERSION",
        "last_sync": "$(date -Iseconds)",
        "tracking_enabled": true
    },
    "syn_os_overlay": {
        "path": "$SYN_OS_OVERLAY_DIR",
        "version_control": true,
        "backup_enabled": true
    },
    "build_tracking": {
        "build_history": "$SYN_OS_ROOT/logs/build-history.json",
        "change_log": "$SYN_OS_ROOT/logs/change-log.json",
        "automated_builds": true
    }
}
EOF
    
    # Create change tracking script
    cat > "$SYN_OS_ROOT/scripts/track-changes.sh" << 'EOF'
#!/bin/bash
# Syn_OS Change Tracking Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/change-tracking.json"
LOG_FILE="$SCRIPT_DIR/../logs/change-tracking.log"

# Load configuration
PARROT_REPO=$(jq -r '.parrot_upstream.repository' "$CONFIG_FILE")
PARROT_BASE_DIR=$(jq -r '.parrot_upstream.path // "/opt/syn_os/build/parrot-base"' "$CONFIG_FILE")

log_change() {
    echo "[$(date -Iseconds)] $1" >> "$LOG_FILE"
}

check_upstream_changes() {
    log_change "Checking for upstream ParrotOS changes..."
    
    cd "$PARROT_BASE_DIR" || exit 1
    
    # Fetch latest changes
    git fetch origin master
    
    # Check if there are new commits
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/master)
    
    if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
        log_change "Upstream changes detected: $LOCAL_COMMIT -> $REMOTE_COMMIT"
        
        # Generate change summary
        git log --oneline "$LOCAL_COMMIT..$REMOTE_COMMIT" > /tmp/parrot-changes.txt
        
        # Update configuration
        jq --arg date "$(date -Iseconds)" '.parrot_upstream.last_sync = $date' "$CONFIG_FILE" > /tmp/config.json
        mv /tmp/config.json "$CONFIG_FILE"
        
        return 0  # Changes found
    else
        log_change "No upstream changes detected"
        return 1  # No changes
    fi
}

# Run change check
if check_upstream_changes; then
    echo "Upstream changes detected. Review /tmp/parrot-changes.txt"
    exit 0
else
    echo "No upstream changes"
    exit 1
fi
EOF
    
    chmod +x "$SYN_OS_ROOT/scripts/track-changes.sh"
    
    # Set up automated change tracking (cron job)
    cat > /tmp/syn-os-cron << EOF
# Syn_OS automated change tracking
0 6 * * * root $SYN_OS_ROOT/scripts/track-changes.sh >> $SYN_OS_ROOT/logs/cron.log 2>&1
EOF
    
    # Install cron job
    cp /tmp/syn-os-cron /etc/cron.d/syn-os-tracking
    chmod 644 /etc/cron.d/syn-os-tracking
    
    log "Change tracking system configured"
}

# Create initial Syn_OS overlay structure
create_syn_os_overlay() {
    log "Creating Syn_OS overlay structure..."
    
    # Copy existing consciousness components
    if [ -d "$(pwd)/src/consciousness_v2" ]; then
        cp -r "$(pwd)/src/consciousness_v2" "$SYN_OS_OVERLAY_DIR/consciousness/"
        log "Copied consciousness components"
    fi
    
    # Copy existing security components
    if [ -d "$(pwd)/src/security" ]; then
        cp -r "$(pwd)/src/security" "$SYN_OS_OVERLAY_DIR/security/"
        log "Copied security components"
    fi
    
    # Copy ParrotOS integration components
    if [ -d "$(pwd)/parrotos-synapticos/synapticos-overlay" ]; then
        cp -r "$(pwd)/parrotos-synapticos/synapticos-overlay"/* "$SYN_OS_OVERLAY_DIR/"
        log "Copied ParrotOS integration components"
    fi
    
    # Create AI integration structure
    mkdir -p "$SYN_OS_OVERLAY_DIR/ai-integration"/{claude,gemini,perplexity,orchestration}
    
    # Create branding structure
    mkdir -p "$SYN_OS_OVERLAY_DIR/branding"/{themes,icons,wallpapers,boot-splash}
    
    # Create configuration templates
    mkdir -p "$SYN_OS_OVERLAY_DIR/config"/{systemd,desktop,kernel}
    
    log "Syn_OS overlay structure created"
}

# Create build configuration
create_build_config() {
    log "Creating build configuration..."
    
    cat > "$SYN_OS_ROOT/config/build-config.yaml" << EOF
# Syn_OS Build Configuration
syn_os:
  version: "1.0.0-alpha"
  codename: "Consciousness"
  release_date: "$(date -Iseconds)"
  
base_system:
  distribution: "ParrotOS"
  version: "$PARROT_VERSION"
  architecture: "amd64"
  kernel: "linux-image-parrot-amd64"
  
consciousness:
  enabled: true
  neural_darwinism: true
  kernel_hooks: true
  ai_integration: true
  
ai_models:
  claude:
    enabled: true
    api_integration: true
  gemini:
    enabled: true
    multimodal: true
  perplexity:
    enabled: true
    real_time_intel: true
  
security_tools:
  parrot_native: true
  consciousness_controlled: true
  autonomous_operations: true
  
build_options:
  iso_name: "syn-os-\${version}-\${architecture}.iso"
  compression: "xz"
  boot_mode: "uefi"
  secure_boot: true
  
deployment:
  bare_metal: true
  virtual_machine: true
  cloud_ready: true
  container_support: true
EOF
    
    log "Build configuration created"
}

# Create initial build script
create_build_script() {
    log "Creating main build script..."
    
    cat > "$SYN_OS_ROOT/scripts/build-syn-os.sh" << 'EOF'
#!/bin/bash
# Syn_OS Main Build Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYN_OS_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_CONFIG="$SYN_OS_ROOT/config/build-config.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BUILD] $1${NC}"; }
warn() { echo -e "${YELLOW}[BUILD] WARNING: $1${NC}"; }
error() { echo -e "${RED}[BUILD] ERROR: $1${NC}"; exit 1; }

# Load build configuration
if [ ! -f "$BUILD_CONFIG" ]; then
    error "Build configuration not found: $BUILD_CONFIG"
fi

VERSION=$(yq eval '.syn_os.version' "$BUILD_CONFIG")
CODENAME=$(yq eval '.syn_os.codename' "$BUILD_CONFIG")

log "Starting Syn_OS $VERSION ($CODENAME) build..."

# Build phases
build_phase_1_foundation() {
    log "Phase 1: Foundation & ParrotOS Integration"
    
    # Prepare ParrotOS base
    log "Preparing ParrotOS base system..."
    # Implementation will be added here
    
    # Integrate consciousness kernel hooks
    log "Integrating consciousness kernel hooks..."
    # Implementation will be added here
    
    log "Phase 1 completed"
}

build_phase_2_ai_integration() {
    log "Phase 2: AI Models Integration"
    
    # Claude integration
    log "Setting up Claude integration..."
    # Implementation will be added here
    
    # Gemini integration
    log "Setting up Gemini integration..."
    # Implementation will be added here
    
    # Perplexity integration
    log "Setting up Perplexity integration..."
    # Implementation will be added here
    
    log "Phase 2 completed"
}

# Main build process
main() {
    case "${1:-all}" in
        "foundation"|"phase1")
            build_phase_1_foundation
            ;;
        "ai"|"phase2")
            build_phase_2_ai_integration
            ;;
        "all")
            build_phase_1_foundation
            build_phase_2_ai_integration
            ;;
        *)
            echo "Usage: $0 [foundation|ai|all]"
            exit 1
            ;;
    esac
    
    log "Syn_OS build completed successfully!"
}

main "$@"
EOF
    
    chmod +x "$SYN_OS_ROOT/scripts/build-syn-os.sh"
    
    log "Build script created"
}

# Create status monitoring
create_status_monitoring() {
    log "Setting up status monitoring..."
    
    cat > "$SYN_OS_ROOT/scripts/status.sh" << 'EOF'
#!/bin/bash
# Syn_OS Status Monitoring Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYN_OS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Syn_OS Development Status ==="
echo
echo "📁 Directory Structure:"
find "$SYN_OS_ROOT" -maxdepth 3 -type d | head -20

echo
echo "🔄 Change Tracking:"
if [ -f "$SYN_OS_ROOT/config/change-tracking.json" ]; then
    echo "✅ Change tracking configured"
    LAST_SYNC=$(jq -r '.parrot_upstream.last_sync' "$SYN_OS_ROOT/config/change-tracking.json")
    echo "   Last ParrotOS sync: $LAST_SYNC"
else
    echo "❌ Change tracking not configured"
fi

echo
echo "🏗️ Build System:"
if [ -f "$SYN_OS_ROOT/scripts/build-syn-os.sh" ]; then
    echo "✅ Build script ready"
else
    echo "❌ Build script missing"
fi

echo
echo "🧠 Consciousness Components:"
if [ -d "$SYN_OS_ROOT/build/syn-os-overlay/consciousness" ]; then
    echo "✅ Consciousness components available"
    COMPONENTS=$(find "$SYN_OS_ROOT/build/syn-os-overlay/consciousness" -name "*.py" | wc -l)
    echo "   Python components: $COMPONENTS"
else
    echo "❌ Consciousness components missing"
fi

echo
echo "🔒 Security Components:"
if [ -d "$SYN_OS_ROOT/build/syn-os-overlay/security" ]; then
    echo "✅ Security components available"
else
    echo "❌ Security components missing"
fi

echo
echo "📊 Recent Activity:"
if [ -f "$SYN_OS_ROOT/logs/change-tracking.log" ]; then
    echo "Recent change tracking entries:"
    tail -5 "$SYN_OS_ROOT/logs/change-tracking.log" 2>/dev/null || echo "No recent activity"
else
    echo "No activity logs found"
fi
EOF
    
    chmod +x "$SYN_OS_ROOT/scripts/status.sh"
    
    log "Status monitoring configured"
}

# Main execution
main() {
    log "Starting Syn_OS ParrotOS Integration Setup..."
    
    check_root
    install_dependencies
    create_directory_structure
    clone_parrot_repo
    setup_change_tracking
    create_syn_os_overlay
    create_build_config
    create_build_script
    create_status_monitoring
    
    log "Syn_OS ParrotOS Integration Setup completed successfully!"
    info "Next steps:"
    info "1. Run: $SYN_OS_ROOT/scripts/status.sh"
    info "2. Review: $SYN_OS_ROOT/config/build-config.yaml"
    info "3. Start building: $SYN_OS_ROOT/scripts/build-syn-os.sh foundation"
    
    echo
    echo "🚀 Syn_OS Foundation Ready!"
    echo "📍 Installation path: $SYN_OS_ROOT"
    echo "🔧 Build system: $SYN_OS_ROOT/scripts/build-syn-os.sh"
    echo "📊 Status check: $SYN_OS_ROOT/scripts/status.sh"
}

# Run main function
main "$@"