class TextIngestor:
    """Wraps raw pasted text into the standard content dict."""

    def ingest(self, text: str, title: str = "My Content") -> dict:
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")
        return {"title": title, "content": text.strip(), "source": "text"}
