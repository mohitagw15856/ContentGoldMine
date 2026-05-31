import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import BaseLLMProvider
from loguru import logger


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=None,
        )
        self.model_name = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug(f"Gemini request | model={self.model_name}")
        combined = f"{system_prompt}\n\n{user_prompt}"
        response = self.model.generate_content(combined)
        return response.text.strip()
