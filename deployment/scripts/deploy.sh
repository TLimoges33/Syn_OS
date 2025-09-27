#!/bin/bash
set -e

echo "🚀 Deploying SynapticOS to Kubernetes..."

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

# Create namespace if it doesn't exist
kubectl create namespace synapticos-prod --dry-run=client -o yaml | kubectl apply -f -

# Add required Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Deploy the Helm chart
echo "⚓ Deploying Helm chart..."
helm upgrade --install synapticos ./deploy/helm/synapticos \
    --namespace synapticos-prod \
    --create-namespace \
    --wait \
    --timeout=10m

# Check deployment status
echo "✅ Checking deployment status..."
kubectl get pods -n synapticos-prod
kubectl get services -n synapticos-prod
kubectl get ingress -n synapticos-prod

echo "🎉 SynapticOS deployment completed!"
echo "🌐 Access the dashboard at: https://dashboard.synapticos.io"
