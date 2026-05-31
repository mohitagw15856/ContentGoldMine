from pathlib import Path
import html as html_lib
from loguru import logger

THEMES = {
    "gold": {
        "bg": "#080808",
        "accent": "#D4AF37",
        "accent2": "#FFD700",
        "text": "#FFFFFF",
        "subtext": "#999999",
        "glow": "rgba(212,175,55,0.10)",
        "brand": "rgba(212,175,55,0.35)",
    },
    "dark": {
        "bg": "#0D0D1F",
        "accent": "#7C6FCD",
        "accent2": "#A78BFA",
        "text": "#FFFFFF",
        "subtext": "#8888AA",
        "glow": "rgba(124,111,205,0.10)",
        "brand": "rgba(167,139,250,0.35)",
    },
    "light": {
        "bg": "#F5F5F7",
        "accent": "#1D4ED8",
        "accent2": "#3B82F6",
        "text": "#111111",
        "subtext": "#555555",
        "glow": "rgba(29,78,216,0.06)",
        "brand": "rgba(29,78,216,0.35)",
    },
}


def _slide_html(slide_data: dict, total: int, t: dict) -> str:
    num = slide_data.get("slide", 1)
    headline = html_lib.escape(slide_data.get("headline", ""))
    body = html_lib.escape(slide_data.get("body", ""))
    emoji = slide_data.get("emoji", "")
    slide_type = slide_data.get("type", "insight")
    is_cta = slide_type == "cta" or num == total

    headline_extra = (
        f"background: linear-gradient(135deg, {t['accent']}, {t['accent2']});"
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent;"
    ) if is_cta else f"color: {t['text']};"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px; height: 1080px;
    background: {t['bg']};
    font-family: -apple-system, 'Helvetica Neue', 'Segoe UI', Arial, sans-serif;
    overflow: hidden; position: relative;
  }}
  .glow {{
    position: absolute;
    width: 800px; height: 800px; border-radius: 50%;
    background: radial-gradient(circle, {t['glow']} 0%, transparent 65%);
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
  }}
  .top-bar {{
    position: absolute; top: 0; left: 0; right: 0; height: 5px;
    background: linear-gradient(90deg, {t['accent']}60, {t['accent2']}, {t['accent2']}, {t['accent']}60);
  }}
  .bottom-bar {{
    position: absolute; bottom: 0; left: 0; right: 0; height: 5px;
    background: linear-gradient(90deg, {t['accent']}60, {t['accent2']}, {t['accent2']}, {t['accent']}60);
  }}
  .counter {{
    position: absolute; top: 32px; right: 48px;
    font-size: 22px; font-weight: 600; letter-spacing: 3px;
    color: {t['brand']};
  }}
  .brand {{
    position: absolute; bottom: 24px; left: 48px;
    font-size: 21px; font-weight: 700; letter-spacing: 0.5px;
    color: {t['brand']};
  }}
  .content {{
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 90px 80px; text-align: center;
    gap: 0;
  }}
  .emoji {{
    font-size: 108px; line-height: 1;
    margin-bottom: 38px;
    filter: drop-shadow(0 4px 24px {t['accent']}40);
  }}
  .headline {{
    font-size: 74px; font-weight: 900;
    line-height: 1.05; letter-spacing: -1.5px;
    max-width: 940px;
    margin-bottom: 32px;
    {headline_extra}
  }}
  .divider {{
    width: 64px; height: 4px; border-radius: 2px;
    background: linear-gradient(90deg, {t['accent']}, {t['accent2']});
    margin: 0 auto 32px;
  }}
  .body-text {{
    font-size: 36px; font-weight: 400;
    color: {t['subtext']};
    line-height: 1.6; max-width: 860px;
  }}
</style>
</head>
<body>
  <div class="glow"></div>
  <div class="top-bar"></div>
  <div class="bottom-bar"></div>
  <div class="counter">{num} / {total}</div>
  <div class="brand">⛏ ContentGoldMine</div>
  <div class="content">
    {'<div class="emoji">' + emoji + '</div>' if emoji else ''}
    <div class="headline">{headline}</div>
    <div class="divider"></div>
    {'<div class="body-text">' + body + '</div>' if body else ''}
  </div>
</body>
</html>"""


class CarouselRenderer:
    def __init__(self, width: int = 1080, height: int = 1080, theme: str = "gold"):
        self.width = width
        self.height = height
        self.theme = THEMES.get(theme, THEMES["gold"])

    def render(self, slides: list[dict], output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        total = len(slides)

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                for slide_data in slides:
                    path = self._render_with_playwright(
                        slide_data, total, output_dir, browser
                    )
                    paths.append(path)
                browser.close()
        except ImportError:
            logger.warning("Playwright not found, falling back to Pillow renderer")
            paths = self._render_pillow_fallback(slides, output_dir)

        logger.success(f"Rendered {len(paths)} carousel slides → {output_dir}")
        return paths

    def _render_with_playwright(self, slide_data, total, output_dir, browser):
        html = _slide_html(slide_data, total, self.theme)
        page = browser.new_page(viewport={"width": self.width, "height": self.height})
        page.set_content(html, wait_until="domcontentloaded")
        page.wait_for_timeout(300)
        num = slide_data.get("slide", 1)
        path = output_dir / f"slide_{num:02d}.png"
        page.screenshot(path=str(path))
        page.close()
        return path

    def _render_pillow_fallback(self, slides, output_dir):
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        t = self.theme
        paths = []
        for slide_data in slides:
            img = Image.new("RGB", (self.width, self.height), color=t["bg"])
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
                small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except Exception:
                font = ImageFont.load_default()
                small = font
            headline = textwrap.fill(slide_data.get("headline", ""), 20)
            body = textwrap.fill(slide_data.get("body", ""), 32)
            draw.multiline_text((540, 420), headline, font=font, fill=t["text"], anchor="mm", align="center")
            draw.multiline_text((540, 620), body, font=small, fill=t["subtext"], anchor="mm", align="center")
            draw.rectangle([(0, 0), (self.width, 5)], fill=t["accent"])
            num = slide_data.get("slide", 1)
            path = output_dir / f"slide_{num:02d}.png"
            img.save(path, "PNG")
            paths.append(path)
        return paths
