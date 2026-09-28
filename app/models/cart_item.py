from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_id",
            name="uq_cart_product"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    cart: Mapped["Cart"] = relationship(
        back_populates="items"
    )