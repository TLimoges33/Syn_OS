# SynapticOS Consciousness System Deployment Automation Scripts
## Complete Deployment and Operational Automation

### Table of Contents

1. [Deployment Scripts](#deployment-scripts)
2. [Configuration Management Scripts](#configuration-management-scripts)
3. [Monitoring and Health Check Scripts](#monitoring-and-health-check-scripts)
4. [Backup and Recovery Scripts](#backup-and-recovery-scripts)
5. [Operational Procedures](#operational-procedures)
6. [Troubleshooting Automation](#troubleshooting-automation)

- --

## Deployment Scripts

### Main Deployment Script

```bash
#!/bin/bash
## scripts/deploy-consciousness-system.sh
## Complete automated deployment with validation and rollback capabilities

set -euo pipefail

## Configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-development}"
VERSION="${2:-latest}"
NAMESPACE="consciousness-system"
TIMEOUT="600s"

## Colors for output

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

## Logging functions

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

## Validation functions

validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"

    case $ENVIRONMENT in
        development|staging|production)
            log_success "Environment $ENVIRONMENT is valid"
            ;;
        * )
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check required tools
    local required_tools=("kubectl" "helm" "terraform" "ansible" "docker")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done

    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Check Helm repositories
    if ! helm repo list | grep -q "consciousness"; then
        log_warning "Consciousness Helm repository not found, adding..."
        helm repo add consciousness https://charts.synapticos.com
        helm repo update
    fi

    log_success "All prerequisites validated"
}

## Infrastructure deployment

deploy_infrastructure() {
    log_info "Deploying infrastructure for $ENVIRONMENT..."

    cd "$PROJECT_ROOT/infrastructure/environments/$ENVIRONMENT"

    # Initialize Terraform
    terraform init -upgrade

    # Plan infrastructure changes
    terraform plan -out=tfplan

    # Apply infrastructure changes
    if terraform apply tfplan; then
        log_success "Infrastructure deployed successfully"
    else
        log_error "Infrastructure deployment failed"
        exit 1
    fi

    cd "$PROJECT_ROOT"
}

## Application deployment

deploy_application() {
    log_info "Deploying consciousness system application..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Deploy using Helm
    helm upgrade --install consciousness-system \
        "$PROJECT_ROOT/helm/consciousness-system" \
        - -namespace "$NAMESPACE" \
        - -values "$PROJECT_ROOT/helm/consciousness-system/values-$ENVIRONMENT.yaml" \
        - -set global.imageTag="$VERSION" \
        - -wait \
        - -timeout="$TIMEOUT"

    if [ $? -eq 0 ]; then
        log_success "Application deployed successfully"
    else
        log_error "Application deployment failed"
        exit 1
    fi
}

## Health checks

run_health_checks() {
    log_info "Running health checks..."

    # Wait for all deployments to be ready
    local deployments=(
        "consciousness-bus"
        "neural-darwinism-engine"
        "personal-context-engine"
        "security-tutor"
        "lm-studio-integration"
    )

    for deployment in "${deployments[@]}"; do
        log_info "Checking deployment: $deployment"
        kubectl wait --for=condition=available \
            - -timeout=300s \
            deployment/"$deployment" \
            - n "$NAMESPACE"

        if [ $? -eq 0 ]; then
            log_success "$deployment is ready"
        else
            log_error "$deployment failed to become ready"
            return 1
        fi
    done

    # Run smoke tests
    log_info "Running smoke tests..."
    python3 "$PROJECT_ROOT/tests/smoke/test_deployment.py" \
        - -environment="$ENVIRONMENT" \
        - -namespace="$NAMESPACE"

    if [ $? -eq 0 ]; then
        log_success "All health checks passed"
    else
        log_error "Health checks failed"
        return 1
    fi
}

## Rollback function

rollback_deployment() {
    log_warning "Rolling back deployment..."

    # Get previous revision
    local previous_revision=$(helm history consciousness-system -n "$NAMESPACE" --max 2 -o json | jq -r '.[1].revision')

    if [ "$previous_revision" != "null" ]; then
        helm rollback consciousness-system "$previous_revision" -n "$NAMESPACE"
        log_success "Rollback completed to revision $previous_revision"
    else
        log_error "No previous revision found for rollback"
        exit 1
    fi
}

## Main deployment function

main() {
    log_info "Starting deployment of SynapticOS Consciousness System"
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"

    validate_environment
    validate_prerequisites

    # Deploy infrastructure
    deploy_infrastructure

    # Deploy application
    if ! deploy_application; then
        log_error "Application deployment failed"
        exit 1
    fi

    # Run health checks
    if ! run_health_checks; then
        log_error "Health checks failed, initiating rollback"
        rollback_deployment
        exit 1
    fi

    log_success "Deployment completed successfully!"
    log_info "Consciousness system is now running in $ENVIRONMENT environment"

    # Display access information
    echo ""
    log_info "Access Information:"
    kubectl get ingress -n "$NAMESPACE" -o wide
    echo ""
    log_info "To monitor the system:"
    echo "kubectl get pods -n $NAMESPACE"
    echo "kubectl logs -f deployment/consciousness-bus -n $NAMESPACE"
}

## Script execution

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```text

## Configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-development}"
VERSION="${2:-latest}"
NAMESPACE="consciousness-system"
TIMEOUT="600s"

## Colors for output

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

## Logging functions

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

## Validation functions

validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"

    case $ENVIRONMENT in
        development|staging|production)
            log_success "Environment $ENVIRONMENT is valid"
            ;;
        * )
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check required tools
    local required_tools=("kubectl" "helm" "terraform" "ansible" "docker")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
            exit 1
        fi
    done

    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Check Helm repositories
    if ! helm repo list | grep -q "consciousness"; then
        log_warning "Consciousness Helm repository not found, adding..."
        helm repo add consciousness https://charts.synapticos.com
        helm repo update
    fi

    log_success "All prerequisites validated"
}

## Infrastructure deployment

deploy_infrastructure() {
    log_info "Deploying infrastructure for $ENVIRONMENT..."

    cd "$PROJECT_ROOT/infrastructure/environments/$ENVIRONMENT"

    # Initialize Terraform
    terraform init -upgrade

    # Plan infrastructure changes
    terraform plan -out=tfplan

    # Apply infrastructure changes
    if terraform apply tfplan; then
        log_success "Infrastructure deployed successfully"
    else
        log_error "Infrastructure deployment failed"
        exit 1
    fi

    cd "$PROJECT_ROOT"
}

## Application deployment

deploy_application() {
    log_info "Deploying consciousness system application..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Deploy using Helm
    helm upgrade --install consciousness-system \
        "$PROJECT_ROOT/helm/consciousness-system" \
        - -namespace "$NAMESPACE" \
        - -values "$PROJECT_ROOT/helm/consciousness-system/values-$ENVIRONMENT.yaml" \
        - -set global.imageTag="$VERSION" \
        - -wait \
        - -timeout="$TIMEOUT"

    if [ $? -eq 0 ]; then
        log_success "Application deployed successfully"
    else
        log_error "Application deployment failed"
        exit 1
    fi
}

## Health checks

run_health_checks() {
    log_info "Running health checks..."

    # Wait for all deployments to be ready
    local deployments=(
        "consciousness-bus"
        "neural-darwinism-engine"
        "personal-context-engine"
        "security-tutor"
        "lm-studio-integration"
    )

    for deployment in "${deployments[@]}"; do
        log_info "Checking deployment: $deployment"
        kubectl wait --for=condition=available \
            - -timeout=300s \
            deployment/"$deployment" \
            - n "$NAMESPACE"

        if [ $? -eq 0 ]; then
            log_success "$deployment is ready"
        else
            log_error "$deployment failed to become ready"
            return 1
        fi
    done

    # Run smoke tests
    log_info "Running smoke tests..."
    python3 "$PROJECT_ROOT/tests/smoke/test_deployment.py" \
        - -environment="$ENVIRONMENT" \
        - -namespace="$NAMESPACE"

    if [ $? -eq 0 ]; then
        log_success "All health checks passed"
    else
        log_error "Health checks failed"
        return 1
    fi
}

## Rollback function

rollback_deployment() {
    log_warning "Rolling back deployment..."

    # Get previous revision
    local previous_revision=$(helm history consciousness-system -n "$NAMESPACE" --max 2 -o json | jq -r '.[1].revision')

    if [ "$previous_revision" != "null" ]; then
        helm rollback consciousness-system "$previous_revision" -n "$NAMESPACE"
        log_success "Rollback completed to revision $previous_revision"
    else
        log_error "No previous revision found for rollback"
        exit 1
    fi
}

## Main deployment function

main() {
    log_info "Starting deployment of SynapticOS Consciousness System"
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"

    validate_environment
    validate_prerequisites

    # Deploy infrastructure
    deploy_infrastructure

    # Deploy application
    if ! deploy_application; then
        log_error "Application deployment failed"
        exit 1
    fi

    # Run health checks
    if ! run_health_checks; then
        log_error "Health checks failed, initiating rollback"
        rollback_deployment
        exit 1
    fi

    log_success "Deployment completed successfully!"
    log_info "Consciousness system is now running in $ENVIRONMENT environment"

    # Display access information
    echo ""
    log_info "Access Information:"
    kubectl get ingress -n "$NAMESPACE" -o wide
    echo ""
    log_info "To monitor the system:"
    echo "kubectl get pods -n $NAMESPACE"
    echo "kubectl logs -f deployment/consciousness-bus -n $NAMESPACE"
}

## Script execution

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

```text

### Environment-Specific Deployment Scripts

#### Production Deployment Script

```bash

```bash
#!/bin/bash
## scripts/deploy-production.sh
## Production-specific deployment with additional safety checks

set -euo pipefail

ENVIRONMENT="production"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

## Production safety checks

production_safety_checks() {
    echo "🔒 Running production safety checks..."

    # Check if this is a tagged release
    if ! git describe --exact-match --tags HEAD &>/dev/null; then
        echo "❌ Production deployments must be from tagged releases"
        exit 1
    fi

    # Check if all tests pass
    echo "🧪 Running full test suite..."
    python -m pytest tests/ -v --tb=short

    # Check security scan
    echo "🔍 Running security scan..."
    safety check --json --output safety-report.json

    # Require manual confirmation
    echo "⚠️  You are about to deploy to PRODUCTION"
    echo "Environment: $ENVIRONMENT"
    echo "Version: $(git describe --tags)"
    echo "Commit: $(git rev-parse HEAD)"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
}

## Production-specific backup

create_pre_deployment_backup() {
    echo "💾 Creating pre-deployment backup..."

    # Database backup
    kubectl exec -n consciousness-system \
        deployment/postgresql -- \
        pg_dump -U consciousness consciousness > \
        "backup-$(date +%Y%m%d-%H%M%S).sql"

    # Configuration backup
    kubectl get configmaps,secrets -n consciousness-system -o yaml > \
        "config-backup-$(date +%Y%m%d-%H%M%S).yaml"

    echo "✅ Backup completed"
}

## Blue-green deployment for production

blue_green_deployment() {
    echo "🔄 Performing blue-green deployment..."

    # Deploy to green environment
    helm upgrade --install consciousness-system-green \
        "$SCRIPT_DIR/../helm/consciousness-system" \
        - -namespace consciousness-system-green \
        - -create-namespace \
        - -values "$SCRIPT_DIR/../helm/consciousness-system/values-production.yaml" \
        - -set global.imageTag="$(git describe --tags)" \
        - -wait \
        - -timeout=600s

    # Run health checks on green
    echo "🏥 Running health checks on green environment..."
    python3 "$SCRIPT_DIR/../tests/smoke/test_deployment.py" \
        - -environment=production \
        - -namespace=consciousness-system-green

    # Switch traffic to green
    echo "🔀 Switching traffic to green environment..."
    kubectl patch service consciousness-bus-service \
        - n consciousness-system \
        - p '{"spec":{"selector":{"deployment":"consciousness-system-green"}}}'

    # Monitor for 5 minutes
    echo "📊 Monitoring green environment for 5 minutes..."
    sleep 300

    # Final health check
    if python3 "$SCRIPT_DIR/../tests/smoke/test_deployment.py" \
        - -environment=production \
        - -namespace=consciousness-system; then
        echo "✅ Green deployment successful, cleaning up blue"
        helm uninstall consciousness-system-blue -n consciousness-system-blue || true
        kubectl delete namespace consciousness-system-blue || true
    else
        echo "❌ Green deployment failed, rolling back to blue"
        kubectl patch service consciousness-bus-service \
            - n consciousness-system \
            - p '{"spec":{"selector":{"deployment":"consciousness-system-blue"}}}'
        exit 1
    fi
}

main() {
    production_safety_checks
    create_pre_deployment_backup
    blue_green_deployment

    echo "🎉 Production deployment completed successfully!"
}

main "$@"
```text

ENVIRONMENT="production"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

## Production safety checks

production_safety_checks() {
    echo "🔒 Running production safety checks..."

    # Check if this is a tagged release
    if ! git describe --exact-match --tags HEAD &>/dev/null; then
        echo "❌ Production deployments must be from tagged releases"
        exit 1
    fi

    # Check if all tests pass
    echo "🧪 Running full test suite..."
    python -m pytest tests/ -v --tb=short

    # Check security scan
    echo "🔍 Running security scan..."
    safety check --json --output safety-report.json

    # Require manual confirmation
    echo "⚠️  You are about to deploy to PRODUCTION"
    echo "Environment: $ENVIRONMENT"
    echo "Version: $(git describe --tags)"
    echo "Commit: $(git rev-parse HEAD)"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
}

## Production-specific backup

create_pre_deployment_backup() {
    echo "💾 Creating pre-deployment backup..."

    # Database backup
    kubectl exec -n consciousness-system \
        deployment/postgresql -- \
        pg_dump -U consciousness consciousness > \
        "backup-$(date +%Y%m%d-%H%M%S).sql"

    # Configuration backup
    kubectl get configmaps,secrets -n consciousness-system -o yaml > \
        "config-backup-$(date +%Y%m%d-%H%M%S).yaml"

    echo "✅ Backup completed"
}

## Blue-green deployment for production

blue_green_deployment() {
    echo "🔄 Performing blue-green deployment..."

    # Deploy to green environment
    helm upgrade --install consciousness-system-green \
        "$SCRIPT_DIR/../helm/consciousness-system" \
        - -namespace consciousness-system-green \
        - -create-namespace \
        - -values "$SCRIPT_DIR/../helm/consciousness-system/values-production.yaml" \
        - -set global.imageTag="$(git describe --tags)" \
        - -wait \
        - -timeout=600s

    # Run health checks on green
    echo "🏥 Running health checks on green environment..."
    python3 "$SCRIPT_DIR/../tests/smoke/test_deployment.py" \
        - -environment=production \
        - -namespace=consciousness-system-green

    # Switch traffic to green
    echo "🔀 Switching traffic to green environment..."
    kubectl patch service consciousness-bus-service \
        - n consciousness-system \
        - p '{"spec":{"selector":{"deployment":"consciousness-system-green"}}}'

    # Monitor for 5 minutes
    echo "📊 Monitoring green environment for 5 minutes..."
    sleep 300

    # Final health check
    if python3 "$SCRIPT_DIR/../tests/smoke/test_deployment.py" \
        - -environment=production \
        - -namespace=consciousness-system; then
        echo "✅ Green deployment successful, cleaning up blue"
        helm uninstall consciousness-system-blue -n consciousness-system-blue || true
        kubectl delete namespace consciousness-system-blue || true
    else
        echo "❌ Green deployment failed, rolling back to blue"
        kubectl patch service consciousness-bus-service \
            - n consciousness-system \
            - p '{"spec":{"selector":{"deployment":"consciousness-system-blue"}}}'
        exit 1
    fi
}

main() {
    production_safety_checks
    create_pre_deployment_backup
    blue_green_deployment

    echo "🎉 Production deployment completed successfully!"
}

main "$@"

```text

- --

## Configuration Management Scripts

### Configuration Validation Script

```bash

### Configuration Validation Script

```bash
#!/bin/bash
## scripts/validate-config.sh
## Validate all configuration files and templates

set -euo pipefail

validate_yaml_files() {
    echo "📋 Validating YAML configuration files..."

    local yaml_files=(
        "helm/consciousness-system/values.yaml"
        "helm/consciousness-system/values-development.yaml"
        "helm/consciousness-system/values-staging.yaml"
        "helm/consciousness-system/values-production.yaml"
        "k8s/base/*.yaml"
        "ansible/vars/*.yml"
    )

    for pattern in "${yaml_files[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                echo "Validating $file..."
                if ! python -c "import yaml; yaml.safe_load(open('$file'))"; then
                    echo "❌ Invalid YAML: $file"
                    exit 1
                fi
            fi
        done
    done

    echo "✅ All YAML files are valid"
}

validate_helm_charts() {
    echo "⚓ Validating Helm charts..."

    local environments=("development" "staging" "production")

    for env in "${environments[@]}"; do
        echo "Validating Helm chart for $env..."
        helm template consciousness-system \
            ./helm/consciousness-system \
            - -values "./helm/consciousness-system/values-$env.yaml" \
            - -dry-run > /dev/null

        if [ $? -eq 0 ]; then
            echo "✅ Helm chart valid for $env"
        else
            echo "❌ Helm chart invalid for $env"
            exit 1
        fi
    done
}

validate_terraform() {
    echo "🏗️ Validating Terraform configurations..."

    local environments=("development" "staging" "production")

    for env in "${environments[@]}"; do
        echo "Validating Terraform for $env..."
        cd "infrastructure/environments/$env"

        terraform init -backend=false
        terraform validate

        if [ $? -eq 0 ]; then
            echo "✅ Terraform valid for $env"
        else
            echo "❌ Terraform invalid for $env"
            exit 1
        fi

        cd - > /dev/null
    done
}

validate_ansible() {
    echo "📚 Validating Ansible playbooks..."

    ansible-playbook ansible/site.yml --syntax-check

    if [ $? -eq 0 ]; then
        echo "✅ Ansible playbooks are valid"
    else
        echo "❌ Ansible playbooks have syntax errors"
        exit 1
    fi
}

main() {
    echo "🔍 Starting configuration validation..."

    validate_yaml_files
    validate_helm_charts
    validate_terraform
    validate_ansible

    echo "🎉 All configurations are valid!"
}

main "$@"
```text

validate_yaml_files() {
    echo "📋 Validating YAML configuration files..."

    local yaml_files=(
        "helm/consciousness-system/values.yaml"
        "helm/consciousness-system/values-development.yaml"
        "helm/consciousness-system/values-staging.yaml"
        "helm/consciousness-system/values-production.yaml"
        "k8s/base/*.yaml"
        "ansible/vars/*.yml"
    )

    for pattern in "${yaml_files[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                echo "Validating $file..."
                if ! python -c "import yaml; yaml.safe_load(open('$file'))"; then
                    echo "❌ Invalid YAML: $file"
                    exit 1
                fi
            fi
        done
    done

    echo "✅ All YAML files are valid"
}

validate_helm_charts() {
    echo "⚓ Validating Helm charts..."

    local environments=("development" "staging" "production")

    for env in "${environments[@]}"; do
        echo "Validating Helm chart for $env..."
        helm template consciousness-system \
            ./helm/consciousness-system \
            - -values "./helm/consciousness-system/values-$env.yaml" \
            - -dry-run > /dev/null

        if [ $? -eq 0 ]; then
            echo "✅ Helm chart valid for $env"
        else
            echo "❌ Helm chart invalid for $env"
            exit 1
        fi
    done
}

validate_terraform() {
    echo "🏗️ Validating Terraform configurations..."

    local environments=("development" "staging" "production")

    for env in "${environments[@]}"; do
        echo "Validating Terraform for $env..."
        cd "infrastructure/environments/$env"

        terraform init -backend=false
        terraform validate

        if [ $? -eq 0 ]; then
            echo "✅ Terraform valid for $env"
        else
            echo "❌ Terraform invalid for $env"
            exit 1
        fi

        cd - > /dev/null
    done
}

validate_ansible() {
    echo "📚 Validating Ansible playbooks..."

    ansible-playbook ansible/site.yml --syntax-check

    if [ $? -eq 0 ]; then
        echo "✅ Ansible playbooks are valid"
    else
        echo "❌ Ansible playbooks have syntax errors"
        exit 1
    fi
}

main() {
    echo "🔍 Starting configuration validation..."

    validate_yaml_files
    validate_helm_charts
    validate_terraform
    validate_ansible

    echo "🎉 All configurations are valid!"
}

main "$@"

```text

### Configuration Update Script

```bash

```bash
#!/bin/bash
## scripts/update-config.sh
## Update configuration across all environments

set -euo pipefail

update_consciousness_config() {
    local environment="$1"
    local config_key="$2"
    local config_value="$3"

    echo "🔧 Updating $config_key to $config_value in $environment"

    # Update Helm values
    yq eval ".$config_key = \"$config_value\"" -i \
        "helm/consciousness-system/values-$environment.yaml"

    # Update Kubernetes ConfigMap
    kubectl patch configmap consciousness-config \
        - n consciousness-system \
        - -patch "{\"data\":{\"$config_key\":\"$config_value\"}}"

    # Restart affected deployments
    kubectl rollout restart deployment \
        - l app.kubernetes.io/name=consciousness-system \
        - n consciousness-system

    echo "✅ Configuration updated successfully"
}

bulk_config_update() {
    local environment="$1"
    local config_file="$2"

    echo "📦 Performing bulk configuration update for $environment"

    # Validate config file
    if [ ! -f "$config_file" ]; then
        echo "❌ Configuration file not found: $config_file"
        exit 1
    fi

    # Apply configuration updates
    while IFS='=' read -r key value; do
        if [[ ! "$key" =~ ^#.* ]] && [[ -n "$key" ]]; then
            update_consciousness_config "$environment" "$key" "$value"
        fi
    done < "$config_file"

    echo "✅ Bulk configuration update completed"
}

main() {
    local action="${1:-help}"

    case "$action" in
        "update")
            update_consciousness_config "$2" "$3" "$4"
            ;;
        "bulk")
            bulk_config_update "$2" "$3"
            ;;
        "help"|*)
            echo "Usage:"
            echo "  $0 update <environment> <key> <value>"
            echo "  $0 bulk <environment> <config_file>"
            echo ""
            echo "Examples:"
            echo "  $0 update production neural-population-size 2000"
            echo "  $0 bulk staging config-updates.txt"
            ;;
    esac
}

main "$@"
```text

update_consciousness_config() {
    local environment="$1"
    local config_key="$2"
    local config_value="$3"

    echo "🔧 Updating $config_key to $config_value in $environment"

    # Update Helm values
    yq eval ".$config_key = \"$config_value\"" -i \
        "helm/consciousness-system/values-$environment.yaml"

    # Update Kubernetes ConfigMap
    kubectl patch configmap consciousness-config \
        - n consciousness-system \
        - -patch "{\"data\":{\"$config_key\":\"$config_value\"}}"

    # Restart affected deployments
    kubectl rollout restart deployment \
        - l app.kubernetes.io/name=consciousness-system \
        - n consciousness-system

    echo "✅ Configuration updated successfully"
}

bulk_config_update() {
    local environment="$1"
    local config_file="$2"

    echo "📦 Performing bulk configuration update for $environment"

    # Validate config file
    if [ ! -f "$config_file" ]; then
        echo "❌ Configuration file not found: $config_file"
        exit 1
    fi

    # Apply configuration updates
    while IFS='=' read -r key value; do
        if [[ ! "$key" =~ ^#.* ]] && [[ -n "$key" ]]; then
            update_consciousness_config "$environment" "$key" "$value"
        fi
    done < "$config_file"

    echo "✅ Bulk configuration update completed"
}

main() {
    local action="${1:-help}"

    case "$action" in
        "update")
            update_consciousness_config "$2" "$3" "$4"
            ;;
        "bulk")
            bulk_config_update "$2" "$3"
            ;;
        "help"|*)
            echo "Usage:"
            echo "  $0 update <environment> <key> <value>"
            echo "  $0 bulk <environment> <config_file>"
            echo ""
            echo "Examples:"
            echo "  $0 update production neural-population-size 2000"
            echo "  $0 bulk staging config-updates.txt"
            ;;
    esac
}

main "$@"

```text

- --

## Monitoring and Health Check Scripts

### System Health Check Script

```bash

### System Health Check Script

```bash
#!/bin/bash
## scripts/health-check.sh
## Comprehensive system health monitoring

set -euo pipefail

check_kubernetes_health() {
    echo "🏥 Checking Kubernetes cluster health..."

    # Check node status
    local unhealthy_nodes=$(kubectl get nodes --no-headers | grep -v Ready | wc -l)
    if [ "$unhealthy_nodes" -gt 0 ]; then
        echo "⚠️ $unhealthy_nodes unhealthy nodes detected"
        kubectl get nodes
    else
        echo "✅ All nodes are healthy"
    fi

    # Check system pods
    local failing_pods=$(kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers | wc -l)
    if [ "$failing_pods" -gt 0 ]; then
        echo "⚠️ $failing_pods failing pods detected"
        kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
    else
        echo "✅ All system pods are healthy"
    fi
}

check_consciousness_components() {
    echo "🧠 Checking consciousness system components..."

    local namespace="consciousness-system"
    local components=(
        "consciousness-bus"
        "neural-darwinism-engine"
        "personal-context-engine"
        "security-tutor"
        "lm-studio-integration"
    )

    for component in "${components[@]}"; do
        local ready_replicas=$(kubectl get deployment "$component" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired_replicas=$(kubectl get deployment "$component" -n "$namespace" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

        if [ "$ready_replicas" -eq "$desired_replicas" ] && [ "$ready_replicas" -gt 0 ]; then
            echo "✅ $component: $ready_replicas/$desired_replicas replicas ready"
        else
            echo "❌ $component: $ready_replicas/$desired_replicas replicas ready"
        fi
    done
}

check_database_health() {
    echo "🗄️ Checking database health..."

    # Check PostgreSQL
    local db_status=$(kubectl exec -n consciousness-system deployment/postgresql -- pg_isready -U consciousness 2>/dev/null && echo "healthy" || echo "unhealthy")
    echo "PostgreSQL: $db_status"

    # Check Redis
    local redis_status=$(kubectl exec -n consciousness-system deployment/redis -- redis-cli ping 2>/dev/null && echo "healthy" || echo "unhealthy")
    echo "Redis: $redis_status"
}

check_consciousness_metrics() {
    echo "📊 Checking consciousness system metrics..."

    # Get consciousness level
    local consciousness_level=$(curl -s http://consciousness-bus-service.consciousness-system:8080/api/v2/consciousness/status | jq -r '.consciousness_level' 2>/dev/null || echo "unknown")
    echo "Current consciousness level: $consciousness_level"

    # Check component response times
    local components=("neural-darwinism-engine" "personal-context-engine" "security-tutor")
    for component in "${components[@]}"; do
        local response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://$component.consciousness-system:8080/health" 2>/dev/null || echo "timeout")
        echo "$component response time: ${response_time}s"
    done
}

generate_health_report() {
    echo "📋 Generating health report..."

    local report_file="health-report-$(date +%Y%m%d-%H%M%S).json"

    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cluster_health": {
    "nodes": $(kubectl get nodes -o json | jq '.items | length'),
    "healthy_nodes": $(kubectl get nodes --no-headers | grep Ready | wc -l),
    "total_pods": $(kubectl get pods -A --no-headers | wc -l),
    "running_pods": $(kubectl get pods -A --field-selector=status.phase=Running --no-headers | wc -l)
  },
  "consciousness_system": {
    "namespace": "consciousness-system",
    "deployments": $(kubectl get deployments -n consciousness-system -o json | jq '[.items[] | {name: .metadata.name, ready: .status.readyReplicas, desired: .spec.replicas}]'),
    "services": $(kubectl get services -n consciousness-system -o json | jq '[.items[] | {name: .metadata.name, type: .spec.type}]')
  },
  "database_health": {
    "postgresql": "$(kubectl exec -n consciousness-system deployment/postgresql -- pg_isready -U consciousness 2>/dev/null && echo 'healthy' || echo 'unhealthy')",
    "redis": "$(kubectl exec -n consciousness-system deployment/redis -- redis-cli ping 2>/dev/null && echo 'healthy' || echo 'unhealthy')"
  }
}
EOF

    echo "Health report saved to: $report_file"
}

main() {
    echo "🔍 Starting comprehensive health check..."
    echo "Timestamp: $(date)"
    echo ""

    check_kubernetes_health
    echo ""
    check_consciousness_components
    echo ""
    check_database_health
    echo ""
    check_consciousness_metrics
    echo ""
    generate_health_report

    echo ""
    echo "🎉 Health check completed!"
}

main "$@"
```text

check_kubernetes_health() {
    echo "🏥 Checking Kubernetes cluster health..."

    # Check node status
    local unhealthy_nodes=$(kubectl get nodes --no-headers | grep -v Ready | wc -l)
    if [ "$unhealthy_nodes" -gt 0 ]; then
        echo "⚠️ $unhealthy_nodes unhealthy nodes detected"
        kubectl get nodes
    else
        echo "✅ All nodes are healthy"
    fi

    # Check system pods
    local failing_pods=$(kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers | wc -l)
    if [ "$failing_pods" -gt 0 ]; then
        echo "⚠️ $failing_pods failing pods detected"
        kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
    else
        echo "✅ All system pods are healthy"
    fi
}

check_consciousness_components() {
    echo "🧠 Checking consciousness system components..."

    local namespace="consciousness-system"
    local components=(
        "consciousness-bus"
        "neural-darwinism-engine"
        "personal-context-engine"
        "security-tutor"
        "lm-studio-integration"
    )

    for component in "${components[@]}"; do
        local ready_replicas=$(kubectl get deployment "$component" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local desired_replicas=$(kubectl get deployment "$component" -n "$namespace" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")

        if [ "$ready_replicas" -eq "$desired_replicas" ] && [ "$ready_replicas" -gt 0 ]; then
            echo "✅ $component: $ready_replicas/$desired_replicas replicas ready"
        else
            echo "❌ $component: $ready_replicas/$desired_replicas replicas ready"
        fi
    done
}

check_database_health() {
    echo "🗄️ Checking database health..."

    # Check PostgreSQL
    local db_status=$(kubectl exec -n consciousness-system deployment/postgresql -- pg_isready -U consciousness 2>/dev/null && echo "healthy" || echo "unhealthy")
    echo "PostgreSQL: $db_status"

    # Check Redis
    local redis_status=$(kubectl exec -n consciousness-system deployment/redis -- redis-cli ping 2>/dev/null && echo "healthy" || echo "unhealthy")
    echo "Redis: $redis_status"
}

check_consciousness_metrics() {
    echo "📊 Checking consciousness system metrics..."

    # Get consciousness level
    local consciousness_level=$(curl -s http://consciousness-bus-service.consciousness-system:8080/api/v2/consciousness/status | jq -r '.consciousness_level' 2>/dev/null || echo "unknown")
    echo "Current consciousness level: $consciousness_level"

    # Check component response times
    local components=("neural-darwinism-engine" "personal-context-engine" "security-tutor")
    for component in "${components[@]}"; do
        local response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://$component.consciousness-system:8080/health" 2>/dev/null || echo "timeout")
        echo "$component response time: ${response_time}s"
    done
}

generate_health_report() {
    echo "📋 Generating health report..."

    local report_file="health-report-$(date +%Y%m%d-%H%M%S).json"

    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "cluster_health": {
    "nodes": $(kubectl get nodes -o json | jq '.items | length'),
    "healthy_nodes": $(kubectl get nodes --no-headers | grep Ready | wc -l),
    "total_pods": $(kubectl get pods -A --no-headers | wc -l),
    "running_pods": $(kubectl get pods -A --field-selector=status.phase=Running --no-headers | wc -l)
  },
  "consciousness_system": {
    "namespace": "consciousness-system",
    "deployments": $(kubectl get deployments -n consciousness-system -o json | jq '[.items[] | {name: .metadata.name, ready: .status.readyReplicas, desired: .spec.replicas}]'),
    "services": $(kubectl get services -n consciousness-system -o json | jq '[.items[] | {name: .metadata.name, type: .spec.type}]')
  },
  "database_health": {
    "postgresql": "$(kubectl exec -n consciousness-system deployment/postgresql -- pg_isready -U consciousness 2>/dev/null && echo 'healthy' || echo 'unhealthy')",
    "redis": "$(kubectl exec -n consciousness-system deployment/redis -- redis-cli ping 2>/dev/null && echo 'healthy' || echo 'unhealthy')"
  }
}
EOF

    echo "Health report saved to: $report_file"
}

main() {
    echo "🔍 Starting comprehensive health check..."
    echo "Timestamp: $(date)"
    echo ""

    check_kubernetes_health
    echo ""
    check_consciousness_components
    echo ""
    check_database_health
    echo ""
    check_consciousness_metrics
    echo ""
    generate_health_report

    echo ""
    echo "🎉 Health check completed!"
}

main "$@"

```text

- --

## Backup and Recovery Scripts

### Automated Backup Script

```bash

### Automated Backup Script

```bash
#!/bin/bash
## scripts/backup-system.sh
## Comprehensive backup of consciousness system

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/consciousness-system}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
NAMESPACE="consciousness-system"

create_backup_directory() {
    local backup_timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_path="$BACKUP_DIR/$backup_timestamp"

    mkdir -p "$backup_path"
    echo "$backup_path"
}

backup_database() {
    local backup_path="$1"

    echo "💾 Backing up PostgreSQL database..."

    kubectl exec -n "$NAMESPACE" deployment/postgresql -- \
        pg_dump -U consciousness consciousness | \
        gzip > "$backup_path/postgresql-backup.sql.gz"

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL backup completed"
    else
        echo "❌ PostgreSQL backup failed"
        return 1
    fi
}

backup_redis() {
    local backup_path="$1"

    echo "💾 Backing up Redis data..."

    kubectl exec -n "$NAMESPACE" deployment/redis -- \
        redis-cli --rdb /tmp/dump.rdb

    kubectl cp "$NAMESPACE/redis-pod:/tmp/dump.rdb" \
        "$backup_path/redis-backup.rdb"

    if [ $? -eq 0 ]; then
        echo "✅ Redis backup completed"
    else
        echo "❌ Redis backup failed"
        return 1
    fi
}

backup_kubernetes_resources() {
    local backup_path="$1"

    echo "💾 Backing up Kubernetes resources..."

    # Backup all resources in consciousness-system namespace
    kubectl get all,configmaps,secrets,pvc -n "$NAMESPACE" -o yaml > \
        "$backup_path/kubernetes-resources.yaml"

    # Backup Helm releases
    helm list -n "$NAMESPACE" -o yaml > \
        "$backup_path/helm-releases.yaml"

    # Backup custom resources
    kubectl get crd -o yaml > \
        "$backup_path/custom-resources.yaml"

    echo "✅ Kubernetes resources backup completed"
}

backup_consciousness_state() {
    local backup_path="$1"

    echo "💾 Backing up consciousness state..."

    # Export consciousness state via API
    curl -s "http://consciousness-bus-service.$NAMESPACE:8080/api/v2/consciousness/export" \
        - H "Authorization: Bearer $CONSCIOUSNESS_API_TOKEN" \
        - o "$backup_path/consciousness-state.json"

    if [ $? -eq 0 ]; then
        echo "✅ Consciousness state backup completed"
    else
        echo "❌ Consciousness state backup failed"
        return 1
    fi
}

cleanup_old_backups() {
    echo "🧹 Cleaning up old backups..."

    find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

    echo "✅ Old backups cleaned up (retention: $RETENTION_DAYS days)"
}

verify_backup() {
    local backup_path="$1"

    echo "🔍 Verifying backup integrity..."

    # Check if all backup files exist
    local required_files=(
        "postgresql-backup.sql.gz"
        "redis-backup.rdb"
        "kubernetes-resources.yaml"
        "consciousness-state.json"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$backup_path/$file" ]; then
            echo "❌ Missing backup file: $file"
            return 1
        fi
    done

    # Verify PostgreSQL backup
    if ! gunzip -t "$backup_path/postgresql-backup.sql.gz"; then
        echo "❌ PostgreSQL backup is corrupted"
        return 1
    fi

    # Verify JSON backup
    if ! jq empty "$backup_path/consciousness-state.json" 2>/dev/null; then
        echo "❌ Consciousness state backup is corrupted"
        return 1
    fi

    echo "✅ Backup verification completed successfully"
}

main() {
    echo "🔄 Starting consciousness system backup..."
    echo "Timestamp: $(date)"

    local backup_path=$(create_backup_directory)
    echo "Backup location: $backup_path"

    # Perform backups
    backup_database "$backup_path"
    backup_redis "$backup_path"
    backup_kubernetes_resources "$backup_path"
    backup_consciousness_state "$backup_path"

    # Verify backup
    verify_backup "$backup_path"

    # Cleanup old backups
    cleanup_old_backups

    # Create backup manifest
    cat > "$backup_path/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_type": "full",
  "namespace": "$NAMESPACE",
  "files": [
    "postgresql-backup.sql.gz",
    "redis-backup.rdb",
    "kubernetes-resources.yaml",
    "consciousness-state.json"
  ],
  "size": "$(du -sh $backup_path | cut -f1)"
}
EOF

    echo "🎉 Backup completed successfully!"
    echo "Backup path: $backup_path"
    echo "Backup size: $(du -sh $backup_path | cut -f1)"
}

main "$@"
```text

BACKUP_DIR="${BACKUP_DIR:-/backups/consciousness-system}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
NAMESPACE="consciousness-system"

create_backup_directory() {
    local backup_timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_path="$BACKUP_DIR/$backup_timestamp"

    mkdir -p "$backup_path"
    echo "$backup_path"
}

backup_database() {
    local backup_path="$1"

    echo "💾 Backing up PostgreSQL database..."

    kubectl exec -n "$NAMESPACE" deployment/postgresql -- \
        pg_dump -U consciousness consciousness | \
        gzip > "$backup_path/postgresql-backup.sql.gz"

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL backup completed"
    else
        echo "❌ PostgreSQL backup failed"
        return 1
    fi
}

backup_redis() {
    local backup_path="$1"

    echo "💾 Backing up Redis data..."

    kubectl exec -n "$NAMESPACE" deployment/redis -- \
        redis-cli --rdb /tmp/dump.rdb

    kubectl cp "$NAMESPACE/redis-pod:/tmp/dump.rdb" \
        "$backup_path/redis-backup.rdb"

    if [ $? -eq 0 ]; then
        echo "✅ Redis backup completed"
    else
        echo "❌ Redis backup failed"
        return 1
    fi
}

backup_kubernetes_resources() {
    local backup_path="$1"

    echo "💾 Backing up Kubernetes resources..."

    # Backup all resources in consciousness-system namespace
    kubectl get all,configmaps,secrets,pvc -n "$NAMESPACE" -o yaml > \
        "$backup_path/kubernetes-resources.yaml"

    # Backup Helm releases
    helm list -n "$NAMESPACE" -o yaml > \
        "$backup_path/helm-releases.yaml"

    # Backup custom resources
    kubectl get crd -o yaml > \
        "$backup_path/custom-resources.yaml"

    echo "✅ Kubernetes resources backup completed"
}

backup_consciousness_state() {
    local backup_path="$1"

    echo "💾 Backing up consciousness state..."

    # Export consciousness state via API
    curl -s "http://consciousness-bus-service.$NAMESPACE:8080/api/v2/consciousness/export" \
        - H "Authorization: Bearer $CONSCIOUSNESS_API_TOKEN" \
        - o "$backup_path/consciousness-state.json"

    if [ $? -eq 0 ]; then
        echo "✅ Consciousness state backup completed"
    else
        echo "❌ Consciousness state backup failed"
        return 1
    fi
}

cleanup_old_backups() {
    echo "🧹 Cleaning up old backups..."

    find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

    echo "✅ Old backups cleaned up (retention: $RETENTION_DAYS days)"
}

verify_backup() {
    local backup_path="$1"

    echo "🔍 Verifying backup integrity..."

    # Check if all backup files exist
    local required_files=(
        "postgresql-backup.sql.gz"
        "redis-backup.rdb"
        "kubernetes-resources.yaml"
        "consciousness-state.json"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$backup_path/$file" ]; then
            echo "❌ Missing backup file: $file"
            return 1
        fi
    done

    # Verify PostgreSQL backup
    if ! gunzip -t "$backup_path/postgresql-backup.sql.gz"; then
        echo "❌ PostgreSQL backup is corrupted"
        return 1
    fi

    # Verify JSON backup
    if ! jq empty "$backup_path/consciousness-state.json" 2>/dev/null; then
        echo "❌ Consciousness state backup is corrupted"
        return 1
    fi

    echo "✅ Backup verification completed successfully"
}

main() {
    echo "🔄 Starting consciousness system backup..."
    echo "Timestamp: $(date)"

    local backup_path=$(create_backup_directory)
    echo "Backup location: $backup_path"

    # Perform backups
    backup_database "$backup_path"
    backup_redis "$backup_path"
    backup_kubernetes_resources "$backup_path"
    backup_consciousness_state "$backup_path"

    # Verify backup
    verify_backup "$backup_path"

    # Cleanup old backups
    cleanup_old_backups

    # Create backup manifest
    cat > "$backup_path/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "backup_type": "full",
  "namespace": "$NAMESPACE",
  "files": [
    "postgresql-backup.sql.gz",
    "redis-backup.rdb",
    "kubernetes-resources.yaml",
    "consciousness-state.json"
  ],
  "size": "$(du -sh $backup_path | cut -f1)"
}
EOF

    echo "🎉 Backup completed successfully!"
    echo "Backup path: $backup_path"
    echo "Backup size: $(du -sh $backup_path | cut -f1)"
}

main "$@"

```text

### Disaster Recovery Script

```bash

```bash
#!/bin/bash
## scripts/disaster-recovery.sh
## Complete disaster recovery procedures

set -euo pipefail

BACKUP_PATH="${1:-}"
NAMESPACE="consciousness-system"

validate_backup() {
    local backup_path="$1"

    echo "🔍 Validating backup for recovery..."

    if [ ! -d "$backup_path" ]; then
        echo "❌ Backup directory not found: $backup_path"
        exit 1
    fi

    if [ ! -f "$backup_path/manifest.json" ]; then
        echo "❌ Backup manifest not found"
        exit 1
    fi

    # Verify backup integrity
    local required_files=(
        "postgresql-backup.sql.gz"
        "redis-backup.rdb"
        "kubernetes-resources.yaml"
        "consciousness-state.json"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$backup_path/$file" ]; then
            echo "❌ Missing backup file: $file"
            exit 1
        fi
    done

    echo "✅ Backup validation completed"
}

prepare_recovery_environment() {
    echo "🏗️ Preparing recovery environment..."

    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Apply RBAC and basic resources
    kubectl apply -f k8s/base/namespace.yaml

    echo "✅ Recovery environment prepared"
}

restore_database() {
    local backup_path="$1"

    echo "🗄️ Restoring PostgreSQL database..."

    # Deploy PostgreSQL if not exists
    helm upgrade --install postgresql \
        bitnami/postgresql \
        - -namespace "$NAMESPACE" \
        - -set auth.postgresPassword="consciousness-db-password" \
        - -set auth.database="consciousness" \
        - -wait

    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n "$NAMESPACE" --timeout=300s

    # Restore database
    gunzip -c "$backup_path/postgresql-backup.sql.gz" | \
        kubectl exec -i -n "$NAMESPACE" deployment/postgresql -- \
        psql -U postgres -d consciousness

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL database restored"
    else
        echo "❌ PostgreSQL database restoration failed"
        exit 1
    fi
}

restore_redis() {
    local backup_path="$1"

    echo "🔴 Restoring Redis data..."

    # Deploy Redis if not exists
    helm upgrade --install redis \
        bitnami/redis \
        - -namespace "$NAMESPACE" \
        - -set auth.password="consciousness-redis-password" \
        - -wait

    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=300s

    # Copy backup file to Redis pod
    kubectl cp "$backup_path/redis-backup.rdb" \
        "$NAMESPACE/redis-master-0:/tmp/dump.rdb"

    # Restart Redis to load the backup
    kubectl delete pod -l app.kubernetes.io/name=redis -n "$NAMESPACE"
    kubectl wait --for

BACKUP_PATH="${1:-}"
NAMESPACE="consciousness-system"

validate_backup() {
    local backup_path="$1"

    echo "🔍 Validating backup for recovery..."

    if [ ! -d "$backup_path" ]; then
        echo "❌ Backup directory not found: $backup_path"
        exit 1
    fi

    if [ ! -f "$backup_path/manifest.json" ]; then
        echo "❌ Backup manifest not found"
        exit 1
    fi

    # Verify backup integrity
    local required_files=(
        "postgresql-backup.sql.gz"
        "redis-backup.rdb"
        "kubernetes-resources.yaml"
        "consciousness-state.json"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$backup_path/$file" ]; then
            echo "❌ Missing backup file: $file"
            exit 1
        fi
    done

    echo "✅ Backup validation completed"
}

prepare_recovery_environment() {
    echo "🏗️ Preparing recovery environment..."

    # Create namespace
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Apply RBAC and basic resources
    kubectl apply -f k8s/base/namespace.yaml

    echo "✅ Recovery environment prepared"
}

restore_database() {
    local backup_path="$1"

    echo "🗄️ Restoring PostgreSQL database..."

    # Deploy PostgreSQL if not exists
    helm upgrade --install postgresql \
        bitnami/postgresql \
        - -namespace "$NAMESPACE" \
        - -set auth.postgresPassword="consciousness-db-password" \
        - -set auth.database="consciousness" \
        - -wait

    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n "$NAMESPACE" --timeout=300s

    # Restore database
    gunzip -c "$backup_path/postgresql-backup.sql.gz" | \
        kubectl exec -i -n "$NAMESPACE" deployment/postgresql -- \
        psql -U postgres -d consciousness

    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL database restored"
    else
        echo "❌ PostgreSQL database restoration failed"
        exit 1
    fi
}

restore_redis() {
    local backup_path="$1"

    echo "🔴 Restoring Redis data..."

    # Deploy Redis if not exists
    helm upgrade --install redis \
        bitnami/redis \
        - -namespace "$NAMESPACE" \
        - -set auth.password="consciousness-redis-password" \
        - -wait

    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=300s

    # Copy backup file to Redis pod
    kubectl cp "$backup_path/redis-backup.rdb" \
        "$NAMESPACE/redis-master-0:/tmp/dump.rdb"

    # Restart Redis to load the backup
    kubectl delete pod -l app.kubernetes.io/name=redis -n "$NAMESPACE"
    kubectl wait --for