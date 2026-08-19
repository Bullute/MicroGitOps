# 🚀 MicroGitOps — Production-Grade Managed Service & Observability Platform

[![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-blue.svg?logo=kubernetes)](https://k3s.io/)
[![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange.svg?logo=argo)](https://argoproj.github.io/cd/)
[![Cloud](https://img.shields.io/badge/Cloud-AWS_EC2-FF9900.svg?logo=amazon-aws)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**MicroGitOps**, AWS cloud altyapısı üzerinde çalışan, Kubernetes tabanlı, GitOps prensipleriyle yönetilen, otomatik ölçeklenebilen (**HPA**) ve özel geliştirilmiş **Dockhand Ops Panel** ile canlı izlenebilen production-ready bir altyapı platformudur.

---

## 📸 Ekran Görüntüleri (Platform Visuals)

### 1. Dockhand Operations Dashboard (Canlı Metrikler & Pod Haritası)
![Dockhand Dashboard](docs/screenshots/dashboard.png)

### 2. Workloads Manager (Canlı Pod & Replica Kontrolü)
![Workloads Manager](docs/screenshots/workloads.png)

### 3. Otomatik Ölçeklenme & Yük Testi (HPA Auto-Scaling in Action)
![HPA Autoscaling](docs/screenshots/hpa-autoscale.png)

### 4. Tünel ve Dinamik Secret Yönetimi (Port Forwards & ArgoCD Key)
![Port Forwards & Tunnels](docs/screenshots/tunnels.png)

### 5. İş Odaklı Sunum Sayfası (Business Landing Page)
![Business Landing Page](docs/screenshots/landing-page.png)

---

## 🔥 Temel Özellikler (Key Features)

* **🚀 Zero-Downtime GitOps (ArgoCD & Helm):** Git deposuna atılan her commit, kümede sıfır kesintiyle otomatik güncellenir (`Auto-Sync & Self-Healing`).
* **⚡ HPA Auto-Scaling Kriz Koruması:** Ani trafik yükünde CPU kullanımı %70'i aştığında sistem 2 saniye içinde Pod kapasitesini **2 → 10** katına otomatik çıkarır.
* **📊 1.500 RPS Performans Kapasitesi:** Autocannon ile yapılan yük testlerinde tek node AWS EC2 sunucusu üzerinde %0 hatayla saniyede 1.500 istek (**günde ~100 Milyon istek**) karşılanmıştır.
* **🛠️ Dockhand Ops Panel (FastAPI + HTML5):** Komut satırı karmaşasını ortadan kaldıran; canlı metrikleri, Pod yönetimi, tünelleri ve şifreleri tek ekranda toplayan yönetim arayüzü.
* **🌐 Traefik Ingress & Dynamic Routing:** Domain yönlendirmeleri (`microgitops.local`) ve yük dengeleme otomatik olarak sağlanır.

---

## 🏗️ Sistem Mimarisi (Architecture)

```
                       ┌─────────────────────────────────────────┐
                       │           AWS EC2 Cloud Node            │
                       │                                         │
[ Ziyaretçi / Müşteri ] ──► [ Traefik Ingress Controller ]        │
                                       │                         │
                     ┌─────────────────┴─────────────────┐       │
                     ▼                                   ▼       │
        [ Service: microgitops-app ]          [ Dockhand Ops Panel ]
                     │                             (Port 7777)
                     ▼                                   │
      ┌──────────────────────────────┐                   │
      │   Kubernetes Pods (HPA)      │ ◄─────────────────┘
      │  [ Pod 1 ] [ Pod 2 ] ...     │   (Scale / Restart / Logs)
      └──────────────────────────────┘
                     ▲
                     │ (Pull-based Auto Sync)
           [ ArgoCD Controller ] ◄────── [ GitHub Repository ]
```

---

## 🛠️ Teknolojik Altyapı (Tech Stack)

| Katman | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Cloud Provider** | AWS EC2 (Ubuntu 22.04) | 7/24 çalışan bulut sunucu altyapısı. |
| **Container & K8s** | Docker / K3s | CNCF sertifikalı, hafif Kubernetes orkestrasyon motoru. |
| **GitOps & Package** | ArgoCD / Helm v3 | Kod değişikliğini kümede otomatik yayınlayan CD motoru. |
| **Ingress & Traffic** | Traefik v2 | Akıllı yük dengeleyici ve dynamic routing. |
| **Monitoring** | Prometheus / Grafana / Chart.js | Canlı metrik toplama ve zaman serisi grafikleri. |
| **Ops Dashboard** | Python FastAPI / HTML5 / CSS3 | Merkezi yönetim ve operasyon paneli. |

---

## 🚀 Hızlı Başlatma (Quick Start)

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Bullute/MicroGitOps.git
cd MicroGitOps
```

### 2. Ops Panelini Çalıştırın
```bash
python panel/server.py
```
Tarayıcıda `http://localhost:7777` adresini açın.

---

## 📊 Performans ve Benchmark Sonuçları

Autocannon ile yapılan yük testi sonuçları:

* **Varsayılan Durum (2 Pods):** 300 RPS \| 67ms Yanıt Süresi
* **Maksimum Yük Durumu (10 Pods HPA):** **1.500 RPS (Dakikada 90.000 / Günde 100M İstek)**
* **Hata Oranı:** %0.00

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
