from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.api.schemas.order import OrderResponse
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter()


# =========================================================
# Create Order - JWT
# =========================================================

@router.post("/orders")
def create_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        cart = db.query(Cart).filter(
            Cart.user_id == current_user.id
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
            user_id=current_user.id,
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


# =========================================================
# Get Orders - JWT
# =========================================================

@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()

    return orders


# =========================================================
# Order Details - JWT
# =========================================================

@router.get("/orders/{order_id}/details")
def get_order_details(
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


# =========================================================
# Create Order - Telegram Bot
# =========================================================

@router.post("/orders/user/{username}")
def create_order_for_bot(
    username: str,
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

    cart = db.query(Cart).filter(
        Cart.user_id == user.id
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
        user_id=user.id,
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

    return {
        "order_id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_price": order.total_price
    }


# =========================================================
# Get Orders - Telegram Bot
# =========================================================

@router.get("/orders/user/{username}")
def get_orders_for_bot(
    username: str,
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

    orders = db.query(Order).filter(
        Order.user_id == user.id
    ).all()

    return [
        {
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price
        }
        for order in orders
    ]

@router.get("/orders/seller/{username}")
def get_seller_orders_for_bot(
    username: str,
    db: Session = Depends(get_db)
):
    seller = db.query(User).filter(
        User.username == username
    ).first()

    if not seller:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if seller.role != "seller":
        raise HTTPException(
            status_code=403,
            detail="User is not a seller"
        )

    seller_items = (
        db.query(OrderItem, Order, Product)
        .join(Order, Order.id == OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.seller_id == seller.id)
        .all()
    )

    orders = {}

    for order_item, order, product in seller_items:
        if order.id not in orders:
            orders[order.id] = {
                "order_id": order.id,
                "buyer_id": order.user_id,
                "status": order.status,
                "seller_total": 0,
                "items": []
            }

        item_total = order_item.price * order_item.quantity

        orders[order.id]["seller_total"] += item_total

        orders[order.id]["items"].append({
            "product_id": product.id,
            "name": product.name,
            "price": order_item.price,
            "quantity": order_item.quantity,
            "total": item_total
        })

    return list(orders.values())