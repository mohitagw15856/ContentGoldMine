import json
import re
from goldmine.llm.base import BaseLLMProvider

SCORE_SYSTEM = (
    "You are a viral content analyst. Rate social media content on engagement potential. "
    "Return ONLY valid JSON — no explanation, no markdown."
)

SCORE_PROMPT = """Rate this {platform} content on viral potential:

---
{content}
---

Return exactly this JSON (integers only for scores):
{{
  "hook_strength": <1-10>,
  "engagement_score": <1-10>,
  "tip": "<one specific improvement, max 15 words>"
}}"""


def score_output(llm: BaseLLMProvider, platform: str, content: str) -> dict:
    """Run a quick second LLM call to rate content. Returns dict or {} on failure."""
    try:
        prompt = SCORE_PROMPT.format(platform=platform, content=content[:2500])
        raw = llm.complete(SCORE_SYSTEM, prompt)
        match = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {
                "hook_strength": int(data.get("hook_strength", 0)),
                "engagement_score": int(data.get("engagement_score", 0)),
                "tip": str(data.get("tip", "")),
            }
    except Exception:
        pass
    return {}
