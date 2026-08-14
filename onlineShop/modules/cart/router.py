from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.cart.schema import (
    CartAdd, CartItemView, CartSummary, CartUpdate
)
from modules.cart.service import CartService
from modules.users.model import User

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("/summary", response_model=CartSummary)
def cart_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View cart total and all items for the logged-in user."""
    return CartService.summary(current_user.id, db)


@router.get("", response_model=list[CartItemView])
def view_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all items in the logged-in user's cart."""
    return CartService.view(current_user.id, db)


@router.post(
    "/add",
    response_model=CartItemView,
    status_code=status.HTTP_201_CREATED,
)
def add_to_cart(
    request: CartAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a product to cart. user_id is derived from the JWT token."""
    return CartService.add(request, current_user.id, db)


@router.put("/update/{cart_item_id}", response_model=CartItemView)
def update_cart(
    cart_item_id: int,
    request: CartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CartService.update(cart_item_id, request, current_user.id, db)


@router.delete(
    "/remove/{cart_item_id}",
    response_class=PlainTextResponse,
)
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a cart item. Only the item owner can remove."""
    return CartService.remove(cart_item_id, current_user.id, db)
