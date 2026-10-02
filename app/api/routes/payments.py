from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.schemas.payment import PaymentResponse
from app.core.config import settings
from app.core.security import get_current_user
from app.database.dependencies import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.services.payment_gateway import (
    create_payment as create_gateway_payment,
    verify_payment,
)


router = APIRouter()


# =========================================================
# Create Payment Record
# =========================================================

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


# =========================================================
# Request Payment From Gateway
# =========================================================

@router.post("/payments/{order_id}/request")
def request_payment(
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

    if order.status == "paid":
        raise HTTPException(
            status_code=409,
            detail="Order is already paid"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id
    ).first()

    if not payment:
        payment = Payment(
            order_id=order.id,
            amount=order.total_price,
            status="pending"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

    if payment.status == "paid":
        raise HTTPException(
            status_code=409,
            detail="Payment already paid"
        )

    try:
        result = create_gateway_payment(
            amount=int(order.total_price),
            description=f"Order #{order.id}",
            callback_url=settings.payment_callback_url
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Payment gateway error: {str(exc)}"
        )

    if "authority" not in result:
        raise HTTPException(
            status_code=502,
            detail="Payment gateway did not return authority"
        )

    payment.authority = result["authority"]

    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "authority": payment.authority,
        "payment_url": result.get("payment_url"),
        "status": payment.status
    }


# =========================================================
# ZarinPal Callback
# =========================================================

@router.get("/payments/callback")
def payment_callback(
    authority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    if not authority:
        raise HTTPException(
            status_code=400,
            detail="Authority is missing"
        )

    payment = db.query(Payment).filter(
        Payment.authority == authority
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

    if payment.status == "paid":
        return {
            "message": "Payment already verified",
            "payment_id": payment.id,
            "order_id": order.id,
            "status": "paid"
        }

    if status != "OK":
        payment.status = "failed"

        db.commit()

        return {
            "message": "Payment was not completed",
            "payment_id": payment.id,
            "order_id": order.id,
            "status": "failed"
        }

    try:
        result = verify_payment(
            amount=int(payment.amount),
            authority=authority
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Payment verification failed: {str(exc)}"
        )

    data = result.get("data", result)

    code = data.get("code")

    ref_id = (
        data.get("ref_id")
        or data.get("refId")
        or data.get("RefID")
    )

    if code in (100, 101):
        payment.status = "paid"

        if ref_id is not None:
            payment.transaction_id = str(ref_id)

        order.status = "paid"

        db.commit()
        db.refresh(payment)

        return {
            "message": "Payment verified successfully",
            "payment_id": payment.id,
            "order_id": order.id,
            "status": "paid",
            "transaction_id": payment.transaction_id
        }

    payment.status = "failed"

    db.commit()

    return {
        "message": "Payment verification failed",
        "payment_id": payment.id,
        "order_id": order.id,
        "status": "failed",
        "gateway_code": code
    }

@router.post("/payments/user/{username}/request")
def request_payment_for_bot(
    username: str,
    order_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status == "paid":
        raise HTTPException(
            status_code=409,
            detail="Order is already paid"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id
    ).first()

    if not payment:
        payment = Payment(
            order_id=order.id,
            amount=order.total_price,
            status="pending"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

    if payment.status == "paid":
        raise HTTPException(
            status_code=409,
            detail="Payment already paid"
        )

    try:
        result = create_gateway_payment(
            amount=int(payment.amount),
            description=f"Order #{order.id}",
            callback_url=settings.payment_callback_url
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Payment gateway error: {str(exc)}"
        )

    if "authority" not in result:
        raise HTTPException(
            status_code=502,
            detail="Payment gateway did not return authority"
        )

    payment.authority = result["authority"]

    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "authority": payment.authority,
        "payment_url": result.get("payment_url"),
        "status": payment.status
    }