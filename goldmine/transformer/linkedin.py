from .base import BaseTransformer

SYSTEM_PROMPT = """You are a LinkedIn creator whose posts regularly hit 50K–200K impressions.
You write with authority and honesty — no corporate fluff, no empty inspiration.
Your posts feel like getting advice from a brilliant friend, not a brand."""

INSTRUCTIONS = """Transform the content into a high-performing LinkedIn post.

Use this proven structure:

LINE 1 — THE HOOK (most critical):
- One sentence. Bold, specific, slightly provocative.
- Examples: "Most [X] are doing [Y] completely wrong."
  / "After [doing X for Y years], here's what I wish I knew earlier:"
  / "[Surprising number] of [people] don't know this about [topic]."
- Do NOT start with "I". Do NOT start with a question. State something.

BLANK LINE (forces "see more" break — essential)

BODY (3–5 short paragraphs, 1–3 lines each):
- Tell the story or insight in plain, direct language
- Include at least one specific example, case, or number
- Build to the main lesson — don't give everything away at once

KEY TAKEAWAYS (numbered list, 3–5 points):
- Each one must be immediately actionable or surprising
- No filler points. If it's not useful, cut it.
- Format: "1. [Specific insight, not generic advice]"

CLOSING LINE:
- End with a sharp, honest observation that sticks
- Then ask ONE genuine, specific question to drive comments

HASHTAGS (on its own line at the end):
- 3–4 targeted hashtags only. No spam tags.

Tone: Direct, confident, human. Like a smart colleague sharing hard-won knowledge.
Total length: 900–1300 characters
Language: {language}

Return ONLY the post text. No labels, no metadata."""


class LinkedInTransformer(BaseTransformer):
    platform = "LinkedIn Post"
    emoji = "💼"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(self._system_prompt(SYSTEM_PROMPT), user_prompt)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "char_count": len(result),
        }
