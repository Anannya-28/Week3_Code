
import asyncio
import logging
from decimal import Decimal

from integration.base_client import BaseExternalClient, ExternalClientError

logger = logging.getLogger(__name__)


# ── Concrete client ───────────────────────────────────────────────────────────

class PaymentGatewayClient(BaseExternalClient):
   

    client_name = "payment_gateway"

    async def _call(self, amount: Decimal, order_id: int, **_) -> dict:
       
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
  


async def charge_payment(amount: Decimal, order_id: int) -> dict:
    try:
        return await _client.execute(amount=amount, order_id=order_id)
    except ExternalClientError as exc:
        raise PaymentError(str(exc)) from exc
