#!/bin/bash
set -euo pipefail

# Container Build Script for Syn_OS
# Builds all production containers with proper tagging and security scanning

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
REGISTRY="${REGISTRY:-ghcr.io/syn-os}"
TAG="${TAG:-latest}"
PUSH_IMAGES=false
SCAN_IMAGES=true
BUILD_CONTEXT="$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build Syn_OS containers for production deployment

Options:
    -r, --registry URL      Container registry URL (default: ghcr.io/syn-os)
    -t, --tag TAG          Image tag (default: latest)
    -p, --push             Push images to registry after building
    -s, --skip-scan        Skip security scanning of images
    -h, --help             Show this help message

Examples:
    $0                          # Build all images with default settings
    $0 -t v1.2.3 -p            # Build and push with specific tag
    $0 -r my-registry.com -p   # Use custom registry and push

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_IMAGES=true
            shift
            ;;
        -s|--skip-scan)
            SCAN_IMAGES=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    
    if [[ "$SCAN_IMAGES" == true ]]; then
        command -v trivy >/dev/null 2>&1 || missing_tools+=("trivy")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install Trivy: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build individual container
build_container() {
    local component="$1"
    local dockerfile="$2"
    local context="$3"
    local image_name="$REGISTRY/syn-os-$component:$TAG"
    
    log_info "Building $component container..."
    
    if [[ ! -f "$dockerfile" ]]; then
        log_error "Dockerfile not found: $dockerfile"
        return 1
    fi
    
    # Build with build-time variables
    docker build \
        --tag "$image_name" \
        --file "$dockerfile" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --build-arg VERSION="$TAG" \
        --label "org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --label "org.opencontainers.image.version=$TAG" \
        --label "org.opencontainers.image.revision=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --label "org.opencontainers.image.title=syn-os-$component" \
        --label "org.opencontainers.image.description=Syn_OS $component service" \
        --label "org.opencontainers.image.vendor=Syn_OS" \
        "$context"
    
    if [[ $? -eq 0 ]]; then
        log_success "Built $component container: $image_name"
        return 0
    else
        log_error "Failed to build $component container"
        return 1
    fi
}

# Scan container for vulnerabilities
scan_container() {
    local component="$1"
    local image_name="$REGISTRY/syn-os-$component:$TAG"
    
    log_info "Scanning $component container for vulnerabilities..."
    
    # Create scan results directory
    local scan_dir="$PROJECT_ROOT/security/scan-results"
    mkdir -p "$scan_dir"
    
    # Run Trivy scan
    trivy image \
        --exit-code 1 \
        --severity HIGH,CRITICAL \
        --format json \
        --output "$scan_dir/${component}-scan.json" \
        "$image_name"
    
    local scan_result=$?
    
    # Also generate human-readable report
    trivy image \
        --severity HIGH,CRITICAL \
        --format table \
        "$image_name" > "$scan_dir/${component}-scan.txt"
    
    if [[ $scan_result -eq 0 ]]; then
        log_success "✓ $component container passed security scan"
        return 0
    else
        log_error "✗ $component container failed security scan"
        log_error "Review scan results in: $scan_dir/${component}-scan.txt"
        return 1
    fi
}

# Push container to registry
push_container() {
    local component="$1"
    local image_name="$REGISTRY/syn-os-$component:$TAG"
    
    log_info "Pushing $component container to registry..."
    
    docker push "$image_name"
    
    if [[ $? -eq 0 ]]; then
        log_success "Pushed $component container: $image_name"
        return 0
    else
        log_error "Failed to push $component container"
        return 1
    fi
}

# Build all containers
build_all_containers() {
    log_info "Building all Syn_OS containers..."
    
    local components=(
        "orchestrator:$PROJECT_ROOT/src/orchestrator/Dockerfile:$PROJECT_ROOT/src/orchestrator"
        "consciousness:$PROJECT_ROOT/src/consciousness/Dockerfile:$PROJECT_ROOT/src/consciousness"
        "security-dashboard:$PROJECT_ROOT/src/security_dashboard/Dockerfile:$PROJECT_ROOT/src/security_dashboard"
    )
    
    local failed_builds=()
    local failed_scans=()
    local failed_pushes=()
    
    for component_info in "${components[@]}"; do
        IFS=':' read -r component dockerfile context <<< "$component_info"
        
        # Build container
        if build_container "$component" "$dockerfile" "$context"; then
            # Scan if enabled
            if [[ "$SCAN_IMAGES" == true ]]; then
                if ! scan_container "$component"; then
                    failed_scans+=("$component")
                fi
            fi
            
            # Push if enabled and scan passed (or scan disabled)
            if [[ "$PUSH_IMAGES" == true ]] && [[ ! " ${failed_scans[*]} " =~ " $component " ]]; then
                if ! push_container "$component"; then
                    failed_pushes+=("$component")
                fi
            fi
        else
            failed_builds+=("$component")
        fi
    done
    
    # Report results
    echo
    log_info "Build Summary:"
    
    if [[ ${#failed_builds[@]} -eq 0 ]]; then
        log_success "✓ All containers built successfully"
    else
        log_error "✗ Failed to build: ${failed_builds[*]}"
    fi
    
    if [[ "$SCAN_IMAGES" == true ]]; then
        if [[ ${#failed_scans[@]} -eq 0 ]]; then
            log_success "✓ All containers passed security scans"
        else
            log_error "✗ Failed security scans: ${failed_scans[*]}"
        fi
    fi
    
    if [[ "$PUSH_IMAGES" == true ]]; then
        if [[ ${#failed_pushes[@]} -eq 0 ]]; then
            log_success "✓ All containers pushed successfully"
        else
            log_error "✗ Failed to push: ${failed_pushes[*]}"
        fi
    fi
    
    # Exit with error if any failures
    if [[ ${#failed_builds[@]} -gt 0 || ${#failed_scans[@]} -gt 0 || ${#failed_pushes[@]} -gt 0 ]]; then
        return 1
    fi
    
    return 0
}

# Create example Dockerfiles if they don't exist
create_example_dockerfiles() {
    log_info "Creating example Dockerfiles..."
    
    # Orchestrator Dockerfile
    if [[ ! -f "$PROJECT_ROOT/src/orchestrator/Dockerfile" ]]; then
        mkdir -p "$PROJECT_ROOT/src/orchestrator"
        cat > "$PROJECT_ROOT/src/orchestrator/Dockerfile" << 'EOF'
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

# Copy built application
COPY --from=builder --chown=appuser:appgroup /app .
COPY --chown=appuser:appgroup ./src ./src

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node healthcheck.js

EXPOSE 8080

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "src/index.js"]
EOF
        log_info "Created example orchestrator Dockerfile"
    fi
    
    # Consciousness Dockerfile
    if [[ ! -f "$PROJECT_ROOT/src/consciousness/Dockerfile" ]]; then
        mkdir -p "$PROJECT_ROOT/src/consciousness"
        cat > "$PROJECT_ROOT/src/consciousness/Dockerfile" << 'EOF'
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy dependencies
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python healthcheck.py

EXPOSE 8081

ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "-m", "consciousness.main"]
EOF
        log_info "Created example consciousness Dockerfile"
    fi
    
    # Security Dashboard Dockerfile
    if [[ ! -f "$PROJECT_ROOT/src/security_dashboard/Dockerfile" ]]; then
        mkdir -p "$PROJECT_ROOT/src/security_dashboard"
        cat > "$PROJECT_ROOT/src/security_dashboard/Dockerfile" << 'EOF'
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy dependencies
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python healthcheck.py

EXPOSE 8083

ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "-m", "security_dashboard.main"]
EOF
        log_info "Created example security dashboard Dockerfile"
    fi
}

# Main function
main() {
    log_info "Starting Syn_OS container build process..."
    
    check_prerequisites
    create_example_dockerfiles
    
    cd "$PROJECT_ROOT"
    
    if build_all_containers; then
        log_success "🎉 All containers built successfully!"
        echo
        log_info "Built images:"
        docker images --filter "reference=$REGISTRY/syn-os-*:$TAG" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    else
        log_error "Container build process failed"
        exit 1
    fi
}

# Run main function
main "$@"