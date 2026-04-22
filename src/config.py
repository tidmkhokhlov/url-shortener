from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(env_path), case_sensitive=True, extra="ignore")

    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    CORS_ORIGINS: list[str] = ["http://localhost:63342"]


settings = Settings()
