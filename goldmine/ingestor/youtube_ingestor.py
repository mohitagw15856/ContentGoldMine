from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
from loguru import logger


class YouTubeIngestor:
    """Extracts transcript and metadata from a YouTube video URL."""

    def ingest(self, url: str) -> dict:
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        logger.info(f"Fetching transcript for video: {video_id}")
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["en", "en-US", "en-GB"]
            )
        except (TranscriptsDisabled, NoTranscriptFound):
            # Fall back to auto-generated captions in any language
            try:
                transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript_list = next(iter(transcripts)).fetch()
            except Exception as e:
                raise ValueError(f"No transcript available for this video: {e}")

        full_text = " ".join(t["text"] for t in transcript_list)
        full_text = re.sub(r"\s+", " ", full_text).strip()
        logger.success(f"Extracted {len(full_text)} chars of transcript")
        return {
            "title": f"YouTube Video ({video_id})",
            "content": full_text,
            "source": url,
        }

    def _extract_video_id(self, url: str) -> str | None:
        patterns = [
            r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
