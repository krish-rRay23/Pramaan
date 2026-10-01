# PRAMAAN v3.1 — Financial Interaction Trust Firewall

FastAPI enterprise trust firewall implementing capability-based interaction authorization:
- **Core Principle:** *"Authenticate the interaction. Not the caller."*
- **Cryptographic Core:** Ed25519 asymmetric signing, canonical JSON, 4-state key rotation lifecycle.
- **Defensive Invariant:** Exact Action Gate (customer, loan, purpose, action, amount, destination, channel, partner, agent, session, single-use nonce, 180s TTL).
- **Fraud Defense:** Coordinated swarm correlation, automated VPA quarantine, cascade intent revocation, and emergency customer kill switch.
- **Transports:** Telegram Bot API (primary demo transport with random one-time pairing), CallMeBot (secondary), Mock fallback, and TVS Enterprise WhatsApp Business API (production target).
- **Storage:** Abstract repository pattern with `InMemoryRepository` (demo baseline) and `PostgreSQLRepository` (production DDL & transactions).

## 1. Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- **Operations Console & Live Attack Lab:** `http://localhost:8000/console.html`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Public Key Metadata:** `http://localhost:8000/auth/public-key`

## 2. Test & Verification Suites

```bash
# 1. Failure Mode & Defensive Invariants Test Suite (16 Automated Failure Scenarios)
python test_failure_modes.py

# 2. Hardening & E2E Integration Suite (12 Core Tests)
python test_hardening.py

# 3. Scalability & Latency Benchmark Engine (10-250 Concurrent Workers)
python benchmarks/scalability_benchmark.py

# 4. Inward Trust AI Deepfake / Heuristic Benchmark Suite
python benchmarks/ai_benchmark.py

# 5. Security Scan & SAST Audit (Zero Critical / High Findings)
python security/security_scanner.py

# 6. CycloneDX 1.5 SBOM Generation
python security/generate_sbom.py
```

## 3. Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/ping` | Health check, authority validation & supported transports |
| GET | `/auth/public-key` | Exposes public Ed25519 verification metadata |
| GET | `/auth/keys` | Public key catalog and lifecycle status (Active, Staged, Verification-Only, Revoked) |
| POST | `/intent/issue` | TVS LMS capability intent issuance (Ed25519 signed) |
| POST | `/intent/verify` | Exact Action Gate: signature + TTL + nonce + exact binding match |
| POST | `/intent/kill-switch` | Emergency customer defense ("I DON'T TRUST THIS REQUEST") |
| GET | `/receipts/verify/{id}` | Independent public verification of signed Trust Receipts (with PII masking) |
| POST | `/telegram/webhook` | Enterprise webhook with secret token validation & single-use pairing |
| POST | `/kyc/authenticity` | Inward Trust KYC media authenticity analysis |
| POST | `/simulator/run` | Attack Lab scenarios (spoof, diversion, overcharge, swarm, replay) |
| GET | `/admin/audit-logs` | Tamper-evident operator action audit log |

## 4. Honest Technical Limitations & Claim Discipline

- **Pilot / Research Transports:** Telegram is utilized strictly as a field-prototype transport. Production deployment targets enterprise Meta WhatsApp Business API with TVS-approved DLT templates.
- **Inward Trust KYC Prototype:** The media authenticity pipeline incorporates the open-source research adapter (`prithivMLmods/open-deepfake-detection`) and Laplacian edge variance heuristics. It is an illustrative research prototype, NOT certified TVS biometric accuracy.
- **System Role:** Pramaan does not replace core TVS banking systems (FinnOne/LMS); it acts as an external cryptographic trust firewall around financial interactions.

