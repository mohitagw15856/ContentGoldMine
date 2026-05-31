from .base import BaseTransformer

SYSTEM_PROMPT = """You write short-form video scripts (TikTok/Reels/Shorts) that hold attention
from first word to last. You know that 70% of viewers drop off in the first 3 seconds —
so you obsess over the hook. You write the way people actually talk, not the way they type."""

INSTRUCTIONS = """Transform the content into a short-form video script (50–90 seconds when spoken).

Use this exact format:

[HOOK — 0 to 3 sec]
<One sentence. The most jarring, specific, or curiosity-triggering thing you can say.
Pattern options: "Did you know [shocking fact]?" / "Stop doing [X]." / "[Number] [things] that [outcome]" / "Here's why [common belief] is wrong."
This line determines if the video gets watched or skipped.>

[POINT 1 — ~15 sec]
<Expand on the hook with the first real insight. Be specific. Use an example if you can.>

[POINT 2 — ~15 sec]
<Second key insight. Keep momentum — each point should feel like a revelation.>

[POINT 3 — ~15 sec]
<Third key insight. Build to the main payoff.>

[PAYOFF — ~10 sec]
<The main takeaway. What should the viewer DO or THINK differently after this video?
Make it actionable and memorable. This is what gets shared.>

[CTA — last 5 sec]
<One specific ask. Not "like and subscribe" — make it relevant to the content.
Example: "Follow for more [specific topic] breakdowns." / "Comment [X] if you want part 2.">

Script rules:
- Write for speaking, not reading. Short sentences. Punchy rhythm.
- Add [PAUSE] where the speaker should let something land
- Add [EMPHASIS] on words that should be stressed for impact
- No filler phrases: "So basically", "In this video", "Without further ado"
- Language: {language}

Return ONLY the formatted script with the section labels."""


class VideoScriptTransformer(BaseTransformer):
    platform = "Video Script"
    emoji = "🎬"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        word_count = len(result.split())
        estimated_seconds = int((word_count / 140) * 60)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "word_count": word_count,
            "estimated_duration_sec": estimated_seconds,
        }
