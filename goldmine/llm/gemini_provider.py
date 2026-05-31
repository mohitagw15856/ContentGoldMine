import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from .base import BaseLLMProvider
from loguru import logger


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).lower()
    # Don't retry on auth/key errors
    return not any(kw in msg for kw in ("api_key", "api key", "invalid key", "permission", "unauthenticated", "403"))


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self._api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)
        self.model_name = model

    def test_connection(self) -> None:
        """Raises immediately if the API key is invalid."""
        list(genai.list_models())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug(f"Gemini request | model={self.model_name}")
        response = self.model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        return response.text.strip()
