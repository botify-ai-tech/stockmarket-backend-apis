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
    DHARMIK_GEMINI_AI_KEY: str = os.environ.get("DHARMIK_GEMINI_AI_KEY")
    HARSH_GEMINI_AI_KEY: str = os.environ.get("HARSH_GEMINI_AI_KEY")
    HET_GEMINI_AI_KEY : str = os.environ.get("HET_GEMINI_AI_KEY")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
    CLIENT_URL: str = os.environ.get("CLIENT_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    LAMBDA_CHROME_URL: str = os.environ.get("LAMBDA_CHROME_URL")

    GEMINI_API_KEY_ONE : str = os.environ.get("GEMINI_API_KEY_ONE")
    GEMINI_API_KEY_TWO : str = os.environ.get("GEMINI_API_KEY_TWO")
    GEMINI_API_KEY_THREE : str = os.environ.get("GEMINI_API_KEY_THREE")
    GEMINI_API_KEY_FIVE : str = os.environ.get("GEMINI_API_KEY_FIVE")
    # GEMINI_API_KEY_SIX : str = os.environ.get("GEMINI_API_KEY_SIX")
    GEMINI_API_KEY_SEVEN : str = os.environ.get("GEMINI_API_KEY_SEVEN")
    GEMINI_API_KEY_EIGHT : str = os.environ.get("GEMINI_API_KEY_EIGHT")
    GEMINI_API_KEY_NINE : str = os.environ.get("GEMINI_API_KEY_NINE")
    GEMINI_API_KEY_TEN : str = os.environ.get("GEMINI_API_KEY_TEN")
    GEMINI_API_KEY_ELEVANE : str = os.environ.get("GEMINI_API_KEY_ELEVANE")
    GEMINI_API_KEY_TWELVE : str = os.environ.get("GEMINI_API_KEY_TWELVE")
    GEMINI_API_KEY_THIRTEEN : str = os.environ.get("GEMINI_API_KEY_THIRTEEN")
    GEMINI_API_KEY_FOURTEEN : str = os.environ.get("GEMINI_API_KEY_FOURTEEN")
    GEMINI_API_KEY_FIFTHTEEN : str = os.environ.get("GEMINI_API_KEY_FIFTHTEEN")
    GEMINI_API_KEY_SIXTEEN : str = os.environ.get("GEMINI_API_KEY_SIXTEEN")
    GEMINI_API_KEY_SEVENTEEN : str = os.environ.get("GEMINI_API_KEY_SEVENTEEN")
    GEMINI_API_KEY_EIGHTTEEN : str = os.environ.get("GEMINI_API_KEY_EIGHTTEEN")
    GEMINI_API_KEY_NINETEEN : str = os.environ.get("GEMINI_API_KEY_NINETEEN")
    GEMINI_API_KEY_TWENTY : str = os.environ.get("GEMINI_API_KEY_TWENTY")
 


settings = Settings()