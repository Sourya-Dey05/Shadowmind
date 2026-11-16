# =============================================================================
# FILE: serial_attack.py
# PURPOSE: Serial (Sequential) Attack Simulation Script for Attacker Laptop.
#          Sends low-and-slow sequential probes to the target ShadowMind gateway,
#          simulating stealthy reconnaissance and beaconing over time.
# =============================================================================

import requests
import time
import sys

# --- CONFIGURE TARGET URL (Can be local IP:8080 or Cloudflare Tunnel URL) ---
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.29.250:8080"

ENDPOINTS = [
    ("Credential Probe", "/vault/credentials.env.enc"),
    ("Database Dump", "/vault/customer_database_dump.sql"),
    ("Source Code Exfil", "/vault/source_code.zip"),
    ("API Keys Access", "/vault/aws_production_keys.env")
]

print("🔴 STARTING SERIAL (SEQUENTIAL) ATTACK SIMULATION...")
print("=" * 65)
print(f"Target: {TARGET_URL}\n")

for i, (desc, path) in enumerate(ENDPOINTS, 1):
    url = f"{TARGET_URL.rstrip('/')}{path}"
    print(f"[{i}/4] Executing {desc} ➔ GET {path}")
    try:
        start = time.time()
        resp = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        print(f"      Status: {resp.status_code} | Size: {len(resp.content)} bytes | Latency: {latency:.1f}ms")
    except Exception as e:
        print(f"      Connection Error: {e}")
    
    print("      ⏳ Waiting 3 seconds before next sequential request...\n")
    time.sleep(3)  # Sequential low-and-slow delay

print("✅ SERIAL ATTACK COMPLETE.")
print("📊 Check Target Laptop Dashboard for Confirmed Exfiltration & Vault Auto-Encryption!")
