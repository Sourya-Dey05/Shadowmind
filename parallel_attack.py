# =============================================================================
# FILE: parallel_attack.py
# PURPOSE: Parallel (Concurrent Multi-Threaded Flood) Attack Simulation Script.
#          Dispatches simultaneous threads to inundate the target ShadowMind
#          gateway, testing HoneyGraph GNN rapid graph construction and
#          multi-threaded defense. Zero external dependencies.
# =============================================================================

import sys
import time
import os
import concurrent.futures
import urllib.request
import urllib.error

# =============================================================================
# 1. CONFIGURATION: TARGET URL & VAULT FILES (EASILY CHANGEABLE)
# =============================================================================
# You can pass the target URL and an OPTIONAL custom file from CLI:
#     python parallel_attack.py http://192.168.1.50:8080
#     python parallel_attack.py http://192.168.1.50:8080 my_secret.txt
#     python parallel_attack.py my_secret.txt
DEFAULT_TARGET_URL = "http://192.168.29.250:8080"

custom_file = None
if len(sys.argv) > 2:
    TARGET_URL = sys.argv[1]
    custom_file = sys.argv[2]
elif len(sys.argv) == 2:
    arg1 = sys.argv[1]
    if arg1.startswith("http://") or arg1.startswith("https://") or arg1.startswith("tcp://") or ":" in arg1:
        TARGET_URL = arg1
    else:
        TARGET_URL = DEFAULT_TARGET_URL
        custom_file = arg1
else:
    TARGET_URL = DEFAULT_TARGET_URL

# Normalize URL (Auto-convert tcp:// from Pinggy into http://)
if TARGET_URL.startswith("tcp://"):
    TARGET_URL = "http://" + TARGET_URL[6:]
elif not TARGET_URL.startswith("http://") and not TARGET_URL.startswith("https://"):
    TARGET_URL = "http://" + TARGET_URL

# --- EDIT OR ADD FILES TO FETCH FROM THE VAULT SIMULTANEOUSLY ---
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

# Number of concurrent attack worker threads (or match custom file count)
CONCURRENT_THREADS = min(8, max(2, len(VAULT_FILES)))

# Directory to save downloaded/intercepted files for verification
OUTPUT_DIR = "exfiltrated_parallel_evidence"

# =============================================================================
# 2. WORKER FUNCTION
# =============================================================================
def exfiltrate_worker(item):
    thread_id, (label, endpoint) = item
    filename = endpoint.strip("/").split("/")[-1]
    url = f"{TARGET_URL.rstrip('/')}{endpoint}"
    
    headers = {
        "User-Agent": f"ShadowMind-ParallelBlitz/2.0 (Worker-{thread_id})",
        "X-Attack-Mode": "Parallel",
        "Accept": "*/*"
    }
    
    req = urllib.request.Request(url, headers=headers)
    start_time = time.time()
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = response.read()
            latency_ms = (time.time() - start_time) * 1000
            
            # Save received evidence
            out_path = os.path.join(OUTPUT_DIR, f"parallel_{filename}")
            with open(out_path, "wb") as f:
                f.write(payload)
                
            is_poison = b"POISON PILL" in payload or b"CIPHERTEXT" in payload or b"SHADOWMIND" in payload
            return {
                "thread": thread_id,
                "label": label,
                "endpoint": endpoint,
                "status": response.status,
                "bytes": len(payload),
                "latency_ms": latency_ms,
                "is_poison": is_poison,
                "path": out_path,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "thread": thread_id,
            "label": label,
            "endpoint": endpoint,
            "status": e.code,
            "bytes": 0,
            "latency_ms": latency_ms,
            "is_poison": False,
            "path": None,
            "error": f"HTTP {e.code}"
        }
    except Exception as e:
        return {
            "thread": thread_id,
            "label": label,
            "endpoint": endpoint,
            "status": 0,
            "bytes": 0,
            "latency_ms": 0,
            "is_poison": False,
            "path": None,
            "error": str(e)
        }

# =============================================================================
# 3. EXECUTION ENGINE
# =============================================================================
def run_parallel_attack():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    target = TARGET_URL.rstrip('/')
    
    print("=" * 75)
    print("  🔵 SHADOWMIND ATTACK SUITE // DIRECT PARALLEL (CONCURRENT) FLOOD")
    print("=" * 75)
    print(f" Target Gateway : {target}")
    print(f" Attack Mode    : Concurrent Multi-Threaded Flood (No Intermediate Relay)")
    print(f" Parallel Threads: {CONCURRENT_THREADS}")
    print(f" Total Endpoints: {len(VAULT_FILES)}")
    print(f" Evidence Folder: ./{OUTPUT_DIR}/")
    print("=" * 75 + "\n")
    print("⚡ Launching simultaneous worker threads across network sockets...\n")

    items = [(i + 1, file_tuple) for i, file_tuple in enumerate(VAULT_FILES)]
    start_all = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        future_map = {executor.submit(exfiltrate_worker, item): item for item in items}
        for future in concurrent.futures.as_completed(future_map):
            res = future.result()
            t_num = res["thread"]
            lbl = res["label"]
            ep = res["endpoint"]
            lat = res["latency_ms"]
            
            if res["error"]:
                print(f"  ❌ [Worker {t_num:02d}] {lbl} ({ep}) ➔ Failed: {res['error']}")
            else:
                poison_tag = "🔒 [POISON PILL TRAPPED]" if res["is_poison"] else "📥 [CAPTURED]"
                print(f"  ⚡ [Worker {t_num:02d}] {lbl} ➔ {res['status']} OK | {res['bytes']:,} bytes in {lat:.1f}ms {poison_tag}")

    total_duration_ms = (time.time() - start_all) * 1000
    print("\n" + "=" * 75)
    print(f"  ✅ PARALLEL ATTACK COMPLETE in {total_duration_ms:.2f} ms")
    print("  📊 Check Target Laptop Dashboard:")
    print("     - Route: Direct Source ➔ Target Enclave (NO IP Hopping)")
    print("     - Status Badge: ● PARALLEL")
    print("     - Defense: DEFCON 1 · CONCURRENT FLOOD & Vault Auto-Encryption")
    print("=" * 75)


if __name__ == "__main__":
    run_parallel_attack()
