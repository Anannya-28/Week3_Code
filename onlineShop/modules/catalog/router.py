
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from modules.catalog.schema import (
    CategoryOut,
    ProductOut,
)
from modules.catalog.service import CategoryService, ProductService


# ── Category routes (public read) ─────────────────────────────────────────────

cat_router = APIRouter(prefix="/api/categories", tags=["Catalog - Categories"])


@cat_router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all product categories."""
    return CategoryService.list_all(db)


# ── Product routes (all public) ───────────────────────────────────────────────

prod_router = APIRouter(prefix="/api/products", tags=["Catalog - Products"])


@prod_router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    """List all active products."""
    return ProductService.list_active(db)


@prod_router.get("/search", response_model=list[ProductOut])
def search_products(
    name: str | None = Query(default=None, max_length=150),
    category: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    """Search active products by name and/or category."""
    return ProductService.search(name, category, db)


@prod_router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Fetch a single product by ID."""
    return ProductService.get(product_id, db)
