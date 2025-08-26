#!/bin/bash
set -e

echo "🗑️ Uninstalling SynapticOS from Kubernetes..."

# Uninstall Helm release
helm uninstall synapticos --namespace synapticos-prod

# Optional: Delete namespace (uncomment if desired)
# kubectl delete namespace synapticos-prod

echo "✅ SynapticOS uninstalled successfully!"
