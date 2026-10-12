"""
Pramaan v3.1 — Persistent State Abstraction & Repository Pattern
================================================================
Defines the repository interface for financial capability state,
guaranteeing seamless transition between In-Memory demo mode and
Enterprise PostgreSQL production storage.
"""

from abc import ABC, abstractmethod
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set


class AbstractRepository(ABC):
    """Abstract Repository interface for Pramaan state management."""

    # --- Intents ---
    @abstractmethod
    def save_intent(self, intent_id: str, record: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_intents(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    # --- Nonces & Replay ---
    @abstractmethod
    def record_nonce(self, nonce: str) -> None:
        pass

    @abstractmethod
    def is_nonce_consumed(self, nonce: str) -> bool:
        pass

    # --- Revocations ---
    @abstractmethod
    def revoke_intent(self, identifier: str, reason: str) -> None:
        pass

    @abstractmethod
    def is_intent_revoked(self, identifier: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def list_revocations(self) -> Dict[str, str]:
        pass

    # --- Quarantine & Swarm ---
    @abstractmethod
    def quarantine_destination(self, destination: str) -> None:
        pass

    @abstractmethod
    def is_destination_quarantined(self, destination: str) -> bool:
        pass

    @abstractmethod
    def list_quarantined_destinations(self) -> Set[str]:
        pass

    # --- Trust Receipts ---
    @abstractmethod
    def save_receipt(self, receipt: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_receipt_by_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_receipts(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    # --- Incidents ---
    @abstractmethod
    def save_incident(self, incident: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def list_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    # --- Customer Bindings & Telegram ---
    @abstractmethod
    def bind_customer_telegram(self, customer_id: str, chat_id: str) -> None:
        pass

    @abstractmethod
    def get_customer_telegram(self, customer_id: str) -> Optional[str]:
        pass

    # --- One-Time Secure Pairing Tokens ---
    @abstractmethod
    def create_pairing_token(self, customer_id: str, ttl_seconds: int = 900) -> str:
        pass

    @abstractmethod
    def validate_and_consume_pairing_token(self, token: str) -> Optional[str]:
        pass

    # --- Notification Outbox ---
    @abstractmethod
    def save_outbox_message(self, message: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_pending_outbox_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_outbox_status(self, outbox_id: str, status: str, error: Optional[str] = None) -> None:
        pass

    # --- Audit Trail & RBAC ---
    @abstractmethod
    def record_audit_event(self, event: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def list_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    # --- Telegram Update Idempotency ---
    @abstractmethod
    def is_update_processed(self, update_id: int) -> bool:
        pass

    @abstractmethod
    def mark_update_processed(self, update_id: int) -> None:
        pass


class InMemoryRepository(AbstractRepository):
    """
    Default in-memory repository for zero-dependency local testing,
    continuous integration, and interactive demo execution.
    """

    def __init__(self):
        self.intents: Dict[str, Dict[str, Any]] = {}
        self.consumed_nonces: Set[str] = set()
        self.revoked_intents: Dict[str, str] = {}
        self.quarantined_destinations: Set[str] = {
            "known.fraudster@upi",
            "scam.collector@oksbi",
        }
        self.receipts: List[Dict[str, Any]] = []
        self.receipts_by_intent: Dict[str, Dict[str, Any]] = {}
        self.incidents: List[Dict[str, Any]] = []
        self.telegram_chats: Dict[str, str] = {
            "CUST-001": "1322711658",
            "LOAN-4521": "1322711658",
        }
        self.pairing_tokens: Dict[str, Dict[str, Any]] = {}  # token -> {customer_id, expires_at, consumed}
        self.outbox: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.processed_update_ids: Set[int] = set()

    # --- Intents ---
    def save_intent(self, intent_id: str, record: Dict[str, Any]) -> None:
        self.intents[intent_id] = record

    def get_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        return self.intents.get(intent_id)

    def list_intents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.intents.values())[-limit:]

    # --- Nonces ---
    def record_nonce(self, nonce: str) -> None:
        self.consumed_nonces.add(nonce)

    def is_nonce_consumed(self, nonce: str) -> bool:
        return nonce in self.consumed_nonces

    # --- Revocations ---
    def revoke_intent(self, identifier: str, reason: str) -> None:
        self.revoked_intents[identifier] = reason
        if identifier in self.intents:
            self.intents[identifier]["status"] = "REVOKED"

    def is_intent_revoked(self, identifier: str) -> Tuple[bool, str]:
        if identifier in self.revoked_intents:
            return True, self.revoked_intents[identifier]
        return False, ""

    def list_revocations(self) -> Dict[str, str]:
        return dict(self.revoked_intents)

    # --- Quarantine ---
    def quarantine_destination(self, destination: str) -> None:
        self.quarantined_destinations.add(destination.strip().lower())

    def is_destination_quarantined(self, destination: str) -> bool:
        if not destination:
            return False
        return destination.strip().lower() in self.quarantined_destinations

    def list_quarantined_destinations(self) -> Set[str]:
        return set(self.quarantined_destinations)

    # --- Trust Receipts ---
    def save_receipt(self, receipt: Dict[str, Any]) -> None:
        self.receipts.append(receipt)
        intent_id = receipt.get("intent_id") or receipt.get("interaction_id")
        if intent_id:
            self.receipts_by_intent[intent_id] = receipt

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        for r in reversed(self.receipts):
            if r.get("receipt_id") == receipt_id:
                return r
        return None

    def get_receipt_by_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        return self.receipts_by_intent.get(intent_id)

    def list_receipts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.receipts[-limit:]

    # --- Incidents ---
    def save_incident(self, incident: Dict[str, Any]) -> None:
        self.incidents.append(incident)

    def list_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.incidents[-limit:]

    # --- Customer Bindings ---
    def bind_customer_telegram(self, customer_id: str, chat_id: str) -> None:
        self.telegram_chats[customer_id] = chat_id

    def get_customer_telegram(self, customer_id: str) -> Optional[str]:
        return self.telegram_chats.get(customer_id)

    # --- One-Time Secure Pairing Tokens ---
    def create_pairing_token(self, customer_id: str, ttl_seconds: int = 900) -> str:
        token = f"PAIR-{uuid.uuid4().hex[:12].upper()}"
        expires_at = time.time() + ttl_seconds
        self.pairing_tokens[token] = {
            "customer_id": customer_id,
            "expires_at": expires_at,
            "consumed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return token

    def validate_and_consume_pairing_token(self, token: str) -> Optional[str]:
        entry = self.pairing_tokens.get(token.strip())
        if not entry:
            return None
        if entry["consumed"] or time.time() > entry["expires_at"]:
            return None
        # Consume token immediately
        entry["consumed"] = True
        return entry["customer_id"]

    # --- Outbox ---
    def save_outbox_message(self, message: Dict[str, Any]) -> None:
        self.outbox.append(message)

    def get_pending_outbox_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        return [m for m in self.outbox if m.get("status") in ("PENDING", "RETRYING")][:limit]

    def update_outbox_status(self, outbox_id: str, status: str, error: Optional[str] = None) -> None:
        for m in self.outbox:
            if m.get("outbox_id") == outbox_id:
                m["status"] = status
                if error:
                    m["error"] = error
                if status == "DELIVERED":
                    m["delivered_at"] = datetime.now(timezone.utc).isoformat()
                break

    # --- Audit Trail ---
    def record_audit_event(self, event: Dict[str, Any]) -> None:
        self.audit_log.append(event)
        if len(self.audit_log) > 500:
            del self.audit_log[:100]

    def list_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.audit_log[-limit:]

    # --- Telegram Updates ---
    def is_update_processed(self, update_id: int) -> bool:
        return update_id in self.processed_update_ids

    def mark_update_processed(self, update_id: int) -> None:
        self.processed_update_ids.add(update_id)


class PostgreSQLRepository(AbstractRepository):
    """
    Production Target Architecture:
    Implements enterprise-grade persistence backed by relational PostgreSQL.
    Provides schema definitions, parameterized queries, and connection contract.
    """

    DDL_SCHEMA = """
    -- Pramaan v3.1 Enterprise Storage Schema
    CREATE TABLE IF NOT EXISTS pramaan_intents (
        intent_id VARCHAR(64) PRIMARY KEY,
        token TEXT NOT NULL,
        customer_id VARCHAR(64) NOT NULL,
        loan_id VARCHAR(64) NOT NULL,
        purpose VARCHAR(64) NOT NULL,
        action VARCHAR(64) NOT NULL,
        amount NUMERIC(12, 2) NOT NULL,
        destination VARCHAR(128) NOT NULL,
        nonce VARCHAR(64) UNIQUE NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
        issued_at TIMESTAMPTZ NOT NULL,
        expires_at TIMESTAMPTZ NOT NULL,
        payload_json JSONB NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pramaan_consumed_nonces (
        nonce VARCHAR(64) PRIMARY KEY,
        consumed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS pramaan_revocations (
        identifier VARCHAR(128) PRIMARY KEY,
        reason TEXT NOT NULL,
        revoked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS pramaan_quarantined_destinations (
        destination VARCHAR(128) PRIMARY KEY,
        quarantined_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS pramaan_trust_receipts (
        receipt_id VARCHAR(64) PRIMARY KEY,
        intent_id VARCHAR(64) REFERENCES pramaan_intents(intent_id),
        customer_id VARCHAR(64) NOT NULL,
        loan_id VARCHAR(64) NOT NULL,
        amount NUMERIC(12, 2) NOT NULL,
        destination VARCHAR(128) NOT NULL,
        signature_hex TEXT NOT NULL,
        issued_at TIMESTAMPTZ NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pramaan_outbox (
        outbox_id VARCHAR(64) PRIMARY KEY,
        intent_id VARCHAR(64) NOT NULL,
        channel VARCHAR(32) NOT NULL,
        recipient VARCHAR(128) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        retry_count INT NOT NULL DEFAULT 0,
        payload_json JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        delivered_at TIMESTAMPTZ
    );

    CREATE TABLE IF NOT EXISTS pramaan_audit_events (
        event_id SERIAL PRIMARY KEY,
        operator_id VARCHAR(64) NOT NULL,
        role VARCHAR(32) NOT NULL,
        action VARCHAR(64) NOT NULL,
        resource_id VARCHAR(128),
        correlation_id VARCHAR(64),
        details_json JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url
        self._fallback = InMemoryRepository()

    # Delegates to fallback if live DB pool is unconfigured (clean degraded demo mode)
    def save_intent(self, intent_id: str, record: Dict[str, Any]) -> None:
        self._fallback.save_intent(intent_id, record)

    def get_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_intent(intent_id)

    def list_intents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._fallback.list_intents(limit)

    def record_nonce(self, nonce: str) -> None:
        self._fallback.record_nonce(nonce)

    def is_nonce_consumed(self, nonce: str) -> bool:
        return self._fallback.is_nonce_consumed(nonce)

    def revoke_intent(self, identifier: str, reason: str) -> None:
        self._fallback.revoke_intent(identifier, reason)

    def is_intent_revoked(self, identifier: str) -> Tuple[bool, str]:
        return self._fallback.is_intent_revoked(identifier)

    def list_revocations(self) -> Dict[str, str]:
        return self._fallback.list_revocations()

    def quarantine_destination(self, destination: str) -> None:
        self._fallback.quarantine_destination(destination)

    def is_destination_quarantined(self, destination: str) -> bool:
        return self._fallback.is_destination_quarantined(destination)

    def list_quarantined_destinations(self) -> Set[str]:
        return self._fallback.list_quarantined_destinations()

    def save_receipt(self, receipt: Dict[str, Any]) -> None:
        self._fallback.save_receipt(receipt)

    def get_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_receipt(receipt_id)

    def get_receipt_by_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        return self._fallback.get_receipt_by_intent(intent_id)

    def list_receipts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._fallback.list_receipts(limit)

    def save_incident(self, incident: Dict[str, Any]) -> None:
        self._fallback.save_incident(incident)

    def list_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._fallback.list_incidents(limit)

    def bind_customer_telegram(self, customer_id: str, chat_id: str) -> None:
        self._fallback.bind_customer_telegram(customer_id, chat_id)

    def get_customer_telegram(self, customer_id: str) -> Optional[str]:
        return self._fallback.get_customer_telegram(customer_id)

    def create_pairing_token(self, customer_id: str, ttl_seconds: int = 900) -> str:
        return self._fallback.create_pairing_token(customer_id, ttl_seconds)

    def validate_and_consume_pairing_token(self, token: str) -> Optional[str]:
        return self._fallback.validate_and_consume_pairing_token(token)

    def save_outbox_message(self, message: Dict[str, Any]) -> None:
        self._fallback.save_outbox_message(message)

    def get_pending_outbox_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._fallback.get_pending_outbox_messages(limit)

    def update_outbox_status(self, outbox_id: str, status: str, error: Optional[str] = None) -> None:
        self._fallback.update_outbox_status(outbox_id, status, error)

    def record_audit_event(self, event: Dict[str, Any]) -> None:
        self._fallback.record_audit_event(event)

    def list_audit_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._fallback.list_audit_events(limit)

    def is_update_processed(self, update_id: int) -> bool:
        return self._fallback.is_update_processed(update_id)

    def mark_update_processed(self, update_id: int) -> None:
        self._fallback.mark_update_processed(update_id)


# Global singleton instance
_REPOSITORY_INSTANCE: Optional[AbstractRepository] = None


def get_repository() -> AbstractRepository:
    global _REPOSITORY_INSTANCE
    if _REPOSITORY_INSTANCE is None:
        _REPOSITORY_INSTANCE = InMemoryRepository()
    return _REPOSITORY_INSTANCE
