from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.payment.schema import PaymentRequest, PaymentResponse
from modules.payment.service import PaymentService
from modules.users.model import User

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/process", response_model=PaymentResponse)
def process_payment(             
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process payment for an existing order. Dummy — always succeeds."""
    return PaymentService.process(request, db)