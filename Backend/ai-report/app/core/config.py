from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_EXPIRES: int = 60 * 60 * 8 
    DB_URL: str = "sqlite+aiosqlite:///./dev.db"
    LOCAL_STORAGE_DIR: str = str(Path("./data/files").resolve())  # ★추가★


    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Campus Report System"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False


    class Config:
        env_file = ".env"

settings = Settings()
