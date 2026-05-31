import json
import re
from .base import BaseTransformer

SYSTEM_PROMPT = """You create Instagram carousels that people screenshot and save.
Every slide must earn its place — if someone can swipe past it without missing anything, cut it.
You know that carousels live or die on the first slide (stops the scroll) and the last (drives action)."""

INSTRUCTIONS = """Transform the content into a high-performing Instagram carousel (8–10 slides).

Return a JSON array. Each element must follow this exact schema:
{{
  "slide": <number>,
  "type": "hook" | "insight" | "cta",
  "headline": "<punchy headline, MAX 6 WORDS — short is powerful>",
  "body": "<supporting detail, MAX 20 WORDS — one clear idea only>",
  "emoji": "<1 highly relevant emoji>"
}}

Slide rules:
- Slide 1 (type: "hook"): Make them stop. Use a bold claim, surprising stat, or "you've been doing X wrong" angle. No fluff.
- Slides 2–(n-1) (type: "insight"): One sharp, specific insight per slide. Concrete > vague. Named > generic.
- Last slide (type: "cta"): "Save this." / "Follow for more [specific topic]." / "Share with someone who needs this."

Quality bar: Every headline should be good enough to stand alone as a tweet.
Language: {language}

Return ONLY a valid JSON array. No markdown fences, no explanation."""


class CarouselTransformer(BaseTransformer):
    platform = "Instagram Carousel"
    emoji = "🎠"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(self._system_prompt(SYSTEM_PROMPT), user_prompt)
        slides = self._parse_slides(result)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "slides": slides,
            "slide_count": len(slides),
        }

    def _parse_slides(self, raw: str) -> list[dict]:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            objects = re.findall(r"\{[^{}]+\}", cleaned, re.DOTALL)
            slides = []
            for obj in objects:
                try:
                    slides.append(json.loads(obj))
                except json.JSONDecodeError:
                    continue
            return slides
