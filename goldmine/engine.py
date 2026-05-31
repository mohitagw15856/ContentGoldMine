from pathlib import Path
from loguru import logger

from goldmine.ingestor import URLIngestor, YouTubeIngestor, TextIngestor
from goldmine.llm import get_llm_provider
from goldmine.transformer import (
    ThreadTransformer,
    LinkedInTransformer,
    NewsletterTransformer,
    CarouselTransformer,
    VideoScriptTransformer,
)
from goldmine.renderer import CarouselRenderer

PLATFORMS = {
    "x_thread": ThreadTransformer,
    "linkedin": LinkedInTransformer,
    "newsletter": NewsletterTransformer,
    "carousel": CarouselTransformer,
    "video_script": VideoScriptTransformer,
}


class GoldMineEngine:
    """Central orchestrator: ingest → transform → render."""

    def __init__(
        self,
        llm_provider: str,
        api_key: str,
        model: str | None = None,
        language: str = "English",
        carousel_theme: str = "gold",
        output_dir: str = "assets/carousel_output",
    ):
        self.llm = get_llm_provider(llm_provider, api_key, model)
        self.language = language
        self.carousel_theme = carousel_theme
        self.output_dir = Path(output_dir)

    def ingest(self, input_type: str, value: str) -> dict:
        if input_type == "url":
            if "youtube.com" in value or "youtu.be" in value:
                return YouTubeIngestor().ingest(value)
            return URLIngestor().ingest(value)
        elif input_type == "youtube":
            return YouTubeIngestor().ingest(value)
        elif input_type == "text":
            return TextIngestor().ingest(value)
        else:
            raise ValueError(f"Unknown input type: {input_type}")

    def repurpose(
        self,
        input_type: str,
        value: str,
        platforms: list[str] | None = None,
    ) -> dict:
        if platforms is None:
            platforms = list(PLATFORMS.keys())

        logger.info(f"Ingesting content | type={input_type}")
        content = self.ingest(input_type, value)
        logger.info(f"Repurposing for platforms: {platforms}")

        results = {"source": content, "outputs": {}}

        for platform_key in platforms:
            if platform_key not in PLATFORMS:
                logger.warning(f"Unknown platform: {platform_key}, skipping")
                continue
            try:
                transformer = PLATFORMS[platform_key](self.llm, self.language)
                logger.info(f"Transforming → {platform_key}")
                output = transformer.transform(content)

                # Render carousel images if applicable
                if platform_key == "carousel" and output.get("slides"):
                    renderer = CarouselRenderer(theme=self.carousel_theme)
                    slide_paths = renderer.render(output["slides"], self.output_dir)
                    output["image_paths"] = [str(p) for p in slide_paths]

                results["outputs"][platform_key] = output
                logger.success(f"Done: {platform_key}")
            except Exception as e:
                logger.error(f"Failed for {platform_key}: {e}")
                results["outputs"][platform_key] = {"error": str(e)}

        return results
