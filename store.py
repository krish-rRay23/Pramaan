"""
Pramaan Backend — in-memory store

In-memory by design for the demo: Render's free tier can spin down
after inactivity, and a fresh, deterministic seed on every restart is
actually safer for a live demo than a database that might carry stale
state from a previous run. Swap this for a real database (Postgres on
Render, or wherever TVS's LMS actually lives) before this is anything
but a demo.
"""

import time
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Seeded "TVS LMS / CRM" account data — the one system of record
# ---------------------------------------------------------------------------

ACCOUNTS: dict[str, dict] = {
    "LOAN-4521": {
        "loan_id": "LOAN-4521",
        "customer_id": "CUST-001",
        "customer_name": "Demo Customer",
        "purpose": "emi_due",
        "amount": 3200.0,
        "due_date": "2026-09-05",
        "authorized_destination": "tvscredit.collections@upi",
    }
}

# customer_id -> most recently issued token (simulates "pending alert")
LATEST_INTENT_BY_CUSTOMER: dict[str, str] = {}

# nonce -> issued_at, so a token can only ever be verified for the account
# it was actually issued for (basic replay bookkeeping)
ISSUED_NONCES: set[str] = set()

ANOMALY_LOG: list[dict] = []

_rate_hits: dict[str, list[float]] = {}
RATE_LIMIT_MAX = 8
RATE_LIMIT_WINDOW_SECONDS = 60


def get_account(loan_id: str) -> Optional[dict]:
    return ACCOUNTS.get(loan_id.strip().upper())


def rate_limit_allow(key: str) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    hits = [t for t in _rate_hits.get(key, []) if t >= window_start]
    hits.append(now)
    _rate_hits[key] = hits
    return len(hits) <= RATE_LIMIT_MAX


def log_anomaly(loan_id: str, kind: str) -> None:
    ANOMALY_LOG.append({
        "at": datetime.now(timezone.utc).isoformat(),
        "loan_id": loan_id,
        "kind": kind,
    })
    # keep the log bounded for a long-running demo session
    if len(ANOMALY_LOG) > 200:
        del ANOMALY_LOG[:100]


def recent_anomalies(limit: int = 20) -> list[dict]:
    return ANOMALY_LOG[-limit:][::-1]
