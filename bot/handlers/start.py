from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.main import buyer_menu, seller_menu
from bot.services.api_client import get_user_role


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:

    user = update.effective_user

    username = user.username

    if not username:
        await update.message.reply_text(
            "❌ Your Telegram account must have a username."
        )
        return

    try:
        role = await get_user_role(username)

    except Exception:
        role = "buyer"

    if role == "seller":
        await update.message.reply_text(
            "🏪 Welcome to Hercules Seller Panel!\n\n"
            "Choose an option:",
            reply_markup=seller_menu()
        )

    else:
        await update.message.reply_text(
            "🛍 Welcome to Hercules Store!\n\n"
            "Choose an option:",
            reply_markup=buyer_menu()
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        "📋 Commands:\n"
        "/start - Open Hercules\n"
        "/help - Show help"
    )