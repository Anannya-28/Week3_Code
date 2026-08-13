"""
Payment Service.

CHANGES FROM MILESTONE 4 REMOVAL:
  - Removed: external HTTP call to payment gateway
  - Replaced with: inline dummy that always returns success
  - Method changed from async → sync (no await needed anymore)
"""

import logging
import uuid

from sqlalchemy.orm import Session

from core.exceptions import AppError
from modules.orders.repository import OrderRepository
from modules.payment.schema import PaymentRequest, PaymentResponse

logger = logging.getLogger("online_shopping.payments")


class PaymentService:

    @staticmethod
    def process(data: PaymentRequest, db: Session) -> PaymentResponse:
        """
        Dummy payment processor.
        No external HTTP call — always returns success.
        Generates a unique transaction ID locally.
        """
        order = OrderRepository.get_by_id(db, data.order_id)

        if not order:
            raise AppError(404, "Order not found")

        if order.payment_status == "PAID":
            raise AppError(409, "Order is already paid")

        # Dummy transaction ID — no external call
        prefix = "COD" if data.method == "COD" else "TXN"
        txn_id = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

        order.payment_status = "PAID"
        db.commit()

        logger.info(
            "DUMMY PAYMENT PROCESSED | order_id=%s | txn=%s | method=%s",
            data.order_id, txn_id, data.method,
        )

        return PaymentResponse(
            success=True,
            transaction_id=txn_id,
            message=f"Dummy payment successful via {data.method}",
            order_id=data.order_id,
        )