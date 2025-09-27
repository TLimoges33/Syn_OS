#!/bin/bash
set -e

echo "🚀 Deploying SynOS to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed or not in PATH"
    exit 1
fi

# Parse command line arguments
ENVIRONMENT=${1:-production}
NAMESPACE="syn-os-${ENVIRONMENT}"
CHART_PATH="./helm/syn-os"

echo "📋 Deployment Configuration:"
echo "   Environment: ${ENVIRONMENT}"
echo "   Namespace: ${NAMESPACE}"
echo "   Chart: ${CHART_PATH}"

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Add required Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update

# Deploy the Helm chart
echo "⚓ Deploying Helm chart..."
helm upgrade --install "syn-os-${ENVIRONMENT}" "${CHART_PATH}" \
    --namespace "${NAMESPACE}" \
    --create-namespace \
    --set environment="${ENVIRONMENT}" \
    --set namespace="${NAMESPACE}" \
    --values "${CHART_PATH}/values.yaml" \
    --wait \
    --timeout=600s

# Check deployment status
echo "🔍 Checking deployment status..."
kubectl rollout status deployment/syn-os-${ENVIRONMENT}-core -n "${NAMESPACE}"

if kubectl get deployment syn-os-${ENVIRONMENT}-security -n "${NAMESPACE}-security" &>/dev/null; then
    kubectl rollout status deployment/syn-os-${ENVIRONMENT}-security -n "${NAMESPACE}-security"
fi

echo "✅ Deployment completed successfully!"

# Display service information
echo ""
echo "📋 Service Information:"
kubectl get services -n "${NAMESPACE}" -l app.kubernetes.io/instance="syn-os-${ENVIRONMENT}"

if kubectl get namespace "${NAMESPACE}-security" &>/dev/null; then
    kubectl get services -n "${NAMESPACE}-security" -l app.kubernetes.io/instance="syn-os-${ENVIRONMENT}"
fi

echo ""
echo "🎯 Access Information:"
echo "   Core Service: kubectl port-forward svc/syn-os-${ENVIRONMENT}-core 8080:8080 -n ${NAMESPACE}"
echo "   Security Service: kubectl port-forward svc/syn-os-${ENVIRONMENT}-security 8443:8443 -n ${NAMESPACE}-security"
echo ""
echo "🔍 Monitor logs:"
echo "   Core: kubectl logs -f deployment/syn-os-${ENVIRONMENT}-core -n ${NAMESPACE}"
echo "   Security: kubectl logs -f deployment/syn-os-${ENVIRONMENT}-security -n ${NAMESPACE}-security"
    --wait \
    --timeout=10m

# Check deployment status
echo "✅ Checking deployment status..."
kubectl get pods -n synapticos-prod
kubectl get services -n synapticos-prod
kubectl get ingress -n synapticos-prod

echo "🎉 SynapticOS deployment completed!"
echo "🌐 Access the dashboard at: https://dashboard.synapticos.io"
