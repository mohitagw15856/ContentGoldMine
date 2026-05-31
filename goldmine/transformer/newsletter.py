from .base import BaseTransformer

SYSTEM_PROMPT = """You write newsletter sections that people actually read instead of archiving.
You know that subscribers open newsletters for insight they can't get elsewhere —
so you surface the non-obvious angle, add context, and make the reader feel smarter."""

INSTRUCTIONS = """Transform the content into a compelling newsletter section. Use this structure:

SUBJECT LINE: (attention-grabbing, creates curiosity without being clickbait)
PREVIEW TEXT: (1 sentence that complements the subject, shown in inbox preview)

---

OPENING (2–3 lines):
- Don't recap the content — open with WHY this matters right now
- Make the reader feel this was written specifically for them

THE INSIGHT (main body, 200–300 words):
- Surface the sharpest, most non-obvious takeaway from the content
- Add at least one specific example, data point, or analogy that makes it stick
- Write in a warm, smart, direct voice — like a well-read friend explaining something
- Use short paragraphs. Vary sentence length.

> KEY TAKEAWAY (blockquote style):
> One sentence. The single most actionable or memorable thing from this section.

WHAT THIS MEANS FOR YOU (2–4 bullet points):
- Each bullet = one concrete action or shift in thinking
- Be specific. "Think about your strategy" is not useful. "Audit your X before doing Y" is.

CLOSING QUESTION or TEASER (1–2 lines):
- Either ask the reader a question that makes them reflect
- Or tease the next section/issue with specific intrigue

Language: {language}

Return the full newsletter section in markdown format. Include the subject line and preview text at the top."""


class NewsletterTransformer(BaseTransformer):
    platform = "Newsletter"
    emoji = "📧"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(self._system_prompt(SYSTEM_PROMPT), user_prompt)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "word_count": len(result.split()),
        }
