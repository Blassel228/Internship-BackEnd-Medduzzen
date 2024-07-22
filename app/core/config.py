from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv


class Settings(BaseSettings):
    uvicorn_host: str
    uvicorn_port: int

    postgresql_host: str
    postgresql_port: int
    postgresql_database_name: str
    postgresql_password: str
    postgresql_user: str

    redis_host: str
    redis_port: int
    redis_password: str

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"localhost:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra="allow")


settings = Settings()
