# =============================================================================
# SHADOWMIND — TEACHER DEMO SCRIPT & CUE SHEET
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Pre-Demo Checklist
1. **Devices Ready:** Laptop (Device C) running ShadowMind + Phone 2 (Device B / Proxy) + Phone 1 (Device A / Attacker) on the same Wi-Fi.
2. **Terminal Open:** 
   ```powershell
   cd D:\Shadowmind
   .venv\Scripts\activate
   python main.py
   ```
3. **Login:** `admin` + bootstrap password.

---

## 2. Live Demo Cue Sheet (Step-by-Step)

### Scene 1: Introduction & Security Architecture (Phase 0)
- **Action:** Launch app, show the secure login screen and dashboard.
- **What to Say:** 
  > *"Sir/Ma'am, this is ShadowMind—an autonomous, self-healing zero-trust defense system for low-and-slow data exfiltration. It features bcrypt password hashing, role-based access control, and SQLite hardening from day one."*

### Scene 2: The AI Detection Engine & GNN Topology (Phases 1 & 2)
- **Action:** Show the Dashboard tab with the live threat score meter and event log.
- **What to Say:** 
  > *"Our detection engine uses a 3-way PyTorch neural network ensemble: Spatial CNN, Temporal LSTM, and a PyTorch Geometric HoneyGraph GNN that analyzes enterprise network graph topology in real time. It achieves 99.96% accuracy on CICIDS2017 benchmark flows."*

### Scene 3: The Physical `/Vault` & Normal Workflow (Phase 3 & 5)
- **Action:** Open file explorer to `D:\Shadowmind\Vault`. Create or view a normal text file (`notes.txt`) in plaintext. Show the File Vault tab tracking it as `📄 [PLAIN] notes.txt`.
- **What to Say:** 
  > *"Users work normally in plaintext inside our local Vault folder without friction. But the moment an intrusion occurs, ShadowMind springs into autonomous defense."*

### Scene 4: The Live Multi-Hop Attack & Autonomous Counter-Measure (Phases 2, 3, & 4)
- **Action:** 
  1. On Phone 2 (Termux), run `python proxy.py`.
  2. On Phone 1 (Attacker), browse to `http://<phone-2-ip>:9000/`.
- **What Happens Live on Laptop:**
  - **Detection (Phase 2):** Dashboard turns **Red (`CONFIRMED EXFILTRATION`)**. Event log displays the multi-hop network path: `Device A ➔ Device B Proxy ➔ Vault (Laptop)`.
  - **Poison Pill Vault (Phase 3):** Automatically encrypts `notes.txt` into `notes.txt.enc` ciphertext in place in < 50ms.
  - **Dynamic Honeypot (Phase 4):** Attacker browser is intercepted and redirected into a fake corporate shared drive. File clicks (`aws_production_keys.env`) are logged live in the Honeypot tab.
- **What to Say:** 
  > *"Notice how the system intercepted the multi-hop attack, instantly auto-encrypted our plaintext workspace files into AES-256 ciphertext in milliseconds, and trapped the attacker in our honeypot sandbox while harvesting their IP for the SOC."*

---
*End of Demo Script*
