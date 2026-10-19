# =============================================================================
# SHADOWMIND — PHASE 5 COMPLETION REPORT: PIPELINE ORCHESTRATION & LOCAL STORAGE VAULT
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Overview
Phase 5 finalizes the **Master Pipeline Orchestrator (`src/orchestrator.py`)** and the **Physical Local Storage Vault (`src/workspace/workspace_vault.py`)**. It unifies all five pillars into a single end-to-end autonomous defense loop, enabling frictionless local file creation in Windows (`/Vault` folder) with automated in-place AES-256 encryption upon breach detection.

---

## 2. Architecture & Methodology

- **Master Orchestrator (`src/orchestrator.py`):** Unifies Telemetry Ingestion ➔ 3-Way ML Ensemble Prediction (CNN+LSTM+GNN) ➔ Poison Pill Vault Rotation ➔ Dynamic Honeypot Redirection ➔ Local Storage Auto-Encryption ➔ TTL RAM Zero-Wipe.
- **Physical Local Storage Vault (`src/workspace/workspace_vault.py`):** Automatically creates a physical `/Vault` folder (`D:\Shadowmind\Vault`) on app startup. Users work in plaintext normally; upon attack detection, files are auto-encrypted into `.enc` ciphertext in place.
- **TTL Privacy Wipe (`ui/tabs/vault_tab.py`):** Automatically clears unencrypted plaintext files from the physical `/Vault` folder upon session logout or app close, ensuring zero disk retention of sensitive data.
- **End-to-End Integration Tests (`tests/test_integration.py`):** Verified automated attack simulation pipeline passing all assertions successfully.

---

## 3. Step-by-Step Live Demo & Testing Guide

### How to Demo Phase 5 (The Grand Finale):
1. **Launch ShadowMind:**
   ```powershell
   python main.py
   ```
   Log in as `admin`.
2. **Local Windows Work:**
   - Open your file explorer to `D:\Shadowmind\Vault`. Create a normal text file (`my_secrets.txt`) and type anything in plaintext.
   - Look at ShadowMind's **File Vault tab**—it tracks the file live as `📄 [PLAIN] my_secrets.txt`.
3. **Simulate the Attack (From Phone / Proxy):**
   - On your phone, visit your laptop's IP address: `http://<laptop-ip>:8080/`
4. **Witness the Automated Defense:**
   - ShadowMind Dashboard turns **Red (`CONFIRMED EXFILTRATION`)**.
   - Honeypot intercepts the request and serves the fake corporate shared drive.
   - **Local Storage Vault Auto-Encrypts:** The physical `my_secrets.txt` file in `D:\Shadowmind\Vault` is instantly converted into `my_secrets.txt.enc` ciphertext in milliseconds!
   - Poison Pill Vault rotates session keys in RAM.
   - When you log out or close ShadowMind, plaintext files are wiped for privacy.

---
*End of Phase 5 Report*
