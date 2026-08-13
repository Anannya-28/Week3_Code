from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:Nannya%40sql@localhost:5432/CaseStudy1"
    )
    ASYNC_DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:Nannya%40sql@localhost:5432/CaseStudy1"
    )

    # JWT
    SECRET_KEY: str = "c33f0982ab3edd21048f630fb26d317b13b6bce1be18b801c0e3eb1418aea0dc"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External integrations
    PAYMENT_GATEWAY_URL: str = "https://api.fake-payment.example.com"
    SHIPPING_API_URL: str = "https://api.fake-shipping.example.com"
    NOTIFICATION_API_URL: str = "https://api.fake-notify.example.com"

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()