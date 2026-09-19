"""
Pramaan Backend — signing utilities

Uses HMAC-SHA256 (symmetric signing) — chosen for demo simplicity and
speed of implementation, not because it's the production-recommended
choice. In production, TVS Credit would use asymmetric signing
(RSA/ECDSA) with a private key that never leaves TVS's HSM/key vault,
so verification could happen in more places without ever sharing the
signing secret. Say this explicitly in the code walkthrough — it's a
deliberate, disclosed simplification, not an oversight.
"""

import base64
import hashlib
import hmac
import json
import os

SECRET_KEY = os.environ.get("PRAMAAN_SECRET_KEY", "demo-secret-change-me").encode()


def canonical_json(payload: dict) -> bytes:
    """Deterministic serialization so the same payload always signs the same way."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_payload(payload: dict) -> str:
    body = canonical_json(payload)
    signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    encoded_body = base64.urlsafe_b64encode(body).decode()
    return f"{encoded_body}.{signature}"


def verify_token(token: str) -> tuple[bool, dict | None]:
    """Returns (signature_valid, decoded_payload_or_None)."""
    try:
        encoded_body, signature = token.split(".", 1)
        body = base64.urlsafe_b64decode(encoded_body.encode())
        expected_signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return False, None
        payload = json.loads(body)
        return True, payload
    except Exception:
        return False, None
