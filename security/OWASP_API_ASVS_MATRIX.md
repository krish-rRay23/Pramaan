# PRAMAAN v3.1 — Security Control Matrix (OWASP API Top 10 & ASVS 5.0.0)

**Document Version:** `v3.1-evidence`  
**Classification:** Security Architecture & Compliance Evidence Matrix  
**Standards:**
- OWASP API Security Top 10 (2023 Edition)
- OWASP Application Security Verification Standard (ASVS v5.0.0, Level 2 Target)
- Static Application Security Testing (Bandit 1.9.4: 3,207 LOC, 0 High Severity)
- Dependency Vulnerability Audit (pip-audit 2.10.1)

---

## 1. Executive Security Assurance

PRAMAAN is designed around a single unbreakable axiom:
> **Failure never becomes authorization.**  
> Any missing claim, expired timestamp, consumed nonce, invalid signature, or parameter tampering forces execution into a deterministic `BLOCKED` state.

---

## 2. OWASP API Security Top 10 (2023 Edition) Control Matrix

| OWASP API Category | Threat Vector | PRAMAAN Architecture & Implementation | Test / Evidence Reference | Status | Identified Production Gap |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **API1:2023 Broken Object Level Authorization (BOLA)** | User accesses unauthorized loan/intent objects via modified IDs | Capability intents cryptographically bind `customer_id` and `loan_id` inside the Ed25519 signed token. Claiming an object ID not bound to the token fails signature and claim validation. | `test_failure_modes.py:test_tampered_payload`<br>`policy_engine.py:evaluate_interaction_policy` | **SATISFIED** | In production, ensure OAuth2 customer bearer tokens are validated at API gateway prior to intent resolution. |
| **API2:2023 Broken Authentication** | Token forgery, credential stuffing, expired session replay | No static API secrets for customer verification. Each capability token carries an ephemeral single-use UUID nonce and 180s TTL freshness window. Signed by TVS Ed25519 private key. | `test_failure_modes.py:test_expired_intent`<br>`test_failure_modes.py:test_replay_attack` | **SATISFIED** | Implement mTLS between TVS LMS microservices and PRAMAAN engine. |
| **API3:2023 Broken Object Property Level Authorization** | Mass assignment, unauthorized field injection or tampering | Pydantic strict schemas (`models.py`) with explicit field typing. The Exact Action Gate explicitly checks `amount`, `destination`, and `purpose` against signed token payload. | `test_failure_modes.py:test_destination_mismatch`<br>`test_failure_modes.py:test_amount_mismatch` | **SATISFIED** | Add schema validation interceptor at ingress load balancer. |
| **API4:2023 Unrestricted Resource Consumption** | DoS via volumetric request flooding | In-memory token lookup with $O(1)$ dictionary lookups. Locust load tests validate 410+ req/s on single CPU with sub-200ms latency. Strict TTL purges stale intents. | `benchmarks/PERFORMANCE_RESULTS.json`<br>`benchmarks/run_performance_benchmark.py` | **SATISFIED** | Implement Redis token-bucket rate limiting (e.g. 50 req/min per IP/API key) in front of FastAPI. |
| **API5:2023 Broken Function Level Authorization (BFLA)** | Customer accessing operator-only simulation or issuance APIs | Operator endpoints require RBAC headers / authorization tokens (`roles.py`: `ADMIN`, `OPERATOR`, `AUDITOR`). Customer endpoints (`/intent/verify`, `/receipts/verify`) cannot issue or revoke keys. | `roles.py:require_permission`<br>`main.py:get_current_operator` | **SATISFIED** | Integrate with enterprise TVS Active Directory / Keycloak via OIDC JWT validation. |
| **API6:2023 Unrestricted Access to Sensitive Business Flows** | Automation of payment verification or spamming customer phones | Dynamic nonce consumption ensures each intent can only be approved once (idempotent duplicate rejection). Pluggable transports enforce customer chat registration. | `test_failure_modes.py:test_idempotency_duplicate_approval`<br>`test_failure_modes.py:test_telegram_pairing_lifecycle` | **SATISFIED** | Introduce Cloudflare Turnstile / device attestation (Play Integrity API) on mobile submission. |
| **API7:2023 Server Side Request Forgery (SSRF)** | Exploitation of webhook dispatch URLs to reach internal networks | Webhook and notification dispatches are restricted to hardcoded, certified provider domains (`api.telegram.org`, `api.callmebot.com`, Meta Cloud API). Custom user-supplied host URLs are disallowed. | `notification_adapter.py:TelegramAdapter`<br>`notification_adapter.py:CallMeBotAdapter` | **SATISFIED** | Egress network firewall policy restricting outbound HTTP to approved IP ranges. |
| **API8:2023 Security Misconfiguration** | Unpatched servers, verbose error stack traces, CORS wildcards | Global exception handlers trap unhandled errors and return generic error JSONs without exposing stack traces. CORS headers restricted in production deployment config. | `main.py:app.middleware`<br>`security/security_scanner.py` | **SATISFIED** | Enforce HSTS headers and Content-Security-Policy (CSP) at reverse proxy level. |
| **API9:2023 Improper Inventory Management** | Zombie endpoints, unversioned APIs, shadow routes | Centralized OpenAPI specification (`/openapi.json`), semantic versioning (`v3.1.0`), and deprecated routes explicitly mapped (e.g. `/whatsapp/dispatch` aliased to `/notification/dispatch`). | `main.py:FastAPI(version="3.1.0")`<br>`security/generate_sbom.py` | **SATISFIED** | Implement automated OpenAPI schema contract diffing in CI/CD pipeline. |
| **API10:2023 Unsafe Consumption of APIs** | Blind trust in third-party webhook payloads or carrier responses | Telegram webhook payloads validate `X-Telegram-Bot-Api-Secret-Token` header. Malformed JSON or unknown update IDs are rejected and deduplicated. | `test_failure_modes.py:test_telegram_update_idempotency`<br>`main.py:telegram_webhook` | **SATISFIED** | Add webhook signature validation for production Meta WhatsApp Cloud Webhooks. |

---

## 3. OWASP ASVS 5.0.0 Control Matrix (Selected Key Controls)

| ASVS Section | Control ID & Requirement | PRAMAAN Implementation | Verification Method & Artifact | Status | Gap & Production Requirement |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **V1 Architecture** | **V1.1.1** Secure SDLC and threat modeling | Threat models documented for AI deepfake swarm attacks, rogue collection agents, and man-in-the-middle UPI diversion. | `docs/SECURITY_MODEL.md`<br>`docs/FAILURE_MODES.md` | **SATISFIED** | Formal external threat modeling audit with Cert-In empaneled auditor. |
| **V2 Authentication** | **V2.1.1** Strong cryptographic credentials | Asymmetric Ed25519 keys with RFC 8032 compliance. Private key resides strictly within security authority; customer devices only hold public key. | `crypto_utils.py:sign_payload`<br>`crypto_utils.py:verify_token` | **SATISFIED** | Store root private keys in Hardware Security Module (HSM) or AWS/GCP KMS. |
| **V3 Session Mgmt** | **V3.1.1** Nonce & Session Uniqueness | Every interaction capability generates a cryptographically random UUIDv4 nonce tracked in `ISSUED_NONCES` and `CONSUMED_NONCES`. | `test_failure_modes.py:test_replay_attack` | **SATISFIED** | Distributed Redis cache with TTL matching token validity window (180s). |
| **V4 Access Control** | **V4.1.1** Least privilege enforcement | Granular role hierarchy: `VIEWER`, `OPERATOR`, `INCIDENT_RESPONDER`, `ADMIN`. Capability issuance restricted to LMS operator roles. | `roles.py:OperatorRole`<br>`main.py:issue_intent` | **SATISFIED** | Granular attribute-based access control (ABAC) per branch and loan portfolio. |
| **V5 Input Validation**| **V5.1.1** Strict server-side validation | Pydantic model validation on all inputs; schema rejects untyped fields, negative amounts, or malformed UPI handles. | `models.py:ClaimedRequest`<br>`models.py:VerifyRequest` | **SATISFIED** | Add regex validation on UPI VPA syntax at API boundary. |
| **V6 Cryptography** | **V6.1.1** Key rotation and algorithm agility | Algorithm agility: key catalog supports multiple keys with `KEY_ID` tracking. Active keys can transition to `VERIFICATION_ONLY` or `REVOKED`. | `test_failure_modes.py:test_key_rotation_lifecycle`<br>`crypto_utils.py:rotate_authority_key` | **SATISFIED** | Automated 90-day key rotation pipeline with alert triggers. |
| **V7 Error Handling** | **V7.1.1** Safe error handling without leakage | Unhandled exceptions return sanitized JSON messages (`{"detail": "..."}`) without exposing internal file paths, SQL queries, or stack traces. | `main.py:launchSafely`<br>`test_engine.py` | **SATISFIED** | Centralized structured logging to cloud SIEM (e.g. Datadog / Splunk). |
| **V8 Data Protection**| **V8.1.1** Zero-PII public exposure | Public verification endpoint (`/receipts/verify/{id}`) masks customer name, phone number, and loan identifiers, revealing only cryptographic outcome. | `test_failure_modes.py:test_receipt_verification_no_pii`<br>`main.py:public_verify_receipt` | **SATISFIED** | Implement field-level encryption for customer identifiers at rest. |
| **V10 Malicious Code** | **V10.1.1** Dependency vulnerability scanning | Automated Software Bill of Materials (`sbom.json`) generated via CycloneDX standard. Scanned via `pip-audit`. | `security/sbom.json`<br>`security/pip_audit_report.json` | **SATISFIED** | Automated Dependabot / Renovate scanning in GitHub Actions with auto-patching. |
| **V13 API Verification**| **V13.1.1** TLS in transit and payload integrity | Endpoints enforce HTTPS in deployed cloud environment (Render/HSTS). Request payloads signed with Ed25519 digital signatures. | `test_failure_modes.py:test_tampered_payload` | **SATISFIED** | Mutual TLS (mTLS) for bank LMS integration. |

---

## 4. Automated Security Scanning Telemetry

### 1. Static Code Analysis (Bandit SAST v1.9.4)
- **Scanned Codebase:** 3,207 Lines of Python Code across core security modules.
- **High Severity Findings:** `0` (Zero high severity vulnerabilities).
- **Medium Severity Findings:** `7` (Standard warnings regarding `urllib.request` URL handling and pseudo-random UUID seeds).
- **Low Severity Findings:** `9` (Standard `try/except/pass` error suppression constructs).
- **Artifact:** `security/bandit_report.json`.

### 2. Dependency Vulnerability Audit (pip-audit v2.10.1)
- **Scanned Virtual Environment:** Python 3.11 site-packages.
- **Vulnerabilities Discovered:** Known CVEs identified in inherited baseline tooling (`pillow 10.4.0`, `setuptools 65.5.0`, `pip 24.0`, `starlette 0.38.6`).
- **Remediation Action:** Production Dockerfile pins upgraded packages (`pillow>=11.0.0`, `starlette>=0.40.0`).
- **Artifact:** `security/pip_audit_report.json`.

### 3. Software Bill of Materials (SBOM)
- **Standard:** CycloneDX JSON (v1.4 compliant).
- **Component Count:** 14 verified direct and transitive dependencies with cryptographic hashes and declared licenses.
- **Artifact:** `security/sbom.json`.
