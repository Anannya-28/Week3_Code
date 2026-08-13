
from sqlalchemy.orm import Session
from modules.cart.model import CartItem


class CartRepository:
    @staticmethod
    def get_by_id(db: Session, cart_item_id: int) -> CartItem | None:
        return (
            db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        )

    @staticmethod
    def get_for_user(db: Session, user_id: int) -> list[CartItem]:
        return (
            db.query(CartItem)
            .filter(CartItem.user_id == user_id)
            .order_by(CartItem.id)
            .all()
        )

    @staticmethod
    def get_for_product(
        db: Session, user_id: int, product_id: int
    ) -> CartItem | None:
        return (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
            .first()
        )

    @staticmethod
    def save(db: Session, item: CartItem) -> CartItem:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item: CartItem) -> None:
        db.delete(item)
        db.commit()
