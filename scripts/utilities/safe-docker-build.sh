#!/bin/bash
################################################################################
# SynOS Safe Build Wrapper
#
# Purpose: Safely execute SynOS build in isolated Docker container
# Author: SynOS Team
# Version: 1.0
# Date: 2025-10-25
#
# This script ensures builds never corrupt the host environment by running
# everything inside an isolated Docker container.
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/docker/build"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              SynOS Safe Build Wrapper (Docker)                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo ""
    echo "Docker is required for safe isolated builds."
    echo ""
    echo "Install Docker:"
    echo "  # For Parrot OS / Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y docker.io docker-compose"
    echo "  sudo systemctl enable --now docker"
    echo "  sudo usermod -aG docker $USER"
    echo "  # Then log out and back in"
    echo ""
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo ""
    echo "Start Docker:"
    echo "  sudo systemctl start docker"
    echo ""
    exit 1
fi

# Check if user is in docker group
if ! groups | grep -q docker; then
    echo -e "${YELLOW}⚠ You are not in the docker group${NC}"
    echo ""
    echo "To avoid using sudo with Docker:"
    echo "  sudo usermod -aG docker $USER"
    echo "  # Then log out and back in"
    echo ""
    echo "For now, you'll need to use sudo."
    echo ""
fi

# Verify /dev health on host (just in case)
DEV_COUNT=$(ls /dev/ | wc -l)
if [ "$DEV_COUNT" -lt 50 ]; then
    echo -e "${RED}✗ Host /dev filesystem appears broken ($DEV_COUNT entries)${NC}"
    echo ""
    echo "Fix host environment first:"
    echo "  sudo reboot"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Host environment check passed"
echo -e "${GREEN}✓${NC} Docker available"
echo ""

# Build Docker image if it doesn't exist or if --rebuild flag is passed
REBUILD_IMAGE=false
if [ "$1" = "--rebuild-image" ]; then
    REBUILD_IMAGE=true
    shift
fi

if [ "$REBUILD_IMAGE" = true ] || ! docker images synos-builder:latest -q | grep -q .; then
    echo -e "${BLUE}→${NC} Building Docker image (this may take a few minutes)..."
    cd "$DOCKER_DIR"
    docker build \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
        -t synos-builder:latest \
        -f Dockerfile \
        ..
    echo -e "${GREEN}✓${NC} Docker image built successfully"
    echo ""
fi

# Show build configuration
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    BUILD CONFIGURATION                               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo -e "  Environment:      Docker Container (isolated)"
echo -e "  Image:            synos-builder:latest"
echo -e "  Project Root:     $PROJECT_ROOT"
echo -e "  Build Args:       $@"
echo -e "  Host /dev:        Protected (not mounted)"
echo ""

# Parse arguments to determine build mode
BUILD_MODE="interactive"
if [ "$1" = "--auto" ]; then
    BUILD_MODE="automatic"
    shift
fi

if [ "$BUILD_MODE" = "interactive" ]; then
    echo -e "${YELLOW}ℹ${NC} Running in INTERACTIVE mode"
    echo ""
    echo "You will get a shell inside the container."
    echo "Run the build manually with:"
    echo "  sudo ./scripts/build-full-distribution.sh --clean --fresh"
    echo ""
    echo "To exit container: type 'exit' or press Ctrl+D"
    echo ""
    read -p "Press Enter to continue..."
    echo ""

    # Run container interactively
    docker run --rm -it \
        --privileged \
        --hostname synos-builder \
        -v "$PROJECT_ROOT:/build:rw" \
        -e BUILD_ENV=docker \
        -e SYNOS_VERSION=2.4.2 \
        --name synos-build-interactive \
        synos-builder:latest \
        /bin/bash

else
    echo -e "${YELLOW}ℹ${NC} Running in AUTOMATIC mode"
    echo ""
    echo "Build will run automatically inside container..."
    echo ""

    # Run container with automatic build
    docker run --rm \
        --privileged \
        --hostname synos-builder \
        -v "$PROJECT_ROOT:/build:rw" \
        -e BUILD_ENV=docker \
        -e SYNOS_VERSION=2.4.2 \
        --name synos-build-auto \
        synos-builder:latest \
        /bin/bash -c "cd /build && sudo ./scripts/build-full-distribution.sh $@"

    BUILD_EXIT_CODE=$?

    if [ $BUILD_EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                    BUILD SUCCESSFUL!                                 ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "ISO files are in: $PROJECT_ROOT/build/full-distribution/"
        echo ""
    else
        echo ""
        echo -e "${RED}╔══════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    BUILD FAILED                                      ║${NC}"
        echo -e "${RED}╚══════════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Check logs in: $PROJECT_ROOT/build/full-distribution/logs/"
        echo ""
        exit $BUILD_EXIT_CODE
    fi
fi

# Verify host /dev still healthy after build
DEV_COUNT_AFTER=$(ls /dev/ | wc -l)
if [ "$DEV_COUNT_AFTER" -lt 50 ]; then
    echo -e "${RED}⚠ WARNING: Host /dev appears corrupted after build!${NC}"
    echo "  This should NEVER happen with Docker isolation."
    echo "  Please report this as a critical bug."
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Host environment still healthy (${DEV_COUNT_AFTER} /dev entries)"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Safe build complete! Your host environment was never at risk.${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════════════════${NC}"
