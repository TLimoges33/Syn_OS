#!/usr/bin/env bash
################################################################################
# SynOS Docker Build Tool
# 
# Reproducible container-based builds for SynOS ISO images.
#
# Usage:
#   ./scripts/docker/build-docker.sh [OPTIONS]
#
# Options:
#   --build           Build SynOS in Docker container
#   --shell           Open interactive shell in build container
#   --clean           Remove build containers and images
#   --image NAME      Docker image to use (default: synos-builder)
#   --tag TAG         Docker image tag (default: latest)
#   --platform ARCH   Target platform (default: linux/amd64)
#   --no-cache        Build without Docker cache
#   --output DIR      Output directory for artifacts (default: build/)
#   --dockerfile FILE Custom Dockerfile (default: docker/Dockerfile.builder)
#   --verbose         Show detailed build output
#   --help            Show this help message
#
# Features:
#   - Reproducible builds in isolated containers
#   - Multi-stage build support
#   - Caching for faster rebuilds
#   - Cross-platform support
#   - Artifact extraction from container
#
# Examples:
#   # Build ISO in Docker
#   ./scripts/docker/build-docker.sh --build
#
#   # Build with custom image
#   ./scripts/docker/build-docker.sh --build --image custom-builder
#
#   # Open shell for debugging
#   ./scripts/docker/build-docker.sh --shell
#
#   # Clean up Docker artifacts
#   ./scripts/docker/build-docker.sh --clean
#
# Exit Codes:
#   0 - Success
#   1 - Build error
#   2 - Docker not available
#
################################################################################

set -euo pipefail

# Determine project root first
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PROJECT_ROOT

# Source shared library
source "${SCRIPT_DIR}/../lib/build-common.sh"

################################################################################
# Configuration
################################################################################

MODE=""  # build, shell, clean
IMAGE_NAME="synos-builder"
IMAGE_TAG="latest"
PLATFORM="linux/amd64"
NO_CACHE=false
OUTPUT_DIR="${PROJECT_ROOT}/build"
DOCKERFILE="${PROJECT_ROOT}/docker/Dockerfile.builder"
VERBOSE=false

# Container name
CONTAINER_NAME="synos-build-${USER}-$$"

################################################################################
# Argument Parsing
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            MODE="build"
            shift
            ;;
        --shell)
            MODE="shell"
            shift
            ;;
        --clean)
            MODE="clean"
            shift
            ;;
        --image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate mode
if [[ -z "$MODE" ]]; then
    error "No mode specified. Use --build, --shell, or --clean"
    exit 1
fi

################################################################################
# Helper Functions
################################################################################

check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Install: https://docs.docker.com/get-docker/"
        exit 2
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon not running. Start with: sudo systemctl start docker"
        exit 2
    fi
    
    # Check if user has Docker permissions
    if ! docker ps &> /dev/null; then
        warning "No Docker permissions. You may need to run with sudo or add user to docker group:"
        warning "  sudo usermod -aG docker $USER"
        warning "  newgrp docker"
    fi
}

create_dockerfile() {
    local dockerfile="$1"
    
    if [[ -f "$dockerfile" ]]; then
        info "Using existing Dockerfile: $dockerfile"
        return 0
    fi
    
    info "Creating default Dockerfile..."
    
    mkdir -p "$(dirname "$dockerfile")"
    
    cat > "$dockerfile" << 'DOCKERFILE_EOF'
# SynOS Builder Image
FROM rust:1.75-bookworm

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    squashfs-tools \
    debootstrap \
    qemu-system-x86 \
    && rm -rf /var/lib/apt/lists/*

# Install Rust nightly and x86_64-unknown-none target
RUN rustup default nightly && \
    rustup target add x86_64-unknown-none

# Set working directory
WORKDIR /synos

# Copy project files
COPY . .

# Set environment
ENV RUST_BACKTRACE=1
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTUP_HOME=/usr/local/rustup

# Default command
CMD ["/bin/bash"]
DOCKERFILE_EOF
    
    success "Created Dockerfile: $dockerfile"
}

build_image() {
    section "Building Docker Image"
    
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    
    info "Image: $full_image"
    info "Platform: $PLATFORM"
    info "Dockerfile: $DOCKERFILE"
    echo ""
    
    # Create Dockerfile if it doesn't exist
    create_dockerfile "$DOCKERFILE"
    
    # Build Docker image
    local docker_cmd="docker build"
    docker_cmd="$docker_cmd --platform $PLATFORM"
    docker_cmd="$docker_cmd -t $full_image"
    docker_cmd="$docker_cmd -f $DOCKERFILE"
    
    if [[ "$NO_CACHE" == true ]]; then
        docker_cmd="$docker_cmd --no-cache"
    fi
    
    docker_cmd="$docker_cmd $PROJECT_ROOT"
    
    info "Building image..."
    
    if [[ "$VERBOSE" == true ]]; then
        eval "$docker_cmd"
    else
        eval "$docker_cmd" > /dev/null 2>&1
    fi
    
    success "✓ Image built: $full_image"
}

build_in_container() {
    section "Building SynOS in Container"
    
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Ensure image exists
    if ! docker image inspect "$full_image" &> /dev/null; then
        info "Image not found, building..."
        build_image
        echo ""
    fi
    
    info "Starting build container..."
    
    # Run build in container
    local docker_cmd="docker run --rm"
    docker_cmd="$docker_cmd --name $CONTAINER_NAME"
    docker_cmd="$docker_cmd --platform $PLATFORM"
    docker_cmd="$docker_cmd -v ${PROJECT_ROOT}:/synos"
    docker_cmd="$docker_cmd -w /synos"
    docker_cmd="$docker_cmd $full_image"
    
    # Build command inside container
    local build_cmd="./scripts/build-iso.sh"
    
    docker_cmd="$docker_cmd bash -c '$build_cmd'"
    
    info "Running build..."
    echo ""
    
    if eval "$docker_cmd"; then
        echo ""
        success "✓ Build completed successfully"
        
        # Show output artifacts
        if [[ -d "$OUTPUT_DIR" ]]; then
            echo ""
            section "Build Artifacts"
            
            find "$OUTPUT_DIR" -maxdepth 1 -name "*.iso" -type f -exec ls -lh {} \; | \
                awk '{print "  " $9 " (" $5 ")"}'
        fi
        
        return 0
    else
        error "✗ Build failed"
        return 1
    fi
}

open_shell() {
    section "Opening Build Container Shell"
    
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    
    # Ensure image exists
    if ! docker image inspect "$full_image" &> /dev/null; then
        info "Image not found, building..."
        build_image
        echo ""
    fi
    
    info "Starting interactive shell..."
    info "Container: $CONTAINER_NAME"
    echo ""
    info "To exit, type: exit"
    echo ""
    
    # Run interactive shell
    docker run --rm -it \
        --name "$CONTAINER_NAME" \
        --platform "$PLATFORM" \
        -v "${PROJECT_ROOT}:/synos" \
        -w /synos \
        "$full_image" \
        /bin/bash
}

clean_docker() {
    section "Cleaning Docker Artifacts"
    
    local full_image="${IMAGE_NAME}:${IMAGE_TAG}"
    local cleaned=0
    
    # Stop running containers
    if docker ps -a | grep -q "$IMAGE_NAME"; then
        info "Stopping containers..."
        docker ps -a | grep "$IMAGE_NAME" | awk '{print $1}' | xargs -r docker stop
        docker ps -a | grep "$IMAGE_NAME" | awk '{print $1}' | xargs -r docker rm
        ((cleaned++))
    fi
    
    # Remove image
    if docker image inspect "$full_image" &> /dev/null; then
        info "Removing image: $full_image"
        docker rmi "$full_image"
        ((cleaned++))
    fi
    
    # Prune build cache
    if [[ "$NO_CACHE" == true ]]; then
        info "Pruning build cache..."
        docker builder prune -f
        ((cleaned++))
    fi
    
    if [[ $cleaned -eq 0 ]]; then
        info "Nothing to clean"
    else
        success "✓ Cleaned $cleaned item(s)"
    fi
}

################################################################################
# Main Entry Point
################################################################################

main() {
    local start_time
    start_time=$(date +%s)
    
    print_banner "SynOS Docker Build Tool"
    
    # Check Docker availability
    check_docker
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    case "$MODE" in
        build)
            info "Mode: Container Build"
            info "Output: $OUTPUT_DIR"
            echo ""
            
            if build_in_container; then
                local end_time
                end_time=$(date +%s)
                
                echo ""
                success "Docker build completed"
                info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            else
                exit 1
            fi
            ;;
            
        shell)
            open_shell
            ;;
            
        clean)
            clean_docker
            
            local end_time
            end_time=$(date +%s)
            
            echo ""
            success "Cleanup complete"
            info "Time elapsed: $(elapsed_time "$start_time" "$end_time")"
            ;;
            
        *)
            error "Invalid mode: $MODE"
            exit 1
            ;;
    esac
    
    return 0
}

################################################################################
# Execute
################################################################################

main "$@"
