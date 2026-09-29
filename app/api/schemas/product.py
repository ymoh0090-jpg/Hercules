from decimal import Decimal

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: Decimal
    stock: int


class ProductUpdate(BaseModel):
    name: str
    price: Decimal
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int

    class Config:
        from_attributes = True