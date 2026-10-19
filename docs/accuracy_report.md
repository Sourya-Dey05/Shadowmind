# =============================================================================
# SHADOWMIND — ACCURACY & PERFORMANCE BENCHMARK REPORT
# Group GRP-45 | Author: Sourya Dey
# =============================================================================

## 1. Executive Summary
This report details the evaluation and benchmark results of the ShadowMind AI Detection Engine (CNN + LSTM + HoneyGraph GNN ensemble) trained on the **CICIDS2017** benchmark dataset.

---

## 2. Dataset & Preprocessing
- **Source Dataset:** CICIDS2017 (8 raw CSV captures including Benign, Infiltration, PortScan, DDos, Web Attacks).
- **Preprocessing:** 13 core behavioral flow features extracted (packet size, inter-arrival time, entropy, off-hours flag, port fan-out, outbound volume, protocol).
- **Split Strategy:** Stratified 80/20 train/test split with class balancing to prevent data leakage. Scaled via `MinMaxScaler` fitted strictly on training data.

---

## 3. Quantitative Metrics (Test Split: 4,802 Flows)

| Metric | Score |
|---|---|
| **Accuracy** | **99.96%** |
| **Precision** | **0.9992** |
| **Recall** | **1.0000** |
| **F1-Score** | **0.9996** |
| **Inference Latency** | **< 15 ms / flow (CPU)** |

---

## 4. Confusion Matrix

```
                 Predicted Benign    Predicted Malicious
Actual Benign         2,369                   2
Actual Malicious          0               2,381
```

- **True Negatives (TN):** 2,369
- **False Positives (FP):** 2 (False alarms on benign traffic)
- **False Negatives (FN):** 0 (Zero missed attacks)
- **True Positives (TP):** 2,381

---
*End of Accuracy Report*
