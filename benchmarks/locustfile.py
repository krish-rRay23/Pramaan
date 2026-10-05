"""
PRAMAAN v3.1 — Official Locust Load Testing Suite
=================================================
Benchmarks realistic PRAMAAN financial interaction flows under controlled concurrency levels:
1. Public Health & Crypto Telemetry: GET /ping, GET /auth/public-key
2. Intent Issuance (LMS Trigger): POST /intent/issue
3. Customer App Real-Time Polling: GET /intent/latest/{customer_id}
4. Exact Action Gate Verification: POST /intent/verify
5. Immutable Receipt History & Independent Verification: GET /receipts/customer/{id}, POST /receipts/verify
6. End-to-End Composite Journey: Issue -> Poll -> Exact Gate Verify -> Verify Receipt
"""

import uuid
from locust import HttpUser, task, between, tag


class PramaanUser(HttpUser):
    wait_time = between(0.01, 0.05)  # Realistic rapid client pacing

    def on_start(self):
        self.loan_id = "LOAN-4521"
        self.customer_id = "CUST-001"
        self.active_token = None
        self.latest_receipt_id = None

    @tag("telemetry")
    @task(3)
    def test_ping(self):
        """Measures lightweight system health probe latency."""
        self.client.get("/ping", name="GET /ping")

    @tag("crypto_metadata")
    @task(2)
    def test_public_key_catalog(self):
        """Measures public Ed25519 key discovery latency."""
        self.client.get("/auth/public-key", name="GET /auth/public-key")

    @tag("intent_issue")
    @task(4)
    def test_issue_intent(self):
        """Simulates TVS LMS issuing a signed capability intent."""
        payload = {
            "loan_id": self.loan_id,
            "action": "collect_payment",
            "purpose": "emi_due",
            "channel": "app",
            "partner_id": "PARTNER-TVS-01",
            "agent_id": "AGT-7701",
            "customer_phone": "+91 98765 43210"
        }
        res = self.client.post("/intent/issue", json=payload, name="POST /intent/issue")
        if res.status_code == 200:
            try:
                data = res.json()
                self.active_token = data.get("token")
            except Exception:
                pass

    @tag("intent_poll")
    @task(5)
    def test_poll_latest_intent(self):
        """Simulates Android client periodic 2.5s shield polling."""
        res = self.client.get(f"/intent/latest/{self.customer_id}", name="GET /intent/latest/{id}")
        if res.status_code == 200:
            try:
                self.active_token = res.json().get("token")
            except Exception:
                pass

    @tag("action_gate")
    @task(4)
    def test_exact_action_gate(self):
        """Core PRAMAAN Gate: Evaluates claimed interaction against cryptographic token."""
        if not self.active_token:
            # Generate a fresh token first if none in state
            issue_res = self.client.post("/intent/issue", json={
                "loan_id": self.loan_id,
                "action": "collect_payment",
                "purpose": "emi_due",
                "channel": "app"
            }, name="POST /intent/issue (setup)")
            if issue_res.status_code == 200:
                self.active_token = issue_res.json().get("token")

        if self.active_token:
            verify_payload = {
                "token": self.active_token,
                "claimed": {
                    "loan_id": self.loan_id,
                    "purpose": "emi_due",
                    "amount": 3200.0,
                    "action": "collect_payment",
                    "destination": "tvscredit.collections@upi",
                    "agent_id": "AGT-7701"
                }
            }
            res = self.client.post("/intent/verify", json=verify_payload, name="POST /intent/verify")
            if res.status_code == 200:
                try:
                    receipt = res.json().get("trust_receipt")
                    if receipt:
                        self.latest_receipt_id = receipt.get("receipt_id")
                except Exception:
                    pass

    @tag("receipts")
    @task(2)
    def test_customer_receipts(self):
        """Retrieves customer's immutable verified receipts ledger."""
        self.client.get(f"/receipts/customer/{self.customer_id}", name="GET /receipts/customer/{id}")

    @tag("end_to_end")
    @task(3)
    def test_end_to_end_journey(self):
        """Complete 4-step financial capability lifecycle:
        Issue Intent -> Poll Active Intent -> Exact Action Gate Verify -> Retrieve Signed Receipt.
        """
        # Step 1: Issue
        issue_res = self.client.post("/intent/issue", json={
            "loan_id": self.loan_id,
            "action": "collect_payment",
            "purpose": "emi_due",
            "channel": "call"
        }, name="E2E: 1. POST /intent/issue")

        if issue_res.status_code != 200:
            return
        token = issue_res.json().get("token")

        # Step 2: Poll
        poll_res = self.client.get(f"/intent/latest/{self.customer_id}", name="E2E: 2. GET /intent/latest/{id}")
        if poll_res.status_code != 200:
            return

        # Step 3: Exact Action Gate
        verify_res = self.client.post("/intent/verify", json={
            "token": token,
            "claimed": {
                "loan_id": self.loan_id,
                "purpose": "emi_due",
                "amount": 3200.0,
                "action": "collect_payment",
                "destination": "tvscredit.collections@upi",
                "agent_id": "AGT-7701"
            }
        }, name="E2E: 3. POST /intent/verify")
        if verify_res.status_code != 200:
            return

        # Step 4: Verify Receipt
        receipt = verify_res.json().get("trust_receipt")
        if receipt and receipt.get("receipt_id"):
            receipt_id = receipt["receipt_id"]
            self.client.get(f"/receipts/verify/{receipt_id}", name="E2E: 4. GET /receipts/verify/{id}")
