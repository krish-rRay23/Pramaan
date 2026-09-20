"""
Pramaan 2.0 Backend — Final Hardening Verification Test Suite
============================================================
Comprehensive test suite testing:
1. Genuine Ed25519 verification
2. Wrong destination (Action gate)
3. Tampered payload (Signature failure)
4. Replay attack (Nonce consumption)
5. Expired intent (TTL freshness)
6. Unauthorized agent (Partner/Agent registry)
7. Swarm correlation & cascading revocation
8. Explicit intent revocation
9. Real KYC AI deepfake adapter
10. Multi-account consistency
11. Android model contract compatibility
12. Console API routes & public key metadata
"""

import io
import time
import uuid
from datetime import datetime, timedelta, timezone
from PIL import Image

import main
import store
import crypto_utils
from kyc_authenticity import evaluate_kyc_media, MODEL_NAME, MODEL_LICENSE
from fastapi.testclient import TestClient

client = TestClient(main.app)

def run_all_hardening_tests():
    print("====================================================================")
    print("STARTING PRAMAAN 2.0 FINAL HARDENING VERIFICATION")
    print("====================================================================")

    # 1. Genuine Ed25519 Signing & Verification
    print("\n[TEST 1] Genuine Ed25519 Signing & Verification")
    issued = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    token = issued["token"]
    assert "." in token, "Token must be {body}.{signature}"
    verify_res = client.post("/intent/verify", json={
        "token": token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "purpose": "emi_due",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert verify_res["decision"] == "ALLOWED", f"Expected ALLOWED, got {verify_res['decision']}"
    assert verify_res["signature_valid"] is True
    assert verify_res["fresh"] is True
    assert verify_res["trust_receipt"] is not None
    receipt = verify_res["trust_receipt"]
    assert receipt["decision"] == "ALLOWED"
    print(f"  PASS: Genuine intent verified. Receipt: {receipt['receipt_id']}")

    # 2. Wrong Destination (Action Gate)
    print("\n[TEST 2] Wrong Destination (Exact Action Gate)")
    issued2 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    verify_res2 = client.post("/intent/verify", json={
        "token": issued2["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "purpose": "emi_due",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "rogue.scammer@upi",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert verify_res2["decision"] == "BLOCKED"
    assert verify_res2["destination_verified"] is False
    assert "destination" in verify_res2["reason"].lower()
    print("  PASS: Rogue destination blocked at Action Gate.")

    # 3. Tampered Payload (Ed25519 Signature Verification Failure)
    print("\n[TEST 3] Payload Tampering (Signature Failure)")
    issued3 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    body_part, sig_part = issued3["token"].split(".", 1)
    # tamper body by substituting amount in base64
    import base64, json
    decoded = json.loads(base64.urlsafe_b64decode(body_part.encode()))
    decoded["amount"] = 99999.0
    tampered_body = base64.urlsafe_b64encode(json.dumps(decoded).encode()).decode()
    tampered_token = f"{tampered_body}.{sig_part}"
    verify_res3 = client.post("/intent/verify", json={
        "token": tampered_token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 99999.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    }).json()
    assert verify_res3["decision"] == "BLOCKED"
    assert verify_res3["signature_valid"] is False
    print("  PASS: Tampered token failed Ed25519 asymmetric verification.")

    # 4. Replay Attack (Nonce Consumption)
    print("\n[TEST 4] Replay Attack (Nonce Consumption)")
    issued4 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    # 1st time
    client.post("/intent/verify", json={
        "token": issued4["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    })
    # 2nd time (replay)
    replay_res = client.post("/intent/verify", json={
        "token": issued4["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    }).json()
    assert replay_res["decision"] == "BLOCKED"
    assert "replay" in replay_res["reason"].lower() or "consumed" in replay_res["reason"].lower()
    print("  PASS: Replayed token rejected via consumed nonce.")

    # 5. Expiry Check (TTL Freshness)
    print("\n[TEST 5] Expired Intent (TTL Expiry)")
    past_time = (datetime.now(timezone.utc) - timedelta(seconds=200)).isoformat()
    expired_payload = {
        "intent_id": f"INT-EXP-{uuid.uuid4().hex[:6]}",
        "customer_id": "CUST-001",
        "loan_id": "LOAN-4521",
        "purpose": "emi_due",
        "amount": 3200.0,
        "action": "collect_payment",
        "destination": "tvscredit.collections@upi",
        "channel": "call",
        "partner_id": "PARTNER-TVS-01",
        "agent_id": "AGT-7701",
        "issued_at": past_time,
        "expires_at": past_time,
        "nonce": str(uuid.uuid4()),
        "audience": "tvs_customer_app"
    }
    expired_token = crypto_utils.sign_payload(expired_payload)
    exp_res = client.post("/intent/verify", json={
        "token": expired_token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    }).json()
    assert exp_res["decision"] == "BLOCKED"
    assert exp_res["fresh"] is False
    print("  PASS: Expired intent rejected by freshness gate.")

    # 6. Unauthorized Agent (Registry Check)
    print("\n[TEST 6] Unauthorized Agent")
    issued6 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    unauth_res = client.post("/intent/verify", json={
        "token": issued6["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi",
            "agent_id": "AGT-ROGUE-999"
        }
    }).json()
    assert unauth_res["decision"] in ("UNVERIFIED", "BLOCKED")
    assert unauth_res["agent_authorized"] is False
    print("  PASS: Unregistered agent rejected.")

    # 7. Swarm Correlation & Cascading Intent Revocation
    print("\n[TEST 7] Heuristic Swarm Correlation & Cascade Revocation")
    rogue_dest = f"swarm.test.{uuid.uuid4().hex[:4]}@upi"
    # Create an active intent pointing to this destination to test cascade revocation
    active_test_intent = {
        "intent_id": f"INT-SWARM-TARGET-{uuid.uuid4().hex[:6]}",
        "destination": rogue_dest
    }
    store.INTENTS_BY_ID[active_test_intent["intent_id"]] = {
        "payload": active_test_intent,
        "status": "ACTIVE"
    }
    # Simulate 3 burst requests across loans
    for lid in ["LOAN-4521", "LOAN-8832", "LOAN-1090"]:
        store.record_destination_attempt(rogue_dest, lid)

    assert rogue_dest in store.QUARANTINED_DESTINATIONS, "Rogue destination should be quarantined"
    assert store.INTENTS_BY_ID[active_test_intent["intent_id"]]["status"] == "REVOKED", "Linked active intent should be auto-revoked"
    print(f"  PASS: Swarm correlation quarantined {rogue_dest} and auto-revoked linked active intents.")

    # 8. Explicit Intent Revocation
    print("\n[TEST 8] Explicit Intent Revocation")
    issued8 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    tok8 = issued8["token"]
    iid8 = issued8["payload"]["intent_id"]
    client.post("/intent/revoke", json={"intent_id": iid8, "reason": "Customer reported suspect call"})
    rev_res = client.post("/intent/verify", json={
        "token": tok8,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    }).json()
    assert rev_res["decision"] == "BLOCKED"
    assert "revoked" in rev_res["reason"].lower()
    print("  PASS: Revoked intent blocked immediately.")

    # 9. Real KYC AI Model Adapter
    print("\n[TEST 9] Real KYC AI Model Adapter (prithivMLmods/open-deepfake-detection)")
    img = Image.new("RGB", (128, 128), color=(20, 40, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    kyc_eval = evaluate_kyc_media(buf.getvalue())
    assert kyc_eval["model_name"] == MODEL_NAME
    assert kyc_eval["license"] == MODEL_LICENSE
    assert kyc_eval["decision"] in ("ACCEPT", "REVIEW", "BLOCK")
    assert len(kyc_eval["limitations"]) >= 3
    print(f"  PASS: KYC AI Adapter evaluated media: decision={kyc_eval['decision']}, risk={kyc_eval['aggregate_risk']}, model={kyc_eval['model_name']}")

    # 10. Multi-Account Simulation Consistency
    print("\n[TEST 10] Multi-Account Simulation Consistency")
    for loan in ["LOAN-4521", "LOAN-8832", "LOAN-1090"]:
        sim_res = client.post(f"/simulator/run?scenario=genuine_interaction&loan_id={loan}").json()
        assert sim_res["passed"] is True
        assert sim_res["loan_id"] == loan
        assert sim_res["actual_decision"] == "ALLOWED"
        assert sim_res["receipt"]["loan_id"] == loan
        print(f"  PASS: Multi-account test for {loan}: {sim_res['customer_name']} (INR {sim_res['amount']})")

    # 11. Android Model Contract Compatibility
    print("\n[TEST 11] Android Client Contract Compatibility")
    sim_run = client.post("/simulator/run?scenario=wrong_destination&loan_id=LOAN-4521").json()
    # verify business fields exist
    for field in ["customer_id", "customer_name", "loan_id", "amount", "action", "destination_claimed", "exact_reason"]:
        assert field in sim_run, f"Missing business field {field}"
    print("  PASS: All business and client fields conform to contract.")

    # 12. Console API Routes & Public Key Metadata
    print("\n[TEST 12] Console Routes & Public Key Endpoint")
    r_key = client.get("/auth/public-key").json()
    assert r_key["algorithm"] == "Ed25519"
    assert r_key["curve"] == "edwards25519"
    assert len(r_key["public_key_hex"]) == 64
    assert client.get("/console").status_code == 200
    assert client.get("/admin/dashboard/stats").status_code == 200
    assert client.get("/admin/partners").status_code == 200
    assert client.get("/admin/campaigns").status_code == 200
    assert client.get("/admin/quarantine").status_code == 200
    print(f"  PASS: /auth/public-key verified Ed25519 (Key ID: {r_key['key_id']}). Console routes OK.")

    print("\n====================================================================")
    print("ALL 12 PRAMAAN 2.0 HARDENING TESTS PASSED SUCCESSFULLY!")
    print("====================================================================")

if __name__ == "__main__":
    run_all_hardening_tests()
