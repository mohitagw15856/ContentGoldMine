import sqlite3
import json
from pathlib import Path
from datetime import datetime

_DB_PATH = Path.home() / ".contentgoldmine" / "history.db"


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at   TEXT NOT NULL,
            title        TEXT,
            source_type  TEXT,
            source_value TEXT,
            platforms    TEXT,
            outputs_json TEXT
        )
    """)
    conn.commit()
    return conn


def save_run(title: str, source_type: str, source_value: str, outputs: dict) -> int:
    conn = _connect()
    platforms = ",".join(outputs.keys())
    cur = conn.execute(
        "INSERT INTO runs (created_at, title, source_type, source_value, platforms, outputs_json) "
        "VALUES (?,?,?,?,?,?)",
        (
            datetime.now().isoformat(timespec="seconds"),
            title[:200],
            source_type,
            source_value[:500],
            platforms,
            json.dumps(outputs),
        ),
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def list_runs(limit: int = 50) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT id, created_at, title, source_type, platforms FROM runs ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "created_at": r[1], "title": r[2], "source_type": r[3], "platforms": r[4]}
        for r in rows
    ]


def load_run(run_id: int) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT id, created_at, title, source_type, source_value, platforms, outputs_json "
        "FROM runs WHERE id=?",
        (run_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "created_at": row[1],
        "title": row[2],
        "source_type": row[3],
        "source_value": row[4],
        "platforms": row[5],
        "outputs": json.loads(row[6]),
    }


def delete_run(run_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM runs WHERE id=?", (run_id,))
    conn.commit()
    conn.close()
