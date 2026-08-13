
"""
Sync and Async repositories for Orders.

WHY ASYNC VARIANTS:
The checkout flow awaits external payment + shipping API calls.
Having async DB methods avoids mixing sync SQLAlchemy with an
async event loop, which would block all concurrent requests.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from modules.orders.model import Order


class OrderRepository:
    # ── Sync ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Order | None:
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def list_for_user(db: Session, user_id: int) -> list[Order]:
        return (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.order_date.desc())
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> list[Order]:
        """Admin/support: all orders, newest first."""
        return db.query(Order).order_by(Order.order_date.desc()).all()

    # ── Async (used by checkout flow) ─────────────────────────────────────────

    @staticmethod
    async def async_create(session: AsyncSession, order: Order) -> Order:
        """
        Persist a new order and flush to get the generated ID
        before external API calls use it.
        """
        session.add(order)
        await session.flush()   # gets order.id without committing yet
        return order

    @staticmethod
    async def async_get_by_id(
        session: AsyncSession, order_id: int
    ) -> Order | None:
        """
        Load order with details eagerly to avoid lazy-load issues
        in async context.
        """
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.details))
            .filter(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def async_commit(session: AsyncSession) -> None:
        await session.commit()

    @staticmethod
    async def async_rollback(session: AsyncSession) -> None:
        await session.rollback()
