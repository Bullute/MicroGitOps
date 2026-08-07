import urllib.request
import time
import sys

url = "http://localhost:8090/"
print(f"🚀 MicroGitOps Load Test Baslatildi! Hede: {url}")
print("Ctrl+C tusuna basarak testi durdurabilirsiniz.\n")

requests_sent = 0
errors = 0

try:
    while True:
        try:
            # Herhangi bir ucuncu parti kütüphaneye (requests vb.) ihtiyac duymadan standart urllib kullanıyoruz.
            req = urllib.request.Request(url, headers={'User-Agent': 'MicroGitOps-LoadTester/1.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                response.read()
                requests_sent += 1
                
                # Her 10 istekte bir konsola durum yazdırıyoruz.
                if requests_sent % 10 == 0:
                    print(f"✅ Gonderilen Toplam Istek: {requests_sent} | Hatalar: {errors}")
                    
        except Exception as e:
            errors += 1
            print(f"❌ Istek Hatasi ({errors}. Hata): {e}")
            
        # İstekler arası bekleme suresi (100ms = Saniyede yaklasik 10 istek).
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n👋 Yuk testi kullanici tarafindan durduruldu.")
    print(f"--- OZET ---")
    print(f"Basarili Istek: {requests_sent}")
    print(f"Hata Sayisi   : {errors}")
    sys.exit(0)
