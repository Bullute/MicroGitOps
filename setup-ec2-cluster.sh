#!/usr/bin/env bash
# ⚡ MicroGitOps — One-Click AWS EC2 K3s & ArgoCD Auto-Provisioner

set -e

echo "🚀 Starting MicroGitOps AWS Cluster Setup..."

# 1. Install K3s (Lightweight Kubernetes)
if ! command -v k3s &> /dev/null; then
    echo "📦 Installing K3s..."
    curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
else
    echo "✅ K3s is already installed."
fi

# Set KUBECONFIG
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2. Wait for Kubernetes Node to be Ready
echo "⏳ Waiting for Kubernetes Node to become Ready..."
kubectl wait --for=condition=Ready node --all --timeout=90s

# 3. Install ArgoCD
echo "📦 Installing ArgoCD in namespace 'argocd'..."
kubectl create namespace argocd 2>/dev/null || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "⏳ Waiting for ArgoCD Server to start..."
kubectl rollout status deployment/argocd-server -n argocd --timeout=180s || true

# 4. Deploy MicroGitOps Application via ArgoCD
echo "🚀 Deploying MicroGitOps App (GitOps Auto-Sync)..."
kubectl apply -f https://raw.githubusercontent.com/Bullute/MicroGitOps/master/argocd-app.yaml

echo ""
echo "========================================================"
echo "🎉 MicroGitOps Cluster Successfully Provisioned!"
echo "========================================================"
echo "📌 Check Application Status:"
echo "   kubectl get app -n argocd"
echo "   kubectl get pods -n microgitops"
echo ""
echo "📌 Initial ArgoCD Password:"
echo "   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d && echo"
echo "========================================================"
