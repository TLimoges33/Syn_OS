#!/bin/bash

# SynapticOS Neural Darwinism Launch Script (Simplified)
# Launches only the core Neural Darwinism and Educational Platform services

set -e

echo "🧬 SynapticOS Neural Darwinism System"
echo "===================================="

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

# Check container runtime
if command -v podman >/dev/null 2>&1; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    print_success "Using Podman container runtime"
elif command -v docker >/dev/null 2>&1; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    print_success "Using Docker container runtime"
else
    print_error "Neither Docker nor Podman found. Please install one of them."
    exit 1
fi

# Check if compose command exists
if ! command -v $COMPOSE_CMD >/dev/null 2>&1; then
    print_error "$COMPOSE_CMD not found. Please install it."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/consciousness_state
mkdir -p data/education
mkdir -p data/vector_storage
mkdir -p logs

print_success "Directories created successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# SynapticOS Neural Darwinism Environment
POSTGRES_DB=synapticos
POSTGRES_USER=synos_user
POSTGRES_PASSWORD=secure_password_123

# AI API Keys (Optional - add your keys)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Local AI Services
LM_STUDIO_URL=http://localhost:1234
OLLAMA_URL=http://localhost:11434
EOF
    print_warning "Created .env file. Update with your actual API keys for full functionality!"
else
    print_success ".env file already exists"
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
$COMPOSE_CMD -f docker-compose-neural.yml down --remove-orphans 2>/dev/null || true

# Pull base images
print_header "Pulling Base Images..."
$CONTAINER_CMD pull docker.io/postgres:15-alpine
$CONTAINER_CMD pull docker.io/redis:7-alpine
$CONTAINER_CMD pull docker.io/nats:2.10-alpine
$CONTAINER_CMD pull docker.io/qdrant/qdrant:latest

# Build our services
print_header "Building Neural Darwinism Services..."
$COMPOSE_CMD -f docker-compose-neural.yml build

# Start infrastructure services first
print_header "Starting Infrastructure Services..."
$COMPOSE_CMD -f docker-compose-neural.yml up -d nats postgres redis vector-db

# Wait for infrastructure
print_status "Waiting for infrastructure services to be ready..."
sleep 15

# Check infrastructure health
print_status "Checking infrastructure health..."
for i in {1..30}; do
    if $CONTAINER_CMD exec synapticos_postgres pg_isready -U synos_user -d synapticos >/dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    elif [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    sleep 2
done

for i in {1..30}; do
    if $CONTAINER_CMD exec synapticos_redis redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is ready"
        break
    elif [ $i -eq 30 ]; then
        print_error "Redis failed to start"
        exit 1
    fi
    sleep 2
done

# Start consciousness services
print_header "Starting Neural Darwinism Services..."
$COMPOSE_CMD -f docker-compose-neural.yml up -d consciousness-ai-bridge

# Wait for consciousness bridge
print_status "Waiting for consciousness bridge to initialize..."
sleep 20

# Start educational services
print_header "Starting Educational Platform..."
$COMPOSE_CMD -f docker-compose-neural.yml up -d educational-platform education-gui

# Start dashboard
print_header "Starting Consciousness Dashboard..."
$COMPOSE_CMD -f docker-compose-neural.yml up -d consciousness-dashboard

# Final wait
print_status "Waiting for all services to stabilize..."
sleep 15

# Display service status
print_header "Neural Darwinism System Status:"
echo ""
echo -e "${CYAN}Core Infrastructure:${NC}"
echo "  🗃️  NATS Message Bus     : http://localhost:8222"
echo "  🗄️  PostgreSQL Database : localhost:5432"
echo "  📦  Redis Cache         : localhost:6379"
echo "  🔍  Vector Database     : http://localhost:6333"

echo ""
echo -e "${CYAN}Neural Darwinism Platform:${NC}"
echo "  🧠  Consciousness Bridge : http://localhost:8082"
echo "  📚  Educational Platform: http://localhost:8084"
echo "  🎓  Education GUI       : http://localhost:8001"
echo "  📊  Consciousness Dashboard: http://localhost:8000"

echo ""
print_header "Features Available:"
echo "  🧬  Neural Darwinism Evolution Engine"
echo "  🎯  Gamified Learning with XP/Achievements"
echo "  📊  Real-time Consciousness Monitoring"
echo "  🌐  Multi-platform Integration"
echo "  🔄  Consciousness-Learning Correlation"

echo ""
print_success "Neural Darwinism system launched successfully!"
echo ""
print_header "Quick Start:"
echo "1. Open Consciousness Dashboard: http://localhost:8000"
echo "2. Access Educational Platform: http://localhost:8001"
echo "3. Start learning to see Neural Darwinism in action!"

echo ""
print_header "Useful Commands:"
echo "  View logs:     $COMPOSE_CMD -f docker-compose-neural.yml logs -f [service]"
echo "  Stop system:   $COMPOSE_CMD -f docker-compose-neural.yml down"
echo "  Restart:       $COMPOSE_CMD -f docker-compose-neural.yml restart [service]"

# Health check
print_status "Performing final health check..."
services_ready=0
for service in consciousness-ai-bridge educational-platform education-gui consciousness-dashboard; do
    container_name="synapticos_$(echo $service | tr '-' '_')"
    if $CONTAINER_CMD ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*Up"; then
        print_success "$service is running"
        ((services_ready++))
    else
        print_warning "$service may not be ready yet"
    fi
done

echo ""
if [ $services_ready -eq 4 ]; then
    print_success "🎉 All Neural Darwinism services are running!"
    print_header "🧠 Ready to evolve consciousness through learning! 🧬"
else
    print_warning "Some services may still be starting. Check logs if needed."
fi
