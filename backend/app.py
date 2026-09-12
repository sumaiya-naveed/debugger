from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DB_PATH = "/home/talha/Desktop/debugger/backend/debugger.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_message TEXT NOT NULL,
            solution TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def analyze_error(error_message: str) -> str:
    msg = error_message.lower()
    if "syntaxerror" in msg or "invalid syntax" in msg or "syntax error" in msg:
        return "It looks like a syntax error. Check for missing colons, parentheses, or incorrect indentation."
    if "nameerror" in msg:
        return "A NameError occurred. Make sure all variables are defined before use."
    if "typeerror" in msg:
        return "A TypeError was raised. Verify that you are using the correct types for operations."
    if "keyerror" in msg:
        return "A KeyError happened. Check that the dictionary key exists before accessing it."
    if "importerror" in msg or "module not found" in msg:
        return "An import error occurred. Ensure the module is installed and the import path is correct."
    return "An unexpected error occurred. Review the stack trace for more details."


class ErrorPayload(BaseModel):
    error_message: str

@app.post("/analyze")
async def analyze(payload: ErrorPayload):
    suggestion = analyze_error(payload.error_message)
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bugs (error_message, solution, created_at) VALUES (?, ?, ?)",
            (payload.error_message, suggestion, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB save error:", e)
    return JSONResponse({"suggestion": suggestion, "error_message": payload.error_message})


@app.get("/bugs")
async def list_bugs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, error_message, solution, created_at FROM bugs ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    bugs = [{"id": r[0], "error_message": r[1], "solution": r[2], "created_at": r[3]} for r in rows]
    return JSONResponse(bugs)