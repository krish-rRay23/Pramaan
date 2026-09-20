import urllib.request
import json
import time

RENDER_URL = "https://pramaan-1zeu.onrender.com"

print("Checking Render Live Service Status...")

# Verify public key endpoint
expected_key_id = "tvs-ed25519-3ec728d83398fb49"
req = urllib.request.Request(f"{RENDER_URL}/auth/public-key")
with urllib.request.urlopen(req, timeout=10) as res:
    data = json.loads(res.read().decode())
    key_id = data.get("key_id")
    pub_hex = data.get("public_key_hex")
    algo = data.get("algorithm")
    print(f"Active Live Key ID: {key_id} | Algo: {algo}")
    assert key_id == expected_key_id, f"Expected {expected_key_id}, got {key_id}"
    print(f"PASS: Render persistent public key confirmed: {pub_hex[:16]}...{pub_hex[-16:]}")

print("\n--- Testing All 7 Simulator Scenarios on Live Render ---")
scenarios = [
    'genuine_interaction',
    'wrong_destination',
    'replay_attack',
    'tamper_amount',
    'unauthorized_agent',
    'coordinated_swarm',
    'deepfake_kyc'
]

for sc in scenarios:
    s_req = urllib.request.Request(f"{RENDER_URL}/simulator/run?scenario={sc}", method="POST")
    s_data = json.loads(urllib.request.urlopen(s_req, timeout=15).read().decode())
    print(f"Scenario: {sc:22} | decision: {s_data['actual_decision']:10} | passed: {s_data['passed']}")
    assert s_data['passed'] is True, f"Scenario {sc} failed!"

print("\n--- Verifying Live Console Content ---")
c_req = urllib.request.Request(f"{RENDER_URL}/console")
c_html = urllib.request.urlopen(c_req, timeout=10).read().decode()

assert "Ed25519 • Asymmetric Digital Signature" in c_html, "Missing updated Ed25519 label in live console"
assert "prototype, non-production grade" in c_html, "Missing prototype disclosure in live console"
print("PASS: Live console contains exact updated string 'Ed25519 • Asymmetric Digital Signature'")
print("PASS: Live console contains explicit KYC prototype/research disclosure")

print("\n--- Verifying Intent Issue & Verify Endpoints Live ---")
# 1. Issue genuine intent
issue_payload = json.dumps({
    "loan_id": "LOAN-8832",
    "purpose": "emi_due",
    "action": "collect_payment",
    "channel": "call",
    "partner_id": "PARTNER-TVS-01",
    "agent_id": "AGT-7701"
}).encode('utf-8')

i_req = urllib.request.Request(
    f"{RENDER_URL}/intent/issue",
    data=issue_payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
i_res = urllib.request.urlopen(i_req, timeout=10)
assert i_res.status == 200
i_data = json.loads(i_res.read().decode())
token = i_data["token"]
payload = i_data["payload"]
print(f"PASS: Issued Live Intent for loan {payload['loan_id']} to {payload['agent_name']} (token: {token[:25]}...)")

# 2. Verify intent via exact action gate
verify_payload = json.dumps({
    "token": token,
    "claimed": {
        "loan_id": payload["loan_id"],
        "purpose": payload["purpose"],
        "amount": payload["amount"],
        "action": payload["action"],
        "destination": payload["destination"],
        "agent_id": payload["agent_id"]
    }
}).encode('utf-8')

v_req = urllib.request.Request(
    f"{RENDER_URL}/intent/verify",
    data=verify_payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
v_res = urllib.request.urlopen(v_req, timeout=10)
assert v_res.status == 200
v_data = json.loads(v_res.read().decode())
assert v_data["decision"] == "ALLOWED", f"Expected ALLOWED, got {v_data['decision']}"
receipt = v_data["trust_receipt"]
print(f"PASS: Verified Live Intent! Decision: {v_data['decision']} | Receipt ID: {receipt['receipt_id']}")
print(f"      Receipt Signature: {receipt['signature'][:32]}...")

print("\n====================================================================")
print("ALL LIVE RENDER VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
print("====================================================================")
