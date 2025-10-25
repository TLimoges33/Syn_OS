#!/bin/bash

# SynOS Debian Packaging Pipeline
# Creates .deb packages for all AI components using APT/dpkg

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PACKAGES_DIR="${PROJECT_ROOT}/../SynOS-Packages"
BUILD_DIR="${PROJECT_ROOT}/packaging/build"
OUTPUT_DIR="${PROJECT_ROOT}/packaging/output"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[PACKAGING]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Package definitions
declare -A PACKAGES=(
    ["synos-consciousness"]="AI consciousness framework and neural darwinism engine"
    ["synos-security-tools"]="AI-enhanced security tools and reconnaissance systems"
    ["synos-nlp-interface"]="Natural language processing interface for security operations"
    ["synos-llm-hub"]="Local LLM integration engine for privacy-preserving AI"
    ["synos-smart-shell"]="Intelligent command completion and shell enhancements"
    ["synos-knowledge-base"]="Security knowledge graph with vector embeddings"
    ["synos-rag-system"]="Retrieval-augmented generation architecture"
    ["synos-adaptive-ui"]="Context-driven UI adaptation system"
    ["synos-smart-anonymity"]="Intelligent anonymity and privacy enhancement tools"
    ["synos-privacy-ai"]="Privacy-preserving AI analysis with homomorphic encryption"
    ["synos-mlops"]="MLOps and responsible AI framework"
)

# Dependencies for each package
declare -A DEPENDENCIES=(
    ["synos-consciousness"]="python3, python3-pip, python3-numpy, python3-scipy, systemd"
    ["synos-security-tools"]="python3, python3-pip, nmap, masscan, gobuster, nuclei, systemd"
    ["synos-nlp-interface"]="python3, python3-pip, python3-spacy, python3-transformers, systemd"
    ["synos-llm-hub"]="python3, python3-pip, python3-torch, python3-transformers, systemd"
    ["synos-smart-shell"]="python3, python3-pip, bash-completion, systemd"
    ["synos-knowledge-base"]="python3, python3-pip, python3-sqlite3, python3-faiss, systemd"
    ["synos-rag-system"]="python3, python3-pip, chromadb, python3-faiss, systemd"
    ["synos-adaptive-ui"]="python3, python3-pip, python3-gtk, mate-desktop-environment, systemd"
    ["synos-smart-anonymity"]="python3, python3-pip, tor, python3-scapy, systemd"
    ["synos-privacy-ai"]="python3, python3-pip, python3-tenseal, python3-concrete, systemd"
    ["synos-mlops"]="python3, python3-pip, python3-mlflow, python3-lime, python3-shap, systemd"
)

check_build_tools() {
    log "Checking build tools..."

    local required_tools=("dpkg-deb" "fakeroot" "debhelper" "dh_make")

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "Required tool '$tool' not found. Install with: sudo apt-get install build-essential devscripts debhelper"
        fi
    done

    log "Build tools verified"
}

create_package_structure() {
    local package_name="$1"
    local package_desc="$2"
    local version="$3"

    log "Creating package structure for $package_name"

    local pkg_dir="${BUILD_DIR}/${package_name}_${version}"
    local debian_dir="${pkg_dir}/DEBIAN"

    # Create directory structure
    mkdir -p "$debian_dir"
    mkdir -p "${pkg_dir}/opt/synos"
    mkdir -p "${pkg_dir}/etc/synos"
    mkdir -p "${pkg_dir}/usr/local/bin"
    mkdir -p "${pkg_dir}/lib/systemd/system"
    mkdir -p "${pkg_dir}/usr/share/doc/${package_name}"
    mkdir -p "${pkg_dir}/var/lib/synos"
    mkdir -p "${pkg_dir}/var/log/synos"

    # Create control file
    cat > "${debian_dir}/control" << EOF
Package: ${package_name}
Version: ${version}
Architecture: all
Maintainer: SynOS Development Team <dev@synos.ai>
Depends: ${DEPENDENCIES[$package_name]}
Priority: optional
Section: utils
Homepage: https://github.com/synos-ai/synos-linux
Description: ${package_desc}
 SynOS AI-Enhanced Linux Distribution component.
 .
 This package provides ${package_desc,,} as part of the
 comprehensive SynOS cybersecurity platform with integrated AI capabilities.
EOF

    # Create postinst script
    cat > "${debian_dir}/postinst" << 'EOF'
#!/bin/bash
set -e

# Create synos user if it doesn't exist
if ! getent passwd synos >/dev/null; then
    useradd -r -s /bin/false -d /var/lib/synos -c "SynOS AI System" synos
fi

# Set ownership and permissions
chown -R synos:synos /var/lib/synos 2>/dev/null || true
chown -R synos:synos /var/log/synos 2>/dev/null || true
chmod 755 /opt/synos/*/bin/* 2>/dev/null || true

# Reload systemd if services were installed
if [ -d /lib/systemd/system ]; then
    systemctl daemon-reload 2>/dev/null || true
fi

# Enable services but don't start them
for service in /lib/systemd/system/synos-*.service; do
    if [ -f "$service" ]; then
        service_name=$(basename "$service")
        systemctl enable "$service_name" 2>/dev/null || true
    fi
done

exit 0
EOF

    # Create prerm script
    cat > "${debian_dir}/prerm" << 'EOF'
#!/bin/bash
set -e

# Stop and disable services
for service in /lib/systemd/system/synos-*.service; do
    if [ -f "$service" ]; then
        service_name=$(basename "$service")
        systemctl stop "$service_name" 2>/dev/null || true
        systemctl disable "$service_name" 2>/dev/null || true
    fi
done

exit 0
EOF

    # Create postrm script
    cat > "${debian_dir}/postrm" << 'EOF'
#!/bin/bash
set -e

if [ "$1" = "purge" ]; then
    # Remove synos user on purge
    if getent passwd synos >/dev/null; then
        userdel synos 2>/dev/null || true
    fi

    # Remove data directories on purge
    rm -rf /var/lib/synos 2>/dev/null || true
    rm -rf /var/log/synos 2>/dev/null || true
fi

# Reload systemd
systemctl daemon-reload 2>/dev/null || true

exit 0
EOF

    # Make scripts executable
    chmod +x "${debian_dir}/postinst"
    chmod +x "${debian_dir}/prerm"
    chmod +x "${debian_dir}/postrm"

    # Create copyright file
    cat > "${pkg_dir}/usr/share/doc/${package_name}/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ${package_name}
Source: https://github.com/synos-ai/synos-linux

Files: *
Copyright: 2024 SynOS Development Team
License: AGPL-3+

License: AGPL-3+
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.
 .
 On Debian systems, the complete text of the GNU Affero General Public
 License version 3 can be found in "/usr/share/common-licenses/AGPL-3".
EOF

    # Create changelog
    cat > "${pkg_dir}/usr/share/doc/${package_name}/changelog.Debian" << EOF
${package_name} (${version}) unstable; urgency=medium

  * Initial release of SynOS AI-Enhanced Linux Distribution
  * Comprehensive cybersecurity platform with integrated AI
  * Privacy-preserving AI analysis capabilities
  * Advanced threat detection and response systems

 -- SynOS Development Team <dev@synos.ai>  $(date -R)
EOF

    gzip -9 "${pkg_dir}/usr/share/doc/${package_name}/changelog.Debian"

    return 0
}

copy_package_files() {
    local package_name="$1"
    local version="$2"

    log "Copying files for $package_name"

    local pkg_dir="${BUILD_DIR}/${package_name}_${version}"
    local source_dir="${PACKAGES_DIR}/${package_name}"

    if [ ! -d "$source_dir" ]; then
        warn "Source directory not found: $source_dir"
        return 1
    fi

    # Copy main application files
    if [ -d "${source_dir}/src" ]; then
        cp -r "${source_dir}/src" "${pkg_dir}/opt/synos/${package_name}/"
    fi

    if [ -d "${source_dir}/bin" ]; then
        cp -r "${source_dir}/bin" "${pkg_dir}/opt/synos/${package_name}/"

        # Create symlinks to executables in /usr/local/bin
        for executable in "${source_dir}/bin"/*; do
            if [ -x "$executable" ]; then
                exe_name=$(basename "$executable")
                ln -sf "/opt/synos/${package_name}/bin/${exe_name}" "${pkg_dir}/usr/local/bin/${exe_name}"
            fi
        done
    fi

    # Copy configuration files
    if [ -d "${source_dir}/config" ]; then
        cp -r "${source_dir}/config"/* "${pkg_dir}/etc/synos/" 2>/dev/null || true
    fi

    # Copy systemd services from filesystem-extract
    local services_dir="${PROJECT_ROOT}/filesystem-extract/etc/systemd/system"
    if [ -d "$services_dir" ]; then
        for service in "${services_dir}"/synos-*.service; do
            if [[ "$(basename "$service")" == *"${package_name##synos-}"* ]]; then
                cp "$service" "${pkg_dir}/lib/systemd/system/"
            fi
        done
    fi

    return 0
}

build_package() {
    local package_name="$1"
    local version="$2"

    log "Building package $package_name"

    local pkg_dir="${BUILD_DIR}/${package_name}_${version}"

    if [ ! -d "$pkg_dir" ]; then
        error "Package directory not found: $pkg_dir"
    fi

    # Set correct ownership and permissions
    find "$pkg_dir" -type d -exec chmod 755 {} \;
    find "$pkg_dir" -type f -exec chmod 644 {} \;
    find "$pkg_dir" -path "*/bin/*" -type f -exec chmod 755 {} \;
    find "$pkg_dir/DEBIAN" -type f -exec chmod 755 {} \;

    # Calculate installed size
    local installed_size
    installed_size=$(du -sk "$pkg_dir" | cut -f1)
    echo "Installed-Size: $installed_size" >> "${pkg_dir}/DEBIAN/control"

    # Build the .deb package
    local deb_file="${OUTPUT_DIR}/${package_name}_${version}_all.deb"

    if ! dpkg-deb --build "$pkg_dir" "$deb_file"; then
        error "Failed to build package $package_name"
    fi

    # Verify the package
    if ! dpkg-deb --info "$deb_file" >/dev/null 2>&1; then
        error "Package verification failed for $package_name"
    fi

    log "Successfully built: $(basename "$deb_file")"
    return 0
}

create_repository() {
    log "Creating APT repository..."

    local repo_dir="${OUTPUT_DIR}/repository"
    mkdir -p "$repo_dir"

    # Copy all .deb files to repository
    cp "${OUTPUT_DIR}"/*.deb "$repo_dir/" 2>/dev/null || true

    # Create Packages file
    cd "$repo_dir"
    dpkg-scanpackages . /dev/null > Packages
    gzip -k Packages

    # Create Release file
    cat > Release << EOF
Origin: SynOS
Label: SynOS AI-Enhanced Linux
Suite: stable
Codename: synos-stable
Version: 1.0
Architectures: all amd64 i386
Components: main
Description: SynOS AI-Enhanced Linux Distribution Repository
Date: $(date -u +"%a, %d %b %Y %H:%M:%S UTC")
EOF

    # Calculate checksums
    {
        echo "MD5Sum:"
        find . -name "Packages*" -exec md5sum {} \; | sed 's/^/ /'
        echo "SHA1:"
        find . -name "Packages*" -exec sha1sum {} \; | sed 's/^/ /'
        echo "SHA256:"
        find . -name "Packages*" -exec sha256sum {} \; | sed 's/^/ /'
    } >> Release

    log "APT repository created at: $repo_dir"
}

create_installation_script() {
    log "Creating installation script..."

    cat > "${OUTPUT_DIR}/install-synos-packages.sh" << 'EOF'
#!/bin/bash

# SynOS Package Installation Script

set -euo pipefail

REPO_URL="file://$(pwd)/repository"
GPG_KEY_URL=""

log() {
    echo -e "\033[0;32m[INSTALL]\033[0m $1"
}

error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
    exit 1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root (use sudo)"
fi

log "Installing SynOS AI-Enhanced Linux packages..."

# Add repository to sources.list
echo "deb [trusted=yes] $REPO_URL ./" > /etc/apt/sources.list.d/synos.list

# Update package lists
apt-get update

# Install all SynOS packages
log "Installing SynOS packages..."
apt-get install -y \
    synos-consciousness \
    synos-security-tools \
    synos-nlp-interface \
    synos-llm-hub \
    synos-smart-shell \
    synos-knowledge-base \
    synos-rag-system \
    synos-adaptive-ui \
    synos-smart-anonymity \
    synos-privacy-ai \
    synos-mlops

log "SynOS installation complete!"
log "Start services with: systemctl start synos-consciousness"
log "Check status with: systemctl status synos-*"
EOF

    chmod +x "${OUTPUT_DIR}/install-synos-packages.sh"
}

main() {
    log "Starting SynOS Debian packaging process..."

    # Clean and create directories
    rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
    mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

    # Check build tools
    check_build_tools

    # Package version
    local version="1.0.0"

    # Build each package
    for package_name in "${!PACKAGES[@]}"; do
        local package_desc="${PACKAGES[$package_name]}"

        log "Processing package: $package_name"

        # Create package structure
        create_package_structure "$package_name" "$package_desc" "$version"

        # Copy files
        if copy_package_files "$package_name" "$version"; then
            # Build package
            build_package "$package_name" "$version"
        else
            warn "Skipping $package_name due to missing files"
            rm -rf "${BUILD_DIR}/${package_name}_${version}"
        fi
    done

    # Create APT repository
    create_repository

    # Create installation script
    create_installation_script

    # Summary
    log "Packaging complete!"
    local deb_count
    deb_count=$(find "$OUTPUT_DIR" -name "*.deb" | wc -l)
    log "Created $deb_count .deb packages"
    log "Repository created at: ${OUTPUT_DIR}/repository"
    log "Installation script: ${OUTPUT_DIR}/install-synos-packages.sh"

    # Show package sizes
    echo
    echo "Package Summary:"
    echo "=================="
    for deb in "${OUTPUT_DIR}"/*.deb; do
        if [ -f "$deb" ]; then
            local size
            size=$(du -h "$deb" | cut -f1)
            local name
            name=$(basename "$deb")
            printf "%-40s %s\n" "$name" "$size"
        fi
    done
}

# Execute main function
main "$@"