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
    PINECONE_API_KEY: str = os.environ.get("PINECONE_API_KEY")
    GEMINI_AI_KEY: str = os.environ.get("GEMINI_AI_KEY")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
    CLIENT_URL: str = os.environ.get("CLIENT_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    LAMBDA_CHROME_URL: str = os.environ.get("LAMBDA_CHROME_URL")


settings = Settings()