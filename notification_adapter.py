"""
Pramaan v3 — Pluggable Notification & Transport Adapter Architecture
===================================================================
Decouples core Pramaan cryptographic intent generation and verification
from external messaging transports.

Transports hierarchy:
1. TelegramTransport / TelegramAdapter (PRIMARY LIVE DEMO TRANSPORT via official Telegram Bot API)
2. CallMeBotAdapter (RETAINED SECONDARY DEMO TRANSPORT — personal WhatsApp bot)
3. MockNotificationAdapter / MockWhatsAppAdapter (OFFLINE / FALLBACK TRANSPORT)
4. TVSWhatsAppBusinessAdapter (PRODUCTION TARGET SPECIFICATION — Meta Cloud API)
"""

import os
import json
import urllib.parse
import urllib.request
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("pramaan.notification")


class NotificationTransport(ABC):
    """Abstract interface for dispatching Pramaan capability intents to customers."""

    @property
    @abstractmethod
    def channel_type(self) -> str:
        """Channel identifier: 'telegram' | 'whatsapp' | 'mock'"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human readable provider name"""
        pass

    @property
    @abstractmethod
    def is_production(self) -> bool:
        """Flag identifying if transport is production vs demo prototype"""
        pass

    @abstractmethod
    def send_verification_message(
        self,
        recipient: str = "",
        payload: Optional[Dict[str, Any]] = None,
        deep_link: str = "",
        web_verify_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Dispatches signed capability verification link to customer."""
        pass


# Backward compatibility alias
WhatsAppTransport = NotificationTransport


def format_pramaan_message(payload: Dict[str, Any], deep_link: str, web_verify_url: Optional[str] = None) -> str:
    """Generates canonical TVS Credit Pramaan verification message from signed intent."""
    loan_id = str(payload.get("loan_id", "LOAN-4521"))
    loan_suffix = loan_id[-4:] if len(loan_id) >= 4 else loan_id
    purpose_raw = str(payload.get("purpose", "emi_due")).replace("_", " ").title()
    amount = float(payload.get("amount", 0.0))
    agent_name = payload.get("agent_name", "TVS Credit Executive")
    agent_id = payload.get("agent_id", "AGT-7701")
    channel = str(payload.get("channel", "call")).upper()
    dest = payload.get("destination") or "tvscredit.collections@upi"

    primary_url = web_verify_url or deep_link

    return (
        "🔒 *PRAMAAN Security Verification*\n"
        "TVS Credit interaction available\n\n"
        f"📋 *Loan:* ••••{loan_suffix} ({loan_id})\n"
        f"🎯 *Purpose:* {purpose_raw}\n"
        f"💰 *Amount:* ₹{amount:,.0f}\n"
        f"🏦 *Authorized Recipient:* `{dest}`\n"
        f"👤 *Authorized Agent:* {agent_name} ({agent_id})\n"
        f"📡 *Origin Channel:* {channel}\n\n"
        f"🛡️ *Verify securely in TVS Credit:*\n{primary_url}\n\n"
        "⚠️ _Only TVS-authorized intent can unlock a financial action. If you did not initiate this request, open the link and tap 'I DON'T TRUST THIS REQUEST'._"
    )


# ---------------------------------------------------------------------------
# 1. Telegram Transport (PRIMARY LIVE DEMO TRANSPORT)
# ---------------------------------------------------------------------------

class TelegramAdapter(NotificationTransport):
    """
    Primary Live Demo Transport using official Telegram Bot API.
    Uses bot token from environment or config.
    Sends rich HTML formatted message with inline 'Verify Securely' button.
    """

    def __init__(self, bot_token: Optional[str] = None, default_chat_id: Optional[str] = None):
        self.bot_token = bot_token.strip() if bot_token is not None else os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        self.default_chat_id = default_chat_id.strip() if default_chat_id is not None else os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    @property
    def channel_type(self) -> str:
        return "telegram"

    @property
    def provider_name(self) -> str:
        return "Telegram Bot API (Primary Demo Transport)"

    @property
    def is_production(self) -> bool:
        return False

    def send_verification_message(
        self,
        recipient: str = "",
        payload: Optional[Dict[str, Any]] = None,
        deep_link: str = "",
        web_verify_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        payload = payload or {}
        target_chat_id = (recipient or recipient_phone or self.default_chat_id or "").strip()
        action_url = web_verify_url or deep_link

        if not self.bot_token:
            return {
                "success": False,
                "status": "FAILED",
                "provider": self.provider_name,
                "channel": "telegram",
                "target": target_chat_id or "UNCONFIGURED",
                "error": "TELEGRAM_BOT_TOKEN is missing or unconfigured.",
                "message_preview": format_pramaan_message(payload, deep_link, web_verify_url),
                "deep_link": deep_link,
                "web_verify_url": action_url,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }

        if not target_chat_id:
            return {
                "success": False,
                "status": "NO_CHAT_ID",
                "provider": self.provider_name,
                "channel": "telegram",
                "target": "UNREGISTERED",
                "error": "No Telegram Chat ID registered for this customer. Customer must send /start to bot first.",
                "message_preview": format_pramaan_message(payload, deep_link, web_verify_url),
                "deep_link": deep_link,
                "web_verify_url": action_url,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }

        # Build clean Telegram message with HTML formatting
        loan_id = str(payload.get("loan_id", "LOAN-4521"))
        loan_suffix = loan_id[-4:] if len(loan_id) >= 4 else loan_id
        purpose_raw = str(payload.get("purpose", "emi_due")).replace("_", " ").title()
        amount = float(payload.get("amount", 0.0))
        agent_name = payload.get("agent_name", "TVS Credit Executive")
        agent_id = payload.get("agent_id", "AGT-7701")
        channel = str(payload.get("channel", "call")).upper()
        dest = payload.get("destination") or "tvscredit.collections@upi"

        html_text = (
            "🔒 <b>PRAMAAN Security Verification</b>\n"
            "<i>TVS Credit interaction available</i>\n\n"
            f"📋 <b>Loan:</b> ••••{loan_suffix} (<code>{loan_id}</code>)\n"
            f"🎯 <b>Purpose:</b> {purpose_raw}\n"
            f"💰 <b>Amount:</b> ₹{amount:,.0f}\n"
            f"🏦 <b>Authorized Recipient:</b> <code>{dest}</code>\n"
            f"👤 <b>Agent:</b> {agent_name} ({agent_id})\n"
            f"📡 <b>Channel:</b> {channel}\n\n"
            "🛡️ <i>Only TVS-authorized intent can unlock a financial action. Tap below to verify:</i>"
        )

        # Inline button with web verify link
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🛡️ Verify Securely in TVS Credit", "url": action_url}
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        post_data = {
            "chat_id": target_chat_id,
            "text": html_text,
            "parse_mode": "HTML",
            "reply_markup": inline_keyboard,
            "disable_web_page_preview": False
        }

        try:
            req_data = json.dumps(post_data).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Pramaan-v3-TelegramAdapter/3.0"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                resp_bytes = response.read()
                resp_json = json.loads(resp_bytes.decode("utf-8"))

                is_ok = resp_json.get("ok", False)
                return {
                    "success": is_ok,
                    "status": "DELIVERED" if is_ok else "FAILED",
                    "provider": self.provider_name,
                    "channel": "telegram",
                    "target": target_chat_id,
                    "message_preview": format_pramaan_message(payload, deep_link, web_verify_url),
                    "deep_link": deep_link,
                    "web_verify_url": action_url,
                    "response_body": str(resp_json)[:200],
                    "dispatched_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.warning(f"Telegram dispatch error: {e}")
            return {
                "success": False,
                "status": "FAILED",
                "provider": self.provider_name,
                "channel": "telegram",
                "target": target_chat_id,
                "error": str(e),
                "message_preview": format_pramaan_message(payload, deep_link, web_verify_url),
                "deep_link": deep_link,
                "web_verify_url": action_url,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }


# ---------------------------------------------------------------------------
# 2. CallMeBot WhatsApp Adapter (RETAINED SECONDARY DEMO TRANSPORT)
# ---------------------------------------------------------------------------

class CallMeBotAdapter(NotificationTransport):
    """
    Retained Secondary Demo Transport: CallMeBot free personal WhatsApp gateway.
    Explicitly labeled as 'Demo WhatsApp Transport'.
    """

    def __init__(self, phone: str = "", api_key: str = ""):
        self.phone = phone.strip()
        self.api_key = api_key.strip()

    @property
    def channel_type(self) -> str:
        return "whatsapp"

    @property
    def provider_name(self) -> str:
        return "CallMeBot (Secondary WhatsApp Demo Transport)"

    @property
    def is_production(self) -> bool:
        return False

    def send_verification_message(
        self,
        recipient: str = "",
        payload: Optional[Dict[str, Any]] = None,
        deep_link: str = "",
        web_verify_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        payload = payload or {}
        target_phone = (recipient or recipient_phone or self.phone or "").strip()
        clean_phone = target_phone.replace("+", "").replace(" ", "").replace("-", "")
        message_text = format_pramaan_message(payload, deep_link, web_verify_url)

        if not self.api_key or not clean_phone:
            return {
                "success": False,
                "status": "FAILED",
                "provider": self.provider_name,
                "channel": "whatsapp",
                "target": target_phone or "UNCONFIGURED",
                "error": "Missing CallMeBot API key or phone number.",
                "message_preview": message_text,
                "deep_link": deep_link,
                "web_verify_url": web_verify_url,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }

        encoded_msg = urllib.parse.quote_plus(message_text)
        url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_msg}&apikey={self.api_key}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Pramaan-v3-TrustEngine/3.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                resp_text = response.read().decode("utf-8", errors="ignore")
                status_code = response.status
                is_success = "success" in resp_text.lower() or status_code == 200
                return {
                    "success": is_success,
                    "status": "DELIVERED" if is_success else "FAILED",
                    "provider": self.provider_name,
                    "channel": "whatsapp",
                    "target": f"+{clean_phone[:2]} •••• {clean_phone[-4:]}" if len(clean_phone) > 6 else clean_phone,
                    "message_preview": message_text,
                    "deep_link": deep_link,
                    "web_verify_url": web_verify_url,
                    "response_body": resp_text[:200],
                    "dispatched_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.warning(f"CallMeBot dispatch exception: {e}")
            return {
                "success": False,
                "status": "FAILED",
                "provider": self.provider_name,
                "channel": "whatsapp",
                "target": target_phone,
                "error": str(e),
                "message_preview": message_text,
                "deep_link": deep_link,
                "web_verify_url": web_verify_url,
                "dispatched_at": datetime.now(timezone.utc).isoformat(),
            }


# ---------------------------------------------------------------------------
# 3. Mock Adapter (OFFLINE / ZERO-DOWNTIME FALLBACK)
# ---------------------------------------------------------------------------

class MockNotificationAdapter(NotificationTransport):
    """
    In-memory simulated Transport ensuring 100% reliable zero-downtime testing
    and demo execution even when external internet or API tokens are unavailable.
    """

    def __init__(self, channel_override: str = "mock"):
        self._channel = channel_override

    @property
    def channel_type(self) -> str:
        return self._channel

    @property
    def provider_name(self) -> str:
        return "Simulated Gateway (Offline Fallback Transport)"

    @property
    def is_production(self) -> bool:
        return False

    def send_verification_message(
        self,
        recipient: str = "",
        payload: Optional[Dict[str, Any]] = None,
        deep_link: str = "",
        web_verify_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        payload = payload or {}
        message_text = format_pramaan_message(payload, deep_link, web_verify_url)
        target = recipient or recipient_phone or "demo_customer"
        masked = f"{target[:4]}••••{target[-4:]}" if len(target) > 8 else target

        return {
            "success": True,
            "status": "DELIVERED",
            "provider": self.provider_name,
            "channel": self._channel,
            "target": masked,
            "message_preview": message_text,
            "deep_link": deep_link,
            "web_verify_url": web_verify_url or deep_link,
            "response_body": "200 OK — Delivery simulated successfully to customer device",
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }


# Backward compatibility alias
MockWhatsAppAdapter = MockNotificationAdapter


# ---------------------------------------------------------------------------
# 4. TVS WhatsApp Business API (PRODUCTION TARGET SPECIFICATION)
# ---------------------------------------------------------------------------

class TVSWhatsAppBusinessAdapter(NotificationTransport):
    """
    Production Architecture Specification:
    Connects to TVS Credit's authorized enterprise WhatsApp Business API
    (Meta Cloud API / BSP). Do NOT claim this is live for prototype.
    """

    @property
    def channel_type(self) -> str:
        return "whatsapp"

    @property
    def provider_name(self) -> str:
        return "TVS Credit Enterprise WhatsApp Business (Meta Cloud API Target)"

    @property
    def is_production(self) -> bool:
        return True

    def send_verification_message(
        self,
        recipient: str = "",
        payload: Optional[Dict[str, Any]] = None,
        deep_link: str = "",
        web_verify_url: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        payload = payload or {}
        target = recipient or recipient_phone or ""
        return {
            "success": False,
            "status": "SPECIFICATION_STUB",
            "provider": self.provider_name,
            "channel": "whatsapp",
            "target": target,
            "message_preview": format_pramaan_message(payload, deep_link, web_verify_url),
            "deep_link": deep_link,
            "web_verify_url": web_verify_url,
            "response_body": "Production target: requires authorized TVS Meta Cloud credentials & HSM templates.",
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Transport Factory
# ---------------------------------------------------------------------------

def get_notification_transport(
    channel: str = "telegram",
    custom_bot_token: Optional[str] = None,
    custom_chat_id: Optional[str] = None,
    custom_phone: Optional[str] = None,
    custom_api_key: Optional[str] = None,
    force_mock: bool = False
) -> NotificationTransport:
    """Factory creating appropriate transport adapter based on configuration and channel."""
    if force_mock:
        return MockNotificationAdapter(channel_override=channel)

    ch = channel.lower().strip()
    if ch in ("telegram", "tg"):
        token = (custom_bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
        chat_id = (custom_chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
        if token:
            return TelegramAdapter(bot_token=token, default_chat_id=chat_id)
        return MockNotificationAdapter(channel_override="telegram")

    elif ch in ("whatsapp", "callmebot"):
        phone = (custom_phone or os.environ.get("CALLMEBOT_PHONE", "")).strip()
        key = (custom_api_key or os.environ.get("CALLMEBOT_API_KEY", "")).strip()
        if phone and key:
            return CallMeBotAdapter(phone=phone, api_key=key)
        return MockWhatsAppAdapter(channel_override="whatsapp")

    return MockNotificationAdapter(channel_override=ch)


# Backward compatibility wrapper
def get_whatsapp_transport(
    custom_phone: Optional[str] = None,
    custom_api_key: Optional[str] = None,
    force_mock: bool = False
) -> NotificationTransport:
    return get_notification_transport(
        channel="whatsapp",
        custom_phone=custom_phone,
        custom_api_key=custom_api_key,
        force_mock=force_mock
    )
