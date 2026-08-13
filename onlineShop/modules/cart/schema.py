
from decimal import Decimal
from pydantic import BaseModel, Field


class CartAdd(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    


class CartUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemView(BaseModel):
    cart_item_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class CartSummary(BaseModel):
    user_id: int
    items: list[CartItemView]
    total_amount: Decimal
