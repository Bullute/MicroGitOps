"""
HPA Stress Test — Kubernetes HPA'yı Tetiklemek İçin
Agresif, çok thread'li yük testi.
Kullanım: python hpa_stress.py
"""

import threading
import requests
import time
import sys

TARGET = "http://microgitops.local"
# /burn?duration=10 → her istek 10 saniye CPU yakar → HPA tetiklenir
ENDPOINTS = ["/burn?duration=10", "/burn?duration=5", "/burn?duration=8"]
THREAD_COUNT = 20       # /burn zaten ağır, 20 thread yeterli
DURATION_SECONDS = 120  # 2 dakika boyunca zorla

results = {"ok": 0, "err": 0, "start": time.time()}
lock = threading.Lock()
stop_event = threading.Event()


def hammer(thread_id):
    import itertools
    for endpoint in itertools.cycle(ENDPOINTS):
        if stop_event.is_set():
            break
        try:
            r = requests.get(f"{TARGET}{endpoint}", timeout=3)
            with lock:
                if r.status_code < 400:
                    results["ok"] += 1
                else:
                    results["err"] += 1
        except Exception:
            with lock:
                results["err"] += 1


def print_stats():
    while not stop_event.is_set():
        time.sleep(5)
        elapsed = time.time() - results["start"]
        total = results["ok"] + results["err"]
        rps = total / elapsed if elapsed > 0 else 0
        print(f"  ⚡ [{elapsed:5.0f}s] "
              f"RPS: {rps:6.1f} | "
              f"OK: {results['ok']:6d} | "
              f"ERR: {results['err']:4d}")
        sys.stdout.flush()


print(f"\n🔥 HPA Stress Test Başlıyor!")
print(f"   Target   : {TARGET}")
print(f"   Threads  : {THREAD_COUNT}")
print(f"   Duration : {DURATION_SECONDS}s")
print(f"\n   Şimdi başka bir terminalde izle:")
print(f"   kubectl --kubeconfig=./aws-kubeconfig get hpa -n microgitops -w")
print(f"\n{'─'*55}")

threads = []
for i in range(THREAD_COUNT):
    t = threading.Thread(target=hammer, args=(i,), daemon=True)
    t.start()
    threads.append(t)

stat_thread = threading.Thread(target=print_stats, daemon=True)
stat_thread.start()

try:
    time.sleep(DURATION_SECONDS)
except KeyboardInterrupt:
    print("\n  ⛔ Kullanıcı tarafından durduruldu.")

stop_event.set()
print(f"\n{'─'*55}")
elapsed = time.time() - results["start"]
total = results["ok"] + results["err"]
print(f"✅ Test tamamlandı!")
print(f"   Toplam istek : {total}")
print(f"   Başarılı     : {results['ok']}")
print(f"   Hatalı       : {results['err']}")
print(f"   Ortalama RPS : {total/elapsed:.1f}")
print(f"   Süre         : {elapsed:.1f}s\n")
