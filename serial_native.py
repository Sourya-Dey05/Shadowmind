# =============================================================================
# FILE: serial_native.py
# PURPOSE: Zero-Dependency Serial Attack Script.
#          Uses ONLY Python Standard Library (urllib.request) — requires NO pip install!
#          Works out-of-the-box on any target machine (Windows, Linux, Mac, Kali).
# =============================================================================

import urllib.request
import urllib.error
import time
import sys

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.29.250:8080"

ENDPOINTS = [
    "/vault/credentials.env.enc",
    "/vault/customer_database_dump.sql",
    "/vault/source_code.zip",
    "/vault/aws_production_keys.env"
]

print("🔴 STARTING NATIVE SERIAL ATTACK (Zero Dependencies)...")
print(f"Target: {TARGET_URL}\n")

for i, path in enumerate(ENDPOINTS, 1):
    url = f"{TARGET_URL.rstrip('/')}{path}"
    print(f"[{i}/4] GET {path}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Native-Recon)"})
        start = time.time()
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read()
            latency = (time.time() - start) * 1000
            print(f"      Status: {resp.status} | Size: {len(body)} bytes | Latency: {latency:.1f}ms")
    except urllib.error.HTTPError as e:
        print(f"      HTTP Error: {e.code}")
    except Exception as e:
        print(f"      Error: {e}")
    
    print("      ⏳ Waiting 3 seconds...\n")
    time.sleep(3)

print("✅ NATIVE SERIAL ATTACK COMPLETE.")
