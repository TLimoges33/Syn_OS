#!/bin/bash

# SynOS Docker Unification Migration Script
# Migrates from fragmented service Dockerfiles to unified architecture

set -e

echo "🔄 Starting SynOS Docker Unification Migration..."

# Define paths
DOCKER_DIR="/home/diablorain/Syn_OS/docker"
SERVICES_DIR="/home/diablorain/Syn_OS/services"
BACKUP_DIR="$DOCKER_DIR/migration-backup-$(date +%Y%m%d-%H%M%S)"

# Create backup directory
echo "📦 Creating backup of current configuration..."
mkdir -p "$BACKUP_DIR"

# Backup original files
cp "$DOCKER_DIR/docker-compose.yml" "$BACKUP_DIR/docker-compose.yml.backup" 2>/dev/null || true
cp -r "$SERVICES_DIR" "$BACKUP_DIR/services-backup" 2>/dev/null || true

echo "✅ Backup created at: $BACKUP_DIR"

# Validate unified configuration
echo "🔍 Validating unified Docker configuration..."
cd "$DOCKER_DIR"

if docker-compose -f docker-compose.unified.yml config --quiet; then
    echo "✅ Unified configuration validated successfully"
else
    echo "❌ Unified configuration validation failed"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build unified images
echo "🔨 Building unified Docker images..."
docker-compose -f docker-compose.unified.yml build

# Test unified deployment
echo "🧪 Testing unified service deployment..."
docker-compose -f docker-compose.unified.yml up -d postgres redis nats

# Wait for infrastructure
sleep 10

# Start core services
docker-compose -f docker-compose.unified.yml up -d orchestrator

# Wait for orchestrator
sleep 5

# Start consciousness services
docker-compose -f docker-compose.unified.yml up -d \
    consciousness-ai-bridge \
    consciousness-dashboard \
    consciousness-unified \
    context-engine \
    context-intelligence

# Start educational platform
docker-compose -f docker-compose.unified.yml up -d \
    educational-platform \
    educational-gui

echo "⏳ Waiting for services to become healthy..."
sleep 30

# Validate deployment
echo "🔍 Validating unified deployment..."
SERVICES=$(docker-compose -f docker-compose.unified.yml ps --services)
RUNNING_SERVICES=$(docker-compose -f docker-compose.unified.yml ps --filter status=running --services)

echo "📊 Deployment Status:"
echo "   Total services: $(echo "$SERVICES" | wc -l)"
echo "   Running services: $(echo "$RUNNING_SERVICES" | wc -l)"

# Health check
echo "🏥 Performing health checks..."
HEALTH_STATUS=0

for service in orchestrator consciousness-ai-bridge consciousness-dashboard; do
    if docker-compose -f docker-compose.unified.yml exec -T "$service" curl -f http://localhost:8080/health >/dev/null 2>&1; then
        echo "   ✅ $service: healthy"
    else
        echo "   ❌ $service: unhealthy"
        HEALTH_STATUS=1
    fi
done

# Archive old service Dockerfiles
if [ $HEALTH_STATUS -eq 0 ]; then
    echo "🗂️  Archiving individual service Dockerfiles..."
    
    for service_dir in "$SERVICES_DIR"/*; do
        if [ -d "$service_dir" ] && [ -f "$service_dir/Dockerfile" ]; then
            service_name=$(basename "$service_dir")
            echo "   📄 Archiving $service_name/Dockerfile"
            mv "$service_dir/Dockerfile" "$service_dir/Dockerfile.legacy"
        fi
    done
    
    # Update primary docker-compose.yml to point to unified version
    echo "🔄 Updating primary Docker Compose configuration..."
    cp "$DOCKER_DIR/docker-compose.yml" "$DOCKER_DIR/docker-compose.legacy.yml"
    cp "$DOCKER_DIR/docker-compose.unified.yml" "$DOCKER_DIR/docker-compose.yml"
    
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📋 Migration Summary:"
    echo "   • Unified Dockerfile: $DOCKER_DIR/Dockerfile.unified"
    echo "   • Unified Compose: $DOCKER_DIR/docker-compose.yml"
    echo "   • Legacy backup: $BACKUP_DIR"
    echo "   • Legacy compose: $DOCKER_DIR/docker-compose.legacy.yml"
    echo "   • Service Dockerfiles: Renamed to *.legacy"
    echo ""
    echo "🚀 New deployment commands:"
    echo "   Start all services: docker-compose up -d"
    echo "   Start infrastructure: docker-compose up -d postgres redis nats"
    echo "   Start core services: docker-compose up -d orchestrator"
    echo "   Check status: docker-compose ps"
    echo ""
    echo "🔧 Benefits of unified architecture:"
    echo "   • Single build context reduces complexity"
    echo "   • Shared dependency management"
    echo "   • Consistent base images and configurations"
    echo "   • Easier maintenance and updates"
    echo "   • Reduced Docker image size through layer sharing"
    
else
    echo "❌ Health checks failed. Rolling back..."
    docker-compose -f docker-compose.unified.yml down
    
    if [ -f "$BACKUP_DIR/docker-compose.yml.backup" ]; then
        cp "$BACKUP_DIR/docker-compose.yml.backup" "$DOCKER_DIR/docker-compose.yml"
        docker-compose up -d
    fi
    
    echo "🔄 Rollback completed. Check logs for issues."
    exit 1
fi

echo "🎉 SynOS Docker Unification Migration Complete!"
