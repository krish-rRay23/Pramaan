# PRAMAAN v3.1 — Demo Reset & State Sanitization Guide

## Overview
This runbook provides the exact steps to reset the entire Pramaan system (backend in-memory state, quarantined VPAs, consumed nonces, test incidents, and mobile cached states) back to pristine baseline prior to a live demonstration rehearsal.

---

## 1. Quick One-Line Backend Reset
If running the backend locally:
```powershell
# Stop existing server (Ctrl+C in terminal)
# Start fresh instance (clears all in-memory nonces, anomalies, and active sessions):
uvicorn main:app --reload --port 8000
```

---

## 2. API-Driven Clean State Reset
Alternatively, execute the reset via Python or cURL without restarting the server:

```python
import store
from repository import get_repository

# 1. Clear consumed nonces to permit replay demos
store.CONSUMED_NONCES.clear()
get_repository().consumed_nonces.clear()

# 2. Reset rate limits
store._rate_hits.clear()

# 3. Reset quarantined destinations to baseline (preserving known fraudsters)
store.QUARANTINED_DESTINATIONS = {
    "known.fraudster@upi",
    "scam.collector@oksbi",
}
get_repository().quarantined_destinations = set(store.QUARANTINED_DESTINATIONS)

# 4. Clear incidents and receipts
store.INCIDENTS.clear()
store.TRUST_RECEIPTS.clear()
store.ANOMALY_LOG.clear()
get_repository().receipts.clear()
get_repository().receipts_by_intent.clear()
get_repository().incidents.clear()

# 5. Reset active campaigns
store.ACTIVE_CAMPAIGNS.clear()

print("[PRAMAAN] State successfully reset to pristine demo baseline.")
```

Save and run directly:
```bash
python demo/reset_demo.py
```

---

## 3. Telegram Pairing Re-registration
To pair the Telegram test customer chat cleanly:
1. Open the **Operations Console**: `http://localhost:8000/console.html`
2. In the Telegram Status card, copy the fresh **One-Time Pairing Link**:  
   `https://t.me/pramaan_demo_bot?start=PAIR_<token>`
3. Send `/start` in Telegram.
4. Verify the bot replies with:
   `🔒 TVS Credit PRAMAAN Security Active`
5. The chat ID is now bound for all live dispatch demonstrations.

---

## 4. Mobile App Reset
1. On the Android device or emulator, swipe away the app from the recent apps switcher to clear in-flight view model state.
2. Re-launch the app: verify **Protection Active** badge is displayed.
