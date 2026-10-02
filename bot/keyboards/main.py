from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def buyer_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                "🛍 Products",
                callback_data="products"
            ),
            InlineKeyboardButton(
                "🛒 Cart",
                callback_data="cart"
            ),
        ],
        [
            InlineKeyboardButton(
                "📦 Orders",
                callback_data="orders"
            ),
            InlineKeyboardButton(
                "👤 Account",
                callback_data="account"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def seller_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add Product",
                callback_data="seller_add_product"
            ),
        ],
        [
            InlineKeyboardButton(
                "📦 My Products",
                callback_data="seller_products"
            ),
        ],
        [
            InlineKeyboardButton(
                "✏️ Edit Product",
                callback_data="seller_edit_product"
            ),
            InlineKeyboardButton(
                "🗑 Delete Product",
                callback_data="seller_delete_product"
            ),
        ],
        [
            InlineKeyboardButton(
                "📋 Orders",
                callback_data="seller_orders"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)