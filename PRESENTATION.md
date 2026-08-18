# 🚀 MicroGitOps Managed Service Provider (MSP) Platform
## Sunum ve Proje Anlatım Rehberi (Presentation Slide Deck)

---

## 📌 Slayt 1: Kapak & Proje Tanıtımı
* **Başlık:** MicroGitOps — Production-Grade Managed Service Platform
* **Alt Başlık:** Kubernetes Mimarisi Üzerinde Tek Tıkla Uygulama Canlıya Alma, HPA Auto-Scaling ve Operasyon Paneli
* **Sunan:** DevOps & Infrastructure Specialist
* **Anahtar Kavramlar:** K3s | Helm | ArgoCD | Traefik | FastAPI | HPA | Chart.js

---

## 📌 Slayt 2: Problem Tanımı (Geleneksel Altyapı Karmaşası)
* **Geleneksel Yöntem:**
  * Bir web sitesi (örneğin HTML/CSS e-ticaret sitesi) canlıya alınırken sunucuya manuel SSH bağlantısı, Nginx konfigürasyonu ve SSL yönetimi gerekir.
  * Ani trafik artışında (DDoS veya Kampanya anlarında) sunucular kilitlenir (`502 Bad Gateway`).
  * Kubernetes ve GitOps sistemlerini yönetmek komut satırı karmaşası sebebiyle geliştiriciler için zordur.
* **İhtiyaç:** Tüm altyapı karmaşıklığını soyutlayan, tek tıkla canlıya alma (Onboarding) ve otomatik çökme koruması sunan merkezi bir **Yönetilen Servis Paneli (MSP Dashboard)**.

---

## 📌 Slayt 3: Çözüm ve Sistem Mimarisi
* **MicroGitOps Mimarisi:**
  * **AWS EC2 & K3s:** Hafif, yüksek performanslı tek-node Kubernetes ortamı.
  * **Traefik Ingress:** Akıllı yük dengeleme ve dynamic domain yönlendirmesi (`http://microgitops.local`).
  * **ArgoCD & Helm:** Git tabanlı otomatik canlıya alma (GitOps / Zero-Downtime Deployment).
  * **Dockhand Ops Panel:** Tüm kümenin kontrolünü sağlayan minimalist, canlı metrikli web yönetim paneli (`FastAPI + HTML5/CSS3 + Chart.js`).

---

## 📌 Slayt 4: Dockhand Ops Panel (Yönetim Paneli)
* **Dockhand Teması:**
  * Gözü yormayan "Sakin Dark-Navy" tasarım dili.
  * **Ana Sayfa:** Anlık Node CPU/Memory haritası ve aktif Pod durumları.
  * **Port Forwards & Tunnels:** Grafana, ArgoCD ve Prometheus tünekleri. Dinamik Kubernetes Secret okuyucu ile tek tıkla şifre kopyalama (`📋 Copy Password`).
  * **Cluster Activity Viewer:** Tüm kümedeki Warning/Normal Kubernetes olaylarını namespace bazlı anlık filtreleme.

---

## 📌 Slayt 5: Canlı Örnek — Müşteri Web Sitesini Canlıya Alma (Kitabevi Örneği)
* **Senaryo:** Müşteri yeni yazdığı `Kitabevi (HTML/CSS)` web sitesini canlıya almak istiyor.
* **İşlem Adımları:**
  1. HTML/CSS kodu Nginx konteynırına paketlenir (`Dockerfile`).
  2. Dockhand Paneli üzerinden **Client Name** ve **Domain** girilerek **Generate & Deploy** butonuna basılır.
  3. Arka planda Helm izolasyonu (Namespace) ve Traefik Ingress otomatik oluşturulur.
  4. Site 1 saniyede kesintisiz olarak canlıya alınır.

---

## 📌 Slayt 6: Otomatik Ölçeklenme (HPA Auto-Scaling Kriz Koruması)
* **Kriz Anı (Peak Traffic):**
  * Sitede kampanya başladığında veya yüksek trafik geldiğinde CPU kullanımı `%70` eşiğini aşar.
* **Kubernetes HPA Tepkisi:**
  * HPA (Horizontal Pod Autoscaler) durumu fark eder ve 2 saniye içinde Pod sayısını **2'den 10'a çıkarır (Scale-Up)**.
* **Ops Paneli HPA Mini-Grafiği:**
  * Canlı grafik üzerinde Yeşil çizgi (Aktif Pod Replicas) ve Sarı kesikli çizgi (Target CPU Load %) gerçek zamanlı çizilir.
* **Trafik Bitince:** Kubernetes 5 dakikalık soğuma süresinden (Stabilization Window) sonra Pod'ları kademeli olarak `10 -> 4 -> 2` seviyesine düşürür.

---

## 📌 Slayt 7: Performans ve Trendyol Peak Karşılaştırması
* **Canlı Benchmark Test Sonuçları (Autocannon):**
  * **2 Pod Kapasitesi:** ~300 RPS (Saniyede 300 İstek) | **67ms Yanıt Süresi**
  * **10 Pod Maksimum Kapasite:** **1.500 RPS (Dakikada 90.000 İstek / Günde ~100 Milyon İstek)**
* **Trendyol Peak Karşılaştırması:**
  * Trendyol Efsane Cuma günü 300.000+ RPS alır (binlerce sunucuda).
  * Bizim tek sunuculu MicroGitOps altyapımız, Trendyol'un devasa trafiğinin **%0.3'ünü tek başına** %0 hata oranı ve 67ms gecikmeyle karşılayabilir.

---

## 📌 Slayt 8: Gözlemlenebilirlik ve Güvenlik (Observability)
* **Grafana & Prometheus Entegrasyonu:**
  * Canlı CPU/RAM zaman serisi grafikleri.
* **Dinamik Secret Yönetimi:**
  * ArgoCD (`argocd-initial-admin-secret`) ve Grafana şifreleri Kubernetes Secret'larından otomatik base64-decode edilerek panele getirilir.
* **Non-Blocking API Mimarisi:**
  * Metrics-server veya küme yük altına girse bile 2 saniyelik timeout ve SSH fallback mekanizması sayesinde arayüz sıfır gecikmeyle (0.1sn) açılır.

---

## 📌 Slayt 9: Canlı Demo Senaryosu (Sunum Esnasında Yapılacaklar)
1. **Arayüz Tanıtımı:** `http://localhost:7777` panelini açıp canlı Pod tablosunu ve CPU/RAM grafiklerini göster.
2. **Şifre Kopyalama:** Port Forwarding sekmesine geç, ArgoCD kartındaki `📋 Copy` butonuna basıp tünek başlat.
3. **Stress Test & HPA Gösterisi:** 
   * Stress Test sekmesine geç.
   * `http://microgitops.local/` target'ını seç ve **50 Connections** ile testi başlat.
   * Canlı HPA grafiğinde Pod sayısının 2'den 10'a çıkışını izlet!

---

## 📌 Slayt 10: Sonuç ve Değerlendirme
* **Elde Edilen Kazanımlar:**
  * Üretim standartlarında (Production-Ready) GitOps ve Kubernetes altyapısı.
  * Tek sunucuda saniyede 1.500 istek kaldırabilen yüksek performans.
  * Son kullanıcı/müşteri için tek tıkla canlıya alma kolaylığı sağlayan modern yönetim arayüzü.
* **Teşekkürler & Soru - Cevap (Q&A)**
