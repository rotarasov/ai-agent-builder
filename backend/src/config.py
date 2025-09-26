import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    base_api_url: str = os.getenv("BASE_API_URL", "http://localhost:8000")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "<openai_api_key>")
    swiss_ai_platform_api_key: str = os.getenv("SWISS_AI_PLATFORM_API_KEY", "<swiss_ai_platform_api_key>")
    swiss_ai_platform_base_url: str = os.getenv("SWISS_AI_PLATFORM_BASE_URL", "https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1")
    leapcell_api_key: str = os.getenv("LEAPCELL_API_KEY", "<leapcell_api_key>")
    composio_api_key: str = os.getenv("COMPOSIO_API_KEY", "<composio_api_key>")

config = Config()