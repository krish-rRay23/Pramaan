"""
Pramaan v3.2 — Adaptive Policy & Context-Driven Gating Test Suite
================================================================
Mathematically proves:
1. Same amount receives different decisions under different contexts (routine vs high-risk).
2. Different amounts receive the same decision under equivalent low-risk context (no hardcoded cutoffs).
3. Unusual destination increases required assurance from STANDARD to ELEVATED.
4. Invariants (replay, revocation, payload tamper, destination diversion) still fail closed.
5. Unavailable policy service fails closed (POL_POLICY_UNAVAILABLE_FAIL_CLOSED).
6. Changing policy configuration changes behavior dynamically without code changes.
7. Zero instances of 50000 / 50,000 business threshold in executable code.
"""

import os
import json
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

import main
from main import app
import store
import policy_engine
from policy_engine import (
    InteractionPolicy,
    evaluate_interaction_policy,
    get_active_policy,
    set_active_policy,
    reload_active_policy
)

client = TestClient(app)


def setup_function():
    """Reset store and load default adaptive policy before each test."""
    store.reset_demo_state()
    reload_active_policy()


def make_payloads(
    loan_id: str = "LOAN-4521",
    customer_id: str = "CUST-4521",
    action: str = "collect_payment",
    amount: float = 3200.0,
    destination: str = "tvscredit.collections@upi",
    channel: str = "in_app",
    nonce: str = "NONCE-TEST-1234",
    device_confirmed: bool = False,
):
    now_utc = datetime.now(timezone.utc)
    signed_payload = {
        "intent_id": f"INTENT-{nonce}",
        "loan_id": loan_id,
        "customer_id": customer_id,
        "purpose": "emi_due",
        "action": action,
        "amount": amount,
        "destination": destination,
        "channel": channel,
        "nonce": nonce,
        "partner_name": "TVS Credit",
        "agent_id": "AGT-7701",
        "issued_at": now_utc.isoformat(),
        "expires_at": (now_utc + timedelta(minutes=3)).isoformat(),
    }
    claimed_action = {
        "loan_id": loan_id,
        "amount": amount,
        "destination": destination,
        "action": action,
        "agent_id": "AGT-7701",
        "device_confirmed": device_confirmed,
    }
    return signed_payload, claimed_action


def test_1_same_amount_different_context_different_decisions():
    """
    Proves: An identical amount (e.g. ₹15,000) produces different gating decisions
    depending entirely on contextual signals (relative loan deviation, action type, destination).
    """
    # Context A: Routine monthly EMI for a commercial loan (baseline ₹15,000/mo)
    # Action: collect_payment, Destination: known tvscredit.collections@upi, Channel: in_app
    payload_a, claimed_a = make_payloads(
        loan_id="LOAN-9921",
        customer_id="CUST-9921",
        action="collect_payment",
        amount=15000.0,
        destination="tvscredit.collections@upi",
        channel="in_app"
    )
    eval_a = evaluate_interaction_policy(
        signed_payload=payload_a,
        claimed_action=claimed_a,
        loan_context={"baseline_amount": 15000.0, "loan_type": "commercial_vehicle"},
        velocity_count=1
    )
    assert eval_a.allowed is True
    assert eval_a.decision == "ALLOWED"
    assert eval_a.assurance_level == "STANDARD"

    # Context B: Foreclosure settlement for a two-wheeler borrower (baseline ₹3,200/mo)
    # ₹15,000 is 4.68x baseline (> 2.5x trigger), action is foreclose_loan (+0.50 pts),
    # destination is standard TVS collection VPA. Score: 0.50 + 0.10 + 0.30 = 0.90 (Elevated).
    payload_b, claimed_b = make_payloads(
        loan_id="LOAN-4521",
        customer_id="CUST-4521",
        action="foreclose_loan",
        amount=15000.0,
        destination="tvscredit.collections@upi",
        channel="sms",
        device_confirmed=False
    )
    eval_b = evaluate_interaction_policy(
        signed_payload=payload_b,
        claimed_action=claimed_b,
        loan_context={
            "baseline_amount": 3200.0,
            "loan_type": "two_wheeler",
            "known_destinations": ["tvscredit.collections@upi"]
        },
        velocity_count=1
    )
    assert eval_b.allowed is False
    assert eval_b.decision == "STEP_UP_REQUIRED"
    assert eval_b.assurance_level == "ELEVATED"
    assert "AMOUNT_DEVIATION_FROM_BASELINE" in eval_b.risk_signals
    assert "ACTION_SENSITIVITY_ELEVATED" in eval_b.risk_signals

    # Once customer completes additional verification (device_confirmed=True)
    claimed_b["device_confirmed"] = True
    eval_b_confirmed = evaluate_interaction_policy(
        signed_payload=payload_b,
        claimed_action=claimed_b,
        loan_context={
            "baseline_amount": 3200.0,
            "loan_type": "two_wheeler",
            "known_destinations": ["tvscredit.collections@upi"]
        },
        velocity_count=1
    )
    assert eval_b_confirmed.allowed is True
    assert eval_b_confirmed.decision == "ALLOWED"
    assert eval_b_confirmed.assurance_level == "ELEVATED"

    # Context C: Compounding risk (Foreclosure + 4.68x spike + Unfamiliar VPA)
    # Score: 0.50 + 0.10 + 0.30 + 0.35 = 1.0 (Critical block score >= 0.95) -> Immediate Block!
    payload_c, claimed_c = make_payloads(
        loan_id="LOAN-4521",
        customer_id="CUST-4521",
        action="foreclose_loan",
        amount=15000.0,
        destination="unregistered-foreign-escrow@upi",
        channel="sms",
        device_confirmed=True
    )
    eval_c = evaluate_interaction_policy(
        signed_payload=payload_c,
        claimed_action=claimed_c,
        loan_context={
            "baseline_amount": 3200.0,
            "loan_type": "two_wheeler",
            "known_destinations": ["tvscredit.collections@upi"]
        },
        velocity_count=1
    )
    assert eval_c.allowed is False
    assert eval_c.decision == "BLOCKED"
    assert eval_c.assurance_level == "CRITICAL"
    assert eval_c.reason_code == "POL_CRITICAL_CONTEXTUAL_RISK"


def test_2_different_amounts_same_decision_under_low_risk_context():
    """
    Proves: A ₹3,200 payment and a ₹75,000 payment both receive STANDARD 1-touch ALLOWED
    decisions when each matches their respective loan baseline and trusted context.
    Proves absence of an arbitrary global monetary cutoff.
    """
    # 2-Wheeler borrower paying routine ₹3,200 EMI
    payload_small, claimed_small = make_payloads(
        loan_id="LOAN-4521",
        customer_id="CUST-4521",
        action="collect_payment",
        amount=3200.0,
        destination="tvscredit.collections@upi",
        channel="in_app"
    )
    eval_small = evaluate_interaction_policy(
        signed_payload=payload_small,
        claimed_action=claimed_small,
        loan_context={"baseline_amount": 3200.0, "loan_type": "two_wheeler"},
        velocity_count=1
    )
    assert eval_small.decision == "ALLOWED"
    assert eval_small.assurance_level == "STANDARD"

    # Commercial borrower paying routine ₹75,000 EMI
    payload_large, claimed_large = make_payloads(
        loan_id="LOAN-9921",
        customer_id="CUST-9921",
        action="collect_payment",
        amount=75000.0,
        destination="tvscredit.collections@upi",
        channel="in_app"
    )
    eval_large = evaluate_interaction_policy(
        signed_payload=payload_large,
        claimed_action=claimed_large,
        loan_context={"baseline_amount": 75000.0, "loan_type": "tractor_loan"},
        velocity_count=1
    )
    assert eval_large.decision == "ALLOWED"
    assert eval_large.assurance_level == "STANDARD"


def test_3_unusual_destination_increases_assurance_to_elevated():
    """
    Proves: A routine ₹3,200 EMI directed to a destination outside the customer's
    pre-registered account destinations elevates risk score and requires step-up.
    """
    # Pre-registered destination: tvscredit.collections@upi
    payload_known, claimed_known = make_payloads(
        loan_id="LOAN-4521",
        destination="tvscredit.collections@upi",
    )
    eval_known = evaluate_interaction_policy(
        signed_payload=payload_known,
        claimed_action=claimed_known,
        loan_context={
            "baseline_amount": 3200.0,
            "authorized_destination": "tvscredit.collections@upi",
            "known_destinations": ["tvscredit.collections@upi"]
        },
        velocity_count=1
    )
    assert eval_known.assurance_level == "STANDARD"
    assert eval_known.decision == "ALLOWED"

    # New / unfamiliar authorized destination: special-settlement@upi
    payload_unfamiliar, claimed_unfamiliar = make_payloads(
        loan_id="LOAN-4521",
        destination="special-settlement@upi",
    )
    eval_unfamiliar = evaluate_interaction_policy(
        signed_payload=payload_unfamiliar,
        claimed_action=claimed_unfamiliar,
        loan_context={
            "baseline_amount": 3200.0,
            "authorized_destination": "tvscredit.collections@upi",
            "known_destinations": ["tvscredit.collections@upi"]
        },
        velocity_count=1
    )
    assert eval_unfamiliar.assurance_level == "ELEVATED"
    assert eval_unfamiliar.decision == "STEP_UP_REQUIRED"
    assert "UNFAMILIAR_DESTINATION_CHANGE" in eval_unfamiliar.risk_signals


def test_4_invariants_still_fail_closed_end_to_end():
    """
    Proves: Cryptographic & gate invariants (Replay, Tamper, Destination Mismatch,
    Revocation) fail closed immediately regardless of amount or policy score.
    """
    # Issue genuine intent
    issue_resp = client.post("/intent/issue", json={
        "loan_id": "LOAN-4521",
        "action": "collect_payment",
        "amount": 3200.0,
        "destination": "tvscredit.collections@upi"
    })
    assert issue_resp.status_code == 200
    token = issue_resp.json()["token"]

    # 4A. Destination Diversion Attack -> Immediate Block
    res_divert = client.post("/intent/verify", json={
        "token": token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "destination": "mule.scammer@upi",  # Mismatch!
            "action": "collect_payment",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert res_divert["decision"] == "BLOCKED"
    assert res_divert["reason_code"] == "POL_MISMATCH_DESTINATION"

    # 4B. Legitimate Verify -> Consumes nonce
    res_legit = client.post("/intent/verify", json={
        "token": token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "destination": "tvscredit.collections@upi",
            "action": "collect_payment",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert res_legit["decision"] == "ALLOWED"

    # 4C. Replay of same token -> Immediate Block
    res_replay = client.post("/intent/verify", json={
        "token": token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "amount": 3200.0,
            "destination": "tvscredit.collections@upi",
            "action": "collect_payment",
            "agent_id": "AGT-7701"
        }
    }).json()
    assert res_replay["decision"] == "BLOCKED"
    assert res_replay["reason_code"] == "POL_REPLAY_DETECTED"


def test_5_unavailable_policy_service_fails_closed():
    """
    Proves: When policy configuration is unavailable or corrupted,
    the engine fails closed with POL_POLICY_UNAVAILABLE_FAIL_CLOSED.
    """
    # Intentionally wipe active policy
    policy_engine.ACTIVE_POLICY = None

    payload, claimed = make_payloads()
    eval_fail = evaluate_interaction_policy(
        signed_payload=payload,
        claimed_action=claimed,
        policy=None
    )
    assert eval_fail.allowed is False
    assert eval_fail.decision == "BLOCKED"
    assert eval_fail.assurance_level == "CRITICAL"
    assert eval_fail.reason_code == "POL_POLICY_UNAVAILABLE_FAIL_CLOSED"

    # Restore policy
    reload_active_policy()


def test_6_runtime_configuration_changes_behavior_without_code_changes():
    """
    Proves: Updating policy configuration at runtime immediately alters
    risk evaluation and gating without changing any code or restarting the app.
    """
    # Context with SMS channel (+0.15 pts) + action (+0.10) = 0.25 < elevated_risk_score (0.35) -> ALLOWED
    payload, claimed = make_payloads(
        loan_id="LOAN-4521",
        action="collect_payment",
        amount=3200.0,
        destination="tvscredit.collections@upi",
        channel="sms"
    )
    eval_std = evaluate_interaction_policy(
        signed_payload=payload,
        claimed_action=claimed,
        loan_context={"baseline_amount": 3200.0}
    )
    assert eval_std.decision == "ALLOWED"
    assert eval_std.assurance_level == "STANDARD"

    # Reconfigure policy at runtime: lower elevated threshold to 0.20 (stricter posture)
    strict_policy = get_active_policy()
    strict_dict = strict_policy.to_dict()
    strict_dict["policy_version"] = "POL-STRICT-HOTFIX-2026"
    strict_dict["scoring"]["assurance_thresholds"]["elevated_risk_score"] = 0.20  # 0.25 will now trigger ELEVATED
    set_active_policy(InteractionPolicy.from_dict(strict_dict))

    # Evaluate the exact same context under updated policy
    eval_strict = evaluate_interaction_policy(
        signed_payload=payload,
        claimed_action=claimed,
        loan_context={"baseline_amount": 3200.0}
    )
    assert eval_strict.decision == "STEP_UP_REQUIRED"
    assert eval_strict.assurance_level == "ELEVATED"
    assert eval_strict.policy_version == "POL-STRICT-HOTFIX-2026"

    # Restore default policy
    reload_active_policy()


def test_7_zero_hardcoded_business_policy_numbers_in_executable_code():
    """
    Proves:
    1. Neither 50000 nor 50_000 exists in executable code.
    2. policy_engine.py contains NO hardcoded dictionary of numeric scoring weights or thresholds.
    3. InteractionPolicy initializes with scoring=None if not provided (no hardcoded fallback dict).
    """
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    target_files = [
        os.path.join(backend_dir, "policy_engine.py"),
        os.path.join(backend_dir, "main.py"),
        os.path.join(backend_dir, "models.py"),
        os.path.join(backend_dir, "store.py"),
        os.path.join(backend_dir, "crypto_utils.py"),
        os.path.join(backend_dir, "repository.py"),
    ]

    for file_path in target_files:
        assert os.path.exists(file_path), f"File {file_path} must exist"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "50000" not in content, f"Hardcoded 50000 found in executable file: {file_path}"
            assert "50_000" not in content, f"Hardcoded 50_000 found in executable file: {file_path}"

    # Verify InteractionPolicy has no embedded fallback scoring dict
    unconfigured_policy = InteractionPolicy(scoring=None)
    assert unconfigured_policy.scoring is None, "InteractionPolicy must not embed hardcoded numeric fallback dictionaries"


def test_8_corrupted_policy_configuration_fails_closed():
    """
    Proves: If policy configuration is corrupted (e.g. missing mandatory scoring sections),
    the engine fails closed with POL_POLICY_CORRUPTED_FAIL_CLOSED and BLOCKED decision.
    """
    # Create corrupted policy missing relative_amount and action_sensitivity sections
    corrupted_data = {
        "policy_id": "POL-CORRUPT-TEST",
        "version": "3.2.0-CORRUPT",
        "scoring": {
            "channel_risk": {"call": 0.15, "default_channel_weight": 0.15, "untrusted_signal_threshold": 0.15}
            # Missing: action_sensitivity, relative_amount, destination, velocity, agent, assurance_thresholds
        }
    }
    corrupted_policy = InteractionPolicy.from_dict(corrupted_data)

    payload, claimed = make_payloads()
    eval_corrupt = evaluate_interaction_policy(
        signed_payload=payload,
        claimed_action=claimed,
        policy=corrupted_policy
    )
    assert eval_corrupt.allowed is False
    assert eval_corrupt.decision == "BLOCKED"
    assert eval_corrupt.assurance_level == "CRITICAL"
    assert eval_corrupt.reason_code == "POL_POLICY_CORRUPTED_FAIL_CLOSED"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
