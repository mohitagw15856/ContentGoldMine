import json
from pathlib import Path

_CONFIG = Path.home() / ".contentgoldmine" / "config.json"


def save_key(provider: str, key: str) -> None:
    _CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = _load()
    data[f"key_{provider}"] = key
    _CONFIG.write_text(json.dumps(data, indent=2))


def load_key(provider: str) -> str:
    return _load().get(f"key_{provider}", "")


def _load() -> dict:
    try:
        return json.loads(_CONFIG.read_text())
    except Exception:
        return {}
