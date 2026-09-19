# Pramaan Backend

FastAPI service implementing the two-lane trust engine: the Contact
Intent Protocol (sign + verify) and a placeholder KYC-authenticity
endpoint. All account data is seeded in-memory — no database needed
for the demo.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI — useful
for testing without the Android app while it's being built.

## Deploy to Render

1. Push this folder to its own GitHub repo (or a subfolder of your
   monorepo — set Render's "Root Directory" accordingly).
2. On Render: **New > Blueprint**, point it at the repo. `render.yaml`
   configures everything automatically (build command, start command,
   and a random `PRAMAAN_SECRET_KEY`).
   - If you'd rather set it up manually: **New > Web Service**, Python
     environment, build command `pip install -r requirements.txt`,
     start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
3. Once deployed, note the URL Render gives you, e.g.
   `https://pramaan-backend.onrender.com`. That's `BASE_URL` for the
   Android app (see the Android README).

## Before you demo live

Render's free tier spins down after ~15 minutes of inactivity. A cold
start can take 30–60 seconds — dead air you don't want in front of a
jury.

- Hit `GET /ping` a few minutes before your slot to wake it up.
- All account data is seeded fresh on every restart (`store.py`), so a
  cold restart mid-demo-day is not a data-loss risk — the same
  `LOAN-4521` account will always be there.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/ping` | Health check / wake-up |
| GET | `/account/{loan_id}` | Read the account "system of record" |
| POST | `/intent/issue` | Simulates TVS initiating real contact — issues a signed token |
| GET | `/intent/latest/{customer_id}` | App polls this for a pending "proactive alert" |
| POST | `/intent/verify` | Core check: signature + freshness + does the claim match what was signed |
| POST | `/kyc/authenticity` | Multipart image upload → risk score (placeholder heuristic — see `kyc_authenticity.py`) |
| GET | `/admin/anomalies` | Recent mismatch/rate-limit events, for the audit-trail talking point |

## Running the demo script by hand (no app needed to test)

```bash
# 1. Issue a genuine intent
curl -X POST $BASE_URL/intent/issue -H "Content-Type: application/json" \
  -d '{"loan_id":"LOAN-4521","purpose":"emi_due","action":"collect_payment","channel":"call"}'

# 2. Take the "token" from the response, then verify a GENUINE claim
curl -X POST $BASE_URL/intent/verify -H "Content-Type: application/json" \
  -d '{"token":"<paste>","claimed":{"loan_id":"LOAN-4521","purpose":"emi_due","amount":3200.0,"action":"collect_payment","destination":"tvscredit.collections@upi"}}'

# 3. Same token, but the ATTACKER's claim (right amount, wrong destination)
curl -X POST $BASE_URL/intent/verify -H "Content-Type: application/json" \
  -d '{"token":"<paste>","claimed":{"loan_id":"LOAN-4521","purpose":"emi_due","amount":3200.0,"action":"collect_payment","destination":"fraudster123@upi"}}'
```

Step 3 returns `"matched": false, "reason": "mismatch on: destination"`
even though the fraudster knew the real loan ID and amount — that's the
Attack Demo slide, running as real code.

## Honest limitations (say these out loud in the code walkthrough)

- **HMAC-SHA256, not asymmetric signing.** Simple and genuinely secure
  for this demo, but production should move to RSA/ECDSA so the
  signing key never has to be shared with anything that verifies.
- **`kyc_authenticity.py` is a placeholder heuristic**, not a trained
  deepfake detector. It's wired with the exact input/output shape a
  real DeepWatch-derived model would use, so swapping it in later is a
  model-loading change, not an architecture change. Do not claim
  otherwise in front of the jury.
- **In-memory storage.** Fine for a demo; production needs this backed
  by TVS's actual LMS/CRM as the account source of truth.
