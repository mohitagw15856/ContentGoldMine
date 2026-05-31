"""Take screenshots of new Tier 2 features for README docs."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

URL = "http://localhost:8501"
DOCS = Path(__file__).parent.parent / "docs"
DOCS.mkdir(exist_ok=True)


async def wait_for_streamlit(page):
    await page.wait_for_load_state("networkidle", timeout=15000)
    await page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
    await asyncio.sleep(2)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await ctx.new_page()

        print("Loading app...")
        await page.goto(URL)
        await wait_for_streamlit(page)

        # ── 1. Full sidebar with Publishing + History expanders open ──────────
        print("Screenshot: sidebar with new sections...")
        # Open Publishing credentials expander
        pub_exp = page.locator("details summary").filter(has_text="Publishing credentials")
        if await pub_exp.count():
            await pub_exp.first.click()
            await asyncio.sleep(0.8)
        # Open History expander
        hist_exp = page.locator("details summary").filter(has_text="History")
        if await hist_exp.count():
            await hist_exp.first.click()
            await asyncio.sleep(0.8)

        sidebar = page.locator('[data-testid="stSidebar"]')
        await sidebar.screenshot(path=str(DOCS / "screenshot_sidebar_new.png"))
        print("  → screenshot_sidebar_new.png")

        # ── 2. Full app with batch mode toggled on ────────────────────────────
        print("Screenshot: batch mode + calendar area...")
        toggle = page.locator('[data-testid="stCheckbox"], [role="switch"]').first
        # Find the batch toggle specifically
        batch_toggle = page.get_by_text("Batch Mode").locator("..")
        toggle_btn = page.locator('[role="switch"]').first
        if await toggle_btn.count():
            await toggle_btn.click()
            await asyncio.sleep(1)
        await page.screenshot(
            path=str(DOCS / "screenshot_batch_mode.png"),
            clip={"x": 320, "y": 0, "width": 1080, "height": 600},
        )
        print("  → screenshot_batch_mode.png")

        # ── 3. Inject mock score bar HTML to screenshot ───────────────────────
        print("Screenshot: viral score bar...")
        await page.evaluate("""() => {
            const div = document.createElement('div');
            div.id = 'mock-score-preview';
            div.style.cssText = `
                position: fixed; top: 80px; left: 360px; right: 40px; z-index: 9999;
                background: #0E0E10; padding: 20px; border-radius: 14px;
                border: 1px solid #2A2A30; font-family: -apple-system, 'Segoe UI', sans-serif;
            `;
            div.innerHTML = `
                <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
                    🏆 Viral Score — X Thread
                </div>
                <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;
                            background:#0F0F16;border:1px solid #1E1E2A;border-radius:10px;
                            padding:12px 16px;margin-bottom:12px;">
                    <span style="display:flex;align-items:center;gap:6px;font-size:0.85rem;font-weight:700;">
                        <span>🎯 Hook</span>
                        <span style="color:#4CAF50;font-size:1rem;font-weight:900;">9/10</span>
                    </span>
                    <span style="display:flex;align-items:center;gap:6px;font-size:0.85rem;font-weight:700;">
                        <span>📈 Engagement</span>
                        <span style="color:#4CAF50;font-size:1rem;font-weight:900;">8/10</span>
                    </span>
                    <span style="color:#888;font-size:0.8rem;font-style:italic;">
                        💡 Add a specific stat to the opening tweet for more impact
                    </span>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
                    <span style="background:#1A1A22;border:1px solid #2A2A34;border-radius:20px;
                                 padding:4px 14px;font-size:0.78rem;color:#D4AF37;font-weight:600;">
                        🐦 12 tweets
                    </span>
                    <span style="background:#1A1A22;border:1px solid #2A2A34;border-radius:20px;
                                 padding:4px 14px;font-size:0.78rem;color:#D4AF37;font-weight:600;">
                        📝 2,140 chars
                    </span>
                </div>
                <div style="background:#13131A;border:1px solid #222230;border-radius:14px;
                            padding:1rem 1.3rem;margin-bottom:0.65rem;position:relative;">
                    <span style="position:absolute;top:12px;right:14px;font-size:0.7rem;font-weight:700;
                                 padding:2px 8px;border-radius:10px;background:#0d2d0d;color:#4CAF50;">
                        47/280
                    </span>
                    <div style="color:#D4AF37;font-weight:700;font-size:0.82rem;margin-bottom:0.3rem;">1/12</div>
                    <div style="color:#E0E0E0;font-size:0.97rem;line-height:1.55;padding-right:60px;">
                        Most founders waste 6 hours a day on content that reaches 200 people. Here's the system that changed everything for me.
                    </div>
                </div>
                <div style="background:#13131A;border:1px solid #222230;border-radius:14px;
                            padding:1rem 1.3rem;margin-bottom:0.65rem;position:relative;">
                    <span style="position:absolute;top:12px;right:14px;font-size:0.7rem;font-weight:700;
                                 padding:2px 8px;border-radius:10px;background:#0d2d0d;color:#4CAF50;">
                        62/280
                    </span>
                    <div style="color:#D4AF37;font-weight:700;font-size:0.82rem;margin-bottom:0.3rem;">2/12</div>
                    <div style="color:#E0E0E0;font-size:0.97rem;line-height:1.55;padding-right:60px;">
                        The real problem isn't writing. It's that you write once, publish once, and the content dies. One post → one platform → one chance.
                    </div>
                </div>
            `;
            document.body.appendChild(div);
        }""")
        await asyncio.sleep(0.5)
        mock_el = page.locator("#mock-score-preview")
        await mock_el.screenshot(path=str(DOCS / "screenshot_viral_score.png"))
        await page.evaluate("document.getElementById('mock-score-preview').remove()")
        print("  → screenshot_viral_score.png")

        # ── 4. Publish panel mock ─────────────────────────────────────────────
        print("Screenshot: publish panel...")
        await page.evaluate("""() => {
            const div = document.createElement('div');
            div.id = 'mock-publish';
            div.style.cssText = `
                position:fixed;top:80px;left:360px;width:700px;z-index:9999;
                background:#0E0E10;padding:20px;border-radius:14px;
                border:1px solid #2A2A30;font-family:-apple-system,'Segoe UI',sans-serif;
            `;
            div.innerHTML = `
                <div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
                    📤 Post to platform
                </div>
                <div style="display:flex;gap:0;border-bottom:1px solid #222230;margin-bottom:16px;">
                    <div style="padding:8px 16px;font-size:0.85rem;font-weight:700;color:#D4AF37;
                                border-bottom:2px solid #D4AF37;">𝕏 Post to X</div>
                    <div style="padding:8px 16px;font-size:0.85rem;color:#666;">💼 Post to LinkedIn</div>
                    <div style="padding:8px 16px;font-size:0.85rem;color:#666;">🔗 Webhook</div>
                </div>
                <div style="color:#888;font-size:0.8rem;margin-bottom:14px;">
                    Will post as a chained thread.
                </div>
                <div style="background:linear-gradient(135deg,#B8860B 0%,#D4AF37 40%,#FFD700 100%);
                            color:#000;font-weight:800;font-size:1rem;
                            border:none;border-radius:10px;padding:0.7rem 2rem;
                            width:100%;text-align:center;cursor:pointer;letter-spacing:0.3px;">
                    🚀 Post Thread to X
                </div>
                <div style="margin-top:14px;padding-top:14px;border-top:1px solid #1E1E26;
                            color:#555;font-size:0.75rem;">
                    ✅ Connected · Keys saved in sidebar → Publishing credentials
                </div>
            `;
            document.body.appendChild(div);
        }""")
        await asyncio.sleep(0.5)
        pub_mock = page.locator("#mock-publish")
        await pub_mock.screenshot(path=str(DOCS / "screenshot_publish.png"))
        await page.evaluate("document.getElementById('mock-publish').remove()")
        print("  → screenshot_publish.png")

        # ── 5. Content calendar mock ──────────────────────────────────────────
        print("Screenshot: content calendar...")
        cal_html = (
            '<div style="font-size:1rem;font-weight:800;color:#D4AF37;margin-bottom:6px;">📅 Weekly Content Calendar</div>'
            '<div style="color:#666;font-size:0.78rem;margin-bottom:16px;">Drag to reorder · Edit any cell · Export as CSV for Buffer or Hootsuite</div>'
            '<table style="width:100%;border-collapse:collapse;font-size:0.8rem;">'
            '<thead><tr style="border-bottom:1px solid #2A2A34;">'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:100px;">Day</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:130px;">Platform</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:220px;">Title</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;width:90px;">Status</th>'
            '<th style="text-align:left;padding:8px 10px;color:#888;font-weight:600;">Preview</th>'
            '</tr></thead><tbody>'
            '<tr style="background:#0F0F14;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Monday</td><td style="padding:7px 10px;color:#D0D0D0;">&#𝕏; X Thread</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">How AI is changing content</td><td style="padding:7px 10px;"><span style="background:#D4AF3722;color:#D4AF37;border:1px solid #D4AF3744;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Draft</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">Most founders waste 6 hours a day...</td></tr>'
            '<tr style="background:#13131A;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Monday</td><td style="padding:7px 10px;color:#D0D0D0;">LinkedIn</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">How AI is changing content</td><td style="padding:7px 10px;"><span style="background:#4CAF5022;color:#4CAF50;border:1px solid #4CAF5044;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Scheduled</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">Here\'s the uncomfortable truth...</td></tr>'
            '<tr style="background:#0F0F14;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Tuesday</td><td style="padding:7px 10px;color:#D0D0D0;">Newsletter</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">How AI is changing content</td><td style="padding:7px 10px;"><span style="background:#D4AF3722;color:#D4AF37;border:1px solid #D4AF3744;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Draft</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">Subject: The content repurposing system...</td></tr>'
            '<tr style="background:#13131A;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Wednesday</td><td style="padding:7px 10px;color:#D0D0D0;">Video Script</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">How AI is changing content</td><td style="padding:7px 10px;"><span style="background:#D4AF3722;color:#D4AF37;border:1px solid #D4AF3744;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Draft</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">[HOOK] Did you know 90% of content...</td></tr>'
            '<tr style="background:#0F0F14;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Thursday</td><td style="padding:7px 10px;color:#D0D0D0;">X Thread</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">10 lessons from building in public</td><td style="padding:7px 10px;"><span style="background:#4CAF5022;color:#4CAF50;border:1px solid #4CAF5044;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Scheduled</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">I\'ve been building in public for 6 months...</td></tr>'
            '<tr style="background:#13131A;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Friday</td><td style="padding:7px 10px;color:#D0D0D0;">LinkedIn</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">10 lessons from building in public</td><td style="padding:7px 10px;"><span style="background:#D4AF3722;color:#D4AF37;border:1px solid #D4AF3744;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Draft</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">Six months ago I committed to building...</td></tr>'
            '<tr style="background:#0F0F14;border-bottom:1px solid #1A1A22;"><td style="padding:7px 10px;color:#D0D0D0;">Saturday</td><td style="padding:7px 10px;color:#D0D0D0;">Newsletter</td><td style="padding:7px 10px;color:#D0D0D0;font-weight:600;">10 lessons from building in public</td><td style="padding:7px 10px;"><span style="background:#7ABCFF22;color:#7ABCFF;border:1px solid #7ABCFF44;border-radius:6px;padding:2px 8px;font-weight:700;font-size:0.72rem;">Posted</span></td><td style="padding:7px 10px;color:#666;font-style:italic;">Subject: What nobody tells you about...</td></tr>'
            '</tbody></table>'
            '<div style="margin-top:14px;">'
            '<button style="background:#1A1A22;border:1px solid #2A2A34;color:#D4AF37;border-radius:8px;padding:6px 16px;font-size:0.82rem;font-weight:600;cursor:pointer;">📥 Export Calendar as CSV</button>'
            '</div>'
        )
        await page.evaluate(
            "(html) => { const div = document.createElement('div'); div.id = 'mock-cal';"
            " div.style.cssText = 'position:fixed;top:60px;left:340px;right:20px;z-index:9999;"
            "background:#0E0E10;padding:24px;border-radius:14px;border:1px solid #2A2A30;"
            "font-family:-apple-system,Segoe UI,sans-serif;';"
            " div.innerHTML = html; document.body.appendChild(div); }",
            cal_html
        )
        await asyncio.sleep(0.5)
        cal_el = page.locator("#mock-cal")
        await cal_el.screenshot(path=str(DOCS / "screenshot_calendar.png"))
        await page.evaluate("document.getElementById('mock-cal').remove()")
        print("  → screenshot_calendar.png")

        # ── 6. History sidebar close-up ────────────────────────────────────────
        print("Screenshot: history sidebar detail...")
        hist_html = (
            '<div style="font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">🕘 History</div>'
            '<select style="width:100%;background:#0D0D12;color:#CCC;border:1px solid #222230;border-radius:8px;padding:6px 10px;font-size:0.82rem;margin-bottom:10px;">'
            '<option>2026-05-31 11:42  How AI Is Changing Con...</option>'
            '<option>2026-05-31 10:18  10 Lessons From Buildin...</option>'
            '<option>2026-05-30 21:05  The Future of Work: 5 Pr...</option>'
            '<option>2026-05-30 18:33  Why Most Startups Fail At...</option>'
            '<option>2026-05-29 14:12  Content Strategy for 2026...</option>'
            '</select>'
            '<div style="display:flex;gap:8px;">'
            '<button style="flex:1;background:linear-gradient(135deg,#B8860B,#D4AF37);color:#000;font-weight:700;border:none;border-radius:8px;padding:7px;font-size:0.82rem;cursor:pointer;">📂 Load</button>'
            '<button style="flex:1;background:#1A1A1F;color:#FF5252;font-weight:700;border:1px solid #3A1A1A;border-radius:8px;padding:7px;font-size:0.82rem;cursor:pointer;">🗑️ Delete</button>'
            '</div>'
            '<div style="margin-top:12px;padding-top:12px;border-top:1px solid #1E1E26;color:#555;font-size:0.72rem;">5 runs saved · Auto-saved on every generation</div>'
        )
        await page.evaluate(
            "(html) => { const div = document.createElement('div'); div.id = 'mock-history';"
            " div.style.cssText = 'position:fixed;top:60px;left:10px;width:300px;z-index:9999;"
            "background:#0A0A0D;padding:16px;border-radius:14px;border:1px solid #1E1E26;"
            "font-family:-apple-system,Segoe UI,sans-serif;';"
            " div.innerHTML = html; document.body.appendChild(div); }",
            hist_html
        )
        await asyncio.sleep(0.5)
        hist_el = page.locator("#mock-history")
        await hist_el.screenshot(path=str(DOCS / "screenshot_history.png"))
        await page.evaluate("document.getElementById('mock-history').remove()")
        print("  → screenshot_history.png")

        await browser.close()
        print("\nAll screenshots saved to docs/")


asyncio.run(main())
