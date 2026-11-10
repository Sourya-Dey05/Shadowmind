# =============================================================================
# FILE: multihop_attack.py
# PURPOSE: Multi-Hop Attack Script for Laptop 2 (Attacker Device).
#          Sends attack probes through the intermediate phone proxy (Device B)
#          which tunnels into ShadowMind on Laptop 1 (Device C), triggering
#          the HoneyGraph GNN topology analyzer and trace logging.
# =============================================================================

import requests
import time

# --- CONFIGURE THESE FOR YOUR DEMO ---
PHONE_PROXY_IP = "192.168.1.75"  # Replace with Phone 2's Wi-Fi IP address running proxy.py
PROXY_PORT = 9000

PATHS = [
    "/vault/credentials.env.enc",
    "/vault/customer_database_dump.sql",
    "/vault/source_code.zip",
    "/vault/aws_production_keys.env"
]

print("🌐 STARTING MULTI-HOP LATERAL MOVEMENT ATTACK (GNN DEMO)")
print("=" * 65)
print(f"Route: Attacker ➔ Phone Proxy ({PHONE_PROXY_IP}:{PROXY_PORT}) ➔ Target Laptop Vault")
print("=" * 65 + "\n")

for i, path in enumerate(PATHS, 1):
    url = f"http://{PHONE_PROXY_IP}:{PROXY_PORT}{path}"
    print(f"[{i}/4] Routing attack through proxy ➔ GET {path}")
    try:
        start = time.time()
        resp = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        print(f"      Status: {resp.status_code} | Size: {len(resp.content)} bytes | Latency: {latency:.1f}ms")
    except Exception as e:
        print(f"      Connection Error: {e}")
    
    print("      ⏳ Waiting 2 seconds before next multi-hop hop...\n")
    time.sleep(2)

print("✅ MULTI-HOP ATTACK COMPLETE.")
print("📊 Check Laptop 1's Dashboard for HoneyGraph GNN Topology Alert!")
