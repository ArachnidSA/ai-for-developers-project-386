from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения. Значения читаются из окружения и файла .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ai-for-developers-project-386 API"
    # Origins, которым разрешены запросы к API (для CORS).
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
