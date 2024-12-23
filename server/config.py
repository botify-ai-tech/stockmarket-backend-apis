import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import pytz

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
    DHARMIK_GEMINI_AI_KEY: str = os.environ.get("DHARMIK_GEMINI_AI_KEY")
    HARSH_GEMINI_AI_KEY: str = os.environ.get("HARSH_GEMINI_AI_KEY")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
    CLIENT_URL: str = os.environ.get("CLIENT_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    LAMBDA_CHROME_URL: str = os.environ.get("LAMBDA_CHROME_URL")

    FYERS_ID: str = os.environ.get("FYERS_ID")
    TOTP_KEY: str = os.environ.get("TOTP_KEY")
    PIN: str = os.environ.get("PIN")
    CLIENT_ID: str = os.environ.get("CLIENT_ID")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    REDIRECT_URI: str = os.environ.get("REDIRECT_URI")
    ACCESS_TOKEN: str = os.environ.get("ACCESS_TOKEN")
    RESPONSE_TYPE: str = os.environ.get("RESPONSE_TYPE")
    GRANT_TYPE: str = os.environ.get("GRANT_TYPE")
    FYERS_SENT_OTP_URL: str = os.environ.get("FYERS_SENT_OTP_URL")
    FYERS_VERIFY_OTP_URL: str = os.environ.get("FYERS_VERIFY_OTP_URL")
    FYERS_VERIFY_PIN_URL: str = os.environ.get("FYERS_VERIFY_PIN_URL")
    FYERS_TOKEN_URL: str = os.environ.get("FYERS_TOKEN_URL")

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DEFAULT_TIMEZONE: pytz = pytz.timezone("Asia/Kolkata")
    COLUMNS: list = ["date", "open", "high", "low", "close", "volume"]

    GEMINI_API_KEY_ONE: str = os.environ.get("GEMINI_API_KEY_ONE")
    GEMINI_API_KEY_TWO: str = os.environ.get("GEMINI_API_KEY_TWO")
    GEMINI_API_KEY_THREE: str = os.environ.get("GEMINI_API_KEY_THREE")
    GEMINI_API_KEY_FOUR: str = os.environ.get("GEMINI_API_KEY_FOUR")
    GEMINI_API_KEY_FIVE: str = os.environ.get("GEMINI_API_KEY_FIVE")
    GEMINI_API_KEY_SIX: str = os.environ.get("GEMINI_API_KEY_SIX")
    GEMINI_API_KEY_SEVEN: str = os.environ.get("GEMINI_API_KEY_SEVEN")
    GEMINI_API_KEY_EIGHT: str = os.environ.get("GEMINI_API_KEY_EIGHT")


settings = Settings()
