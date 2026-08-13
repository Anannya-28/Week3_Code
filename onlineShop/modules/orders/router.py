

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.database import get_async_db, get_db
from core.dependencies import get_current_user, require_roles
from modules.orders.schema import CheckoutRequest, OrderOut
from modules.orders.service import OrderService
from modules.users.model import User

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post(
    "/checkout",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    request: CheckoutRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    ASYNC endpoint — awaits payment gateway + shipping client.

    WHY ASYNC:
    Checkout involves two sequential external HTTP calls
    (payment + shipping). Making this async frees the event loop
    for ~500ms per request, enabling significantly higher throughput
    under concurrent load compared to a blocking sync version.

    Background tasks (email + audit log) run AFTER the response
    is returned — user is not blocked waiting for notifications.
    """
    return await OrderService.checkout(
        request,
        current_user.id,
        session,
        background_tasks,
    )


@router.get("/me", response_model=list[OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    SYNC endpoint — simple DB read for current user's orders.

    WHY SYNC: No external calls, fast indexed query.
    Converting to async here would add complexity with zero benefit.
    """
    return OrderService.history(current_user.id, db)


@router.get("/details/{order_id}", response_model=OrderOut)
def order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a specific order. ABAC check: only owner or admin/support."""
    order = OrderService.details(order_id, db)

    if (
        current_user.role not in ("admin", "support")  # ABAC — customer can only see THEIR orders
        and order.user_id != current_user.id
    ):
        from core.exceptions import AppError
        raise AppError(403, "You do not have access to this order")

    return order
