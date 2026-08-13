"""
Dummy Notification / Email Client — Milestone 4 & 5.
"""

import asyncio
import logging
from dataclasses import dataclass

from integration.base_client import BaseExternalClient, ExternalClientError

logger = logging.getLogger(__name__)


@dataclass
class OrderConfirmationPayload:
    recipient_email: str
    order_id: int
    total: str
    item_count: int


class NotificationClient(BaseExternalClient):
    client_name = "notification"

    async def _call(
        self,
        recipient_email: str,
        order_id: int,
        total: str,
        item_count: int,
        **_,
    ) -> dict:
        await asyncio.sleep(0.05)
        logger.debug(
            "notification_attempt",
            extra={"recipient": recipient_email, "order_id": order_id},
        )
        return {"delivered": True, "recipient": recipient_email}


_client = NotificationClient()


class NotificationError(ExternalClientError):
    """Raised when email delivery fails after all retry attempts."""


async def send_order_confirmation(payload: OrderConfirmationPayload) -> None:
    try:
        await _client.execute(
            recipient_email=payload.recipient_email,
            order_id=payload.order_id,
            total=payload.total,
            item_count=payload.item_count,
        )
    except ExternalClientError as exc:
        raise NotificationError(str(exc)) from exc