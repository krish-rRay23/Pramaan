"""
Pramaan 2.0 Backend — Cryptographic Trust Utilities (Ed25519 Asymmetric Engine)
==============================================================================
Implements genuine asymmetric Ed25519 public-key signing and verification.
- Server holds the private signing key (never leaves backend / never in Android).
- Public verification key is published at /auth/public-key.
- Full canonical binding: customer, loan, purpose, action, amount, destination,
  channel, partner, agent, nonce, expiry, audience, and session.
"""

import base64
import json
import logging
import os
import secrets
from typing import Tuple, Optional, Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger("pramaan.crypto")

# -------------------------------------------------------------------------
# Key Lifecycle Management
# -------------------------------------------------------------------------
# Load private key from environment variable (hex encoded 32-byte seed)
# If not present, generate an ephemeral Ed25519 key pair for this runtime.
_env_key_hex = os.environ.get("PRAMAAN_ED25519_PRIVATE_KEY")
if _env_key_hex and len(_env_key_hex.strip()) == 64:
    try:
        _PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(_env_key_hex.strip()))
        logger.info("[SECURITY] Loaded Ed25519 Private Key from PRAMAAN_ED25519_PRIVATE_KEY")
    except Exception as e:
        logger.warning(f"[SECURITY] Failed to load key from env: {e}. Generating new key.")
        _PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
else:
    _PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
    logger.warning("[SECURITY ADVISORY] PRAMAAN_ED25519_PRIVATE_KEY not set in environment. Generated runtime Ed25519 key pair.")

_PUBLIC_KEY = _PRIVATE_KEY.public_key()
_PUBLIC_KEY_BYTES = _PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)
PUBLIC_KEY_HEX = _PUBLIC_KEY_BYTES.hex()
KEY_ID = f"tvs-ed25519-{PUBLIC_KEY_HEX[:16]}"


def canonical_json(payload: dict) -> bytes:
    """Deterministic serialization ensuring signature reproducibility across architectures."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict) -> str:
    """Signs an intent payload using Ed25519 private key.
    Returns a URL-safe bearer token: {base64url(payload_json)}.{signature_hex}
    """
    body_bytes = canonical_json(payload)
    signature_bytes = _PRIVATE_KEY.sign(body_bytes)
    signature_hex = signature_bytes.hex()
    encoded_body = base64.urlsafe_b64encode(body_bytes).decode("ascii")
    return f"{encoded_body}.{signature_hex}"


def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verifies Ed25519 public key signature over the token body.
    Requires only the Ed25519 public key.
    """
    try:
        if not token or "." not in token:
            return False, None
        encoded_body, signature_hex = token.split(".", 1)
        body_bytes = base64.urlsafe_b64decode(encoded_body.encode("ascii"))
        sig_bytes = bytes.fromhex(signature_hex)
        _PUBLIC_KEY.verify(sig_bytes, body_bytes)
        payload = json.loads(body_bytes.decode("utf-8"))
        return True, payload
    except (InvalidSignature, ValueError, Exception):
        return False, None


def sign_receipt(receipt_data: dict) -> str:
    """Generates an unforgeable Ed25519 cryptographic attestation for a Trust Receipt."""
    body_bytes = canonical_json(receipt_data)
    return _PRIVATE_KEY.sign(body_bytes).hex()


def verify_receipt_signature(receipt_data: dict, signature_hex: str) -> bool:
    """Verifies an issued Trust Receipt signature using the Ed25519 public key."""
    try:
        body_bytes = canonical_json(receipt_data)
        sig_bytes = bytes.fromhex(signature_hex)
        _PUBLIC_KEY.verify(sig_bytes, body_bytes)
        return True
    except Exception:
        return False


def get_public_crypto_metadata() -> Dict[str, Any]:
    """Exposes public cryptographic algorithm and raw Ed25519 public key."""
    return {
        "algorithm": "Ed25519",
        "curve": "edwards25519",
        "key_id": KEY_ID,
        "issuer": "TVS Credit Pramaan Trust Engine",
        "key_type": "Asymmetric-Ed25519",
        "public_key_hex": PUBLIC_KEY_HEX,
        "format": "raw-32-byte-hex",
    }
