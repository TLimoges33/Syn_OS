#!/bin/bash
# Environment Validation Script for Syn_OS
# Validates NATS integration and all required environment variables

set -e

# Mode toggles (set CORE_ONLY=1 to validate only core infra: nats/postgres/redis/orchestrator)
CORE_ONLY=${CORE_ONLY:-${VALIDATOR_CORE_ONLY:-0}}

echo "🔍 Validating Syn_OS Environment Configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please copy .env.example to .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"

# Source environment variables
source .env

# Required variables for NATS integration
REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "JWT_SECRET_KEY"
    "ENCRYPTION_KEY"
    "INTERNAL_API_KEY"
    "NATS_URL"
    "CONSCIOUSNESS_ENCRYPTION_KEY"
)

# Check required variables
echo -e "${BLUE}🔍 Checking required environment variables...${NC}"
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required variable $var is not set${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ $var is set${NC}"
    fi
done

# Validate JWT secret key length
if [ ${#JWT_SECRET_KEY} -lt 32 ]; then
    echo -e "${RED}❌ JWT_SECRET_KEY must be at least 32 characters${NC}"
    exit 1
fi

# Validate encryption key length
if [ ${#ENCRYPTION_KEY} -lt 32 ]; then
    echo -e "${RED}❌ ENCRYPTION_KEY must be at least 32 characters${NC}"
    exit 1
fi

# Validate consciousness encryption key length
if [ ${#CONSCIOUSNESS_ENCRYPTION_KEY} -lt 32 ]; then
    echo -e "${RED}❌ CONSCIOUSNESS_ENCRYPTION_KEY must be at least 32 characters${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All environment variables are valid${NC}"

# Validate NATS configuration
echo -e "${BLUE}🔍 Validating NATS configuration...${NC}"

# Check NATS URL format
if [[ ! $NATS_URL =~ ^nats://.*:[0-9]+$ ]]; then
    echo -e "${RED}❌ NATS_URL format is invalid. Expected format: nats://host:port${NC}"
    exit 1
fi

echo -e "${GREEN}✅ NATS URL format is valid${NC}"

# Check required NATS variables
NATS_VARS=(
    "NATS_CLUSTER_ID"
    "NATS_CLIENT_ID"
    "NATS_MAX_RECONNECT"
)

for var in "${NATS_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${YELLOW}⚠️  NATS variable $var is not set, using defaults${NC}"
    else
        echo -e "${GREEN}✅ $var is set${NC}"
    fi
done

# Test database connection (if PostgreSQL is running)
echo -e "${BLUE}🔍 Testing database connection...${NC}"
if command -v psql &> /dev/null; then
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Database connection failed (may not be running yet)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  psql not available, skipping database test${NC}"
fi

# Test Redis connection (if Redis is running)
echo -e "${BLUE}🔍 Testing Redis connection...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis connection failed (may not be running yet)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  redis-cli not available, skipping Redis test${NC}"
fi

# Test NATS connection (if NATS is running)
echo -e "${BLUE}🔍 Testing NATS connection...${NC}"
if command -v nats &> /dev/null; then
    if timeout 5 nats pub test.connection "test" --server=$NATS_URL &> /dev/null; then
        echo -e "${GREEN}✅ NATS connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️  NATS connection failed (may not be running yet)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  nats CLI not available, skipping NATS test${NC}"
fi

echo -e "${BLUE}🔍 Validating Docker requirements...${NC}"

warn_or_fail_missing() {
    local label="$1"
    if [ "$CORE_ONLY" = "1" ]; then
        echo -e "${YELLOW}⚠️  $label is missing (CORE_ONLY mode)${NC}"
    else
        echo -e "${RED}❌ $label is missing${NC}"
        exit 1
    fi
}

# Check if required Dockerfiles exist (support both root and docker/ paths)
if [ -f "docker/Dockerfile.consciousness" ] || [ -f "Dockerfile.consciousness" ]; then
    echo -e "${GREEN}✅ Dockerfile.consciousness exists${NC}"
else
    warn_or_fail_missing "Dockerfile.consciousness"
fi

if [ -f "services/orchestrator/Dockerfile" ] || [ -f "docker/services/orchestrator/Dockerfile" ]; then
    echo -e "${GREEN}✅ services/orchestrator/Dockerfile exists${NC}"
else
    warn_or_fail_missing "services/orchestrator/Dockerfile"
fi

if [ -f "applications/security_dashboard/Dockerfile" ] || [ -f "docker/applications/security_dashboard/Dockerfile" ]; then
    echo -e "${GREEN}✅ applications/security_dashboard/Dockerfile exists${NC}"
else
    warn_or_fail_missing "applications/security_dashboard/Dockerfile"
fi

# Check if requirements files exist (fix path for consciousness requirements)
if [ -f "config/dependencies/requirements-consciousness.txt" ] || [ -f "requirements-consciousness.txt" ]; then
    echo -e "${GREEN}✅ requirements-consciousness.txt exists${NC}"
else
    warn_or_fail_missing "requirements-consciousness.txt"
fi

if [ -f "config/dependencies/requirements-nats.txt" ] || [ -f "requirements-nats.txt" ]; then
    echo -e "${GREEN}✅ config/dependencies/requirements-nats.txt exists${NC}"
else
    warn_or_fail_missing "config/dependencies/requirements-nats.txt"
fi

if [ -f "applications/security_dashboard/requirements.txt" ] || [ -f "docker/applications/security_dashboard/requirements.txt" ]; then
    echo -e "${GREEN}✅ applications/security_dashboard/requirements.txt exists${NC}"
else
    warn_or_fail_missing "applications/security_dashboard/requirements.txt"
fi

# Validate consciousness system configuration
echo -e "${BLUE}🔍 Validating consciousness system configuration...${NC}"

if [ "${CORE_ONLY}" = "1" ]; then
    echo -e "${YELLOW}⚠️  CORE_ONLY: Skipping strict consciousness_v2 checks${NC}"
fi

# Check consciousness source directory
if [ -d "src/consciousness_v2" ]; then
    echo -e "${GREEN}✅ Consciousness v2 source directory exists${NC}"
else
    if [ "$CORE_ONLY" = "1" ]; then
        echo -e "${YELLOW}⚠️  Consciousness v2 source directory is missing (CORE_ONLY mode)${NC}"
    else
        echo -e "${RED}❌ Consciousness v2 source directory is missing${NC}"
        exit 1
    fi
fi

# Check for main consciousness files
CONSCIOUSNESS_FILES=(
    "src/consciousness_v2/main.py"
    "src/consciousness_v2/bridges/nats_bridge.py"
    "src/consciousness_v2/core/consciousness_bus.py"
    "src/consciousness_v2/core/state_manager.py"
    "src/consciousness_v2/core/data_models.py"
)

for file in "${CONSCIOUSNESS_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        if [ "$CORE_ONLY" = "1" ]; then
            echo -e "${YELLOW}⚠️  $file is missing (CORE_ONLY mode)${NC}"
        else
            echo -e "${RED}❌ $file is missing${NC}"
            exit 1
        fi
    fi
done

# Final validation summary
echo -e "${GREEN}🎉 Environment validation completed${NC}"
echo -e "${BLUE}📋 Summary:${NC}"
echo "  - Environment variables: ✅ Valid"
echo "  - NATS configuration: ✅ Valid"
if [ "$CORE_ONLY" = "1" ]; then
    echo "  - Docker requirements: ✅ Core-only"
    echo "  - Consciousness system: ✅ Core-only"
else
    echo "  - Docker requirements: ✅ Valid"
    echo "  - Consciousness system: ✅ Valid"
fi
echo ""
echo -e "${BLUE}🚀 Ready to start NATS integration testing!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Run: docker-compose up -d nats postgres redis"
echo "  2. Run: docker-compose build consciousness orchestrator security-dashboard"
echo "  3. Run: docker-compose up -d"
echo "  4. Test NATS integration with: ./scripts/test-nats-integration.sh"