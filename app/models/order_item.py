from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2)
    )