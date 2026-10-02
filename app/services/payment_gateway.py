from zarinpal import ZarinPal
from zarinpal_utils.Config import Config

from app.core.config import settings


config = Config(
    access_token=settings.payment_access_token,
    merchant_id=settings.payment_merchant_id,
    sandbox=True
)

zarinpal = ZarinPal(config)


# =========================================================
# Create Payment
# =========================================================

def create_payment(
    amount: int,
    description: str,
    callback_url: str
):
    result = zarinpal.payments.create({
        "amount": amount,
        "description": description,
        "callback_url": callback_url,
    })

    return result


# =========================================================
# Verify Payment
# =========================================================

def verify_payment(
    amount: int,
    authority: str
):
    result = zarinpal.verifications.verify({
        "amount": amount,
        "authority": authority,
    })

    return result