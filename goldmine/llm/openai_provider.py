from openai import OpenAI, AuthenticationError, PermissionDeniedError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type
from .base import BaseLLMProvider
from loguru import logger

_NO_RETRY = (AuthenticationError, PermissionDeniedError)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def test_connection(self) -> None:
        """Raises immediately if the API key is invalid."""
        self.client.models.list()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type(_NO_RETRY),
        reraise=True,
    )
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        logger.debug(f"OpenAI request | model={self.model}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
