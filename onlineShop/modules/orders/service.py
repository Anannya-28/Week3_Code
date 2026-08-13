import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from core.exceptions import AppError
from modules.cart.repository import CartRepository
from modules.catalog.repository import ProductRepository

# ↓ Root-level folder: integration  (NOT modules.integration)
from integration.payment_gateway import PaymentError, charge_payment
from modules.orders.repository import OrderRepository
from modules.users.repository import UserRepository

logger = logging.getLogger(__name__)


class OrderService:

    @staticmethod
    async def checkout(user_id: int, data, db: Session) -> object:
        logger.info("checkout_started", extra={"user_id": user_id})

        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, "User not found")

        cart_items = CartRepository.list_for_user(db, user_id)
        if not cart_items:
            raise AppError(400, "Cart is empty")

        total = Decimal("0.00")
        order_lines = []

        for item in cart_items:
            product = ProductRepository.get_by_id(db, item.product_id)
            if not product or not product.is_active:
                raise AppError(400, f"Product {item.product_id} is unavailable")
            if product.available_quantity < item.quantity:
                raise AppError(
                    400,
                    f"Insufficient stock for '{product.name}' "
                    f"(requested {item.quantity}, "
                    f"available {product.available_quantity})",
                )
            subtotal = product.price * item.quantity
            total += subtotal
            order_lines.append((product, item.quantity, subtotal))

        # Create the order row first — needed for payment reference
        order = OrderRepository.create(db, user_id=user_id, total=total)

        # ── Milestone 4: retry + timeout payment ──────────────────────────────
        try:
            payment_result = await charge_payment(
                amount=total, order_id=order.id
            )
        except PaymentError as exc:
            OrderRepository.delete(db, order)
            logger.error(
                "checkout_payment_failed",
                extra={
                    "user_id": user_id,
                    "order_id": order.id,
                    "error": str(exc),
                },
            )
            raise AppError(502, "Payment processing failed. Please try again.") from exc

        # Deduct stock and persist order items
        for product, qty, _ in order_lines:
            product.available_quantity -= qty
            OrderRepository.add_item(
                db,
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=product.price,
            )

        CartRepository.clear_for_user(db, user_id)
        db.commit()
        db.refresh(order)

        logger.info(
            "checkout_completed",
            extra={
                "user_id": user_id,
                "order_id": order.id,
                "total": str(total),
                "transaction_id": payment_result.get("transaction_id"),
            },
        )
        return order

    @staticmethod
    def history(user_id: int, db: Session) -> list:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, "User not found")
        return OrderRepository.list_for_user(db, user_id)

    @staticmethod
    def details(order_id: int, db: Session) -> object:
        order = OrderRepository.get_by_id(db, order_id)
        if not order:
            raise AppError(404, "Order not found")
        return order

    @staticmethod
    def list_all(db: Session) -> list:
        return OrderRepository.list_all(db)