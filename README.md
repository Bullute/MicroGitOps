# 🚀 MicroGitOps Platform: Cloud-Native DevOps & GitOps Architecture

A production-grade, hardened, and highly observable GitOps deployment platform designed to package, secure, deploy, and monitor scalable APIs on AWS EC2 nodes orchestrating on lightweight Kubernetes (K3s).

This project demonstrates modern DevSecOps, Infrastructure-as-Code (IaC), GitOps, and Site Reliability Engineering (SRE) principles in action.

---

## 🏗️ System Architecture & Workflow

The platform spans from local development, to continuous quality checks, automated GitOps delivery, and final server-health monitoring in the AWS cloud. Below is the Mermaid-rendered model (natively supported by GitHub):

```mermaid
graph TD
    %% Section 1: Dev
    subgraph Developer Laptop [1. Local Development]
        A[FastAPI App: main.py] -->|Package Blueprint| B[Dockerfile: Multi-stage]
    end

    %% Section 2: CI/CD
    subgraph pipeline [2. Quality Control & GitOps]
        C[Git Push] -->|Triggers CI| D[GitHub Actions]
        D -->|Linting| E[Ruff Linter]
        D -->|Vulnerability Check| F[Trivy Scanner]
        D -->|Compile & Publish| G[Docker Registry / Local Import]
        G -->|Sync Manifests| H[ArgoCD / Helm Chart]
    end

    %% Section 3: AWS
    subgraph aws [3. AWS Cloud Environment / K3s K8s]
        I[Traefik Ingress: Port 80 / DNS] -->|Routes traffic| J[App Service: Load Balancer]
        J -->|Round-Robin| K[Pod 1: FastAPI container]
        J -->|Round-Robin| L[Pod 2: FastAPI container]
        
        M[Prometheus Scraper] -->|Pulls API Metrics /metrics| K
        M -->|Pulls Host stats| N[cAdvisor / Node Exporter]
        O[Grafana Dashboard] -->|Visualizes data| M
    end

    B --> C
    H -->|Auto Deploy / Sync| I
```

---

## 🛡️ Core Highlights & Features

1. **Application Hardening & Telemetry:**
   * Built with **FastAPI** leveraging Prometheus middleware instrumentation (`/metrics`) and Kubernetes liveness/readiness probes (`/health`).
   * **Hardened Dockerfile:** Employing multi-stage builds (`builder` -> `runner` stages) to omit compilation compilers in production, running under non-privileged UID `10001` (non-root context) to protect host kernels.

2. **Continuous Integration (CI):**
   * Configured via **GitHub Actions** (`ci.yml`) to enforce code formatting using `Ruff` and static security scanning for CVE dependencies using `Trivy`.

3. **Infrastructure as Code (IaC):**
   * Deployed via **Terraform** defining Kubernetes namespaces, secrets, and configuration maps dynamically targeting cluster environments.

4. **Continuous Delivery (CD):**
   * Managed via **Helm Charts** defining scalable templates (Deployments, Services, Ingresses, HPA, and ServiceMonitors) synchronized automatically onto the cluster via **ArgoCD**.

5. **Site Reliability Engineering (SRE):**
   * Vertically scaled from `t3.micro` (1 GB) through `t3.small` (2 GB) to **`c7i-flex.large`** (4 GB RAM) on AWS EC2, diagnosing and resolving Out-Of-Memory (OOM) crashes at each stage.
   * Configured a **2 GB Linux Swap file** (`/swapfile`) and performed live K3s control-plane recovery under SQLite database lock contention.

---

## 📸 Platform Previews & Dashboards

Below are the live dashboard captures verifying the successful GitOps synchronization and the dynamic load testing metrics on our AWS cluster:

### 1. ArgoCD GitOps Sync Status
![ArgoCD Dashboard](./argocd-dashboard.png)

### 2. ArgoCD GitOps Card Status
![ArgoCD Dashboard](./argo_card.png)

### 3. Grafana Observability Dashboard (Under Sleep-Wave Load Test)
![Grafana Dashboard](./grafana-observability.png)

### 4. Grafana Observability HTTP Request Rate
![Grafana Dashboard](./grafana_rr.png)

### 5. Grafana Observability Average Request Latency 
![Grafana Dashboard](./grafana_arl.png)

---

## 📂 Repository Structure

```text
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI pipeline (Ruff lint & Trivy scan)
├── terraform/
│   ├── main.tf              # Terraform manifests (Namespaces, Secrets, ConfigMaps)
│   ├── providers.tf         # K8s provider bindings (AWS remote Kubeconfig target)
│   └── variables.tf         # Parameterized input variables
├── helm/microgitops/
│   ├── Chart.yaml           # Helm chart metadata
│   ├── values.yaml          # Configuration panel (replicas, CPU/RAM, ingress, HPA)
│   └── templates/           # K8s templates (deployment, service, ingress, HPA, servicemonitor)
├── grafana/
│   └── dashboard.json       # Custom Grafana dashboard JSON model
├── main.py                  # FastAPI server with Prometheus instrumentation middleware
├── Dockerfile               # Production-hardened multi-stage Docker build
├── argocd-app.yaml          # ArgoCD Application manifest for GitOps sync
├── stress_test.py           # Dynamic wave-pattern HTTP load testing utility
├── requirements.txt         # Python dependencies (FastAPI, Uvicorn, Prometheus)
└── README.md                # Project documentation
```

---

## ⚙️ How to Deploy & Verify

### 1. Local Container Verification (Docker)
Build and run the application locally to test the API endpoints:
```bash
# Build the container
docker build -t microgitops:v1 .

# Run the container mapping ports locally
docker run --rm -p 8000:8000 microgitops:v1
```
Access endpoints:
* **Home:** `http://localhost:8000/`
* **Health Check:** `http://localhost:8000/health`
* **Metrics:** `http://localhost:8000/metrics`

### 2. Infrastructure Deployment (Terraform & Helm)
Connect to the AWS K3s cluster and run:
```bash
# Apply Terraform foundations
cd terraform && terraform init && terraform apply -auto-approve

# Install Helm App Stack
cd .. && helm upgrade --install microgitops-release ./helm/microgitops -n microgitops
```

### 3. Load Testing & Monitoring Verification
Run the built-in stress test to generate dynamic traffic patterns:
```bash
python stress_test.py
```
Once targets are scraped by Prometheus, import the `grafana/dashboard.json` dashboard to view:
* HTTP Request Rates (counts/success)
* Request Duration Latencies (percentiles)
* Dynamic wave-pattern traffic visualizations
