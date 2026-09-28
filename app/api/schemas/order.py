from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)