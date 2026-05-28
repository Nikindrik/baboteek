from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Compiler API"
    secret_key: str
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    database_url: str

    model_config = SettingsConfigDict(env_file="app.env")


settings = Settings()  # ty:ignore[missing-argument]
