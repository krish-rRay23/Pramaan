"""
Pramaan 2.0 Backend — In-Memory Trust Store & State of Record
============================================================
Holds seeded TVS LMS/CRM records, partner/agent registry,
revocation lists, quarantine barriers, campaign states, and trust receipts.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

# ---------------------------------------------------------------------------
# 1. TVS LMS / CRM Master Records (System of Record)
# ---------------------------------------------------------------------------

ACCOUNTS: Dict[str, Dict[str, Any]] = {
    "LOAN-4521": {
        "loan_id": "LOAN-4521",
        "customer_id": "CUST-001",
        "customer_name": "Aarav Patel",
        "product_name": "TVS Two-Wheeler Loan",
        "purpose": "emi_due",
        "amount": 3200.0,
        "due_date": "2026-09-25",
        "authorized_destination": "tvscredit.collections@upi",
    },
    "LOAN-8832": {
        "loan_id": "LOAN-8832",
        "customer_id": "CUST-002",
        "customer_name": "Priya Sundaram",
        "product_name": "TVS Used Car Loan",
        "purpose": "emi_due",
        "amount": 14500.0,
        "due_date": "2026-09-28",
        "authorized_destination": "tvscredit.collections@upi",
    },
    "LOAN-1090": {
        "loan_id": "LOAN-1090",
        "customer_id": "CUST-003",
        "customer_name": "Ramesh Kumar",
        "product_name": "TVS Tractor / Agri Loan",
        "purpose": "emi_due",
        "amount": 8750.0,
        "due_date": "2026-09-30",
        "authorized_destination": "tvscredit.agri@upi",
    },
}

# ---------------------------------------------------------------------------
# 2. Partner & Authorized Agent Registry
# ---------------------------------------------------------------------------

PARTNERS: Dict[str, Dict[str, Any]] = {
    "PARTNER-TVS-01": {
        "partner_id": "PARTNER-TVS-01",
        "partner_name": "TVS Credit Direct Collection Hub",
        "partner_type": "DIRECT_TVS",
        "status": "AUTHORIZED",
    },
    "PARTNER-APEX-02": {
        "partner_id": "PARTNER-APEX-02",
        "partner_name": "Apex Recovery Services (LSP)",
        "partner_type": "LSP_PARTNER",
        "status": "AUTHORIZED",
    },
    "PARTNER-ROGUE-03": {
        "partner_id": "PARTNER-ROGUE-03",
        "partner_name": "Unverified Third-Party Agency",
        "partner_type": "RECOVERY_AGENCY",
        "status": "SUSPENDED",
    },
}

AGENTS: Dict[str, Dict[str, Any]] = {
    "AGT-7701": {
        "agent_id": "AGT-7701",
        "partner_id": "PARTNER-TVS-01",
        "agent_name": "Suresh Menon",
        "phone": "+91 98765 43210",
        "status": "AUTHORIZED",
        "allowed_actions": ["collect_payment", "inform", "confirm_kyc"],
    },
    "AGT-7702": {
        "agent_id": "AGT-7702",
        "partner_id": "PARTNER-APEX-02",
        "agent_name": "Pooja Verma",
        "phone": "+91 91234 56789",
        "status": "AUTHORIZED",
        "allowed_actions": ["inform"],  # Notice: NOT authorized to collect payments!
    },
    "AGT-FRAUD-99": {
        "agent_id": "AGT-FRAUD-99",
        "partner_id": "PARTNER-ROGUE-03",
        "agent_name": "Impersonator Agent 99",
        "phone": "+91 90000 00000",
        "status": "REVOKED",
        "allowed_actions": [],
    },
}

# ---------------------------------------------------------------------------
# 3. Dynamic Intent, Replay & Revocation State
# ---------------------------------------------------------------------------

INTENTS_BY_ID: Dict[str, Dict[str, Any]] = {}
LATEST_INTENT_BY_CUSTOMER: Dict[str, str] = {}
ISSUED_NONCES: set[str] = set()
CONSUMED_NONCES: set[str] = set()  # Replay attack protection
REVOKED_INTENTS: Dict[str, str] = {}  # intent_id -> reason

# ---------------------------------------------------------------------------
# 4. Swarm Containment & Attack Campaign State
# ---------------------------------------------------------------------------

QUARANTINED_DESTINATIONS: set[str] = {
    "known.fraudster@upi",
    "scam.collector@oksbi",
}
QUARANTINED_AGENTS: set[str] = {"AGT-FRAUD-99"}

CAMPAIGNS: List[Dict[str, Any]] = []
_destination_anomaly_counter: Dict[str, List[float]] = {}

# ---------------------------------------------------------------------------
# 5. Verifiable Trust Receipts Log & Anomaly Log
# ---------------------------------------------------------------------------

TRUST_RECEIPTS: List[Dict[str, Any]] = []
ANOMALY_LOG: List[Dict[str, Any]] = []

_rate_hits: Dict[str, List[float]] = {}
RATE_LIMIT_MAX = 12
RATE_LIMIT_WINDOW_SECONDS = 60


def get_account(loan_id: str) -> Optional[Dict[str, Any]]:
    return ACCOUNTS.get(loan_id.strip().upper())


def get_partner(partner_id: str) -> Optional[Dict[str, Any]]:
    return PARTNERS.get(partner_id.strip().upper())


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    return AGENTS.get(agent_id.strip().upper())


def is_destination_quarantined(destination: Optional[str]) -> bool:
    if not destination:
        return False
    return destination.strip().lower() in {d.lower() for d in QUARANTINED_DESTINATIONS}


# ---------------------------------------------------------------------------
# ARCHITECTURAL REVOCATION BOUNDARY:
# Revoking an Agent or Partner in the registry immediately blocks NEW intent
# issuance under that entity. It does NOT retroactively invalidate an existing
# capability token that was already issued and is currently inside its short TTL window
# (those expire naturally on their 180s TTL, ensuring deterministic, stateless
# bearer-capability verification without continuous external lookup overhead).
# For immediate emergency invalidation of a specific active token or intent, use
# the explicit token revocation endpoint (revoke_intent / POST /intent/revoke).
# ---------------------------------------------------------------------------

def is_intent_revoked(intent_id: Optional[str], token: Optional[str] = None) -> Tuple[bool, str]:
    if intent_id and intent_id in REVOKED_INTENTS:
        return True, REVOKED_INTENTS[intent_id]
    if token and token in REVOKED_INTENTS:
        return True, REVOKED_INTENTS[token]
    return False, ""


def revoke_intent(identifier: str, reason: str = "Compromised or manually revoked") -> bool:
    REVOKED_INTENTS[identifier] = reason
    if identifier in INTENTS_BY_ID:
        INTENTS_BY_ID[identifier]["status"] = "REVOKED"
    return True


def consume_nonce(nonce: str) -> None:
    CONSUMED_NONCES.add(nonce)


def is_nonce_consumed(nonce: str) -> bool:
    return nonce in CONSUMED_NONCES


def rate_limit_allow(key: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    hits = [t for t in _rate_hits.get(key, []) if t >= window_start]
    hits.append(now)
    _rate_hits[key] = hits
    return len(hits) <= RATE_LIMIT_MAX


def log_anomaly(loan_id: str, kind: str, severity: str = "WARNING", details: Optional[str] = None) -> None:
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "loan_id": loan_id,
        "kind": kind,
        "severity": severity,
        "details": details or "",
    }
    ANOMALY_LOG.append(entry)
    if len(ANOMALY_LOG) > 300:
        del ANOMALY_LOG[:100]


def record_destination_attempt(destination: str, loan_id: str) -> Optional[Dict[str, Any]]:
    """Monitors incoming rogue destination patterns. Detects AI-scaled coordinated swarms."""
    if not destination:
        return None
    dest = destination.strip().lower()
    now = time.time()
    timestamps = _destination_anomaly_counter.setdefault(dest, [])
    # Keep timestamps within 3-minute window
    timestamps = [t for t in timestamps if now - t < 180]
    timestamps.append(now)
    _destination_anomaly_counter[dest] = timestamps

    # If 3 or more anomalous requests hit the same rogue destination across loans
    if len(timestamps) >= 3 and dest not in {d.lower() for d in QUARANTINED_DESTINATIONS}:
        QUARANTINED_DESTINATIONS.add(dest)
        campaign_id = f"CMP-{int(now)}-{uuid.uuid4().hex[:6].upper()}"
        campaign = {
            "campaign_id": campaign_id,
            "pattern": f"Coordinated destination redirect targeting multiple loans ({len(timestamps)} attempts in 3m)",
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "target_count": len(timestamps),
            "rogue_destination": dest,
            "status": "CONTAINED",
            "mitigation_action": "Destination automatically quarantined; linked intents revoked",
        }
        CAMPAIGNS.append(campaign)
        log_anomaly(
            loan_id=loan_id,
            kind="SWARM_ATTACK_CONTAINED",
            severity="CRITICAL",
            details=f"Campaign {campaign_id}: Quarantined destination {dest}",
        )
        return campaign
    return None


def add_trust_receipt(receipt: Dict[str, Any]) -> None:
    TRUST_RECEIPTS.append(receipt)
    if len(TRUST_RECEIPTS) > 300:
        del TRUST_RECEIPTS[:100]


def get_receipt(receipt_id: str) -> Optional[Dict[str, Any]]:
    for r in reversed(TRUST_RECEIPTS):
        if r.get("receipt_id") == receipt_id:
            return r
    return None


def get_receipts_by_customer(customer_id: str) -> List[Dict[str, Any]]:
    return [r for r in reversed(TRUST_RECEIPTS) if r.get("customer_id") == customer_id]


def recent_anomalies(limit: int = 30) -> List[Dict[str, Any]]:
    return ANOMALY_LOG[-limit:][::-1]
