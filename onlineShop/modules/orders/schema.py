
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaymentMethod = Literal["CARD", "UPI", "COD"]


class CheckoutRequest(BaseModel):
    """
    user_id is removed — it is extracted from the JWT token in the router.
    This prevents users from checking out on behalf of others.
    """
    payment_method: PaymentMethod


class OrderDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    order_date: datetime
    payment_method: str
    total_amount: Decimal
    payment_status: str = "PENDING"
    tracking_id: str | None = None
    details: list[OrderDetailOut] = Field(default_factory=list)
