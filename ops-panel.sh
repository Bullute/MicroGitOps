#!/bin/bash
# ==============================================================================
#  MicroGitOps Operations Control Panel
#  All-in-one management panel for the MicroGitOps platform on AWS K3s.
# ==============================================================================

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KUBECONFIG="$SCRIPT_DIR/aws-kubeconfig"
SSH_KEY="$HOME/Downloads/microgitops-key.pem"
SSH_USER="ubuntu"
HELM_CHART="$SCRIPT_DIR/helm/microgitops"
HELM_RELEASE="microgitops-release"
APP_NAMESPACE="microgitops"
HOSTS_DOMAIN="microgitops.local"
GRAFANA_PASSWORD="YIQ5fTrlrgt9i0Vax4jfLwcZ0dw1xPuzDuXuyl3K"

# PID files to track background port-forward processes
PID_DIR="/tmp/microgitops-pids"
mkdir -p "$PID_DIR"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Helper Functions ---
get_current_ip() {
    grep "$HOSTS_DOMAIN" /etc/hosts | awk '{print $1}' | head -1
}

get_kubeconfig_ip() {
    grep "server:" "$KUBECONFIG" | sed 's|.*https://||' | cut -d':' -f1
}

print_header() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "  ╔══════════════════════════════════════════════════════╗"
    echo "  ║        MicroGitOps Operations Control Panel          ║"
    echo "  ╚══════════════════════════════════════════════════════╝${NC}"
    CURRENT_IP=$(get_current_ip)
    echo -e "  ${YELLOW}AWS IP:${NC} ${CURRENT_IP:-Not configured}"
    echo ""
}

print_menu() {
    echo -e "  ${BOLD}--- Infrastructure ---${NC}"
    echo -e "  ${GREEN}1)${NC} Update AWS IP  ${YELLOW}(run this first after restarting AWS!)${NC}"
    echo -e "  ${GREEN}2)${NC} Check Cluster Status (all pods)"
    echo ""
    echo -e "  ${BOLD}--- Tunnels & Access ---${NC}"
    echo -e "  ${GREEN}3)${NC} Open Grafana Dashboard        → http://localhost:3000"
    echo -e "  ${GREEN}4)${NC} Open ArgoCD Dashboard         → https://localhost:8080"
    echo -e "  ${GREEN}5)${NC} Open Prometheus               → http://localhost:9090"
    echo -e "  ${GREEN}6)${NC} Close All Tunnels"
    echo ""
    echo -e "  ${BOLD}--- Application ---${NC}"
    echo -e "  ${GREEN}7)${NC} Deploy / Upgrade Application  (Helm upgrade)"
    echo -e "  ${GREEN}8)${NC} Start Stress Test"
    echo -e "  ${GREEN}9)${NC} Stop Stress Test"
    echo ""
    echo -e "  ${BOLD}--- Utilities ---${NC}"
    echo -e "  ${GREEN}10)${NC} SSH into AWS server"
    echo -e "  ${GREEN}11)${NC} Show ArgoCD admin password"
    echo -e "  ${GREEN}0)${NC}  Exit"
    echo ""
    echo -ne "  ${BOLD}Select option:${NC} "
}

tunnel_running() {
    local name=$1
    [ -f "$PID_DIR/$name.pid" ] && kill -0 "$(cat "$PID_DIR/$name.pid")" 2>/dev/null
}

start_tunnel() {
    local name=$1
    local svc=$2
    local ns=$3
    local local_port=$4
    local remote_port=$5

    if tunnel_running "$name"; then
        echo -e "  ${YELLOW}⚠ Tunnel '$name' is already running (PID: $(cat "$PID_DIR/$name.pid"))${NC}"
        return
    fi

    kubectl --kubeconfig="$KUBECONFIG" port-forward -n "$ns" "svc/$svc" "$local_port:$remote_port" &>/dev/null &
    echo $! > "$PID_DIR/$name.pid"
    sleep 1.5
    if tunnel_running "$name"; then
        echo -e "  ${GREEN}✔ Tunnel '$name' started → localhost:$local_port${NC}"
    else
        echo -e "  ${RED}✘ Failed to start tunnel '$name'. Is the cluster reachable?${NC}"
        rm -f "$PID_DIR/$name.pid"
    fi
}

stop_all_tunnels() {
    local stopped=0
    for pid_file in "$PID_DIR"/*.pid; do
        [ -f "$pid_file" ] || continue
        local pid
        pid=$(cat "$pid_file")
        if kill "$pid" 2>/dev/null; then
            echo -e "  ${GREEN}✔ Stopped tunnel (PID: $pid)${NC}"
            ((stopped++))
        fi
        rm -f "$pid_file"
    done
    if [ "$stopped" -eq 0 ]; then
        echo -e "  ${YELLOW}No active tunnels found.${NC}"
    fi
}

# ==============================================================================
#  MENU ACTIONS
# ==============================================================================

action_update_ip() {
    echo ""
    echo -ne "  ${BOLD}Enter new AWS public IP:${NC} "
    read -r NEW_IP

    if [[ ! "$NEW_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "  ${RED}✘ Invalid IP address. Aborting.${NC}"
        return
    fi

    OLD_IP=$(get_current_ip)

    # 1. Update aws-kubeconfig
    sed -i "s|https://$OLD_IP:|https://$NEW_IP:|g" "$KUBECONFIG"
    echo -e "  ${GREEN}✔ aws-kubeconfig updated${NC} ($OLD_IP → $NEW_IP)"

    # 2. Update /etc/hosts (requires sudo)
    echo -e "  ${YELLOW}→ Updating /etc/hosts (sudo required)...${NC}"
    if grep -q "$HOSTS_DOMAIN" /etc/hosts; then
        sudo sed -i "s|$OLD_IP $HOSTS_DOMAIN|$NEW_IP $HOSTS_DOMAIN|g" /etc/hosts
    else
        echo "$NEW_IP $HOSTS_DOMAIN" | sudo tee -a /etc/hosts >/dev/null
    fi
    echo -e "  ${GREEN}✔ /etc/hosts updated${NC} → $NEW_IP $HOSTS_DOMAIN"

    # 3. Update SSH_HOST variable for this session
    SSH_HOST="$NEW_IP"
    echo -e "  ${GREEN}✔ All configurations updated! Ready to connect.${NC}"
}

action_cluster_status() {
    echo ""
    echo -e "  ${CYAN}--- Cluster Pod Status ---${NC}"
    kubectl --kubeconfig="$KUBECONFIG" get pods -A --no-headers 2>&1 | \
        awk '{
            status=$4;
            name=$2;
            ns=$1;
            if (status == "Running" || status == "Completed")
                printf "  \033[0;32m✔\033[0m  %-20s %-50s %s\n", ns, name, status;
            else
                printf "  \033[0;31m✘\033[0m  %-20s %-50s %s\n", ns, name, status;
        }'
    echo ""
}

action_open_grafana() {
    echo ""
    stop_all_tunnels 2>/dev/null
    start_tunnel "grafana" "prometheus-stack-grafana" "monitoring" "3000" "80"
    echo -e "  ${CYAN}Credentials → admin / $GRAFANA_PASSWORD${NC}"
    echo -e "  ${CYAN}Open: http://localhost:3000${NC}"
    sleep 1
    xdg-open "http://localhost:3000" &>/dev/null &
}

action_open_argocd() {
    echo ""
    start_tunnel "argocd" "argocd-server" "argocd" "8080" "443"
    echo -e "  ${CYAN}Credentials → admin / (see option 11)${NC}"
    echo -e "  ${CYAN}Open: https://localhost:8080${NC}"
    sleep 1
    xdg-open "https://localhost:8080" &>/dev/null &
}

action_open_prometheus() {
    echo ""
    start_tunnel "prometheus" "prometheus-stack-kube-prom-prometheus" "monitoring" "9090" "9090"
    echo -e "  ${CYAN}Open: http://localhost:9090${NC}"
    sleep 1
    xdg-open "http://localhost:9090" &>/dev/null &
}

action_deploy_app() {
    echo ""
    echo -e "  ${CYAN}→ Running Helm upgrade for $HELM_RELEASE...${NC}"
    helm --kubeconfig="$KUBECONFIG" upgrade --install "$HELM_RELEASE" "$HELM_CHART" -n "$APP_NAMESPACE"
    echo -e "  ${GREEN}✔ Deployment complete!${NC}"
}

action_stress_test_start() {
    if [ -f "$PID_DIR/stress.pid" ] && kill -0 "$(cat "$PID_DIR/stress.pid")" 2>/dev/null; then
        echo -e "  ${YELLOW}⚠ Stress test is already running (PID: $(cat "$PID_DIR/stress.pid"))${NC}"
        return
    fi
    echo ""
    echo -e "  ${CYAN}→ Starting stress test...${NC}"
    python "$SCRIPT_DIR/stress_test.py" &>/tmp/microgitops-stress.log &
    echo $! > "$PID_DIR/stress.pid"
    echo -e "  ${GREEN}✔ Stress test started in background (PID: $(cat "$PID_DIR/stress.pid"))${NC}"
    echo -e "  ${CYAN}  Logs: tail -f /tmp/microgitops-stress.log${NC}"
}

action_stress_test_stop() {
    if [ -f "$PID_DIR/stress.pid" ]; then
        kill "$(cat "$PID_DIR/stress.pid")" 2>/dev/null
        rm -f "$PID_DIR/stress.pid"
        echo -e "  ${GREEN}✔ Stress test stopped.${NC}"
    else
        echo -e "  ${YELLOW}No active stress test found.${NC}"
    fi
}

action_ssh() {
    local ip
    ip=$(get_kubeconfig_ip)
    echo ""
    echo -e "  ${CYAN}→ Connecting to ubuntu@$ip...${NC}"
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "ubuntu@$ip"
}

action_argocd_password() {
    echo ""
    echo -ne "  ${CYAN}ArgoCD admin password: ${NC}"
    kubectl --kubeconfig="$KUBECONFIG" get secret argocd-initial-admin-secret \
        -n argocd -o jsonpath="{.data.password}" 2>/dev/null | base64 -d && echo
    echo ""
}

# ==============================================================================
#  MAIN LOOP
# ==============================================================================

while true; do
    print_header
    print_menu
    read -r choice

    case $choice in
        1) action_update_ip ;;
        2) action_cluster_status ;;
        3) action_open_grafana ;;
        4) action_open_argocd ;;
        5) action_open_prometheus ;;
        6) stop_all_tunnels ;;
        7) action_deploy_app ;;
        8) action_stress_test_start ;;
        9) action_stress_test_stop ;;
        10) action_ssh ;;
        11) action_argocd_password ;;
        0) echo -e "\n  ${GREEN}Goodbye! Stopping all tunnels...${NC}"; stop_all_tunnels; exit 0 ;;
        *) echo -e "  ${RED}Invalid option.${NC}" ;;
    esac

    echo ""
    echo -ne "  ${YELLOW}Press Enter to continue...${NC}"
    read -r
done
