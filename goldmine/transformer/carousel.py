import json
import re
from .base import BaseTransformer

SYSTEM_PROMPT = """You are an Instagram carousel creator who designs scroll-stopping
educational carousels. Each slide must be punchy, visual-friendly, and make viewers
swipe to the next one."""

INSTRUCTIONS = """Transform the content into an Instagram carousel (8–12 slides).

Return a JSON array only. Each element:
{{
  "slide": <number>,
  "headline": "<bold headline, max 8 words>",
  "body": "<supporting text, max 30 words>",
  "emoji": "<1-2 relevant emojis>"
}}

Rules:
- Slide 1: Hook slide — make them stop scrolling
- Slides 2–(n-1): One key insight per slide
- Last slide: CTA — follow/save/share
- Language: {language}

Return ONLY valid JSON array, no markdown fences."""


class CarouselTransformer(BaseTransformer):
    platform = "Instagram Carousel"
    emoji = "🎠"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        slides = self._parse_slides(result)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "slides": slides,
            "slide_count": len(slides),
        }

    def _parse_slides(self, raw: str) -> list[dict]:
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Best-effort extraction of individual slide objects
            objects = re.findall(r"\{[^{}]+\}", cleaned, re.DOTALL)
            slides = []
            for obj in objects:
                try:
                    slides.append(json.loads(obj))
                except json.JSONDecodeError:
                    continue
            return slides
