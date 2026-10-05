"""
Pramaan v3.2 — Versioned Adaptive Financial Interaction Policy Engine
====================================================================
Evaluates contact capability claims against formal versioned policy objects.
Replaces static amount cutoffs with an adaptive, context-driven risk evaluation model.

Architecture:
context -> risk/policy evaluation -> required assurance level -> Exact Action Gate -> ALLOW / STEP-UP / BLOCK

Outputs:
- decision (ALLOWED | STEP_UP_REQUIRED | BLOCKED | QUARANTINED | REVOKED | EXPIRED | UNVERIFIED)
- assurance_level (STANDARD | ELEVATED | CRITICAL)
- reason_code (e.g. POL_AUTHORIZED, POL_STEP_UP_REQUIRED, POL_MISMATCH_DESTINATION, etc.)
- policy_version (e.g. 3.2.0)
- risk_signals (e.g. ["ACTION_SENSITIVITY_ELEVATED", "UNFAMILIAR_DESTINATION_CHANGE"])
- forensic details
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


class InteractionPolicy:
    """Versioned policy defining rules and adaptive contextual scoring for financial interactions."""

    def __init__(
        self,
        policy_id: str = "POL-TVS-2026.2-ADAPTIVE",
        version: str = "3.2.0",
        name: str = "Adaptive Contextual Financial Interaction Policy",
        description: str = "Risk-proportional, policy-driven gating that adapts required verification to transaction context rather than relying on a fixed monetary cutoff.",
        required_bindings: Optional[List[str]] = None,
        max_ttl_seconds: int = 180,
        allowed_channels: Optional[List[str]] = None,
        strict_destination_check: bool = True,
        scoring: Optional[Dict[str, Any]] = None,
    ):
        self.policy_id = policy_id
        self.version = version
        self.name = name
        self.description = description
        self.required_bindings = required_bindings or [
            "loan_id", "customer_id", "purpose", "action",
            "amount", "destination", "channel", "nonce"
        ]
        self.max_ttl_seconds = max_ttl_seconds
        self.allowed_channels = allowed_channels or ["call", "whatsapp", "telegram", "sms", "in_app"]
        self.strict_destination_check = strict_destination_check
        self.scoring = scoring

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InteractionPolicy":
        v = data.get("policy_version") or data.get("version") or "3.2.0"
        return cls(
            policy_id=data.get("policy_id", "POL-TVS-2026.2-ADAPTIVE"),
            version=v,
            name=data.get("name", "Adaptive Contextual Financial Interaction Policy"),
            description=data.get("description", ""),
            required_bindings=data.get("required_bindings"),
            max_ttl_seconds=data.get("max_ttl_seconds", 180),
            allowed_channels=data.get("allowed_channels"),
            strict_destination_check=data.get("strict_destination_check", True),
            scoring=data.get("scoring"),
        )

    @classmethod
    def from_file(cls, filepath: str) -> "InteractionPolicy":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "policy_version": self.version,
            "name": self.name,
            "description": self.description,
            "required_bindings": self.required_bindings,
            "max_ttl_seconds": self.max_ttl_seconds,
            "allowed_channels": self.allowed_channels,
            "strict_destination_check": self.strict_destination_check,
            "scoring": self.scoring,
        }


def _load_default_policy() -> Optional[InteractionPolicy]:
    """Attempts to load policy from policy_config.json. Returns None if unparseable or missing (fail-closed)."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "policy_config.json")
    if os.path.exists(config_path):
        try:
            return InteractionPolicy.from_file(config_path)
        except Exception:
            return None
    return None


ACTIVE_POLICY: Optional[InteractionPolicy] = _load_default_policy()


def set_active_policy(policy: InteractionPolicy) -> None:
    """Updates the globally active policy at runtime without service restart."""
    global ACTIVE_POLICY
    ACTIVE_POLICY = policy


def reload_active_policy() -> InteractionPolicy:
    """Reloads the policy from policy_config.json."""
    global ACTIVE_POLICY
    ACTIVE_POLICY = _load_default_policy()
    return ACTIVE_POLICY


def get_active_policy() -> InteractionPolicy:
    """Returns the currently active policy instance."""
    return ACTIVE_POLICY


class PolicyEvaluationResult:
    """Encapsulates outcome of an Exact Action Gate evaluation under adaptive policy."""

    def __init__(
        self,
        allowed: bool,
        decision: str,
        reason_code: str,
        policy_version: str,
        assurance_level: str = "STANDARD",
        risk_signals: Optional[List[str]] = None,
        context_score: float = 0.0,
        details: Optional[Dict[str, Any]] = None,
        mismatch_field: Optional[str] = None,
    ):
        self.allowed = allowed
        self.decision = decision
        self.reason_code = reason_code
        self.policy_version = policy_version
        self.assurance_level = assurance_level
        self.risk_signals = risk_signals or []
        self.context_score = context_score
        self.details = details or {}
        self.mismatch_field = mismatch_field

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "policy_version": self.policy_version,
            "assurance_level": self.assurance_level,
            "risk_signals": self.risk_signals,
            "context_score": self.context_score,
            "mismatch_field": self.mismatch_field,
            "details": self.details,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


def evaluate_interaction_policy(
    signed_payload: Dict[str, Any],
    claimed_action: Dict[str, Any],
    policy: Optional[InteractionPolicy] = None,
    loan_context: Optional[Dict[str, Any]] = None,
    velocity_count: int = 1,
    is_destination_quarantined_fn=None,
    is_nonce_consumed_fn=None,
    is_revoked_fn=None,
) -> PolicyEvaluationResult:
    """
    Evaluates signed intent against claimed interaction under active versioned policy.
    Replaces static amount cutoffs with an adaptive, context-driven risk engine.

    Guarantees:
    1. FAILURE MUST NEVER BECOME AUTHORIZATION.
    2. Missing/corrupted policy configuration immediately FAILS CLOSED.
    3. Context (action, deviation from loan baseline, destination novelty, channel, velocity)
       determines whether standard or elevated step-up assurance is required.
    """
    pol = policy or ACTIVE_POLICY

    # Fail closed if policy is not available
    if not pol:
        return PolicyEvaluationResult(
            allowed=False,
            decision="BLOCKED",
            reason_code="POL_POLICY_UNAVAILABLE_FAIL_CLOSED",
            policy_version="UNKNOWN",
            assurance_level="CRITICAL",
            details={"error": "Policy service unavailable. Failing closed securely."}
        )

    # 1. Missing Required Cryptographic Bindings
    for binding in pol.required_bindings:
        if binding not in signed_payload:
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MISSING_BINDING",
                policy_version=pol.version,
                assurance_level="CRITICAL",
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
            assurance_level="CRITICAL",
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
                assurance_level="CRITICAL",
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
                    assurance_level="CRITICAL",
                    details={"expires_at": expires_at_str, "current_time": now.isoformat()}
                )
        except Exception:
            return PolicyEvaluationResult(
                allowed=False,
                decision="BLOCKED",
                reason_code="POL_MALFORMED_EXPIRY",
                policy_version=pol.version,
                assurance_level="CRITICAL",
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
            assurance_level="CRITICAL",
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
                assurance_level="CRITICAL",
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
                    assurance_level="CRITICAL",
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
                assurance_level="CRITICAL",
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
                assurance_level="CRITICAL",
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
                assurance_level="CRITICAL",
                mismatch_field="action",
                details={"claimed": claimed_action["action"], "authorized": signed_payload.get("action")}
            )

    # ---------------------------------------------------------------------------
    # 9. Adaptive Contextual Risk Evaluation (100% Policy-Driven, Zero Magic Numbers)
    # ---------------------------------------------------------------------------
    scoring = pol.scoring
    if not scoring:
        return PolicyEvaluationResult(
            allowed=False,
            decision="BLOCKED",
            reason_code="POL_POLICY_UNAVAILABLE_FAIL_CLOSED",
            policy_version=pol.version,
            assurance_level="CRITICAL",
            details={"error": "Policy scoring configuration is unavailable. Failing closed securely."}
        )

    action_cfg = scoring.get("action_sensitivity")
    channel_cfg = scoring.get("channel_risk")
    rel_cfg = scoring.get("relative_amount")
    dest_cfg = scoring.get("destination")
    vel_cfg = scoring.get("velocity")
    agent_cfg = scoring.get("agent")
    assurance_cfg = scoring.get("assurance_thresholds")

    if not all([action_cfg, channel_cfg, rel_cfg, dest_cfg, vel_cfg, agent_cfg, assurance_cfg]):
        return PolicyEvaluationResult(
            allowed=False,
            decision="BLOCKED",
            reason_code="POL_POLICY_CORRUPTED_FAIL_CLOSED",
            policy_version=pol.version,
            assurance_level="CRITICAL",
            details={"error": "Policy configuration missing mandatory scoring sections. Failing closed securely."}
        )

    context_score = 0.0
    risk_signals: List[str] = []

    # Signal 1: Action Sensitivity
    action_key = str(signed_payload.get("action") or claimed_action.get("action") or "").lower()
    purpose_key = str(signed_payload.get("purpose") or claimed_action.get("purpose") or "").lower()
    default_action_weight = action_cfg["default_action_weight"]
    elevated_action_threshold = action_cfg["elevated_signal_threshold"]
    action_weight = action_cfg.get(action_key, action_cfg.get(purpose_key, default_action_weight))
    context_score += action_weight
    if action_weight >= elevated_action_threshold:
        risk_signals.append("ACTION_SENSITIVITY_ELEVATED")

    # Signal 2: Channel Inward Trust State
    channel_key = str(signed_payload.get("channel") or claimed_action.get("channel") or "call").lower()
    default_channel_weight = channel_cfg["default_channel_weight"]
    untrusted_channel_threshold = channel_cfg["untrusted_signal_threshold"]
    channel_weight = channel_cfg.get(channel_key, default_channel_weight)
    context_score += channel_weight
    if channel_weight >= untrusted_channel_threshold:
        risk_signals.append("UNTRUSTED_INWARD_CHANNEL")

    # Signal 3: Relative Amount Deviation against Loan Baseline (Context-Driven, not absolute cutoff!)
    tx_amount = float(signed_payload.get("amount", 0.0))
    baseline_amount = 0.0
    if loan_context and "amount" in loan_context:
        baseline_amount = float(loan_context["amount"])
    elif loan_context and "baseline_amount" in loan_context:
        baseline_amount = float(loan_context["baseline_amount"])

    if baseline_amount > 0:
        multiplier = tx_amount / baseline_amount
        high_mult = rel_cfg["deviation_multiplier_high"]
        elev_mult = rel_cfg["deviation_multiplier_elevated"]
        if multiplier >= high_mult:
            context_score += rel_cfg["risk_penalty_high"]
            risk_signals.append("EXTREME_AMOUNT_DEVIATION_FROM_BASELINE")
        elif multiplier >= elev_mult:
            context_score += rel_cfg["risk_penalty_elevated"]
            risk_signals.append("AMOUNT_DEVIATION_FROM_BASELINE")

    # Signal 4: Destination Novelty / Change
    target_dest = str(signed_payload.get("destination") or "").strip().lower()
    if loan_context:
        known_dests = [str(d).strip().lower() for d in loan_context.get("known_destinations", [])]
        auth_dest = str(loan_context.get("authorized_destination", "")).strip().lower()
        if auth_dest and auth_dest not in known_dests:
            known_dests.append(auth_dest)

        if known_dests and target_dest not in known_dests:
            context_score += dest_cfg["unfamiliar_destination_penalty"]
            risk_signals.append("UNFAMILIAR_DESTINATION_CHANGE")

    # Signal 5: Velocity & Frequency
    vel_threshold = vel_cfg["elevated_count_threshold"]
    if velocity_count >= vel_threshold:
        context_score += vel_cfg["velocity_risk_penalty"]
        risk_signals.append("HIGH_INTERACTION_VELOCITY")

    # Signal 6: Agent Assignment
    agent_id = str(signed_payload.get("agent_id") or claimed_action.get("agent_id") or "")
    if not agent_id or agent_id.upper() in ("UNKNOWN", "UNASSIGNED"):
        context_score += agent_cfg["unassigned_agent_penalty"]
        risk_signals.append("UNASSIGNED_AGENT_DISPATCH")

    # Context Score Normalization & Boundary Gating
    context_score = min(1.0, round(context_score, 3))
    elevated_cutoff = assurance_cfg["elevated_risk_score"]
    critical_cutoff = assurance_cfg["critical_block_score"]

    if context_score >= critical_cutoff:
        return PolicyEvaluationResult(
            allowed=False,
            decision="BLOCKED",
            reason_code="POL_CRITICAL_CONTEXTUAL_RISK",
            policy_version=pol.version,
            assurance_level="CRITICAL",
            risk_signals=risk_signals,
            context_score=context_score,
            details={
                "error": "Contextual risk exceeded critical tolerance threshold.",
                "risk_signals": risk_signals,
                "assurance_level": "CRITICAL",
            }
        )

    # ---------------------------------------------------------------------------
    # 10. Gating Decision: STANDARD vs ELEVATED Assurance
    # ---------------------------------------------------------------------------
    device_confirmed = bool(claimed_action.get("device_confirmed", False))

    if context_score >= elevated_cutoff:
        assurance_level = "ELEVATED"
        if not device_confirmed:
            return PolicyEvaluationResult(
                allowed=False,
                decision="STEP_UP_REQUIRED",
                reason_code="POL_STEP_UP_REQUIRED",
                policy_version=pol.version,
                assurance_level="ELEVATED",
                risk_signals=risk_signals,
                context_score=context_score,
                details={
                    "message": "Additional verification required based on interaction context.",
                    "risk_signals": risk_signals,
                    "assurance_level": "ELEVATED",
                }
            )
        else:
            return PolicyEvaluationResult(
                allowed=True,
                decision="ALLOWED",
                reason_code="POL_AUTHORIZED_STEP_UP",
                policy_version=pol.version,
                assurance_level="ELEVATED",
                risk_signals=risk_signals,
                context_score=context_score,
                details={
                    "message": "Interaction authorized under elevated assurance following customer confirmation.",
                    "risk_signals": risk_signals,
                    "assurance_level": "ELEVATED",
                }
            )

    # Standard assurance: streamlined confirmation
    return PolicyEvaluationResult(
        allowed=True,
        decision="ALLOWED",
        reason_code="POL_AUTHORIZED",
        policy_version=pol.version,
        assurance_level="STANDARD",
        risk_signals=risk_signals,
        context_score=context_score,
        details={
            "loan_id": signed_payload.get("loan_id"),
            "customer_id": signed_payload.get("customer_id"),
            "amount": signed_payload.get("amount"),
            "destination": signed_payload.get("destination"),
            "assurance_level": "STANDARD",
            "message": "Interaction authorized by TVS Credit Exact Action Gate with standard assurance."
        }
    )
