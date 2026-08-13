

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging_config import setup_logging
from core.exceptions import AppError, app_error_handler, unhandled_error_handler
from modules.auth.router import router as auth_router
from modules.users.router import router as users_router
from modules.catalog.router import cat_router, prod_router
from modules.cart.router import router as cart_router
from modules.orders.router import router as orders_router
from modules.payment.router import router as payments_router
from modules.admin.router import router as admin_router

setup_logging()

tags_metadata = [
    {
        "name": "General",
        "description": "Health check and root endpoints.",
    },
    {
        "name": "Auth",
        "description": "Login, logout and token refresh.",
    },
    {
        "name": "Users",
        "description": "User registration and profile management.",
    },
    {
        "name": "Catalog - Categories",
        "description": "Browse product categories (public).",
    },
    {
        "name": "Catalog - Products",
        "description": "Browse, search and retrieve products (public).",
    },
    {
        "name": "Cart",
        "description": "Add, update, remove and view cart items.",
    },
    {
        "name": "Orders",
        "description": "Checkout, order history and order details.",
    },
    {
        "name": "Payments",
        "description": "Process payments for placed orders.",
    },
    {
        "name": "Admin",
        "description": "Admin-only — manage products, categories and orders.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="ABC Store API",
    description="E-commerce REST API built with FastAPI + SQLAlchemy",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


# ── Exception handlers ────────────────────────────────────────────────────────

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(cat_router)       
app.include_router(prod_router)     
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(admin_router)


# ── General routes ────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    return {"message": "Welcome to ABC Store API"}


@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy", "environment": settings.APP_ENV}
