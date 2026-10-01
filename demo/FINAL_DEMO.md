# PRAMAAN v3.1 — Grand Finale Live Demonstration Script

## Demonstration Objective
Prove live to TVS Credit leadership that Pramaan successfully enforces the principle:
> **"Authenticate the interaction. Not the caller."**  
> Any channel may talk to the customer; only a TVS-authorized intent can authorize the exact financial action.

---

## 0. Pre-Flight Preparation Checklist
- [ ] Backend running (`uvicorn main:app --reload --port 8000`)
- [ ] Operations Console open in browser: `http://localhost:8000/console.html`
- [ ] Android App launched on physical device / emulator (or Web Verification Bridge open: `http://localhost:8000/verify?token=...`)
- [ ] Telegram Bot paired (`@pramaan_demo_bot` connected)
- [ ] Clean demo state reset executed (`python demo/reset_demo.py` or restart backend)

---

## 1. Hero Journey 1: Genuine Interaction & Trusted Handoff

### Step 1.1: Trigger Collection Interaction from TVS LMS
1. In the **Operations Console**, navigate to **Direct Dispatcher**.
2. Select:
   - **Loan ID:** `LOAN-4521 (Krish Ray - TVS Two-Wheeler Loan)`
   - **Action:** `collect_payment` (₹3,200.00)
   - **Channel:** `Telegram (Primary Live Demo)`
3. Click **"Dispatch Authorized Interaction"**.

### Step 1.2: Telegram Message Delivery
1. Observe the live customer Telegram chat (`@pramaan_demo_bot`).
2. A formal notification arrives:
   ```text
   🔒 TVS Credit — Official Payment Notice
   Hello Krish Ray! Your EMI payment of ₹3,200.00 is due.
   Click below to verify this interaction securely with TVS Credit:
   [🛡️ Verify Securely on TVS App]
   ```
3. **Key Narrative Point:** *Notice that the Telegram message contains an opaque, short-lived verification token. Even if this Telegram message is intercepted or forwarded, it cannot be tampered with.*

### Step 1.3: Exact Action Gate & Approval
1. Tap the verification link.
2. The **TVS Customer Protection App** opens via deep link (`pramaan://verify?token=...`).
3. The **Exact Action Gate** displays:
   - **Status:** `Verified TVS Credit Interaction` (Green Shield)
   - **Authorized Purpose:** EMI Payment
   - **Amount:** ₹3,200.00
   - **Authorized Destination:** `tvscredit.collections@upi`
   - **Assigned Agent:** Suresh Menon (`AGT-7701`)
4. Tap **"Authorize Payment"**.
5. The screen immediately transitions to an attested **Trust Receipt** (`RCP-...`) with Ed25519 cryptographic signature.

---

## 2. Hero Journey 2: Attack Lab & Tamper Defenses

In the **Operations Console**, open the **Attack Lab Simulator**. Run the live attack scenarios:

### Step 2.1: Destination Tampering Attack (Rogue Agent VPA)
1. Select Scenario: **"Destination Modification (Mule VPA Redirection)"**.
2. A rogue agent attempts to substitute `scam.collector@oksbi`.
3. Click **"Execute Attack Simulation"**.
4. **Live Result:**
   - Decision: **`BLOCKED`**
   - Reason Code: **`POL_MISMATCH_DESTINATION`**
   - The gate halts execution: *Claimed destination does not match TVS-authorized VPA.*

### Step 2.2: Amount Modification Attack
1. Select Scenario: **"Amount Alteration (Overcharge Scam)"**.
2. Scammer claims ₹9,999.00 instead of ₹3,200.00.
3. Click **"Execute Attack Simulation"**.
4. **Live Result:**
   - Decision: **`BLOCKED`**
   - Reason Code: **`POL_MISMATCH_AMOUNT`**
   - Overcharge blocked deterministically.

### Step 2.3: Replay Attack
1. Select Scenario: **"Replay Attack (Nonce Reuse)"**.
2. Click **"Execute Attack Simulation"**.
3. **Live Result:**
   - Decision: **`BLOCKED`**
   - Reason Code: **`POL_REPLAY_DETECTED`**
   - Capability already consumed; duplicate payment execution prevented.

---

## 3. Hero Journey 3: Coordinated Swarm Attack & Auto-Quarantine

1. In the Attack Lab, select **"Coordinated Swarm Attack"**.
2. Click **"Execute Attack Simulation"**.
3. The simulator triggers 3 rapid rogue diversion requests targeting the same mule account (`scam.swarm.ring@oksbi`).
4. **Observe the Operations Console in Real Time:**
   - **Alert Banner:** `CRITICAL: Coordinated Swarm Detected on scam.swarm.ring@oksbi`
   - **Auto-Quarantine:** Destination VPA is immediately blacklisted across TVS network.
   - **Cascade Revocation:** All active in-flight intents for that destination are instantaneously revoked.
   - Decision: **`CONTAINED`**

---

## 4. Hero Journey 4: Emergency Customer Kill Switch

1. On the Android App / Web Verification screen, simulate a suspicious or coercive situation.
2. The customer taps the emergency red button: **"I DON'T TRUST THIS REQUEST"**.
3. **Live Result:**
   - Active intent is revoked instantaneously.
   - Reported destination is flagged and quarantined.
   - Critical Fraud Incident (`INC-...`) is broadcast to the Operations Console.
   - A protective **BLOCKED** Trust Receipt is generated for customer records.

---

## 5. Hero Journey 5: Independent Trust Receipt Verification (P2-19)

1. Take the `receipt_id` generated from Journey 1 (e.g. `RCP-DF4B929D`).
2. Call the public verification endpoint:
   `GET http://localhost:8000/receipts/verify/RCP-DF4B929D`
3. Observe the response:
   ```json
   {
     "valid": true,
     "receipt_id": "RCP-DF4B929D",
     "decision": "ALLOWED",
     "amount": 3200.0,
     "masked_customer": "CU***01",
     "authority": "TVS Credit Services Ltd.",
     "status": "AUTHORITATIVE_VERIFIED"
   }
   ```
4. **Key Narrative Point:** *Borrowers and auditors can independently verify that a receipt was signed by TVS Credit without leaking sensitive personal identifiers.*
