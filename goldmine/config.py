from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    default_llm_provider: Literal["openai", "anthropic", "gemini"] = "openai"
    default_llm_model: str = "gpt-4o"
    default_language: str = "English"

    carousel_width: int = 1080
    carousel_height: int = 1080
    carousel_font_size: int = 52

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
