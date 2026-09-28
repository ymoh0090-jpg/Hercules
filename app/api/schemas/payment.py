from decimal import Decimal

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: str
    transaction_id: str | None

    class Config:
        from_attributes = True