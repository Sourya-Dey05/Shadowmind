# =============================================================================
# FILE: serial_attack.py
# PURPOSE: Serial (Sequential Probes) Attack Simulation Script for Attacker Laptop.
#          Sends stealthy, low-and-slow sequential requests to the target
#          ShadowMind Vault. Zero external dependencies (uses standard library).
# =============================================================================

import sys
import time
import os
import urllib.request
import urllib.error

# =============================================================================
# 1. CONFIGURATION: TARGET URL & VAULT FILES (EASILY CHANGEABLE)
# =============================================================================
# You can pass the target URL as a command line argument, e.g.:
#     python serial_attack.py http://192.168.1.50:8080
# or: python serial_attack.py https://your-tunnel.trycloudflare.com
DEFAULT_TARGET_URL = "http://192.168.29.250:8080"
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET_URL

# --- EDIT OR ADD FILES TO FETCH FROM THE VAULT HERE ---
VAULT_FILES = [
    # (Friendly Description, Vault File Endpoint)
    ("Database Credentials",      "/vault/credentials.env.enc"),
    ("Customer SQL Database Dump", "/vault/customer_database_dump.sql"),
    ("Proprietary Source Code",   "/vault/source_code.zip"),
    ("AWS Production Cloud Keys",  "/vault/aws_production_keys.env"),
    ("Corporate Financial Passwords", "/vault/financial_passwords_2026.xlsx"),
    ("Executive Payroll & Salaries",  "/vault/executive_payroll_salaries.pdf"),
    ("Internal Network Topology", "/vault/internal_network_topology.txt"),
    ("R&D Secret Project Intel",  "/vault/secret_project_intel.txt"),
]

# Delay in seconds between sequential requests (low-and-slow simulation)
DELAY_BETWEEN_REQUESTS = 3.0

# Directory to save downloaded/intercepted files for verification
OUTPUT_DIR = "exfiltrated_serial_evidence"

# =============================================================================
# 2. EXECUTION ENGINE
# =============================================================================
def run_serial_attack():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = TARGET_URL.rstrip('/')
    
    print("=" * 75)
    print("  🔴 SHADOWMIND ATTACK SUITE // DIRECT SERIAL (SEQUENTIAL) ATTACK")
    print("=" * 75)
    print(f" Target Gateway : {target}")
    print(f" Attack Mode    : Direct Sequential (No Intermediate Relay)")
    print(f" Total Probes   : {len(VAULT_FILES)} endpoints")
    print(f" Inter-Probe Gap: {DELAY_BETWEEN_REQUESTS} seconds")
    print(f" Evidence Folder: ./{OUTPUT_DIR}/")
    print("=" * 75 + "\n")

    for idx, (label, endpoint) in enumerate(VAULT_FILES, 1):
        filename = endpoint.strip("/").split("/")[-1]
        url = f"{target}{endpoint}"
        
        print(f"[{idx}/{len(VAULT_FILES)}] 🎯 Requesting: {label}")
        print(f"      Endpoint : GET {endpoint}")
        
        headers = {
            "User-Agent": "ShadowMind-SerialRecon/2.0",
            "X-Attack-Mode": "Serial",
            "Accept": "*/*"
        }
        
        req = urllib.request.Request(url, headers=headers)
        start_time = time.time()
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.status
                payload = response.read()
                latency_ms = (time.time() - start_time) * 1000
                
                # Save received evidence
                out_path = os.path.join(OUTPUT_DIR, f"serial_{filename}")
                with open(out_path, "wb") as f:
                    f.write(payload)
                
                print(f"      Status   : {status_code} OK")
                print(f"      Size     : {len(payload):,} bytes (Latency: {latency_ms:.1f}ms)")
                
                # Check for Poison Pill watermark in payload
                preview = payload[:120].decode("utf-8", errors="ignore")
                if "POISON PILL" in preview or "CIPHERTEXT" in preview or "SHADOWMIND" in preview:
                    print(f"      Defense  : 🔒 [POISON PILL DETECTED] Plaintext destroyed into unrecoverable ciphertext!")
                else:
                    print(f"      Defense  : Intercepted payload captured.")
                print(f"      Saved to : {out_path}")
                
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start_time) * 1000
            err_body = e.read()
            print(f"      Status   : HTTP {e.code} ({latency_ms:.1f}ms)")
            if e.code in (401, 403):
                print(f"      Defense  : 🛡️ Access blocked by ShadowMind Zero-Trust Policy.")
        except Exception as e:
            print(f"      Error    : ❌ Connection failed ({e})")
            
        if idx < len(VAULT_FILES):
            print(f"      ⏳ Pausing {DELAY_BETWEEN_REQUESTS}s (simulating stealth reconnaissance)...\n")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print("\n" + "=" * 75)
    print("  ✅ SERIAL ATTACK RUN COMPLETE")
    print("  📊 Check Target Laptop Dashboard:")
    print("     - Route: Direct Source ➔ Target Enclave (NO IP Hopping)")
    print("     - Status Badge: ● SERIAL")
    print("     - Defense: Poison Pill Key Rotation & AES-256 Ciphertext Enforced")
    print("=" * 75)


if __name__ == "__main__":
    run_serial_attack()
