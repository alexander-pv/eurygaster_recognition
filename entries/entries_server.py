import threading
import os
import time
import datetime as dt
import uvicorn
import sqlite3

from loguru import logger
from pydantic import BaseModel
from fastapi import FastAPI

DATABASE = 'entries.db'
TIME_OFFSET_HRS = 3
LIMIT_ENTRIES = int(os.environ.get("LIMIT_ENTRIES", 50))
CLEAR_TIMING_MIN = int(os.environ.get("CLEAR_TIMING_MIN", 5))
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8084))


def get_current_time() -> str:
    offset = dt.timezone(dt.timedelta(hours=TIME_OFFSET_HRS))
    return str(dt.datetime.now(offset))


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score REAL NOT NULL,
        time TEXT NOT NULL,
        class_name TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


init_db()
app = FastAPI()


# Pydantic model for request body
class ScoreData(BaseModel):
    score: float
    class_name: str


@app.post("/add_score/")
async def add_score(data: ScoreData):
    new_etnry = (get_current_time(), data.score, data.class_name)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (time, score, class_name) VALUES (?, ?, ?)", new_etnry)
    conn.commit()
    conn.close()
    logger.info(f"Saved new entry: {new_etnry}")
    return {"message": "Score added successfully!"}


@app.get("/get_score/")
async def get_recent_scores(n: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT time, score, class_name FROM scores ORDER BY id DESC LIMIT ?", (n,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_old_entries():
    while True:
        time.sleep(CLEAR_TIMING_MIN * 60)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM scores WHERE id NOT IN (
            SELECT id FROM scores ORDER BY id DESC LIMIT ?
        )
        """, (LIMIT_ENTRIES,))
        conn.commit()
        conn.close()
        logger.info("Cleared old entries")


thread = threading.Thread(target=clear_old_entries)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
