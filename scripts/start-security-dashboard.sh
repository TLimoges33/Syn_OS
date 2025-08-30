#!/bin/bash

# Syn_OS Security Dashboard Startup Script
# Starts the secure 10/10 security dashboard with all components

set -e

echo "🛡️  Starting Syn_OS Security Dashboard..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "📦 Running in Docker container"
    DOCKER_MODE=true
else
    echo "🖥️  Running in local development mode"
    DOCKER_MODE=false
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export SECURITY_DASHBOARD_PORT=${SECURITY_DASHBOARD_PORT:-8083}
export NATS_URL=${NATS_URL:-nats://localhost:4222}
export ORCHESTRATOR_URL=${ORCHESTRATOR_URL:-http://localhost:8080}
export CONSCIOUSNESS_URL=${CONSCIOUSNESS_URL:-http://localhost:8081}

# Create necessary directories
mkdir -p logs/security
mkdir -p logs/security/hsm
mkdir -p logs/security/zero_trust
mkdir -p logs/security/quantum
mkdir -p logs/security/consciousness

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "📝 Please edit .env file with your actual configuration"
fi

# Install Python dependencies if not in Docker
if [ "$DOCKER_MODE" = false ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r applications/security_dashboard/requirements.txt
fi

# Check if security backend is running
echo "🔍 Checking security backend services..."

check_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service_name at $service_url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$service_url/health" > /dev/null 2>&1; then
            echo "✅ $service_name is running"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  $service_name is not responding, continuing anyway..."
    return 1
}

# Check services (non-blocking)
check_service "Orchestrator" "$ORCHESTRATOR_URL" || true
check_service "Consciousness" "$CONSCIOUSNESS_URL" || true

# Check NATS connection
echo "🔍 Checking NATS connection..."
if command -v nats &> /dev/null; then
    if nats server check --server="$NATS_URL" &> /dev/null; then
        echo "✅ NATS is running"
    else
        echo "⚠️  NATS is not responding, continuing anyway..."
    fi
else
    echo "⚠️  NATS CLI not available, skipping check"
fi

# Validate security configuration
echo "🔐 Validating security configuration..."
python3 -c "
import sys
sys.path.append('src')
try:
    from security.config_manager import validate_system_security
    if validate_system_security():
        print('✅ Security configuration is valid')
    else:
        print('⚠️  Security configuration has issues, check logs')
except Exception as e:
    print(f'⚠️  Could not validate security config: {e}')
"

# Start the security dashboard
echo "🚀 Starting Security Dashboard on port $SECURITY_DASHBOARD_PORT..."

cd applications/security_dashboard

if [ "$DOCKER_MODE" = true ]; then
    # In Docker, run directly
    exec python3 main.py
else
    # In development, use Python with proper error handling
    python3 main.py 2>&1 | tee ../../logs/security/dashboard.log
fi