from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter()



@router.post("/carts")
def create_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if existing_cart:
        raise HTTPException(
            status_code=409,
            detail="User already has a cart"
        )

    cart = Cart(user_id=current_user.id)

    db.add(cart)
    db.commit()
    db.refresh(cart)

    return cart

@router.post("/carts/{cart_id}/items")
def add_item_to_cart(
    cart_id: int,
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cart = db.query(Cart).filter(
        Cart.id == cart_id
    ).first()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    if cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this cart"
        )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id
    ).first()

    current_quantity = item.quantity if item else 0

    if current_quantity + quantity > product.stock:
        raise HTTPException(
            status_code=409,
            detail="Not enough stock"
        )

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    db.commit()
    db.refresh(item)

    return item
@router.get("/carts/{cart_id}")
def get_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.id == cart_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    if cart.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this cart"
        )

    items = db.query(CartItem).filter(
        CartItem.cart_id == cart_id
    ).all()

    result = []

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            result.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "total": product.price * item.quantity
            })

    return {
        "cart_id": cart.id,
        "items": result
    }