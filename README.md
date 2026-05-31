<div align="center">

# ⛏️ ContentGoldMine

### The content repurposing machine built for creators who want to work smarter.

**One blog post. One YouTube video. One idea.**
**→ Instantly becomes a viral thread, LinkedIn post, newsletter, carousel, and video script.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Stars](https://img.shields.io/github/stars/mohitagw15856/ContentGoldMine?style=social)](https://github.com/mohitagw15856/ContentGoldMine/stargazers)
[![Forks](https://img.shields.io/github/forks/mohitagw15856/ContentGoldMine?style=social)](https://github.com/mohitagw15856/ContentGoldMine/network)
[![License: MIT](https://img.shields.io/badge/License-MIT-D4AF37)](LICENSE)
[![Inspired by MoneyPrinterTurbo](https://img.shields.io/badge/Inspired%20by-MoneyPrinterTurbo-gold)](https://github.com/harry0703/MoneyPrinterTurbo)

</div>

---

## The Problem Every Creator Knows

You spend hours writing a great piece of content. You publish it once. It gets a handful of views. Then it's gone.

Meanwhile, the creators making real money aren't writing more — **they're repurposing smarter.** The same insight that makes a great LinkedIn post also makes a great Twitter thread, a newsletter section, an Instagram carousel, and a TikTok script.

**ContentGoldMine automates that entire process.**

---

## See It In Action

### The App
![ContentGoldMine UI](assets/screenshot.png)

### ⚙️ Settings Sidebar — Tone, Brand Voice & Saved API Keys
![Sidebar](docs/screenshot_sidebar.png)

### ✅ Results — Tweet Cards, Copy Button & ZIP Download
![Results View](docs/screenshot_results.png)

### 𝕏 Thread Output — Tweet Cards with Live Character Counts
![Thread Output](docs/screenshot_thread.png)

### 🎠 Carousel Slides — 1080×1080 Generated Images
![Carousel Output](docs/screenshot_carousel.png)

### 🎬 Video Script — Color-Coded Sections
![Script Output](docs/screenshot_script.png)

### 📦 Batch Mode — Process Multiple URLs at Once
![Batch Mode](docs/screenshot_batch.png)

---

## What You Get

Paste any URL or text → click **Mine the Gold** → get back 5 ready-to-post formats:

| Format | What's Generated | Best For |
|--------|-----------------|---------|
| **𝕏 Thread** | 10–14 tweets with hooks, live char count per tweet | Growing X / Twitter |
| **💼 LinkedIn Post** | Story-driven post with takeaways + hashtags | B2B authority & leads |
| **📧 Newsletter** | Subject line, preview text, formatted body | Email monetization |
| **🎠 Instagram Carousel** | 8–10 designed 1080×1080 PNG slides | Saves & shares |
| **🎬 Video Script** | Hook + 3 points + payoff + CTA, colour-coded | TikTok / Reels / Shorts |

---

## Features

### Content Generation
- **3 Input Types** — Blog/article URL, YouTube URL, or raw text
- **5 Platform Outputs** — Thread, LinkedIn, Newsletter, Carousel, Video Script
- **📦 Batch Mode** — Paste 10 URLs, get 50 pieces of content in one run
- **🎠 Beautiful Carousel Images** — Real 1080×1080 PNGs rendered via Playwright

### Make It Sound Like You
- **🎭 Tone & Persona Selector** — Choose from 5 distinct voices:
  - `Professional` — authoritative, data-backed, polished
  - `Casual & Fun` — conversational, warm, light humour
  - `Contrarian` — challenges conventional wisdom, provocative opener
  - `Educational` — teacher-mode, analogies, logical structure
  - `Storytelling` — emotional arc, scene-based, narrative-driven
- **✍️ Custom Brand Voice** — Describe your voice in plain English. Every output will sound like *you*, not a generic AI.

### Workflow & UX
- **📋 One-click Copy** — Every output has a built-in copy button. No selecting, no Ctrl+A.
- **📦 Download All as ZIP** — One click packages all text files + carousel images into a ready-to-share archive
- **🔐 Saved API Keys** — Type once, saved locally. Never asked again.
- **🔑 Test API Key** — Validate your key before running to avoid failed jobs
- **⚡ Live Progress** — Watch each format generate step by step in real time
- **🌍 Multi-language** — English, Spanish, French, German, Portuguese, Hindi, Arabic
- **3 LLM Providers** — OpenAI, Anthropic (Claude), Google Gemini
- **3 Carousel Themes** — Gold, Dark, Light
- **REST API** — Full FastAPI backend for automation
- **CLI** — Run from terminal for scripting and pipelines

---

## Who Is This For?

- **Content creators** who publish on one platform and watch everything else go dark
- **Solopreneurs** who want to be everywhere without burning out
- **Newsletter writers** who want to squeeze more reach from every issue
- **YouTubers** who want to milk every video for 5× the reach
- **Marketers** who need quality content at scale — not just volume

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/mohitagw15856/ContentGoldMine.git
cd ContentGoldMine
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Launch

```bash
python main.py webui
# Opens at http://localhost:8501
```

### 3. Use it

1. Paste your API key in the sidebar → hit **💾** to save it permanently
2. (Optional) Pick a **Tone** and describe your **Brand Voice**
3. Drop in a URL or paste text
4. Pick your platforms, click **⛏️ Mine the Gold**
5. Copy outputs with one click or **📦 Download All as ZIP**

---

## Tone & Brand Voice

Two settings that change everything about the output quality:

**Tone selector** — applies to all 5 outputs at once:

```
Professional  → "This data suggests a 3x improvement in retention..."
Casual & Fun  → "Okay so here's the thing nobody tells you about retention..."
Contrarian    → "Everyone's obsessing over retention. Here's why that's wrong."
Educational   → "Retention works like a leaky bucket. Let me explain..."
Storytelling  → "Last Tuesday, I watched a startup lose 40% of users overnight..."
```

**Brand Voice** — describe yourself in plain English in the sidebar text area:

```
e.g. "I'm a no-BS founder. Plain English. Short sentences.
      I never use buzzwords like 'leverage' or 'synergy'.
      I'm direct and slightly opinionated."
```

Every output — thread, LinkedIn, newsletter, carousel, script — will match that voice.

---

## Batch Processing

Turn a week's worth of reading into a week's worth of content in one session.

Enable **Batch Mode** → paste URLs (one per line) → hit Mine.

```
https://medium.com/article-1
https://youtube.com/watch?v=abc123
https://yourfavouriteblog.com/post
```

→ 3 URLs × 5 formats = **15 pieces of content**. Each URL gets its own ZIP download.

---

## API Usage

```bash
python main.py api
# Docs at http://localhost:8000/docs
```

```bash
curl -X POST http://localhost:8000/repurpose \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "url",
    "value": "https://yourblog.com/post",
    "platforms": ["x_thread", "linkedin", "carousel"],
    "llm_provider": "openai",
    "api_key": "sk-...",
    "language": "English"
  }'
```

---

## CLI

```bash
# Repurpose a blog post (all platforms)
python main.py repurpose url "https://yourblog.com/post" --key sk-...

# YouTube video, specific platforms, Spanish output
python main.py repurpose youtube "https://youtube.com/watch?v=..." \
  --key sk-... --platforms "x_thread,linkedin" --lang Spanish
```

---

## Supported LLM Providers

| Provider | Recommended Model | Get API Key |
|----------|------------------|-------------|
| **OpenAI** | `gpt-4o` | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Anthropic** | `claude-sonnet-4-6` | [console.anthropic.com](https://console.anthropic.com) |
| **Google Gemini** | `gemini-1.5-pro` | [aistudio.google.com](https://aistudio.google.com/apikey) |

---

## Project Structure

```
ContentGoldMine/
├── main.py                     # CLI entry (webui / api / repurpose)
├── app/
│   ├── webui.py                # Streamlit UI
│   └── api.py                  # FastAPI REST API
├── goldmine/
│   ├── engine.py               # Orchestrator
│   ├── key_store.py            # Local API key persistence
│   ├── ingestor/               # URL / YouTube / Text extractors
│   ├── llm/                    # OpenAI, Anthropic, Gemini providers
│   ├── transformer/            # Per-platform content transformers
│   │   └── base.py             # Tone + brand voice injection
│   └── renderer/               # HTML→PNG carousel renderer (Playwright)
└── assets/carousel_output/     # Generated carousel images
```

---

## Roadmap

- [x] Blog URL + YouTube + raw text ingestion
- [x] X Thread, LinkedIn, Newsletter, Carousel, Video Script
- [x] Beautiful HTML+Playwright carousel image generation
- [x] Saved API keys (local, private) + Test Key button
- [x] Live generation progress (per-platform status)
- [x] **Batch processing** (multiple URLs at once)
- [x] **One-click copy buttons** on every output
- [x] **Download All as ZIP** (text files + carousel images)
- [x] **Tone & Persona selector** (5 distinct voices)
- [x] **Custom Brand Voice** injection
- [x] Multi-language support
- [x] FastAPI backend + CLI
- [ ] Auto-post to X, LinkedIn, Instagram
- [ ] Podcast/audio input (Whisper transcription)
- [ ] Scheduled repurposing (weekly automation)
- [ ] Analytics — track what performs best per platform

---

## Contributing

PRs welcome. Open an issue first for anything major.

---

## License

MIT — use it, fork it, build on it, make money with it.

---

<div align="center">

**If ContentGoldMine saved you time, drop it a ⭐ — it helps other creators find it.**

Built for creators who want to work 10× smarter, not harder.

</div>
