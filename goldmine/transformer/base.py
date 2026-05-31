from abc import ABC, abstractmethod
from goldmine.llm.base import BaseLLMProvider


class BaseTransformer(ABC):
    platform: str = ""
    emoji: str = ""

    def __init__(self, llm: BaseLLMProvider, language: str = "English"):
        self.llm = llm
        self.language = language

    @abstractmethod
    def transform(self, content: dict) -> dict:
        """Transform ingested content into platform-specific output."""
        ...

    def _build_prompt(self, content: dict, instructions: str) -> str:
        return (
            f"Title: {content.get('title', 'Untitled')}\n\n"
            f"Content:\n{content['content']}\n\n"
            f"Instructions:\n{instructions}"
        )
