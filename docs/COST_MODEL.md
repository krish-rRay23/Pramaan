# PRAMAAN v3.1 — Capacity & Cost Planning Model

**Model Specification:** Planning Reference Architecture (ap-south-1 Mumbai)  
**Notice:** Planning model for enterprise sizing. **Not TVS Credit proprietary pricing or actual cost data.**

---

## 1. Baseline Model Parameters

| Parameter | Planning Value | Description |
| :--- | :---: | :--- |
| **Monthly Financial Interactions** | `1,000,000` | Customer outbound notices, collection calls, KYC updates |
| **Exact Action Verification Rate** | `85.0%` | Percentage of interactions reaching Exact Action Gate |
| **Notification Dispatches** | `1.2x` | Multiplier accounting for multi-channel reminders |
| **AI Inference Percentage** | `5.0%` | Facial/KYC authenticity checks on high-risk interactions |
| **Audit Retention Requirement** | `24 Months` | Statutory financial interaction audit archive duration |
| **Trust Receipt Payload Size** | `1200 Bytes` | Cryptographic Ed25519 receipt + metadata record |
| **Exchange Rate Baseline** | `1 USD = ₹86.50` | India currency conversion baseline |

---

## 2. Monthly Volumetric Envelope

- **Total Interaction Ingestion:** `1,000,000`
- **Exact Action Gate Authorizations:** `850,000`
- **Notification Messages Dispatched:** `1,200,000`
- **Inward Trust KYC Inferences:** `50,000`
- **Incidents Contained / Quarantined:** `5,000`
- **Estimated Peak Real-Time TPS:** `1.39 requests/second`

---

## 3. Infrastructure Compute & Storage Envelope

| Infrastructure Component | Sizing Envelope | Specification |
| :--- | :--- | :--- |
| **Stateless Engine Containers** | `3 Nodes (N+1)` | 2 vCPU / 4 GB RAM per container |
| **Compute Headroom** | `2592.0x` | Headroom over estimated peak traffic spike |
| **Monthly Database Ingestion** | `1.86 GB/month` | PostgreSQL state, active nonces, revocations |
| **Cumulative Regulatory Archive** | `44.7 GB (24 mo)` | S3 / GCS India-Resident object store |

---

## 4. Estimated Infrastructure Cost Breakdown

| Cost Category | Monthly (USD) | Monthly (INR) | % of Infra Total |
| :--- | :---: | :---: | :---: |
| **Stateless Container Cluster (N+1)** | `$135.0` | `₹11,677.50` | ~45% |
| **High-Performance DB (PostgreSQL)** | `$0.64` | `₹55.36` | ~20% |
| **Cold Audit Archive Storage** | `$1.03` | `₹89.09` | ~10% |
| **AI Authenticity Inference Nodes** | `$75.0` | `₹6,487.50` | ~18% |
| **Managed Load Balancer (ALB)** | `$35.0` | `₹3,027.50` | ~7% |
| **TOTAL INFRASTRUCTURE ENVELOPE** | **`$246.67`** | **`₹21,337.02`** | **100%** |

---

## 5. Unit Economics & Cost Drivers

- **Pramaan Pure Infrastructure Cost per 1,000 Interactions:** **`₹21.337`** (`$0.2467`)
- **Pramaan Pure Infrastructure Cost per 1,000,000 Interactions:** **`₹21,337.02`** (`$246.67`)

### Cost Driver Hierarchy:
1. **Telephony / WhatsApp Channel Fees:** External carrier transport (e.g. Meta Cloud API ~₹0.35/utility msg) accounts for ~85% of total interaction delivery cost, dwarfing core cryptographic compute.
2. **Stateless Compute:** Running redundant high-availability containers ensures 99.99% availability during collection rush hours.
3. **Inward Trust AI Processing:** Selective sampling (5% high-risk) keeps AI inference costs minimal while mitigating deepfake impersonation.
4. **Cryptographic Storage:** Ed25519 signatures and canonical JSON receipts are compact (~1.2 KB), making multi-year regulatory retention negligible in cost.
