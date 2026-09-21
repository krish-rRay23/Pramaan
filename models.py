"""
Pramaan 2.0 Backend — Pydantic models
===================================
API contract between TVS Backend, Operations Console, and Android App.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Account(BaseModel):
    loan_id: str
    customer_id: str
    customer_name: str
    product_name: str = "TVS Two-Wheeler Loan"
    purpose: str = "emi_due"
    amount: float
    due_date: str
    authorized_destination: str   # Authorized UPI VPA for TVS Credit collection


class Partner(BaseModel):
    partner_id: str
    partner_name: str
    partner_type: str            # "DIRECT_TVS" | "LSP_PARTNER" | "RECOVERY_AGENCY"
    status: str                  # "AUTHORIZED" | "SUSPENDED" | "REVOKED"


class Agent(BaseModel):
    agent_id: str
    partner_id: str
    agent_name: str
    phone: str
    status: str                  # "AUTHORIZED" | "SUSPENDED" | "REVOKED"
    allowed_actions: List[str]   # e.g. ["collect_payment", "inform"]


class IntentPayload(BaseModel):
    """The cryptographically signed capability intent.
    Bound to customer, loan, action, amount, destination, partner, and agent.
    """
    intent_id: str
    customer_id: str
    loan_id: str
    purpose: str
    amount: float
    action: str                  # "inform" | "collect_payment" | "confirm_kyc" | "update_bank_details"
    destination: Optional[str] = None
    channel: str = "call"        # "call" | "sms" | "whatsapp" | "in_app"
    partner_id: str = "PARTNER-TVS-01"
    partner_name: str = "TVS Credit Direct"
    agent_id: str = "AGT-7701"
    agent_name: str = "Suresh Menon"
    issued_at: str
    expires_at: str
    nonce: str
    audience: str = "tvs_customer_app"
    session_id: Optional[str] = None


class SignedIntent(BaseModel):
    token: str
    payload: IntentPayload
    expires_in_seconds: int
    status: str = "ACTIVE"       # "ACTIVE" | "REVOKED" | "EXPIRED" | "CONSUMED"
    deep_link: Optional[str] = None


class IssueIntentRequest(BaseModel):
    loan_id: str
    purpose: str = "emi_due"
    action: str = "collect_payment"
    channel: str = "whatsapp"    # "call" | "sms" | "whatsapp" | "agent"
    partner_id: Optional[str] = "PARTNER-TVS-01"
    agent_id: Optional[str] = "AGT-7701"
    customer_phone: Optional[str] = None
    send_whatsapp: bool = False
    callmebot_api_key: Optional[str] = None


class NotificationDispatchRequest(BaseModel):
    channel: str = "telegram"     # "telegram" | "whatsapp" | "mock"
    token: Optional[str] = None
    intent_id: Optional[str] = None
    loan_id: Optional[str] = None
    customer_id: Optional[str] = "CUST-001"
    # Telegram specific
    telegram_chat_id: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    # WhatsApp specific
    recipient_phone: Optional[str] = None
    callmebot_api_key: Optional[str] = None
    force_mock: bool = False


class TelegramRegisterRequest(BaseModel):
    customer_id: str = "CUST-001"
    loan_id: Optional[str] = "LOAN-4521"
    chat_id: str


class TelegramBotInfoResponse(BaseModel):
    bot_username: str
    bot_name: str
    connect_url: str
    is_configured: bool
    registered_chat_id: Optional[str] = None


class WhatsAppDispatchRequest(BaseModel):
    token: Optional[str] = None
    intent_id: Optional[str] = None
    loan_id: Optional[str] = None
    recipient_phone: Optional[str] = None
    callmebot_api_key: Optional[str] = None
    force_mock: bool = False


class WhatsAppLogEntry(BaseModel):
    log_id: str
    provider: str
    target_phone: str
    loan_id: str
    status: str                  # "DELIVERED" | "FAILED" | "SIMULATED"
    dispatched_at: str
    message_preview: str
    deep_link: str
    details: Optional[str] = None


class NotificationLogEntry(BaseModel):
    log_id: str
    channel: str                 # "telegram" | "whatsapp" | "mock"
    provider: str
    target: str
    loan_id: str
    status: str                  # "DELIVERED" | "FAILED" | "SIMULATED" | "NO_CHAT_ID"
    dispatched_at: str
    message_preview: str
    deep_link: str
    web_verify_url: Optional[str] = None
    details: Optional[str] = None


class CustomerKillSwitchRequest(BaseModel):
    loan_id: str
    customer_id: Optional[str] = "CUST-001"
    intent_id: Optional[str] = None
    token: Optional[str] = None
    reported_destination: Optional[str] = None
    reason: str = "Customer marked: I DON'T TRUST THIS REQUEST"


class CustomerKillSwitchResponse(BaseModel):
    success: bool
    incident_id: str
    status: str
    message: str
    trust_receipt: Optional[TrustReceipt] = None


class ClaimedRequest(BaseModel):
    """What the caller or message claims during the interaction."""
    loan_id: str
    purpose: str = "emi_due"
    amount: float
    action: str = "collect_payment"
    destination: Optional[str] = None
    agent_id: Optional[str] = None


class TrustReceipt(BaseModel):
    """Cryptographically verifiable proof of interaction evaluation."""
    receipt_id: str
    interaction_id: str
    customer_id: str
    loan_id: str
    purpose: str
    action: str
    amount: float
    destination: Optional[str]
    channel: str
    partner_name: str
    agent_name: str
    agent_id: str
    decision: str                # "ALLOWED" | "BLOCKED" | "UNVERIFIED" | "QUARANTINED"
    decision_reason: str
    timestamp: str
    authorization_ref: str
    signature: str


class VerifyRequest(BaseModel):
    token: str
    claimed: ClaimedRequest


class VerifyResponse(BaseModel):
    matched: bool
    decision: str                # "ALLOWED" | "BLOCKED" | "UNVERIFIED" | "QUARANTINED"
    reason: str
    signature_valid: bool
    fresh: bool
    agent_authorized: bool = True
    destination_verified: bool = True
    on_record: Optional[IntentPayload] = None
    trust_receipt: Optional[TrustReceipt] = None


class RevokeRequest(BaseModel):
    intent_id: Optional[str] = None
    token: Optional[str] = None
    reason: str = "Suspicious behavior reported"



class Campaign(BaseModel):
    campaign_id: str
    pattern: str
    detected_at: str
    target_count: int
    rogue_destination: Optional[str] = None
    status: str                  # "ACTIVE" | "CONTAINED" | "QUARANTINED"
    mitigation_action: str


class AuthenticityResponse(BaseModel):
    risk_score: float
    verdict: str                 # "authentic" | "needs_review" | "flagged"
    note: str
    model_version: str = "DeepWatch-v2-Prototype"


class AnomalyEntry(BaseModel):
    at: str
    loan_id: str
    kind: str
    severity: str = "WARNING"    # "INFO" | "WARNING" | "CRITICAL"
    details: Optional[str] = None


class AttackSimulationResult(BaseModel):
    scenario: str
    title: str
    description: str
    expected_decision: str
    actual_decision: str
    passed: bool
    details: Dict[str, Any]
    receipt: Optional[TrustReceipt] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    loan_id: Optional[str] = None
    amount: Optional[float] = None
    action: Optional[str] = None
    destination_claimed: Optional[str] = None
    destination_authoritative: Optional[str] = None
    agent_id: Optional[str] = None
    campaign_id: Optional[str] = None
    exact_reason: Optional[str] = None
