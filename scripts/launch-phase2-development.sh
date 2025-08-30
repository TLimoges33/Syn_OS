#!/bin/bash

# SynapticOS Phase 2 Development Launch Script
# Launches consciousness-integrated educational platform with Neural Darwinism

set -e

echo "🧠 SynapticOS Phase 2: Neural Darwinism & Educational Platform"
echo "============================================================"

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

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
    print_warning "Created .env file with default values. Please update with your actual API keys and secure passwords!"
else
    print_success ".env file already exists"
fi

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose pull

# Build services
print_header "Building SynapticOS Services..."
docker-compose build

# Start infrastructure services first
print_header "Starting Infrastructure Services..."
docker-compose up -d nats postgres redis vector-db

# Wait for infrastructure to be ready
print_status "Waiting for infrastructure services to be ready..."
sleep 10

# Check if services are healthy
print_status "Checking service health..."
for service in nats postgres redis; do
    for i in {1..30}; do
        if docker-compose ps $service | grep -q "healthy\|Up"; then
            print_success "$service is ready"
            break
        else
            if [ $i -eq 30 ]; then
                print_error "$service failed to start properly"
                docker-compose logs $service
                exit 1
            fi
            print_status "Waiting for $service... ($i/30)"
            sleep 2
        fi
    done
done

# Start consciousness services
print_header "Starting Consciousness & AI Services..."
docker-compose up -d consciousness-ai-bridge

# Wait for consciousness bridge
print_status "Waiting for consciousness bridge to be ready..."
sleep 15

# Start educational services
print_header "Starting Educational Platform Services..."
docker-compose up -d educational-platform education-gui

# Wait for educational services
print_status "Waiting for educational services to be ready..."
sleep 10

# Start monitoring and dashboard services
print_header "Starting Monitoring & Dashboard Services..."
docker-compose up -d consciousness-dashboard

# Start remaining services
print_header "Starting Additional Services..."
docker-compose up -d orchestrator consciousness security-dashboard learning-hub security-tutor web-dashboard threat-intelligence nats-surveyor

# Final status check
print_header "Final Service Status Check..."
sleep 10

# Display service status
print_header "Service Status Summary:"
echo ""
echo -e "${CYAN}Core Infrastructure:${NC}"
echo "  🗃️  NATS Message Bus     : http://localhost:8222"
echo "  🗄️  PostgreSQL Database : localhost:5432"
echo "  📦  Redis Cache         : localhost:6379"
echo "  🔍  Vector Database     : http://localhost:6333"

echo ""
echo -e "${CYAN}SynapticOS Platform:${NC}"
echo "  🧠  Consciousness Bridge : http://localhost:8082"
echo "  📚  Educational Platform: http://localhost:8084"
echo "  🎓  Education GUI       : http://localhost:8001"
echo "  📊  Consciousness Dashboard: http://localhost:8000"

echo ""
echo -e "${CYAN}Original Services:${NC}"
echo "  🎯  Service Orchestrator: http://localhost:8080"
echo "  🧠  Consciousness Core  : http://localhost:8081"
echo "  🛡️  Security Dashboard : http://localhost:8083"
echo "  📖  Learning Hub       : http://localhost:8084"
echo "  👨‍🏫  Security Tutor     : http://localhost:8085"
echo "  🌐  Web Dashboard      : http://localhost:8086"
echo "  🔍  Threat Intelligence: http://localhost:8087"
echo "  📊  NATS Monitoring    : http://localhost:7777"

echo ""
print_header "Phase 2 Features Enabled:"
echo "  🧬  Neural Darwinism Engine"
echo "  🎯  Gamified Learning System"
echo "  🏆  Achievement & Badge System"
echo "  📊  Real-time Consciousness Monitoring"
echo "  🌐  Multi-platform Integration"
echo "  🔄  Consciousness-Learning Correlation"

echo ""
print_success "SynapticOS Phase 2 launched successfully!"
echo ""
print_header "Quick Start Guide:"
echo "1. Open Consciousness Dashboard: http://localhost:8000"
echo "2. Access Educational Platform: http://localhost:8001"
echo "3. Monitor consciousness evolution in real-time"
echo "4. Start learning sessions to see Neural Darwinism in action"
echo "5. Track achievements and consciousness correlation"

echo ""
print_header "Development Commands:"
echo "  View logs:     docker-compose logs -f [service_name]"
echo "  Stop all:      docker-compose down"
echo "  Restart:       docker-compose restart [service_name]"
echo "  Health check:  curl http://localhost:8000/health"

echo ""
print_warning "Note: Update .env file with your actual API keys for full AI functionality"

# Optional: Open services in browser (uncomment if desired)
# print_status "Opening services in browser..."
# sleep 3
# xdg-open http://localhost:8000 >/dev/null 2>&1 || open http://localhost:8000 >/dev/null 2>&1 || true
# xdg-open http://localhost:8001 >/dev/null 2>&1 || open http://localhost:8001 >/dev/null 2>&1 || true
