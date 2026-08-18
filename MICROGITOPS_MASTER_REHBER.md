# 🚀 MicroGitOps Master Eğitim & Mülakat Rehberi

---

## 📌 BÖLÜM 1: PROJE AMACI VE VİZYONU

### Proje Tanımı
MicroGitOps, AWS cloud üzerinde çalışan, Kubernetes tabanlı, otomatik ölçeklenebilen (HPA), GitOps prensipleriyle yönetilen ve canlı izlenebilen production-grade bir altyapı platformudur.

### Problem Tanımı ve Çözüm
* **Geleneksel Yöntem:** Manuel sunucu kurulumu, kesintili güncellemeler ve yüksek trafikte sunucunun kilitlenmesi (`502 Bad Gateway`).
* **MicroGitOps Çözümü:** Sıfır kesintili otomatik canlıya alma (GitOps / ArgoCD), 2 saniyede 10 kata kadar otomatik ölçeklenme (HPA) ve tüm altyapının tek bir yönetim paneli üzerinden izlenmesi.

---

## 📌 BÖLÜM 2: MİMARİ VE TEKNOLOJİ HARİTASI

| Teknoloji | Tanım ve Sorumluluk | Tercih Sebebi | Analoji / Metaphor |
| :--- | :--- | :--- | :--- |
| **AWS EC2** | 7/24 bulut sunucu altyapısı. | Production ortamında bağımsız ve erişilebilir çalışma. | Kiralık bulut arsa / dükkan. |
| **Docker** | Konteynırlaştırma teknolojisi. | "Ortam uyumsuzluğu" ve bağımlılık sorunlarını giderme. | Standart nakliye konteynırı. |
| **K3s (Kubernetes)** | Hafif Kubernetes orkestrasyon motoru. | Düşük RAM kullanımı (~500MB) ve yüksek K8s API uyumluluğu. | Dükkan müdürü / Orkestra şefi. |
| **Helm** | Kubernetes paket ve şablon yöneticisi. | Karmaşık K8s kaynaklarını şablonlaştırıp tek komutla dağıtma. | Kurulum broşürü / Şablon. |
| **ArgoCD** | GitOps sürekli dağıtım (CD) motoru. | Git tabanlı pull-model ile sıfır kesintili ve güvenli güncellemeler. | Otomatik kargo / Yayıncı. |
| **Traefik Ingress** | Akıllı Ingress yönlendirici. | Dinamik Ingress routing (`microgitops.local`) ve HTTPS yönetimi. | Danışma / Trafik polisi. |
| **HPA (Auto-Scaler)**| Yatay pod otomatik ölçekleyici. | CPU yükü %70'i aştığında pod sayısını 2 → 10 çıkarma. | Ekstra gişe/vektör açma. |
| **Prometheus & Grafana**| Zaman serisi metrik toplama ve görselleştirme. | CPU, RAM, Network ve Pod restart durumlarını anlık izleme. | Araç kadranı ve hız göstergesi. |
| **FastAPI & Dockhand Panel**| Python tabanlı web operasyon paneli. | Komut satırı bağımlılığını azaltma, şifre ve yük testi yönetimi. | Direksiyon ve kontrol paneli. |
| **Autocannon** | Yüksek performanslı HTTP yük testi aracı. | Sistemin 1.500 RPS limitlerini ve HPA tepki hızını doğrulama. | Stres ve dayanıklılık testi. |

---

## 📌 BÖLÜM 3: SUNUM AKIŞI VE SENARYO (5 DAKİKA)

### 1. Dakika: Giriş ve Problem
Bir web uygulamasının canlıya alınması, güncellenmesi ve yüksek trafikte ayakta tutulması geleneksel yöntemlerle risklidir. MicroGitOps, bu altyapı karmaşasını kullanıcıdan soyutlayan yönetilen bir platformdur.

### 2. Dakika: Dinamik Ölçeklenme Mantığı (Otoyol Gişesi Analojisi)
Sistem normal zamanlarda 2 pod (gişe) çalıştırarak kaynak tasarrufu sağlar. İndirim veya kampanya anında gelen yoğun trafikte durum algılanır ve 2 saniyede kapasite 10 pod'a çıkarılır. Trafik normale döndüğünde sistem soğuma penceresiyle kademeli olarak küçülür.

### 3. Dakika: Performans Rakamları (`index.html`)
AWS EC2 üzerindeki tek node K3s testlerinde:
* **2 Pod:** ~300 RPS \| 67ms ortalama yanıt süresi.
* **10 Pod (HPA Peak):** **1.500 RPS** (Dakikada 90.000 / Günde ~100 Milyon istek kapasitesi).
* **Hata Oranı:** Test süresince %0.

### 4. Dakika: Canlı Operasyon Demosu (`http://localhost:7777`)
1. Operasyon panelinden canlı CPU/RAM ve Pod durumları gösterilir.
2. Stress Test sekmesinden `http://microgitops.local` hedefine yapay trafik başlatılır.
3. HPA grafiğinde aktif pod sayısının 2 → 10 çıkışı ve yükün karşılanması canlı izletilir.

---

## 📌 BÖLÜM 4: TEKNİK SORULAR VE REFERANS CEVAPLAR

### 1. Geleneksel yöntemler ile MicroGitOps arasındaki fark nedir?
Manuel sunucu yönetiminde güncellemeler kesintili olabilir ve ani trafikte kilitlenme yaşanır. MicroGitOps'ta ArgoCD ile kesintisiz güncelleme yapılır, HPA ile 2 saniyede 10 kata kadar otomatik ölçeklenme sağlanır ve tüm metrikler canlı izlenir.

### 2. Yazılımcı kod getirdiğinde DevOps sorumluluğu nedir?
DevOps mühendisi uygulama kodunu (business logic) yazmaz. Görevi; uygulamayı `Dockerfile` ile konteynırlaştırmak, Helm şablonlarıyla Kubernetes'e dağıtmak, Traefik üzerinden Ingress yönlendirmesini yapmak, HPA ölçeklenme politikalarını tanımlamak ve Grafana izlemelerini aktif etmektir.

### 3. Ani trafik şokunda (Flash Traffic) HPA gecikmesi nasıl yönetilir?
HPA 15 saniyede bir ölçüm yapar. Planlı trafiklerde (indirim, lansman) olaydan önce `minReplicas` artırılarak **Pre-Warming (Ön Isıtma)** uygulanır. Sürpriz trafiklerde ise KEDA veya Ingress seviyesindeki RPS metriklerine göre agresif ölçeklendirme yapılır.

### 4. DevSecOps yaklaşımı projede nasıl uygulanır?
Güvenlik en son yapılan kontrol değil, CI/CD pipeline'ına entegre edilen otomasyondur. Projede ArgoCD ile secret okuma, Kubernetes Namespace izolasyonu ve Traefik Ingress kuralları DevSecOps standartlarına uygun kurgulanmıştır.

---

## 📌 BÖLÜM 5: GERÇEK HAYAT ALTYAPI KRİZLERİ VE ÇÖZÜMLERİ (OHAL SENARYOLARI)

| Kriz Senaryosu | Neden Yaşanır? | Olası Sonuç | DevOps / SRE Mühendisi Çözümü |
| :--- | :--- | :--- | :--- |
| **Disk Dolması (Log Flooding)** | Uygulama hata döngüsüne girip diske devasa log yazar. | Sunucu diski %100 dolar, Kubernetes kilitlenir. | `logrotate` ve log toplama araçları (Loki/Fluentd) entegrasyonu. |
| **DB Bağlantı Patlaması** | HPA yeni pod açtıkça veritabanı bağlantı limiti aşılır. | Veritabanı çöker, tüm site `500 Error` verir. | Connection Pooling (PgBouncer) ve DB limit yapılandırması. |
| **DDoS & Bot Saldırısı** | Yapay isteklerle HPA sürekli pod açar. | Sunucu çökmez ama AWS faturası binlerce dolar olur. | Cloudflare WAF, Rate Limiting ve IP Engelleme. |
| **Önbellek & Yük Yönetimi (Redis/TTL)** | Her aramada veritabanına sorgu atılır. | Veritabanı CPU %100 olur, yanıt süreleri uzar. | **Redis Caching**, Varnish CDN ve TTL (Time-To-Live) yapılandırması. |
| **Bellek Sızıntısı (Memory Leak)** | Kod kullanılan RAM'i serbest bırakmaz. | Pod `OOMKilled` patlar, sonsuz restart döngüsü olur. | K8s Pod Bellek Limitleri (`limits.memory`) ve Profiling. |
| **Cloud Servis Kesintisi** | AWS veri merkezinde erişim sorunu oluşur. | Kod sorunsuz olsa da sunucuya erişilemez. | Multi-Region / Disaster Recovery (DR) yedekli mimari. |

---

## 📌 BÖLÜM 6: UZMANLIK TANIMI

> **"Cloud Altyapısı, Kubernetes Orkestrasyonu, Yük Yönetimi (Caching/Scaling) ve DevOps Otomasyonu alanlarında uzmanlaşıyorum. Amacım; yazılımların kesintisiz, yüksek performanslı, otomatik ölçeklenebilir ve güvenli bir altyapı üzerinde 7/24 çalışmasını sağlamaktır."**
