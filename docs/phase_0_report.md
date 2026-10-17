# =============================================================================
# SHADOWMIND — PHASE 0 COMPLETION REPORT
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Overview
Phase 0 establishes the complete foundational architecture for ShadowMind, ensuring security, robust data handling, and a working desktop UI before implementing the deep learning and cryptographic engines.

---

## 2. What Was Done

### A. Security & Hardening (Baked in from Day 1)
- **Password Hashing:** Implemented bcrypt with configurable work factor (cost=12) in `src/auth/auth.py`. No plaintext passwords are ever stored.
- **Brute-Force Protection:** Added login attempt tracking with automatic account lockout after 5 failed attempts (`lockout_duration_seconds: 300`).
- **Role-Based Access Control (RBAC):** Defined `USER` and `ADMIN` roles. Restricted administrative features (Settings tab) to ADMIN only.
- **Input Sanitization:** Regex validation on usernames (`[A-Za-z0-9_.@-]{3,64}`) and IP addresses to prevent injection attacks.
- **Secure Storage:** SQLite database initialized with owner-only file permissions (`0o600` on Unix).
- **Git Security:** Comprehensive `.gitignore` configured to block `.env`, secrets, model weights, raw data captures, and SQLite databases from ever reaching GitHub.

### B. Core Architecture & Modules
- **Central Configuration (`configs/thresholds.yaml`):** All detection thresholds, TTL durations, key rotation parameters, and debug flags centralized in one YAML file.
- **Data Ingestion & Pipeline (`src/data/generator.py` & `preprocessor.py`):** Synthetic traffic generator (benign business-hours traffic vs. malicious low-and-slow exfiltration) + CICIDS2017 raw dataset support, feature normalization (MinMaxScaler), and LSTM sequence builders.
- **Desktop UI Skeleton (`ui/main_window.py` & tabs):** CustomTkinter dark-mode desktop app featuring:
  - Secure Login screen with input validation
  - Top bar with active session indicator and live TTL self-destruct countdown timer
  - **Dashboard Tab:** System status, threat level, session key state, threat graph container, and real-time event log
  - **File Vault Tab:** Protected files list, session key status, TTL countdown info, and emergency rotation trigger
  - **Honeypot Tab:** Active decoys list and attacker interaction live log
  - **Settings Tab (Admin Only):** Read-only configuration viewer displaying all active parameters from `thresholds.yaml`
- **Application Entry Point (`main.py`):** Performs startup safety checks (Python version, dependency verification), configures rotating file logging, bootstraps the default admin account on first run, and launches the UI.

---

## 3. Expected Output & Verification

When running `python main.py`:

1. **Console Output:**
   ```
   2026-10-18 00:43:10 [INFO] shadowmind.main — Synthetic dataset generated (6000 rows)
   2026-10-18 00:43:10 [INFO] src.auth.auth — Auth DB initialized
   2026-10-18 00:43:10 [INFO] src.auth.auth — [BOOTSTRAP] Default admin password: iD4Ywe-aEJwZcvJCWnAsZw
   2026-10-18 00:43:10 [INFO] shadowmind.main — UI launched
   ```

2. **Desktop Application Window:**
   - Opens a dark-themed CustomTkinter GUI titled **"ShadowMind — AI Defense System"**.
   - Prompts for username (`admin`) and the auto-generated password from the console.
   - Upon successful login, displays the 4-tab main interface with active session token management, live TTL countdown, and system status cards.

---
*End of Phase 0 Report*
