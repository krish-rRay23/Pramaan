# PRAMAAN: Financial Interaction Trust Firewall
### Capability-Based Interaction Security for Enterprise Retail Lending

[![TVS Credit Finale](https://img.shields.io/badge/TVS%20Credit%20Epic%206-Finale%20Release-gold.svg)](#)
[![Policy Engine](https://img.shields.io/badge/Policy%20Engine-v3.2.0%20Adaptive-blue.svg)](#)
[![Security Invariant](https://img.shields.io/badge/Security-Ed25519%20Cryptographic%20Gate-emerald.svg)](#)
[![Performance](https://img.shields.io/badge/Throughput-410%2B%20req%2Fs%20(0%25%20Errors)-brightgreen.svg)](#)
[![OWASP Top 10](https://img.shields.io/badge/OWASP%20API-10%2F10%20Mitigated-purple.svg)](#)
[![License](https://img.shields.io/badge/License-Apache%202.0%20%2F%20MIT-lightgrey.svg)](#)

> **Core Axiom:**  
> **“Authenticate the interaction. Not the caller.”**  
> *Pramaan eliminates remote financial fraud by shifting trust from spoofable communication channels (phone calls, WhatsApp, SMS) to single-use, tamper-proof, Ed25519-signed capability tokens enforced at the Exact Action Gate.*

---

## 1. Executive Summary

In Indian retail lending and NBFC operations, borrower communications are facing an unprecedented trust crisis:
- **Caller ID & Messaging Spoofing:** Scammers impersonate loan collection officers using spoofed caller IDs, fake WhatsApp business badges, and counterfeit notice templates.
- **Rogue Field Agent Redirection:** Unscrupulous recovery agents substitute personal or mule UPI VPAs during collections to divert customer EMIs into untraceable accounts.
- **Borrower Hesitation:** Delinquent borrowers refuse to pay legitimate collectors over digital channels due to justifiable fear of fraud.

**Pramaan** solves this by establishing a zero-trust financial firewall. The communication conduit is treated as fundamentally hostile. Instead of asking customers to trust who is contacting them, TVS Credit's Loan Management System (LMS) issues an ephemeral (180s TTL) cryptographic capability token. When the customer opens the verification link or receives an automated push, the **Exact Action Gate** deterministically verifies the loan ID, purpose, amount, recipient VPA, and agent capability against the cryptographic seal. 

Any tampering, redirection, replay, or staleness causes the gate to fail closed immediately.

```
                              UNTRUSTED CONDUIT
           (Spoofed Calls, WhatsApp Notices, Smishing SMS, QR Codes)
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │     PRAMAAN TRUST FIREWALL      │
                    │   "Authenticate Interaction"    │
                    └────────────────┬────────────────┘
                                     │
            ┌────────────────────────┴────────────────────────┐
            ▼                                                 ▼
   [Lane 1: Inward Trust]                            [Lane 2: Outward Trust]
 Identity / Deepfake KYC Telemetry               Cryptographic Capability Gate
(CPU Edge Filter: 3.45ms Latency)              (Ed25519 Asymmetric Verification)
            │                                                 │
            └────────────────────────┬────────────────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │    ADAPTIVE POLICY ENGINE   │
                      │  (POL-TVS-2026.2-ADAPTIVE)  │
                      └──────────────┬──────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   [STANDARD ASSURANCE]     [ELEVATED ASSURANCE]      [CRITICAL ANOMALY]
   Streamlined 1-Touch       Step-Up Verification      Immediate Fail-Closed
   "VERIFIED / सत्यापित"     "ADDITIONAL VERIFICATION"   "BLOCKED / अवरुद्ध"
           │                         │                         │
           ▼                         ▼                         ▼
    One-Click Approve        Biometric / Checkbox     Quarantine & Revoke
           │                         │
           └────────────►┬◄──────────┘
                         │
                         ▼
           ┌───────────────────────────┐
           │  EXACT ACTION GATE PASS   │
           │  Mint Tamper-Proof Ed25519│
           │       Trust Receipt       │
           └───────────────────────────┘
```

---

## 2. Adaptive Policy Engine (v3.2.0 — Zero Hardcoded Cutoffs)

Pramaan v3.2.0 replaces all static monetary thresholds (including the legacy ₹50,000 cutoff) with a **versioned, context-driven, deterministic risk policy engine**.

### 2.1 The Problem with Fixed Cutoffs
In retail lending, an arbitrary ₹50,000 threshold is fundamentally broken:
- For a rural two-wheeler borrower paying ₹3,200/month, an unexpected ₹18,000 foreclosure notice represents a massive relative risk that warrants immediate step-up confirmation.
- For a commercial vehicle or tractor borrower, a scheduled ₹65,000 monthly EMI to TVS Credit's verified account is completely routine and should proceed with streamlined single-touch friction.

### 2.2 Contextual Signals Evaluated
The policy engine evaluates multiple risk vectors simultaneously to assign an assurance tier:
1. **Action Sensitivity:** Foreclosure / loan close (`0.50`), collateral release (`0.55`), settlement (`0.40`) vs routine payment (`0.10`).
2. **Relative Amount Deviation:** Compares transaction amount against the customer's loan baseline repayment (`amount / baseline_amount` $\ge$ 2.5x or 5.0x) rather than an arbitrary global amount.
3. **Destination Familiarity:** Unfamiliar or freshly changed VPAs outside customer's pre-approved accounts add contextual risk penalty (`+0.35`).
4. **Velocity & Frequency:** Monitors interaction frequency to intercept rapid retries or credential stuffing attacks (`+0.30` penalty when $\ge$ threshold).
5. **Channel Trust State:** In-app session (`0.05`) vs SMS (`0.10`) vs WhatsApp/Telegram (`0.15`) vs Phone Call (`0.15`).
6. **Agent Authorization:** Validates agent assignment and flags unassigned collections (`+0.25`).

### 2.3 Single Source of Truth: `policy_config.json`
- **Zero hardcoded business-policy numbers in executable logic:** All weights, multipliers, penalties, and assurance boundaries reside strictly in [policy_config.json](pramaan-backend/policy_config.json).
- **Runtime Policy Reloading:** Policy rules can be hot-reloaded dynamically via `POST /policy/reload` without server restarts.
- **Fail-Closed Guarantee:** If the policy file is corrupted or unavailable, the engine fails closed securely (`POL_POLICY_UNAVAILABLE_FAIL_CLOSED` $\to$ `BLOCKED`).

---

## 3. Real-World Attack Containment Matrix

| Threat Vector | Real-World Attack Scenario | Pramaan Firewall Defense | Outcome |
| :--- | :--- | :--- | :---: |
| **Fake Notice / Lookalike** | Scammer sends lookalike collection letter on WhatsApp with rogue QR. | Customer taps link. Exact Action Gate checks for TVS signature; no signed intent exists. | **UNVERIFIED / BLOCKED** |
| **Mule VPA Diversion** | Recovery agent presents genuine loan balance but supplies personal UPI ID. | Gate checks claimed VPA against authoritative `tvscredit.collections@upi` in signed seal. | **BLOCKED (POL_MISMATCH_DESTINATION)** |
| **Amount Tampering** | Scammer inflates collection amount by ₹2,000 to pocket difference. | Gate flags parameter discrepancy; Ed25519 cryptographic seal invalid. | **BLOCKED (POL_MISMATCH_AMOUNT)** |
| **Capability Replay** | Attacker intercepts genuine payment link and tries to execute it a second time. | Server-side consumed nonce registry intercepts token re-use. | **BLOCKED (POL_REPLAY_DETECTED)** |
| **Stale Link Phishing** | Attacker saves old payment link to collect from borrower days later. | Freshness gate checks `expires_at` against UTC clock (180s strict window). | **BLOCKED (POL_EXPIRED_TTL)** |
| **Coordinated Swarm** | Rogue syndicate targets multiple borrowers directing funds to a single VPA. | Swarm Defense correlates target VPA across loans, auto-quarantines VPA, and cascades revocation. | **CONTAINED (POL_QUARANTINED_DESTINATION)** |
| **Deepfake Video KYC** | Synthetic identity or face-swap submitted during inward verification. | Auxiliary Inward Trust edge filter flags high spatial anomaly score for review. | **FLAGGED FOR MAKER-CHECKER** |

---

## 4. Empirically Proven Benchmark Evidence

All metrics reported below were collected using industry-standard open-source benchmarking frameworks on commodity, single-node CPU infrastructure:

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│       14,070 ops/sec            │            0.25 ms              │            97.0 ms              │
│    LMS Token Issuance Rate      │  Cryptographic Gate Verification│   Full E2E Mobile Verification  │
│      (Single Core CPU)          │       (Exact Action Gate)       │      (Customer Journey)         │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│       410.37 req/sec            │             0.0%                │          ~2.1 Paise             │
│    Sustained Concurrency        │    Error Rate (14,000+ Req)     │     Infra Cost per Customer     │
│       (Locust 2.46.6)           │       (Stress Conditions)       │          Verification           │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

### 4.1 Pure Cryptographic Primitive Benchmark
*Source: `cryptography.hazmat.primitives.asymmetric.ed25519` (5,000 isolated iterations)*
- **Token Signing Throughput:** `14,070.8 ops/sec` (Median p50: `66.2 µs`, p95: `96.3 µs`)
- **Signature Verification Throughput:** `3,233.3 ops/sec` (Median p50: `253.6 µs`, p95: `396.7 µs`)
- **Keypair Generation:** `14,048.7 keys/sec` (Mean: `71.18 µs`)
- *Takeaway:* Asymmetric verification introduces **under 0.3 milliseconds** of overhead into transaction gateways.

### 4.2 End-to-End System Concurrency (Locust 2.46.6)
*Multi-tier concurrency load evaluation on single-node Python 3.11 runtime:*

| Concurrency Tier | Concurrent Users | Spawn Rate | Requests Evaluated | Peak Throughput | Median Latency | p95 Latency | Packet Loss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1 (Routine)** | 10 | 2/s | 2,186 | **209.21 req/s** | 9.0 ms | 21.0 ms | **0.0%** |
| **Tier 2 (Moderate)** | 50 | 10/s | 5,258 | **399.25 req/s** | 79.0 ms | 130.0 ms | **0.0%** |
| **Tier 3 (Stress)** | 100 | 25/s | 6,653 | **410.37 req/s** | 190.0 ms | 290.0 ms | **0.0%** |

### 4.3 Unit Economics & Fraud Break-Even ROI
*Source: [TVS Credit Capacity & Cost Model](pramaan-backend/docs/COST_MODEL.md) (AWS Mumbai `ap-south-1` Reference Architecture)*
- **Infrastructure Cost per 1,000 Interactions:** **`₹21.34`** (`$0.2467`)
- **Monthly Infrastructure for 1,000,000 Interactions:** **`₹21,337 / month`** (`$246.67`)
- **Unit Cost per Customer Verification:** **`~2.1 Paise`**
- **Break-Even Analysis:** Preventing just **ONE single ₹15,000 two-wheeler EMI diversion** pays for the infrastructure of **~700,000 customer verifications**.

### 4.4 Security SAST & Failure Invariants
- **OWASP API Security Top 10 (2023):** 10 / 10 categories satisfied with mathematical bindings ([Matrix](pramaan-backend/security/OWASP_API_ASVS_MATRIX.md)).
- **Bandit SAST Scanner:** 0 High-Severity vulnerabilities across 3,207 LOC.
- **Enterprise Failure-Mode Suite:** 16 / 16 scenarios pass, proving mathematically that **failure never becomes authorization**.

---

## 5. Multi-Platform Architecture

```
Pramaan Repository Workspace
│
├── pramaan-backend/                # FastAPI High-Throughput Trust Engine
│   ├── main.py                     # API Gateway, Exact Action Gate, Simulator Routes
│   ├── policy_engine.py            # Versioned Adaptive Contextual Risk Engine
│   ├── policy_config.json          # Single Source of Truth for Policy Weights/Thresholds
│   ├── crypto_utils.py             # Pure Ed25519 Canonical JSON Signing & Key Rotation
│   ├── store.py                    # Nonce Registry, Swarm Defense, Accounts Database
│   ├── notification_adapter.py     # Multi-Channel Bridge (Telegram, CallMeBot, WhatsApp)
│   ├── console.html                # Operations Console & Live Attack Lab
│   └── tests/                      # 4 Automated Test Suites (Hardening, Failure Modes, Adaptive)
│
├── pramaan-android/                # Native Jetpack Compose Customer Mobile Client
│   ├── ui/ExactActionGateScreen.kt # Risk-Proportional Gate UI (Standard vs Step-Up)
│   ├── ui/HomeScreen.kt            # Customer Dashboard, Trust Receipts, Kill Switch
│   ├── ui/KycScreen.kt             # Inward Trust Media Authenticity Scanner
│   ├── ui/theme/                   # Minimalist White Glassmorphism Design System
│   └── network/ApiService.kt       # Deep-Link Intent Verification Client
│
└── docs/                           # Enterprise Documentation & Evidence Dossiers
    ├── SECURITY_MODEL.md           # Threat Model, Cryptographic Lifecycle, RBAC
    ├── COST_MODEL.md               # AWS Mumbai Infrastructure Cost & Capacity Model
    └── GTM_PLAN.md                 # Commercial Rollout & Cross-Lender Swarm Consortium
```

### 5.1 Rural & Low-Digital-Literacy UX (Android)
- **Minimalist White Glassmorphism:** Clean, modern interface designed for clarity and legibility.
- **Bilingual Accessibility:** Instant toggle between English and Hindi (**हिन्दी**).
- **Assisted Voice / Text-to-Speech (TTS):** Reads aloud the exact borrower name, loan account, verified amount, and authorized destination in the customer's chosen language.
- **Human-Readable Trust Badges:** Replaces confusing technical terminology with clean visual indicators:
  - `VERIFIED / सत्यापित` (Green)
  - `ADDITIONAL VERIFICATION REQUIRED / अतिरिक्त सत्यापन आवश्यक` (Amber)
  - `BLOCKED / अवरुद्ध` (Red)
- **Deep Link Handling:** Seamless 1-tap transition from Telegram, WhatsApp, or SMS notices via `pramaan://verify?token=...` directly into the Exact Action Gate.

---

## 6. Live Interactive Demo & Attack Lab

The backend serves an interactive Operations Console at `http://localhost:8000/console.html` equipped with an **Attack Lab Simulator** providing 1-click execution of 8 real-world scenarios:

1. **Genuine TVS EMI Interaction:** Customer verifies exact loan details; gate passes and mints signed Trust Receipt (`ALLOWED`).
2. **Forged / Fake Intent:** Attacker crafts intent without TVS master private key; fails signature check (`BLOCKED`).
3. **Amount Tampering Attack:** Scammer inflates collection amount; gate rejects discrepancy (`BLOCKED`).
4. **Destination Mule Redirection:** Rogue agent supplies personal UPI ID; gate catches mismatch (`BLOCKED`).
5. **Capability Nonce Replay:** Attacker intercepts and replays spent payment link; intercepted by nonce registry (`BLOCKED`).
6. **Expired Intent Staleness:** Token presented after 180s TTL window; rejected by freshness gate (`BLOCKED`).
7. **Unauthorized Agent Action:** Suspended agent attempts payment collection; blocked by RBAC scope (`UNVERIFIED`).
8. **Coordinated Swarm Attack:** Syndicate targets multiple accounts to a single mule VPA; correlation engine auto-quarantines VPA and cascade-revokes all related active intents (`CONTAINED`).

---

## 7. Quick Start Guide

### 7.1 Backend Setup & Execution
```bash
# 1. Clone repository
git clone https://github.com/krish-ray/pramaan.git
cd pramaan/pramaan-backend

# 2. Set up virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # On Linux/macOS: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch backend trust firewall
uvicorn main:app --reload --port 8000
```

### 7.2 Access Endpoints
- **Operations Console & Attack Lab:** [http://localhost:8000/console.html](http://localhost:8000/console.html)
- **Interactive OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Authority Public Key Metadata:** [http://localhost:8000/auth/public-key](http://localhost:8000/auth/public-key)
- **Active Versioned Policy Configuration:** [http://localhost:8000/policy/active](http://localhost:8000/policy/active)

### 7.3 Android Client Setup
1. Open `pramaan-android` in Android Studio (Ladybug / Hedgehog or newer).
2. Confirm the `BASE_URL` in `app/build.gradle.kts` points to your backend (`http://10.0.2.2:8000/` for emulator or your LAN IP for physical device).
3. Run `.\gradlew.bat assembleDebug` or launch directly to device.

---

## 8. Automated Test Suite Execution

Pramaan includes four automated regression suites covering failure modes, performance, and policy hardening:

```bash
# 1. Adaptive Policy Test Suite (Zero hardcoded cutoffs, dynamic reload, fail-closed)
.\.venv\Scripts\python -m pytest test_adaptive_policy.py -v

# 2. Hardening & E2E Integration Suite (12 Core Production Scenarios)
.\.venv\Scripts\python test_hardening.py

# 3. Defensive Invariants & Failure-Mode Suite (16 Automated Failure Assertions)
.\.venv\Scripts\python test_failure_modes.py

# 4. Core Trust Engine Test Suite
.\.venv\Scripts\python test_engine.py

# 5. Android Client Compilation Check
cd ../pramaan-android
.\gradlew.bat compileDebugKotlin
```

---

## 9. Technology Stack

- **Backend Runtime:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Cryptographic Primitives:** PyCA Cryptography (Ed25519 asymmetric signatures, Curve25519)
- **Adaptive Policy Engine:** Versioned JSON schema (`POL-TVS-2026.2-ADAPTIVE`), fail-closed deterministic evaluator
- **Android Client:** Kotlin, Jetpack Compose, Material 3, Android Text-to-Speech (TTS), Retrofit2, OkHttp3
- **Notification Conduits:** Telegram Bot API (Primary demo), CallMeBot API, Mock Gateway
- **Benchmarking & Testing:** Locust 2.46.6, Pytest, Bandit SAST, pip-audit, CycloneDX SBOM

---

## 10. Authors & Acknowledgments

Developed for the **TVS Credit E.P.I.C 6 Innovation Challenge**.

*“Turning financial communication into verifiable trust.”*
