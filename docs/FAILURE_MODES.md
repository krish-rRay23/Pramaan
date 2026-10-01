# PRAMAAN v3.1 — Failure Modes & Defensive Invariants Matrix

## Core Defensive Invariant
> **"FAILURE MUST NEVER BECOME AUTHORIZATION."**  
> If any cryptographic check, network request, database lookup, policy rule, timeout, or external dependency fails or degrades, the system must deterministically fail closed into **BLOCKED** or **UNVERIFIED**. A transaction is **NEVER** authorized by default or on error.

---

## 1. Automated Failure-Mode Coverage Matrix

Every failure mode listed below is verified by automated test suites (`test_failure_modes.py`, `test_hardening.py`, `test_engine.py`):

| Failure Scenario | Trigger Condition | Engine Behavior | Final Decision | Reason Code |
| :--- | :--- | :--- | :---: | :--- |
| **1. Invalid Signature** | Forged signature hex or bit flips | Cryptographic verification fails | **BLOCKED** | `POL_INVALID_SIGNATURE` |
| **2. Wrong Key ID** | Signed by foreign / uncataloged key | Key lookup fails in registry | **BLOCKED** | `POL_UNKNOWN_KEY` |
| **3. Expired Key (Revoked)** | Key transitioned to `REVOKED` | Key lifecycle status check fails | **BLOCKED** | `POL_REVOKED_KEY` |
| **4. Expired Intent (TTL)** | UTC time > `expires_at` (180s) | Freshness gate intercepts | **BLOCKED** | `POL_EXPIRED_TTL` |
| **5. Nonce Replay** | Same nonce presented a 2nd time | Nonce found in consumed set | **BLOCKED** | `POL_REPLAY_DETECTED` |
| **6. Payload Tampering** | Amount/destination modified in token | Canonical signature check fails | **BLOCKED** | `POL_INVALID_SIGNATURE` |
| **7. Wrong Audience/Session** | Target audience != `tvs_customer_app` | Session/Audience binding check fails | **BLOCKED** | `POL_AUDIENCE_MISMATCH` |
| **8. Amount Mismatch** | Claimed amount != Intent amount | Exact Action Gate check fails | **BLOCKED** | `POL_MISMATCH_AMOUNT` |
| **9. Destination Mismatch** | Claimed VPA != Authorized VPA | Exact Action Gate check fails | **BLOCKED** | `POL_MISMATCH_DESTINATION` |
| **10. Wrong Action/Purpose** | Action outside authorized purpose | Action matrix validation fails | **BLOCKED** | `POL_PURPOSE_MISMATCH` |
| **11. Unauthorized Agent** | Agent suspended or action not in scope | Agent capability registry check | **BLOCKED** | `POL_UNAUTHORIZED_AGENT` |
| **12. Unauthorized Partner** | Partner suspended or revoked | Partner status validation fails | **BLOCKED** | `POL_UNAUTHORIZED_PARTNER` |
| **13. Duplicate Approval** | Client retries without `idempotent=True` | Nonce already consumed | **BLOCKED** | `POL_REPLAY_DETECTED` |
| **14. Safe Idempotent Retry** | Client retries with `idempotent=True` | Returns prior valid receipt safely | **ALLOWED** | `POL_AUTHORIZED` (No duplicate nonce) |
| **15. DB Unavailability** | PostgreSQL disconnected or timeout | Fails closed with clean 503 error | **503 / BLOCKED** | No unauthorized outcome issued |
| **16. Notification Failure** | Telegram / WhatsApp network outage | Outbox retries asynchronously | **UNAFFECTED** | Verification proceeds independently |
| **17. Backend Timeout** | Gateway network timeout on mobile | Android app defaults to unverified | **UNVERIFIED** | Local action gate remains locked |
| **18. Malformed / Corrupt Input** | Garbage bytes or invalid JSON | Schema validation & parser exception | **BLOCKED** | HTTP 400/422; no action |
| **19. Public Key Unavailable** | Network partition fetching keys | Signature cannot be verified | **BLOCKED** | App blocks payment |
| **20. AI Model Timeout / Bad Media** | Corrupted image, OOM, timeout | Graceful degradation to heuristic | **BLOCK / REVIEW** | Defaults to high risk (0.95) |

---

## 2. In-Depth Failure Case Analysis

### 2.1 The Destination Diversion Case
- **Scenario:** A rogue recovery agent contacts borrower claiming an EMI payment of ₹3,200. The agent provides their personal UPI ID (`scam.collector@oksbi`).
- **Pramaan Action:** The Android app receives the claim and evaluates it against the signed TVS intent (`tvscredit.collections@upi`).
- **Result:** The Exact Action Gate detects the discrepancy, highlights the rogue destination in red, logs an anomaly, and generates a **BLOCKED** Trust Receipt. The customer cannot proceed with payment to the personal account.

### 2.2 The Notification Partition Case
- **Scenario:** Telegram or WhatsApp experiences an infrastructure outage.
- **Pramaan Action:** The Transactional Notification Outbox enqueues the message with an exponential backoff retry policy. In-app verification operates directly via deep link or local intent resolution.
- **Result:** External carrier failures never deadlock or compromise financial interaction verification.

### 2.3 The AI Pipeline Degradation Case
- **Scenario:** A borrower uploads an unreadable or corrupt image file, or the AI service experiences a container memory spike.
- **Pramaan Action:** The system catches the error, marks the risk score at maximum (`0.95`), and classifies the verdict as `flagged` with a policy reason of `[BLOCK]`.
- **Result:** Corrupted or failing AI input **never** passes as authentic.
