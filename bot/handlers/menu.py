from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.services.api_client import (
    get_cart,
    update_cart_item,
    delete_cart_item,
    create_order,
    get_orders,
    request_payment,
    get_user_role,
)


async def menu_callback(
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
    # Buyer: Cart
    # =========================

    if query.data == "cart":
        await show_cart(query, username)
        return

    # =========================
    # Buyer: Orders
    # =========================

    if query.data == "orders":
        try:
            orders = await get_orders(username)

        except Exception:
            await query.message.reply_text(
                "❌ Could not load your orders."
            )
            return

        if not orders:
            await query.message.reply_text(
                "📦 You don't have any orders yet."
            )
            return

        text = "📦 <b>Your Orders</b>\n\n"

        for order in orders:
            text += (
                f"🆔 Order ID: {order['order_id']}\n"
                f"📌 Status: {order['status']}\n"
                f"💰 Total: {order['total_price']}\n"
                "━━━━━━━━━━━━━━\n"
            )

        await query.message.reply_text(
            text,
            parse_mode="HTML"
        )
        return

    # =========================
    # Buyer: Account
    # =========================

    if query.data == "account":
        try:
            role = await get_user_role(username)

        except Exception:
            await query.message.reply_text(
                "❌ Could not load your account."
            )
            return

        await query.message.reply_text(
            "👤 <b>Your Account</b>\n\n"
            f"🔹 Username: @{username}\n"
            f"🔹 Role: {role}",
            parse_mode="HTML"
        )
        return

    await query.message.reply_text(
        "❌ Unknown option"
    )


async def show_cart(
    query,
    username: str
) -> None:
    try:
        cart = await get_cart(username)

    except Exception:
        await query.message.reply_text(
            "❌ Could not load your cart."
        )
        return

    items = cart.get("items", [])

    if not items:
        await query.message.edit_text(
            "🛒 Your cart is empty."
        )
        return

    text = "🛒 <b>Your Cart</b>\n\n"

    keyboard = []

    for item in items:
        text += (
            f"📦 {item['name']}\n"
            f"💰 Price: {item['price']}\n"
            f"🔢 Quantity: {item['quantity']}\n"
            f"💵 Total: {item['total']}\n\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                "➖",
                callback_data=f"cart_dec_{item['product_id']}"
            ),
            InlineKeyboardButton(
                f"{item['quantity']}",
                callback_data="cart_noop"
            ),
            InlineKeyboardButton(
                "➕",
                callback_data=f"cart_inc_{item['product_id']}"
            ),
            InlineKeyboardButton(
                "🗑",
                callback_data=f"cart_del_{item['product_id']}"
            ),
        ])

    text += (
        "━━━━━━━━━━━━━━\n"
        f"💰 <b>Grand Total: {cart['grand_total']}</b>"
    )

    keyboard.append([
        InlineKeyboardButton(
            "✅ Checkout",
            callback_data="checkout"
        )
    ])

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cart_action_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query

    username = update.effective_user.username

    if not username:
        await query.answer(
            "Please set a Telegram username first.",
            show_alert=True
        )
        return

    data = query.data

    if data == "cart_noop":
        await query.answer()
        return

    try:
        parts = data.split("_")
        action = parts[1]
        product_id = int(parts[2])

    except (ValueError, IndexError):
        await query.answer(
            "❌ Invalid cart action.",
            show_alert=True
        )
        return

    try:
        cart = await get_cart(username)

    except Exception:
        await query.answer(
            "❌ Could not load your cart.",
            show_alert=True
        )
        return

    item = next(
        (
            item
            for item in cart.get("items", [])
            if item["product_id"] == product_id
        ),
        None
    )

    if not item:
        await query.answer(
            "❌ Product is not in your cart.",
            show_alert=True
        )
        return

    current_quantity = item["quantity"]

    if action == "inc":
        try:
            await update_cart_item(
                username=username,
                product_id=product_id,
                quantity=current_quantity + 1
            )

        except Exception:
            await query.answer(
                "❌ Not enough stock.",
                show_alert=True
            )
            return

    elif action == "dec":
        if current_quantity == 1:
            await query.answer(
                "Minimum quantity is 1. Use 🗑 to remove it.",
                show_alert=True
            )
            return

        try:
            await update_cart_item(
                username=username,
                product_id=product_id,
                quantity=current_quantity - 1
            )

        except Exception:
            await query.answer(
                "❌ Could not update quantity.",
                show_alert=True
            )
            return

    elif action == "del":
        try:
            await delete_cart_item(
                username=username,
                product_id=product_id
            )

        except Exception:
            await query.answer(
                "❌ Could not remove product.",
                show_alert=True
            )
            return

    await query.answer("✅ Cart updated.")

    await show_cart(query, username)


async def checkout_callback(
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
        order = await create_order(username)

    except Exception:
        await query.message.reply_text(
            "❌ Could not create your order.\n"
            "Please make sure your cart is not empty and try again."
        )
        return

    try:
        payment = await request_payment(
            username=username,
            order_id=order["order_id"]
        )

    except Exception:
        await query.message.edit_text(
            "✅ <b>Order created successfully!</b>\n\n"
            f"🆔 Order ID: <b>{order['order_id']}</b>\n"
            f"💰 Total: <b>{order['total_price']}</b>\n\n"
            "❌ Could not create payment link."
        )
        return

    payment_url = payment.get("payment_url")

    keyboard = []

    if payment_url:
        keyboard.append([
            InlineKeyboardButton(
                "💳 Pay Now",
                url=payment_url
            )
        ])

    await query.message.edit_text(
        "✅ <b>Order created successfully!</b>\n\n"
        f"🆔 Order ID: <b>{order['order_id']}</b>\n"
        f"💰 Total: <b>{order['total_price']}</b>\n\n"
        "💳 Click below to continue payment.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )