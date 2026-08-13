

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    payment_method = Column(String(20), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Set by async checkout after payment + shipping calls
    payment_status = Column(
        String(20), nullable=False, default="PENDING"
    )
    tracking_id = Column(String(100), nullable=True)

    user = relationship("User", back_populates="orders")
    details = relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="details")
    product = relationship("Product", back_populates="order_details")
