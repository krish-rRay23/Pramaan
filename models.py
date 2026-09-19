"""
Pramaan Backend — Pydantic models
===================================
These are the exact request/response shapes the Android app must match.
Treat this file as the API contract between backend and app.
"""

from pydantic import BaseModel
from typing import Optional


class Account(BaseModel):
    loan_id: str
    customer_id: str
    customer_name: str
    purpose: str            # "emi_due" | "kyc_reverification" | "service_request"
    amount: float
    due_date: str
    authorized_destination: str   # e.g. a UPI VPA — the ONLY destination this loan is allowed to pay to


class IntentPayload(BaseModel):
    """The signed payload. Every field here is what a genuine TVS-initiated
    contact is authorized to say. This is generated FROM the account record —
    never from arbitrary caller input — so the 'truth' always traces back to
    the account system of record."""
    customer_id: str
    loan_id: str
    purpose: str
    amount: float
    action: str              # "inform" | "collect_payment" | "confirm_kyc"
    destination: Optional[str]
    channel: str              # "call" | "sms" | "whatsapp"
    issued_at: str
    expires_at: str
    nonce: str


class SignedIntent(BaseModel):
    token: str                # base64(payload_json) + "." + hmac_signature_hex
    payload: IntentPayload
    expires_in_seconds: int


class IssueIntentRequest(BaseModel):
    loan_id: str
    purpose: str
    action: str = "inform"
    channel: str = "call"


class ClaimedRequest(BaseModel):
    """What the caller/message ACTUALLY says during the interaction —
    entered by the customer (or, in the demo, typed in by the presenter
    to play either the genuine caller or the fraudster)."""
    loan_id: str
    purpose: str
    amount: float
    action: str
    destination: Optional[str] = None


class VerifyRequest(BaseModel):
    token: str
    claimed: ClaimedRequest


class VerifyResponse(BaseModel):
    matched: bool
    reason: str
    signature_valid: bool
    fresh: bool
    on_record: Optional[IntentPayload] = None


class AuthenticityResponse(BaseModel):
    risk_score: float
    verdict: str             # "authentic" | "needs_review" | "flagged"
    note: str


class AnomalyEntry(BaseModel):
    at: str
    loan_id: str
    kind: str
