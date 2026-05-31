from .base import BaseTransformer

SYSTEM_PROMPT = """You are a viral X (Twitter) content strategist who writes threads
that get thousands of engagements. You understand hooks, pacing, and what makes people
tap "read more" and retweet."""

INSTRUCTIONS = """Transform the content into a viral X (Twitter) thread.

Rules:
- Start with an irresistible hook tweet (no "Thread:" label — just the hook)
- Each tweet max 280 characters
- Use numbers for each tweet: 1/, 2/, 3/ etc.
- Add value in every single tweet — no filler
- Use line breaks for readability
- End with a strong CTA tweet that drives follows/engagement
- 8–15 tweets total
- Language: {language}

Return ONLY the tweets, each on its own line starting with the number (1/, 2/, etc.).
Separate tweets with a blank line."""


class ThreadTransformer(BaseTransformer):
    platform = "X Thread"
    emoji = "🐦"

    def transform(self, content: dict) -> dict:
        instructions = INSTRUCTIONS.format(language=self.language)
        user_prompt = self._build_prompt(content, instructions)
        result = self.llm.complete(SYSTEM_PROMPT, user_prompt)
        tweets = self._parse_tweets(result)
        return {
            "platform": self.platform,
            "emoji": self.emoji,
            "raw": result,
            "tweets": tweets,
            "tweet_count": len(tweets),
        }

    def _parse_tweets(self, raw: str) -> list[str]:
        tweets = []
        for line in raw.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("—")):
                tweets.append(line)
        return tweets if tweets else [t.strip() for t in raw.split("\n\n") if t.strip()]
