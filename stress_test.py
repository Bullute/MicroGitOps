import urllib.request
import time
import sys

url = "http://microgitops.local/"
print(f"🚀 MicroGitOps Load Test Started! Target: {url}")
print("Press Ctrl+C to stop the test.\n")

requests_sent = 0
errors = 0

try:
    while True:
        try:
            # Using standard urllib library to avoid external dependencies like requests
            req = urllib.request.Request(url, headers={'User-Agent': 'MicroGitOps-LoadTester/1.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                response.read()
                requests_sent += 1
                
                # Print stats to console every 10 requests
                if requests_sent % 10 == 0:
                    print(f"✅ Total Requests Sent: {requests_sent} | Errors: {errors}")
                    
        except Exception as e:
            errors += 1
            print(f"❌ Request Error ({errors}): {e}")
            
        # Generate dynamic traffic wave patterns (Burst -> Idle -> Normal -> Rest)
        cycle = (requests_sent // 20) % 4
        if cycle == 0:
            time.sleep(0.01)  # Burst load (High Traffic)
        elif cycle == 1:
            time.sleep(0.25)  # Idle load (Low Traffic)
        elif cycle == 2:
            time.sleep(0.06)  # Medium load (Normal Traffic)
        else:
            time.sleep(0.40)  # Rest period (Minimal Traffic)

except KeyboardInterrupt:
    print("\n👋 Load test stopped by user.")
    print(f"--- SUMMARY ---")
    print(f"Successful Requests: {requests_sent}")
    print(f"Failed Requests     : {errors}")
    sys.exit(0)
