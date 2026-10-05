# PRAMAAN v3.1 — AI Media Authenticity Benchmark Report

**Benchmark Timestamp:** `2026-10-04T08:10:00.516521+00:00`  
**Evaluation Standard:** Independent Public Evaluation on Established Face Forgery Dataset (DeepfakeBench Standard)  
**Evaluated Detector:** `prithivMLmods/open-deepfake-detection` (License: `Apache-2.0`)  
**Operational Status:** Prototype Inward Trust Auxiliary Filter (NOT certified TVS biometric accuracy)

---

## 1. Executive Summary & Benchmark Discipline

This report provides reproducible, evidence-backed evaluation for PRAMAAN's Inward Trust Media Authenticity Shield.

> [!IMPORTANT]
> **Claim Discipline & Regulatory Disclaimer:**  
> The media authenticity pipeline in PRAMAAN v3.1 is an **illustrative open-source research adapter** combining the Apache-2.0 `prithivMLmods/open-deepfake-detection` pipeline with lightweight spatial Laplacian edge variance analysis.  
> It is **NOT** certified TVS production biometric accuracy, nor does it claim ISO/IEC 30107-3 Presentation Attack Detection (PAD) compliance.  
> In TVS production workflows, biometric evaluations act strictly as auxiliary secondary signals and are **always bound to out-of-band Ed25519 cryptographic authorization**.

---

## 2. Primary Benchmark: Public Open Benchmark Test Cohort

Evaluated on 200 balanced test samples derived from standard face forgery benchmarks (**Celeb-DF & FaceForensics++**):
- **Real Faces:** 100 authentic high-resolution human portrait samples.
- **Deepfake Faces:** 100 face-swapped / synthesized human portrait samples.
- **Data Source:** `yashduhan/deepfake-detection-small` (Apache-2.0 / Open Access).

### Primary Benchmark Metrics

| Metric | Measured Value | Standard Interpretation |
| :--- | :---: | :--- |
| **ROC-AUC** | **`0.9664`** | Area Under Receiver Operating Characteristic Curve |
| **Average Precision (PR-AUC)** | **`0.9605`** | Precision-Recall curve area across confidence range |
| **Equal Error Rate (EER)** | **`0.07`** | Operational point where False Positive Rate == False Negative Rate |
| **EER Operating Threshold** | **`0.153`** | Calibrated decision boundary for equal error |
| **Accuracy (Default $\tau=0.50$)** | **`81.5%`** | Classification accuracy at standard 0.50 threshold |
| **Precision (Default $\tau=0.50$)** | **`95.7%`** | Ratio of true deepfakes among flagged items |
| **Recall (Default $\tau=0.50$)** | **`66.0%`** | Fraction of deepfakes successfully flagged |
| **F1-Score (Default $\tau=0.50$)** | **`0.7811`** | Harmonic mean of precision and recall |
| **Optimal Operating Threshold** | **`0.15`** | Threshold maximizing F1 score (`0.9353`) |

### Confusion Matrix (Default $\tau=0.50$)

| | Actual Real (`0`) | Actual Deepfake (`1`) | Total |
| :--- | :---: | :---: | :---: |
| **Predicted Authentic (ACCEPT)** | **`97`** (TN) | **`34`** (FN) | `131` |
| **Predicted Synthetic (BLOCK)** | **`3`** (FP) | **`66`** (TP) | `69` |
| **Total** | **`100`** | **`100`** | **`200`** |

---

## 3. Threshold Sensitivity Analysis

Analysis of false positive versus detection rate across the decision boundary spectrum:

| Threshold ($\tau$) | Accuracy | Precision | Recall | F1-Score | True Positives | False Positives |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `0.10` | `92.0%` | `87.5%` | `98.0%` | `0.9245` | `98` | `14` |
| `0.15` | `93.5%` | `93.1%` | `94.0%` | `0.9353` | `94` | `7` |
| `0.20` | `91.5%` | `94.6%` | `88.0%` | `0.9119` | `88` | `5` |
| `0.25` | `91.0%` | `95.6%` | `86.0%` | `0.9053` | `86` | `4` |
| `0.30` | `88.5%` | `95.3%` | `81.0%` | `0.8757` | `81` | `4` |
| `0.35` | `86.0%` | `95.0%` | `76.0%` | `0.8444` | `76` | `4` |
| `0.40` | `82.0%` | `94.4%` | `68.0%` | `0.7907` | `68` | `4` |
| `0.45` | `82.0%` | `94.4%` | `68.0%` | `0.7907` | `68` | `4` |
| `0.50` | `81.5%` | `95.7%` | `66.0%` | `0.7811` | `66` | `3` |
| `0.55` | `80.0%` | `96.9%` | `62.0%` | `0.7561` | `62` | `2` |
| `0.60` | `75.5%` | `96.4%` | `53.0%` | `0.6839` | `53` | `2` |
| `0.65` | `72.0%` | `97.8%` | `45.0%` | `0.6164` | `45` | `1` |
| `0.70` | `68.5%` | `97.4%` | `38.0%` | `0.5468` | `38` | `1` |
| `0.75` | `67.0%` | `97.2%` | `35.0%` | `0.5147` | `35` | `1` |
| `0.80` | `63.5%` | `96.5%` | `28.0%` | `0.4341` | `28` | `1` |
| `0.85` | `60.0%` | `100.0%` | `20.0%` | `0.3333` | `20` | `0` |
| `0.90` | `56.5%` | `100.0%` | `13.0%` | `0.2301` | `13` | `0` |

---

## 4. Inference Latency & System Footprint

Measurements conducted on single-threaded CPU execution:

| Latency Metric | Measured Time (ms) |
| :--- | :---: |
| **Median Latency (p50)** | **`275.123 ms`** |
| **Mean Latency** | **`275.704 ms`** |
| **95th Percentile (p95)** | **`290.345 ms`** |
| **99th Percentile (p99)** | **`337.235 ms`** |
| **Min / Max Latency** | `249.766 ms` / `359.647 ms` |
| **Peak Memory Consumption** | **`764.41 MB`** (RSS) |

---

## 5. Secondary Test: Controlled Synthetic Smoke Test (Boundary Stress)

The secondary test evaluates 100 synthetic stress samples across 4 distinct boundary conditions:

| Cohort | Samples | Target Feature Tested | Mean Risk Score | Status |
| :--- | :---: | :--- | :---: | :---: |
| **REAL_CLEAN** | 25 | Natural facial camera noise and dynamic gradient | `0.3918` | PASS |
| **REAL_COMPRESSED** | 25 | Aggressive JPEG/WhatsApp messaging compression | `0.4146` | PASS |
| **FAKE_SMOOTHED** | 25 | Over-smoothed boundary without pore texture | `0.52` | PASS |
| **FAKE_CHECKERBOARD** | 25 | High-frequency deconvolution checkerboard grid | `0.5809` | PASS |

- **Smoke Test ROC-AUC:** `1.0`
- **Smoke Test Accuracy at $\tau=0.50$:** `100.0%`

---

## 6. Known Model Limitations & Production Gaps

1. **Lightweight Fallback Baseline:** On resource-constrained edge/cloud nodes without GPU acceleration, the detector operates on high-frequency spatial Laplacian edge variance. While effective against over-smoothed artifacts and crude GAN checkerboards, advanced modern diffusion-based deepfakes require full neural feature extractors.
2. **Compression Degradation:** Highly compressed WhatsApp/MMS media reduces boundary resolution, elevating the false review rate.
3. **Requirement for Presentation Attack Detection (PAD):** True production biometric defense requires active challenge-response liveness (head movement, micro-blink detection) certified under ISO/IEC 30107-3.
4. **Architectural Role:** Within PRAMAAN, media authenticity acts solely as an inbound gate; security is ultimately anchored in the deterministic **Ed25519 Exact Action Gate**.
