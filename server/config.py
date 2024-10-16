import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    
    debug: bool = os.environ.get("DEBUG")
    FASTAPI_CONFIG: str = os.environ.get("FASTAPI_CONFIG")
    AUTH_TOKEN: str = os.environ.get("AUTH_TOKEN")
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM: str = os.environ.get("MAIL_FROM")
    MAIL_PORT: str = os.environ.get("MAIL_PORT")
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER")

settings = Settings()