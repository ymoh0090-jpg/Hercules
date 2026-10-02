import httpx

from app.core.config import settings


async def get_seller_products(username: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/products/seller/{username}"
        )

        response.raise_for_status()

        return response.json()


async def create_product(
    name: str,
    price: str,
    stock: int,
    username: str
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            f"{settings.api_base_url}/products/seller/{username}",
            json={
                "name": name,
                "price": price,
                "stock": stock
            }
        )

        response.raise_for_status()

        return response.json()


async def get_user_role(username: str) -> str:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/users/role/{username}"
        )

        response.raise_for_status()

        data = response.json()

        return data["role"]


async def update_seller_product(
    username: str,
    product_id: int,
    name: str,
    price: str,
    stock: int
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.put(
            f"{settings.api_base_url}/products/seller/"
            f"{username}/{product_id}",
            json={
                "name": name,
                "price": price,
                "stock": stock
            }
        )

        response.raise_for_status()

        return response.json()

async def get_products() -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/products"
        )

        response.raise_for_status()

        return response.json()


async def delete_seller_product(
    username: str,
    product_id: int
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.delete(
            f"{settings.api_base_url}/products/seller/"
            f"{username}/{product_id}"
        )
        response.raise_for_status()
        return response.json()

async def add_to_cart(
    username: str,
    product_id: int,
    quantity: int = 1
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            f"{settings.api_base_url}/carts/user/"
            f"{username}/items",
            params={
                "product_id": product_id,
                "quantity": quantity
            }
        )
        response.raise_for_status()
        return response.json()


async def get_cart(
    username: str
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/carts/user/"
            f"{username}"
        )
        response.raise_for_status()
        return response.json()


async def update_cart_item(
    username: str,
    product_id: int,
    quantity: int
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.put(
            f"{settings.api_base_url}/carts/user/"
            f"{username}/items/{product_id}",
            params={
                "quantity": quantity
            }
        )
        response.raise_for_status()
        return response.json()


async def delete_cart_item(
    username: str,
    product_id: int
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.delete(
            f"{settings.api_base_url}/carts/user/"
            f"{username}/items/{product_id}"
        )
        response.raise_for_status()
        return response.json()


async def create_order(
    username: str
) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            f"{settings.api_base_url}/orders/user/{username}"
        )
        response.raise_for_status()
        return response.json()


async def get_orders(
    username: str
) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/orders/user/{username}"
        )
        response.raise_for_status()
        return response.json()

async def request_payment(
    username: str,
    order_id: int
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.api_base_url}/payments/user/"
            f"{username}/request",
            params={
                "order_id": order_id
            }
        )
        response.raise_for_status()
        return response.json()


async def get_seller_orders(
    username: str
) -> list[dict]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            f"{settings.api_base_url}/orders/seller/{username}"
        )
        response.raise_for_status()
        return response.json()