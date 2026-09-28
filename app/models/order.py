from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending"
    )