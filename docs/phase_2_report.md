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

## 4. Live Testing & Multi-Hop Demo Guide

### How to Test Phase 2 Live (3-Device Topology):
1. **Device C (Laptop):** Run `python main.py`, log in as `admin`.
2. **Device B (Phone 2 - Compromised Workstation):** Run `python proxy.py` (configured with your laptop's Wi-Fi IP on port `9000`).
3. **Device A (Phone 1 - Attacker):** Open browser and visit `http://<phone-2-ip>:9000/`.
4. **Expected Output:**
   - Phone 2 relays the request, preserving the original attacker IP via `X-Forwarded-For`.
   - ShadowMind intercepts the connection, runs it through the 3-way CNN+LSTM+GNN ensemble, and instantly triggers a **Red Alert (`CONFIRMED EXFILTRATION`)**.
   - The event log displays the precise topological path: 
     `HoneyGraph GNN Topology Alert: Device A (192.168.1.10) ➔ Device B Proxy (192.168.1.25) ➔ Vault (Laptop)`.

---
*End of Phase 2 Report*
