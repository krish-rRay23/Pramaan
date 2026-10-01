"""
Pramaan v3.1 — Demo State Reset Script
======================================
Resets in-memory state, nonces, rate limits, incidents, and receipts
back to initial pristine demo baseline.
"""

import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import store
from repository import get_repository

def reset_state():
    repo = get_repository()

    # 1. Consumed nonces
    store.CONSUMED_NONCES.clear()
    repo.consumed_nonces.clear()

    # 2. Rate limits
    store._rate_hits.clear()

    # 3. Quarantined destinations
    baseline_q = {"known.fraudster@upi", "scam.collector@oksbi"}
    store.QUARANTINED_DESTINATIONS = set(baseline_q)
    repo.quarantined_destinations = set(baseline_q)

    # 4. Clear incidents and receipts
    store.INCIDENTS.clear()
    store.TRUST_RECEIPTS.clear()
    store.ANOMALY_LOG.clear()
    repo.receipts.clear()
    repo.receipts_by_intent.clear()
    repo.incidents.clear()

    # 5. Reset active campaigns
    store.ACTIVE_CAMPAIGNS.clear()

    print("[PRAMAAN] State successfully reset to pristine demo baseline.")

if __name__ == "__main__":
    reset_state()
