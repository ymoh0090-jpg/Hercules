from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from bot.services.api_client import (
    create_product,
    get_user_role,
    get_seller_products,
    update_seller_product,
    delete_seller_product,
    get_seller_orders,
)


PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_STOCK = range(3)

EDIT_PRODUCT_ID, EDIT_PRODUCT_NAME, EDIT_PRODUCT_PRICE, EDIT_PRODUCT_STOCK = range(3, 7)

DELETE_PRODUCT_ID = 7


# =========================================================
# Add Product
# =========================================================

async def start_add_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    if not user.username:
        await query.message.reply_text(
            "❌ Please set a Telegram username first."
        )
        return ConversationHandler.END

    try:
        role = await get_user_role(user.username)

    except Exception:
        await query.message.reply_text(
            "❌ Could not verify your account."
        )
        return ConversationHandler.END

    if role != "seller":
        await query.message.reply_text(
            "❌ This section is only available to sellers."
        )
        return ConversationHandler.END

    await query.message.reply_text(
        "➕ Add Product\n\n"
        "Enter product name:"
    )

    return PRODUCT_NAME


async def get_product_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(
            "❌ Product name cannot be empty."
        )
        return PRODUCT_NAME

    context.user_data["product_name"] = name

    await update.message.reply_text(
        "💰 Enter product price:"
    )

    return PRODUCT_PRICE


async def get_product_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    price = update.message.text.strip()

    try:
        float(price)

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid price.\n"
            "Enter a number, for example: 2500"
        )
        return PRODUCT_PRICE

    context.user_data["product_price"] = price

    await update.message.reply_text(
        "📦 Enter stock quantity:"
    )

    return PRODUCT_STOCK


async def get_product_stock(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    stock = update.message.text.strip()

    if not stock.isdigit():
        await update.message.reply_text(
            "❌ Invalid stock.\n"
            "Enter a whole number, for example: 20"
        )
        return PRODUCT_STOCK

    try:
        product = await create_product(
            name=context.user_data["product_name"],
            price=context.user_data["product_price"],
            stock=int(stock),
            username=update.effective_user.username
        )

    except Exception:
        await update.message.reply_text(
            "❌ Could not create product."
        )
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ Product added successfully!\n\n"
        f"🆔 ID: {product['id']}\n"
        f"📦 Name: {product['name']}\n"
        f"💰 Price: {product['price']}\n"
        f"🔢 Stock: {product['stock']}"
    )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel_add_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Adding product cancelled."
    )

    return ConversationHandler.END


# =========================================================
# Seller Menu
# =========================================================

async def seller_menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    username = update.effective_user.username

    if not username:
        await query.message.reply_text(
            "❌ Please set a Telegram username first."
        )
        return

    # =========================
    # My Products
    # =========================

    if query.data == "seller_products":
        try:
            products = await get_seller_products(username)

        except Exception:
            await query.message.reply_text(
                "❌ Could not load your products."
            )
            return

        if not products:
            await query.message.reply_text(
                "📦 You have no products yet."
            )
            return

        text = "📦 <b>My Products</b>\n\n"

        for product in products:
            text += (
                f"🆔 <b>{product['id']}</b>\n"
                f"📦 {product['name']}\n"
                f"💰 {product['price']}\n"
                f"🔢 Stock: {product['stock']}\n\n"
            )

        await query.message.reply_text(
            text,
            parse_mode="HTML"
        )

        return

    # =========================
    # Seller Orders
    # =========================

    if query.data == "seller_orders":
        try:
            orders = await get_seller_orders(username)

        except Exception:
            await query.message.reply_text(
                "❌ Could not load your orders."
            )
            return

        if not orders:
            await query.message.reply_text(
                "📋 You don't have any orders yet."
            )
            return

        text = "📋 <b>Seller Orders</b>\n\n"

        for order in orders:
            text += (
                f"🆔 <b>Order #{order['order_id']}</b>\n"
                f"👤 Buyer ID: {order['buyer_id']}\n"
                f"📌 Status: {order['status']}\n"
                f"💰 Your Total: {order['seller_total']}\n\n"
            )

            for item in order["items"]:
                text += (
                    f"📦 {item['name']}\n"
                    f"   Quantity: {item['quantity']}\n"
                    f"   Price: {item['price']}\n"
                    f"   Total: {item['total']}\n"
                )

            text += "\n━━━━━━━━━━━━━━\n\n"

        await query.message.reply_text(
            text,
            parse_mode="HTML"
        )

        return

    # =========================
    # Other Seller Buttons
    # =========================

    messages = {
        "seller_edit_product": "✏️ Edit Product",
        "seller_delete_product": "🗑 Delete Product",
    }

    message = messages.get(
        query.data,
        "❌ Unknown option"
    )

    await query.message.reply_text(message)


# =========================================================
# Edit Product
# =========================================================

async def start_edit_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    username = update.effective_user.username

    if not username:
        await query.message.reply_text(
            "❌ Please set a Telegram username first."
        )
        return ConversationHandler.END

    try:
        products = await get_seller_products(username)

    except Exception:
        await query.message.reply_text(
            "❌ Could not load your products."
        )
        return ConversationHandler.END

    if not products:
        await query.message.reply_text(
            "📦 You have no products to edit."
        )
        return ConversationHandler.END

    text = "✏️ Enter the Product ID you want to edit:\n\n"

    for product in products:
        text += (
            f"🆔 {product['id']} | "
            f"{product['name']} | "
            f"{product['price']} | "
            f"Stock: {product['stock']}\n"
        )

    await query.message.reply_text(text)

    return EDIT_PRODUCT_ID


async def get_edit_product_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    product_id = update.message.text.strip()

    if not product_id.isdigit():
        await update.message.reply_text(
            "❌ Product ID must be a number."
        )
        return EDIT_PRODUCT_ID

    username = update.effective_user.username

    try:
        products = await get_seller_products(username)

    except Exception:
        await update.message.reply_text(
            "❌ Could not load your products."
        )
        return ConversationHandler.END

    product = next(
        (
            item for item in products
            if item["id"] == int(product_id)
        ),
        None
    )

    if not product:
        await update.message.reply_text(
            "❌ Product not found in your products."
        )
        return EDIT_PRODUCT_ID

    context.user_data["edit_product_id"] = int(product_id)

    await update.message.reply_text(
        f"Current name: {product['name']}\n\n"
        "Enter new product name:"
    )

    return EDIT_PRODUCT_NAME


async def get_edit_product_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(
            "❌ Product name cannot be empty."
        )
        return EDIT_PRODUCT_NAME

    context.user_data["edit_product_name"] = name

    await update.message.reply_text(
        "💰 Enter new price:"
    )

    return EDIT_PRODUCT_PRICE


async def get_edit_product_price(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    price = update.message.text.strip()

    try:
        float(price)

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid price."
        )
        return EDIT_PRODUCT_PRICE

    context.user_data["edit_product_price"] = price

    await update.message.reply_text(
        "📦 Enter new stock:"
    )

    return EDIT_PRODUCT_STOCK


async def get_edit_product_stock(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    stock = update.message.text.strip()

    if not stock.isdigit():
        await update.message.reply_text(
            "❌ Stock must be a whole number."
        )
        return EDIT_PRODUCT_STOCK

    username = update.effective_user.username

    try:
        product = await update_seller_product(
            username=username,
            product_id=context.user_data["edit_product_id"],
            name=context.user_data["edit_product_name"],
            price=context.user_data["edit_product_price"],
            stock=int(stock)
        )

    except Exception:
        await update.message.reply_text(
            "❌ Could not update product."
        )
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ Product updated successfully!\n\n"
        f"🆔 ID: {product['id']}\n"
        f"📦 Name: {product['name']}\n"
        f"💰 Price: {product['price']}\n"
        f"🔢 Stock: {product['stock']}"
    )

    context.user_data.clear()

    return ConversationHandler.END


# =========================================================
# Delete Product
# =========================================================

async def start_delete_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    if not user.username:
        await query.message.reply_text(
            "❌ Please set a Telegram username first."
        )
        return ConversationHandler.END

    role = await get_user_role(user.username)

    if role != "seller":
        await query.message.reply_text(
            "⛔ Only sellers can delete products."
        )
        return ConversationHandler.END

    products = await get_seller_products(user.username)

    if not products:
        await query.message.reply_text(
            "📦 You don't have any products."
        )
        return ConversationHandler.END

    message = "🗑 Products you can delete:\n\n"

    for product in products:
        message += (
            f"🆔 {product['id']} | "
            f"{product['name']} | "
            f"{product['price']}\n"
        )

    message += "\n✏️ Enter the product ID you want to delete:"

    await query.message.reply_text(message)

    return DELETE_PRODUCT_ID


async def get_delete_product_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    user = update.effective_user

    try:
        product_id = int(update.message.text)

    except ValueError:
        await update.message.reply_text(
            "❌ Product ID must be a number."
        )
        return DELETE_PRODUCT_ID

    if not user.username:
        await update.message.reply_text(
            "❌ Please set a Telegram username first."
        )
        return ConversationHandler.END

    try:
        await delete_seller_product(
            user.username,
            product_id
        )

        await update.message.reply_text(
            "✅ Product deleted successfully.\n\n"
            f"🆔 Product ID: {product_id}"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Product not found or you don't have permission to delete it."
        )

    return ConversationHandler.END


async def cancel_delete_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "❌ Delete operation cancelled."
    )

    return ConversationHandler.END