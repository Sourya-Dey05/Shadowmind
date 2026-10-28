# =============================================================================
# SHADOWMIND — ACADEMIC NOVELTY & LITERATURE COMPARISON REPORT
# Group GRP-45 |
# =============================================================================

## 1. Introduction & Research Context
Traditional intrusion detection systems (IDS) and data loss prevention (DLP) frameworks operate in isolated silos. Prior literature establishes deep learning for intrusion detection (Ferrag et al., 2020; Di Mauro et al., 2020), graph neural networks for network topology analysis (Caville et al., 2022; Zhong et al., 2024), and machine learning for dynamic honeypots (Zhang & Shi, 2023). However, existing research fails to integrate **real-time AI intrusion detection, enterprise graph reasoning, automated emergency key re-encryption, and time-bound RAM self-destruction into a single autonomous pipeline**.

ShadowMind bridges this critical research gap by introducing a closed-loop adaptive defense system.

---

## 2. Literature Survey & Research Gap Comparison

| Related Work / Study | Approach & Limitation | ShadowMind's Novel Contribution |
|---|---|---|
| **Ferrag et al. (2020)**<br>*Deep learning for IDS* | Focuses on isolated deep learning models (CNN, RNN) for network traffic classification. **Limitation:** Detects and alerts only; lacks automated post-breach cryptographic response. | Pairs the AI detection engine with an automated **Poison Pill Vault** that neutralizes stolen data in milliseconds. |
| **Caville et al. (2022) & Zhong et al. (2024)**<br>*GNN-based IDS / Anomaly-E* | Uses Graph Neural Networks to model flow relationships and network topology. **Limitation:** Restricted to detection without active deception or dynamic asset re-encryption. | Combines **HoneyGraph GNN** message passing with a **Dynamic Honeypot** to actively misdirect attackers while locking real assets. |
| **Zhang & Shi (2023)**<br>*ML-based dynamic honeypot* | Demonstrates machine learning configured dynamic honeypots for attacker diversion. **Limitation:** Operates independently without coupling to cryptographic file enclaves. | Fuses dynamic deception directly with the **Poison Pill Vault**, creating an autonomous loop from detection ➔ deception ➔ key rotation. |
| **NIST SP 800-207 (2020)**<br>*Zero Trust Architecture* | Defines architectural shifts for securing users, assets, and resources. **Limitation:** Lacks real-time AI adaptive response and ephemeral RAM key management. | Implements **TTL Self-Destruct** (RAM zero-wipe) and per-session GAN/secure keys to guarantee zero persistent key windows. |

---

## 3. Core Academic Novelty & Original Contributions

1. **3-Way Fusion Ensemble (CNN + LSTM + HoneyGraph GNN):**
   - Catches both spatial anomalies (single-flow packet size spikes), temporal anomalies (low-and-slow periodic <5KB beacons over weeks), and topological anomalies (coordinated multi-hop lateral movement across enterprise nodes).
2. **Autonomous Counter-Measure Loop (< 50ms):**
   - Eliminates human latency in SOC response by instantly triggering physical vault folder auto-encryption and RAM key rotation upon `CONFIRMED EXFILTRATION`.
3. **Dual-Layer Ephemeral Cryptography:**
   - Combines per-session AES-256 Fernet keys with low-level RAM zero-wipes (`memset`) on session exit, ensuring compromised keys cannot be reused after logoff.
4. **Standalone Zero-Dependency Desktop Architecture:**
   - Proves that advanced zero-trust defense systems can run offline on standard hardware without enterprise cloud infrastructure.

---
*End of Academic Novelty Report*
