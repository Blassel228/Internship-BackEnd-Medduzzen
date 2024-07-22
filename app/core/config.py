from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv


class Settings(BaseSettings):
    uvicorn_host: str
    uvicorn_port: int

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_password: str
    postgres_user: str

    redis_port: int
    redis_pass: str
    redis_host: str

    cors_origins: list[str] = ["http://127.0.0.1:8000", "http://0.0.0.0:8000"]

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"localhost:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra="allow")

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
