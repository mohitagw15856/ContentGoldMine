import requests


def post_webhook(url: str, payload: dict, headers: dict | None = None) -> dict:
    """POST JSON payload to a Buffer / Zapier / Make.com webhook URL."""
    resp = requests.post(url, json=payload, headers=headers or {}, timeout=15)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return {"status": "ok", "status_code": resp.status_code}
