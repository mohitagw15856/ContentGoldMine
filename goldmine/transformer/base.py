from abc import ABC, abstractmethod
from goldmine.llm.base import BaseLLMProvider

TONE_INSTRUCTIONS = {
    "Professional": (
        "Tone: Authoritative and polished. Use precise language and data where available. "
        "No slang, no humor. Sound like a respected industry expert."
    ),
    "Casual & Fun": (
        "Tone: Warm, conversational, and fun. Use contractions and relatable language. "
        "Add light humor where it fits. Sound like a smart, helpful friend — not a brand."
    ),
    "Contrarian": (
        "Tone: Provocative and contrarian. Challenge conventional wisdom. Open with the "
        "unpopular opinion. Make readers stop and question what they thought they knew."
    ),
    "Educational": (
        "Tone: Clear, patient, and structured. Use analogies to simplify complex ideas. "
        "Build logically from basics to insight. Think 'best teacher you ever had'."
    ),
    "Storytelling": (
        "Tone: Frame everything as a story. Open with a vivid scene or specific moment. "
        "Build an emotional arc: problem → discovery → resolution → insight."
    ),
}


class BaseTransformer(ABC):
    platform: str = ""
    emoji: str = ""

    def __init__(
        self,
        llm: BaseLLMProvider,
        language: str = "English",
        tone: str = "Default",
        brand_voice: str = "",
    ):
        self.llm = llm
        self.language = language
        self.tone = tone
        self.brand_voice = brand_voice.strip()

    @abstractmethod
    def transform(self, content: dict) -> dict:
        ...

    def _system_prompt(self, base: str) -> str:
        """Prepend brand voice and append tone instruction to any system prompt."""
        parts = []
        if self.brand_voice:
            parts.append(
                f"BRAND VOICE (apply throughout — this overrides generic style):\n"
                f"{self.brand_voice}\n"
                f"---"
            )
        parts.append(base)
        if self.tone and self.tone != "Default":
            parts.append(f"\n{TONE_INSTRUCTIONS[self.tone]}")
        return "\n\n".join(parts)

    def _build_prompt(self, content: dict, instructions: str) -> str:
        return (
            f"Title: {content.get('title', 'Untitled')}\n\n"
            f"Content:\n{content['content']}\n\n"
            f"Instructions:\n{instructions}"
        )
