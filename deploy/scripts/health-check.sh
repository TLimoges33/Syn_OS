#!/bin/bash

echo "🏥 SynapticOS Health Check..."

NAMESPACE="synapticos-prod"

# Check if namespace exists
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "❌ Namespace $NAMESPACE does not exist"
    exit 1
fi

# Check pod status
echo "📋 Pod Status:"
kubectl get pods -n $NAMESPACE

# Check service status
echo "🔗 Service Status:"
kubectl get services -n $NAMESPACE

# Check ingress status
echo "🌐 Ingress Status:"
kubectl get ingress -n $NAMESPACE

# Check HPA status
echo "📈 Auto-scaling Status:"
kubectl get hpa -n $NAMESPACE

# Check resource usage
echo "💾 Resource Usage:"
kubectl top pods -n $NAMESPACE

echo "✅ Health check completed!"
