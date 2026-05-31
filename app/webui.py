import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from goldmine.engine import GoldMineEngine

st.set_page_config(
    page_title="ContentGoldMine",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* ── Global ── */
  html, body, [class*="css"] { font-family: -apple-system, 'Segoe UI', sans-serif; }
  .block-container { padding: 2rem 2.5rem 3rem; max-width: 1200px; }

  /* ── Hero ── */
  .hero { text-align: center; padding: 1.5rem 0 2rem; }
  .hero-title {
    font-size: 3.2rem; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #B8860B, #D4AF37, #FFD700, #D4AF37, #B8860B);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
  }
  .hero-sub {
    font-size: 1.15rem; color: #888; font-weight: 400; margin-bottom: 0;
  }
  .hero-badges { margin-top: 0.8rem; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
  .badge {
    background: #1A1A1F; border: 1px solid #2A2A30;
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.78rem; color: #888;
  }

  /* ── Input card ── */
  .input-card {
    background: #13131A; border: 1px solid #222230;
    border-radius: 16px; padding: 1.8rem 2rem; margin-bottom: 1.5rem;
  }

  /* ── Mine button ── */
  div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #B8860B 0%, #D4AF37 40%, #FFD700 100%) !important;
    color: #000 !important; font-weight: 800 !important;
    font-size: 1.1rem !important; border: none !important;
    border-radius: 10px !important; padding: 0.8rem 2rem !important;
    width: 100% !important; letter-spacing: 0.3px !important;
    transition: opacity 0.15s, transform 0.15s !important;
  }
  div[data-testid="stButton"] > button:hover {
    opacity: 0.92 !important; transform: translateY(-1px) !important;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] { background: #0A0A0D; border-right: 1px solid #1E1E26; }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stTextInput label { color: #999 !important; font-size: 0.82rem !important; }

  /* ── Tweet cards ── */
  .tweet-card {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1.1rem 1.4rem;
    margin-bottom: 0.7rem; position: relative;
  }
  .tweet-card:hover { border-color: #D4AF37; }
  .tweet-num { color: #D4AF37; font-weight: 700; font-size: 0.85rem; margin-bottom: 0.35rem; }
  .tweet-text { color: #E0E0E0; font-size: 1rem; line-height: 1.55; white-space: pre-wrap; }
  .tweet-chars {
    position: absolute; top: 10px; right: 14px;
    font-size: 0.72rem; font-weight: 600; padding: 2px 8px;
    border-radius: 10px;
  }
  .chars-ok { background: #0d2d0d; color: #4CAF50; }
  .chars-warn { background: #2d1f00; color: #FF9800; }
  .chars-over { background: #2d0000; color: #F44336; }

  /* ── LinkedIn preview ── */
  .li-card {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1.6rem 2rem; line-height: 1.7;
    color: #D8D8D8; font-size: 1rem; white-space: pre-wrap;
  }
  .li-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;
    padding-bottom: 1rem; border-bottom: 1px solid #222230;
  }
  .li-avatar {
    width: 48px; height: 48px; border-radius: 50%;
    background: linear-gradient(135deg, #D4AF37, #8B6914);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; font-weight: 900; color: #000; flex-shrink: 0;
  }
  .li-name { font-weight: 700; color: #E0E0E0; font-size: 0.95rem; }
  .li-title { color: #777; font-size: 0.82rem; margin-top: 1px; }

  /* ── Newsletter preview ── */
  .nl-subject {
    background: #13131A; border: 1px solid #D4AF37;
    border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 0.6rem;
  }
  .nl-subject-label { font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
  .nl-subject-text { font-size: 1.1rem; font-weight: 700; color: #FFD700; margin-top: 2px; }
  .nl-body {
    background: #13131A; border: 1px solid #222230;
    border-radius: 14px; padding: 1.8rem 2rem; color: #D8D8D8; line-height: 1.8;
  }

  /* ── Video script ── */
  .script-section { margin-bottom: 1rem; }
  .script-label {
    display: inline-block; font-size: 0.72rem; font-weight: 800;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 6px; margin-bottom: 6px;
  }
  .label-hook { background: #D4AF3722; color: #FFD700; border: 1px solid #D4AF3744; }
  .label-point { background: #1A2A3A; color: #7ABCFF; border: 1px solid #2A4A6A; }
  .label-payoff { background: #1A2A1A; color: #7AFF9A; border: 1px solid #2A4A2A; }
  .label-cta { background: #2A1A1A; color: #FF9A7A; border: 1px solid #4A2A2A; }
  .script-text { color: #D8D8D8; font-size: 1rem; line-height: 1.7; white-space: pre-wrap; padding-left: 2px; }

  /* ── Stat chips ── */
  .chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.2rem; }
  .chip {
    background: #1A1A22; border: 1px solid #2A2A34;
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.8rem; color: #D4AF37; font-weight: 600;
  }

  /* ── Download button ── */
  .dl-row { display: flex; gap: 8px; margin-top: 0.8rem; }

  /* ── Copy area ── */
  .stTextArea textarea {
    background: #0D0D12 !important; color: #CCCCCC !important;
    border: 1px solid #222230 !important; border-radius: 10px !important;
    font-size: 0.9rem !important; font-family: 'Menlo', monospace !important;
  }

  /* ── Success banner ── */
  .success-banner {
    background: linear-gradient(135deg, #0D1F0D, #0D1A0D);
    border: 1px solid #1E4D1E; border-radius: 12px;
    padding: 1rem 1.4rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 10px;
    color: #7AFF9A; font-weight: 600;
  }

  /* ── Tab styling ── */
  button[data-baseweb="tab"] {
    font-size: 0.9rem !important; font-weight: 600 !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    color: #D4AF37 !important;
    border-bottom: 2px solid #D4AF37 !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">⛏️ ContentGoldMine</div>
  <div class="hero-sub">One input → five platform-ready formats, instantly.</div>
  <div class="hero-badges">
    <span class="badge">𝕏 Thread</span>
    <span class="badge">💼 LinkedIn</span>
    <span class="badge">📧 Newsletter</span>
    <span class="badge">🎠 Carousel</span>
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
    model_defaults = {
        "openai": "gpt-4o",
        "anthropic": "claude-sonnet-4-6",
        "gemini": "gemini-1.5-pro",
    }
    model = st.text_input("Model", value=model_defaults[provider])
    api_key = st.text_input("API Key", type="password", placeholder="sk-...")

    st.divider()
    language = st.selectbox(
        "Output Language",
        ["English", "Spanish", "French", "German", "Portuguese", "Hindi", "Arabic"],
    )
    carousel_theme = st.selectbox(
        "Carousel Theme",
        ["gold", "dark", "light"],
        format_func=lambda x: {"gold": "⭐ Gold (Premium)", "dark": "🌑 Dark (Purple)", "light": "☀️ Light (Blue)"}[x],
    )

    st.divider()
    st.markdown("**Select Platforms**")
    platforms = {
        "x_thread":    st.checkbox("𝕏  Thread", value=True),
        "linkedin":    st.checkbox("💼  LinkedIn Post", value=True),
        "newsletter":  st.checkbox("📧  Newsletter", value=True),
        "carousel":    st.checkbox("🎠  Instagram Carousel", value=True),
        "video_script":st.checkbox("🎬  Video Script", value=True),
    }
    selected_platforms = [k for k, v in platforms.items() if v]

    st.divider()
    st.caption("⛏️ [ContentGoldMine](https://github.com/mohitagw15856/ContentGoldMine)")


# ── Input ─────────────────────────────────────────────────────────────────────
input_type = st.radio(
    "Input Type",
    ["url", "youtube", "text"],
    horizontal=True,
    format_func=lambda x: {
        "url": "🔗  Blog / Article URL",
        "youtube": "▶️  YouTube Video",
        "text": "✍️  Raw Text",
    }[x],
)

if input_type == "text":
    user_input = st.text_area(
        "Paste your content",
        height=140,
        placeholder="Paste your blog post, notes, podcast transcript, or any content...",
        label_visibility="collapsed",
    )
else:
    placeholder = {
        "url": "https://example.com/your-article",
        "youtube": "https://www.youtube.com/watch?v=...",
    }[input_type]
    user_input = st.text_input("URL", placeholder=placeholder, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate = st.button("⛏️  Mine the Gold", use_container_width=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def char_chip(n: int) -> str:
    cls = "chars-ok" if n <= 240 else "chars-warn" if n <= 280 else "chars-over"
    return f'<span class="tweet-chars {cls}">{n} / 280</span>'


def render_thread(output: dict):
    tweets = output.get("tweets") or []
    for tweet in tweets:
        text = tweet.lstrip("0123456789/").strip()
        num_part = tweet[:tweet.index("/") + 1] if "/" in tweet[:4] else ""
        n = len(text)
        st.markdown(f"""
<div class="tweet-card">
  {char_chip(n)}
  <div class="tweet-num">{num_part or "—"}</div>
  <div class="tweet-text">{text}</div>
</div>""", unsafe_allow_html=True)


def render_linkedin(output: dict):
    text = output.get("raw", "")
    st.markdown(f"""
<div class="li-card">
  <div class="li-header">
    <div class="li-avatar">M</div>
    <div>
      <div class="li-name">Mohit</div>
      <div class="li-title">Content Creator · ContentGoldMine</div>
    </div>
  </div>
  {text.replace(chr(10), '<br>')}
</div>""", unsafe_allow_html=True)


def render_newsletter(output: dict):
    raw = output.get("raw", "")
    lines = raw.split("\n")
    subject = ""
    preview = ""
    body_lines = []
    for i, line in enumerate(lines):
        if line.lower().startswith("subject"):
            subject = line.split(":", 1)[-1].strip().strip("*")
        elif line.lower().startswith("preview"):
            preview = line.split(":", 1)[-1].strip()
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    if subject:
        st.markdown(f"""
<div class="nl-subject">
  <div class="nl-subject-label">Subject Line</div>
  <div class="nl-subject-text">{subject}</div>
  {'<div style="color:#888;font-size:0.82rem;margin-top:4px;">' + preview + '</div>' if preview else ''}
</div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="nl-body">', unsafe_allow_html=True)
    st.markdown(body)
    st.markdown("</div>", unsafe_allow_html=True)


def render_video_script(output: dict):
    raw = output.get("raw", "")
    import re
    label_map = {
        "HOOK": ("label-hook", "🎯 Hook"),
        "POINT 1": ("label-point", "📍 Point 1"),
        "POINT 2": ("label-point", "📍 Point 2"),
        "POINT 3": ("label-point", "📍 Point 3"),
        "PAYOFF": ("label-payoff", "💡 Payoff"),
        "CTA": ("label-cta", "📢 CTA"),
    }
    sections = re.split(r"\[([A-Z][A-Z 0-9]+)\s*[—–-]?[^\]]*\]", raw)
    if len(sections) <= 1:
        st.markdown(f'<div class="script-text">{raw}</div>', unsafe_allow_html=True)
        return
    result_html = ""
    i = 0
    if sections[0].strip():
        result_html += f'<div class="script-section"><div class="script-text">{sections[0].strip()}</div></div>'
        i = 1
    while i < len(sections) - 1:
        key = sections[i].strip()
        text = sections[i + 1].strip() if i + 1 < len(sections) else ""
        cls, label = label_map.get(key, ("label-point", f"▸ {key}"))
        result_html += f"""
<div class="script-section">
  <span class="script-label {cls}">{label}</span>
  <div class="script-text">{text}</div>
</div>"""
        i += 2
    st.markdown(result_html, unsafe_allow_html=True)


# ── Generate ──────────────────────────────────────────────────────────────────
if generate:
    if not api_key:
        st.error("Add your API key in the sidebar first.")
        st.stop()
    if not user_input or not user_input.strip():
        st.error("Enter a URL or paste some text to repurpose.")
        st.stop()
    if not selected_platforms:
        st.error("Select at least one output platform in the sidebar.")
        st.stop()

    engine = GoldMineEngine(
        llm_provider=provider,
        api_key=api_key,
        model=model,
        language=language,
        carousel_theme=carousel_theme,
    )

    with st.spinner("⛏️ Mining your content gold..."):
        try:
            results = engine.repurpose(input_type, user_input, selected_platforms)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    source = results["source"]
    n_ok = sum(1 for v in results["outputs"].values() if "error" not in v)
    st.markdown(f"""
<div class="success-banner">
  ✅ &nbsp; <b>{source.get('title','your content')}</b> repurposed into <b>{n_ok}</b> formats.
</div>""", unsafe_allow_html=True)

    tab_labels = []
    for k, v in results["outputs"].items():
        ok = "error" not in v
        icons = {"x_thread": "𝕏", "linkedin": "💼", "newsletter": "📧", "carousel": "🎠", "video_script": "🎬"}
        names = {"x_thread": "Thread", "linkedin": "LinkedIn", "newsletter": "Newsletter", "carousel": "Carousel", "video_script": "Script"}
        tab_labels.append(f"{'✅' if ok else '❌'} {icons.get(k,'')} {names.get(k, k)}")

    tabs = st.tabs(tab_labels)

    for tab, (key, output) in zip(tabs, results["outputs"].items()):
        with tab:
            if "error" in output:
                st.error(f"Failed: {output['error']}")
                continue

            # Stat chips
            chips = []
            if "tweet_count" in output:
                chips.append(f"🐦 {output['tweet_count']} tweets")
            if "char_count" in output:
                chips.append(f"📝 {output['char_count']:,} chars")
            if "word_count" in output:
                chips.append(f"📖 {output['word_count']} words")
            if "slide_count" in output:
                chips.append(f"🖼️ {output['slide_count']} slides")
            if "estimated_duration_sec" in output:
                chips.append(f"⏱️ ~{output['estimated_duration_sec']}s")
            if chips:
                chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
                st.markdown(f'<div class="chips">{chip_html}</div>', unsafe_allow_html=True)

            # Platform-specific rendering
            if key == "x_thread":
                render_thread(output)
            elif key == "linkedin":
                render_linkedin(output)
            elif key == "newsletter":
                render_newsletter(output)
            elif key == "video_script":
                render_video_script(output)
            elif key == "carousel":
                if output.get("image_paths"):
                    cols_per_row = 4
                    paths = output["image_paths"]
                    for row_start in range(0, len(paths), cols_per_row):
                        row = paths[row_start:row_start + cols_per_row]
                        cols = st.columns(len(row))
                        for col, img_path in zip(cols, row):
                            with col:
                                st.image(img_path, use_container_width=True)
                    st.caption(f"📁 Slides saved to `assets/carousel_output/`")

            # Raw copy area (collapsed by default for cleaner look)
            with st.expander("📋 Copy raw text"):
                st.text_area("", value=output["raw"], height=280, key=f"raw_{key}", label_visibility="collapsed")
