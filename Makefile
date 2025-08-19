# Syn_OS Production Makefile
# Provides convenient commands for building, testing, and deploying Syn_OS

.PHONY: help build test deploy clean setup monitoring security-scan docker-build k8s-deploy

# Default target
.DEFAULT_GOAL := help

# Variables
ENVIRONMENT ?= production
REGISTRY ?= ghcr.io/syn-os
TAG ?= latest
KUBECONFIG ?= ~/.kube/config

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
NC := \033[0m

# Help target
help: ## Show this help message
	@echo "$(GREEN)Syn_OS Production Build System$(NC)"
	@echo ""
	@echo "$(BLUE)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Variables:$(NC)"
	@echo "  ENVIRONMENT  Target environment (default: production)"
	@echo "  REGISTRY     Container registry (default: ghcr.io/syn-os)"
	@echo "  TAG          Image tag (default: latest)"
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make setup                    # Setup production environment"
	@echo "  make build TAG=v1.2.3        # Build with specific tag"
	@echo "  make deploy ENVIRONMENT=staging  # Deploy to staging"

# Setup commands
setup: ## Setup environment and dependencies
	@echo "$(BLUE)Setting up $(ENVIRONMENT) environment...$(NC)"
	./scripts/environment-setup.sh -e $(ENVIRONMENT)

setup-ssl: ## Setup with SSL certificates
	@echo "$(BLUE)Setting up $(ENVIRONMENT) environment with SSL...$(NC)"
	./scripts/environment-setup.sh -e $(ENVIRONMENT) -s

setup-staging: ## Setup staging environment
	@echo "$(BLUE)Setting up staging environment...$(NC)"
	./scripts/environment-setup.sh -e staging -s

# Build commands
build: ## Build all containers
	@echo "$(BLUE)Building containers...$(NC)"
	./scripts/build-containers.sh -t $(TAG)

build-push: ## Build and push containers to registry
	@echo "$(BLUE)Building and pushing containers...$(NC)"
	./scripts/build-containers.sh -t $(TAG) -r $(REGISTRY) -p

docker-build: build ## Alias for build

# Test commands
test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -f "scripts/run-tests.sh" ]; then \
		./scripts/run-tests.sh; \
	else \
		echo "$(YELLOW)No test script found. Skipping tests.$(NC)"; \
	fi

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml run --rm test-runner

security-scan: ## Run security scans on containers
	@echo "$(BLUE)Running security scans...$(NC)"
	./scripts/build-containers.sh -t $(TAG) --skip-build --scan-only

# Deployment commands
deploy: ## Deploy with Docker Compose
	@echo "$(BLUE)Deploying to $(ENVIRONMENT) with Docker...$(NC)"
	./scripts/deploy-production.sh -t docker -e $(ENVIRONMENT) -T $(TAG)

deploy-k8s: ## Deploy with Kubernetes
	@echo "$(BLUE)Deploying to $(ENVIRONMENT) with Kubernetes...$(NC)"
	./scripts/deploy-production.sh -t kubernetes -e $(ENVIRONMENT) -T $(TAG)

k8s-deploy: deploy-k8s ## Alias for deploy-k8s

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	./scripts/deploy-production.sh -t docker -e staging -T $(TAG)

deploy-force: ## Force deployment without confirmation
	@echo "$(BLUE)Force deploying to $(ENVIRONMENT)...$(NC)"
	./scripts/deploy-production.sh -t docker -e $(ENVIRONMENT) -T $(TAG) -f

# Monitoring commands
monitoring: ## Setup monitoring stack
	@echo "$(BLUE)Setting up monitoring stack...$(NC)"
	./scripts/setup-monitoring.sh

monitoring-start: ## Start monitoring stack only
	@echo "$(BLUE)Starting monitoring stack...$(NC)"
	docker-compose -f deploy/docker-compose.monitoring.yml up -d

monitoring-stop: ## Stop monitoring stack
	@echo "$(BLUE)Stopping monitoring stack...$(NC)"
	docker-compose -f deploy/docker-compose.monitoring.yml down

monitoring-logs: ## Show monitoring logs
	@echo "$(BLUE)Showing monitoring logs...$(NC)"
	docker-compose -f deploy/docker-compose.monitoring.yml logs -f

# Management commands
status: ## Show deployment status
	@echo "$(BLUE)Deployment Status:$(NC)"
	@if docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml ps >/dev/null 2>&1; then \
		docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml ps; \
	else \
		echo "$(YELLOW)Docker services not running$(NC)"; \
	fi
	@echo ""
	@if kubectl get pods -n syn-os-$(ENVIRONMENT) >/dev/null 2>&1; then \
		echo "$(BLUE)Kubernetes Status:$(NC)"; \
		kubectl get pods -n syn-os-$(ENVIRONMENT); \
	fi

logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml logs -f

health: ## Check service health
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -s http://localhost/health || echo "$(RED)Health check failed$(NC)"
	@echo ""

backup: ## Create backup
	@echo "$(BLUE)Creating backup...$(NC)"
	./scripts/backup.sh

restore: ## Restore from backup (requires BACKUP_DIR)
	@echo "$(BLUE)Restoring from backup...$(NC)"
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "$(RED)Error: BACKUP_DIR variable required$(NC)"; \
		echo "Usage: make restore BACKUP_DIR=/path/to/backup"; \
		exit 1; \
	fi
	./scripts/restore.sh $(BACKUP_DIR)

# Cleanup commands
stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml down

clean: ## Clean up containers and volumes
	@echo "$(BLUE)Cleaning up...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml down -v
	docker system prune -f

clean-all: ## Clean everything including images
	@echo "$(BLUE)Cleaning everything...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml down -v --rmi all
	docker system prune -af

# Development commands
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose -f docker-compose.yml up -d

dev-logs: ## Show development logs
	@echo "$(BLUE)Showing development logs...$(NC)"
	docker-compose -f docker-compose.yml logs -f

dev-clean: ## Clean development environment
	@echo "$(BLUE)Cleaning development environment...$(NC)"
	docker-compose -f docker-compose.yml down -v

# Utility commands
shell: ## Open shell in orchestrator container
	@echo "$(BLUE)Opening shell in orchestrator container...$(NC)"
	docker exec -it syn_os_orchestrator_1 /bin/sh

db-shell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	docker exec -it syn_os_postgres_primary psql -U syn_os -d syn_os_$(ENVIRONMENT)

redis-shell: ## Open Redis CLI
	@echo "$(BLUE)Opening Redis CLI...$(NC)"
	docker exec -it syn_os_redis_master redis-cli

update: ## Update containers to latest versions
	@echo "$(BLUE)Updating containers...$(NC)"
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml pull
	docker-compose -f docker-compose.yml -f deploy/docker-compose.production.yml up -d

# Security commands
security-check: ## Run comprehensive security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@if [ -f "scripts/security-audit.sh" ]; then \
		./scripts/security-audit.sh; \
	else \
		echo "$(YELLOW)Security audit script not found$(NC)"; \
	fi

vulnerability-scan: ## Scan for vulnerabilities
	@echo "$(BLUE)Scanning for vulnerabilities...$(NC)"
	./scripts/build-containers.sh --skip-build --scan-only

# CI/CD helpers
ci-build: ## Build for CI/CD pipeline
	@echo "$(BLUE)Building for CI/CD...$(NC)"
	./scripts/build-containers.sh -t $(TAG) -r $(REGISTRY)

ci-test: ## Run tests for CI/CD pipeline
	@echo "$(BLUE)Running CI/CD tests...$(NC)"
	@$(MAKE) test
	@$(MAKE) security-scan

ci-deploy: ## Deploy for CI/CD pipeline
	@echo "$(BLUE)Deploying via CI/CD...$(NC)"
	./scripts/deploy-production.sh -t docker -e $(ENVIRONMENT) -T $(TAG) -f

# Quick commands
quick-deploy: build deploy ## Quick build and deploy
quick-update: update ## Quick update and restart

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not implemented yet$(NC)"

# Validation
validate: ## Validate configuration and deployment
	@echo "$(BLUE)Validating configuration...$(NC)"
	@./scripts/deploy-production.sh -t docker -e $(ENVIRONMENT) -T $(TAG) -n
