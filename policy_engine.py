"""
Pramaan v3.1 — Versioned Financial Interaction Policy Engine
============================================================
Evaluates contact capability claims against formal versioned policy objects.
Every decision explicitly outputs:
- policy_version (e.g. POL-v3.1-DEFAULT)
- decision (ALLOWED | BLOCKED | QUARANTINED | EXPIRED | REVOKED | UNVERIFIED | STEP_UP_REQUIRED)
- reason_code (e.g. POL_OK, POL_MISMATCH_DESTINATION, POL_REPLAY_DETECTED, etc.)
- forensic details
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


class InteractionPolicy:
    """Versioned policy defining rules for financial interactions."""

    def __init__(
        self,
        policy_id: str = "POL-TVS-2026.1",
        version: str = "3.1.0",
        required_bindings: Optional[List[str]] = None,
        max_ttl_seconds: int = 180,
        step_up_threshold: float = 50000.0,
        allowed_channels: Optional[List[str]] = None,
        strict_destination_check: bool = True,
    ):
        self.policy_id = policy_id
        self.version = version
        self.required_bindings = required_bindings or [
            "loan_id", "customer_id", "purpose", "action",
            "amount", "destination", "channel", "nonce"
        ]
        self.max_ttl_seconds = max_ttl_seconds
        self.step_up_threshold = step_up_threshold
        self.allowed_channels = allowed_channels or ["call", "whatsapp", "telegram", "sms", "in_app"]
        self.strict_destination_check = strict_destination_check


# Active default policy
ACTIVE_POLICY = InteractionPolicy(
    policy_id="POL-TVS-2026.1",
    version="3.1.0",
    max_ttl_seconds=180,
    step_up_threshold=50000.0
)


class PolicyEvaluationResult:
    """Encapsulates outcome of an Exact Action Gate evaluation."""

    def __init__(
        self,
        allowed: bool,
        decision: str,
        reason_code: str,
        policy_version: str,
        details: Optional[Dict[str, Any]] = None,
        mismatch_field: Optional[str] = None,
    ):
        self.allowed = allowed
        self.decision = decision
        self.reason_code = reason_code
        self.policy_version = policy_version
        self.details = details or {}
        self.mismatch_field = mismatch_field

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "policy_version": self.policy_version,
            "mismatch_field": self.mismatch_field,
            "details": self.details,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


def evaluate_interaction_policy(
    signed_payload: Dict[str, Any],
    claimed_action: Dict[str, Any],
    policy: Optional[InteractionPolicy] = None,
    is_destination_quarantined_fn=None,
    is_nonce_consumed_fn=None,
    is_revoked_fn=None,
) -> PolicyEvaluationResult:
    """
    Evaluates signed intent against claimed interaction under active versioned policy.
    Guarantees: FAILURE MUST NEVER BECOME AUTHORIZATION.
    """
    pol = policy or ACTIVE_POLICY

    # 1. Missing Required Bindings
    for binding in pol.required_bindings:
        if binding not in signed_payload:
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MISSING_BINDING",
                policy_version=pol.version,
                mismatch_field=binding,
                details={"error": f"Required policy binding '{binding}' is missing in signed capability token."}
            )

    # 2. Destination Quarantine Check
    destination = claimed_action.get("destination") or signed_payload.get("destination")
    if is_destination_quarantined_fn and is_destination_quarantined_fn(destination):
        return PolicyEvaluationResult(
            allowed=False,
            decision="QUARANTINED",
            reason_code="POL_QUARANTINED_DESTINATION",
            policy_version=pol.version,
            mismatch_field="destination",
            details={"destination": destination, "error": "Destination is on TVS Credit active quarantine list."}
        )

    # 3. Explicit Revocation Check
    intent_id = signed_payload.get("intent_id")
    if is_revoked_fn:
        revoked, reason = is_revoked_fn(intent_id)
        if revoked:
            return PolicyEvaluationResult(
                allowed=False,
                decision="REVOKED",
                reason_code="POL_REVOKED_INTENT",
                policy_version=pol.version,
                details={"reason": reason}
            )

    # 4. Freshness / TTL Check
    expires_at_str = signed_payload.get("expires_at")
    if expires_at_str:
        try:
            exp = datetime.fromisoformat(expires_at_str)
            now = datetime.now(timezone.utc)
            if now > exp:
                return PolicyEvaluationResult(
                    allowed=False,
                    decision="EXPIRED",
                    reason_code="POL_EXPIRED_TTL",
                    policy_version=pol.version,
                    details={"expires_at": expires_at_str, "current_time": now.isoformat()}
                )
        except Exception:
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MALFORMED_EXPIRY",
                policy_version=pol.version,
                details={"error": "Invalid expiry timestamp format."}
            )

    # 5. Nonce / Replay Check
    nonce = signed_payload.get("nonce")
    if is_nonce_consumed_fn and is_nonce_consumed_fn(nonce):
        return PolicyEvaluationResult(
            allowed=False,
            decision="BLOCKED",
            reason_code="POL_REPLAY_DETECTED",
            policy_version=pol.version,
            mismatch_field="nonce",
            details={"nonce": nonce, "error": "Capability nonce already consumed in prior authorization."}
        )

    # 6. Destination Exact Match Gate
    if pol.strict_destination_check and "destination" in claimed_action:
        claimed_dest = str(claimed_action.get("destination") or "").strip().lower()
        signed_dest = str(signed_payload.get("destination") or "").strip().lower()
        if claimed_dest != signed_dest:
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MISMATCH_DESTINATION",
                policy_version=pol.version,
                mismatch_field="destination",
                details={
                    "claimed_destination": claimed_dest,
                    "authorized_destination": signed_dest,
                    "threat": "Exact Action Gate: Attempted destination diversion detected."
                }
            )

    # 7. Amount Exact Match Gate
    if "amount" in claimed_action and claimed_action["amount"] is not None:
        try:
            claimed_amt = float(claimed_action["amount"])
            signed_amt = float(signed_payload.get("amount", 0.0))
            if abs(claimed_amt - signed_amt) > 0.01:
                return PolicyEvaluationResult(
                    allowed=False,
                    decision="BLOCKED",
                    reason_code="POL_MISMATCH_AMOUNT",
                    policy_version=pol.version,
                    mismatch_field="amount",
                    details={
                        "claimed_amount": claimed_amt,
                        "authorized_amount": signed_amt,
                        "threat": "Exact Action Gate: Amount tampering detected."
                    }
                )
        except (ValueError, TypeError):
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_INVALID_AMOUNT_FORMAT",
                policy_version=pol.version,
                details={"error": "Malformed amount value."}
            )

    # 8. Purpose & Action Match
    if "purpose" in claimed_action and claimed_action["purpose"]:
        if str(claimed_action["purpose"]).strip().lower() != str(signed_payload.get("purpose", "")).strip().lower():
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MISMATCH_PURPOSE",
                policy_version=pol.version,
                mismatch_field="purpose",
                details={"claimed": claimed_action["purpose"], "authorized": signed_payload.get("purpose")}
            )

    if "action" in claimed_action and claimed_action["action"]:
        if str(claimed_action["action"]).strip().lower() != str(signed_payload.get("action", "")).strip().lower():
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MISMATCH_ACTION",
                policy_version=pol.version,
                mismatch_field="action",
                details={"claimed": claimed_action["action"], "authorized": signed_payload.get("action")}
            )

    # 9. Step-Up Authentication Rule
    amount = float(signed_payload.get("amount", 0.0))
    if amount >= pol.step_up_threshold and not claimed_action.get("device_confirmed"):
        return PolicyEvaluationResult(
            allowed=False,
            decision="STEP_UP_REQUIRED",
            reason_code="POL_STEP_UP_REQUIRED",
            policy_version=pol.version,
            details={
                "threshold": pol.step_up_threshold,
                "amount": amount,
                "message": "High-value interaction requires biometric or device-bound approval."
            }
        )

    # 10. All checks passed -> AUTHORIZATION
    return PolicyEvaluationResult(
        allowed=True,
        decision="ALLOWED",
        reason_code="POL_AUTHORIZED",
        policy_version=pol.version,
        details={
            "loan_id": signed_payload.get("loan_id"),
            "customer_id": signed_payload.get("customer_id"),
            "amount": signed_payload.get("amount"),
            "destination": signed_payload.get("destination"),
            "message": "Interaction authorized by TVS Credit Exact Action Gate."
        }
    )
