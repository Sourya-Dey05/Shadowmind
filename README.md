# ShadowMind — An Adaptive Cyber Defense System

> **An Integrated Framework for Slow Attack Detection, Dynamic Deception, and Zero-Trust File Protection**

[![Status](https://img.shields.io/badge/status-prototype%20%2F%20Colab-blue)](#overview)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](#tech-stack)
[![Group](https://img.shields.io/badge/group-GRP--45-lightgrey)](#team--credits)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

Source: `SHADOWMIND_GRP-45.pdf` (12 pages, Canva — 2026-09-09) + `ShadowMind.pptx` by **Sourya Dey**. This README is a structured synthesis of that deck.

---

## Table of Contents

- [Overview](#overview)
- [Problem Identification — The Silent Heist](#problem-identification--the-silent-heist)
- [Literature Survey](#literature-survey)
- [Research Gap & Justification](#research-gap--justification)
- [Novelty & Original Contribution](#novelty--original-contribution)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
- [Workflow Demonstration](#workflow-demonstration)
- [Results & Expected Outcomes](#results--expected-outcomes)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Future Scope](#future-scope)
- [Limitations](#limitations--assumptions)
- [References](#references)
- [Team & Credits](#team--credits)

---

## Overview

**ShadowMind** unifies three pillars into a single adaptive pipeline to defeat **low-and-slow** exfiltration:

1. **AI Detection Engine** — CNN (spatial) + LSTM (temporal) + MLP fusion, augmented by a GNN graph layer (*HoneyGraph*) that reasons over the whole network topology.
2. **Dynamic Deception** — an ML-driven honeypot that adapts decoys to attacker behavior, wastes attacker time, and harvests intelligence.
3. **Zero-Trust File Protection** — the *Poison Pill Vault* with GAN-generated per-session keys, **millisecond emergency rotation** on breach, and **TTL self-destruct** that zero-wipes keys from RAM at session expiry.

Core promise: even if an attacker slowly steals data over months, the stolen bytes are rendered **cryptographically useless within milliseconds**, and no usable key survives past the user's session.

> Thesis: move from a static "fortress" perimeter to a **self-healing, zero-trust immune system** that detects → deceives → destroys keys on demand.

Maturity: **simulated / Google Colab prototype** that runs on standard laptops without enterprise infrastructure. 99%+ accuracy target is a design goal pending validation on a labeled slow-attack dataset.

---

## Problem Identification — The Silent Heist

> "Imagine a thief who does not break down the door but slowly picks the lock — one tiny turn every hour while you are asleep. That is exactly how slow cyber attacks work."

| Dimension | What happens |
|---|---|
| **Low Visibility** | Attackers send tiny packets (< 5 KB) at random intervals, mimicking legitimate user traffic to stay under the radar. |
| **Long Dwell Time** | Attackers can remain hidden for **6–12 months**, quietly exfiltrating data the entire time. |
| **The Fatal Blow** | Traditional tools alert only **after** damage — e.g., after a 10 GB database has already been downloaded. |

### Why Existing Solutions Fail

- **Signature-based IDS (Snort / Suricata):** Miss zero-day slow patterns hidden inside normal-looking traffic.
- **Legacy encryption:** Static keys protect files at rest but do nothing if the attacker steals the key alongside the file — the data remains readable.

ShadowMind is purpose-built for this **low-and-slow** threat model that evades both network and at-rest controls.

---

## Literature Survey

| Study / Year | Approach | Key Finding | Relevance to ShadowMind |
|---|---|---|---|
| Ferrag et al. (2020) | Deep learning for IDS — CNN, RNN, Autoencoders | Deep learning improves automated intrusion detection | Focuses on detection, not post-breach protection |
| Di Mauro et al. (2020) | Experimental comparison of neural IDS models | Neural models improve F-measure with resource trade-offs | Motivates efficient, reliable detection |
| Sabir et al. (2021) | ML for data-exfiltration detection | Behavioral / temporal / spatial / statistical features help | Supports behavior-driven detection |
| Caville et al. (2022) | Anomaly-E — GNN-based IDS | GNNs exploit flow relationships & topology | Strong detection, limited integrated response |
| Zhang & Shi (2023) | ML-based dynamic honeypot | ML can dynamically configure realistic honeypots | Adaptive deception, no crypto coupling |
| Zhong et al. (2024) | Survey of GNN-based IDS | GNNs enable complex intrusion analysis | Graph cost & deployment challenges remain |
| NIST SP 800-207 (2020) | Zero Trust Architecture | Shifts security to users/assets/resources | Strong resource security, no AI adaptive response |
| Recent research (2026) | AI-driven adaptive honeypots | Deception moving from static → adaptive/interactive | Scalability & dataset diversity remain open |

---

## Research Gap & Justification

| Research Gap | ShadowMind's Answer |
|---|---|
| Traditional IDS only detects & alerts | Pairs detection with a **Dynamic Honeypot** that engages attackers in real time |
| AI/ML detection focuses on isolated patterns | Uses **GNN (HoneyGraph)** to model relationships across the whole network |
| GNN detection lacks integration | Fully integrates GNN detection + deception + crypto response in **one pipeline** |
| Deception is static / diversion-only | Dynamic honeypot **continuously adapts** to attacker behavior |
| Zero-Trust & encryption lack real-time AI response | Adds **AI-driven, time-bound controls** (key rotation + TTL) that react as threats happen |

---

## Novelty & Original Contribution

The novelty is the **fusion** — each piece exists, but their self-destructing loop does not:

1. **Ensemble + graph detection** for slow exfiltration — spatial (CNN) + temporal (LSTM) + fusion (MLP) + graph reasoning, catching both sudden large transfers (e.g., 2 GB outbound) and subtle temporal anomalies (off-hours access).
2. **Adaptive dynamic honeypot** that evolves decoy realism/placement from observed attacker behavior.
3. **Poison Pill Vault** — per-session GAN-generated keys + emergency rotation that re-encrypts resources and invalidates stolen ciphertext in milliseconds.
4. **TTL Self-Destruct** — at session expiry (e.g., 5 PM logoff), all session decryption keys are force-wiped from RAM (zero-overwritten). Next login gets a fresh GAN key. No persistent key window remains.
5. **Zero user disruption** — all rotation/re-issuance happens transparently in the background.

---

## System Architecture

```
              Network Traffic / File Access Telemetry
                            │
               ┌────────────▼────────────┐
               │   AI Detection Engine   │
               │ CNN + LSTM + MLP + GNN  │
               │     (HoneyGraph)        │
               └─────┬─────────────┬─────┘
                     │             │
              Benign │    Malicious│
                     │             │
              ┌──────▼──────┐ ┌────▼──────────────┐
              │ Allow &     │ │ Dynamic Honeypot  │
              │ Monitor     │ │ (adaptive decoys) │
              └──────┬──────┘ └────┬──────────────┘
                     │             │
                     │      ┌──────▼──────────────┐
                     │      │ Poison Pill Vault   │
                     │      │ GAN keys · AES-256  │
                     │      │ Emergency rotation  │
                     │      └──────┬──────────────┘
                     │             │
              ┌──────▼─────────────▼──────┐
              │  TTL Self-Destruct Engine │
              │  Session expiry → RAM wipe│
              └───────────────────────────┘
```

> Slides 5–8 and 10 in the deck are diagram-heavy images; the diagram above is a faithful textual reconstruction. Refer to the PDF/PPTX for exact visuals.

---

## Methodology

### 1. AI Detection Engine

- **Features:** packet size, inter-arrival time, entropy, off-hours flags, flow statistics, file-access logs, user baselines.
- **CNN** — spatial anomalies (sudden large outbound transfer, unusual port fan-out).
- **LSTM** — temporal anomalies (periodic < 5 KB beacons over weeks, login-time drift).
- **MLP** — fuses CNN + LSTM embeddings into a joint decision.
- **HoneyGraph (GNN)** — enterprise as graph (hosts/users/flows as edges); message passing detects coordinated, distributed exfiltration that looks benign in isolation.
- **Output:** risk score → `benign` / `suspicious` / `confirmed exfiltration`.

### 2. Poison Pill Vault & Encryption

- **Key generation:** GAN produces high-entropy per-session keys (unique per user per login, never reused).
- **Encryption:** AES-256 (or equivalent) with session key held **only in RAM**.
- **Emergency rotation:** on `confirmed exfiltration`, immediately re-encrypts protected resources, invalidates old key — attacker's copy becomes permanently unreadable.
- **Transparency:** legitimate sessions are re-issued keys in the background.

### 3. Time-Based Self-Destruct (TTL)

| Step | What happens |
|---|---|
| **Trigger** | Employee logs off (e.g., 5 PM) → session TTL expires |
| **Wipe** | All remaining session decryption keys are zero-overwritten in server RAM |
| **Result** | File stays encrypted but the key no longer exists — not on disk, memory, or server |
| **Immunity window** | Even a key intercepted earlier that day is now permanently dead |
| **Next login** | GAN issues a completely fresh key; cycle restarts clean |

Guarantee: **no persistent key survives** past its intended lifetime.

---

## Workflow Demonstration

1. Employee logs in → GAN issues session key → AI engine monitors access.
2. Attacker beacons with < 5 KB packets mimicking normal traffic.
3. AI engine flags temporal + graph anomaly → traffic steered to **Dynamic Honeypot**.
4. **Poison Pill Vault** rotates keys in milliseconds → stolen data becomes undecryptable.
5. SOC receives enriched alert with honeypot intelligence.
6. At logoff, **TTL self-destruct** wipes keys → residual risk eliminated.

---

## Results & Expected Outcomes

### Target Detection Performance

- **Targeting 99%+ detection** for slow, low-and-slow exfiltration via CNN+LSTM+MLP ensemble — *pending validation on a labeled dataset*.
- Designed for both spatial (sudden 2 GB outbound) and temporal (off-hours access) anomalies that Snort/Suricata miss.

### Expected Security Outcomes

- Stolen data rendered unusable **within milliseconds** of confirmed exfiltration.
- **Zero disruption** to legitimate users.
- **No residual risk** at session end — TTL guarantees no key survives.

### Expected Operational Outcomes

- Wasted attacker time/resources via decoys.
- Runs on **standard laptops / Google Colab** — no enterprise spend required.
- Posture shift from static fortress → self-healing zero-trust immune system.

> All figures are design targets from deck page 11, not yet benchmarked on production traffic.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| AI / ML | Python, TensorFlow / PyTorch, scikit-learn, PyTorch Geometric (GNN), GAN |
| Detection | CNN, LSTM, MLP ensemble, HoneyGraph (GNN) |
| Deception | Dynamic honeypot (e.g., Cowrie / custom ML decoys) |
| Crypto | AES-256, secure RAM handling, GAN keygen |
| Platform | Google Colab / Jupyter, standard laptop |
| Future | Kubernetes, HSM/TPM, federated learning |

---

## Project Structure

Suggested layout when implementing from this spec (adapt to your repo):

```
Shadowmind/
├── README.md
├── docs/
│   ├── SHADOWMIND_GRP-45.pdf
│   └── ShadowMind.pptx
├── notebooks/
│   ├── 01_detection_cnn_lstm_mlp.ipynb
│   ├── 02_honeygraph_gnn.ipynb
│   └── 03_poison_pill_vault.ipynb
├── src/
│   ├── detection/        # CNN / LSTM / MLP / GNN
│   ├── honeypot/         # dynamic honeypot logic
│   ├── vault/            # Poison Pill Vault + GAN + AES
│   └── ttl/              # TTL self-destruct + RAM wipe
├── data/
│   ├── raw/
│   └── processed/
├── configs/
│   └── thresholds.yaml
└── tests/
    └── test_ttl_wipe.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Colab or local `pip` environment
- Optional GPU for training

### Quick Start (Colab-friendly)

```bash
git clone <your-repo-url> Shadowmind
cd Shadowmind

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install torch tensorflow scikit-learn torch-geometric cryptography pandas matplotlib jupyter

jupyter notebook notebooks/
```

### Minimal Demo Flow

1. Generate synthetic slow-exfiltration traffic (small random-interval packets vs. benign baseline).
2. Run `01_detection_cnn_lstm_mlp.ipynb` to train/evaluate the ensemble.
3. Simulate confirmed exfiltration → trigger vault rotation.
4. Expire session TTL → verify RAM wipe.

---

## Future Scope

From deck page 12:

- **Enterprise pilots** — validate accuracy under real production traffic.
- **Federated Threat Intelligence** — share attack patterns via federated learning without exposing raw data.
- **Cloud-Native scaling** — distributed Poison Pill Vault / rotation on Kubernetes.
- **IoT & Edge protection** — lightweight CNN/LSTM for edge devices.
- **Explainable AI Dashboard** — show SOC analysts *why* an event was flagged.
- **Hardware-Backed Vault** — HSM/TPM for tamper-proof, audit-ready key management.

---

## Limitations & Assumptions

- 99%+ accuracy is projected, pending real labeled slow-attack evaluation.
- GAN keys + RAM wipe must avoid swap/core-dump leakage — requires careful OS-level hardening.
- Honeypot realism depends on dataset diversity and attacker-model fidelity.
- GNN graph cost can be high on large topologies — needs optimization.
- No HSM/TPM or formal audit trail in current prototype.

---

## References

- Ferrag et al. 2020 — Deep learning for IDS
- Di Mauro et al. 2020 — Neural IDS comparison
- Sabir et al. 2021 — ML for exfiltration detection
- Caville et al. 2022 — Anomaly-E (GNN IDS)
- Zhang & Shi 2023 — ML dynamic honeypot
- Zhong et al. 2024 — Survey of GNN IDS
- NIST SP 800-207 (2020) — Zero Trust Architecture
- Recent cyber-deception research (2026) — AI adaptive honeypots

---

## Team & Credits

- **Author (deck):** Sourya Dey , Soham Mukherjee , Ditipriya Laha , Rachit Bhattacherjee and Muhammad Ahmed — **Group GRP-45**
- **Created:** 2026-09-09 15:38 UTC (Canva)
- **Source files:** `D:\SHADOWMIND_GRP-45.pdf` and `D:\ShadowMind.pptx` (12 slides)

---

## License

MIT — replace with your institutional policy before publishing. For college submissions, confirm whether the deck/report should remain private.

---

*Synthesized from the visual deck. For exact diagrams (architecture, AI methodology, vault, workflow), see the original PDF/PPTX.*
