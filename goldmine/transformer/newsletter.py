from .base import BaseTransformer

SYSTEM_PROMPT = """You are an expert email newsletter writer. You write concise,
valuable newsletter sections that subscribers look forward to reading every week."""

INSTRUCTIONS = """Transform the content into a compelling newsletter section.

Format:
- Subject line (attention-grabbing, not clickbait)
- Preview text (1 sentence, complements subject)
- Body: well-structured with a brief intro, 2–4 key insights with short explanations
- A "Key Takeaway" box (1–2 sentences, the single most actionable insight)
- A closing sentence that teases what's coming next
- Language: {language}

Use markdown formatting. Return ONLY the newsletter section content."""


class NewsletterTransformer(BaseTransformer):
    platform = "Newsletter"
    emoji = "📧"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "word_count": len(result.split()),
        }
