# =============================================================================
# FILE: parallel_attack.py
# PURPOSE: Parallel (Concurrent) Attack Simulation Script for Attacker Laptop.
#          Dispatches multiple simultaneous threads to flood the target gateway,
#          triggering mass exfiltration, HoneyGraph GNN analysis, and instant
#          Poison Pill key rotation.
# =============================================================================

import requests
import concurrent.futures
import time
import sys

# --- CONFIGURE TARGET URL (Can be local IP:8080 or Cloudflare Tunnel URL) ---
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
        start = time.time()
        resp = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        return f"⚡ Target Hit {path} ➔ Status: {resp.status_code} ({len(resp.content)} bytes) in {latency:.1f}ms"
    except Exception as e:
        return f"❌ Target Miss {path} ➔ Error: {e}"

print("🔵 STARTING PARALLEL (CONCURRENT) ATTACK SIMULATION...")
print("=" * 65)
print(f"Target: {TARGET_URL}")
print(f"Dispatching 6 simultaneous threads...\n")

start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(hit_target, p) for p in PATHS]
    for future in concurrent.futures.as_completed(futures):
        print(f"  {future.result()}")

total_time = (time.time() - start_time) * 1000
print(f"\n✅ PARALLEL ATTACK COMPLETE in {total_time:.2f} ms.")
print("📊 Check Target Laptop Dashboard for GNN Topology Alert & Auto-Encryption!")
