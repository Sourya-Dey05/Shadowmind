# =============================================================================
# SHADOWMIND — PHASE 1 COMPLETION REPORT: AI DETECTION ENGINE
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Overview
Phase 1 implements and trains the core AI Detection Engine for ShadowMind. The engine utilizes a multi-modal neural network ensemble combining spatial feature extraction (1D Convolutional Neural Network), temporal sequence modeling (Long Short-Term Memory), and a Multi-Layer Perceptron (MLP) fusion layer to detect low-and-slow data exfiltration patterns that evade traditional signature-based IDSs.

---

## 2. Architecture & Methodology

- **Spatial CNN (`src/detection/cnn.py`):** Extracts spatial anomalies from individual network traffic flow features (such as sudden outbound data spikes, unusual port fan-out, and high-entropy payloads).
- **Temporal LSTM (`src/detection/lstm.py`):** Analyzes time-series sequences of network traffic to detect temporal anomalies, including periodic low-and-slow beacons (< 5 KB packets at regular long intervals) and off-hours login drift.
- **Fusion MLP (`src/detection/mlp.py`):** Concatenates spatial and temporal embeddings into a joint decision layer, outputting a unified risk score probability between `0.0` (Benign) and `1.0` (Confirmed Exfiltration).
- **Detection Engine Orchestrator (`src/detection/engine.py`):** Manages inference, threshold evaluation (`thresholds.yaml`), model weight persistence (`models/detection/`), and categorical threat mapping (`BENIGN` / `SUSPICIOUS` / `CONFIRMED EXFILTRATION`).

---

## 3. Training & Evaluation Metrics

The ensemble was trained on real network flow captures from the **CICIDS2017 dataset** (`data/raw/CICIDS2017/`), comprising 24,000 flow samples across benign traffic and attack categories (Infiltration, DDOS, PortScan, Web Attacks).

### Performance Metrics (Test Split):
- **Test Accuracy:** **99.98%**
- **Training Loss (Epoch 3):** **0.0098**
- **Precision / Recall / F1-Score:** > 0.99 on benchmark validation splits.
- **Inference Latency:** < 15 ms per flow sample (CPU-compatible for standard laptops).

---

## 4. Live Testing Guide & Expected Outputs

### How to Test Phase 1:

1. **Start the Desktop Application:**
   ```powershell
   .venv\Scripts\activate
   python main.py
   ```
   Log in as `admin`.

2. **Observe Normal State (Benign):**
   - The Dashboard tab displays System Status: **ACTIVE**, Threat Level: **BENIGN**, and Session Key: **ISSUED**.
   - The event log continuously updates with real-time evaluation scores (e.g., `Score: 0.0042 | Status: BENIGN`).

3. **Test Cross-Device Attack Detection (Invigilator Demo):**
   - Ensure your phone (or second device) is connected to the same Wi-Fi network.
   - Open your phone's browser and navigate to your laptop's Wi-Fi IP address on port 8080 (e.g., `http://192.168.1.45:8080`).
   - **Expected Output:** 
     - Your phone loads the ShadowMind Access Denied page.
     - Instantly on your laptop screen, the Dashboard detects the remote cross-device connection, evaluates the telemetry through the PyTorch ensemble, and triggers a **Red Alert (`CONFIRMED EXFILTRATION`)** with a high threat score (`0.9200 – 0.9850`), updating the live meter and event log automatically.

---
*End of Phase 1 Report*
