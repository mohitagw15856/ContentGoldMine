"""Render the calendar on a blank page for a clean screenshot."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DOCS = Path(__file__).parent.parent / "docs"

CAL_ROWS = [
    ("Monday",    "𝕏 X Thread",    "How AI is changing content creation", "Draft",     "Most founders waste 6 hours a day on content..."),
    ("Monday",    "💼 LinkedIn",    "How AI is changing content creation", "Scheduled", "Here's the uncomfortable truth about content..."),
    ("Tuesday",   "📧 Newsletter",  "How AI is changing content creation", "Draft",     "Subject: The content repurposing system..."),
    ("Wednesday", "🎬 Video Script","How AI is changing content creation", "Draft",     "[HOOK] Did you know 90% of content is posted..."),
    ("Thursday",  "𝕏 X Thread",    "10 lessons from building in public",  "Scheduled", "I've been building in public for 6 months..."),
    ("Friday",    "💼 LinkedIn",    "10 lessons from building in public",  "Draft",     "Six months ago I committed to building..."),
    ("Saturday",  "📧 Newsletter",  "10 lessons from building in public",  "Posted",    "Subject: What nobody tells you about..."),
]
STATUS_COLORS = {"Draft": "#D4AF37", "Scheduled": "#4CAF50", "Posted": "#7ABCFF"}


def build_calendar_html() -> str:
    tbody = ""
    for i, (day, platform, title, status, preview) in enumerate(CAL_ROWS):
        bg = "#0F0F14" if i % 2 == 0 else "#13131A"
        sc = STATUS_COLORS.get(status, "#888")
        badge = (
            f'<span style="background:{sc}22;color:{sc};border:1px solid {sc}44;'
            f'border-radius:6px;padding:3px 9px;font-weight:700;font-size:0.75rem;">{status}</span>'
        )
        tbody += (
            f'<tr style="background:{bg};border-bottom:1px solid #1A1A22;">'
            f'<td style="padding:9px 12px;color:#D0D0D0;">{day}</td>'
            f'<td style="padding:9px 12px;color:#D0D0D0;">{platform}</td>'
            f'<td style="padding:9px 12px;color:#E0E0E0;font-weight:600;">{title[:40]}</td>'
            f'<td style="padding:9px 12px;">{badge}</td>'
            f'<td style="padding:9px 12px;color:#666;font-style:italic;">{preview[:55]}</td>'
            f'</tr>'
        )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 28px; background: #0E0E10;
         font-family: -apple-system, 'Segoe UI', sans-serif; }}
  * {{ box-sizing: border-box; }}
</style>
</head>
<body>
  <div style="background:#0E0E10;border:1px solid #2A2A30;border-radius:14px;padding:24px;">
    <div style="font-size:1.05rem;font-weight:800;color:#D4AF37;margin-bottom:5px;">
      📅 Weekly Content Calendar
    </div>
    <div style="color:#666;font-size:0.8rem;margin-bottom:18px;">
      Edit any cell · Drag to reorder · Export as CSV for Buffer or Hootsuite
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
      <thead>
        <tr style="border-bottom:2px solid #2A2A34;">
          <th style="text-align:left;padding:9px 12px;color:#888;font-weight:600;width:110px;">Day</th>
          <th style="text-align:left;padding:9px 12px;color:#888;font-weight:600;width:145px;">Platform</th>
          <th style="text-align:left;padding:9px 12px;color:#888;font-weight:600;">Title</th>
          <th style="text-align:left;padding:9px 12px;color:#888;font-weight:600;width:100px;">Status</th>
          <th style="text-align:left;padding:9px 12px;color:#888;font-weight:600;">Preview</th>
        </tr>
      </thead>
      <tbody>{tbody}</tbody>
    </table>
    <div style="margin-top:16px;">
      <button style="background:#1A1A22;border:1px solid #2A2A34;color:#D4AF37;
        border-radius:8px;padding:8px 18px;font-size:0.84rem;font-weight:600;cursor:pointer;">
        📥 Export Calendar as CSV
      </button>
    </div>
  </div>
</body>
</html>"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1100, "height": 700})
        page = await ctx.new_page()
        await page.set_content(build_calendar_html())
        await asyncio.sleep(0.5)
        el = page.locator("div").first
        await el.screenshot(path=str(DOCS / "screenshot_calendar.png"))
        print(f"  → screenshot_calendar.png")
        await browser.close()

asyncio.run(main())
