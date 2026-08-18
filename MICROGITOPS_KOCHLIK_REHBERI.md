# 🚀 MicroGitOps Koçluk & Mülakat Rehberi (Samimi Versiyon)
> **Bu belge, seninle birebir konuştuğumuz, samimi tüyoların ve benzetmelerin olduğu özel çalışma rehberindir.**

---

## 📌 BÖLÜM 1: BU PROJEYİ NEDEN YAPTIM? (Hikayen & Vizyonun)

### ❓ Soru: "Bu projeyi neden yaptın, amacı ne?"
**Cevap:**
"Ben sadece tek bir web sitesi yazıp teslim eden sıradan bir yazılımcı olmak istemedim. Çünkü tek bir site yapıp teslim etmek sürdürülebilir bir altyapı tecrübesi kazandırmaz. 
Ben kurumsal şirketlerin (e-ticaret, banka, SaaS) kullandığı **büyük ölçekli, 7/24 kesintisiz çalışan, aniden 100.000 kişi yüklendiğinde çökmeyen ve canlı izlenen altyapıların** arkasındaki mantığı çözmek ve bunu kendi elimle **AWS** üzerinde kurmak için bu projeyi geliştirdim."

---

## 📌 BÖLÜM 2: TEKNOLOJİ HARİTASI (Ne İş Yapar, Niye Kullandım?)

Sana sorulan her teknolojiyi aşağıdaki **Günlük Hayat Benzetmesi** ile anlatırsan seni dinleyen herkes anında kavrar:

| Teknoloji | Ne İş Yapar? | Niye Kullandım? | Günlük Hayat Benzetmesi |
| :--- | :--- | :--- | :--- |
| **AWS EC2** | İnternette 7/24 çalışan sanal bulut sunucusu. | Projemizin kendi bilgisayarımda değil, gerçek internette 7/24 yaşaması için. | Kiraladığımız dükkan / arsa. |
| **Docker** | Kodumuzu ve kütüphanelerini tek pakete (imaja) koyar. | "Benim bilgisayarımda çalışıyordu ama sunucuda çalışmıyor" sorununu bitirmek için. | Standart nakliye konteynırı. |
| **K3s (Kubernetes)** | Konteynırları ve sunucuları yöneten orkestra şefi. | Çöken pod'u yeniden açmak, yük artınca yeni pod eklemek için. | Dükkanın müdürü (garsonları ve yükü yöneten beyin). |
| **Helm** | Kubernetes dosyalarını tek komutla kuran paket yöneticisi. | Karmaşık Kubernetes YAML dosyalarını şablonlaştırıp tek tıkla deploy etmek için. | Hazır mobilya kurulum kılavuzu. |
| **ArgoCD** | GitOps mantığıyla çalışan otomatik yayınlama aracı. | Git'te kod değiştiği an kümede sıfır kesintiyle (Zero-Downtime) güncellemek için. | Otomatik kargo dağıtıcısı (GitOps). |
| **Traefik Ingress** | Gelen internet trafiğini doğru uygulamaya dağıtan akıllı yönlendirici. | `http://microgitops.local` adresine gelen ziyaretçiyi doğru pod'a yönlendirmek için. | Danışma / Trafik Polisi. |
| **HPA (Auto-Scaler)**| CPU yükü artınca Pod sayısını 2'den 10'a çıkaran sistem. | Ani trafik patlamasında sitenin kilitlenmesini engellemek için. | Yoğunluk anında yeni gişe açan görevli. |
| **Prometheus & Grafana**| Sistem metriklerini toplayıp canlı grafik yapan izleme aracı. | Sunucunun CPU, RAM ve trafik durumunu anlık takip etmek için. | Arabanın kadranı (hız ve benzin göstergesi). |
| **FastAPI & Dockhand Panel**| Tüm bu altyapıyı tek ekrandan yönettiğimiz web arayüzümüz. | Komut satırı karmaşasını bitirip şifreleri, logları ve yük testini tek ekrana toplamak için. | Arabanın direksiyonu ve kontrol paneli. |
| **Autocannon** | Sisteme saniyede 1.500 istek bindiren yük testi aracı. | Sistemimizin gerçek limitlerini ve HPA'in otomatik büyümesini kanıtlamak için. | Arabanın stres/çarpışma testi. |

---

## 📌 BÖLÜM 3: MASADAKİ ABİLERE 5 DAKİKALIK SUNUM SENARYOSU

### 1. Dakika: Giriş & Problem
> "Merhabalar abiler/hocalar. Bir web sitesi yapıldığında onu sunucuya koymak, güncellemeleri yayınlamak ve indirim/kampanya günlerinde yüksek trafik geldiğinde sitenin çökmesini engellemek geleneksel yöntemlerle çok zordur. Benim geliştirdiğim **MicroGitOps** sistemi, tüm bu altyapı karmaşasını arka planda otomatik halleden bir yönetim platformudur."

### 2. Dakika: Otoyol Gişesi Benzetmesi
> "Sistemi bir **otoyol gişesi** gibi düşünebiliriz:
> Normalde 2 tane gişe (sunucu) açık çalışır ve boşuna elektrik/para harcamaz.
> Bayram gününde veya indirim anında binlerce araç (ziyaretçi) geldiğinde, sistem trafiği otomatik algılar ve 2 saniyede gişe sayısını 10'a çıkarır. Trafik bitince tekrar 2 gişeye düşer. Böylece hem site hiç çökmüyor hem de gereksiz sunucu maliyeti ödenmiyor."

### 3. Dakika: Canlı Rakamlar (`index.html`)
> *(Ekranında `index.html` sayfasını göster)*
> "AWS üzerinde yaptığımız gerçek yük testlerinde, sistemimizin saniyede 1.500 isteği kesintisiz karşıladığını kanıtladık. Bu da günde **~100 milyon istek** demek. Orta-büyük ölçekli e-ticaret sitelerinin tüm trafiğini tek başına kaldırabilecek güçte."

### 4. Dakika: Şov Anı — Ops Panel (`http://localhost:7777`)
> *(Panele geç: `http://localhost:7777`)*
> "Burası geliştirdiğim operasyon paneli. Sunucumuzun canlı CPU/RAM durumunu buradan izliyoruz.
> Şimdi **Stress Test** sekmesine geçiyorum. Sisteme aniden yoğun bir trafik bindiriyorum.
> Bakın canlı grafikte gördüğünüz gibi CPU yükseldiği an yeşil çizgi (sunucu sayısı) **2'den 10'a otomatik çıktı** ve yükü %0 hatayla göğüsledi!"

---

## 📌 BÖLÜM 4: SIKÇA SORULAN SORULAR VE ŞOV CEVAPLARI

### Soru 1: "Rakiplerine / Geleneksel yöntemlere göre ne farkı var?"
* **Cevap:** *"Manuel sunucu kurulumunda site güncellenirken kesintiye uğrayabilir, ani trafikte kilitlenir. Bizim sistemimizde ArgoCD ile sıfır kesintiyle güncelleme yapılır, HPA ile 2 saniyede 10 kata kadar otomatik büyür ve tüm durum tek ekrandan izlenir."*

### Soru 2: "Yazılımcı (örneğin İzzet Bey) bir PHP kodu getirdiğinde senin görevin nedir?"
* **Cevap:** *"Ben PHP kodunun içindeki iş mantığını yazmam, o yazılımcının işidir. Benim görevim o kodu `Dockerfile` ile paketlemek, Helm ile Kubernetes kümesine deploy etmek, Traefik ile domain bağlamak ve site çökmesin diye HPA ve Grafana izlemelerini aktif etmektir."*

### Soru 3: "Ani trafik geldiğinde Pod'lar açılana kadar ne olur?"
* **Cevap:** *"HPA 15 saniyede bir ölçüm yapar. Eğer trafik saat 00:00'da indirim başlayacak gibi planlı bir trafikse, olaydan 5 dakika önce `minReplicas` sayısını manuel veya CronJob ile 10'a çıkarırız (Pre-Warming). Eğer sürpriz trafikse KEDA kullanarak RPS bazlı daha hızlı ölçeklendiririz."*

### Soru 4: "DevSecOps nedir, senin yaptığınla ilgisi var mı?"
* **Cevap:** *"DevOps işin hızlı ve kesintisiz canlıya geçmesini sağlar. DevSecOps ise bu hızı düşürmeden araya otomatik güvenlik süzgeçleri (Trivy imaj taraması, Secret yönetimi) koyar. Güvenlik en son yapılan kontrol değil, pipeline'ın içindeki otomasyondur."*

---

## 📌 BÖLÜM 5: GERÇEK HAYATTAN İSTİSNAİ FELAKETLER (OHAL SENARYOLARI)

### ❓ Soru: "Kod mükemmel olsa bile sunucuda ne patlayabilir ki?"
* **Dış Servis Çökmesi:** Yazılımcının kodu mükemmel olabilir. Ama iyzico (ödeme altyapısı) veya Merkez Bankası döviz servisi kilitlenirse, mükemmel yazılmış PHP/Python kodu yanıt beklerken timeout'a düşer ve log basarak sunucuyu kilitler.
* **Disk Dolması (Log Flooding):** Yazılımcı sunucu diskini yönetemez. Sunucuda logların diski doldurmaması (`logrotate` / Loki) %100 DevOps Mühendisinin işidir.
* **Veritabanı Patlaması:** HPA pod sayısını 10'a çıkarınca veritabanının bağlantı limiti (Connection Pool) dolar. Yeni pod açılması veritabanını DAHADA ÇÖKERTİR. PgBouncer ve bağlantı havuzu ayarı DevOps/SRE işidir.
* **Önbellek & Trendyol Örneği (Redis & TTL):** Trendyol'daki gibi arama sonuçlarının veritabanına yük bindirmemesi için Redis önbellekte tutulması (TTL - Time To Live) ve CDN (Varnish/Cloudflare) mimarisini kurgulamak **TAM OLARAK DEVOPS / SRE MÜHENDİSİNİN İŞİDİR.**

---

## 📌 BÖLÜM 6: KENDİNİ TANITMA CÜMLESİ (CV & MÜLAKAT)

> **"Ben Cloud (Bulut Altyapısı), Kubernetes Orkestrasyonu, Yük Yönetimi (Caching/Redis) ve DevOps Otomasyonu alanıyla ilgileniyorum.**
> **Amacım; yazılımcıların yazdığı kodun sunucularda takılmadan, çökmeden, yüksek performansla ve güvenle çalışmasını sağlayan sistemleri kurmak.**
> **Bu projeyi de bir altyapının A'dan Z'ye nasıl kurgulandığını, yük altında nasıl davranması gerektiğini ve nasıl izleneceğini bizzat uygulayarak kanıtlamak için geliştirdim."**
