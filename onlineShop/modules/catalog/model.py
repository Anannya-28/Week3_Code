

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, Numeric, String
)
from sqlalchemy.orm import relationship
from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column("category_name", String(100), unique=True, nullable=False)

    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column("product_name", String(150), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    available_quantity = Column(Integer, nullable=False)
    product_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_details = relationship("OrderDetail", back_populates="product")
