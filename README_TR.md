# ⚡ MicroGitOps — Production-Grade Managed Service & GitOps Platform

[![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-blue.svg?logo=kubernetes)](https://k3s.io/)
[![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange.svg?logo=argo)](https://argoproj.github.io/cd/)
[![Cloud](https://img.shields.io/badge/Cloud-AWS_EC2-FF9900.svg?logo=amazon-aws)](https://aws.amazon.com/)
[![IaC](https://img.shields.io/badge/IaC-Terraform-purple.svg?logo=terraform)](https://www.terraform.io/)
[![DevSecOps](https://img.shields.io/badge/DevSecOps-Trivy_Scan-green.svg?logo=aquasec)](https://trivy.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[🇺🇸 English Documentation (Primary README)](README.md)

**MicroGitOps**, AWS bulut altyapısı üzerinde çalışan, Kubernetes tabanlı, **ArgoCD GitOps** prensipleriyle yönetilen, otomatik ölçeklenebilen (**HPA**) ve özel geliştirilmiş **Dockhand Ops Panel** ile 7/24 canlı izlenebilen production-ready bir Managed Service Provider (MSP) altyapı platformudur.

---

## 📸 Platform Görsel Sergisi (Visual Showcase)

| Ekran | Açıklama | Görsel |
| :--- | :--- | :--- |
| **1. Dockhand Ops Panel** | Canlı sistem metrikleri, Pod haritası ve tünel yönetimi | `![Dashboard](docs/screenshots/dashboard.png)` |
| **2. Workloads Manager** | Tek tıkla Replica ölçekleme, restart ve Pod yaşam döngüsü | `![Workloads](docs/screenshots/workloads.png)` |
| **3. Live HPA Autoscaling** | Yük altında 2 → 10 Pod anlık dinamik ölçeklenme grafiği | `![HPA Chart](docs/screenshots/hpa-autoscale.png)` |
| **4. Credentials & Tunnels** | Şifre yönetimi, Port-forwarding ve canlı tünel erişimi | `![Tunnels](docs/screenshots/tunnels.png)` |
| **5. Business Landing Page** | Global standartlarda İngilizce sunum ve metrik lansman sayfası | `![Landing Page](docs/screenshots/landing-page.png)` |

---

## 🔥 Temel Özellikler ve Öne Çıkan Başarılar

* **🚀 Zero-Downtime GitOps (ArgoCD & Helm v3):** 
  Kod veya altyapı konfigürasyonu Git deposuna `push` edildiğinde, ArgoCD değişikliği algılar ve **kesintisiz (rolling-update)** olarak ortama yayar (`Auto-Sync & Self-Healing`).
* **⚡ Sub-Second HPA Auto-Scaling:** 
  Trafik patlamalarında CPU yükü %50'yi aştığında Kubernetes HPA pod kapasitesini **2 → 10 pod'a** hızla çıkarır.
* **🛡️ Yo-Yo (Flapping) Önleyici HPA Stabilizasyonu:** 
  Trafik aniden düştüğünde sistemin ani pod kapatmasını engellemek için `stabilizationWindowSeconds: 300` (5 Dakika Soğuma Penceresi) uygulanmıştır.
* **🔒 DevSecOps Güvenlik Hattı (Trivy Scan):** 
  GitHub Actions CI/CD hattında Trivy taraması çalıştırılarak CVE zafiyeti barındıran container imajlarının canlı ortama geçişi otomatik engellenir.
* **📊 1.500 RPS Performans Kapasitesi:** 
  Autocannon yük testinde tek node AWS EC2 sunucusu üzerinde **%0.00 hata oranı** ile saniyede 1.500 istek (**dakikada 90.000 / günde ~100 Milyon istek**) karşılanmıştır.
* **🛠️ Dockhand Ops Panel (FastAPI & Chart.js):** 
  Komut satırı karmaşasını ortadan kaldıran; canlı düğüm telemetrisi, Pod yönetimi, tüneller ve canlı `kubectl` çıktılarını sunan merkezi operasyon paneli (`http://localhost:7777`).

---

## 🏗️ Sistem Mimarisi (Architecture Flowchart)

```
                                  [ Geliştirici Git Commit ]
                                               │
                                               ▼
                                 [ GitHub Actions CI Pipeline ]
                                  (Trivy CVE Security Scan)
                                               │
                                               ▼
                                   [ ECR / Docker Hub Registry ]
                                               │
                                               ▼
                       ┌──────────────────────────────────────────────┐
                       │              AWS EC2 Cloud Node              │
                       │                                              │
[ Ziyaretçi Trafiği ] ──► [ Traefik Ingress Controller ]        │
                                       │                              │
                     ┌─────────────────┴──────────────────┐           │
                     ▼                                    ▼           │
        [ Service: microgitops-app ]          [ Dockhand Ops Panel ]  │
                     │                             (Port 7777)        │
                     ▼                                    │           │
      ┌──────────────────────────────┐                    │           │
      │   Kubernetes Pods (HPA)      │ ◄──────────────────┘           │
      │  [ Pod 1 ] [ Pod 2 ] ...     │   (Workloads / Scale / Logs)   │
      └──────────────────────────────┘                                │
                     ▲                                                │
                     │ (Pull-based Auto-Sync & Self-Healing)          │
           [ ArgoCD Controller ] ◄────── [ Git Repository (State) ]    │
                       └──────────────────────────────────────────────┘
```

---

## 🛠️ Teknolojik Altyapı Katmanları (Tech Stack)

| Katman | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Cloud Infrastructure** | AWS EC2 (Ubuntu 22.04 LTS) | AWS üzerinde konuşlandırılmış 7/24 kesintisiz bulut sunucu. |
| **Orchestration** | Kubernetes (K3s) | CNCF sertifikalı, yüksek performanslı hafif Kubernetes kümesi. |
| **IaC & Automation** | Terraform | Bulut kaynaklarının kodla (Infrastructure as Code) oluşturulması. |
| **Continuous Delivery** | ArgoCD | GitOps mantığıyla çalışan pull-based sürekli canlılama motoru. |
| **Packaging & Config** | Helm v3 | Kubernetes uygulama paketleme ve versiyonlama aracı. |
| **Ingress & Networking** | Traefik v2 | Akıllı yük dengeleyici ve dynamic HTTP/HTTPS routing. |
| **DevSecOps** | Trivy Scanner | Container imaj güvenlik ve CVE zafiyet taraması. |
| **Ops Dashboard** | Python FastAPI / HTML5 / Chart.js | Merkezi küme izleme, HPA grafikleri ve Workloads Manager. |

---

## ⚙️ Kurulum ve Hızlı Başlatma (Quick Start)

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/Bullute/MicroGitOps.git
cd MicroGitOps
```

### 2. Ops Panelini Çalıştırın
```bash
python panel/server.py
```
Tarayıcıdan **`http://localhost:7777`** adresine gidin.

### 3. ArgoCD & Kubernetes Durumunu Doğrulayın
```bash
kubectl --kubeconfig ./aws-kubeconfig get app -n argocd
```
Çıktı: `microgitops-app Synced Healthy 💚`

---

## 📈 Performans ve Benchmark Özetı

Autocannon ile gerçekleştirilen stres testi sonuçları:

| Metrik | Varsayılan (2 Pods) | Maksimum Yük (10 Pods HPA) |
| :--- | :--- | :--- |
| **Saniyedeki İstek (RPS)** | 300 RPS | **1.500 RPS** |
| **Dakikadaki İşlem** | 18.000 Req/Min | **90.000 Req/Min** |
| **Günlük Yük Kapasitesi** | ~25M Req/Day | **~100M Req/Day** |
| **Ortalama Yanıt Süresi** | 42ms | **67ms** |
| **Hata / Paket Kaybı** | %0.00 | **%0.00** |

---

## 🧠 Üretim Ortamı Problem & Çözüm Vakaları (Troubleshooting Scenarios)

Bu altyapı geliştirilirken karşılaşılan ve çözülen mülakat seviyesi teknik zorluklar:

1. **Yo-Yo (Flapping) Dalgalanması ve Çözümü:**
   * *Problem:* Trafik biter bitmez HPA'nın pod'ları anında kapatması ve tekrar yük gelince yeniden açması sebebiyle pod'ların sürekli açılıp kapanması.
   * *Çözüm:* HPA spec içerisine `scaleDown.stabilizationWindowSeconds: 300` (5 dakika soğuma süresi) eklendi.
2. **Kubelet Probe Timeout ve Erken Pod Öldürme:**
   * *Problem:* Aşırı yük altında pod CPU'su sınırlandığında `/health` kontrolünün 1 saniyeden uzun sürmesi ve Kubelet'in pod'u öldürüp ArgoCD'yi `Degraded (Kırmızı Kalp)` yapması.
   * *Çözüm:* `readinessProbe` süresi `initialDelaySeconds: 2`, `periodSeconds: 3` yapılarak pod'ların 2 saniyede `Ready` olması sağlandı; probe timeout süresi 5 saniyeye yükseltildi.
3. **Tek Sunucuda CPU Darboğazı Önleme:**
   * *Problem:* Pod başı `500m` CPU limiti 10 pod açıldığında tek EC2 sunucusunu kilitliyordu.
   * *Çözüm:* Pod başı CPU isteği `50m`, limiti `200m` olarak ayarlanarak 10 pod'un kümede sorunsuz sığması sağlandı.

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
