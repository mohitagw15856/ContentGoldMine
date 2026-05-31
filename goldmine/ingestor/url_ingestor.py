import trafilatura
import requests
from loguru import logger


class URLIngestor:
    """Extracts clean article text from any blog/article URL."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def ingest(self, url: str) -> dict:
        logger.info(f"Ingesting URL: {url}")
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            text = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
            )
            if not text:
                raise ValueError("Could not extract readable text from URL.")
            title = self._extract_title(response.text)
            logger.success(f"Extracted {len(text)} chars from {url}")
            return {"title": title, "content": text, "source": url}
        except Exception as e:
            logger.error(f"URL ingestion failed: {e}")
            raise

    def _extract_title(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            tag = soup.find("title") or soup.find("h1")
            return tag.get_text(strip=True) if tag else "Untitled"
        except Exception:
            return "Untitled"
