import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def run_tests():
    # 1. Ping
    r = client.get("/ping")
    assert r.status_code == 200
    print("Ping:", r.json())

    # 2. Console
    r = client.get("/console")
    assert r.status_code == 200
    print("Console length:", len(r.text))

    # 3. Issue intent
    r = client.post("/intent/issue", json={"loan_id": "LOAN-4521", "action": "collect_payment"})
    assert r.status_code == 200
    data = r.json()
    token = data["token"]
    print("Issued Token:", token[:30] + "...")

    # 4. Verify genuine
    r = client.post("/intent/verify", json={
        "token": token,
        "claimed": {
            "loan_id": "LOAN-4521",
            "purpose": "emi_due",
            "amount": 3200.0,
            "action": "collect_payment",
            "destination": "tvscredit.collections@upi",
            "agent_id": "AGT-7701"
        }
    })
    assert r.status_code == 200
    res = r.json()
    assert res["decision"] == "ALLOWED"
    assert res["trust_receipt"] is not None
    print("Genuine verify:", res["decision"], res["trust_receipt"]["receipt_id"])

    # 5. Attack Simulator (all 7 scenarios)
    scenarios = [
        "genuine_interaction",
        "wrong_destination",
        "replay_attack",
        "tamper_amount",
        "unauthorized_agent",
        "coordinated_swarm",
        "deepfake_kyc"
    ]
    for sc in scenarios:
        res = client.post(f"/simulator/run?scenario={sc}")
        assert res.status_code == 200
        res_data = res.json()
        assert res_data["passed"] is True
        print(f"Simulator {sc}: passed={res_data['passed']} | decision={res_data['actual_decision']}")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
