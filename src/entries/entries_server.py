"""
Entries server: stores and serves recent recognition scores and thumbnail icons.
Used by the login page for preview carousel and recent entries table.
"""
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Iterator

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from loguru import logger
from pydantic import BaseModel, Field

# Configuration from environment
DATABASE = os.environ.get("ENTRIES_DATABASE", "entries.db")
TIME_OFFSET_HRS = int(os.environ.get("TIME_OFFSET_HRS", "3"))
LIMIT_ENTRIES = int(os.environ.get("LIMIT_ENTRIES", "50"))
CLEAR_TIMING_MIN = int(os.environ.get("CLEAR_TIMING_MIN", "5"))
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8084"))
MAX_ICON_B64_LEN = int(os.environ.get("ENTRIES_MAX_ICON_B64_LEN", "3145728"))  # 3 MiB default
MAX_SCORES_PARAM = 500
MAX_ICONS_PARAM = 500


def _get_current_time() -> str:
    import datetime as dt
    offset = dt.timezone(dt.timedelta(hours=TIME_OFFSET_HRS))
    return str(dt.datetime.now(offset))


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score REAL NOT NULL,
            time TEXT NOT NULL,
            class_name TEXT NOT NULL,
            icon_b64 TEXT NOT NULL
        )
        """)
    logger.info("Database initialized: {}", DATABASE)


init_db()
app = FastAPI(title="Entries Server", description="Recent recognition scores and icons for Eurygaster app")


class ScoreData(BaseModel):
    score: float = Field(..., ge=-10.0, le=10.0, description="Classification score")
    class_name: str = Field(..., min_length=1, max_length=256)
    icon_b64: str = Field(..., min_length=1, max_length=MAX_ICON_B64_LEN)


@app.get("/health")
def health() -> dict:
    """Health check for orchestrators and load balancers."""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        logger.warning("Health check failed: {}", e)
        raise HTTPException(503, "Service unavailable") from e


@app.post("/add_score/")
async def add_score(data: ScoreData) -> dict:
    try:
        row = (_get_current_time(), data.score, data.class_name, data.icon_b64)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO scores (time, score, class_name, icon_b64) VALUES (?, ?, ?, ?)",
                row,
            )
        logger.info("Saved entry: time={} score={} class_name={}", row[0], row[1], row[2])
        return {"message": "Score added successfully!"}
    except sqlite3.Error as e:
        logger.error("Database error on add_score: {}", e)
        raise HTTPException(500, "Failed to save score") from e


@app.get("/get_score/")
async def get_recent_scores(
    n: int = Query(10, ge=1, le=MAX_SCORES_PARAM, description="Number of recent scores"),
) -> list[dict]:
    try:
        with get_db() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT time, score, class_name FROM scores ORDER BY id DESC LIMIT ?",
                (n,),
            )
            rows = cur.fetchall()
        return [
            {"DateTime": r["time"], "Score": r["score"], "Recognized": r["class_name"]}
            for r in rows
        ]
    except sqlite3.Error as e:
        logger.error("Database error on get_score: {}", e)
        raise HTTPException(500, "Failed to fetch scores") from e


@app.get("/get_icons/")
async def get_recent_icons(
    n: int = Query(10, ge=1, le=MAX_ICONS_PARAM, description="Number of recent icons"),
) -> list[str]:
    try:
        with get_db() as conn:
            cur = conn.execute(
                "SELECT icon_b64 FROM scores ORDER BY id DESC LIMIT ?",
                (n,),
            )
            rows = cur.fetchall()
        return [r[0] for r in rows]
    except sqlite3.Error as e:
        logger.error("Database error on get_icons: {}", e)
        raise HTTPException(500, "Failed to fetch icons") from e


def _clear_old_entries() -> None:
    while True:
        time.sleep(CLEAR_TIMING_MIN * 60)
        try:
            with get_db() as conn:
                conn.execute(
                    """
                    DELETE FROM scores WHERE id NOT IN (
                        SELECT id FROM scores ORDER BY id DESC LIMIT ?
                    )
                    """,
                    (LIMIT_ENTRIES,),
                )
            logger.debug("Cleared old entries (keeping {} most recent)", LIMIT_ENTRIES)
        except Exception as e:
            logger.warning("clear_old_entries failed: {}", e)


_thread = threading.Thread(target=_clear_old_entries, daemon=True)
_thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
