# 🏛 Hercules

A full-stack Telegram e-commerce project built with **Python, FastAPI, SQLAlchemy, and python-telegram-bot**.

Hercules provides a Telegram-based shopping experience for buyers and product management tools for sellers, backed by a FastAPI REST API and a relational database.

## ✨ Features

### 🛍️ Buyer

* Browse available products
* Add products to cart
* Increase or decrease item quantity
* Remove products from cart
* View cart and total price
* Create orders from cart
* View order history
* View account information and role
* Start the payment process through ZarinPal

### 👨‍💼 Seller

* Add products
* View own products
* Edit products
* Delete products
* View orders containing the seller's products
* View seller-specific order totals

### 💳 Payment

* Payment record management
* ZarinPal payment request
* Payment authority storage
* Payment callback endpoint
* Payment verification
* Order status update after successful verification

## 🏗 Architecture

```text
                    Hercules
                        │
          ┌─────────────┴─────────────┐
          │                           │
    Telegram Bot                 FastAPI API
          │                           │
          │                     ┌─────┴─────┐
          │                     │           │
          │                  Database    Payment
          │                     │           │
          └─────────────────────┴───────────┘
```

### Main flow

```text
Buyer
  ↓
Products
  ↓
Cart
  ↓
Checkout
  ↓
Order
  ↓
Payment
  ↓
ZarinPal
  ↓
Callback
  ↓
Verify
  ↓
Order = paid
```

## 🛠 Tech Stack

* Python 3.13
* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* Pydantic Settings
* Python Dotenv
* HTTPX
* PyJWT
* pwdlib
* python-telegram-bot
* ZarinPal Python SDK
* Pytest

## 📁 Project Structure

```text
Hercules/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   ├── orders.py
│   │   │   └── payments.py
│   │   │
│   │   └── schemas/
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── cart_item.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── payment.py
│   │
│   └── services/
│       └── payment_gateway.py
│
├── bot/
│   ├── handlers/
│   │   ├── start.py
│   │   ├── menu.py
│   │   ├── products.py
│   │   └── seller.py
│   │
│   ├── services/
│   │   └── api_client.py
│   │
│   └── main.py
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

Create a `.env` file in the project root.

```env
BOT_TOKEN=your_telegram_bot_token

DATABASE_URL=your_database_url

JWT_SECRET_KEY=your_jwt_secret

PAYMENT_MERCHANT_ID=your_merchant_id
PAYMENT_ACCESS_TOKEN=your_access_token
PAYMENT_CALLBACK_URL=https://your-public-domain/payments/callback

API_BASE_URL=http://127.0.0.1:8000
```

Do **not** commit `.env` or secret credentials to GitHub.

## 🚀 Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd Hercules
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run the FastAPI Backend

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 🤖 Run the Telegram Bot

In another terminal:

```bash
python -m bot.main
```

## 💳 Payment Callback

For local development, the payment callback must be reachable from the internet.

Example:

```text
https://your-public-domain/payments/callback
```

A temporary tunneling service can be used during development.

For production, use a stable public HTTPS endpoint.

## 🔐 Security Notes

* Keep `.env` out of version control.
* Never publish Telegram bot tokens.
* Never publish JWT secrets.
* Never publish payment credentials.
* Payment status should only be changed to `paid` after gateway verification.
* Bot-facing endpoints should be protected appropriately before production deployment.

## 🧪 Testing

Tests can be executed with:

```bash
pytest
```

## 📌 Project Status

Hercules is a portfolio-focused e-commerce project demonstrating:

* REST API development with FastAPI
* Database modeling with SQLAlchemy
* JWT authentication
* Telegram bot development
* Buyer and seller workflows
* Cart and order management
* Payment gateway integration
* API and bot architecture

## 📈 Future Improvements

Possible future improvements include:

* Docker deployment
* Production database configuration
* Better authentication between the Telegram bot and API
* Advanced order status management
* Seller dashboard
* Admin panel
* Automated tests
* Improved payment and webhook handling
* Production deployment

## 👨‍💻 Author

Built as a Python portfolio project focused on backend development, APIs, databases, Telegram bots, and payment integration.
