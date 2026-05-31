"""Retake history and calendar screenshots with fixes."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DOCS = Path(__file__).parent.parent / "docs"


async def inject_and_snap(page, elem_id: str, html: str, style: str, out: str):
    await page.evaluate(
        "(args) => {"
        "  const div = document.createElement('div');"
        "  div.id = args.id;"
        "  div.style.cssText = args.style;"
        "  div.innerHTML = args.html;"
        "  document.body.appendChild(div);"
        "}",
        {"id": elem_id, "html": html, "style": style},
    )
    await asyncio.sleep(0.4)
    el = page.locator(f"#{elem_id}")
    await el.screenshot(path=out)
    await page.evaluate("(id) => document.getElementById(id).remove()", elem_id)
    print(f"  → {Path(out).name}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await ctx.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
        await asyncio.sleep(2)

        # ── History ────────────────────────────────────────────────────────────
        hist_html = (
            '<div style="font-size:0.75rem;color:#888;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:12px;">🕘 History — Browse Past Runs</div>'
            '<select style="width:100%;background:#0D0D12;color:#CCC;border:1px solid #222230;'
            'border-radius:8px;padding:8px 12px;font-size:0.85rem;margin-bottom:12px;">'
            '<option>2026-05-31 11:42  How AI Is Changing Content Creation</option>'
            '<option>2026-05-31 10:18  10 Lessons From Building In Public</option>'
            '<option>2026-05-30 21:05  The Future of Work: 5 Predictions</option>'
            '<option>2026-05-30 18:33  Why Most Startups Fail At Marketing</option>'
            '<option>2026-05-29 14:12  Content Strategy for 2026</option>'
            '</select>'
            '<div style="display:flex;gap:10px;margin-bottom:14px;">'
            '<button style="flex:1;background:linear-gradient(135deg,#B8860B,#D4AF37);color:#000;'
            'font-weight:800;border:none;border-radius:8px;padding:9px;font-size:0.88rem;'
            'cursor:pointer;">📂 Load</button>'
            '<button style="flex:1;background:#1A1A1F;color:#FF5252;font-weight:700;'
            'border:1px solid #3A1A1A;border-radius:8px;padding:9px;font-size:0.88rem;'
            'cursor:pointer;">🗑️ Delete</button>'
            '</div>'
            '<div style="padding-top:12px;border-top:1px solid #1E1E26;color:#555;font-size:0.75rem;">'
            '5 runs saved &nbsp;·&nbsp; Auto-saved on every generation &nbsp;·&nbsp; '
            'Click Load to re-render any past output'
            '</div>'
        )
        hist_style = (
            "position:fixed;top:80px;left:50%;transform:translateX(-50%);width:520px;"
            "z-index:9999;background:#0A0A0D;padding:20px;border-radius:14px;"
            "border:1px solid #1E1E26;font-family:-apple-system,Segoe UI,sans-serif;"
        )
        await inject_and_snap(page, "mock-history", hist_html, hist_style,
                               str(DOCS / "screenshot_history.png"))

        # ── Calendar (fixed X Thread icon) ─────────────────────────────────────
        cal_rows = [
            ("Monday",    "𝕏 X Thread",    "How AI is changing content creation", "Draft",     "Most founders waste 6 hours a day on content..."),
            ("Monday",    "💼 LinkedIn",    "How AI is changing content creation", "Scheduled", "Here's the uncomfortable truth about content..."),
            ("Tuesday",   "📧 Newsletter",  "How AI is changing content creation", "Draft",     "Subject: The content repurposing system..."),
            ("Wednesday", "🎬 Video Script","How AI is changing content creation", "Draft",     "[HOOK] Did you know 90% of content is posted..."),
            ("Thursday",  "𝕏 X Thread",    "10 lessons from building in public",  "Scheduled", "I've been building in public for 6 months..."),
            ("Friday",    "💼 LinkedIn",    "10 lessons from building in public",  "Draft",     "Six months ago I committed to building..."),
            ("Saturday",  "📧 Newsletter",  "10 lessons from building in public",  "Posted",    "Subject: What nobody tells you about..."),
        ]
        status_colors = {"Draft": "#D4AF37", "Scheduled": "#4CAF50", "Posted": "#7ABCFF"}

        tbody = ""
        for i, (day, platform, title, status, preview) in enumerate(cal_rows):
            bg = "#0F0F14" if i % 2 == 0 else "#13131A"
            sc = status_colors.get(status, "#888")
            badge = (
                f'<span style="background:{sc}22;color:{sc};border:1px solid {sc}44;'
                f'border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">{status}</span>'
            )
            tbody += (
                f'<tr style="background:{bg};border-bottom:1px solid #1A1A22;">'
                f'<td style="padding:8px 10px;color:#D0D0D0;">{day}</td>'
                f'<td style="padding:8px 10px;color:#D0D0D0;">{platform}</td>'
                f'<td style="padding:8px 10px;color:#E0E0E0;font-weight:600;">{title[:38]}</td>'
                f'<td style="padding:8px 10px;">{badge}</td>'
                f'<td style="padding:8px 10px;color:#666;font-style:italic;">{preview[:52]}...</td>'
                f'</tr>'
            )

        cal_html = (
            '<div style="font-size:1rem;font-weight:800;color:#D4AF37;margin-bottom:6px;">📅 Weekly Content Calendar</div>'
            '<div style="color:#666;font-size:0.78rem;margin-bottom:14px;">Edit any cell · Drag to reorder · Export as CSV for Buffer or Hootsuite</div>'
            '<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">'
            '<thead><tr style="border-bottom:2px solid #2A2A34;">'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:100px;">Day</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:140px;">Platform</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;">Title</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:90px;">Status</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;">Preview</th>'
            '</tr></thead>'
            f'<tbody>{tbody}</tbody></table>'
            '<div style="margin-top:14px;">'
            '<button style="background:#1A1A22;border:1px solid #2A2A34;color:#D4AF37;'
            'border-radius:8px;padding:7px 18px;font-size:0.82rem;font-weight:600;cursor:pointer;">'
            '📥 Export Calendar as CSV</button>'
            '</div>'
        )
        cal_style = (
            "position:fixed;top:60px;left:50%;transform:translateX(-50%);width:900px;"
            "z-index:9999;background:#0E0E10;padding:24px;border-radius:14px;"
            "border:1px solid #2A2A30;font-family:-apple-system,Segoe UI,sans-serif;"
        )
        await inject_and_snap(page, "mock-cal", cal_html, cal_style,
                               str(DOCS / "screenshot_calendar.png"))

        await browser.close()
        print("Done.")


asyncio.run(main())
