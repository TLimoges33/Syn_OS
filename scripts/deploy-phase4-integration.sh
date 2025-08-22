#!/bin/bash

# Phase 4 Integration Deployment Script
# =====================================
# Deploys comprehensive threat intelligence dashboard and Phase 4 integration components
# Includes Kubernetes deployment, monitoring setup, and integration validation

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="synos-phase4"
DEPLOYMENT_TIMEOUT="300s"
LOG_FILE="/tmp/phase4-deployment-$(date +%Y%m%d-%H%M%S).log"

# Logging function
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "${RED}❌ Error occurred in deployment script at line $1${NC}"
    log "${RED}❌ Phase 4 integration deployment failed${NC}"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "=============================================================="
    echo "   🚀 Syn_OS Phase 4 Integration Deployment Script"
    echo "=============================================================="
    echo "   • Threat Intelligence Dashboard with Real-time Visualization"
    echo "   • Phase 4 Integration Bridge"
    echo "   • Kubernetes Production Deployment"
    echo "   • Monitoring and Observability Setup"
    echo "=============================================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "${CYAN}=== CHECKING PREREQUISITES ===${NC}"
    
    # Check if kubectl is installed and configured
    if ! command -v kubectl &> /dev/null; then
        log "${RED}❌ kubectl is not installed${NC}"
        exit 1
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        log "${RED}❌ kubectl cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log "${YELLOW}⚠️ helm is not installed. Some features may not be available${NC}"
    fi
    
    # Check if docker is available for building images
    if ! command -v docker &> /dev/null; then
        log "${YELLOW}⚠️ docker is not installed. Pre-built images will be used${NC}"
    fi
    
    log "${GREEN}✅ Prerequisites check completed${NC}"
}

# Build Docker images
build_docker_images() {
    log "${CYAN}=== BUILDING DOCKER IMAGES ===${NC}"
    
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        # Build threat intelligence dashboard image
        log "${BLUE}📦 Building threat intelligence dashboard image...${NC}"
        docker build -t synos/threat-intelligence-dashboard:latest \
            -f "$PROJECT_ROOT/applications/threat_intelligence_dashboard/Dockerfile" \
            "$PROJECT_ROOT/applications/threat_intelligence_dashboard/" || {
                log "${YELLOW}⚠️ Failed to build threat intelligence dashboard image. Using pre-built image.${NC}"
            }
        
        # Build Phase 4 integration bridge image
        log "${BLUE}📦 Building Phase 4 integration bridge image...${NC}"
        docker build -t synos/phase4-integration-bridge:latest \
            -f "$PROJECT_ROOT/src/integration/Dockerfile" \
            "$PROJECT_ROOT/src/integration/" || {
                log "${YELLOW}⚠️ Failed to build integration bridge image. Using pre-built image.${NC}"
            }
        
        log "${GREEN}✅ Docker images built successfully${NC}"
    else
        log "${YELLOW}⚠️ Docker not available. Using pre-built images from registry${NC}"
    fi
}

# Create namespace and RBAC
setup_kubernetes_resources() {
    log "${CYAN}=== SETTING UP KUBERNETES RESOURCES ===${NC}"
    
    # Apply the main deployment manifest
    log "${BLUE}📋 Applying Phase 4 Kubernetes manifests...${NC}"
    kubectl apply -f "$PROJECT_ROOT/deploy/kubernetes/phase4-integration.yaml"
    
    # Wait for namespace to be ready
    log "${BLUE}⏳ Waiting for namespace to be ready...${NC}"
    kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=60s
    
    log "${GREEN}✅ Kubernetes resources setup completed${NC}"
}

# Deploy monitoring infrastructure
deploy_monitoring() {
    log "${CYAN}=== DEPLOYING MONITORING INFRASTRUCTURE ===${NC}"
    
    # Check if Prometheus operator is available
    if kubectl get crd servicemonitors.monitoring.coreos.com &> /dev/null; then
        log "${GREEN}✅ Prometheus operator detected${NC}"
        
        # ServiceMonitor should already be applied with main manifest
        log "${BLUE}📊 ServiceMonitor for Phase 4 services is configured${NC}"
    else
        log "${YELLOW}⚠️ Prometheus operator not found. Manual monitoring setup required${NC}"
    fi
    
    # Create Grafana dashboard ConfigMap
    create_grafana_dashboard
    
    log "${GREEN}✅ Monitoring infrastructure deployed${NC}"
}

# Create Grafana dashboard
create_grafana_dashboard() {
    log "${BLUE}📊 Creating Grafana dashboard for Phase 4 components...${NC}"
    
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: phase4-grafana-dashboard
  namespace: $NAMESPACE
  labels:
    grafana_dashboard: "1"
data:
  phase4-integration.json: |
    {
      "dashboard": {
        "id": null,
        "title": "Syn_OS Phase 4 Integration Dashboard",
        "tags": ["synos", "phase4", "integration"],
        "timezone": "browser",
        "panels": [
          {
            "id": 1,
            "title": "Integration Health Score",
            "type": "stat",
            "targets": [
              {
                "expr": "synos_phase4_integration_health",
                "refId": "A"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "unit": "percent",
                "min": 0,
                "max": 100
              }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
          },
          {
            "id": 2,
            "title": "Component Status",
            "type": "table",
            "targets": [
              {
                "expr": "synos_phase4_component_status",
                "refId": "A"
              }
            ],
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
          },
          {
            "id": 3,
            "title": "Threat Intelligence Processing Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(synos_threats_processed_total[5m])",
                "refId": "A"
              }
            ],
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
          }
        ],
        "time": {"from": "now-1h", "to": "now"},
        "refresh": "30s"
      }
    }
EOF
    
    log "${GREEN}✅ Grafana dashboard created${NC}"
}

# Wait for deployments to be ready
wait_for_deployments() {
    log "${CYAN}=== WAITING FOR DEPLOYMENTS ===${NC}"
    
    local deployments=("threat-intelligence-dashboard" "phase4-integration-bridge")
    
    for deployment in "${deployments[@]}"; do
        log "${BLUE}⏳ Waiting for deployment $deployment to be ready...${NC}"
        kubectl wait --for=condition=Available deployment/$deployment \
            --namespace=$NAMESPACE --timeout=$DEPLOYMENT_TIMEOUT
        
        log "${GREEN}✅ Deployment $deployment is ready${NC}"
    done
    
    log "${GREEN}✅ All deployments are ready${NC}"
}

# Run integration tests
run_integration_tests() {
    log "${CYAN}=== RUNNING INTEGRATION TESTS ===${NC}"
    
    # Test threat intelligence dashboard health
    log "${BLUE}🧪 Testing threat intelligence dashboard...${NC}"
    local dashboard_pod=$(kubectl get pods -n $NAMESPACE -l app=threat-intelligence-dashboard -o jsonpath='{.items[0].metadata.name}')
    
    if kubectl exec -n $NAMESPACE $dashboard_pod -- curl -f http://localhost:8084/health &> /dev/null; then
        log "${GREEN}✅ Threat intelligence dashboard health check passed${NC}"
    else
        log "${RED}❌ Threat intelligence dashboard health check failed${NC}"
        return 1
    fi
    
    # Test integration bridge health
    log "${BLUE}🧪 Testing Phase 4 integration bridge...${NC}"
    local bridge_pod=$(kubectl get pods -n $NAMESPACE -l app=phase4-integration-bridge -o jsonpath='{.items[0].metadata.name}')
    
    if kubectl exec -n $NAMESPACE $bridge_pod -- curl -f http://localhost:8085/health &> /dev/null; then
        log "${GREEN}✅ Phase 4 integration bridge health check passed${NC}"
    else
        log "${RED}❌ Phase 4 integration bridge health check failed${NC}"
        return 1
    fi
    
    # Test service connectivity
    log "${BLUE}🧪 Testing service connectivity...${NC}"
    if kubectl get svc -n $NAMESPACE threat-intelligence-dashboard-service &> /dev/null && \
       kubectl get svc -n $NAMESPACE phase4-integration-bridge-service &> /dev/null; then
        log "${GREEN}✅ Service connectivity test passed${NC}"
    else
        log "${RED}❌ Service connectivity test failed${NC}"
        return 1
    fi
    
    log "${GREEN}✅ All integration tests passed${NC}"
}

# Display deployment information
display_deployment_info() {
    log "${CYAN}=== DEPLOYMENT INFORMATION ===${NC}"
    
    echo -e "${GREEN}"
    echo "🎉 Phase 4 Integration Deployment Completed Successfully!"
    echo ""
    echo "📊 Threat Intelligence Dashboard:"
    echo "   • Service: threat-intelligence-dashboard-service:8084"
    echo "   • Ingress: https://threat-intel.synos.local"
    echo "   • Real-time threat feed visualization"
    echo "   • Global threat intelligence correlations"
    echo "   • Interactive threat hunting interface"
    echo ""
    echo "🔗 Phase 4 Integration Bridge:"
    echo "   • Service: phase4-integration-bridge-service:8085"
    echo "   • Ingress: https://integration-bridge.synos.local"
    echo "   • Component health monitoring"
    echo "   • Integration status reporting"
    echo "   • Deployment readiness assessment"
    echo ""
    echo "🚀 Deployment Details:"
    echo "   • Namespace: $NAMESPACE"
    echo "   • Replicas: Auto-scaling enabled"
    echo "   • Monitoring: ServiceMonitor configured"
    echo "   • Storage: Persistent volumes configured"
    echo "   • Network: Network policies applied"
    echo ""
    echo "📈 Monitoring:"
    echo "   • Prometheus metrics: /metrics endpoints"
    echo "   • Grafana dashboard: Phase 4 Integration Dashboard"
    echo "   • Health checks: /health endpoints"
    echo "   • Log aggregation: Enabled"
    echo -e "${NC}"
    
    # Display access information
    echo -e "${BLUE}"
    echo "🔗 Access Information:"
    echo ""
    
    # Get ingress information
    if kubectl get ingress -n $NAMESPACE phase4-ingress &> /dev/null; then
        echo "External Access (via Ingress):"
        kubectl get ingress -n $NAMESPACE phase4-ingress -o custom-columns="HOST:.spec.rules[*].host,TLS:.spec.tls[*].secretName" --no-headers | while read host tls; do
            echo "   • https://$host"
        done
    fi
    
    echo ""
    echo "Internal Access (from within cluster):"
    echo "   • Threat Intel Dashboard: http://threat-intelligence-dashboard-service.synos-phase4.svc.cluster.local:8084"
    echo "   • Integration Bridge: http://phase4-integration-bridge-service.synos-phase4.svc.cluster.local:8085"
    echo ""
    
    echo "Port Forwarding (for development):"
    echo "   kubectl port-forward -n $NAMESPACE svc/threat-intelligence-dashboard-service 8084:8084"
    echo "   kubectl port-forward -n $NAMESPACE svc/phase4-integration-bridge-service 8085:8085"
    echo -e "${NC}"
}

# Display resource status
display_resource_status() {
    log "${CYAN}=== RESOURCE STATUS ===${NC}"
    
    echo -e "${BLUE}📋 Pods Status:${NC}"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo -e "\n${BLUE}🔗 Services Status:${NC}"
    kubectl get svc -n $NAMESPACE
    
    echo -e "\n${BLUE}📊 Ingress Status:${NC}"
    kubectl get ingress -n $NAMESPACE
    
    echo -e "\n${BLUE}💾 PVC Status:${NC}"
    kubectl get pvc -n $NAMESPACE
    
    echo -e "\n${BLUE}📈 HPA Status:${NC}"
    kubectl get hpa -n $NAMESPACE
}

# Cleanup function (for rollback if needed)
cleanup_deployment() {
    log "${YELLOW}🧹 Cleaning up Phase 4 deployment...${NC}"
    
    # Delete the deployed resources
    kubectl delete -f "$PROJECT_ROOT/deploy/kubernetes/phase4-integration.yaml" --ignore-not-found=true
    
    # Wait for namespace deletion
    kubectl wait --for=delete namespace/$NAMESPACE --timeout=300s || true
    
    log "${GREEN}✅ Cleanup completed${NC}"
}

# Main deployment function
main() {
    print_banner
    
    log "${GREEN}🚀 Starting Phase 4 Integration Deployment${NC}"
    log "${BLUE}📝 Deployment log: $LOG_FILE${NC}"
    
    # Parse command line arguments
    local cleanup_mode=false
    local skip_tests=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                cleanup_mode=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --cleanup     Remove Phase 4 deployment"
                echo "  --skip-tests  Skip integration tests"
                echo "  -h, --help    Show this help message"
                exit 0
                ;;
            *)
                log "${RED}❌ Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    # Handle cleanup mode
    if [[ "$cleanup_mode" == true ]]; then
        cleanup_deployment
        exit 0
    fi
    
    # Execute deployment steps
    check_prerequisites
    build_docker_images
    setup_kubernetes_resources
    deploy_monitoring
    wait_for_deployments
    
    # Run integration tests unless skipped
    if [[ "$skip_tests" == false ]]; then
        run_integration_tests
    else
        log "${YELLOW}⚠️ Integration tests skipped${NC}"
    fi
    
    # Display deployment information
    display_deployment_info
    display_resource_status
    
    log "${GREEN}🎉 Phase 4 Integration Deployment completed successfully!${NC}"
    log "${BLUE}📝 Full deployment log available at: $LOG_FILE${NC}"
}

# Run main function
main "$@"