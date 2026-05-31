import tweepy


def post_thread(
    tweets: list[str],
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_secret: str,
) -> list[str]:
    """Post tweet strings as a chained thread. Returns list of posted tweet IDs."""
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )
    tweet_ids: list[str] = []
    reply_to: str | None = None
    for text in tweets:
        if len(text) > 280:
            text = text[:277] + "..."
        kwargs: dict = {"text": text}
        if reply_to:
            kwargs["in_reply_to_tweet_id"] = reply_to
        resp = client.create_tweet(**kwargs)
        tweet_id = resp.data["id"]
        tweet_ids.append(tweet_id)
        reply_to = tweet_id
    return tweet_ids
