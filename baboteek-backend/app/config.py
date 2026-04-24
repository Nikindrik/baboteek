from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Compiler API"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Автоматически ищет .env в корне проекта
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()