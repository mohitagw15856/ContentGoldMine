from .base import BaseTransformer

SYSTEM_PROMPT = """You are a top LinkedIn content creator with 100K+ followers.
You write posts that feel personal, professional, and insightful — the kind that
get thousands of reactions and shares from professionals."""

INSTRUCTIONS = """Transform the content into a high-performing LinkedIn post.

Rules:
- Open with a bold, curiosity-driven first line (no "I" as the very first word)
- Use short paragraphs (1–3 lines max)
- Tell a story or share a surprising insight
- Include 3–5 key takeaways formatted as bullet points or numbered list
- End with a thought-provoking question to drive comments
- Add 3–5 relevant hashtags at the end
- Ideal length: 800–1300 characters
- Language: {language}

Return ONLY the post text, ready to copy-paste into LinkedIn."""


class LinkedInTransformer(BaseTransformer):
    platform = "LinkedIn Post"
    emoji = "💼"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "char_count": len(result),
        }
