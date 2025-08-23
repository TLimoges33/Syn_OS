#!/bin/bash

# SynapticOS Phase 2 Podman Launch Script
# Uses Podman instead of Docker for container management

set -e

echo "🧠 SynapticOS Phase 2: Neural Darwinism (Podman Mode)"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Set Docker host for Podman compatibility
export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock

# Check if Podman is running
if ! podman info >/dev/null 2>&1; then
    print_error "Podman is not accessible. Trying to start Podman socket..."
    systemctl --user start podman.socket
    sleep 2
fi

# Start Podman socket if not running
if ! podman info >/dev/null 2>&1; then
    print_status "Starting Podman socket..."
    systemctl --user enable --now podman.socket
    sleep 3
fi

# Verify Podman is working
if ! podman info >/dev/null 2>&1; then
    print_error "Could not start Podman. Please check your installation."
    exit 1
fi

print_success "Podman is running successfully"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/consciousness_state
mkdir -p data/education
mkdir -p data/vector_storage
mkdir -p logs/security
mkdir -p logs/consciousness
mkdir -p logs/education

# Set proper permissions
chmod 755 data/consciousness_state
chmod 755 data/education
chmod 755 data/vector_storage
chmod 755 logs/security
chmod 755 logs/consciousness
chmod 755 logs/education

print_success "Directories created successfully"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file with default values..."
    cat > .env << EOF
# SynapticOS Environment Configuration
POSTGRES_DB=syn_os
POSTGRES_USER=syn_os_user
POSTGRES_PASSWORD=secure_password_change_me
POSTGRES_SSL_MODE=require

# Redis
REDIS_PASSWORD=redis_password_change_me

# JWT and Encryption
JWT_SECRET_KEY=jwt_secret_key_change_me_in_production
ENCRYPTION_KEY=encryption_key_32_characters_long
CONSCIOUSNESS_ENCRYPTION_KEY=consciousness_encryption_key_32_chars
INTERNAL_API_KEY=internal_api_key_change_me
SIGNING_KEY=signing_key_change_me

# AI API Keys (Optional - add your keys)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Local AI Services
LM_STUDIO_URL=http://localhost:1234
OLLAMA_URL=http://localhost:11434

# Service URLs
NATS_URL=nats://nats:4222
ORCHESTRATOR_URL=http://orchestrator:8080
CONSCIOUSNESS_URL=http://consciousness:8081

# Logging
LOG_LEVEL=INFO

# Consciousness System
CONSCIOUSNESS_MODE=production
EOF
    print_warning "Created .env file with default values. Please update with your actual API keys!"
else
    print_success ".env file already exists"
fi

# Use podman-compose instead of docker-compose
COMPOSE_CMD="podman-compose"

# Check if podman-compose exists, fallback to docker-compose with Podman socket
if ! command -v podman-compose >/dev/null 2>&1; then
    print_warning "podman-compose not found, using docker-compose with Podman backend"
    COMPOSE_CMD="docker-compose"
fi

print_status "Using compose command: $COMPOSE_CMD"

# Pull latest images
print_status "Pulling latest container images..."
$COMPOSE_CMD pull || print_warning "Some images may need to be built"

# Build services
print_header "Building SynapticOS Services..."
$COMPOSE_CMD build

# Start infrastructure services first
print_header "Starting Infrastructure Services..."
$COMPOSE_CMD up -d nats postgres redis vector-db

# Wait for infrastructure to be ready
print_status "Waiting for infrastructure services to be ready..."
sleep 15

# Check if services are running
print_status "Checking service status..."
$COMPOSE_CMD ps

# Start consciousness services
print_header "Starting Consciousness & AI Services..."
$COMPOSE_CMD up -d consciousness-ai-bridge || print_warning "Building consciousness-ai-bridge..."

# Wait for consciousness bridge
print_status "Waiting for consciousness bridge to be ready..."
sleep 10

# Start educational services
print_header "Starting Educational Platform Services..."
$COMPOSE_CMD up -d educational-platform education-gui || print_warning "Building educational services..."

# Wait for educational services
print_status "Waiting for educational services to be ready..."
sleep 10

# Start monitoring and dashboard services
print_header "Starting Monitoring & Dashboard Services..."
$COMPOSE_CMD up -d consciousness-dashboard || print_warning "Building dashboard..."

# Start remaining services (optional)
print_header "Starting Additional Services..."
$COMPOSE_CMD up -d orchestrator consciousness security-dashboard learning-hub web-dashboard || print_warning "Some services may not start"

# Final status check
print_header "Final Service Status Check..."
sleep 5
$COMPOSE_CMD ps

# Display service status
print_header "Service Status Summary:"
echo ""
echo -e "${CYAN}Core Infrastructure:${NC}"
echo "  🗃️  NATS Message Bus     : http://localhost:8222"
echo "  🗄️  PostgreSQL Database : localhost:5432"
echo "  📦  Redis Cache         : localhost:6379"
echo "  🔍  Vector Database     : http://localhost:6333"

echo ""
echo -e "${CYAN}SynapticOS Phase 2:${NC}"
echo "  🧠  Consciousness Bridge : http://localhost:8082"
echo "  📚  Educational Platform: http://localhost:8084"
echo "  🎓  Education GUI       : http://localhost:8001"
echo "  📊  Consciousness Dashboard: http://localhost:8000"

echo ""
print_header "Phase 2 Features:"
echo "  🧬  Neural Darwinism Engine"
echo "  🎯  Gamified Learning System"
echo "  🏆  Achievement & Badge System"
echo "  📊  Real-time Consciousness Monitoring"

echo ""
print_success "SynapticOS Phase 2 launched with Podman!"
echo ""
print_header "Quick Access:"
echo "  Consciousness Dashboard: http://localhost:8000"
echo "  Educational Platform:    http://localhost:8001"
echo ""
print_header "Development Commands:"
echo "  View logs:     $COMPOSE_CMD logs -f [service_name]"
echo "  Stop all:      $COMPOSE_CMD down"
echo "  Restart:       $COMPOSE_CMD restart [service_name]"
echo "  Status:        $COMPOSE_CMD ps"

echo ""
print_warning "Note: Using Podman as Docker replacement. Some features may need adjustment."
