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

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #D4AF37, #FFD700, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 0.5rem 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .platform-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #D4AF37;
        margin-bottom: 1rem;
    }
    .stat-chip {
        background: #2a2a3e;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        color: #D4AF37;
        display: inline-block;
        margin: 0.2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37, #FFD700);
        color: #000;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FFD700, #D4AF37);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">⛏️ ContentGoldMine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Turn one piece of content into gold across every platform — instantly.</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.divider()

    provider = st.selectbox(
        "LLM Provider",
        ["openai", "anthropic", "gemini"],
        format_func=lambda x: {"openai": "OpenAI (GPT-4o)", "anthropic": "Anthropic (Claude)", "gemini": "Google (Gemini)"}[x],
    )

    model_defaults = {"openai": "gpt-4o", "anthropic": "claude-sonnet-4-6", "gemini": "gemini-1.5-pro"}
    model = st.text_input("Model", value=model_defaults[provider])

    api_key = st.text_input("API Key", type="password", placeholder="Paste your API key here")

    st.divider()
    language = st.selectbox("Output Language", ["English", "Spanish", "French", "German", "Portuguese", "Hindi", "Japanese", "Arabic"])

    carousel_theme = st.selectbox("Carousel Theme", ["gold", "dark", "light"])

    st.divider()
    st.markdown("### 📤 Select Platforms")
    platforms = {
        "x_thread": st.checkbox("🐦 X Thread", value=True),
        "linkedin": st.checkbox("💼 LinkedIn Post", value=True),
        "newsletter": st.checkbox("📧 Newsletter Section", value=True),
        "carousel": st.checkbox("🎠 Instagram Carousel", value=True),
        "video_script": st.checkbox("🎬 Video Script", value=True),
    }
    selected_platforms = [k for k, v in platforms.items() if v]

    st.divider()
    st.markdown("**ContentGoldMine** · [GitHub](https://github.com/mohit/ContentGoldMine)")

# ── Main Input ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    input_type = st.radio(
        "Input Type",
        ["url", "youtube", "text"],
        format_func=lambda x: {"url": "🔗 Blog / Article URL", "youtube": "▶️ YouTube Video", "text": "✍️ Raw Text"}[x],
    )

with col2:
    if input_type == "text":
        user_input = st.text_area(
            "Paste your content",
            height=160,
            placeholder="Paste your blog post, notes, or any text here...",
        )
    else:
        placeholder = {
            "url": "https://yourblog.com/amazing-post",
            "youtube": "https://www.youtube.com/watch?v=...",
        }[input_type]
        user_input = st.text_input("Enter URL", placeholder=placeholder)

# ── Generate Button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate = st.button("⛏️ Mine the Gold")

# ── Results ───────────────────────────────────────────────────────────────────
if generate:
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        st.stop()
    if not user_input or not user_input.strip():
        st.error("Please enter a URL or some text to repurpose.")
        st.stop()
    if not selected_platforms:
        st.error("Please select at least one output platform.")
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
    st.success(f"✅ Done! Repurposed **{source.get('title', 'your content')}** into {len(results['outputs'])} formats.")
    st.divider()

    tabs = st.tabs([
        f"{v.get('emoji','') if not isinstance(v, dict) or 'error' not in v else '❌'} {k.replace('_', ' ').title()}"
        for k, v in results["outputs"].items()
    ])

    for tab, (key, output) in zip(tabs, results["outputs"].items()):
        with tab:
            if "error" in output:
                st.error(f"Failed: {output['error']}")
                continue

            # Stats chips
            stats_html = ""
            if "tweet_count" in output:
                stats_html += f'<span class="stat-chip">🐦 {output["tweet_count"]} tweets</span>'
            if "char_count" in output:
                stats_html += f'<span class="stat-chip">📝 {output["char_count"]} chars</span>'
            if "word_count" in output:
                stats_html += f'<span class="stat-chip">📖 {output["word_count"]} words</span>'
            if "slide_count" in output:
                stats_html += f'<span class="stat-chip">🖼️ {output["slide_count"]} slides</span>'
            if "estimated_duration_sec" in output:
                stats_html += f'<span class="stat-chip">⏱️ ~{output["estimated_duration_sec"]}s</span>'
            if stats_html:
                st.markdown(stats_html, unsafe_allow_html=True)

            # Carousel images
            if key == "carousel" and output.get("image_paths"):
                img_cols = st.columns(min(4, len(output["image_paths"])))
                for i, img_path in enumerate(output["image_paths"]):
                    with img_cols[i % len(img_cols)]:
                        st.image(img_path, use_container_width=True)
                st.markdown("---")

            # Raw text output
            st.text_area(
                "Copy to clipboard",
                value=output["raw"],
                height=350,
                key=f"output_{key}",
            )

            # Copy button hint
            st.caption("⬆️ Click the text area, Ctrl+A then Ctrl+C to copy all")
