from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send a prompt and return the text response."""
        ...
