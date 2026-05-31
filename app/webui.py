import streamlit as st
from pathlib import Path
import sys
import re
import io

sys.path.insert(0, str(Path(__file__).parent.parent))
from goldmine.engine import GoldMineEngine
from goldmine.key_store import save_key, load_key
from goldmine.llm import get_llm_provider
from goldmine.scorer import score_output
from goldmine.history import save_run, list_runs, load_run, delete_run
from goldmine.publisher.twitter import post_thread
from goldmine.publisher.linkedin import post_linkedin
from goldmine.publisher.webhook import post_webhook


def _unwrap(e: Exception) -> str:
    if hasattr(e, "last_attempt"):
        inner = e.last_attempt.exception()
        if inner is not None:
            return str(inner)
    return str(e)


def _is_auth_error(msg: str) -> bool:
    msg = msg.lower()
    return any(k in msg for k in ("authentication", "api key", "invalid key", "incorrect api",
                                  "permission denied", "unauthenticated", "401", "403"))


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

  .score-bar {
    display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
    background: #0F0F16; border: 1px solid #1E1E2A; border-radius: 10px;
    padding: 0.7rem 1rem; margin-bottom: 1rem;
  }
  .score-chip {
    display: flex; align-items: center; gap: 5px;
    font-size: 0.8rem; font-weight: 700;
  }
  .score-high { color: #4CAF50; }
  .score-mid  { color: #FF9800; }
  .score-low  { color: #F44336; }
  .score-tip  { color: #888; font-size: 0.78rem; font-style: italic; margin-left: 4px; }

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

  .history-item {
    background: #0F0F14; border: 1px solid #1E1E26; border-radius: 8px;
    padding: 0.6rem 0.9rem; margin-bottom: 0.4rem; cursor: pointer;
  }
  .history-title { font-size: 0.85rem; color: #D0D0D0; font-weight: 600; }
  .history-meta  { font-size: 0.72rem; color: #555; margin-top: 2px; }

  .cal-header { font-size: 1rem; font-weight: 800; color: #D4AF37; margin: 1.2rem 0 0.6rem; }

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
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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
    _provider_key = f"_loaded_{provider}"
    if not st.session_state.get(_provider_key):
        stored = load_key(provider)
        if stored:
            st.session_state["_api_key"] = stored
        st.session_state[_provider_key] = True

    key_col, save_col = st.columns([4, 1])
    with key_col:
        api_key = st.text_input(
            "key", type="password",
            placeholder="Paste your API key → press Enter",
            key="_api_key", label_visibility="collapsed",
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
        "Brand Voice (optional)", height=90,
        placeholder="e.g. I'm a no-BS startup founder. I use plain English, short sentences, and I never use buzzwords like 'leverage' or 'synergy'.",
        help="Injected into every prompt. Your outputs will sound like you.",
    )

    carousel_theme = st.selectbox(
        "Carousel Theme", ["gold", "dark", "light"],
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

    # ── Publishing credentials ─────────────────────────────────────────────────
    st.divider()
    with st.expander("📤 Publishing credentials"):
        st.caption("Store once — used by the Post buttons in each output tab.")

        tw_ck  = st.text_input("X Consumer Key",    type="password", key="tw_ck",  value=load_key("tw_consumer_key")  or "")
        tw_cs  = st.text_input("X Consumer Secret", type="password", key="tw_cs",  value=load_key("tw_consumer_secret") or "")
        tw_at  = st.text_input("X Access Token",    type="password", key="tw_at",  value=load_key("tw_access_token")  or "")
        tw_as  = st.text_input("X Access Secret",   type="password", key="tw_as",  value=load_key("tw_access_secret") or "")
        li_tok = st.text_input("LinkedIn Access Token", type="password", key="li_tok", value=load_key("linkedin_token") or "")
        wh_url = st.text_input("Webhook URL (Buffer/Zapier)", key="wh_url", value=load_key("webhook_url") or "",
                               placeholder="https://hooks.zapier.com/...")

        if st.button("💾 Save publishing keys", key="save_pub_keys"):
            for k, v in [("tw_consumer_key", tw_ck), ("tw_consumer_secret", tw_cs),
                         ("tw_access_token", tw_at), ("tw_access_secret", tw_as),
                         ("linkedin_token", li_tok), ("webhook_url", wh_url)]:
                if v:
                    save_key(k, v)
            st.success("Saved!")

    # ── History browser ────────────────────────────────────────────────────────
    st.divider()
    with st.expander("🕘 History"):
        runs = list_runs(30)
        if not runs:
            st.caption("No saved runs yet — generate something first!")
        else:
            run_options = {f"{r['created_at'][:16]}  {r['title'][:35]}": r["id"] for r in runs}
            selected_label = st.selectbox("Past runs", list(run_options.keys()), label_visibility="collapsed")
            selected_id = run_options[selected_label]

            hcol1, hcol2 = st.columns(2)
            with hcol1:
                if st.button("📂 Load", key="hist_load", use_container_width=True):
                    st.session_state["_history_load_id"] = selected_id
            with hcol2:
                if st.button("🗑️ Delete", key="hist_del", use_container_width=True):
                    delete_run(selected_id)
                    st.rerun()

    st.divider()
    st.caption("⛏️ [ContentGoldMine on GitHub](https://github.com/mohitagw15856/ContentGoldMine)")


# ── Helpers ───────────────────────────────────────────────────────────────────
def char_chip(n: int) -> str:
    cls = "chars-ok" if n <= 240 else "chars-warn" if n <= 280 else "chars-over"
    return f'<span class="tweet-chars {cls}">{n}/280</span>'


def _score_color(v: int) -> str:
    if v >= 8: return "score-high"
    if v >= 5: return "score-mid"
    return "score-low"


def render_score_bar(score: dict):
    if not score:
        return
    hook = score.get("hook_strength", 0)
    eng  = score.get("engagement_score", 0)
    tip  = score.get("tip", "")
    hc = _score_color(hook)
    ec = _score_color(eng)
    st.markdown(
        f'<div class="score-bar">'
        f'<span class="score-chip"><span>🎯 Hook</span><span class="{hc}">{hook}/10</span></span>'
        f'<span class="score-chip"><span>📈 Engagement</span><span class="{ec}">{eng}/10</span></span>'
        f'{"<span class=\"score-tip\">💡 " + tip + "</span>" if tip else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


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
    st.caption("📁 Saved to `assets/carousel_output/`")


def _render_publish_panel(key: str, output: dict, tab_key: str):
    """Render the publish expander for a single platform output."""
    raw = output.get("raw", "")
    if not raw:
        return

    with st.expander("📤 Post to platform", expanded=False):
        pub_tab_x, pub_tab_li, pub_tab_wh = st.tabs(["𝕏 Post to X", "💼 Post to LinkedIn", "🔗 Webhook"])

        # ── X / Twitter ───────────────────────────────────────────────────────
        with pub_tab_x:
            ck = load_key("tw_consumer_key")
            cs = load_key("tw_consumer_secret")
            at = load_key("tw_access_token")
            as_ = load_key("tw_access_secret")
            if not all([ck, cs, at, as_]):
                st.warning("Add your X API keys in the sidebar → Publishing credentials.")
            else:
                st.caption("Will post as a chained thread.")
                if st.button("🚀 Post Thread to X", key=f"post_x_{tab_key}", use_container_width=True):
                    tweets = output.get("tweets") if key == "x_thread" else [raw[i:i+270] for i in range(0, len(raw), 270)]
                    if not tweets:
                        tweets = [raw[:270]]
                    with st.spinner("Posting thread..."):
                        try:
                            ids = post_thread(tweets, ck, cs, at, as_)
                            st.success(f"✅ Posted {len(ids)} tweet(s)! First tweet ID: {ids[0]}")
                        except Exception as e:
                            st.error(f"Failed: {e}")

        # ── LinkedIn ──────────────────────────────────────────────────────────
        with pub_tab_li:
            li_tok = load_key("linkedin_token")
            if not li_tok:
                st.warning("Add your LinkedIn Access Token in the sidebar → Publishing credentials.")
                st.caption("Get one at [linkedin.com/developers](https://www.linkedin.com/developers/)")
            else:
                st.caption("Posts as a public text share.")
                if st.button("🚀 Post to LinkedIn", key=f"post_li_{tab_key}", use_container_width=True):
                    with st.spinner("Posting..."):
                        try:
                            post_linkedin(raw[:3000], li_tok)
                            st.success("✅ Posted to LinkedIn!")
                        except Exception as e:
                            st.error(f"Failed: {e}")

        # ── Webhook ───────────────────────────────────────────────────────────
        with pub_tab_wh:
            wh = load_key("webhook_url")
            if not wh:
                st.warning("Add your webhook URL in the sidebar → Publishing credentials.")
                st.caption("Works with Zapier, Buffer, Make.com, n8n, etc.")
            else:
                st.caption(f"Sends JSON to: `{wh[:60]}...`" if len(wh) > 60 else f"Sends JSON to: `{wh}`")
                if st.button("📡 Send to Webhook", key=f"post_wh_{tab_key}", use_container_width=True):
                    with st.spinner("Sending..."):
                        try:
                            result = post_webhook(wh, {"platform": key, "content": raw})
                            st.success(f"✅ Webhook delivered! Response: {str(result)[:100]}")
                        except Exception as e:
                            st.error(f"Failed: {e}")


def render_output_tabs(outputs: dict, scores: dict | None = None, tab_prefix: str = ""):
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

            # ── Score bar ─────────────────────────────────────────────────────
            if scores and key in scores and scores[key]:
                render_score_bar(scores[key])

            # ── Stat chips ────────────────────────────────────────────────────
            chips = []
            if "tweet_count" in output:            chips.append(f"🐦 {output['tweet_count']} tweets")
            if "char_count"  in output:            chips.append(f"📝 {output['char_count']:,} chars")
            if "word_count"  in output:            chips.append(f"📖 {output['word_count']} words")
            if "slide_count" in output:            chips.append(f"🖼️ {output['slide_count']} slides")
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
            st.code(output.get("raw", ""), language=None, wrap_lines=True)

            # ── Publish panel ─────────────────────────────────────────────────
            if key != "carousel":
                _render_publish_panel(key, output, tab_key=f"{tab_prefix}{key}")


def build_zip(results: dict) -> bytes:
    import zipfile
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


def _score_all(llm, outputs: dict) -> dict:
    """Run viral scoring for all non-carousel, non-error outputs."""
    scores = {}
    for key, output in outputs.items():
        if "error" in output or key == "carousel" or not output.get("raw"):
            continue
        scores[key] = score_output(llm, PLATFORM_LABELS.get(key, key), output["raw"])
    return scores


def render_content_calendar(batch_results: list[dict]):
    """Render a weekly content calendar from batch results using st.data_editor."""
    import pandas as pd

    st.markdown('<div class="cal-header">📅 Weekly Content Calendar</div>', unsafe_allow_html=True)
    st.caption("Drag to reorder • Edit any cell • Export as CSV for Buffer or Hootsuite")

    rows = []
    day_idx = 0
    for result in batch_results:
        title = result["source"].get("title", "Untitled")[:50]
        for platform_key, output in result["outputs"].items():
            if "error" in output or platform_key == "carousel":
                continue
            rows.append({
                "Day":      DAYS[day_idx % 7],
                "Platform": PLATFORM_ICONS.get(platform_key, "") + " " + PLATFORM_LABELS.get(platform_key, platform_key),
                "Title":    title,
                "Status":   "Draft",
                "Preview":  (output.get("raw", "")[:80] + "...").strip(),
            })
            day_idx += 1

    if not rows:
        st.info("No content to calendar.")
        return

    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Day":      st.column_config.SelectboxColumn("Day", options=DAYS, required=True),
            "Platform": st.column_config.TextColumn("Platform"),
            "Title":    st.column_config.TextColumn("Title"),
            "Status":   st.column_config.SelectboxColumn("Status", options=["Draft", "Scheduled", "Posted"], required=True),
            "Preview":  st.column_config.TextColumn("Preview", width="large"),
        },
        hide_index=True,
        key="content_calendar",
    )

    csv_bytes = edited.to_csv(index=False).encode()
    st.download_button(
        "📥 Export Calendar as CSV",
        data=csv_bytes,
        file_name="content_calendar.csv",
        mime="text/csv",
        use_container_width=False,
    )


def run_with_status(engine: GoldMineEngine, input_type: str, value: str, slug: str = "default") -> dict | None:
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

            # Score all generated outputs
            scoreable = {k: v for k, v in outputs.items() if "error" not in v and k != "carousel" and v.get("raw")}
            scores = {}
            if scoreable:
                st.write("🏆 Scoring content quality...")
                scores = _score_all(engine.llm, outputs)
                st.write("✅ Scores ready")

            n_ok = len([o for o in outputs.values() if "error" not in o])
            status.update(label=f"✅ Done — {n_ok}/{len(selected_platforms)} formats generated", state="complete", expanded=False)
            return {"source": content, "outputs": outputs, "scores": scores}

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
        "urls", height=140,
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


# ── Auth error banner ─────────────────────────────────────────────────────────
if auth_err := st.session_state.pop("_auth_error", None):
    st.markdown(f"""<div class="auth-banner">
🔑 <b>Invalid API Key</b><br>
Your key was rejected by {provider.upper()}. Please check it and try again.<br>
<small style="opacity:0.7">{auth_err[:200]}</small>
</div>""", unsafe_allow_html=True)


# ── History load ──────────────────────────────────────────────────────────────
if hist_id := st.session_state.pop("_history_load_id", None):
    hist_run = load_run(hist_id)
    if hist_run:
        st.markdown(f"### 🕘 Loaded: {hist_run['title']}")
        st.caption(f"Saved on {hist_run['created_at']} | Source: {hist_run['source_type']} | {hist_run['source_value'][:60]}")
        render_output_tabs(hist_run["outputs"], tab_prefix=f"hist_{hist_id}_")
        zip_data = build_zip({"source": {"title": hist_run["title"]}, "outputs": hist_run["outputs"]})
        st.download_button(
            "📦 Download as ZIP",
            data=zip_data,
            file_name=f"contentgoldmine_history_{hist_id}.zip",
            mime="application/zip",
        )
        st.divider()


# ── Generate ──────────────────────────────────────────────────────────────────
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
                save_run(
                    result["source"].get("title", url),
                    input_t, url, result["outputs"],
                )
                render_output_tabs(result["outputs"], scores=result.get("scores"), tab_prefix=f"b{i}_")
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

        if all_results:
            render_content_calendar(all_results)

    # ── Single mode ───────────────────────────────────────────────────────────
    else:
        if not user_input or not user_input.strip():
            st.error("Enter a URL or paste some text first.")
            st.stop()

        result = run_with_status(engine, input_type, user_input)
        if result:
            source = result["source"]
            n_ok = sum(1 for v in result["outputs"].values() if "error" not in v)

            save_run(source.get("title", user_input[:60]), input_type, user_input, result["outputs"])

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

            render_output_tabs(result["outputs"], scores=result.get("scores"))
