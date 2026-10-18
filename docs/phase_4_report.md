# =============================================================================
# SHADOWMIND — PHASE 4 COMPLETION REPORT: DYNAMIC HONEYPOT & DECEPTION ENGINE
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Overview
Phase 4 introduces the **Dynamic Honeypot and Deception Engine**. When an attacker attempts unauthorized access or slow exfiltration, ShadowMind automatically deploys deceptive traps, serves a fake corporate file share page to the attacker's browser, intercepts file clicks, and harvests precise telemetry (attacker IP, requested asset, interaction timestamp) for SOC analysts.

---

## 2. Architecture & Methodology

- **Decoy Manager (`src/honeypot/decoy_manager.py`):** Automatically deploys realistic trap files (`financial_passwords_2026.xlsx`, `aws_production_keys.env`, `customer_database_dump.sql`, etc.) on app startup (`main.py`).
- **Interaction Logger (`src/honeypot/interaction_log.py`):** Records attacker actions, IP addresses, and specific file clicks into `logs/honeypot_interactions.log`.
- **Traffic Redirector (`src/honeypot/redirector.py` & `dashboard_tab.py`):** Intercepts incoming malicious requests on port `8080`, serves an interactive corporate file share HTML interface to the attacker's browser, and triggers automated Poison Pill key rotation simultaneously.
- **Honeypot UI Tab (`ui/tabs/honeypot_tab.py`):** Displays active deception traps and live attacker interaction intel in real time.

---

## 3. Step-by-Step Live Testing & Demo Guide

### How to Test Phase 4 (Live Honeypot Attack Demo):
1. **Start ShadowMind on Laptop (Device C):**
   ```powershell
   python main.py
   ```
   Log in as `admin` and keep the **Dashboard** or **Honeypot** tab visible.
2. **Launch Attack from Phone (Device A):**
   - Open your phone's browser and visit your laptop's Wi-Fi IP address:
     `http://<laptop-ip>:8080/`
   - **Expected Hacker View:** Your phone displays a realistic corporate shared drive (`📁 INTERNAL SHARED DRIVE // SECURE_VAULT_BACKUP`).
   - **Interactive Trap:** Click on `aws_production_keys.env` or `financial_passwords_2026.xlsx`. Your browser shows a download interception screen.
3. **Verify Defender View (Laptop):**
   - ShadowMind Dashboard turns **Red (`CONFIRMED EXFILTRATION`)**.
   - Poison Pill Vault automatically rotates AES-256 keys in < 50ms.
   - Switch to the **Honeypot tab** on your laptop:
     - The **Attacker Interaction Log** instantly displays:
       `[HH:MM:SS] IP: 192.168.1.15 | Action: DOWNLOAD_ATTEMPT: aws_production_keys.env | Decoy Target: aws_production_keys.env`
     - **Attacker Diverted** counter increments.

---
*End of Phase 4 Report*
