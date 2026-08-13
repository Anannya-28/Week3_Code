
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

PaymentMethod = Literal["CARD", "UPI", "COD"]


class PaymentRequest(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    method: PaymentMethod


class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str | None = None
    message: str
    order_id: int
