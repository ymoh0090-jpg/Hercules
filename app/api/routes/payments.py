from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.api.schemas.payment import PaymentResponse


router = APIRouter()


@router.post(
    "/payments/{order_id}",
    response_model=PaymentResponse
)
def create_payment(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this order"
        )

    existing_payment = db.query(Payment).filter(
        Payment.order_id == order.id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail="Payment already exists"
        )

    payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

@router.post("/payments/{payment_id}/confirm")
def confirm_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this payment"
        )

    if payment.status == "paid":
        raise HTTPException(
            status_code=409,
            detail="Payment already confirmed"
        )

    payment.status = "paid"
    payment.transaction_id = f"TXN-{payment.id}-{order.id}"

    order.status = "paid"

    db.commit()
    db.refresh(payment)

    return payment