from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv

class Settings(BaseSettings):
    uvicorn_host: str
    uvicorn_port: int

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra = "allow")

settings = Settings()