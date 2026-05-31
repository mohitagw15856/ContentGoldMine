<div align="center">

# ⛏️ ContentGoldMine

### Turn **one piece of content** into gold across every platform — instantly.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/ContentGoldMine?style=social)](https://github.com/yourusername/ContentGoldMine)
[![Forks](https://img.shields.io/github/forks/yourusername/ContentGoldMine?style=social)](https://github.com/yourusername/ContentGoldMine)

**Inspired by [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) — but for the content repurposing goldmine.**

[Features](#-features) · [Quick Start](#-quick-start) · [How it Works](#-how-it-works) · [API Docs](#-api) · [Roadmap](#-roadmap)

</div>

---

## What is ContentGoldMine?

You write (or find) **one piece of content** — a blog post, YouTube video, or raw notes.

ContentGoldMine uses AI to automatically transform it into **5 platform-optimized formats**, ready to post:

| Input | → | Outputs |
|-------|---|---------|
| Blog post URL | → | 🐦 Viral X Thread |
| YouTube video URL | → | 💼 LinkedIn Post |
| Raw text / notes | → | 📧 Newsletter Section |
| | → | 🎠 Instagram Carousel (with images) |
| | → | 🎬 Short Video Script (TikTok/Reels) |

**One input. Five revenue streams. Zero manual work.**

---

## ✨ Features

- **3 Input Types** — Blog URL, YouTube URL, or raw text
- **5 Platform Outputs** — X Thread, LinkedIn, Newsletter, Instagram Carousel, Video Script
- **Carousel Image Generation** — Generates actual 1080×1080 slide images with gradient themes
- **3 LLM Providers** — OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini)
- **Multi-language** — Generate content in English, Spanish, French, German, and more
- **Streamlit Web UI** — Clean, easy-to-use browser interface
- **FastAPI Backend** — Full REST API for automation and integrations
- **CLI** — Run from the terminal for scripting and automation

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/ContentGoldMine.git
cd ContentGoldMine
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API key (OpenAI, Anthropic, or Gemini)
```

### 3. Launch the Web UI

```bash
python main.py webui
# Opens at http://localhost:8501
```

That's it. Paste a URL, pick your platforms, click **Mine the Gold**.

---

## 🖥️ Web UI

```
┌─────────────────────────────────────────────────────────────┐
│                  ⛏️  ContentGoldMine                         │
│     Turn one piece of content into gold across every        │
│                  platform — instantly.                      │
├──────────────┬──────────────────────────────────────────────┤
│  Settings    │  Input Type:  ● Blog URL  ○ YouTube  ○ Text │
│              │                                              │
│  Provider:   │  URL: https://yourblog.com/my-post           │
│  [OpenAI  ▾] │                                              │
│              │  Platforms:                                  │
│  API Key:    │  ☑ X Thread   ☑ LinkedIn   ☑ Newsletter     │
│  [●●●●●●●] │  ☑ Carousel   ☑ Video Script                 │
│              │                                              │
│  Language:   │         [ ⛏️  Mine the Gold ]                │
│  [English ▾] │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

---

## 🔧 How it Works

```
Input (URL / YouTube / Text)
        │
        ▼
   ┌──────────┐
   │ Ingestor │  ← Extracts clean text (trafilatura / yt-dlp)
   └──────────┘
        │
        ▼
   ┌─────────────┐
   │ LLM Engine  │  ← OpenAI / Anthropic / Gemini
   └─────────────┘
        │
   ┌────┴────────────────────────────────────┐
   │                                         │
   ▼         ▼         ▼         ▼          ▼
X Thread  LinkedIn  Newsletter  Carousel  Video Script
                                  │
                                  ▼
                           Image Renderer
                         (1080×1080 PNGs)
```

---

## 🌐 API

Start the API server:

```bash
python main.py api
# Docs at http://localhost:8000/docs
```

### Example Request

```bash
curl -X POST http://localhost:8000/repurpose \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "url",
    "value": "https://yourblog.com/my-post",
    "platforms": ["x_thread", "linkedin", "carousel"],
    "llm_provider": "openai",
    "api_key": "sk-...",
    "language": "English"
  }'
```

### Response

```json
{
  "source": { "title": "My Post", "content": "...", "source": "https://..." },
  "outputs": {
    "x_thread": {
      "platform": "X Thread",
      "tweets": ["1/ Hook tweet...", "2/ Point one..."],
      "tweet_count": 10
    },
    "linkedin": {
      "platform": "LinkedIn Post",
      "raw": "The full post text...",
      "char_count": 1150
    },
    "carousel": {
      "platform": "Instagram Carousel",
      "slides": [...],
      "image_paths": ["assets/carousel_output/slide_01.png", ...]
    }
  }
}
```

---

## 💻 CLI Usage

```bash
# Repurpose a blog post
python main.py repurpose url "https://yourblog.com/post" --key sk-...

# Repurpose a YouTube video, specific platforms only
python main.py repurpose youtube "https://youtube.com/watch?v=..." \
  --key sk-... \
  --platforms "x_thread,linkedin"

# Repurpose raw text in Spanish
python main.py repurpose text "My amazing content here..." \
  --key sk-... \
  --lang Spanish
```

---

## 🛠️ Supported LLM Providers

| Provider | Models | Key Env Var |
|----------|--------|-------------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | `OPENAI_API_KEY` |
| Anthropic | `claude-sonnet-4-6`, `claude-opus-4-7` | `ANTHROPIC_API_KEY` |
| Google Gemini | `gemini-1.5-pro`, `gemini-1.5-flash` | `GEMINI_API_KEY` |

---

## 📂 Project Structure

```
ContentGoldMine/
├── main.py                    # CLI entry point
├── app/
│   ├── webui.py               # Streamlit web interface
│   └── api.py                 # FastAPI REST API
├── goldmine/
│   ├── engine.py              # Core orchestrator
│   ├── config.py              # Settings
│   ├── ingestor/              # URL / YouTube / Text ingestion
│   ├── llm/                   # LLM provider abstractions
│   ├── transformer/           # Platform-specific content transformers
│   └── renderer/              # Carousel image renderer (Pillow)
└── assets/
    └── carousel_output/       # Generated carousel images
```

---

## 🗺️ Roadmap

- [x] Blog URL ingestion
- [x] YouTube transcript ingestion
- [x] X/Twitter thread generation
- [x] LinkedIn post generation
- [x] Newsletter section generation
- [x] Instagram carousel (text + images)
- [x] Short video script
- [x] Multi-LLM provider support
- [x] Multi-language support
- [x] Streamlit web UI
- [x] FastAPI backend
- [ ] Auto-posting to X, LinkedIn, Instagram
- [ ] Batch processing (multiple URLs at once)
- [ ] Podcast episode generation (audio output)
- [ ] Custom brand voice / tone settings
- [ ] Scheduled repurposing (cron jobs)
- [ ] Analytics dashboard

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss major changes.

---

## 📄 License

MIT License — use it, fork it, build on it.

---

<div align="center">

**If this saved you time, give it a ⭐ — it helps others find it.**

Made with ❤️ for content creators who want to work smarter, not harder.

</div>
