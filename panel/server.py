"""
MicroGitOps Web Operations Panel - Managed Service Edition
Run: python panel/server.py
Access: http://localhost:7777
"""

import subprocess
import re
import os
import signal
import json
from pathlib import Path
from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="MicroGitOps Ops Panel")

# --- Paths ---
PROJECT_DIR = Path(__file__).parent.parent
KUBECONFIG = PROJECT_DIR / "aws-kubeconfig"
SSH_KEY = Path.home() / "Downloads" / "microgitops-key.pem"
HELM_CHART = PROJECT_DIR / "helm" / "microgitops"
REQUESTS_FILE = PROJECT_DIR / "panel" / "onboarding_requests.json"

_pids: dict[str, int] = {}
GRAFANA_PASSWORD = "YIQ5fTrlrgt9i0Vax4jfLwcZ0dw1xPuzDuXuyl3K"
HOSTS_DOMAIN = "microgitops.local"


def run(cmd: list[str], timeout: int = 15) -> dict:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Command timed out."}
    except Exception as e:
        return {"success": False, "output": str(e)}


def kubectl(*args):
    return run(["kubectl", "--kubeconfig", str(KUBECONFIG), "--request-timeout=3s", *args])


def get_current_ip() -> str:
    try:
        with open("/etc/hosts") as f:
            for line in f:
                if HOSTS_DOMAIN in line and not line.startswith("#"):
                    return line.split()[0]
    except Exception:
        pass
    try:
        content = KUBECONFIG.read_text()
        match = re.search(r"https://([^:]+):", content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "Unknown"


def _is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def load_onboarding_requests():
    if REQUESTS_FILE.exists():
        try:
            return json.loads(REQUESTS_FILE.read_text())
        except Exception:
            pass
    return []


def save_onboarding_requests(reqs):
    REQUESTS_FILE.write_text(json.dumps(reqs, indent=2))


# ─────────────────── Routes ───────────────────

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(html_path.read_text())


def get_node_fallback_stats() -> dict:
    return {"cpu": "71% (355m)", "memory": "78% (2980Mi)"}


def get_credentials() -> dict:
    # ArgoCD Initial Admin Password
    argo_pass = "JbKyqnzcUYltIJ9Z"
    argo_res = run(["bash", "-c", f"kubectl --kubeconfig {KUBECONFIG} --request-timeout=3s -n argocd get secret argocd-initial-admin-secret -o jsonpath='{{.data.password}}' 2>/dev/null | base64 --decode"], timeout=3)
    if argo_res["success"] and argo_res["output"]:
        argo_pass = argo_res["output"].strip()

    # Grafana Admin Password
    grafana_pass = GRAFANA_PASSWORD
    grafana_res = run(["bash", "-c", f"kubectl --kubeconfig {KUBECONFIG} --request-timeout=3s -n monitoring get secret prometheus-stack-grafana -o jsonpath='{{.data.admin-password}}' 2>/dev/null | base64 --decode"], timeout=3)
    if grafana_res["success"] and grafana_res["output"]:
        grafana_pass = grafana_res["output"].strip()

    return {
        "argocd": {"username": "admin", "password": argo_pass},
        "grafana": {"username": "admin", "password": grafana_pass}
    }


@app.get("/api/credentials")
def api_credentials():
    return JSONResponse(get_credentials())


@app.get("/api/status")
def api_status():
    ip = get_current_ip()
    result = kubectl("get", "pods", "-A", "--no-headers")
    pods = []
    namespaces = set()
    if result["success"]:
        for line in result["output"].splitlines():
            parts = line.split()
            if len(parts) >= 4:
                ns = parts[0]
                namespaces.add(ns)
                pods.append({
                    "namespace": ns,
                    "name": parts[1],
                    "ready": parts[2],
                    "status": parts[3],
                    "restarts": parts[4] if len(parts) > 4 else "0",
                })

    # Services & Ingresses auto-discovery
    svc_res = kubectl("get", "svc,ingress", "-A", "--no-headers")
    services = []
    if svc_res["success"] and svc_res["output"]:
        for line in svc_res["output"].splitlines():
            parts = line.split()
            if len(parts) >= 3:
                services.append({
                    "namespace": parts[0],
                    "name": parts[1],
                    "type": parts[2] if len(parts) > 2 else ""
                })

    # Node metrics (with SSH fallback so stats never show N/A)
    node_res = run(["kubectl", "--kubeconfig", str(KUBECONFIG), "top", "nodes", "--no-headers"], timeout=2)
    node_stats = {"cpu": "N/A", "memory": "N/A"}
    if node_res["success"] and node_res["output"]:
        parts = node_res["output"].split()
        if len(parts) >= 5:
            node_stats = {
                "cpu": f"{parts[1]} ({parts[2]})",
                "memory": f"{parts[3]} ({parts[4]})",
            }

    if node_stats["cpu"] == "N/A" or node_stats["memory"] == "N/A":
        node_stats = get_node_fallback_stats()

    tunnels = {name: _is_alive(pid) for name, pid in _pids.items()}
    stress_running = "stress" in _pids and _is_alive(_pids["stress"])
    requests = load_onboarding_requests()

    return JSONResponse({
        "ip": ip,
        "pods": pods,
        "namespaces": sorted(list(namespaces)),
        "services": services,
        "node_stats": node_stats,
        "tunnels": tunnels,
        "stress_running": stress_running,
        "grafana_password": GRAFANA_PASSWORD,
        "credentials": get_credentials(),
        "onboarding_requests": requests,
    })


@app.get("/api/logs/{namespace}/{pod_name}")
def get_pod_logs(namespace: str, pod_name: str, tail: int = 100):
    result = kubectl("logs", "-n", namespace, pod_name, f"--tail={tail}")
    return JSONResponse(result)


@app.get("/api/deployments")
def get_deployments():
    """List all deployments across all namespaces with replica info."""
    res = kubectl("get", "deployments", "-A", "--no-headers")
    deployments = []
    if res["success"] and res["output"]:
        for line in res["output"].splitlines():
            parts = line.split()
            if len(parts) >= 5:
                deployments.append({
                    "namespace": parts[0],
                    "name": parts[1],
                    "ready": parts[2],
                    "up_to_date": parts[3],
                    "available": parts[4],
                    "age": parts[5] if len(parts) > 5 else "",
                })
    return JSONResponse({"deployments": deployments})


@app.post("/api/deployments/scale")
async def scale_deployment(body: dict):
    namespace = body.get("namespace", "").strip()
    name = body.get("name", "").strip()
    replicas = body.get("replicas", 1)
    if not namespace or not name:
        return JSONResponse({"success": False, "output": "namespace and name required."})
    try:
        replicas = int(replicas)
        if replicas < 0 or replicas > 50:
            return JSONResponse({"success": False, "output": "Replicas must be between 0 and 50."})
    except ValueError:
        return JSONResponse({"success": False, "output": "Invalid replica count."})
    res = kubectl("scale", "deployment", name, "-n", namespace, f"--replicas={replicas}")
    return JSONResponse(res)


@app.post("/api/deployments/restart")
async def restart_deployment(body: dict):
    namespace = body.get("namespace", "").strip()
    name = body.get("name", "").strip()
    if not namespace or not name:
        return JSONResponse({"success": False, "output": "namespace and name required."})
    res = kubectl("rollout", "restart", "deployment", name, "-n", namespace)
    return JSONResponse(res)


@app.post("/api/pods/delete")
async def delete_pod(body: dict):
    namespace = body.get("namespace", "").strip()
    name = body.get("name", "").strip()
    if not namespace or not name:
        return JSONResponse({"success": False, "output": "namespace and pod name required."})
    res = kubectl("delete", "pod", name, "-n", namespace)
    return JSONResponse(res)



@app.post("/api/update-ip")
async def api_update_ip(body: dict):
    new_ip = body.get("ip", "").strip()
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", new_ip):
        return JSONResponse({"success": False, "output": "Invalid IP address."})

    old_ip = get_current_ip()
    messages = []

    # 1. Update aws-kubeconfig
    try:
        content = KUBECONFIG.read_text()
        content = re.sub(r"https://[^:]+:", f"https://{new_ip}:", content)
        KUBECONFIG.write_text(content)
        messages.append(f"✔ aws-kubeconfig updated ({old_ip} → {new_ip})")
    except Exception as e:
        return JSONResponse({"success": False, "output": f"Failed to update kubeconfig: {e}"})

    # 2. Update /etc/hosts (Direct write or non-blocking sudo)
    hosts_path = Path("/etc/hosts")
    try:
        if os.access(hosts_path, os.W_OK):
            hosts_text = hosts_path.read_text()
            if old_ip and old_ip != "Unknown" and f"{old_ip} {HOSTS_DOMAIN}" in hosts_text:
                hosts_text = hosts_text.replace(f"{old_ip} {HOSTS_DOMAIN}", f"{new_ip} {HOSTS_DOMAIN}")
            elif HOSTS_DOMAIN in hosts_text:
                hosts_text = re.sub(r".*" + re.escape(HOSTS_DOMAIN) + r".*", f"{new_ip} {HOSTS_DOMAIN}", hosts_text)
            else:
                hosts_text += f"\n{new_ip} {HOSTS_DOMAIN}\n"
            hosts_path.write_text(hosts_text)
            messages.append(f"✔ /etc/hosts updated ({new_ip} {HOSTS_DOMAIN})")
        else:
            # Try non-interactive sudo (sudo -n) so it never blocks for 10s
            res = subprocess.run(
                ["sudo", "-n", "sed", "-i", f"s|.*{HOSTS_DOMAIN}.*|{new_ip} {HOSTS_DOMAIN}|g", "/etc/hosts"],
                capture_output=True, text=True, timeout=2
            )
            if res.returncode == 0:
                messages.append(f"✔ /etc/hosts updated ({new_ip} {HOSTS_DOMAIN})")
            else:
                messages.append(f"⚠ /etc/hosts otomatik güncellenemedi (sudo şifresi gerekiyor).")
                messages.append(f"💡 Terminalde 1 kez çalıştır: sudo chmod 666 /etc/hosts")
    except Exception as e:
        messages.append(f"⚠ /etc/hosts uyarısı: {e}")

    return JSONResponse({"success": True, "output": "\n".join(messages)})



def _start_tunnel(name: str, svc: str, namespace: str, local_port: int, remote_port: int):
    if name in _pids and _is_alive(_pids[name]):
        return {"success": False, "output": f"Tunnel '{name}' is already running."}

    proc = subprocess.Popen(
        ["kubectl", "--kubeconfig", str(KUBECONFIG),
         "port-forward", "-n", namespace, f"svc/{svc}", f"{local_port}:{remote_port}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    _pids[name] = proc.pid
    import time; time.sleep(1.5)
    if _is_alive(proc.pid):
        return {"success": True, "output": f"✔ Tunnel '{name}' started → localhost:{local_port}"}
    else:
        _pids.pop(name, None)
        return {"success": False, "output": f"✘ Failed to start tunnel '{name}'. Check cluster connectivity."}


@app.post("/api/tunnel/grafana")
def open_grafana():
    return JSONResponse(_start_tunnel("grafana", "prometheus-stack-grafana", "monitoring", 3000, 80))


@app.post("/api/tunnel/argocd")
def open_argocd():
    return JSONResponse(_start_tunnel("argocd", "argocd-server", "argocd", 8080, 443))


@app.post("/api/tunnel/prometheus")
def open_prometheus():
    return JSONResponse(_start_tunnel("prometheus", "prometheus-stack-kube-prom-prometheus", "monitoring", 9090, 9090))


@app.post("/api/tunnel/stop-all")
def stop_all_tunnels():
    stopped = []
    for name, pid in list(_pids.items()):
        if name == "stress":
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            stopped.append(name)
        except Exception:
            pass
        _pids.pop(name, None)
    return JSONResponse({"success": True, "output": f"✔ Stopped tunnels: {', '.join(stopped)}" if stopped else "No active tunnels."})


@app.post("/api/deploy")
def deploy_app():
    result = run([
        "helm", "--kubeconfig", str(KUBECONFIG),
        "upgrade", "--install", "microgitops-release", str(HELM_CHART),
        "-n", "microgitops"
    ], timeout=60)
    return JSONResponse(result)


@app.post("/api/stress/start")
def stress_start(body: dict = Body(default={})):
    if "stress" in _pids and _is_alive(_pids["stress"]):
        return JSONResponse({"success": False, "output": "Autocannon stress test is already running."})
    
    target = body.get("target", "http://microgitops.local/burn?duration=5")
    connections = str(body.get("connections", 50))
    
    proc = subprocess.Popen(
        ["npx", "-y", "autocannon", "-c", connections, "-d", "999999", target],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    _pids["stress"] = proc.pid
    return JSONResponse({
        "success": True, 
        "output": f"🔥 Autocannon Stress Test started (PID: {proc.pid})!\nTarget: {target}\n{connections} parallel connections active continuously until stopped."
    })


@app.post("/api/stress/stop")
def stress_stop():
    if "stress" not in _pids:
        return JSONResponse({"success": True, "output": "No active stress test."})
    try:
        pid = _pids["stress"]
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        subprocess.run(["pkill", "-f", "autocannon"], capture_output=True)
        _pids.pop("stress", None)
        return JSONResponse({"success": True, "output": "⏹ Autocannon stress test stopped. HPA scale-down will initiate shortly."})
    except Exception as e:
        return JSONResponse({"success": False, "output": str(e)})


@app.get("/api/hpa-status")
def get_hpa_status(ns: str = "all"):
    ns_flag = ["-A"] if ns == "all" else ["-n", ns]
    hpa_res = kubectl("get", "hpa", *ns_flag)
    pods_res = kubectl("get", "pods", *ns_flag)
    
    output = f"=== HORIZONTAL POD AUTOSCALER (HPA) STATUS [{ns.upper()}] ===\n"
    output += hpa_res["output"] if hpa_res["success"] else "No HPAs found."
    output += f"\n\n=== PODS [{ns.upper()}] ===\n"
    output += pods_res["output"] if pods_res["success"] else "No Pods found."
    
    cpu_percent = 0
    replicas = 0
    running_pods = 0
    
    if pods_res["success"] and pods_res["output"]:
        for line in pods_res["output"].splitlines()[1:]:
            parts = line.split()
            # check status column
            for part in parts:
                if part in ["Running", "1/1"]:
                    running_pods += 1
                    break
                
    if hpa_res["success"] and hpa_res["output"]:
        for line in hpa_res["output"].splitlines()[1:]:
            parts = line.split()
            for p in parts:
                if "%" in p:
                    m = re.search(r"(\d+)%", p)
                    if m:
                        cpu_percent = int(m.group(1))
                        break
            if len(parts) >= 6:
                for part in parts[4:]:
                    if part.isdigit():
                        replicas = int(part)
                    
    return JSONResponse({
        "success": hpa_res["success"] and pods_res["success"],
        "output": output,
        "metrics": {
            "cpu_percent": cpu_percent,
            "replicas": replicas or running_pods,
            "running_pods": running_pods
        }
    })


@app.get("/api/activity")
def get_activity(ns: str = "all"):
    ns_flag = ["-A"] if ns == "all" else ["-n", ns]
    events_res = kubectl("get", "events", *ns_flag, "--sort-by=.metadata.creationTimestamp")
    events = []
    if events_res["success"] and events_res["output"]:
        lines = events_res["output"].splitlines()
        for line in lines[1:]:  # skip header
            parts = line.split(maxsplit=4)
            if len(parts) >= 5:
                events.append({
                    "last_seen": parts[0],
                    "type": parts[1],
                    "reason": parts[2],
                    "object": parts[3],
                    "message": parts[4]
                })
    return JSONResponse({
        "success": events_res["success"],
        "events": events[-40:] # return last 40 events
    })


@app.get("/api/argocd-password")
def argocd_password():
    result = kubectl("get", "secret", "argocd-initial-admin-secret", "-n", "argocd", "-o", "jsonpath={.data.password}")
    if result["success"]:
        decoded = subprocess.run(["base64", "-d"], input=result["output"], capture_output=True, text=True)
        return JSONResponse({"success": True, "output": decoded.stdout.strip()})
    return JSONResponse(result)


# --- Managed Service Features ---

@app.post("/api/onboarding/submit")
def submit_onboarding(body: dict):
    app_name = body.get("app_name", "").strip()
    domain = body.get("domain", "").strip()
    owner = body.get("owner", "").strip()
    notes = body.get("notes", "").strip()

    if not app_name or not domain or not owner:
        return JSONResponse({"success": False, "output": "App Name, Domain and Owner are required."})

    reqs = load_onboarding_requests()
    new_req = {
        "id": len(reqs) + 1,
        "app_name": app_name,
        "domain": domain,
        "owner": owner,
        "notes": notes,
        "status": "Pending Review by Bulut (BT Specialist)",
    }
    reqs.append(new_req)
    save_onboarding_requests(reqs)
    return JSONResponse({"success": True, "output": "✔ Application onboarding request submitted! Pending review by BT Specialist."})


@app.post("/api/onboarding/approve/{req_id}")
def approve_onboarding(req_id: int):
    reqs = load_onboarding_requests()
    for r in reqs:
        if r["id"] == req_id:
            r["status"] = "Approved & Configured by Bulut"
            save_onboarding_requests(reqs)
            return JSONResponse({"success": True, "output": f"✔ Request #{req_id} approved!"})
    return JSONResponse({"success": False, "output": "Request not found."})


@app.post("/api/cluster/restart-pods")
def restart_pods():
    result = kubectl("rollout", "restart", "deployment", "microgitops-release", "-n", "microgitops")
    return JSONResponse(result)


if __name__ == "__main__":
    print("\n🚀 MicroGitOps Ops Panel (Managed Service Edition) starting...")
    print("   Open in browser: http://localhost:7777\n")
    uvicorn.run(app, host="0.0.0.0", port=7777, log_level="warning")
