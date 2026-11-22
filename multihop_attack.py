# =============================================================================
# FILE: multihop_attack.py
# PURPOSE: Multi-Hop Attack Script for Laptop 2 (Attacker Device).
#          Routes attack probes through the intermediate phone proxy (Device B)
#          which tunnels into ShadowMind on Laptop 1 (Device C), triggering
#          the HoneyGraph GNN topology analyzer and IP HOPPING display.
#
# USAGE ON LAPTOP 2:
#     python multihop_attack.py [PHONE_PROXY_URL]
# Example:
#     python multihop_attack.py http://192.168.43.1:9000
# =============================================================================

import sys
import time
import os
import socket
import urllib.request
import urllib.error

def get_attacker_ip():
    """Detect the attacker laptop's local IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "10.28.82.21"

# =============================================================================
# 1. CONFIGURATION: PROXY URL & VAULT FILES (EASILY CHANGEABLE)
# =============================================================================
# Target Phone Proxy URL (Device B).
# e.g.: python multihop_attack.py http://192.168.43.1:9000
#   or: python multihop_attack.py http://192.168.43.1:9000 my_secret.txt
DEFAULT_PHONE_PROXY = "http://192.168.43.1:9000"

custom_file = None
if len(sys.argv) > 2:
    PROXY_URL = sys.argv[1]
    custom_file = sys.argv[2]
elif len(sys.argv) == 2:
    if sys.argv[1].startswith("http://") or sys.argv[1].startswith("https://") or ":" in sys.argv[1]:
        PROXY_URL = sys.argv[1]
    else:
        PROXY_URL = DEFAULT_PHONE_PROXY
        custom_file = sys.argv[1]
else:
    PROXY_URL = DEFAULT_PHONE_PROXY

# Normalize URL (Auto-convert tcp:// from Pinggy into http://)
if PROXY_URL.startswith("tcp://"):
    PROXY_URL = "http://" + PROXY_URL[6:]
elif not PROXY_URL.startswith("http://") and not PROXY_URL.startswith("https://"):
    PROXY_URL = f"http://{PROXY_URL}"

# --- EDIT OR ADD FILES TO FETCH FROM THE VAULT HERE ---
VAULT_FILES = [
    # (Friendly Description, Vault File Endpoint)
    ("Database Credentials",         "/vault/credentials.env.enc"),
    ("Customer SQL Database Dump",    "/vault/customer_database_dump.sql"),
    ("Proprietary Source Code",      "/vault/source_code.zip"),
    ("AWS Production Cloud Keys",     "/vault/aws_production_keys.env"),
    ("Corporate Financial Passwords","/vault/financial_passwords_2026.xlsx"),
    ("Executive Payroll & Salaries", "/vault/executive_payroll_salaries.pdf"),
    ("Internal Network Topology",    "/vault/internal_network_topology.txt"),
    ("R&D Secret Project Intel",     "/vault/secret_project_intel.txt"),
]

# If a specific custom file was passed in the command line, attack only that file:
if custom_file:
    clean_name = custom_file.strip("/").replace("vault/", "")
    VAULT_FILES = [(f"Custom Target File ({clean_name})", f"/vault/{clean_name}")]

# Delay in seconds between multi-hop requests
DELAY_BETWEEN_HOPS = 2.5

# Directory to save downloaded/intercepted files for verification
OUTPUT_DIR = "exfiltrated_multihop_evidence"

# =============================================================================
# 2. EXECUTION ENGINE
# =============================================================================
def run_multihop_attack():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    proxy = PROXY_URL.rstrip('/')
    
    print("=" * 75)
    print("  🌐 SHADOWMIND ATTACK SUITE // MULTI-HOP LATERAL ATTACK (IP HOPPING)")
    attacker_ip = get_attacker_ip()
    print("=" * 75)
    print(f" Intermediate Proxy (Hop 2) : {proxy}")
    print(f" Attacker Origin    (Hop 1) : {attacker_ip}")
    print(f" Attack Topology            : Attacker Laptop (Hop 1)")
    print(f"                               ➔ Phone Proxy Relay (Hop 2)")
    print(f"                               ➔ Target ShadowMind Vault (Hop 3)")
    print(f" Total Probes               : {len(VAULT_FILES)} endpoints")
    print(f" Inter-Hop Delay            : {DELAY_BETWEEN_HOPS} seconds")
    print(f" Evidence Folder            : ./{OUTPUT_DIR}/")
    print("=" * 75 + "\n")

    for idx, (label, endpoint) in enumerate(VAULT_FILES, 1):
        filename = endpoint.strip("/").split("/")[-1]
        sep = "&" if "?" in endpoint else "?"
        url = f"{proxy}{endpoint}{sep}src={attacker_ip}"
        
        print(f"[{idx}/{len(VAULT_FILES)}] 🌐 Routing through intermediate proxy: {label}")
        print(f"      Relay Target : GET {url}")
        
        headers = {
            "User-Agent": "ShadowMind-MultiHopClient/2.0",
            "X-Attack-Mode": "MultiHop",
            "X-Real-IP": attacker_ip,
            "X-Forwarded-For": attacker_ip,
            "Accept": "*/*"
        }
        
        req = urllib.request.Request(url, headers=headers)
        start_time = time.time()
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.status
                payload = response.read()
                latency_ms = (time.time() - start_time) * 1000
                
                # Save received evidence
                out_path = os.path.join(OUTPUT_DIR, f"multihop_{filename}")
                with open(out_path, "wb") as f:
                    f.write(payload)
                
                print(f"      Status       : {status_code} OK (Latency: {latency_ms:.1f}ms)")
                print(f"      Payload Size : {len(payload):,} bytes")
                
                # Check for Poison Pill watermark in payload
                preview = payload[:120].decode("utf-8", errors="ignore")
                if "POISON PILL" in preview or "CIPHERTEXT" in preview or "SHADOWMIND" in preview:
                    print(f"      Defense      : 🔒 [POISON PILL ENGAGED] Plaintext destroyed into unrecoverable ciphertext!")
                else:
                    print(f"      Defense      : Intercepted payload captured.")
                print(f"      Saved to     : {out_path}")
                
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start_time) * 1000
            err_body = e.read()
            print(f"      Status       : HTTP {e.code} ({latency_ms:.1f}ms)")
            print(f"      Response     : {err_body[:100].decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"      Error        : ❌ Proxy Relay Connection Failed: {e}")
            print(f"                     (Make sure the phone is running proxy.py on port 9000)")
            
        if idx < len(VAULT_FILES):
            print(f"      ⏳ Waiting {DELAY_BETWEEN_HOPS}s for lateral hop sequence...\n")
            time.sleep(DELAY_BETWEEN_HOPS)

    print("\n" + "=" * 75)
    print("  ✅ MULTI-HOP ATTACK COMPLETE")
    print("  📊 Check Target Laptop Dashboard:")
    print("     - Route: Hop 1 [Attacker IP] ➔ Hop 2 [Phone Relay IP] ➔ Target [Vault]")
    print("     - Status Badge: ● IP HOPPING (Crimson Active Alert)")
    print("     - GNN Radar: Dynamic Multi-Hop Graph Edge Constructed")
    print("=" * 75)


if __name__ == "__main__":
    run_multihop_attack()
