"""
Dummy Shipping Client — Milestone 4.
"""

import asyncio
import logging

from integration.base_client import BaseExternalClient, ExternalClientError

logger = logging.getLogger(__name__)


class ShippingClient(BaseExternalClient):
    client_name = "shipping"

    async def _call(self, order_id: int, address: str = "N/A", **_) -> dict:
        await asyncio.sleep(0.08)
        logger.debug(
            "shipping_attempt",
            extra={"order_id": order_id, "address": address},
        )
        return {
            "tracking_number": f"SHIP-{order_id}-DUMMY",
            "carrier": "DummyCourier",
            "estimated_days": 3,
        }


_client = ShippingClient()


class ShippingError(ExternalClientError):
    """Raised when shipment creation fails after all retry attempts."""


async def create_shipment(order_id: int, address: str = "N/A") -> dict:
    try:
        return await _client.execute(order_id=order_id, address=address)
    except ExternalClientError as exc:
        raise ShippingError(str(exc)) from exc