"""
Pramaan 2.0 Backend — Cryptographic Trust Utilities
===================================================
Handles tamper-evident capability token signing, signature verification,
and digital trust receipt signing.
"""

import base64
import hashlib
import hmac
import json
import os
from typing import Tuple, Optional, Dict, Any

SECRET_KEY = os.environ.get("PRAMAAN_SECRET_KEY", "tvs-credit-pramaan-master-secret-key-2026").encode()
RECEIPT_KEY = hashlib.sha256(SECRET_KEY + b"-receipts").digest()


def canonical_json(payload: dict) -> bytes:
    """Deterministic serialization ensuring signature reproducibility."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_payload(payload: dict) -> str:
    """Signs an intent payload and returns a URL-safe bearer token."""
    body = canonical_json(payload)
    signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    encoded_body = base64.urlsafe_b64encode(body).decode()
    return f"{encoded_body}.{signature}"


def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verifies HMAC signature over the token body."""
    try:
        encoded_body, signature = token.split(".", 1)
        body = base64.urlsafe_b64decode(encoded_body.encode())
        expected_signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return False, None
        payload = json.loads(body.decode())
        return True, payload
    except Exception:
        return False, None


def sign_receipt(receipt_data: dict) -> str:
    """Generates an unforgeable cryptographic seal for a Trust Receipt."""
    body = canonical_json(receipt_data)
    return hmac.new(RECEIPT_KEY, body, hashlib.sha256).hexdigest()


def get_public_crypto_metadata() -> Dict[str, Any]:
    """Exposes public cryptographic algorithm and key fingerprint."""
    key_fingerprint = hashlib.sha256(SECRET_KEY).hexdigest()[:16]
    return {
        "algorithm": "HMAC-SHA256",
        "key_id": f"tvs-master-{key_fingerprint}",
        "issuer": "TVS Credit Pramaan Trust Engine",
        "key_type": "ServerSide-Vaulted",
        "public_fingerprint": f"SHA256:{hashlib.sha256(SECRET_KEY).hexdigest()}",
    }
