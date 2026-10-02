import os

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.handlers.start import start, help_command
from bot.handlers.menu import (
    menu_callback,
    cart_action_callback,
)
from bot.handlers.menu import (
    menu_callback,
    cart_action_callback,
    checkout_callback,
)

from bot.handlers.seller import (
    start_add_product,
    get_product_name,
    get_product_price,
    get_product_stock,
    cancel_add_product,
    seller_menu_callback,

    start_edit_product,
    get_edit_product_id,
    get_edit_product_name,
    get_edit_product_price,
    get_edit_product_stock,

    start_delete_product,
    get_delete_product_id,
    cancel_delete_product,

    PRODUCT_NAME,
    PRODUCT_PRICE,
    PRODUCT_STOCK,

    EDIT_PRODUCT_ID,
    EDIT_PRODUCT_NAME,
    EDIT_PRODUCT_PRICE,
    EDIT_PRODUCT_STOCK,

    DELETE_PRODUCT_ID,
)


load_dotenv()


TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TOKEN")
)


if not TOKEN:
    raise ValueError(
        "Telegram bot token not found. "
        "Set BOT_TOKEN in your .env file."
    )


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # =========================
    # Basic Commands
    # =========================

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    # =========================
    # Buyer: Products
    # =========================

    app.add_handler(
        CallbackQueryHandler(
            products_callback,
            pattern="^products$"
        )
    )

    # =========================
    # Buyer: Cart / Orders / Account
    # =========================

    app.add_handler(
        CallbackQueryHandler(
            menu_callback,
            pattern="^(cart|orders|account)$"
        )
    )

    # =========================
    # Seller: Add Product
    # =========================

    add_product_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_add_product,
                pattern="^seller_add_product$"
            )
        ],
        states={
            PRODUCT_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_product_name
                )
            ],
            PRODUCT_PRICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_product_price
                )
            ],
            PRODUCT_STOCK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_product_stock
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_add_product
            )
        ],
    )

    app.add_handler(add_product_conversation)

    # =========================
    # Seller: Edit Product
    # =========================

    edit_product_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_edit_product,
                pattern="^seller_edit_product$"
            )
        ],
        states={
            EDIT_PRODUCT_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_edit_product_id
                )
            ],
            EDIT_PRODUCT_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_edit_product_name
                )
            ],
            EDIT_PRODUCT_PRICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_edit_product_price
                )
            ],
            EDIT_PRODUCT_STOCK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_edit_product_stock
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_add_product
            )
        ],
    )

    app.add_handler(edit_product_conversation)

    # =========================
    # Seller: Delete Product
    # =========================

    delete_product_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_delete_product,
                pattern="^seller_delete_product$"
            )
        ],
        states={
            DELETE_PRODUCT_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_delete_product_id
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_delete_product
            )
        ],
    )

    app.add_handler(delete_product_conversation)

    # =========================
    # Seller: Other Menu Buttons
    # =========================

    app.add_handler(
        CallbackQueryHandler(
            seller_menu_callback,
            pattern="^(seller_products|seller_orders)$"
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            add_to_cart_callback,
            pattern="^add_cart_[0-9]+$"
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            cart_action_callback,
            pattern="^cart_(inc|dec|del)_[0-9]+$|^cart_noop$"
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            checkout_callback,
            pattern="^checkout$"
        )
    )
    # =========================
    # Start Bot
    # =========================

    app.run_polling()


if __name__ == "__main__":
    main()