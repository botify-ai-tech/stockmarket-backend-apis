import random
from google import generativeai as genai
from ..config import settings 


gemini_api_keys = [
    settings.GEMINI_AI_KEY,
    settings.HET_GEMINI_AI_KEY,
    settings.GEMINI_API_KEY_ONE,
    settings.GEMINI_API_KEY_TWO,
    settings.GEMINI_API_KEY_THREE,
    settings.GEMINI_API_KEY_FIVE,
    settings.GEMINI_API_KEY_SEVEN,
    settings.GEMINI_API_KEY_EIGHT,
    settings.GEMINI_API_KEY_NINE,
    settings.GEMINI_API_KEY_TEN,
    settings.GEMINI_API_KEY_ELEVANE,
    settings.GEMINI_API_KEY_TWELVE,
    settings.GEMINI_API_KEY_THIRTEEN,
    settings.GEMINI_API_KEY_FOURTEEN,
    settings.GEMINI_API_KEY_FIFTHTEEN,
    settings.GEMINI_API_KEY_SIXTEEN,
    settings.GEMINI_API_KEY_SEVENTEEN,
    settings.GEMINI_API_KEY_EIGHTTEEN,
    settings.GEMINI_API_KEY_NINETEEN,
    settings.GEMINI_API_KEY_TWENTY
]
def configure_gemini():

    global gemini_api_keys  
    if not gemini_api_keys:
        raise Exception("All API keys have been exhausted! Check quota limits.")

    api_key = random.choice(gemini_api_keys)
    genai.configure(api_key=api_key)
    return api_key


def remove_api_key(api_key):
    """Remove an API key from the list if quota is exceeded."""
    global gemini_api_keys
    if api_key in gemini_api_keys:
        gemini_api_keys.remove(api_key)
        print(f"Removed exhausted API key: {api_key}. Remaining keys: {len(gemini_api_keys)}")
