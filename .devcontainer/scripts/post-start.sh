#!/bin/bash
# Syn_OS Development Environment Post-Start Script
# Runs every time the container is started

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}🔄 Syn_OS Development Environment Startup${NC}"
echo -e "${BLUE}=========================================${NC}"

cd /workspace

log "Checking development environment status..."

# Activate Python virtual environment if it exists
if [ -f /workspace/.venv/bin/activate ]; then
    source /workspace/.venv/bin/activate
    log "Python virtual environment activated"
fi

# Source Rust environment
if [ -f ~/.cargo/env ]; then
    source ~/.cargo/env
    log "Rust environment loaded"
fi

# Source environment variables
if [ -f /workspace/config/local/.env ]; then
    source /workspace/config/local/.env
    log "Environment variables loaded"
fi

log "Starting development services..."

# Function to start service if not running
start_service() {
    local service_name=$1
    local check_command=$2
    local start_command=$3
    
    if eval "$check_command" &>/dev/null; then
        log "$service_name already running"
    else
        log "Starting $service_name..."
        eval "$start_command" &
        sleep 2
        if eval "$check_command" &>/dev/null; then
            success "$service_name started successfully"
        else
            warn "Failed to start $service_name"
        fi
    fi
}

# Start Docker daemon if not running (if we have permissions)
if command -v docker &> /dev/null; then
    if ! docker info &>/dev/null; then
        log "Docker daemon not running, attempting to start..."
        sudo service docker start 2>/dev/null || warn "Could not start Docker daemon"
    else
        log "Docker daemon is running"
    fi
fi

# Check if we need to start development services
if [ -f docker-compose.yml ]; then
    log "Found docker-compose.yml, checking services..."
    
    # Start basic development services
    docker-compose up -d redis nats postgres 2>/dev/null || warn "Some services failed to start"
    
    # Wait a moment for services to initialize
    sleep 3
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        success "Development services started successfully"
    else
        warn "Some development services may not be running properly"
    fi
fi

log "Performing system health checks..."

# Quick health check on critical components
checks_failed=0

# Check Rust
if ! command -v rustc &> /dev/null; then
    error "Rust compiler not available"
    ((checks_failed++))
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python3 not available"
    ((checks_failed++))
fi

# Check Git
if ! command -v git &> /dev/null; then
    error "Git not available"
    ((checks_failed++))
fi

# Check workspace structure
required_dirs=("src" "docs" "tests")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "/workspace/$dir" ]; then
        warn "Required directory $dir not found"
        ((checks_failed++))
    fi
done

log "Updating development tools..."

# Update Rust toolchain (quietly)
if command -v rustup &> /dev/null; then
    rustup update stable &>/dev/null || warn "Failed to update Rust toolchain"
fi

# Update cargo registry
if command -v cargo &> /dev/null; then
    cargo fetch &>/dev/null || warn "Failed to update cargo registry"
fi

log "Setting up workspace permissions..."
# Ensure proper permissions on key directories
chmod -R u+w /workspace/target 2>/dev/null || true
chmod -R u+w /workspace/build 2>/dev/null || true
chmod -R u+w /workspace/logs 2>/dev/null || true

log "Creating session log..."
# Create session log
echo "=== Syn_OS Development Session Started: $(date) ===" >> /workspace/logs/session.log
echo "User: $USER" >> /workspace/logs/session.log
echo "Working Directory: $(pwd)" >> /workspace/logs/session.log
echo "Environment: $SYNAPTICOS_ENV" >> /workspace/logs/session.log
echo "" >> /workspace/logs/session.log

# Log system information
uname -a >> /workspace/logs/session.log
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $2 " total, " $7 " available"}')" >> /workspace/logs/session.log
echo "Disk: $(df -h / | tail -1 | awk '{print $4 " available"}')" >> /workspace/logs/session.log
echo "" >> /workspace/logs/session.log

log "Checking for project updates..."
# Check if there are any git updates (if we're in a git repo)
if [ -d .git ]; then
    git fetch origin &>/dev/null || warn "Could not fetch git updates"
    
    local_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    remote_commit=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null || echo "unknown")
    
    if [ "$local_commit" != "$remote_commit" ] && [ "$remote_commit" != "unknown" ]; then
        warn "Your local branch is behind the remote. Consider running 'git pull'."
        echo "Local:  $local_commit" >> /workspace/logs/session.log
        echo "Remote: $remote_commit" >> /workspace/logs/session.log
    fi
fi

# Performance optimization
log "Optimizing development environment..."

# Set CPU governor to performance if available
if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1 || true
fi

# Increase file watch limits for development
echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf >/dev/null 2>&1 || true
sudo sysctl -p >/dev/null 2>&1 || true

# Final status report
echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Startup Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✓ Environment is ready for development${NC}"
    echo -e "${GREEN}✓ All critical tools available${NC}"
    echo -e "${GREEN}✓ Services started successfully${NC}"
    echo ""
    echo -e "Run ${BLUE}syn-dev health${NC} for a detailed environment check"
    echo -e "Run ${BLUE}syn-welcome${NC} to see the welcome message"
else
    echo -e "${YELLOW}⚠ Environment started with $checks_failed issues${NC}"
    echo -e "Run ${BLUE}healthcheck.sh${NC} for detailed diagnostics"
fi

echo -e "\n${BLUE}Happy coding! 🚀${NC}"
echo ""

# Create a marker file to indicate successful startup
touch /workspace/.devcontainer-started
echo "$(date)" > /workspace/.devcontainer-started
