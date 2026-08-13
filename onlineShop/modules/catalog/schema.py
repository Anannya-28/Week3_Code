
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=500)
    category_id: int = Field(gt=0)
    price: Decimal = Field(gt=0)
    available_quantity: int = Field(ge=0)
    product_url: str | None = Field(default=None, max_length=500)


class ProductUpdate(BaseModel):
    """All fields optional — only provided fields are updated (partial update)."""
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    price: Decimal | None = Field(default=None, gt=0)
    available_quantity: int | None = Field(default=None, ge=0)
    product_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None  # admin can soft-deactivate/reactivate


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    category_id: int
    price: Decimal
    available_quantity: int
    product_url: str | None = None
    is_active: bool = True
