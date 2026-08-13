"""
Dummy Payment Gateway Client — Milestone 4.

Simulates an external payment API with:
  - Configurable timeout  (5 s per attempt)
  - Exponential back-off retry  (max 3 attempts)
  - Structured logging on every attempt and outcome
  - PaymentError raised when all retries exhausted

No real money moves.
Replace _call() body with a live httpx call when connecting a real provider.
"""

import asyncio
import logging
from decimal import Decimal

from integration.base_client import BaseExternalClient, ExternalClientError

logger = logging.getLogger(__name__)


# ── Concrete client ───────────────────────────────────────────────────────────

class PaymentGatewayClient(BaseExternalClient):
    """Dummy payment gateway — always approves any charge."""

    client_name = "payment_gateway"

    async def _call(self, amount: Decimal, order_id: int, **_) -> dict:
        """
        Simulates ~100 ms network round-trip to a payment provider.

        To connect a real gateway replace this body with:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    "https://gateway.example.com/charge",
                    json={"amount": str(amount), "order_id": order_id},
                )
                resp.raise_for_status()
                return resp.json()
        """
        await asyncio.sleep(0.1)                   
        logger.debug(
            "payment_gateway_attempt",
            extra={"order_id": order_id, "amount": str(amount)},
        )
        return {
            "status": "approved",
            "transaction_id": f"TXN-{order_id}-DUMMY",
            "amount_charged": str(amount),
        }



_client = PaymentGatewayClient()


class PaymentError(ExternalClientError):
    """Raised when the payment gateway fails after all retry attempts."""


async def charge_payment(amount: Decimal, order_id: int) -> dict:
    """
    Charge `amount` for `order_id` with automatic retry + timeout.

    Returns the gateway response dict on success, e.g.:
        {"status": "approved", "transaction_id": "TXN-1-DUMMY", ...}

    Raises:
        PaymentError — if all retry attempts are exhausted.
    """
    try:
        return await _client.execute(amount=amount, order_id=order_id)
    except ExternalClientError as exc:
        raise PaymentError(str(exc)) from exc