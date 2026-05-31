from .base import BaseTransformer

SYSTEM_PROMPT = """You are a top-1% X (Twitter) creator who has grown accounts to 100K+ followers.
You write threads that get saved, retweeted, and quoted. You know that generic advice gets ignored
— so you extract the sharpest, most non-obvious insight from any content and build a thread around it."""

INSTRUCTIONS = """Transform the content into a viral X thread. Follow this exact structure:

TWEET 1 (Hook — the most important tweet):
- Open with a bold, specific, counterintuitive claim OR a "most people don't know this" setup
- No "Thread:" label. No "I". No fluff opener.
- Must make someone stop scrolling. Example formats:
  · "X does Y. But nobody talks about the Z part."
  · "I [did/studied/analyzed] X. Here's what actually happens:"
  · A shocking number or statistic as the first line

TWEETS 2–(n-1) (Value):
- One sharp insight per tweet. No filler.
- Use short punchy lines, not paragraphs
- Include specific examples, numbers, or named concepts where possible
- Each tweet must be standalone-valuable — someone should want to screenshot it

LAST TWEET (CTA):
- Ask a genuine question OR give a strong reason to follow
- Don't say "RT if useful" — make it conversational

Rules:
- 10–14 tweets total
- Max 260 characters per tweet (leave buffer)
- Number as: 1/, 2/, 3/
- Language: {language}

Return ONLY the numbered tweets separated by blank lines. Nothing else."""


class ThreadTransformer(BaseTransformer):
    platform = "X Thread"
    emoji = "𝕏"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(self._system_prompt(SYSTEM_PROMPT), user_prompt)
        tweets = self._parse_tweets(result)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "tweets": tweets,
            "tweet_count": len(tweets),
        }

    def _parse_tweets(self, raw: str) -> list[str]:
        blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
        tweets = [b for b in blocks if b and b[0].isdigit()]
        return tweets if tweets else blocks
