
import logging
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import AppError
from modules.cart.model import CartItem
from modules.cart.repository import CartRepository
from modules.cart.schema import CartAdd, CartItemView, CartSummary, CartUpdate
from modules.catalog.repository import ProductRepository

logger = logging.getLogger("online_shopping.cart")


class CartService:


    @staticmethod
    def _to_view(item: CartItem) -> CartItemView:
        unit_price = Decimal(str(item.product.price))
        return CartItemView(
            cart_item_id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=unit_price,
            line_total=unit_price * item.quantity,
        )

    

    @staticmethod
    def view(user_id: int, db: Session) -> list[CartItemView]:
        items = CartRepository.get_for_user(db, user_id)
        return [CartService._to_view(i) for i in items]

    @staticmethod
    def summary(user_id: int, db: Session) -> CartSummary:
        items = CartService.view(user_id, db)
        total = sum((i.line_total for i in items), Decimal("0.00"))
        return CartSummary(
            user_id=user_id, items=items, total_amount=total
        )

    @staticmethod
    def add(data: CartAdd, user_id: int, db: Session) -> CartItemView:
       
        product = ProductRepository.get_by_id(db, data.product_id)

        if not product:
            raise AppError(404, "Product not found")

        if not product.is_active:
            raise AppError(400, "Product is no longer available")

        existing = CartRepository.get_for_product(db, user_id, data.product_id)
        total_qty = data.quantity + (existing.quantity if existing else 0)

        if total_qty > product.available_quantity:
            raise AppError(400, "Quantity exceeds available stock")

        if existing:
            existing.quantity = total_qty
            item = existing
        else:
            item = CartItem(
                user_id=user_id,
                product_id=data.product_id,
                quantity=data.quantity,
            )
            db.add(item)

        try:
            db.commit()
            db.refresh(item)
            logger.info(
                "CART ADD | user_id=%s | product_id=%s | qty=%s",
                user_id, data.product_id, item.quantity,
            )
            return CartService._to_view(item)
        except IntegrityError as exc:
            db.rollback()
            raise AppError(409, "Cart item could not be added") from exc

    @staticmethod
    def update(
        cart_item_id: int,
        data: CartUpdate,
        user_id: int,
        db: Session,
    ) -> CartItemView:
        item = CartRepository.get_by_id(db, cart_item_id)

        if not item:
            raise AppError(404, "Cart item not found")

        # ABAC: only owner can update their cart item
        if item.user_id != user_id:
            raise AppError(403, "This cart item does not belong to you")

        if data.quantity > item.product.available_quantity:
            raise AppError(400, "Quantity exceeds available stock")

        item.quantity = data.quantity
        db.commit()
        db.refresh(item)
        return CartService._to_view(item)

    @staticmethod
    def remove(
        cart_item_id: int,
        user_id: int,
        db: Session,
    ) -> str:
        item = CartRepository.get_by_id(db, cart_item_id)

        if not item:
            raise AppError(404, "Cart item not found")

        # ABAC: only owner can remove their cart item
        if item.user_id != user_id:
            raise AppError(403, "This cart item does not belong to you")

        CartRepository.delete(db, item)
        logger.info(
            "CART REMOVE | user_id=%s | cart_item_id=%s",
            user_id, cart_item_id,
        )
        return "Cart item removed successfully"
