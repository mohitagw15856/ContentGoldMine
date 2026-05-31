import streamlit as st
from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from goldmine.engine import GoldMineEngine
from goldmine.key_store import save_key, load_key
from goldmine.llm import get_llm_provider


def _unwrap(e: Exception) -> str:
    """Pull the real error out of a tenacity RetryError."""
    if hasattr(e, "last_attempt"):
        inner = e.last_attempt.exception()
        if inner is not None:
            return str(inner)
    return str(e)


def _is_auth_error(msg: str) -> bool:
    msg = msg.lower()
    return any(k in msg for k in ("authentication", "api key", "invalid key", "incorrect api", "permission denied", "unauthenticated", "401", "403"))

st.set_page_config(
    page_title="ContentGoldMine",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  html, body, [class*="css"] { font-family: -apple-system, 'Segoe UI', sans-serif; }
  .block-container { padding: 2rem 2.5rem 3rem; max-width: 1200px; }

  .hero { text-align: center; padding: 1.5rem 0 1.8rem; }
  .hero-title {
    font-size: 3.2rem; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #B8860B, #D4AF37, #FFD700, #D4AF37, #B8860B);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
  }
  .hero-sub { font-size: 1.1rem; color: #888; margin-bottom: 0.8rem; }
  .hero-badges { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
  .badge {
    background: #1A1A1F; border: 1px solid #2A2A30;
    border-radius: 20px; padding: 4px 14px; font-size: 0.78rem; color: #888;
  }

  div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #B8860B 0%, #D4AF37 40%, #FFD700 100%) !important;
    color: #000 !important; font-weight: 800 !important; font-size: 1.05rem !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.75rem 2rem !important; width: 100% !important; letter-spacing: 0.3px !important;
    transition: opacity 0.15s, transform 0.15s !important;
  }
  div[data-testid="stButton"] > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

  section[data-testid="stSidebar"] { background: #0A0A0D; border-right: 1px solid #1E1E26; }

  .key-saved    { color: #4CAF50; font-size: 0.8rem; font-weight: 600; padding: 2px 0; }
  .key-error    { color: #FF5252; font-size: 0.8rem; font-weight: 600; padding: 2px 0; }
  .auth-banner  {
    background: #1F0A0A; border: 1px solid #7F1F1F; border-radius: 12px;
    padding: 1rem 1.4rem; margin-bottom: 1rem; color: #FF7070; font-size: 0.95rem;
  }
  .auth-banner b { color: #FF9090; }

  .tweet-card {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1rem 1.3rem 1rem 1.3rem;
    margin-bottom: 0.65rem; position: relative;
  }
  .tweet-card:hover { border-color: #D4AF3766; }
  .tweet-num { color: #D4AF37; font-weight: 700; font-size: 0.82rem; margin-bottom: 0.3rem; }
  .tweet-text { color: #E0E0E0; font-size: 0.97rem; line-height: 1.55; white-space: pre-wrap; padding-right: 60px; }
  .tweet-chars {
    position: absolute; top: 12px; right: 14px;
    font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px;
  }
  .chars-ok  { background: #0d2d0d; color: #4CAF50; }
  .chars-warn { background: #2d1f00; color: #FF9800; }
  .chars-over { background: #2d0000; color: #F44336; }

  .li-card {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1.5rem 1.8rem; color: #D0D0D0;
    font-size: 0.97rem; line-height: 1.75;
  }
  .li-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;
    padding-bottom: 1rem; border-bottom: 1px solid #222230;
  }
  .li-avatar {
    width: 46px; height: 46px; border-radius: 50%;
    background: linear-gradient(135deg, #D4AF37, #8B6914);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 900; color: #000; flex-shrink: 0;
  }
  .li-name { font-weight: 700; color: #E0E0E0; font-size: 0.93rem; }
  .li-meta { color: #666; font-size: 0.8rem; margin-top: 1px; }

  .nl-subject {
    background: #13131A; border: 1px solid #D4AF3766; border-radius: 10px;
    padding: 0.85rem 1.2rem; margin-bottom: 0.55rem;
  }
  .nl-label { font-size: 0.68rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
  .nl-subject-text { font-size: 1.05rem; font-weight: 700; color: #FFD700; margin-top: 2px; }
  .nl-preview-text { color: #777; font-size: 0.82rem; margin-top: 3px; font-style: italic; }
  .nl-body {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1.6rem 2rem; color: #D0D0D0; line-height: 1.8;
  }

  .script-section { margin-bottom: 1.1rem; }
  .script-label {
    display: inline-block; font-size: 0.68rem; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 6px; margin-bottom: 6px;
  }
  .label-hook   { background: #D4AF3722; color: #FFD700;  border: 1px solid #D4AF3744; }
  .label-point  { background: #1A2A3A;   color: #7ABCFF;  border: 1px solid #2A4A6A; }
  .label-payoff { background: #1A2A1A;   color: #7AFF9A;  border: 1px solid #2A4A2A; }
  .label-cta    { background: #2A1A1A;   color: #FF9A7A;  border: 1px solid #4A2A2A; }
  .script-text  { color: #D0D0D0; font-size: 0.97rem; line-height: 1.7; white-space: pre-wrap; }

  .chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.1rem; }
  .chip {
    background: #1A1A22; border: 1px solid #2A2A34;
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.78rem; color: #D4AF37; font-weight: 600;
  }

  .success-banner {
    background: linear-gradient(135deg, #0D1F0D, #0D1A0D);
    border: 1px solid #1E4D1E; border-radius: 12px;
    padding: 0.9rem 1.3rem; margin-bottom: 1.4rem;
    color: #7AFF9A; font-weight: 600;
  }

  .batch-url-result {
    background: #0F0F14; border: 1px solid #222230;
    border-radius: 14px; padding: 1.4rem 1.8rem; margin-bottom: 1rem;
  }

  .stTextArea textarea {
    background: #0D0D12 !important; color: #CCCCCC !important;
    border: 1px solid #222230 !important; border-radius: 10px !important;
    font-size: 0.88rem !important;
  }

  button[data-baseweb="tab"][aria-selected="true"] {
    color: #D4AF37 !important; border-bottom: 2px solid #D4AF37 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
PLATFORM_ICONS  = {"x_thread": "𝕏", "linkedin": "💼", "newsletter": "📧", "carousel": "🎠", "video_script": "🎬"}
PLATFORM_LABELS = {"x_thread": "X Thread", "linkedin": "LinkedIn", "newsletter": "Newsletter", "carousel": "Carousel", "video_script": "Script"}
PLATFORM_STEPS  = {
    "x_thread":    "𝕏  Crafting viral thread...",
    "linkedin":    "💼  Writing LinkedIn post...",
    "newsletter":  "📧  Composing newsletter...",
    "carousel":    "🎠  Building carousel slides...",
    "video_script":"🎬  Scripting video...",
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">⛏️ ContentGoldMine</div>
  <div class="hero-sub">One input → five platform-ready formats, instantly.</div>
  <div class="hero-badges">
    <span class="badge">𝕏 Thread</span><span class="badge">💼 LinkedIn</span>
    <span class="badge">📧 Newsletter</span><span class="badge">🎠 Carousel</span>
    <span class="badge">🎬 Video Script</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.divider()

    provider = st.selectbox(
        "LLM Provider",
        ["openai", "anthropic", "gemini"],
        format_func=lambda x: {
            "openai": "🟢 OpenAI (GPT-4o)",
            "anthropic": "🟣 Anthropic (Claude)",
            "gemini": "🔵 Google (Gemini)",
        }[x],
    )

    model_defaults = {"openai": "gpt-4o", "anthropic": "claude-sonnet-4-6", "gemini": "gemini-1.5-pro"}
    model = st.text_input("Model", value=model_defaults[provider])

    # ── API Key with memory ────────────────────────────────────────────────────
    st.markdown("**API Key**")

    # Load saved key when provider changes
    _provider_key = f"_loaded_{provider}"
    if not st.session_state.get(_provider_key):
        stored = load_key(provider)
        if stored:
            st.session_state["_api_key"] = stored
        st.session_state[_provider_key] = True

    key_col, save_col = st.columns([4, 1])
    with key_col:
        api_key = st.text_input(
            "key",
            type="password",
            placeholder="Paste your API key → press Enter",
            key="_api_key",
            label_visibility="collapsed",
        )
    with save_col:
        st.write("")
        save_clicked = st.button("💾", key="save_key_btn", help="Save key locally so you never have to paste it again")

    if save_clicked and api_key:
        save_key(provider, api_key)
        st.session_state["_just_saved"] = True

    if st.session_state.pop("_just_saved", False):
        st.markdown('<div class="key-saved">✅ Saved — won\'t ask again</div>', unsafe_allow_html=True)
    elif load_key(provider):
        st.markdown('<div class="key-saved">🔐 Using saved key</div>', unsafe_allow_html=True)
    else:
        st.caption("Hit 💾 to save your key locally")

    # ── Test Key button ────────────────────────────────────────────────────────
    if st.button("🔑 Test API Key", key="test_key_btn", use_container_width=True):
        if not api_key:
            st.error("Paste a key first.")
        else:
            with st.spinner("Checking key..."):
                try:
                    provider_obj = get_llm_provider(provider, api_key, model)
                    provider_obj.test_connection()
                    st.session_state["_key_status"] = "ok"
                except Exception as e:
                    st.session_state["_key_status"] = _unwrap(e)

    ks = st.session_state.get("_key_status")
    if ks == "ok":
        st.markdown('<div class="key-saved">✅ Key is valid — ready to mine!</div>', unsafe_allow_html=True)
    elif ks:
        st.markdown(f'<div class="key-error">❌ {ks[:120]}</div>', unsafe_allow_html=True)

    st.divider()
    language = st.selectbox("Output Language", ["English", "Spanish", "French", "German", "Portuguese", "Hindi", "Arabic"])

    tone = st.selectbox(
        "Tone & Persona",
        ["Default", "Professional", "Casual & Fun", "Contrarian", "Educational", "Storytelling"],
        help="Shapes the voice and style of every output.",
    )

    brand_voice = st.text_area(
        "Brand Voice (optional)",
        height=90,
        placeholder="e.g. I'm a no-BS startup founder. I use plain English, short sentences, and I never use buzzwords like 'leverage' or 'synergy'.",
        help="Injected into every prompt. Your outputs will sound like you.",
    )

    carousel_theme = st.selectbox(
        "Carousel Theme",
        ["gold", "dark", "light"],
        format_func=lambda x: {"gold": "⭐ Gold", "dark": "🌑 Dark", "light": "☀️ Light"}[x],
    )

    st.divider()
    st.markdown("**Platforms**")
    platforms = {
        "x_thread":    st.checkbox("𝕏  X Thread",           value=True),
        "linkedin":    st.checkbox("💼  LinkedIn Post",       value=True),
        "newsletter":  st.checkbox("📧  Newsletter",          value=True),
        "carousel":    st.checkbox("🎠  Instagram Carousel",  value=True),
        "video_script":st.checkbox("🎬  Video Script",        value=True),
    }
    selected_platforms = [k for k, v in platforms.items() if v]

    st.divider()
    st.caption("⛏️ [ContentGoldMine on GitHub](https://github.com/mohitagw15856/ContentGoldMine)")


# ── Helpers ───────────────────────────────────────────────────────────────────
def char_chip(n: int) -> str:
    cls = "chars-ok" if n <= 240 else "chars-warn" if n <= 280 else "chars-over"
    return f'<span class="tweet-chars {cls}">{n}/280</span>'

def render_thread(output: dict):
    for tweet in output.get("tweets") or []:
        body = tweet.lstrip("0123456789/").strip()
        num = tweet[:tweet.index("/")+1] if "/" in tweet[:4] else "—"
        n = len(body)
        st.markdown(f"""<div class="tweet-card">{char_chip(n)}
<div class="tweet-num">{num}</div>
<div class="tweet-text">{body}</div></div>""", unsafe_allow_html=True)

def render_linkedin(output: dict):
    body = output.get("raw","").replace("\n","<br>")
    st.markdown(f"""<div class="li-card"><div class="li-header">
<div class="li-avatar">M</div>
<div><div class="li-name">Mohit</div><div class="li-meta">Content Creator · ContentGoldMine</div></div>
</div>{body}</div>""", unsafe_allow_html=True)

def render_newsletter(output: dict):
    raw = output.get("raw","")
    lines = raw.split("\n")
    subject, preview, body_lines = "", "", []
    for line in lines:
        ll = line.lower()
        if ll.startswith("subject"):
            subject = line.split(":",1)[-1].strip().strip("*_")
        elif ll.startswith("preview"):
            preview = line.split(":",1)[-1].strip()
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    if subject:
        st.markdown(f"""<div class="nl-subject">
<div class="nl-label">Subject Line</div>
<div class="nl-subject-text">{subject}</div>
{'<div class="nl-preview-text">' + preview + '</div>' if preview else ''}
</div>""", unsafe_allow_html=True)
    st.markdown('<div class="nl-body">', unsafe_allow_html=True)
    st.markdown(body)
    st.markdown("</div>", unsafe_allow_html=True)

def render_video_script(output: dict):
    raw = output.get("raw","")
    label_map = {
        "HOOK":    ("label-hook",   "🎯 Hook"),
        "POINT 1": ("label-point",  "📍 Point 1"),
        "POINT 2": ("label-point",  "📍 Point 2"),
        "POINT 3": ("label-point",  "📍 Point 3"),
        "PAYOFF":  ("label-payoff", "💡 Payoff"),
        "CTA":     ("label-cta",    "📢 CTA"),
    }
    sections = re.split(r"\[([A-Z][A-Z 0-9]+)[^\]]*\]", raw)
    if len(sections) <= 1:
        st.markdown(f'<div class="script-text">{raw}</div>', unsafe_allow_html=True)
        return
    html = ""
    if sections[0].strip():
        html += f'<div class="script-section"><div class="script-text">{sections[0].strip()}</div></div>'
    i = 1
    while i < len(sections) - 1:
        key = sections[i].strip()
        text = sections[i+1].strip() if i+1 < len(sections) else ""
        cls, label = label_map.get(key, ("label-point", f"▸ {key}"))
        html += f'<div class="script-section"><span class="script-label {cls}">{label}</span><div class="script-text">{text}</div></div>'
        i += 2
    st.markdown(html, unsafe_allow_html=True)

def render_carousel(output: dict):
    paths = output.get("image_paths") or []
    if not paths:
        st.info("No slides generated.")
        return
    for row_start in range(0, len(paths), 4):
        row = paths[row_start:row_start+4]
        cols = st.columns(len(row))
        for col, p in zip(cols, row):
            with col:
                st.image(p, use_container_width=True)
    st.caption(f"📁 Saved to `assets/carousel_output/`")

def render_output_tabs(outputs: dict):
    labels = [
        f"{'❌' if 'error' in v else PLATFORM_ICONS.get(k,'')} {PLATFORM_LABELS.get(k,k)}"
        for k, v in outputs.items()
    ]
    tabs = st.tabs(labels)
    for tab, (key, output) in zip(tabs, outputs.items()):
        with tab:
            if "error" in output:
                st.error(f"Failed: {output['error']}")
                continue
            chips = []
            if "tweet_count" in output:   chips.append(f"🐦 {output['tweet_count']} tweets")
            if "char_count"  in output:   chips.append(f"📝 {output['char_count']:,} chars")
            if "word_count"  in output:   chips.append(f"📖 {output['word_count']} words")
            if "slide_count" in output:   chips.append(f"🖼️ {output['slide_count']} slides")
            if "estimated_duration_sec" in output: chips.append(f"⏱️ ~{output['estimated_duration_sec']}s")
            if chips:
                st.markdown(
                    '<div class="chips">' + "".join(f'<span class="chip">{c}</span>' for c in chips) + "</div>",
                    unsafe_allow_html=True,
                )
            if   key == "x_thread":    render_thread(output)
            elif key == "linkedin":    render_linkedin(output)
            elif key == "newsletter":  render_newsletter(output)
            elif key == "video_script":render_video_script(output)
            elif key == "carousel":    render_carousel(output)

            st.caption("📋 Copy text — click the icon in the top-right corner of the box:")
            st.code(output["raw"], language=None, wrap_lines=True)


def build_zip(results: dict) -> bytes:
    import zipfile, io
    buf = io.BytesIO()
    title_slug = re.sub(r"[^\w\s-]", "", results["source"].get("title", "content"))[:40].strip().replace(" ", "_")
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for key, output in results["outputs"].items():
            if "error" in output or not output.get("raw"):
                continue
            fname = {"x_thread": "x_thread.txt", "linkedin": "linkedin.txt",
                     "newsletter": "newsletter.txt", "video_script": "video_script.txt",
                     "carousel": "carousel_script.txt"}.get(key, f"{key}.txt")
            zf.writestr(fname, output["raw"])
            if key == "carousel":
                for img_path in output.get("image_paths") or []:
                    p = Path(img_path)
                    if p.exists():
                        zf.write(p, f"carousel/{p.name}")
    buf.seek(0)
    return buf.read()


def run_with_status(engine: GoldMineEngine, input_type: str, value: str, slug: str = "default") -> dict | None:
    """Process content with a live status widget showing each step."""
    outputs = {}
    with st.status("⛏️ Mining content gold...", expanded=True) as status:
        try:
            st.write("🔍 Reading and extracting content...")
            content = engine.ingest(input_type, value)
            st.write(f"✅ Got: **{content['title']}** — {len(content['content']):,} characters extracted")

            for platform in selected_platforms:
                st.write(PLATFORM_STEPS[platform])
                try:
                    out = engine.process_platform(content, platform, carousel_slug=slug)
                    outputs[platform] = out
                    st.write(f"✅ {PLATFORM_LABELS[platform]} ready")
                except Exception as e:
                    err = _unwrap(e)
                    outputs[platform] = {"error": err, "raw": ""}
                    st.write(f"⚠️ {PLATFORM_LABELS[platform]} failed: {err[:120]}")

            n_ok = len([o for o in outputs.values() if "error" not in o])
            status.update(label=f"✅ Done — {n_ok}/{len(selected_platforms)} formats generated", state="complete", expanded=False)
            return {"source": content, "outputs": outputs}

        except Exception as e:
            err = _unwrap(e)
            status.update(label="❌ Failed", state="error", expanded=True)
            if _is_auth_error(err):
                st.session_state["_auth_error"] = err
            else:
                st.error(f"Error: {err}")
            return None


# ── Input ─────────────────────────────────────────────────────────────────────
batch_mode = st.toggle("📦 Batch Mode — process multiple URLs at once", value=False)

if batch_mode:
    st.markdown("**Enter URLs — one per line** (blog articles, YouTube videos, or mix both):")
    urls_raw = st.text_area(
        "urls",
        height=140,
        placeholder="https://medium.com/your-article\nhttps://youtube.com/watch?v=...\nhttps://yourblog.com/post",
        label_visibility="collapsed",
    )
    urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
    st.caption(f"{len(urls)} URL{'s' if len(urls)!=1 else ''} entered")
else:
    input_type = st.radio(
        "Input Type", ["url", "youtube", "text"], horizontal=True,
        format_func=lambda x: {"url": "🔗 Blog / Article URL", "youtube": "▶️ YouTube Video", "text": "✍️ Raw Text"}[x],
    )
    if input_type == "text":
        user_input = st.text_area("Content", height=130,
            placeholder="Paste your blog post, notes, podcast transcript...",
            label_visibility="collapsed")
    else:
        user_input = st.text_input("URL",
            placeholder={"url":"https://example.com/article","youtube":"https://youtube.com/watch?v=..."}[input_type],
            label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    label = f"⛏️ Mine {len(urls)} URLs" if batch_mode and 'urls' in dir() and urls else "⛏️ Mine the Gold"
    generate = st.button(label, use_container_width=True)


# ── Generate ──────────────────────────────────────────────────────────────────
# Show auth error banner if the last run had a bad key
if auth_err := st.session_state.pop("_auth_error", None):
    st.markdown(f"""<div class="auth-banner">
🔑 <b>Invalid API Key</b><br>
Your key was rejected by {provider.upper()}. Please check it and try again.<br>
<small style="opacity:0.7">{auth_err[:200]}</small>
</div>""", unsafe_allow_html=True)

if generate:
    if not api_key:
        st.error("Paste your API key in the sidebar — or hit 💾 to save one permanently.")
        st.stop()
    if not selected_platforms:
        st.error("Select at least one platform in the sidebar.")
        st.stop()

    engine = GoldMineEngine(
        llm_provider=provider, api_key=api_key, model=model,
        language=language, tone=tone, brand_voice=brand_voice,
        carousel_theme=carousel_theme,
    )

    # ── Batch mode ────────────────────────────────────────────────────────────
    if batch_mode:
        if not urls:
            st.error("Enter at least one URL in the box above.")
            st.stop()

        st.markdown(f"### Processing {len(urls)} URLs")
        all_results = []

        for i, url in enumerate(urls):
            st.markdown(f"#### {i+1}. `{url}`")
            input_t = "youtube" if ("youtube.com" in url or "youtu.be" in url) else "url"
            result = run_with_status(engine, input_t, url, slug=f"batch_{i}")
            if result:
                all_results.append(result)
                render_output_tabs(result["outputs"])
                zip_data = build_zip(result)
                title_slug = re.sub(r"[^\w]", "_", result["source"].get("title","content"))[:30]
                st.download_button(
                    f"📦 Download ZIP — {result['source'].get('title','')[:40]}",
                    data=zip_data,
                    file_name=f"contentgoldmine_{title_slug}.zip",
                    mime="application/zip",
                    key=f"zip_batch_{i}",
                )
            st.divider()

        n_ok = len(all_results)
        st.markdown(f'<div class="success-banner">✅ Batch complete — {n_ok}/{len(urls)} URLs processed successfully.</div>', unsafe_allow_html=True)

    # ── Single mode ───────────────────────────────────────────────────────────
    else:
        if not user_input or not user_input.strip():
            st.error("Enter a URL or paste some text first.")
            st.stop()

        result = run_with_status(engine, input_type, user_input)
        if result:
            source = result["source"]
            n_ok = sum(1 for v in result["outputs"].values() if "error" not in v)

            banner_col, zip_col = st.columns([3, 1])
            with banner_col:
                st.markdown(f'<div class="success-banner">✅ <b>{source.get("title","your content")}</b> → {n_ok} formats ready</div>', unsafe_allow_html=True)
            with zip_col:
                zip_data = build_zip(result)
                title_slug = re.sub(r"[^\w]", "_", source.get("title", "content"))[:30]
                st.download_button(
                    "📦 Download All as ZIP",
                    data=zip_data,
                    file_name=f"contentgoldmine_{title_slug}.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

            render_output_tabs(result["outputs"])
