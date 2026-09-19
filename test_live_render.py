import urllib.request
import json

scenarios = [
    'genuine_interaction',
    'wrong_destination',
    'replay_attack',
    'tamper_amount',
    'unauthorized_agent',
    'coordinated_swarm',
    'deepfake_kyc'
]

print("--- Testing Live Render Backend (https://pramaan-1zeu.onrender.com) ---")
for sc in scenarios:
    req = urllib.request.Request(f'https://pramaan-1zeu.onrender.com/simulator/run?scenario={sc}', method='POST')
    data = json.loads(urllib.request.urlopen(req).read().decode())
    print(f"{sc:22} | decision: {data['actual_decision']:12} | passed: {data['passed']}")

print("\n--- Testing Console Route ---")
c_req = urllib.request.Request('https://pramaan-1zeu.onrender.com/console')
c_res = urllib.request.urlopen(c_req)
print(f"Console response status: {c_res.status}, length: {len(c_res.read().decode())}")
