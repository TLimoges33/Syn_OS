#!/bin/bash
# Syn_OS Package Repository Setup Script
# Create APT and YUM repositories for community updates

set -e

# Configuration
REPO_VERSION="1.0.0"
REPO_BASE_DIR="repository"
GPG_KEY_ID="syn-os-signing-key"
REPO_ORIGIN="Syn_OS"
REPO_LABEL="Syn_OS Consciousness-Integrated Linux"
REPO_DESCRIPTION="Official package repository for Syn_OS consciousness services and updates"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_phase() { echo -e "${PURPLE}[PHASE]${NC} $1"; }

check_prerequisites() {
    log_phase "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("dpkg-dev" "reprepro" "createrepo" "gpg" "docker")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_warning "Missing tools: ${missing_tools[*]}"
        log_info "Installing missing dependencies..."
        
        # Install on Ubuntu/Debian
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y dpkg-dev reprepro createrepo-c gnupg docker.io
        # Install on CentOS/RHEL
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y rpm-build createrepo gnupg docker
        # Install on Fedora
        elif command -v dnf >/dev/null 2>&1; then
            sudo dnf install -y rpm-build createrepo gnupg docker
        else
            log_error "Unsupported package manager. Please install required tools manually."
            exit 1
        fi
    fi
    
    log_success "Prerequisites checked"
}

setup_gpg_signing() {
    log_phase "Setting up GPG signing key..."
    
    # Check if GPG key exists
    if ! gpg --list-secret-keys | grep -q "$GPG_KEY_ID"; then
        log_info "Creating GPG signing key for package repository..."
        
        cat > gpg-key-config << EOF
%echo Generating Syn_OS package signing key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Syn_OS Package Repository
Name-Comment: Official package signing key
Name-Email: packages@syn-os.org
Expire-Date: 2y
Passphrase: 
%commit
%echo GPG key generated
EOF
        
        gpg --batch --generate-key gpg-key-config
        rm gpg-key-config
        
        log_success "GPG signing key created"
    else
        log_info "Using existing GPG key: $GPG_KEY_ID"
    fi
    
    # Export public key
    gpg --armor --export packages@syn-os.org > "$REPO_BASE_DIR/syn-os-keyring.gpg"
    
    log_success "GPG setup complete"
}

create_repository_structure() {
    log_phase "Creating repository directory structure..."
    
    # Create base directories
    mkdir -p "$REPO_BASE_DIR"/{apt,yum,docker,docs}
    
    # APT repository structure
    mkdir -p "$REPO_BASE_DIR/apt"/{pool,dists}
    mkdir -p "$REPO_BASE_DIR/apt/pool/main"/{s,c,e}  # syn-os, consciousness, educational
    mkdir -p "$REPO_BASE_DIR/apt/dists/stable"/{main,contrib,non-free}/binary-{amd64,arm64,armhf}
    mkdir -p "$REPO_BASE_DIR/apt/dists/testing"/{main,contrib,non-free}/binary-{amd64,arm64,armhf}
    mkdir -p "$REPO_BASE_DIR/apt/dists/unstable"/{main,contrib,non-free}/binary-{amd64,arm64,armhf}
    
    # YUM repository structure  
    mkdir -p "$REPO_BASE_DIR/yum"/{stable,testing,unstable}/{x86_64,aarch64,armv7hl}
    mkdir -p "$REPO_BASE_DIR/yum/repodata"
    
    # Docker registry structure
    mkdir -p "$REPO_BASE_DIR/docker"/{consciousness,educational,context-intelligence,ctf}
    
    log_success "Repository structure created"
}

create_apt_configuration() {
    log_phase "Setting up APT repository configuration..."
    
    # Create reprepro configuration
    mkdir -p "$REPO_BASE_DIR/apt/conf"
    
    cat > "$REPO_BASE_DIR/apt/conf/options" << EOF
verbose
ask-passphrase
basedir .
EOF
    
    cat > "$REPO_BASE_DIR/apt/conf/distributions" << EOF
Origin: $REPO_ORIGIN
Label: $REPO_LABEL
Codename: stable
Architectures: amd64 arm64 armhf source
Components: main contrib non-free
Description: $REPO_DESCRIPTION (stable)
SignWith: packages@syn-os.org
Pull: testing

Origin: $REPO_ORIGIN
Label: $REPO_LABEL
Codename: testing
Architectures: amd64 arm64 armhf source
Components: main contrib non-free
Description: $REPO_DESCRIPTION (testing)
SignWith: packages@syn-os.org
Pull: unstable

Origin: $REPO_ORIGIN
Label: $REPO_LABEL
Codename: unstable
Architectures: amd64 arm64 armhf source
Components: main contrib non-free
Description: $REPO_DESCRIPTION (unstable)
SignWith: packages@syn-os.org
EOF
    
    cat > "$REPO_BASE_DIR/apt/conf/incoming" << EOF
Name: default
IncomingDir: incoming
TempDir: tmp
Allow: stable testing unstable
Cleanup: unused_files on_error on_deny
EOF
    
    log_success "APT configuration created"
}

build_consciousness_packages() {
    log_phase "Building consciousness service packages..."
    
    local services=("consciousness-unified" "educational-unified" "context-intelligence-unified" "ctf-unified")
    
    for service in "${services[@]}"; do
        log_info "Building package for $service..."
        
        # Create package directory
        local pkg_dir="packaging/$service"
        mkdir -p "$pkg_dir/DEBIAN"
        mkdir -p "$pkg_dir/opt/synos/services/$service"
        mkdir -p "$pkg_dir/etc/systemd/system"
        mkdir -p "$pkg_dir/usr/share/doc/$service"
        
        # Copy service files
        if [ -d "services/$service" ]; then
            cp -r "services/$service"/* "$pkg_dir/opt/synos/services/$service/"
            
            # Copy systemd service file if exists
            if [ -f "services/$service/${service}.service" ]; then
                cp "services/$service/${service}.service" "$pkg_dir/etc/systemd/system/"
            fi
        fi
        
        # Create control file
        cat > "$pkg_dir/DEBIAN/control" << EOF
Package: syn-os-$service
Version: $REPO_VERSION
Section: net
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.11), python3-pip, docker.io
Maintainer: Syn_OS Team <packages@syn-os.org>
Description: Syn_OS $service
 Part of the Syn_OS consciousness-integrated Linux distribution.
 This package provides the $service for consciousness-enhanced computing.
Homepage: https://syn-os.org
EOF
        
        # Create postinst script
        cat > "$pkg_dir/DEBIAN/postinst" << EOF
#!/bin/bash
set -e

# Install Python dependencies
if [ -f /opt/synos/services/$service/requirements.txt ]; then
    pip3 install -r /opt/synos/services/$service/requirements.txt
fi

# Enable and start service
if [ -f /etc/systemd/system/${service}.service ]; then
    systemctl daemon-reload
    systemctl enable ${service}.service
fi

echo "Syn_OS $service installed successfully"
EOF
        chmod +x "$pkg_dir/DEBIAN/postinst"
        
        # Create prerm script
        cat > "$pkg_dir/DEBIAN/prerm" << EOF
#!/bin/bash
set -e

# Stop service if running
if systemctl is-active --quiet ${service}.service; then
    systemctl stop ${service}.service
fi

# Disable service
if systemctl is-enabled --quiet ${service}.service; then
    systemctl disable ${service}.service
fi
EOF
        chmod +x "$pkg_dir/DEBIAN/prerm"
        
        # Build package
        dpkg-deb --build "$pkg_dir" "$REPO_BASE_DIR/apt/pool/main/${service:0:1}/syn-os-${service}_${REPO_VERSION}_amd64.deb"
        
        log_success "Package built: syn-os-$service"
    done
}

create_metapackages() {
    log_phase "Creating metapackages..."
    
    # Create syn-os-full metapackage
    local meta_dir="packaging/syn-os-full"
    mkdir -p "$meta_dir/DEBIAN"
    mkdir -p "$meta_dir/usr/share/doc/syn-os-full"
    
    cat > "$meta_dir/DEBIAN/control" << EOF
Package: syn-os-full
Version: $REPO_VERSION
Section: metapackages
Priority: optional
Architecture: all
Depends: syn-os-consciousness-unified, syn-os-educational-unified, syn-os-context-intelligence-unified, syn-os-ctf-unified, postgresql, redis-server, docker.io
Recommends: nginx, prometheus, grafana
Maintainer: Syn_OS Team <packages@syn-os.org>
Description: Complete Syn_OS consciousness-integrated system
 This metapackage installs all components of the Syn_OS consciousness-integrated
 Linux distribution, including all consciousness services, databases, and
 supporting infrastructure.
Homepage: https://syn-os.org
EOF
    
    cat > "$meta_dir/DEBIAN/postinst" << EOF
#!/bin/bash
set -e

echo "Starting Syn_OS full installation..."

# Start infrastructure services
systemctl enable postgresql redis-server docker
systemctl start postgresql redis-server docker

# Configure databases
sudo -u postgres createdb synos || true
sudo -u postgres createuser synos || true

# Start consciousness services
systemctl start consciousness-unified.service
systemctl start educational-unified.service  
systemctl start context-intelligence-unified.service
systemctl start ctf-unified.service

echo ""
echo "🎉 Syn_OS installation complete!"
echo ""
echo "Access points:"
echo "🧠 Consciousness Dashboard: http://localhost:8080"
echo "🎓 Educational Platform: http://localhost:8081"
echo "🔍 Context Intelligence: http://localhost:8082"
echo "🏁 CTF Platform: http://localhost:8083"
echo ""
echo "Default login: syn-user / consciousness"
echo "Documentation: https://docs.syn-os.org"
EOF
    chmod +x "$meta_dir/DEBIAN/postinst"
    
    # Build metapackage
    dpkg-deb --build "$meta_dir" "$REPO_BASE_DIR/apt/pool/main/s/syn-os-full_${REPO_VERSION}_all.deb"
    
    log_success "Metapackages created"
}

update_apt_repository() {
    log_phase "Updating APT repository..."
    
    cd "$REPO_BASE_DIR/apt"
    
    # Add packages to repository
    for deb in pool/main/*/*.deb; do
        if [ -f "$deb" ]; then
            reprepro includedeb stable "$deb"
        fi
    done
    
    cd ../..
    
    log_success "APT repository updated"
}

create_yum_repository() {
    log_phase "Creating YUM repository..."
    
    # Note: For a complete YUM repo, we'd need to build RPM packages
    # This creates the structure and metadata for future RPM builds
    
    cd "$REPO_BASE_DIR/yum/stable/x86_64"
    
    # Create repository metadata
    createrepo .
    
    # Sign repository metadata
    gpg --detach-sign --armor repodata/repomd.xml
    
    cd ../../..
    
    # Create repo configuration file
    cat > "$REPO_BASE_DIR/yum/syn-os.repo" << EOF
[syn-os-stable]
name=Syn_OS Stable Repository
baseurl=https://packages.syn-os.org/yum/stable/\$basearch/
enabled=1
gpgcheck=1
gpgkey=https://packages.syn-os.org/syn-os-keyring.gpg

[syn-os-testing]
name=Syn_OS Testing Repository
baseurl=https://packages.syn-os.org/yum/testing/\$basearch/
enabled=0
gpgcheck=1
gpgkey=https://packages.syn-os.org/syn-os-keyring.gpg

[syn-os-unstable]
name=Syn_OS Unstable Repository
baseurl=https://packages.syn-os.org/yum/unstable/\$basearch/
enabled=0
gpgcheck=1
gpgkey=https://packages.syn-os.org/syn-os-keyring.gpg
EOF
    
    log_success "YUM repository structure created"
}

create_docker_registry() {
    log_phase "Setting up Docker registry structure..."
    
    # Create registry configuration
    cat > "$REPO_BASE_DIR/docker/config.yml" << EOF
version: 0.1
log:
  fields:
    service: registry
storage:
  filesystem:
    rootdirectory: /var/lib/registry
  cache:
    blobdescriptor: inmemory
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
EOF
    
    # Create registry startup script
    cat > "$REPO_BASE_DIR/docker/start-registry.sh" << EOF
#!/bin/bash
# Start local Syn_OS Docker registry

docker run -d \\
  -p 5000:5000 \\
  --restart=always \\
  --name syn-os-registry \\
  -v \$(pwd)/config.yml:/etc/docker/registry/config.yml \\
  -v \$(pwd)/data:/var/lib/registry \\
  registry:2

echo "Syn_OS Docker registry started on port 5000"
echo "Push images with: docker tag <image> localhost:5000/<image>"
echo "                  docker push localhost:5000/<image>"
EOF
    chmod +x "$REPO_BASE_DIR/docker/start-registry.sh"
    
    log_success "Docker registry configuration created"
}

create_installation_instructions() {
    log_phase "Creating installation instructions..."
    
    cat > "$REPO_BASE_DIR/docs/repository-setup.md" << EOF
# Syn_OS Package Repository Setup

## APT Repository (Ubuntu/Debian)

### Add Repository
\`\`\`bash
# Add GPG key
curl -fsSL https://packages.syn-os.org/syn-os-keyring.gpg | sudo apt-key add -

# Add repository
echo "deb https://packages.syn-os.org/apt stable main" | sudo tee /etc/apt/sources.list.d/syn-os.list

# Update package list
sudo apt update
\`\`\`

### Install Syn_OS
\`\`\`bash
# Install complete system
sudo apt install syn-os-full

# Or install individual services
sudo apt install syn-os-consciousness-unified
sudo apt install syn-os-educational-unified
sudo apt install syn-os-context-intelligence-unified
sudo apt install syn-os-ctf-unified
\`\`\`

## YUM Repository (CentOS/RHEL/Fedora)

### Add Repository
\`\`\`bash
# Add repository configuration
sudo curl -o /etc/yum.repos.d/syn-os.repo https://packages.syn-os.org/yum/syn-os.repo

# Import GPG key
sudo rpm --import https://packages.syn-os.org/syn-os-keyring.gpg
\`\`\`

### Install Syn_OS
\`\`\`bash
# Install complete system
sudo yum install syn-os-full

# Or install individual services
sudo yum install syn-os-consciousness-unified
\`\`\`

## Docker Registry

### Pull Images
\`\`\`bash
# Pull consciousness services
docker pull packages.syn-os.org/consciousness-unified:latest
docker pull packages.syn-os.org/educational-unified:latest
docker pull packages.syn-os.org/context-intelligence-unified:latest
docker pull packages.syn-os.org/ctf-unified:latest

# Quick start with compose
curl -o docker-compose.yml https://packages.syn-os.org/docker-compose.yml
docker-compose up -d
\`\`\`

## Verification

### Check Installation
\`\`\`bash
# Check service status
systemctl status consciousness-unified
systemctl status educational-unified

# Access web interfaces
curl http://localhost:8080/health  # Consciousness
curl http://localhost:8081/health  # Educational
curl http://localhost:8082/health  # Context Intelligence  
curl http://localhost:8083/health  # CTF Platform
\`\`\`

### Package Information
\`\`\`bash
# APT
apt show syn-os-full
apt list syn-os-*

# YUM  
yum info syn-os-full
yum list syn-os-*
\`\`\`

## Support

- **Documentation**: https://docs.syn-os.org
- **Forums**: https://community.syn-os.org
- **Issues**: https://github.com/syn-os/syn-os/issues
- **Email**: packages@syn-os.org
EOF
    
    log_success "Installation instructions created"
}

generate_repository_website() {
    log_phase "Generating repository website..."
    
    cat > "$REPO_BASE_DIR/docs/index.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Syn_OS Package Repository</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; background: linear-gradient(45deg, #2196F3, #9C27B0); color: white; padding: 2rem; border-radius: 10px; }
        .section { margin: 2rem 0; padding: 1rem; background: #f5f5f5; border-radius: 5px; }
        .code { background: #333; color: #fff; padding: 1rem; border-radius: 5px; overflow-x: auto; }
        .download-btn { background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📦 Syn_OS Package Repository</h1>
        <p>Official packages for the world's first consciousness-integrated Linux distribution</p>
    </div>

    <div class="section">
        <h2>🚀 Quick Install</h2>
        <h3>Ubuntu/Debian (APT)</h3>
        <div class="code">
curl -fsSL https://packages.syn-os.org/syn-os-keyring.gpg | sudo apt-key add -<br>
echo "deb https://packages.syn-os.org/apt stable main" | sudo tee /etc/apt/sources.list.d/syn-os.list<br>
sudo apt update && sudo apt install syn-os-full
        </div>

        <h3>CentOS/RHEL/Fedora (YUM)</h3>
        <div class="code">
sudo curl -o /etc/yum.repos.d/syn-os.repo https://packages.syn-os.org/yum/syn-os.repo<br>
sudo yum install syn-os-full
        </div>
    </div>

    <div class="section">
        <h2>📋 Available Packages</h2>
        <ul>
            <li><strong>syn-os-full</strong> - Complete consciousness-integrated system</li>
            <li><strong>syn-os-consciousness-unified</strong> - Neural Darwinism consciousness engine</li>
            <li><strong>syn-os-educational-unified</strong> - AI-powered educational platform</li>
            <li><strong>syn-os-context-intelligence-unified</strong> - Context processing and news intelligence</li>
            <li><strong>syn-os-ctf-unified</strong> - Dynamic CTF challenge platform</li>
        </ul>
    </div>

    <div class="section">
        <h2>🔗 Resources</h2>
        <a href="repository-setup.md" class="download-btn">Setup Guide</a>
        <a href="../syn-os-keyring.gpg" class="download-btn">GPG Key</a>
        <a href="https://syn-os.org" class="download-btn">Main Site</a>
        <a href="https://docs.syn-os.org" class="download-btn">Documentation</a>
    </div>

    <div class="section">
        <h2>ℹ️ Repository Information</h2>
        <p><strong>Version:</strong> $REPO_VERSION</p>
        <p><strong>Last Updated:</strong> $(date)</p>
        <p><strong>Architectures:</strong> amd64, arm64, armhf</p>
        <p><strong>Components:</strong> main, contrib, non-free</p>
        <p><strong>GPG Fingerprint:</strong> $(gpg --fingerprint packages@syn-os.org | grep fingerprint | cut -d'=' -f2 | tr -d ' ')</p>
    </div>
</body>
</html>
EOF
    
    log_success "Repository website generated"
}

display_summary() {
    log_phase "🎉 Package Repository Setup Complete"
    echo "======================================"
    echo ""
    echo "📦 **APT Repository Ready:**"
    echo "   • Location: $REPO_BASE_DIR/apt/"
    echo "   • Packages: $(find $REPO_BASE_DIR/apt/pool -name "*.deb" | wc -l) DEB packages created"
    echo "   • GPG Signed: Yes"
    echo ""
    echo "📦 **YUM Repository Structure:**"
    echo "   • Location: $REPO_BASE_DIR/yum/"
    echo "   • Configuration: syn-os.repo created"
    echo "   • Metadata: Repository structure ready"
    echo ""
    echo "🐳 **Docker Registry:**"
    echo "   • Configuration: $REPO_BASE_DIR/docker/config.yml"
    echo "   • Startup script: start-registry.sh"
    echo ""
    echo "📚 **Documentation:**"
    echo "   • Installation guide: repository-setup.md"
    echo "   • Website: index.html"
    echo "   • GPG key: syn-os-keyring.gpg"
    echo ""
    echo "🔧 **Next Steps:**"
    echo "   1. Upload repository to hosting (packages.syn-os.org)"
    echo "   2. Configure web server with proper MIME types"
    echo "   3. Set up automated package building pipeline"
    echo "   4. Test installation on clean systems"
    echo ""
    echo "🌍 **Community Installation Commands:**"
    echo "   APT: curl -fsSL https://packages.syn-os.org/setup-apt.sh | sudo bash"
    echo "   YUM: curl -fsSL https://packages.syn-os.org/setup-yum.sh | sudo bash"
    echo ""
    log_success "Package repositories ready for community deployment!"
}

# Main execution
main() {
    echo "📦 Setting up Syn_OS Package Repositories"
    echo "========================================="
    echo ""
    
    check_prerequisites
    setup_gpg_signing
    create_repository_structure
    create_apt_configuration
    build_consciousness_packages
    create_metapackages
    update_apt_repository
    create_yum_repository
    create_docker_registry
    create_installation_instructions
    generate_repository_website
    display_summary
    
    log_success "🎉 Package repository setup complete!"
}

# Execute main function
main "$@"