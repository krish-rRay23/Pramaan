# Pramaan Android App

Kotlin + Jetpack Compose client. All "intelligence" (signing, verification,
the account system of record, authenticity scoring) lives in the backend —
this app is a thin, honest client: capture input, call the API, show the
result.

## One-time setup

1. Open this folder in Android Studio (Hedgehog / 2023.1.1 or newer).
   Let it sync Gradle on first open — this downloads dependencies, so do
   it once with a good connection before you need to work offline.
2. **Point the app at your deployed backend.** In
   `app/build.gradle.kts`, both `defaultConfig` and the `debug` build type
   have a `BASE_URL` build config field:
   ```kotlin
   buildConfigField("String", "BASE_URL", "\"https://pramaan-backend.onrender.com/\"")
   ```
   Replace `https://pramaan-backend.onrender.com/` with your actual Render
   URL — **keep the trailing slash**, Retrofit requires it. Update it in
   both places (or just the `debug` one if you only ever build debug
   builds, which is normal for a hackathon demo).
3. Run on an emulator or a physical device (API 26+). A physical device
   is safer for a live demo — no emulator networking quirks.

## How the pieces map to the backend

| App action | Calls | What it proves |
|---|---|---|
| Home screen loads | `GET /account/{loanId}` | TVS's account system of record |
| "Issue Contact (Admin)" | `POST /intent/issue` | TVS initiating genuine, signed contact |
| "Check For Alert" | `GET /intent/latest/{customerId}` | The proactive alert, before the call |
| "Check This Request" | `POST /intent/verify` | The core mechanism — signature + freshness + does the claim match |
| "KYC Authenticity Check" | `POST /kyc/authenticity` | Where the trained DeepWatch-derived model plugs in |
| "Anomaly Log" | `GET /admin/anomalies` | The audit trail / rate-limit story |

## Running the live demo (single phone)

1. Home → **Wake Backend** — do this a couple of minutes before your slot.
2. Home → **1 · Issue Contact (Admin)** → pick purpose `emi_due`, action
   `collect_payment`, channel `call` → **Issue Signed Contact Intent**.
   This plays TVS's side. Tap **Continue as Customer** to switch roles.
3. On the Alert screen, you're now the customer — the proactive alert is
   already showing the real amount and loan. Tap **Continue to Call**.
4. On the Check screen, the fields are pre-filled to match the genuine
   intent. To run the **genuine scenario**, just tap **Check This
   Request**. To run the **attack scenario**, change only the
   "Payment destination" field to something else (e.g. `fraudster@upi`)
   before tapping — this is the exact "fraudster knows the real loan and
   amount but not the destination" scenario from the deck.
5. The Result screen shows Matched / Not Verified with the reason, and
   what was actually signed for comparison.
6. Anomaly Log will now show the mismatch you just triggered.

## Running it as two roles on two devices (more dramatic in front of a jury)

Same flow, but have a teammate run steps 2 on their own phone (or via
`curl` — see the backend README) while you play the customer on a second
phone starting from step 3 (**Check For Alert** will pick up the intent
your teammate just issued, since both point at the same backend).

## If something doesn't connect

- **Confirm `BASE_URL` matches your actual Render URL exactly**, including
  `https://` and the trailing slash.
- **Cold start**: the first call after backend inactivity can take
  30-60 seconds. The app's network timeouts are set to 60s to absorb
  this, but hitting "Wake Backend" ahead of time avoids the wait
  entirely.
- **Check Logcat** — `OkHttp` tag will show the full request/response
  if `HttpLoggingInterceptor` is active (it is, by default, in this
  build), which is the fastest way to see whether the app is hitting the
  URL you think it is.

## Honest limitations (say these out loud in the code walkthrough)

- The KYC screen calls a placeholder authenticity heuristic on the
  backend (see the backend README) — not a trained deepfake detector.
- This is a single hardcoded demo account (`LOAN-4521`) — there's no
  login, no multi-account support, no persistence beyond the backend's
  in-memory store. That's a deliberate demo-scope choice, not an
  oversight.
