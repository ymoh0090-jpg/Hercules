from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.api.routes.products import router as products_router
from app.database.base import Base
from app.database.database import engine
from app.api.routes.orders import router as orders_router
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.api.routes.cart import router as cart_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Hercules API",
    description="Hercules E-commerce Backend",
    version="1.0.0"
)


app.include_router(health_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)