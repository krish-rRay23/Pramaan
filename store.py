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
# 5. Verifiable Trust Receipts Log, Anomaly Log, Notification Logs & Telegram Chats
# ---------------------------------------------------------------------------

TRUST_RECEIPTS: List[Dict[str, Any]] = []
ANOMALY_LOG: List[Dict[str, Any]] = []
WHATSAPP_LOGS: List[Dict[str, Any]] = []
NOTIFICATION_LOGS: List[Dict[str, Any]] = []
FRAUD_INCIDENTS: List[Dict[str, Any]] = []

# Persistent customer chat mappings for Telegram bot: customer_id / loan_id -> telegram chat_id
CUSTOMER_TELEGRAM_CHATS: Dict[str, str] = {
    "CUST-001": "",
    "LOAN-4521": "",
}

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


def revoke_intents_by_destination(destination: str, reason: str = "Quarantined rogue destination") -> int:
    """Cascading mitigation: revokes any active capability intents that reference a quarantined destination."""
    if not destination:
        return 0
    count = 0
    dest = destination.strip().lower()
    for intent_id, record in list(INTENTS_BY_ID.items()):
        payload = record.get("payload", {})
        intent_dest = str(payload.get("destination") or "").strip().lower()
        if intent_dest == dest and record.get("status") == "ACTIVE":
            record["status"] = "REVOKED"
            REVOKED_INTENTS[intent_id] = reason
            token = record.get("token")
            if token:
                REVOKED_INTENTS[token] = reason
            count += 1
    return count


def record_destination_attempt(destination: str, loan_id: str) -> Optional[Dict[str, Any]]:
    """Heuristic Correlation Engine (Rule-based temporal & destination clustering; NOT ML/AI).
    Monitors incoming anomalous destination patterns across loans.
    """
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
        revoked_count = revoke_intents_by_destination(dest, reason=f"Quarantined under Campaign {campaign_id}")
        campaign = {
            "campaign_id": campaign_id,
            "pattern": f"Coordinated destination redirect targeting multiple loans ({len(timestamps)} attempts in 3m)",
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "target_count": len(timestamps),
            "rogue_destination": dest,
            "status": "CONTAINED",
            "mitigation_action": f"Destination quarantined across portfolio; {revoked_count} active intent(s) auto-revoked",
        }
        CAMPAIGNS.append(campaign)
        log_anomaly(
            loan_id=loan_id,
            kind="SWARM_ATTACK_CONTAINED",
            severity="CRITICAL",
            details=f"Campaign {campaign_id}: Quarantined {dest}, revoked {revoked_count} intent(s)",
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


def add_whatsapp_log(log_entry: Dict[str, Any]) -> None:
    WHATSAPP_LOGS.append(log_entry)
    add_notification_log(log_entry)
    if len(WHATSAPP_LOGS) > 200:
        del WHATSAPP_LOGS[:50]


def get_whatsapp_logs(limit: int = 50) -> List[Dict[str, Any]]:
    return WHATSAPP_LOGS[-limit:][::-1]


def add_notification_log(log_entry: Dict[str, Any]) -> None:
    NOTIFICATION_LOGS.append(log_entry)
    if len(NOTIFICATION_LOGS) > 300:
        del NOTIFICATION_LOGS[:80]


def get_notification_logs(channel: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    logs = NOTIFICATION_LOGS
    if channel:
        c_low = channel.lower().strip()
        logs = [l for l in logs if l.get("channel", "").lower() == c_low]
    return logs[-limit:][::-1]


def register_customer_telegram(customer_or_loan_id: str, chat_id: str) -> None:
    key = customer_or_loan_id.strip().upper()
    CUSTOMER_TELEGRAM_CHATS[key] = str(chat_id).strip()


def get_customer_telegram(customer_or_loan_id: str) -> Optional[str]:
    key = customer_or_loan_id.strip().upper()
    val = CUSTOMER_TELEGRAM_CHATS.get(key)
    if val:
        return val
    # Check if loan_id corresponds to customer_id
    acc = get_account(key)
    if acc:
        c_id = acc.get("customer_id", "").upper()
        if c_id in CUSTOMER_TELEGRAM_CHATS and CUSTOMER_TELEGRAM_CHATS[c_id]:
            return CUSTOMER_TELEGRAM_CHATS[c_id]
    return None


def add_fraud_incident(incident: Dict[str, Any]) -> None:
    FRAUD_INCIDENTS.append(incident)
    if len(FRAUD_INCIDENTS) > 200:
        del FRAUD_INCIDENTS[:50]


def get_fraud_incidents(limit: int = 50) -> List[Dict[str, Any]]:
    return FRAUD_INCIDENTS[-limit:][::-1]


def trigger_kill_switch(
    customer_id: str,
    loan_id: str,
    intent_id: Optional[str] = None,
    token: Optional[str] = None,
    reported_destination: Optional[str] = None,
    reason: str = "Customer marked: I DON'T TRUST THIS REQUEST"
) -> Dict[str, Any]:
    """Executes customer kill switch:
    1. Revokes intent immediately
    2. Flags & quarantines suspicious destination
    3. Cascades revocation across any active intents referencing the destination
    4. Records critical fraud incident
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    incident_id = f"INC-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"

    # 1. Revoke active intent
    if intent_id:
        revoke_intent(intent_id, reason=f"Kill-switch triggered: {reason}")
    if token:
        revoke_intent(token, reason=f"Kill-switch triggered: {reason}")

    # 2. Extract or quarantine reported destination
    dest_to_quarantine = reported_destination
    if not dest_to_quarantine and intent_id and intent_id in INTENTS_BY_ID:
        dest_to_quarantine = INTENTS_BY_ID[intent_id].get("payload", {}).get("destination")

    revoked_cascade_count = 0
    if dest_to_quarantine:
        dest_clean = dest_to_quarantine.strip().lower()
        QUARANTINED_DESTINATIONS.add(dest_clean)
        revoked_cascade_count = revoke_intents_by_destination(
            dest_clean,
            reason=f"Auto-revoked under customer incident {incident_id}"
        )

    # 3. Record fraud incident
    incident = {
        "incident_id": incident_id,
        "customer_id": customer_id,
        "loan_id": loan_id,
        "intent_id": intent_id or "N/A",
        "flagged_destination": dest_to_quarantine or "UNSPECIFIED",
        "reported_reason": reason,
        "timestamp": now_iso,
        "severity": "CRITICAL",
        "status": "CONTAINED",
        "action_taken": f"Authorization revoked. Destination {dest_to_quarantine or 'N/A'} quarantined. {revoked_cascade_count} active intent(s) cascade-revoked.",
    }
    add_fraud_incident(incident)

    log_anomaly(
        loan_id=loan_id,
        kind="CUSTOMER_KILL_SWITCH_ACTIVATED",
        severity="CRITICAL",
        details=f"Incident {incident_id}: Customer rejected interaction. Destination {dest_to_quarantine} quarantined.",
    )

    return incident
