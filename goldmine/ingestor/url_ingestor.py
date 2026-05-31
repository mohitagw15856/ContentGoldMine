import trafilatura
from trafilatura.settings import use_config
from loguru import logger


class URLIngestor:
    """Extracts clean article text from any blog/article URL."""

    def ingest(self, url: str) -> dict:
        logger.info(f"Ingesting URL: {url}")
        try:
            # Use trafilatura's own fetcher — handles bot-detection, redirects,
            # and paywalled sites (Medium, Substack, etc.) better than raw requests
            config = use_config()
            config.set("DEFAULT", "DOWNLOAD_TIMEOUT", "20")
            downloaded = trafilatura.fetch_url(url, config=config)
            if not downloaded:
                raise ValueError("Could not download page. The site may be blocking automated access.")

            metadata = trafilatura.extract_metadata(downloaded)
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_recall=True,
            )
            if not text:
                raise ValueError("Could not extract readable text. Try pasting the content directly as Raw Text.")

            title = (metadata.title if metadata and metadata.title else None) or self._extract_title(downloaded)
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
