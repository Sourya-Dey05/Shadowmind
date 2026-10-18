# =============================================================================
# SHADOWMIND — PHASE 2 COMPLETION REPORT: HONEYGRAPH GNN & MULTI-HOP TELEMETRY
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Overview
Phase 2 introduces **HoneyGraph**, a Graph Neural Network (GNN) built with PyTorch Geometric that models the enterprise network topology as a connected graph (`hosts = nodes, flows = edges`). Combined with Phase 1's Spatial CNN and Temporal LSTM, ShadowMind now executes a powerful **3-way fusion ensemble** (`CNN + LSTM + GNN`) capable of detecting complex, distributed lateral movement and multi-hop proxy attacks.

---

## 2. Architecture & Methodology

- **Enterprise Graph Builder (`src/data/graph_builder.py`):** Converts network traffic flows and host communication logs into PyTorch Geometric `Data` graph objects.
- **HoneyGraph GNN (`src/detection/gnn.py`):** Employs Graph Convolutional Networks (GCNConv) to perform message passing across neighboring hosts and network flows, detecting coordinated exfiltration that appears benign in isolation.
- **3-Way Fusion MLP (`src/detection/mlp.py`):** Concatenates spatial (32), temporal (32), and topological (32) embeddings (96 dims total) to compute a high-precision risk score probability `[0, 1]`.
- **Multi-Hop Network Telemetry (`ui/tabs/dashboard_tab.py` & `proxy.py`):** 
  - Integrated local HTTP listener on port `8080`.
  - Supports `X-Forwarded-For` header inspection via `proxy.py` (deployed on Phone 2 / Device B) to trace complete multi-hop attack routes (`Device A ➔ Device B Proxy ➔ Vault Laptop`).

---

## 3. Training & Evaluation Metrics

- **Test Accuracy:** **99.98%**
- **Precision:** **0.9996**
- **Recall:** **1.0000**
- **F1-Score:** **0.9998**
- **Confusion Matrix:** 2,370 True Negatives, 2,381 True Positives, 1 False Positive, 0 False Negatives.

---

## 4. Step-by-Step Live Testing & Multi-Hop Demo Guide

### Prerequisites
- All three devices (**Device A - Attacker Phone**, **Device B - Proxy Phone**, **Device C - Laptop**) must be connected to the **same Wi-Fi network**.

---

### Step 1: Start ShadowMind on Device C (Laptop)
1. Open PowerShell on your laptop:
   ```powershell
   cd D:\Shadowmind
   .venv\Scripts\activate
   python main.py
   ```
2. Log in using your `admin` credentials. Keep the **Dashboard tab** visible to the invigilator.

---

### Step 2: Configure and Run `proxy.py` on Device B (Phone 2 / Termux)
1. Open **Termux** on Phone 2.
2. Install Python if not already installed:
   ```bash
   pkg update && pkg install python -y
   ```
3. Create the proxy script using `nano`:
   ```bash
   nano proxy.py
   ```
4. Paste this exact code into Termux:
   ```python
   import http.server
   import urllib.request

   LAPTOP_IP = "YOUR_LAPTOP_WIFI_IP"  # e.g. "192.168.1.50"
   PORT = 8080
   LISTEN_PORT = 9000

   class MultiHopProxyHandler(http.server.BaseHTTPRequestHandler):
       def do_GET(self):
           target_url = f"http://{LAPTOP_IP}:{PORT}{self.path}"
           attacker_ip = self.client_address[0]
           print(f"[HOP 2] Attacker: {attacker_ip} ➔ Relaying to Vault: {target_url}")

           headers = {"X-Forwarded-For": attacker_ip}
           req = urllib.request.Request(target_url, headers=headers)

           try:
               resp = urllib.request.urlopen(req)
               self.send_response(resp.status)
               self.end_headers()
               self.wfile.write(resp.read())
           except Exception as e:
               self.send_response(500)
               self.end_headers()
               self.wfile.write(str(e).encode())

       def log_message(self, format, *args):
           return

   if __name__ == "__main__":
       print(f"Proxy relay running on port {LISTEN_PORT}...")
       http.server.HTTPServer(('', LISTEN_PORT), MultiHopProxyHandler).serve_forever()
   ```
   *(Replace `"YOUR_LAPTOP_WIFI_IP"` with your laptop's actual IPv4 address found via `ipconfig`).*
5. Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`).
6. Run the proxy script:
   ```bash
   python proxy.py
   ```
7. Note down Phone 2's local IP address (run `ifconfig` in Termux, e.g., `192.168.1.75`).

---

### Step 3: Launch Attack from Device A (Phone 1)
1. On **Phone 1**, open your mobile web browser.
2. Navigate to Phone 2's proxy listener on port 9000:
   `http://<PHONE_2_IP>:9000/` (e.g., `http://192.168.1.75:9000/`).

---

### Step 4: Verify Live Detection on Laptop (Device C)
- **Expected Result:**
  - Phone 1's request is relayed through Phone 2 (Termux).
  - ShadowMind instantly intercepts the cross-device multi-hop flow.
  - The Dashboard threat score jumps above `0.9100`, turning **Red (`CONFIRMED EXFILTRATION`)**.
  - The Event Log prints:
    `HoneyGraph GNN Topology Alert: Device A (<Phone-1-IP>) ➔ Device B Proxy (<Phone-2-IP>) ➔ Vault (Laptop)`

---
*End of Phase 2 Report*
