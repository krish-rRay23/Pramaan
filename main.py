"""
Pramaan Backend — main FastAPI application

Run locally:
    uvicorn main:app --reload --port 8000

Deploy: see README.md for Render instructions.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import store
from crypto_utils import sign_payload, verify_token
from kyc_authenticity import score_image
from models import (
    Account, IssueIntentRequest, SignedIntent, IntentPayload,
    VerifyRequest, VerifyResponse, AuthenticityResponse, AnomalyEntry,
)

INTENT_VALIDITY_SECONDS = 120  # matches the "Fresh • 02:00 remaining" UI copy

app = FastAPI(title="Pramaan Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # fine for a demo; restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    """Health check — hit this a couple of minutes before your live demo
    to wake a sleeping Render free-tier instance."""
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/account/{loan_id}", response_model=Account)
def get_account(loan_id: str):
    account = store.get_account(loan_id)
    if not account:
        raise HTTPException(404, "No such loan on record")
    return account


@app.post("/intent/issue", response_model=SignedIntent)
def issue_intent(req: IssueIntentRequest):
    """Simulates TVS's LMS/CRM initiating a real, authorized contact.
    Every field in the signed payload is pulled from the account record —
    this endpoint does not accept an arbitrary amount or destination from
    the caller, by design."""
    account = store.get_account(req.loan_id)
    if not account:
        raise HTTPException(404, "No such loan on record")

    now = datetime.now(timezone.utc)
    payload = {
        "customer_id": account["customer_id"],
        "loan_id": account["loan_id"],
        "purpose": req.purpose,
        "amount": account["amount"],
        "action": req.action,
        "destination": account["authorized_destination"] if req.action == "collect_payment" else None,
        "channel": req.channel,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=INTENT_VALIDITY_SECONDS)).isoformat(),
        "nonce": str(uuid.uuid4()),
    }
    token = sign_payload(payload)
    store.ISSUED_NONCES.add(payload["nonce"])
    store.LATEST_INTENT_BY_CUSTOMER[account["customer_id"]] = token

    return SignedIntent(token=token, payload=IntentPayload(**payload), expires_in_seconds=INTENT_VALIDITY_SECONDS)


@app.get("/intent/latest/{customer_id}", response_model=SignedIntent)
def latest_intent(customer_id: str):
    """The Android app polls this to simulate a proactive alert: 'TVS Credit
    will contact you now.' Returns 404 once nothing fresh is pending."""
    token = store.LATEST_INTENT_BY_CUSTOMER.get(customer_id)
    if not token:
        raise HTTPException(404, "No pending contact for this customer")

    valid, payload = verify_token(token)
    if not valid:
        raise HTTPException(500, "Stored intent failed signature check")

    expires_at = datetime.fromisoformat(payload["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(404, "No pending contact for this customer")

    remaining = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    return SignedIntent(token=token, payload=IntentPayload(**payload), expires_in_seconds=max(remaining, 0))


@app.post("/intent/verify", response_model=VerifyResponse)
def verify_intent(req: VerifyRequest):
    """The core mechanism. Checks the token's signature and freshness,
    then compares what the caller CLAIMED against what was actually
    signed — not against the account record directly, so a stale but
    validly-signed token for a different purpose still gets caught."""

    if not store.rate_limit_allow(req.claimed.loan_id):
        store.log_anomaly(req.claimed.loan_id, "rate_limited")
        return VerifyResponse(matched=False, reason="rate_limited", signature_valid=False, fresh=False)

    signature_valid, payload = verify_token(req.token)
    if not signature_valid:
        store.log_anomaly(req.claimed.loan_id, "invalid_signature")
        return VerifyResponse(matched=False, reason="invalid_signature", signature_valid=False, fresh=False)

    expires_at = datetime.fromisoformat(payload["expires_at"])
    fresh = datetime.now(timezone.utc) <= expires_at
    if not fresh:
        store.log_anomaly(req.claimed.loan_id, "expired_token")
        return VerifyResponse(matched=False, reason="expired", signature_valid=True, fresh=False,
                               on_record=IntentPayload(**payload))

    mismatches = []
    if req.claimed.loan_id != payload["loan_id"]:
        mismatches.append("loan_id")
    if req.claimed.purpose != payload["purpose"]:
        mismatches.append("purpose")
    if abs(req.claimed.amount - payload["amount"]) > 0.01:
        mismatches.append("amount")
    if req.claimed.action != payload["action"]:
        mismatches.append("action")
    if payload.get("destination") and req.claimed.destination != payload["destination"]:
        mismatches.append("destination")

    if mismatches:
        store.log_anomaly(req.claimed.loan_id, f"mismatch:{','.join(mismatches)}")
        return VerifyResponse(
            matched=False, reason=f"mismatch on: {', '.join(mismatches)}",
            signature_valid=True, fresh=True, on_record=IntentPayload(**payload),
        )

    return VerifyResponse(matched=True, reason="matches signed intent", signature_valid=True,
                           fresh=True, on_record=IntentPayload(**payload))


@app.post("/kyc/authenticity", response_model=AuthenticityResponse)
async def kyc_authenticity(file: UploadFile = File(...)):
    image_bytes = await file.read()
    risk_score, verdict, note = score_image(image_bytes)
    return AuthenticityResponse(risk_score=risk_score, verdict=verdict, note=note)


@app.get("/admin/anomalies", response_model=list[AnomalyEntry])
def admin_anomalies():
    return store.recent_anomalies()
