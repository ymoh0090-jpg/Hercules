from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.dependencies import get_db
from app.models.product import Product
from app.api.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate
)


router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db)
):
    products = db.query(Product).all()

    return products


@router.post("/products", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db)
):
    product = Product(
        name=data.name,
        price=data.price,
        stock=data.stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.name = data.name
    product.price = data.price
    product.stock = data.stock

    db.commit()
    db.refresh(product)

    return product


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }
@router.post(
    "/products/seller/{username}",
    response_model=ProductResponse
)
def create_seller_product(
    username: str,
    data: ProductCreate,
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

    product = Product(
        name=data.name,
        price=data.price,
        stock=data.stock,
        seller_id=seller.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

@router.get(
    "/products/seller/{username}",
    response_model=list[ProductResponse]
)
def get_seller_products(
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

    return db.query(Product).filter(
        Product.seller_id == seller.id
    ).all()
@router.put(
    "/products/seller/{username}/{product_id}",
    response_model=ProductResponse
)
def update_seller_product(
    username: str,
    product_id: int,
    data: ProductUpdate,
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

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == seller.id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or does not belong to seller"
        )

    product.name = data.name
    product.price = data.price
    product.stock = data.stock

    db.commit()
    db.refresh(product)

    return product