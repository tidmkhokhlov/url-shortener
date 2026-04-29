from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(env_path), case_sensitive=True, extra="ignore")

    DB_HOST: str = "localhost"
    DB_PORT: str = "6432"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: str = "0"
    REDIS_POOL_SIZE: int = 10

    CORS_ORIGINS: list[str] = ["http://localhost:63342"]


settings = Settings()
