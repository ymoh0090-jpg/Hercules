from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.api_client import (
    get_products,
    add_to_cart,
)


async def products_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query

    await query.answer()

    try:
        products = await get_products()

    except Exception:
        await query.message.edit_text(
            "❌ Could not connect to Hercules API."
        )
        return

    if not products:
        await query.message.edit_text(
            "🛍 No products available."
        )
        return

    text = "🛍 <b>Hercules Products</b>\n\n"

    keyboard = []

    for product in products:
        text += (
            f"🆔 <b>{product['id']}</b>\n"
            f"📦 {product['name']}\n"
            f"💰 {product['price']}\n"
            f"🔢 Stock: {product['stock']}\n\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                f"➕ Add {product['name']}",
                callback_data=f"add_cart_{product['id']}"
            )
        ])

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_to_cart_callback(
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

    try:
        product_id = int(query.data.replace("add_cart_", ""))

    except ValueError:
        await query.message.reply_text(
            "❌ Invalid product."
        )
        return

    try:
        item = await add_to_cart(
            username=username,
            product_id=product_id,
            quantity=1
        )

    except Exception:
        await query.message.reply_text(
            "❌ Could not add product to cart."
        )
        return

    await query.message.reply_text(
        f"✅ Product added to cart!\n\n"
        f"🆔 Product ID: {item['product_id']}\n"
        f"🔢 Quantity: {item['quantity']}"
    )