from youtube_transcript_api import YouTubeTranscriptApi
import re
from loguru import logger


class YouTubeIngestor:
    """Extracts transcript and metadata from a YouTube video URL."""

    def ingest(self, url: str) -> dict:
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        logger.info(f"Fetching transcript for video: {video_id}")

        api = YouTubeTranscriptApi()
        try:
            # Try English first
            fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        except Exception:
            # Fall back to whatever language is available
            try:
                transcript_list = api.list(video_id)
                first = next(iter(transcript_list))
                fetched = first.fetch()
            except Exception as e:
                raise ValueError(f"No transcript available for this video: {e}")

        full_text = " ".join(snippet.text for snippet in fetched)
        full_text = re.sub(r"\s+", " ", full_text).strip()
        logger.success(f"Extracted {len(full_text)} chars of transcript")
        return {
            "title": f"YouTube Video ({video_id})",
            "content": full_text,
            "source": url,
        }

    def _extract_video_id(self, url: str) -> str | None:
        match = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})", url)
        return match.group(1) if match else None
