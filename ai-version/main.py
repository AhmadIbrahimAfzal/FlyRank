"""
AI-generated version for Stage 6 Bonus Rematch
Specification: FastAPI CRUD Task API backed by SQLite (tasks.db) with parameterized queries.
"""
import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

app = FastAPI(
    title="AI Task API",
    description="AI-generated task API with SQLite database backend",
    version="1.0"
)

DB_FILE = os.path.join(os.path.dirname(__file__), "tasks.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)
        cursor = conn.execute("SELECT COUNT(*) FROM tasks")
        if cursor.fetchone()[0] == 0:
            sample_tasks = [
                ("Buy groceries", 0),
                ("Read a book", 1),
                ("Learn FastAPI", 0)
            ]
            conn.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", sample_tasks)
            conn.commit()

setup_database()

@app.get("/")
def api_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    with get_db() as conn:
        query = "SELECT id, title, done FROM tasks"
        params = []
        filters = []
        if done is not None:
            filters.append("done = ?")
            params.append(1 if done else 0)
        if search:
            filters.append("title LIKE ?")
            params.append(f"%{search}%")
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY id ASC"
        rows = conn.execute(query, params).fetchall()
        return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

@app.get("/tasks/{id}")
def get_single_task(id: int):
    with get_db() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,)).fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks")
def create_new_task(payload: dict = Body(default={})):
    title = payload.get("title") if isinstance(payload, dict) else None
    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required and cannot be empty"})
    with get_db() as conn:
        cursor = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title.strip(), 0))
        new_id = cursor.lastrowid
        conn.commit()
        return JSONResponse(
            status_code=201,
            content={"id": new_id, "title": title.strip(), "done": False}
        )

@app.put("/tasks/{id}")
def update_existing_task(id: int, payload: dict = Body(default={})):
    if not isinstance(payload, dict) or not payload:
        return JSONResponse(status_code=400, content={"error": "Request body cannot be empty"})
    with get_db() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,)).fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
        
        title = row["title"]
        done = row["done"]
        updated = False
        
        if "title" in payload:
            t = payload["title"]
            if not isinstance(t, str) or not t.strip():
                return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
            title = t.strip()
            updated = True
            
        if "done" in payload:
            d = payload["done"]
            if not isinstance(d, bool):
                return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})
            done = 1 if d else 0
            updated = True
            
        if not updated:
            return JSONResponse(status_code=400, content={"error": "No valid fields to update"})
            
        conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, id))
        conn.commit()
        return {"id": id, "title": title, "done": bool(done)}

@app.delete("/tasks/{id}")
def delete_existing_task(id: int):
    with get_db() as conn:
        row = conn.execute("SELECT id FROM tasks WHERE id = ?", (id,)).fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
        conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
        return Response(status_code=204)
