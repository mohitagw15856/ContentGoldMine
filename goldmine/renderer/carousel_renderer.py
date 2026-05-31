from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap
from loguru import logger

THEMES = {
    "gold": {
        "bg_start": (20, 15, 0),
        "bg_end": (60, 45, 5),
        "accent": (212, 175, 55),
        "headline_color": (255, 220, 80),
        "body_color": (230, 215, 180),
        "slide_num_color": (150, 120, 30),
    },
    "dark": {
        "bg_start": (10, 10, 20),
        "bg_end": (25, 25, 50),
        "accent": (100, 80, 255),
        "headline_color": (255, 255, 255),
        "body_color": (200, 200, 220),
        "slide_num_color": (100, 80, 200),
    },
    "light": {
        "bg_start": (245, 245, 250),
        "bg_end": (225, 225, 240),
        "accent": (80, 60, 200),
        "headline_color": (20, 20, 50),
        "body_color": (60, 60, 90),
        "slide_num_color": (120, 100, 200),
    },
}


class CarouselRenderer:
    def __init__(self, width: int = 1080, height: int = 1080, theme: str = "gold"):
        self.width = width
        self.height = height
        self.theme = THEMES.get(theme, THEMES["gold"])
        self.font_path = self._find_font()

    def render(self, slides: list[dict], output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for slide_data in slides:
            path = self._render_slide(slide_data, output_dir)
            paths.append(path)
        logger.success(f"Rendered {len(paths)} carousel slides → {output_dir}")
        return paths

    def _render_slide(self, slide_data: dict, output_dir: Path) -> Path:
        img = self._make_gradient_bg()
        draw = ImageDraw.Draw(img)
        t = self.theme

        slide_num = slide_data.get("slide", 1)
        headline = slide_data.get("headline", "")
        body = slide_data.get("body", "")
        emoji = slide_data.get("emoji", "")

        # Accent bar at top
        draw.rectangle([(0, 0), (self.width, 8)], fill=t["accent"])

        # Slide number
        num_font = self._get_font(32)
        draw.text((60, 40), f"{slide_num}", font=num_font, fill=t["slide_num_color"])

        # Emoji (large, centered top area)
        if emoji:
            em_font = self._get_font(90)
            em_w = draw.textlength(emoji, font=em_font) if hasattr(draw, "textlength") else 90
            draw.text(
                ((self.width - em_w) / 2, 160),
                emoji,
                font=em_font,
                fill=t["headline_color"],
            )

        # Headline
        h_font = self._get_font(68, bold=True)
        wrapped_headline = textwrap.fill(headline, width=22)
        h_bbox = draw.multiline_textbbox((0, 0), wrapped_headline, font=h_font)
        h_height = h_bbox[3] - h_bbox[1]
        h_y = 320 if emoji else 240
        draw.multiline_text(
            ((self.width - (h_bbox[2] - h_bbox[0])) / 2, h_y),
            wrapped_headline,
            font=h_font,
            fill=t["headline_color"],
            align="center",
        )

        # Divider
        div_y = h_y + h_height + 40
        draw.rectangle(
            [(self.width // 2 - 60, div_y), (self.width // 2 + 60, div_y + 4)],
            fill=t["accent"],
        )

        # Body text
        if body:
            b_font = self._get_font(42)
            wrapped_body = textwrap.fill(body, width=34)
            b_bbox = draw.multiline_textbbox((0, 0), wrapped_body, font=b_font)
            b_x = (self.width - (b_bbox[2] - b_bbox[0])) / 2
            draw.multiline_text(
                (b_x, div_y + 30),
                wrapped_body,
                font=b_font,
                fill=t["body_color"],
                align="center",
                spacing=14,
            )

        # Accent bar at bottom
        draw.rectangle(
            [(0, self.height - 8), (self.width, self.height)],
            fill=t["accent"],
        )

        filename = output_dir / f"slide_{slide_num:02d}.png"
        img.save(filename, "PNG")
        return filename

    def _make_gradient_bg(self) -> Image.Image:
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        start = self.theme["bg_start"]
        end = self.theme["bg_end"]
        for y in range(self.height):
            r = int(start[0] + (end[0] - start[0]) * y / self.height)
            g = int(start[1] + (end[1] - start[1]) * y / self.height)
            b = int(start[2] + (end[2] - start[2]) * y / self.height)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return img

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        if self.font_path:
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except Exception:
                pass
        return ImageFont.load_default()

    def _find_font(self) -> Path | None:
        candidates = [
            # macOS
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/Library/Fonts/Arial.ttf"),
            # Linux
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            # Windows
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
        ]
        for p in candidates:
            if p.exists():
                return p
        return None
