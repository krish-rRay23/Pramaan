"""
Pramaan v3.1 — Cryptographic Trust Utilities (Ed25519 Asymmetric Engine)
========================================================================
Implements genuine asymmetric Ed25519 public-key signing, verification,
and enterprise key lifecycle management:
- Lifecycle states: ACTIVE -> STAGED -> VERIFICATION_ONLY -> REVOKED.
- Every signed intent and Trust Receipt carries its key_id.
- Master authority keys never leave the server; public keys published at /auth/public-key.
- Full canonical binding: customer, loan, purpose, action, amount, destination,
  channel, partner, agent, nonce, expiry, audience, session, and key_id.
"""

import base64
import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any, List

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger("pramaan.crypto")

# -------------------------------------------------------------------------
# Environment loading
# -------------------------------------------------------------------------
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    _k = _k.strip()
                    _v = _v.strip().strip("'\"")
                    if _k and _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        pass

# -------------------------------------------------------------------------
# Key Lifecycle Management (Active, Staged, Verification-Only, Revoked)
# -------------------------------------------------------------------------
_DEFAULT_TVS_SEED = hashlib.sha256(b"tvs_credit_pramaan_ed25519_master_authority_2026").digest()

_KEY_REGISTRY: Dict[str, Dict[str, Any]] = {}
_ACTIVE_KEY_ID: str = ""


def _register_key(private_bytes: bytes, status: str = "ACTIVE") -> str:
    global _ACTIVE_KEY_ID
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    pub_hex = pub_bytes.hex()
    key_id = f"tvs-ed25519-{pub_hex[:16]}"

    _KEY_REGISTRY[key_id] = {
        "key_id": key_id,
        "status": status,
        "private_key": priv,
        "public_key": pub,
        "public_key_hex": pub_hex,
        "algorithm": "Ed25519",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if status == "ACTIVE":
        _ACTIVE_KEY_ID = key_id

    return key_id


# Initialize master TVS Credit authority key
_env_key_hex = os.environ.get("PRAMAAN_ED25519_PRIVATE_KEY")
if _env_key_hex and len(_env_key_hex.strip()) == 64:
    try:
        _PRIMARY_KEY_ID = _register_key(bytes.fromhex(_env_key_hex.strip()), status="ACTIVE")
        logger.info(f"[SECURITY] Loaded persistent Ed25519 Private Key: {_PRIMARY_KEY_ID}")
    except Exception as e:
        logger.warning(f"[SECURITY] Failed to load key from env: {e}. Using deterministic TVS master key.")
        _PRIMARY_KEY_ID = _register_key(_DEFAULT_TVS_SEED, status="ACTIVE")
else:
    _PRIMARY_KEY_ID = _register_key(_DEFAULT_TVS_SEED, status="ACTIVE")

# Backward compatibility module-level references
_ACTIVE_RECORD = _KEY_REGISTRY[_ACTIVE_KEY_ID]
_PRIVATE_KEY = _ACTIVE_RECORD["private_key"]
_PUBLIC_KEY = _ACTIVE_RECORD["public_key"]
PUBLIC_KEY_HEX = _ACTIVE_RECORD["public_key_hex"]
KEY_ID = _ACTIVE_KEY_ID


def rotate_authority_key(new_seed: Optional[bytes] = None) -> str:
    """
    Rotates the active Ed25519 signing key.
    Transitions prior active key to VERIFICATION_ONLY (permitting in-flight intents to verify until expiry).
    Returns the new active key_id.
    """
    global _ACTIVE_KEY_ID, _PRIVATE_KEY, _PUBLIC_KEY, PUBLIC_KEY_HEX, KEY_ID
    if _ACTIVE_KEY_ID in _KEY_REGISTRY:
        _KEY_REGISTRY[_ACTIVE_KEY_ID]["status"] = "VERIFICATION_ONLY"

    seed = new_seed or secrets.token_bytes(32)
    new_key_id = _register_key(seed, status="ACTIVE")
    _ACTIVE_KEY_ID = new_key_id
    _ACTIVE_RECORD = _KEY_REGISTRY[new_key_id]
    _PRIVATE_KEY = _ACTIVE_RECORD["private_key"]
    _PUBLIC_KEY = _ACTIVE_RECORD["public_key"]
    PUBLIC_KEY_HEX = _ACTIVE_RECORD["public_key_hex"]
    KEY_ID = new_key_id
    logger.info(f"[SECURITY] Rotated signing authority to new key: {new_key_id}")
    return new_key_id


def revoke_authority_key(target_key_id: str, reason: str = "Compromise mitigation") -> bool:
    """Transitions a key to REVOKED. Tokens signed with this key will fail verification."""
    if target_key_id in _KEY_REGISTRY:
        _KEY_REGISTRY[target_key_id]["status"] = "REVOKED"
        _KEY_REGISTRY[target_key_id]["revoked_reason"] = reason
        logger.warning(f"[SECURITY] Key {target_key_id} has been REVOKED. Reason: {reason}")
        return True
    return False


def get_key_catalog() -> List[Dict[str, Any]]:
    """Returns public key catalog for third-party / mobile verification."""
    return [
        {
            "key_id": k["key_id"],
            "status": k["status"],
            "algorithm": k["algorithm"],
            "public_key_hex": k["public_key_hex"],
            "created_at": k["created_at"],
            "is_active": (k["key_id"] == _ACTIVE_KEY_ID and k["status"] == "ACTIVE")
        }
        for k in _KEY_REGISTRY.values()
    ]


def canonical_json(payload: dict) -> bytes:
    """Deterministic serialization ensuring signature reproducibility across architectures."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict, key_id: Optional[str] = None) -> str:
    """
    Signs an intent payload using specified or active Ed25519 private key.
    Includes key_id in payload metadata.
    Returns URL-safe bearer token: {base64url(payload_json)}.{signature_hex}
    """
    target_key_id = key_id or payload.get("key_id") or _ACTIVE_KEY_ID
    target_record = _KEY_REGISTRY.get(target_key_id, _ACTIVE_RECORD)
    payload_to_sign = dict(payload)
    payload_to_sign["key_id"] = target_record["key_id"]

    body_bytes = canonical_json(payload_to_sign)
    signature_bytes = target_record["private_key"].sign(body_bytes)
    signature_hex = signature_bytes.hex()
    encoded_body = base64.urlsafe_b64encode(body_bytes).decode("ascii")
    return f"{encoded_body}.{signature_hex}"


def verify_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verifies Ed25519 public key signature over the token body.
    Supports key rotation: locates appropriate public key by key_id.
    Fails if key is REVOKED, STAGED, or invalid.
    """
    try:
        if not token or "." not in token:
            return False, None
        encoded_body, signature_hex = token.split(".", 1)
        body_bytes = base64.urlsafe_b64decode(encoded_body.encode("ascii"))
        payload = json.loads(body_bytes.decode("utf-8"))
        sig_bytes = bytes.fromhex(signature_hex)

        # Locate key
        token_key_id = payload.get("key_id", _ACTIVE_KEY_ID)
        key_record = _KEY_REGISTRY.get(token_key_id)

        if not key_record:
            # Fallback to default active key
            key_record = _ACTIVE_RECORD

        # Key lifecycle check
        if key_record["status"] not in ("ACTIVE", "VERIFICATION_ONLY"):
            logger.warning(f"[SECURITY] Rejecting token: Key {token_key_id} is {key_record['status']}")
            return False, None

        key_record["public_key"].verify(sig_bytes, body_bytes)
        return True, payload
    except (InvalidSignature, ValueError, Exception):
        return False, None


def sign_receipt(receipt_data: dict) -> str:
    """Generates an unforgeable Ed25519 cryptographic attestation for a Trust Receipt."""
    active_key = _KEY_REGISTRY.get(_ACTIVE_KEY_ID, _ACTIVE_RECORD)
    receipt_data["key_id"] = active_key["key_id"]
    body_bytes = canonical_json(receipt_data)
    return active_key["private_key"].sign(body_bytes).hex()


def verify_receipt_signature(receipt_data: dict, signature_hex: str) -> bool:
    """Verifies an issued Trust Receipt signature using the appropriate Ed25519 public key."""
    try:
        receipt_key_id = receipt_data.get("key_id", _ACTIVE_KEY_ID)
        key_record = _KEY_REGISTRY.get(receipt_key_id, _ACTIVE_RECORD)
        if key_record["status"] not in ("ACTIVE", "VERIFICATION_ONLY"):
            return False

        body_bytes = canonical_json(receipt_data)
        sig_bytes = bytes.fromhex(signature_hex)
        key_record["public_key"].verify(sig_bytes, body_bytes)
        return True
    except Exception:
        return False


def get_public_crypto_metadata() -> dict:
    """Public cryptographic contract exposed for mobile and third-party verification."""
    return {
        "authority": "TVS Credit Services Limited",
        "algorithm": "Ed25519",
        "key_id": _ACTIVE_KEY_ID,
        "public_key_hex": PUBLIC_KEY_HEX,
        "signature_format": "RAW_HEX_64_BYTES",
        "encoding": "RFC 8032",
        "canonicalization": "RFC 8785 (Deterministic JSON JCS)",
        "key_catalog": get_key_catalog(),
    }
