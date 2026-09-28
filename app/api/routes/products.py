from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.product import Product
from app.api.schemas.product import ProductResponse, ProductUpdate



router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return products


@router.post("/products", response_model=ProductResponse)
def create_product(
    name: str,
    price: float,
    stock: int,
    db: Session = Depends(get_db)
):
    product = Product(
        name=name,
        price=price,
        stock=stock
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