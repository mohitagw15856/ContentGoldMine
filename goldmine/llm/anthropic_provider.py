import anthropic
from anthropic import AuthenticationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type
from .base import BaseLLMProvider
from loguru import logger

_NO_RETRY = (AuthenticationError,)


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
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
        logger.debug(f"Anthropic request | model={self.model}")
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text.strip()
