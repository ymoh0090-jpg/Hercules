from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str
    price: Decimal
    stock: int