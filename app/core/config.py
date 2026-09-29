from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    jwt_secret_key: str
    payment_merchant_id: str
    payment_callback_url: str
    payment_access_token: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"

    )


settings = Settings()