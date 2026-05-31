from .base import BaseTransformer

SYSTEM_PROMPT = """You are a viral short-form video scriptwriter for TikTok, YouTube
Shorts, and Instagram Reels. You write scripts that hook viewers in the first 3
seconds and keep them watching until the end."""

INSTRUCTIONS = """Transform the content into a short-form video script (45–90 seconds).

Format:
[HOOK] (0–3 sec): The opening line that grabs attention immediately
[BODY] (3–75 sec): 4–6 punchy points, each 1–2 sentences
[CTA] (last 5 sec): Clear call to action

Rules:
- Write for spoken delivery — natural, conversational, energetic
- Add [PAUSE] or [EMPHASIS] stage directions where useful
- Estimate reading time at ~130 words per minute
- Language: {language}

Return ONLY the formatted script."""


class VideoScriptTransformer(BaseTransformer):
    platform = "Video Script"
    emoji = "🎬"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        word_count = len(result.split())
        estimated_seconds = int((word_count / 130) * 60)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "word_count": word_count,
            "estimated_duration_sec": estimated_seconds,
        }
