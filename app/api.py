from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from goldmine.engine import GoldMineEngine

app = FastAPI(
    title="ContentGoldMine API",
    description="Turn any content into platform-ready gold. One input → X thread, LinkedIn, newsletter, carousel, video script.",
    version="1.0.0",
)


class RepurposeRequest(BaseModel):
    input_type: Literal["url", "youtube", "text"]
    value: str
    platforms: Optional[list[str]] = None
    llm_provider: Literal["openai", "anthropic", "gemini"] = "openai"
    api_key: str
    model: Optional[str] = None
    language: str = "English"
    carousel_theme: str = "gold"


@app.get("/")
def root():
    return {"message": "ContentGoldMine API is running ⛏️", "docs": "/docs"}


@app.get("/platforms")
def list_platforms():
    return {
        "platforms": [
            {"key": "x_thread", "name": "X Thread", "emoji": "🐦"},
            {"key": "linkedin", "name": "LinkedIn Post", "emoji": "💼"},
            {"key": "newsletter", "name": "Newsletter Section", "emoji": "📧"},
            {"key": "carousel", "name": "Instagram Carousel", "emoji": "🎠"},
            {"key": "video_script", "name": "Video Script", "emoji": "🎬"},
        ]
    }


@app.post("/repurpose")
def repurpose(req: RepurposeRequest):
    try:
        engine = GoldMineEngine(
            llm_provider=req.llm_provider,
            api_key=req.api_key,
            model=req.model,
            language=req.language,
            carousel_theme=req.carousel_theme,
        )
        results = engine.repurpose(req.input_type, req.value, req.platforms)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
