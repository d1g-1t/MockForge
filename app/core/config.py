from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 18765

    redis_url: str = "redis://localhost:26379/0"

    postgres_dsn: str = "postgresql://mockforge:mockforge@localhost:25432/mockforge"

    session_ttl: int = 3600
    record_mode: bool = False
    target_url: str = ""


settings = Settings()
