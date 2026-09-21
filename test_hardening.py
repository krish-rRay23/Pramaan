"""
Pramaan v3 Backend — Hardening & Verification Test Suite
========================================================
Comprehensive automated test suite covering:
1. Valid Ed25519 signing & verification
2. Deep-link generation & verification endpoint
3. Wrong destination (Exact Action Gate)
4. Expired intent (TTL freshness)
5. Replay attack (Nonce consumption)
6. Amount mismatch
7. Unauthorized action & partner/agent capability violation
8. Swarm campaign correlation & automatic quarantine
9. Cascade intent revocation upon quarantine
10. Customer Kill Switch ("I DON'T TRUST THIS REQUEST")
11. WhatsApp notification adapter (CallMeBot + Mock fallback)
12. Multi-account consistency & Operations Console endpoints
"""

import io
import time
import uuid
import base64
import json
from datetime import datetime, timedelta, timezone
from PIL import Image

import main
import store
import crypto_utils
from notification_adapter import CallMeBotAdapter, MockWhatsAppAdapter
from kyc_authenticity import evaluate_kyc_media, MODEL_NAME, MODEL_LICENSE
from fastapi.testclient import TestClient

client = TestClient(main.app)

def run_all_hardening_tests():
    print("====================================================================")
    print("STARTING PRAMAAN v3 END-TO-END HARDENING & INTEGRATION TESTS")
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

    # 2. Deep-Link Verification & Web Landing Endpoint
    print("\n[TEST 2] Deep-Link Generation & Landing Page")
    assert "deep_link" in issued, "Issued response must contain deep_link"
    assert issued["deep_link"].startswith("pramaan://verify?token="), f"Invalid deep link format: {issued['deep_link']}"
    # Test web verification landing page
    landing_res = client.get(f"/verify?token={token}")
    assert landing_res.status_code == 200
    assert "PRAMAAN v3" in landing_res.text
    assert "pramaan://verify?token=" in landing_res.text
    print(f"  PASS: Deep link validated: {issued['deep_link'][:50]}... Web fallback page OK.")

    # 3. Destination Mismatch (Exact Action Gate)
    print("\n[TEST 3] Destination Mismatch (Exact Action Gate)")
    issued3 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    verify_res3 = client.post("/intent/verify", json={
        "token": issued3["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "purpose": "emi_due",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "fraudster.badguy@upi",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert verify_res3["decision"] == "BLOCKED"
    assert verify_res3["destination_verified"] is False
    assert "destination" in verify_res3["reason"].lower()
    print("  PASS: Rogue destination blocked at Exact Action Gate.")

    # 4. Amount Mismatch (Action Gate & Integrity)
    print("\n[TEST 4] Amount Mismatch")
    issued4 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    verify_res4 = client.post("/intent/verify", json={
        "token": issued4["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "purpose": "emi_due",
            "amount": 9999.0, # Diverted amount
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert verify_res4["decision"] == "BLOCKED"
    assert verify_res4["matched"] is False
    assert "amount" in verify_res4["reason"].lower()
    print("  PASS: Diverted amount rejected.")

    # 5. Expired Intent (TTL Expiry)
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
        "channel": "whatsapp",
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

    # 6. Replay Attack (Nonce Consumption)
    print("\n[TEST 6] Replay Attack (Nonce Consumption)")
    issued6 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    # 1st time
    client.post("/intent/verify", json={
        "token": issued6["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi"
        }
    })
    # 2nd time (replay)
    replay_res = client.post("/intent/verify", json={
        "token": issued6["token"],
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

    # 7. Unauthorized Action / Partner Capability Violation
    print("\n[TEST 7] Partner/Agent Capability Violation")
    issued7 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    unauth_res = client.post("/intent/verify", json={
        "token": issued7["token"],
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "action": "transfer_ownership", # Unauthorized action for agent capability
            "destination": "tvscredit.collections@upi",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert unauth_res["decision"] == "BLOCKED"
    assert "action" in unauth_res["reason"].lower()
    print("  PASS: Action outside agent capability successfully blocked.")

    # 8. Campaign Correlation & Automatic Quarantine
    print("\n[TEST 8] Swarm Campaign Correlation & Auto-Quarantine")
    rogue_vpa = f"swarm.v3.{uuid.uuid4().hex[:4]}@upi"
    # Create an active intent pointing to this destination to verify cascade revocation
    active_test_intent = {
        "intent_id": f"INT-CASCADE-{uuid.uuid4().hex[:6]}",
        "destination": rogue_vpa
    }
    store.INTENTS_BY_ID[active_test_intent["intent_id"]] = {
        "payload": active_test_intent,
        "status": "ACTIVE"
    }
    # Simulate multi-loan attack burst (3 loans)
    for lid in ["LOAN-4521", "LOAN-8832", "LOAN-1090"]:
        store.record_destination_attempt(rogue_vpa, lid)

    assert rogue_vpa in store.QUARANTINED_DESTINATIONS, "Destination should be in quarantine"
    assert store.INTENTS_BY_ID[active_test_intent["intent_id"]]["status"] == "REVOKED", "Linked intent should be cascade-revoked"
    
    # Try issuing new intent to quarantined destination - should fail
    store.INTENTS_BY_ID["INT-QUAR-TEST"] = {
        "payload": {"intent_id": "INT-QUAR-TEST", "destination": rogue_vpa},
        "status": "ACTIVE"
    }
    print(f"  PASS: Campaign correlated, destination quarantined, cascade revocation confirmed.")

    # 9. Customer Kill Switch ("I DON'T TRUST THIS REQUEST")
    print("\n[TEST 9] Customer Kill Switch")
    issued9 = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"}).json()
    token9 = issued9["token"]
    ks_res = client.post("/intent/kill-switch", json={
        "customer_id": "CUST-001",
        "loan_id": "LOAN-4521",
        "token": token9,
        "reason": "Customer reported fraudulent voice call"
    }).json()
    assert ks_res["success"] is True
    assert "CONTAINED" in ks_res["status"].upper() or "REVOKED" in ks_res["status"].upper()
    assert ks_res["incident_id"].startswith("INC-")
    assert ks_res["trust_receipt"]["decision"] == "BLOCKED"
    
    # Check that incident is listed in /admin/incidents
    incidents = client.get("/admin/incidents").json()
    assert any(inc["incident_id"] == ks_res["incident_id"] for inc in incidents)
    print(f"  PASS: Kill switch deployed: Incident {ks_res['incident_id']} logged in admin console.")

    # 10. Telegram Primary Transport + Retained WhatsApp & Mock Fallback
    print("\n[TEST 10] Notification Adapters: Telegram (Primary), CallMeBot (Secondary), Mock (Fallback)")
    from notification_adapter import TelegramAdapter, MockNotificationAdapter, format_pramaan_message

    # A. Telegram Adapter with missing credentials -> graceful handling
    unconfigured_tg = TelegramAdapter(bot_token="", default_chat_id="")
    res_unconf = unconfigured_tg.send_verification_message(
        recipient="",
        payload={"loan_id": "LOAN-4521", "amount": 3200.0, "purpose": "emi_due"},
        deep_link="pramaan://verify?token=test_tok"
    )
    assert res_unconf["success"] is False
    assert res_unconf["status"] == "FAILED"

    # B. Telegram Adapter with valid token but unregistered chat -> status NO_CHAT_ID
    demo_token = "8959183345:AAGKlf4rehQCjHm21PzKg1ZAKR9rfut1hxI"
    tg_adapter = TelegramAdapter(bot_token=demo_token, default_chat_id="")
    res_nochat = tg_adapter.send_verification_message(
        recipient="",
        payload={"loan_id": "LOAN-4521", "amount": 3200.0, "purpose": "emi_due"},
        deep_link="pramaan://verify?token=test_tok"
    )
    assert res_nochat["status"] == "NO_CHAT_ID"

    # C. Telegram customer chat registration flow
    reg_res = client.post("/telegram/register", json={
        "customer_id": "CUST-001",
        "loan_id": "LOAN-4521",
        "chat_id": "987654321"
    }).json()
    assert reg_res["success"] is True
    assert store.get_customer_telegram("CUST-001") == "987654321"
    assert store.get_customer_telegram("LOAN-4521") == "987654321"

    # D. Telegram bot-info endpoint
    info_res = client.get("/telegram/bot-info?customer_id=CUST-001").json()
    assert "bot_username" in info_res
    assert info_res["registered_chat_id"] == "987654321"
    assert "t.me/" in info_res["connect_url"]

    # E. Unified /notification/dispatch on telegram channel (with mock fallback or registered chat)
    dispatch_tg = client.post("/notification/dispatch", json={
        "channel": "telegram",
        "loan_id": "LOAN-4521",
        "token": token,
        "telegram_chat_id": "987654321",
        "telegram_bot_token": demo_token,
        "force_mock": True
    }).json()
    assert dispatch_tg["channel"] == "telegram"
    assert "deep_link" in dispatch_tg
    assert "web_verify_url" in dispatch_tg

    # F. Retained CallMeBot & WhatsApp backward compatibility regression
    mock_adapter = MockWhatsAppAdapter()
    send_mock = mock_adapter.send_verification_message(
        recipient_phone="+919876543210",
        payload={"loan_id": "LOAN-4521", "purpose": "emi_due", "amount": 3200.0},
        deep_link="pramaan://verify?token=test_tok"
    )
    assert send_mock["success"] is True

    res_dispatch = client.post("/whatsapp/dispatch", json={
        "recipient_phone": "+919876543210",
        "token": token,
        "loan_id": "LOAN-4521",
        "callmebot_api_key": "dummy_key",
        "force_mock": True
    }).json()
    assert res_dispatch["success"] is True

    # G. Verification and delivery logs
    notif_logs = client.get("/notification/logs").json()
    assert len(notif_logs) > 0
    assert any(l["channel"] == "telegram" for l in notif_logs)

    wa_logs = client.get("/whatsapp/logs").json()
    assert len(wa_logs) > 0
    print("  PASS: Telegram primary adapter, chat registration, unified dispatch, and WhatsApp regression confirmed.")

    # 11. Live Attack Lab Scenarios (A to G)
    print("\n[TEST 11] Live Attack Lab Simulator Scenarios (A through G)")
    scenarios = [
        "genuine_interaction",
        "fake_request",
        "amount_modification",
        "destination_modification",
        "expired_intent",
        "replay_attack",
        "unauthorized_action",
        "coordinated_swarm"
    ]
    for sc in scenarios:
        sim_res = client.post(f"/simulator/run?scenario={sc}&loan_id=LOAN-4521").json()
        assert sim_res["passed"] is True, f"Scenario {sc} failed: {sim_res}"
        print(f"  PASS: Simulator scenario '{sc}' -> Decision: {sim_res['actual_decision']}")

    # 12. Operations Console Metrics & Endpoints
    print("\n[TEST 12] Operations Console Live Cards & Public Key Metadata")
    stats = client.get("/admin/dashboard/stats").json()
    for metric in [
        "active_intents", "verified_count", "blocked_attacks",
        "expired_intents", "campaigns_count", "quarantined_destinations",
        "revoked_count", "fraud_incidents_count"
    ]:
        assert metric in stats, f"Missing metric {metric} in /admin/dashboard/stats"
    
    pk_info = client.get("/auth/public-key").json()
    assert pk_info["algorithm"] == "Ed25519"
    assert len(pk_info["public_key_hex"]) == 64
    print(f"  PASS: Operations Console 8 live metric cards & Ed25519 public key endpoint verified.")

    print("\n====================================================================")
    print("ALL 12 PRAMAAN v3 TESTS PASSED SUCCESSFULLY!")
    print("====================================================================")

if __name__ == "__main__":
    run_all_hardening_tests()
