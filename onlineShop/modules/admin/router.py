from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_roles
from modules.catalog.schema import (
    CategoryCreate, CategoryOut,
    CategoryUpdate, ProductCreate,
    ProductOut, ProductUpdate,
)
from modules.catalog.service import CategoryService, ProductService
from modules.orders.schema import OrderOut
from modules.orders.service import OrderService
from modules.users.model import User

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ── Product management (admin only) ──────────────────────────────────────────

@router.post(
    "/products",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_product(
    request: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """Create a new product. Admin only."""
    return ProductService.create(request, db)


@router.put("/products/{product_id}", response_model=ProductOut)
def admin_update_product(
    product_id: int,
    request: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """Partial update a product. Admin only."""
    return ProductService.update(product_id, request, db)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_200_OK,
)
def admin_deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """
    Soft-deactivate a product (sets is_active=False).
    Hard delete is intentionally not exposed — preserves order history.
    """
    return ProductService.deactivate(product_id, db)


# ── Category management (admin only) ─────────────────────────────────────────

@router.post(
    "/categories",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """Create a new category. Admin only."""
    return CategoryService.create(request, db)


@router.put("/categories/{category_id}", response_model=CategoryOut)
def admin_update_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
):
    """Update a category name. Admin only."""
    return CategoryService.update(category_id, request, db)


# ── Order management (admin + support) ───────────────────────────────────────

@router.get("/orders", response_model=list[OrderOut])
def admin_list_orders(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "support")),
):
    """
    View all orders across all customers.
    Accessible by admin and support roles.
    """
    return OrderService.list_all(db)
