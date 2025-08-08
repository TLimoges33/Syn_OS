# Syn_OS Unified Build System
.PHONY: help build test clean start stop restart logs status install-deps

# Default target
help:
	@echo "Syn_OS Build System"
	@echo "==================="
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build all services"
	@echo "  test           - Run all tests"
	@echo "  clean          - Clean build artifacts"
	@echo "  start          - Start all services with Docker Compose"
	@echo "  stop           - Stop all services"
	@echo "  restart        - Restart all services"
	@echo "  logs           - Show logs from all services"
	@echo "  status         - Show status of all services"
	@echo "  install-deps   - Install development dependencies"
	@echo "  orchestrator   - Build orchestrator service only"
	@echo "  consciousness  - Build consciousness system only"
	@echo "  dev-setup      - Set up development environment"
	@echo "  integration    - Run integration tests"

# Install development dependencies
install-deps:
	@echo "Installing Go dependencies..."
	cd services/orchestrator && go mod download
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-nats.txt
	@echo "Installing NATS CLI..."
	curl -sf https://binaries.nats.dev/nats-io/natscli/nats@latest | sh
	sudo mv nats /usr/local/bin/

# Build all services
build: orchestrator consciousness

# Build orchestrator service
orchestrator:
	@echo "Building orchestrator service..."
	cd services/orchestrator && go build -o bin/orchestrator ./cmd/orchestrator
	@echo "Orchestrator built successfully"

# Build consciousness system
consciousness:
	@echo "Building consciousness system..."
	python -m py_compile src/consciousness_v2/main.py
	@echo "Consciousness system validated"

# Run tests
test: test-orchestrator test-consciousness

test-orchestrator:
	@echo "Running orchestrator tests..."
	cd services/orchestrator && go test ./...

test-consciousness:
	@echo "Running consciousness tests..."
	python -m pytest src/consciousness_v2/tests/ -v

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cd services/orchestrator && rm -rf bin/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	docker system prune -f

# Development environment setup
dev-setup: install-deps
	@echo "Setting up development environment..."
	@echo "Creating necessary directories..."
	mkdir -p logs data/postgres data/redis data/nats
	@echo "Setting up Git hooks..."
	cp scripts/pre-commit .git/hooks/pre-commit 2>/dev/null || echo "No pre-commit hook found"
	chmod +x .git/hooks/pre-commit 2>/dev/null || true
	@echo "Development environment ready"

# Docker Compose operations
start:
	@echo "Starting Syn_OS services..."
	docker-compose up -d
	@echo "Services started. Use 'make logs' to view logs or 'make status' to check status"

stop:
	@echo "Stopping Syn_OS services..."
	docker-compose down

restart: stop start

logs:
	docker-compose logs -f

status:
	@echo "Service Status:"
	@echo "==============="
	docker-compose ps

# Integration tests
integration:
	@echo "Running integration tests..."
	@echo "Starting test environment..."
	docker-compose -f docker-compose.test.yml up -d
	@echo "Waiting for services to be ready..."
	sleep 30
	@echo "Running integration test suite..."
	python -m pytest tests/integration/ -v
	@echo "Cleaning up test environment..."
	docker-compose -f docker-compose.test.yml down

# Development shortcuts
dev-orchestrator:
	@echo "Starting orchestrator in development mode..."
	cd services/orchestrator && \
	ENV=development \
	NATS_URL=nats://localhost:4222 \
	POSTGRES_HOST=localhost \
	REDIS_HOST=localhost \
	go run ./cmd/orchestrator

dev-consciousness:
	@echo "Starting consciousness system in development mode..."
	NATS_URL=nats://localhost:4222 \
	ORCHESTRATOR_URL=http://localhost:8080 \
	python -m src.consciousness_v2.main

# Database operations
db-migrate:
	@echo "Running database migrations..."
	cd services/orchestrator && go run ./cmd/migrate

db-reset:
	@echo "Resetting database..."
	docker-compose exec postgres psql -U syn_os_user -d syn_os -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	$(MAKE) db-migrate

# Monitoring and debugging
monitor:
	@echo "Opening monitoring dashboard..."
	@echo "NATS Monitor: http://localhost:8222"
	@echo "Orchestrator API: http://localhost:8080"
	@echo "Consciousness Health: http://localhost:8081/health"

debug-nats:
	@echo "NATS debugging information:"
	nats server info
	nats stream list
	nats consumer list

debug-logs:
	@echo "Recent logs from all services:"
	docker-compose logs --tail=50

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build
	@echo "Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production deployment complete"

# Backup and restore
backup:
	@echo "Creating system backup..."
	mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	docker-compose exec postgres pg_dump -U syn_os_user syn_os > backups/$(shell date +%Y%m%d_%H%M%S)/postgres.sql
	docker-compose exec redis redis-cli --rdb backups/$(shell date +%Y%m%d_%H%M%S)/redis.rdb
	@echo "Backup created in backups/$(shell date +%Y%m%d_%H%M%S)/"

# Security and maintenance
security-scan:
	@echo "Running security scans..."
	docker run --rm -v $(PWD):/app securecodewarrior/docker-security-scan /app
	python -m safety check -r requirements.txt

update-deps:
	@echo "Updating dependencies..."
	cd services/orchestrator && go get -u ./...
	pip install --upgrade -r requirements.txt

# Documentation
docs:
	@echo "Generating documentation..."
	cd docs && make html
	@echo "Documentation available at docs/_build/html/index.html"

# Quick health check
health:
	@echo "System Health Check:"
	@echo "==================="
	@curl -s http://localhost:8080/health | jq . || echo "Orchestrator: DOWN"
	@curl -s http://localhost:8081/health | jq . || echo "Consciousness: DOWN"
	@curl -s http://localhost:8222/healthz || echo "NATS: DOWN"
