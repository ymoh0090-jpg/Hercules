from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.api.schemas.order import OrderResponse


router = APIRouter()


@router.post(
    "/orders/{user_id}",
    response_model=OrderResponse
)
def create_order(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        cart = db.query(Cart).filter(
            Cart.user_id == user_id
        ).first()

        if not cart:
            raise HTTPException(
                status_code=404,
                detail="Cart not found"
            )

        items = db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).all()

        if not items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        total_price = 0

        for item in items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail="Product not found"
                )

            if item.quantity > product.stock:
                raise HTTPException(
                    status_code=409,
                    detail=f"Not enough stock for {product.name}"
                )

            total_price += product.price * item.quantity

        order = Order(
            user_id=user_id,
            total_price=total_price,
            status="pending"
        )

        db.add(order)
        db.flush()


        for item in items:
            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )

            db.add(order_item)

            product.stock -= item.quantity

            db.delete(item)

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise
@router.get("/orders/{user_id}", response_model=list[OrderResponse])
def get_orders(
    user_id: int,
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).all()

    return orders
@router.get("/orders/{order_id}/details")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        return {"error": "Order not found"}

    items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    result = []

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        result.append({
            "product_id": item.product_id,
            "name": product.name if product else "Unknown",
            "price": item.price,
            "quantity": item.quantity,
            "total": item.price * item.quantity
        })

    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_price": order.total_price,
        "items": result
    }