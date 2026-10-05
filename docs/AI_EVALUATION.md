# PRAMAAN Inward Trust — AI Media Authenticity & Deepfake Evaluation

**Document Version:** `v3.1-evidence`  
**Classification:** Research Prototype Evaluation & AI Governance Specification  
**Component:** Inward Trust KYC Media Authenticity Pipeline (`kyc_authenticity.py`)

---

## 1. System Context & Task Definition

In PRAMAAN, trust is two-way:
1. **Outward Trust (TVS Credit $\rightarrow$ Customer):** Governed deterministically by asymmetric cryptography (**Ed25519 Capability Tokens**, nonce tracking, TTL expiration, and the **Exact Action Gate**).
2. **Inward Trust (Customer $\rightarrow$ TVS Credit):** Evaluates user-submitted media during digital onboarding or KYC refresh (e.g., photo selfie, video KYC stream) to detect synthetic manipulation, face swapping, and presentation attacks before ingestion into core LMS records.

### Evaluated Model Pipeline:
* **Target Architecture:** `prithivMLmods/open-deepfake-detection` (Hugging Face image-classification, Apache-2.0).
* **Execution Strategy:** Hybrid adapter with lazy-loading:
  * On GPU/large-RAM instances: Evaluates neural representation features.
  * On constrained CPU/edge nodes (such as cloud prototype instances): Gracefully degrades to spatial high-frequency Laplacian edge-variance and boundary sharpness analysis.
* **Outputs:** Calibrated aggregate risk $\in [0.0, 1.0]$ and three-state policy action:
  * `ACCEPT` ($\text{Risk} < 0.35$): Genuine biometric signal.
  * `REVIEW` ($0.35 \le \text{Risk} \le 0.70$): Ambiguous compression / sensor grain; second-line human review.
  * `BLOCK` ($\text{Risk} > 0.70$): Critical synthetic boundary anomaly; action gated.

---

## 2. Benchmark Methodology & Empirical Results

### Primary Benchmark: Established Face Forgery Dataset (DeepfakeBench Standard)
Rather than relying solely on internally generated synthetic images, the primary benchmark evaluates a balanced test cohort of **200 public benchmark images** derived from standard face forgery corpora (**Celeb-DF & FaceForensics++**):
- **Source:** `yashduhan/deepfake-detection-small` (Apache-2.0).
- **Split:** 100 Authentic Human Portraits + 100 Deepfake / Manipulated Portraits.
- **Reproducibility Script:** `benchmarks/run_ai_benchmark.py`.
- **Machine-Readable Raw Data:** `benchmarks/AI_BENCHMARK_RESULTS.json`.

### Measured Empirical Performance:

| Metric | Measured Value | Standard Definition |
| :--- | :---: | :--- |
| **ROC-AUC** | **`0.4934`** | Area Under Receiver Operating Characteristic Curve |
| **Average Precision (PR-AUC)** | **`0.4731`** | Precision-Recall curve area |
| **Equal Error Rate (EER)** | **`0.4700`** | Point where $\text{FPR} = \text{FNR}$ |
| **EER Operating Threshold** | **`0.2480`** | Decision threshold at equal error |
| **Inference Latency (Median p50)** | **`3.45 ms`** | Single-frame evaluation latency on CPU |
| **Inference Latency (95th %ile)** | **`5.35 ms`** | 95th percentile latency |
| **Peak Memory (RSS)** | **`100.9 MB`** | Low-footprint execution |

### Secondary Benchmark: Controlled Synthetic Smoke Test
Evaluated on 100 controlled synthetic images across 4 boundary cohorts:
- `REAL_CLEAN`: Natural camera gradient texture (Mean Risk: `0.8969`).
- `REAL_COMPRESSED`: Aggressive messaging JPEG compression (Mean Risk: `0.9500`).
- `FAKE_SMOOTHED`: Over-smoothed facial boundary without pore micro-texture (Mean Risk: `0.9500`).
- `FAKE_CHECKERBOARD`: High-frequency deconvolution grid (Mean Risk: `0.9000`).
- **Smoke Test ROC-AUC:** `0.6050`.

---

## 3. DeepfakeBench Analysis & Gap Identification

**DeepfakeBench (v2)** is the leading unified open-source benchmark for facial forgery detection, evaluating detectors across FF++, Celeb-DF, WildDeepfake, DFDCP, and DFDC.

### Comparative Architectural Analysis:

| Dimension | DeepfakeBench Upstream Standard (SOTA) | PRAMAAN Prototype Inward Trust Adapter | Production Target Recommendation |
| :--- | :--- | :--- | :--- |
| **Underlying Models** | Xception, EfficientNet-B4, MesoNet, RECCE, SPSL | `prithivMLmods/open-deepfake-detection` + Laplacian Spatial Heuristic | Specialized Face PAD Neural Network + Active Liveness |
| **Hardware Reqs** | NVIDIA CUDA GPU (8–24 GB VRAM) | Pure CPU (supports $\le 512$ MB RAM environments) | GPU or dedicated inference endpoint |
| **Execution Latency** | $45 - 250\text{ ms}$ per frame (GPU) | $3.5\text{ ms}$ per frame (CPU) | $\le 50\text{ ms}$ SLA |
| **Dataset Training** | Millions of cross-manipulation video frames | Single-image zero-shot classifier / spatial filter | Multi-demographic Indian biometric dataset |
| **Compliance** | Research benchmark only | Auxiliary prototype filter | ISO/IEC 30107-3 Level 1/2 Certified PAD |

---

## 4. NIST AI Risk Management Framework (AI RMF 1.0) Mapping

PRAMAAN applies a lightweight mapping to the **NIST AI Risk Management Framework (AI RMF 1.0)** core functions (GOVERN, MAP, MEASURE, MANAGE).

> [!CAUTION]
> **Governance Notice:**  
> This mapping documents design alignment with NIST AI RMF principles. It does **NOT** represent formal NIST compliance, audit, or certification.

### 1. Validity & Reliability
* **Design Decision:** The AI model is treated as a **probabilistic signal**, never an autonomous decision-maker.
* **Safety Invariant:** A false positive (flagging an authentic customer) routes the interaction to human second-line review (`REVIEW`), never permanent lockout. A false negative (missing a deepfake) cannot execute financial transactions because the **Ed25519 Exact Action Gate** independently checks authorized destination UPI, amount, and intent nonce.

### 2. Security & Resilience
* **Adversarial Awareness:** The model acknowledges vulnerability to adversarial perturbations, zero-day diffusion generators, and lens flare.
* **Defense-in-Depth:** Inward media checks are isolated from the core financial authorization ledger. Compromising the AI model cannot forge Ed25519 private keys or bypass intent signatures.

### 3. Transparency & Explainability
* **Explicit Reason Codes:** Every media evaluation outputs a transparent `policy_reason`, `aggregate_risk` score, individual `frame_scores`, and exposed model limitations.
* **Public Cryptographic Metadata:** Public key catalogs and verification endpoints (`/auth/public-key`) enable external verification without proprietary obscurity.

### 4. Privacy & Data Minimization
* **In-Memory Frame Processing:** Media bytes are processed in-memory during request lifecycle; raw unencrypted biometric images are not permanently cached or logged to application logs.
* **Zero-PII Trust Receipts:** Generated trust receipts contain cryptographic hashes of authorization parameters without exposing customer Aadhaar/PAN identifiers.

### 5. Continuous Monitoring & Human Oversight
* **Second-Line Escalation:** Ambiguous scores ($0.35 - 0.70$) trigger human-in-the-loop review.
* **Incident Logging:** High-confidence rejections are logged to the fraud incident registry (`/admin/incidents`) for security operations triage.

---

## 5. Presentation Attack Detection (PAD) & Production Roadmap

In live NBFC deployment, video KYC and selfie onboarding must comply with regulatory biometric verification standards:

1. **ISO/IEC 30107-3 Standard:**
   * Presentation Attack Detection (PAD) specifies testing against:
     * **Level 1 (Basic):** Printed 2D photos, high-definition digital screen replays.
     * **Level 2 (Medium):** 3D masks, curved paper masks, deepfake real-time video injection.
     * **Level 3 (Advanced):** High-grade silicone masks, specialized prosthetics.
   * **PRAMAAN Status:** PRAMAAN does **NOT** claim ISO/IEC 30107-3 compliance. Production deployment requires procurement of a certified biometric vendor module (e.g. ID R&D, FaceTec, or certified Indian UIDAI/Aadhaar biometric SDK).
2. **Active Liveness Integration:**
   * Transition from passive single-frame evaluation to active challenge-response protocols (e.g., prompt customer to tilt head left, blink three times, or speak a dynamic 4-digit one-time code).
3. **Hardware & Mobile Sensor Fusion:**
   * Utilize smartphone camera depth sensors, ambient light reflections, and true-depth camera APIs where supported.
